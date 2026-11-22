#!/usr/bin/env python3
# pihole_admin.py

from __future__ import annotations

import argparse
import logging
import os
import re
import shutil
import signal
import sqlite3
import subprocess
import sys
import textwrap
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, NoReturn

if TYPE_CHECKING:  # Imported only for type hints; pandas stays an optional runtime dep.
    import pandas as pd

# Pi-hole FTL "status" codes that represent a blocked answer (gravity, regex,
# denied, special-domain, etc.). Centralized so every query stays consistent.
BLOCKED_STATUS_CODES = (1, 4, 5, 6, 7, 8, 9, 10, 11)
BLOCKED_STATUS_IN = ", ".join(str(code) for code in BLOCKED_STATUS_CODES)

# Every third-party package (tabulate, matplotlib, pandas, seaborn,
# rapidfuzz/fuzzywuzzy, tld) is imported lazily inside the few functions that use
# it. This keeps --help and the common commands (stats, add/remove, optimize,
# backup) fast and lets them run when none of those packages are installed.


def _grid(rows: list[dict[str, Any]]) -> str:
    """Render rows of dicts as a bordered table."""
    try:
        from tabulate import tabulate
    except ImportError:
        sys.exit("tabulate is required to print tables. Install it with: pip install tabulate")
    return tabulate(rows, headers="keys", tablefmt="grid")


def _load_pyplot():
    """Import matplotlib with a headless-safe backend, plus optional seaborn."""
    import matplotlib
    matplotlib.use("Agg")  # Must precede pyplot import; renders without a display.
    import matplotlib.pyplot as plt
    try:
        import seaborn as sns
    except ImportError:
        sns = None
    return plt, sns


def _get_ratio():
    """Return a string-similarity function (0-100), preferring the fastest lib."""
    try:
        from rapidfuzz import fuzz
        return fuzz.ratio
    except ImportError:
        pass
    try:
        from fuzzywuzzy import fuzz
        return fuzz.ratio
    except ImportError:
        from difflib import SequenceMatcher
        return lambda a, b: SequenceMatcher(None, a, b).ratio() * 100


def _suffix_extractor():
    """Return a function mapping a domain to its registry suffix/category."""
    try:
        from tld import get_tld
    except ImportError:
        get_tld = None

    def extract(domain: str) -> str:
        if get_tld is not None:
            # fix_protocol lets bare domains (no scheme) be parsed correctly;
            # without it tld returns None for every Pi-hole entry. fail_silently
            # makes tld return None for anything it cannot parse instead of raising.
            info = get_tld(domain, as_object=True, fail_silently=True, fix_protocol=True)
            return info.suffix if info else "Unknown"
        parts = domain.split('.')
        return '.'.join(parts[-2:]) if len(parts) > 1 else "Unknown"

    return extract


# Exact allow (0) and deny (1) entries; Pi-hole lowercases these before storing them.
EXACT_LIST_TYPES = (0, 1)
REGEX_LIST_TYPES = (2, 3)


@dataclass(frozen=True)
class ListEntry:
    """One domainlist row with its group links, as read in a single snapshot."""
    id: int
    type: int
    domain: str
    enabled: bool
    comment: str | None
    groups: tuple[int, ...]


@dataclass(frozen=True)
class Removal:
    entry: ListEntry
    keeper: ListEntry


@dataclass
class DuplicatePlan:
    removals: list[Removal] = field(default_factory=list)
    # Same entry on an allow list and its deny list: reported, never changed.
    overlaps: list[tuple[ListEntry, ListEntry]] = field(default_factory=list)


def read_domainlist(conn: sqlite3.Connection) -> list[ListEntry]:
    links: dict[int, list[int]] = defaultdict(list)
    for domain_id, group_id in conn.execute(
            "SELECT domainlist_id, group_id FROM domainlist_by_group ORDER BY domainlist_id, group_id"):
        links[domain_id].append(group_id)
    return [ListEntry(row_id, list_type, domain, bool(enabled), comment, tuple(links[row_id]))
            for row_id, list_type, domain, enabled, comment in conn.execute(
                "SELECT id, type, domain, enabled, comment FROM domainlist ORDER BY id")]


def plan_duplicates(entries: list[ListEntry]) -> DuplicatePlan:
    """Find exact-list entries that only differ in letter case, and the copies to remove.

    Pi-hole FTL lowercases exact domains when they are added and compares them byte for byte
    with the query name, which it lowercases (ASCII A-Z only). An exact entry with a capital
    letter therefore never matches, so removing it changes no filtering whatever its groups or
    enabled state. Regex entries are never touched: case-insensitive matching does not make
    regexes that differ in case equivalent (\\w and \\W, ;querytype= and ;QUERYTYPE=), and
    FTL stops at the first regex that matches. Non-ASCII entries are left alone too.
    """
    plan = DuplicatePlan()
    by_name: dict[tuple[int, str], list[ListEntry]] = defaultdict(list)
    for entry in entries:
        if entry.type in EXACT_LIST_TYPES and entry.domain.isascii():
            by_name[(entry.type, entry.domain.lower())].append(entry)
    for key in sorted(by_name):
        copies = sorted(by_name[key], key=lambda entry: entry.id)
        if len(copies) < 2:
            continue
        # UNIQUE(domain, type) allows at most one all-lowercase copy; it is the only one
        # Pi-hole can match.
        keeper = next((entry for entry in copies if entry.domain == key[1]), copies[0])
        plan.removals += [Removal(entry, keeper) for entry in copies if entry is not keeper]

    # Keys are (first list type of the pair, text): 0 for exact lists, 2 for regex lists.
    by_text: dict[tuple[int, str], dict[int, list[ListEntry]]] = defaultdict(lambda: defaultdict(list))
    for entry in entries:
        if entry.type in EXACT_LIST_TYPES:
            text = entry.domain.lower() if entry.domain.isascii() else entry.domain
            by_text[(0, text)][entry.type].append(entry)
        elif entry.type in REGEX_LIST_TYPES:
            by_text[(2, entry.domain)][entry.type].append(entry)
    for key in sorted(by_text):
        allow_type, deny_type = key[0], key[0] + 1
        by_type = by_text[key]
        plan.overlaps += [(allow, deny) for allow in by_type[allow_type] for deny in by_type[deny_type]]
    return plan


# Pi-hole's `updatechecker` keeps the installed and the latest version of every part of
# Pi-hole in this file (since v5.14); its web interface reads the same file.
VERSIONS_FILE = "/etc/pihole/versions"
# (name shown, key prefix in the versions file)
COMPONENTS = (("Core", "CORE"), ("Web", "WEB"), ("FTL", "FTL"))
UP_TO_DATE, UPDATE_AVAILABLE, UNKNOWN = "up to date", "update available", "unknown"


def version_key(text: str) -> tuple[int, ...] | None:
    """Turn 'v6.6.1' into (6, 6, 1) for comparing; None when it is not a version."""
    # A release tag, or `git describe` output based on one (v6.6-3-gabc1234, v5.14-0-gabc1234-dirty).
    # Pi-hole records a bare commit hash when it finds no tag, and that must not read as a version.
    match = re.fullmatch(r"v(\d+(?:\.\d+)*)(?:-\d+-g[0-9a-f]+)?(?:-dirty)?", text)
    if match is None:
        return None
    parts = [int(part) for part in match.group(1).split(".")]
    # v6.6.0 and v6.6 are the same release.
    while parts and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


def same_commit(first: str, second: str) -> bool:
    # Pi-hole v5 abbreviates the installed and the latest hash to different lengths.
    return first != "" and second != "" and (first.startswith(second) or second.startswith(first))


@dataclass(frozen=True)
class Component:
    """One part of Pi-hole as recorded in its versions file."""
    name: str
    installed: str
    latest: str
    branch: str
    installed_hash: str
    latest_hash: str

    @property
    def on_release(self) -> bool:
        return self.branch == "master"

    @property
    def state(self) -> str:
        # The same rule as Pi-hole's web interface (scripts/js/footer.js): releases
        # compare version numbers, and any other branch compares commit hashes.
        if self.on_release:
            installed, latest = version_key(self.installed), version_key(self.latest)
            if installed is None or latest is None:
                return UNKNOWN
            return UPDATE_AVAILABLE if installed < latest else UP_TO_DATE
        if self.installed_hash == "" or self.latest_hash == "":
            return UNKNOWN
        return UP_TO_DATE if same_commit(self.installed_hash, self.latest_hash) else UPDATE_AVAILABLE

    @property
    def installed_text(self) -> str:
        if self.on_release:
            return self.installed or "unknown"
        return f"{self.branch or 'unknown branch'} {self.installed_hash}".strip()

    @property
    def latest_text(self) -> str:
        return (self.latest if self.on_release else self.latest_hash) or "unknown"

    def has_reached(self, target: Component) -> bool:
        """True when this component now runs what `target` offered before the update."""
        if target.on_release:
            now, wanted = version_key(self.installed), version_key(target.latest)
            return now is not None and wanted is not None and now >= wanted
        # A branch can gain commits while the update runs, so the commit Pi-hole now names as
        # the latest counts as well as the one offered.
        return self.branch == target.branch and (same_commit(self.installed_hash, target.latest_hash)
                                                 or same_commit(self.installed_hash, self.latest_hash))


def read_versions(path: str) -> dict[str, str]:
    values = {}
    with open(path, encoding="utf-8", errors="replace") as record:
        for line in record:
            key, separator, value = line.partition("=")
            if separator:
                value = value.strip()
                # Pi-hole writes "null" for a value it could not look up.
                values[key.strip()] = "" if value == "null" else value
    return values


def components_from(versions: dict[str, str]) -> list[Component]:
    # A part the file does not mention is not installed (Pi-hole v5 without the web interface).
    return [Component(name,
                      installed=versions.get(f"{key}_VERSION", ""),
                      latest=versions.get(f"GITHUB_{key}_VERSION", ""),
                      branch=versions.get(f"{key}_BRANCH", ""),
                      installed_hash=versions.get(f"{key}_HASH", ""),
                      latest_hash=versions.get(f"GITHUB_{key}_HASH", ""))
            for name, key in COMPONENTS
            if f"{key}_VERSION" in versions or f"{key}_BRANCH" in versions]


class DatabaseConnectionPool:
    def __init__(self, db_path: str, max_connections: int = 5):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = []

    def get_connection(self) -> sqlite3.Connection:
        if len(self.connections) < self.max_connections:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connections.append(conn)
            return conn
        else:
            # Simple round-robin connection retrieval
            conn = self.connections.pop(0)
            self.connections.append(conn)
            return conn

    def close_all(self):
        for conn in self.connections:
            conn.close()
        self.connections.clear()


class PiholeDBAdmin:
    def __init__(self, gravity_db_path: str = "/etc/pihole/gravity.db",
                 query_db_path: str = "/etc/pihole/pihole-FTL.db"):
        self.gravity_db_pool = DatabaseConnectionPool(gravity_db_path)
        self.query_db_pool = DatabaseConnectionPool(query_db_path)
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("PiholeDBAdmin")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        if not logger.handlers:
            logger.addHandler(handler)
        return logger

    def close_pools(self):
        self.gravity_db_pool.close_all()
        self.query_db_pool.close_all()

    def __del__(self):
        self.close_pools()

    def _get_connection(self, db_path: str) -> sqlite3.Connection:
        if db_path == self.gravity_db_pool.db_path:
            return self.gravity_db_pool.get_connection()
        elif db_path == self.query_db_pool.db_path:
            return self.query_db_pool.get_connection()
        else:
            raise ValueError(f"Unknown database path: {db_path}")

    def optimize_database(self) -> None:
        self.logger.info("Starting database optimization...")

        dbs = [self.gravity_db_pool.db_path, self.query_db_pool.db_path]
        summaries = []

        for db in dbs:
            try:
                with self._get_connection(db) as conn:
                    cursor = conn.cursor()

                    cursor.execute("PRAGMA page_count")
                    initial_pages = cursor.fetchone()[0]
                    cursor.execute("PRAGMA page_size")
                    page_size = cursor.fetchone()[0]
                    initial_size = initial_pages * page_size / (1024 * 1024)  # Size in MB

                    cursor.execute("PRAGMA freelist_count")
                    initial_fragmentation = cursor.fetchone()[0] * page_size / (1024 * 1024)  # Fragmentation in MB

                    start_time = time.time()
                    conn.execute("VACUUM")
                    vacuum_time = time.time() - start_time

                    cursor.execute("PRAGMA page_count")
                    post_vacuum_pages = cursor.fetchone()[0]
                    post_vacuum_size = post_vacuum_pages * page_size / (1024 * 1024)  # Size in MB

                    cursor.execute("PRAGMA freelist_count")
                    post_vacuum_fragmentation = cursor.fetchone()[0] * page_size / (1024 * 1024)  # Fragmentation in MB

                    start_time = time.time()
                    conn.execute("ANALYZE")
                    analyze_time = time.time() - start_time

                    cursor.execute("SELECT COUNT(*) FROM sqlite_stat1")
                    stats_count = cursor.fetchone()[0]

                summary = f"""
Database: {db}
Initial State:
  - Size: {initial_size:.2f} MB
  - Fragmentation: {initial_fragmentation:.2f} MB

VACUUM Operation:
  - Duration: {vacuum_time:.2f} seconds
  - Size after VACUUM: {post_vacuum_size:.2f} MB
  - Fragmentation after VACUUM: {post_vacuum_fragmentation:.2f} MB
  - Space saved: {initial_size - post_vacuum_size:.2f} MB

ANALYZE Operation:
  - Duration: {analyze_time:.2f} seconds
  - Table statistics gathered: {stats_count}

Final Results:
  - Total optimization time: {vacuum_time + analyze_time:.2f} seconds
  - Final database size: {post_vacuum_size:.2f} MB
  - Total space saved: {initial_size - post_vacuum_size:.2f} MB
  - Total fragmentation reduced: {initial_fragmentation - post_vacuum_fragmentation:.2f} MB

Changes Made:
  - Database size change: {post_vacuum_size - initial_size:+.2f} MB
  - Fragmentation change: {post_vacuum_fragmentation - initial_fragmentation:+.2f} MB
"""
                summaries.append(summary)
            except sqlite3.Error as e:
                self.logger.error(f"Error optimizing database {db}: {e}")

        print("\n".join(summaries))
        self.logger.info("Database optimization completed.")

    def backup_database(self, backup_path: str) -> None:
        self.logger.info(f"Backing up databases to {backup_path}")
        try:
            os.makedirs(backup_path, exist_ok=True)
        except OSError as e:
            self.logger.error(f"Failed to create backup directory {backup_path}: {e}")
            return

        dbs = [self.gravity_db_pool.db_path, self.query_db_pool.db_path]
        for db in dbs:
            db_name = os.path.basename(db)
            timestamp = datetime.now().astimezone().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_path, f"{db_name}_backup_{timestamp}.db")

            try:
                start_time = time.time()
                with self._get_connection(db) as conn, closing(sqlite3.connect(backup_file)) as backup:
                    conn.backup(backup)
                backup_time = time.time() - start_time
                backup_size = os.path.getsize(backup_file) / (1024 * 1024)  # Size in MB
                self.logger.info(f"Database {db_name} backup completed in {backup_time:.2f} seconds")
                self.logger.info(f"Backup size: {backup_size:.2f} MB")
            except sqlite3.Error as e:
                self.logger.error(f"Failed to backup database {db}: {e}")
            except OSError as e:
                self.logger.error(f"Failed to access backup file {backup_file}: {e}")

    def get_statistics(self) -> dict[str, Any]:
        self.logger.info("Fetching database statistics...")
        stats = {}
        stats['stats_generated_at'] = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with self._get_connection(self.gravity_db_pool.db_path) as conn:
                cursor = conn.cursor()

                def safe_execute(query: str, default=0) -> Any:
                    try:
                        cursor.execute(query)
                        result = cursor.fetchone()
                        return int(result[0]) if result and result[0] is not None else default
                    except sqlite3.OperationalError as e:
                        self.logger.error(f"Query failed: {query}. Error: {e}")
                        return default

                stats['total_domains'] = safe_execute("SELECT COUNT(*) FROM gravity")
                stats['whitelisted_domains'] = safe_execute(
                    "SELECT COUNT(*) FROM domainlist WHERE type = 0 AND enabled = 1")
                stats['blacklisted_domains'] = safe_execute(
                    "SELECT COUNT(*) FROM domainlist WHERE type = 1 AND enabled = 1")
                stats['regex_whitelist'] = safe_execute(
                    "SELECT COUNT(*) FROM domainlist WHERE type = 2 AND enabled = 1")
                stats['regex_blacklist'] = safe_execute(
                    "SELECT COUNT(*) FROM domainlist WHERE type = 3 AND enabled = 1")
                stats['total_adlists'] = safe_execute("SELECT COUNT(*) FROM adlist WHERE enabled = 1")
                stats['adlist_urls'] = safe_execute(
                    "SELECT COUNT(DISTINCT address) FROM adlist WHERE enabled = 1")

                cursor.execute("SELECT value FROM info WHERE property = 'gravity_count'")
                result = cursor.fetchone()
                stats['gravity_count'] = int(result[0]) if result else 0

                cursor.execute("SELECT value FROM info WHERE property = 'updated'")
                result = cursor.fetchone()
                if result:
                    try:
                        last_updated = datetime.fromtimestamp(int(result[0]), tz=timezone.utc).astimezone()
                        stats['last_gravity_update'] = last_updated.strftime("%m-%d-%Y %I:%M:%S %p")
                    except (ValueError, OverflowError, OSError):
                        stats['last_gravity_update'] = "Invalid timestamp"
                else:
                    stats['last_gravity_update'] = "Unknown"
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching gravity statistics: {e}")

        try:
            with self._get_connection(self.query_db_pool.db_path) as conn:
                cursor = conn.cursor()

                stats['total_queries'] = int(cursor.execute("SELECT COUNT(*) FROM queries").fetchone()[0] or 0)
                stats['blocked_queries'] = int(
                    cursor.execute(f"SELECT COUNT(*) FROM queries WHERE status IN ({BLOCKED_STATUS_IN})").fetchone()[0] or 0)
                stats['forwarded_queries'] = int(
                    cursor.execute("SELECT COUNT(*) FROM queries WHERE status = 2").fetchone()[0] or 0)
                stats['cached_queries'] = int(
                    cursor.execute("SELECT COUNT(*) FROM queries WHERE status = 3").fetchone()[0] or 0)

                if stats['total_queries'] > 0:
                    stats['blocking_percentage'] = (stats['blocked_queries'] / stats['total_queries']) * 100
                else:
                    stats['blocking_percentage'] = 0.0
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching query statistics: {e}")

        self.logger.info("Statistics fetched successfully.")
        return stats

    def clean_old_data(self, days: int = 30) -> None:
        self.logger.info(f"Cleaning data older than {days} days...")
        try:
            with self._get_connection(self.query_db_pool.db_path) as conn:
                cursor = conn.cursor()
                cutoff_timestamp = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())

                cursor.execute("SELECT COUNT(*) FROM query_storage WHERE timestamp < ?", (cutoff_timestamp,))
                queries_to_delete = cursor.fetchone()[0] or 0

                cursor.execute("DELETE FROM query_storage WHERE timestamp < ?", (cutoff_timestamp,))
                conn.commit()

            self.logger.info(f"Deleted {queries_to_delete} old queries.")
            self.logger.info("Old data cleaned successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error cleaning old data: {e}")

    def add_domains_to_list(self, domains: list[str], list_type: int) -> None:
        list_name = self.get_list_type(list_type)
        self.logger.info(f"Adding domains to {list_name}...")
        added_count = 0
        try:
            with self._get_connection(self.gravity_db_pool.db_path) as conn:
                cursor = conn.cursor()
                for domain in domains:
                    normalized_domain = self.normalize_domain(domain)
                    cursor.execute(
                        "INSERT OR IGNORE INTO domainlist (type, domain, enabled, date_added) VALUES (?, ?, 1, strftime('%s', 'now'))",
                        (list_type, normalized_domain)
                    )
                    if cursor.rowcount > 0:
                        added_count += 1
                conn.commit()
            self.logger.info(f"{added_count} domains added to {list_name} successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error adding domains to {list_name}: {e}")

    def remove_domains_from_list(self, domains: list[str], list_type: int) -> None:
        list_name = self.get_list_type(list_type)
        self.logger.info(f"Removing domains from {list_name}...")
        removed_count = 0
        try:
            with self._get_connection(self.gravity_db_pool.db_path) as conn:
                cursor = conn.cursor()
                for domain in domains:
                    normalized_domain = self.normalize_domain(domain)
                    cursor.execute(
                        "DELETE FROM domainlist WHERE type = ? AND domain = ?",
                        (list_type, normalized_domain)
                    )
                    removed_count += cursor.rowcount
                conn.commit()
            self.logger.info(f"{removed_count} domains removed from {list_name} successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error removing domains from {list_name}: {e}")

    def update_gravity(self) -> None:
        self.logger.info("Updating gravity...")
        try:
            start_time = time.time()
            process = subprocess.Popen(
                ["pihole", "-g"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                errors="replace",
                bufsize=1
            )
            if process.stdout:
                for line in process.stdout:
                    self.logger.info(line.strip())
            process.wait()
            update_time = time.time() - start_time
            if process.returncode == 0:
                self.logger.info(f"Gravity updated successfully in {update_time:.2f} seconds.")
            else:
                self.logger.error(f"Gravity update failed after {update_time:.2f} seconds.")
        except FileNotFoundError:
            self.logger.error("Pi-hole command not found. Ensure Pi-hole is installed and accessible.")
        except OSError as e:
            self.logger.error(f"Could not run 'pihole -g': {e}")

    def analyze_top_domains(self, limit: int = 10, blocked: bool = True) -> list[dict[str, Any]]:
        status_codes = BLOCKED_STATUS_CODES if blocked else (2, 3)
        status_label = 'blocked' if blocked else 'allowed'
        self.logger.info(f"Analyzing top {limit} {status_label} domains...")

        try:
            with self._get_connection(self.query_db_pool.db_path) as conn:
                cursor = conn.cursor()
                placeholders = ','.join(['?'] * len(status_codes))
                cursor.execute(f"""
                    SELECT domain, COUNT(*) as count
                    FROM queries
                    WHERE status IN ({placeholders})
                    GROUP BY domain
                    ORDER BY count DESC
                    LIMIT ?
                """, (*status_codes, limit))
                results = [{"domain": row[0], "count": row[1]} for row in cursor.fetchall()]
            self.logger.info(f"Top {status_label} domains analysis completed.")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Error analyzing top {status_label} domains: {e}")
            return []

    def run_custom_query(self, query: str) -> list[dict[str, Any]]:
        self.logger.info("Running custom query...")
        results = []
        try:
            with self._get_connection(self.query_db_pool.db_path) as conn:
                cursor = conn.cursor()
                start_time = time.time()
                cursor.execute(query)
                query_time = time.time() - start_time
                # Statements such as DELETE or UPDATE return no result columns.
                if cursor.description is None:
                    changed = f" {cursor.rowcount} rows changed." if cursor.rowcount >= 0 else ""
                    self.logger.info(f"Custom statement executed in {query_time:.2f} seconds. "
                                     f"It returns no rows.{changed}")
                    return results
                columns = [description[0] for description in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            self.logger.info(f"Custom query executed successfully in {query_time:.2f} seconds.")
        except sqlite3.Error as e:
            self.logger.error(f"Error executing custom query: {e}")
        return results

    def run_simplified_query(self, query_type: str, order_by: str, limit: int) -> list[dict[str, Any]]:
        valid_query_types = ['domains', 'clients']
        if query_type not in valid_query_types:
            self.logger.error(f"Invalid query type: {query_type}. Must be one of {valid_query_types}.")
            return []

        if order_by not in ['queries', 'blocked']:
            self.logger.warning(f"Invalid order_by: {order_by}. Defaulting to 'queries'.")
            order_by = 'queries'

        self.logger.info(f"Running simplified query: type={query_type}, order_by={order_by}, limit={limit}")

        # Both columns come from the fixed allow-lists validated above, so it is
        # safe to embed them directly in the SQL text.
        group_column = 'domain' if query_type == 'domains' else 'client'
        order_column = 'blocked_queries' if order_by == 'blocked' else 'total_queries'

        query = f"""
            SELECT {group_column}, COUNT(*) as total_queries,
                   SUM(CASE WHEN status IN ({BLOCKED_STATUS_IN}) THEN 1 ELSE 0 END) as blocked_queries
            FROM queries
            GROUP BY {group_column}
            ORDER BY {order_column} DESC
            LIMIT ?
        """

        try:
            with self._get_connection(self.query_db_pool.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (limit,))
                columns = [description[0] for description in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            self.logger.info("Simplified query executed successfully.")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Error running simplified query: {e}")
            return []

    def generate_report(self) -> str:
        self.logger.info("Generating comprehensive report...")

        stats = self.get_statistics()
        top_blocked_domains = self.analyze_top_domains(10, blocked=True)
        top_allowed_domains = self.analyze_top_domains(10, blocked=False)

        report = []
        report.append("\nPi-hole Database Report")
        report.append("=======================\n")
        report.append("General Statistics:\n")
        report.append(f"Total domains in gravity: {stats.get('total_domains', 0):,}")
        report.append(f"Whitelisted domains: {stats.get('whitelisted_domains', 0):,}")
        report.append(f"Blacklisted domains: {stats.get('blacklisted_domains', 0):,}")
        report.append(f"Regex whitelist entries: {stats.get('regex_whitelist', 0):,}")
        report.append(f"Regex blacklist entries: {stats.get('regex_blacklist', 0):,}")
        report.append(f"Total enabled adlists: {stats.get('total_adlists', 0):,}")
        report.append(f"Unique adlist URLs: {stats.get('adlist_urls', 0):,}")
        report.append(f"Gravity count: {stats.get('gravity_count', 0):,}")
        report.append(f"Last gravity update: {stats.get('last_gravity_update', 'Unknown')}")
        report.append(f"Total queries: {stats.get('total_queries', 0):,}")
        report.append(f"Blocked queries: {stats.get('blocked_queries', 0):,}")
        report.append(f"Forwarded queries: {stats.get('forwarded_queries', 0):,}")
        report.append(f"Cached queries: {stats.get('cached_queries', 0):,}")
        report.append(f"Blocking percentage: {stats.get('blocking_percentage', 0.0):.2f}%\n")

        report.append("Top 10 Blocked Domains:\n")
        report.append(_grid(top_blocked_domains))
        report.append("\nTop 10 Allowed Domains:\n")
        report.append(_grid(top_allowed_domains))

        report_str = "\n".join(report)
        print(report_str)

        self.generate_charts(top_blocked_domains, top_allowed_domains)

        self.logger.info("Comprehensive report generated.")
        return report_str

    def generate_charts(self, top_blocked_domains: list[dict[str, Any]],
                        top_allowed_domains: list[dict[str, Any]]):
        try:
            plt, sns = _load_pyplot()
        except ImportError:
            self.logger.error("matplotlib is required for charts. Install it with: pip install matplotlib")
            return
        chart_path = 'pihole_domain_stats.png'
        try:
            plt.figure(figsize=(14, 7))
            if sns:
                sns.set_style("whitegrid")

            # Top Blocked Domains
            plt.subplot(1, 2, 1)
            plt.bar([d['domain'] for d in top_blocked_domains],
                    [d['count'] for d in top_blocked_domains],
                    color='red')
            plt.title('Top 10 Blocked Domains')
            plt.xlabel('Domain')
            plt.ylabel('Count')
            plt.xticks(rotation=45, ha='right')

            # Top Allowed Domains
            plt.subplot(1, 2, 2)
            plt.bar([d['domain'] for d in top_allowed_domains],
                    [d['count'] for d in top_allowed_domains],
                    color='green')
            plt.title('Top 10 Allowed Domains')
            plt.xlabel('Domain')
            plt.ylabel('Count')
            plt.xticks(rotation=45, ha='right')

            plt.tight_layout()
            plt.savefig(chart_path)
        except (OSError, ValueError) as e:
            self.logger.error(f"Error generating charts: {e}")
            return
        finally:
            plt.close("all")
        self.logger.info(f"Charts saved as {chart_path}")

    def check_for_updates(self) -> None:
        self.logger.info("Checking for Pi-hole updates...")
        root = os.geteuid() == 0
        if root and not self._refresh_versions():
            return
        try:
            versions = read_versions(VERSIONS_FILE)
            checked = datetime.fromtimestamp(os.path.getmtime(VERSIONS_FILE)).astimezone()
        except OSError as e:
            self.logger.error(f"Could not read Pi-hole's versions: {e}. Pi-hole v5.14 or newer keeps them there.")
            return
        components = components_from(versions)
        # Only the web interface is optional (Pi-hole v5 can be installed without it).
        missing = [name for name in ("Core", "FTL") if name not in [component.name for component in components]]
        if missing:
            self.logger.error(f"{VERSIONS_FILE} has no version for {', '.join(missing)}.")
            return

        for component in components:
            self.logger.info(f"{component.name}: installed {component.installed_text}, "
                             f"latest {component.latest_text} ({component.state})")
        self.logger.info(f"Pi-hole looked these versions up on {checked:%Y-%m-%d at %H:%M}."
                         + ("" if root else " Run with sudo for a fresh check."))
        unknown = [component.name for component in components if component.state == UNKNOWN]
        if unknown:
            self.logger.error(f"Cannot compare versions for {', '.join(unknown)}: the installed or the latest "
                              "version is not known (GitHub unreachable or rate-limited?). Try again later.")
            return
        if versions.get("DOCKER_VERSION", "") != "":
            self.logger.info("This Pi-hole runs in Docker, where every part is updated by replacing the image: "
                             "https://docs.pi-hole.net/docker/upgrading/")
            return
        outdated = [component for component in components if component.state == UPDATE_AVAILABLE]
        if not outdated:
            self.logger.info("Pi-hole is up to date.")
            return

        self.logger.info("Update available: "
                         + ", ".join(f"{component.name} {component.latest_text}" for component in outdated))
        if not root:
            self.logger.info("Updating needs root. Run: sudo pihole -up")
            return
        answer = ask("\nDo you want to update Pi-hole? [y/N]: ")
        if answer is True:
            self.update_pihole(outdated)
        elif answer is None:
            self.logger.info("No answer, so Pi-hole was not updated.")
        else:
            self.logger.info("Update skipped by user.")

    def _refresh_versions(self) -> bool:
        """Have Pi-hole look the versions up now instead of waiting for its daily check."""
        def identity() -> tuple[int, int] | None:
            try:
                status = os.stat(VERSIONS_FILE)
            except OSError:
                return None
            return status.st_ino, status.st_mtime_ns

        before = identity()
        try:
            # No pipes: after a timeout, run() would wait on them for as long as a stuck
            # download started by the command keeps them open.
            subprocess.run(["pihole", "updatechecker"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=120, check=False)
        except FileNotFoundError:
            self.logger.error("Pi-hole command not found. Ensure Pi-hole is installed and accessible.")
            return False
        except subprocess.TimeoutExpired:
            self.logger.error("'pihole updatechecker' did not finish in 120 seconds.")
            return False
        except OSError as e:
            self.logger.error(f"Could not run 'pihole updatechecker': {e}")
            return False
        # The command exits 0 even when it fails; it rewrites the file only when it worked.
        if identity() in (None, before):
            self.logger.error(f"'pihole updatechecker' did not rewrite {VERSIONS_FILE}, "
                              "so the latest versions are not known.")
            return False
        return True

    def update_pihole(self, targets: list[Component]) -> None:
        self.logger.info("Updating Pi-hole with 'pihole -up'...")
        interrupted = []
        # The terminal sends Ctrl+C to Pi-hole's updater as well, and it stops by itself.
        # Python's default would raise here and kill the installer in the middle of its work.
        previous = signal.signal(signal.SIGINT, lambda _signum, _frame: interrupted.append(True))
        try:
            subprocess.run(["pihole", "-up"], check=False)
            self._report_update(targets)
        except FileNotFoundError:
            self.logger.error("Pi-hole command not found. Ensure Pi-hole is installed and accessible.")
        except OSError as e:
            self.logger.error(f"Could not run 'pihole -up': {e}")
        finally:
            signal.signal(signal.SIGINT, previous)
        # Ctrl+C still ends the script here, so no later option runs after it.
        if interrupted:
            raise KeyboardInterrupt

    def _report_update(self, targets: list[Component]) -> None:
        # 'pihole -up' exits 0 whatever happened, so the installed versions decide.
        try:
            now = {component.name: component for component in components_from(read_versions(VERSIONS_FILE))}
        except OSError as e:
            self.logger.error(f"Could not read Pi-hole's versions after the update: {e}")
            return
        behind = [target.name for target in targets
                  if target.name not in now or not now[target.name].has_reached(target)]
        if behind:
            self.logger.error(f"Pi-hole update failed: {', '.join(behind)} not updated. "
                              "See the output of 'pihole -up' above.")
        else:
            self.logger.info("Update finished. Installed now: " + ", ".join(
                f"{target.name} {now[target.name].installed_text}" for target in targets))

    def find_duplicates(self) -> DuplicatePlan | None:
        self.logger.info("Searching for duplicate entries...")
        try:
            with closing(sqlite3.connect(self.gravity_db_pool.db_path, isolation_level=None, timeout=30)) as conn:
                # One read transaction, so rows and group links come from the same moment. It ends
                # here, before any confirmation prompt, so no lock is held while waiting.
                conn.execute("BEGIN")
                try:
                    plan = plan_duplicates(read_domainlist(conn))
                finally:
                    conn.execute("COMMIT")
        except sqlite3.Error as e:
            self.logger.error(f"Error searching for duplicate entries: {e}")
            return None
        self.logger.info(f"Found {len(plan.removals)} duplicate entries.")
        return plan

    def remove_duplicates(self, approved: DuplicatePlan) -> tuple[list[ListEntry], list[ListEntry]] | None:
        """Delete the approved removals that still hold; return (removed, skipped), or None on error.

        The table is read again inside one write transaction. A removal is carried out only
        when the fresh plan contains it unchanged: the same row, text, enabled state, comment
        and groups, with the same unchanged keeper. Anything edited since it was shown is skipped.
        """
        removed: list[ListEntry] = []
        skipped: list[ListEntry] = []
        try:
            with closing(sqlite3.connect(self.gravity_db_pool.db_path, isolation_level=None, timeout=30)) as conn:
                conn.execute("BEGIN IMMEDIATE")
                try:
                    current = set(plan_duplicates(read_domainlist(conn)).removals)
                    for removal in approved.removals:
                        if removal in current:
                            conn.execute("DELETE FROM domainlist WHERE id = ?", (removal.entry.id,))
                            removed.append(removal.entry)
                        else:
                            skipped.append(removal.entry)
                    conn.execute("COMMIT")
                finally:
                    if conn.in_transaction:
                        conn.execute("ROLLBACK")
        except sqlite3.Error as e:
            self.logger.error(f"Nothing was removed. Error removing duplicate entries: {e}")
            return None
        self.logger.info(f"Removed {len(removed)} duplicate entries.")
        return removed, skipped

    @staticmethod
    def normalize_domain(domain: str) -> str:
        # "www." stays: www.example.com and example.com are separate exact entries in Pi-hole.
        domain = domain.lower().strip()
        domain = re.sub(r'^https?://', '', domain)
        domain = re.sub(r'/$', '', domain)
        return domain

    @staticmethod
    def get_list_type(type_value: int) -> str:
        list_types = {
            0: "exact whitelist",
            1: "exact blacklist",
            2: "regex whitelist",
            3: "regex blacklist"
        }
        return list_types.get(type_value, f"unknown list type ({type_value})")

    def find_similar_domains(self, similarity_threshold: int) -> dict[str, list[tuple[str, str, int]]]:
        if not (0 < similarity_threshold <= 100):
            self.logger.error("Similarity threshold must be between 1 and 100.")
            return {}

        self.logger.info(f"Searching for similar domains with a threshold of {similarity_threshold}%...")
        similar_domains = defaultdict(list)

        try:
            with self._get_connection(self.gravity_db_pool.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT domain, type FROM domainlist")
                domains = cursor.fetchall()

            domain_types = defaultdict(set)
            for domain, type_value in domains:
                domain_types[domain].add(type_value)

            def list_type_summary(domain: str) -> str:
                types = sorted(domain_types.get(domain, []))
                if not types:
                    return "unknown list type"
                if len(types) == 1:
                    return self.get_list_type(types[0])
                return ", ".join(self.get_list_type(t) for t in types)

            ratio = _get_ratio()

            def compare_domains(start_index: int, chunk: list[tuple[str, int]]) -> list[tuple[str, str, int]]:
                results = []
                for offset, (domain1, _type1) in enumerate(chunk):
                    i = start_index + offset
                    for domain2, _type2 in domains[i + 1:]:
                        similarity = round(ratio(domain1, domain2))
                        if similarity >= similarity_threshold:
                            results.append((domain1, domain2, similarity))
                return results

            with ThreadPoolExecutor() as executor:
                futures = []
                chunk_size = 500
                for start_index in range(0, len(domains), chunk_size):
                    chunk = domains[start_index:start_index + chunk_size]
                    futures.append(executor.submit(compare_domains, start_index, chunk))

                for future in as_completed(futures):
                    for domain1, domain2, similarity in future.result():
                        similar_domains[domain1].append((domain2, list_type_summary(domain2), similarity))
                        similar_domains[domain2].append((domain1, list_type_summary(domain1), similarity))

            self.logger.info(f"Found {len(similar_domains)} domains with similar matches.")
            return similar_domains
        except sqlite3.Error as e:
            self.logger.error(f"Error finding similar domains: {e}")
            return {}

    def categorize_domains(self) -> dict[str, list[str]]:
        self.logger.info("Categorizing domains...")
        categories = defaultdict(list)

        try:
            with self._get_connection(self.gravity_db_pool.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT domain FROM domainlist")
                domains = [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching domains for categorization: {e}")
            return {}

        extract_suffix = _suffix_extractor()
        for domain in domains:
            categories[extract_suffix(domain)].append(domain)

        self.logger.info(f"Domains categorized into {len(categories)} categories.")
        return dict(categories)

    def analyze_query_trends(self, days: int = 30) -> pd.DataFrame | None:
        self.logger.info(f"Analyzing query trends for the last {days} days...")
        try:
            import pandas as pd
        except ImportError:
            self.logger.error("pandas is required for query-trend analysis. Install it with: pip install pandas")
            return None
        try:
            with self._get_connection(self.query_db_pool.db_path) as conn:
                query = f"""
                    SELECT date(timestamp, 'unixepoch') as date,
                           COUNT(*) as total_queries,
                           SUM(CASE WHEN status IN ({BLOCKED_STATUS_IN}) THEN 1 ELSE 0 END) as blocked_queries
                    FROM queries
                    WHERE timestamp >= strftime('%s', 'now', ?)
                    GROUP BY date
                    ORDER BY date
                """
                df = pd.read_sql_query(query, conn, params=(f"-{days} days",))
        except sqlite3.Error as e:
            self.logger.error(f"Error analyzing query trends: {e}")
            return None

        if df.empty:
            self.logger.warning("No data found for query trends.")
            return df

        df['date'] = pd.to_datetime(df['date'])
        df['allowed_queries'] = df['total_queries'] - df['blocked_queries']
        df['blocking_percentage'] = df.apply(
            lambda row: (row['blocked_queries'] / row['total_queries']) * 100 if row['total_queries'] > 0 else 0.0,
            axis=1
        )

        self.logger.info("Query trend analysis completed.")
        return df

    def plot_query_trends(self, df: pd.DataFrame):
        if df.empty:
            self.logger.warning("No data available to plot query trends.")
            return

        try:
            plt, sns = _load_pyplot()
        except ImportError:
            self.logger.error("matplotlib is required for charts. Install it with: pip install matplotlib")
            return
        chart_path = 'pihole_query_trends.png'
        try:
            plt.figure(figsize=(14, 8))
            if sns:
                sns.set_style("whitegrid")

            # Plot total, blocked, and allowed queries
            plt.plot(df['date'], df['total_queries'], label='Total Queries', marker='o')
            plt.plot(df['date'], df['blocked_queries'], label='Blocked Queries', marker='o')
            plt.plot(df['date'], df['allowed_queries'], label='Allowed Queries', marker='o')

            plt.title('Query Trends Over Time')
            plt.xlabel('Date')
            plt.ylabel('Number of Queries')
            plt.legend()

            # Plot blocking percentage on secondary y-axis
            ax2 = plt.twinx()
            ax2.plot(df['date'], df['blocking_percentage'], color='red', label='Blocking Percentage', marker='o')
            ax2.set_ylabel('Blocking Percentage (%)')
            ax2.legend(loc='lower right')

            plt.tight_layout()
            plt.savefig(chart_path)
        except (OSError, ValueError) as e:
            self.logger.error(f"Error plotting query trends: {e}")
            return
        finally:
            plt.close("all")
        self.logger.info(f"Query trend chart saved as {chart_path}")


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

REPO_URL = "https://github.com/slyfox1186/pihole-regex"
HELP_MAX_WIDTH = 100
# Below this much room beside the option column, descriptions move under the option.
HELP_MIN_TEXT_WIDTH = 36


class Palette:
    def __init__(self, enabled: bool) -> None:
        def code(n: int) -> str:
            return f"\033[{n}m" if enabled else ""

        self.reset, self.bold, self.dim = code(0), code(1), code(2)
        self.red, self.green = code(31), code(32)
        self.magenta, self.cyan = code(35), code(36)


def _color_wanted(stream: Any) -> bool:
    # Follows the NO_COLOR convention (https://no-color.org) and keeps escape
    # codes out of pipes and log files.
    return (stream.isatty() and os.environ.get("NO_COLOR", "") == ""
            and os.environ.get("TERM") != "dumb")


class HelpAction(argparse.Action):
    def __init__(self, option_strings: list[str], dest: str, **_kwargs: Any) -> None:
        super().__init__(option_strings, dest, nargs=0, default=argparse.SUPPRESS)

    def __call__(self, parser, namespace, values, option_string=None):
        print_help(parser.prog)
        parser.exit()


@dataclass(frozen=True)
class Option:
    """One command-line option: the single source for the parser and the help."""
    flags: tuple[str, ...]
    text: str
    note: str = ""
    parser_kwargs: dict[str, Any] = field(default_factory=dict)

    @property
    def value_name(self) -> str:
        return self.parser_kwargs.get("metavar", "")

    @property
    def label(self) -> str:
        # Short flags are padded so the long flags line up in one column.
        short = self.flags[0] + "," if len(self.flags) > 1 else ""
        value = f" {self.value_name}" if self.value_name else ""
        return f"{short:<5} {self.flags[-1]}{value}"


def _option(flags: str, text: str, note: str = "", **parser_kwargs: Any) -> Option:
    return Option(tuple(flags.split(", ")), text, note, parser_kwargs)


def _switch(flags: str, text: str, note: str = "") -> Option:
    return _option(flags, text, note, action="store_true")


def _whole_number(minimum: int, maximum: int | None = None):
    """An argparse type: a whole number no smaller than `minimum`, no larger than `maximum`."""
    def parse(text: str) -> int:
        try:
            value = int(text)
        except ValueError:
            raise argparse.ArgumentTypeError(f"'{text}' is not a whole number") from None
        if maximum is not None and not minimum <= value <= maximum:
            raise argparse.ArgumentTypeError(f"{value} is not from {minimum} to {maximum}")
        if value < minimum:
            raise argparse.ArgumentTypeError(f"{value} is less than {minimum}")
        return value

    return parse


# (title, introduction, options). Texts are kept short enough to sit on one
# line beside the option column in an 80-column terminal.
OPTION_SECTIONS: tuple[tuple[str, str, tuple[Option, ...]], ...] = (
    ("MAINTENANCE", "", (
        _switch("-o, --optimize",
                "Compact and re-index both databases.",
                "VACUUM and ANALYZE, with a size report."),
        _option("-b, --backup",
                "Copy both databases into DIR.",
                "Timestamped files. Creates DIR if missing.", metavar="DIR"),
        _option("-c, --clean",
                "Delete query history older than DAYS days.",
                "Permanent. Runs without asking first.", type=_whole_number(0), metavar="DAYS"),
        _switch("-g, --update-gravity",
                "Rebuild gravity from the adlists.",
                "Runs 'pihole -g'."),
        _switch("-u, --check-updates",
                "Check for a newer Pi-hole release.",
                "Checks Core, Web and FTL. Asks first."),
    )),
    ("STATISTICS AND REPORTS", "", (
        _switch("-s, --stats",
                "Counts for the lists, gravity and queries."),
        _switch("-r, --report",
                "The statistics plus the top 10 domains.",
                "Saves a chart to ./pihole_domain_stats.png"),
        _option("-td, --top-domains",
                "Top N blocked and top N allowed domains.", type=_whole_number(1), metavar="N"),
        _option("-q, --query",
                "Rank domains or clients by query count.",
                choices=["domains", "clients"], metavar="domains|clients"),
        _option("--order-by",
                "With --query, the count to rank by.",
                "Default: queries.", choices=["queries", "blocked"], metavar="queries|blocked"),
        _option("--limit",
                "With --query, how many rows to show.",
                "Default: 10.", type=_whole_number(1), default=10, metavar="N"),
        _option("-aqt, --analyze-query-trends",
                "Daily query totals for the last DAYS days.",
                "Saves a chart to ./pihole_query_trends.png", type=_whole_number(1), metavar="DAYS"),
        _option("-aq, --advanced-query",
                "Run your own SQL on the query database.",
                "Written for SELECT. Quote the statement.", metavar="SQL"),
    )),
    ("DOMAIN LISTS",
     ("DOMAINS is one quoted value with spaces between the names, for example "
      "\"ads.example.com ad.example.net\". Names are stored in lowercase, without a leading "
      "http:// or https:// and a trailing /."), (
        _option("-aw, --add-whitelist", "Add domains to the exact whitelist.", metavar="DOMAINS"),
        _option("-ab, --add-blacklist", "Add domains to the exact blacklist.", metavar="DOMAINS"),
        _option("-rw, --remove-whitelist", "Remove domains from the exact whitelist.", metavar="DOMAINS"),
        _option("-rb, --remove-blacklist", "Remove domains from the exact blacklist.", metavar="DOMAINS"),
        _switch("-rd, --remove-duplicates",
                "Remove exact entries listed twice.",
                "Shows them, can save them, asks first."),
        _switch("-y, --yes",
                "With -rd, remove without asking."),
        _option("-fs, --find-similar",
                "Find entries at least PERCENT% alike.",
                "PERCENT is a whole number from 1 to 100.", type=_whole_number(1, 100), metavar="PERCENT"),
        _switch("-cd, --categorize-domains",
                "Group entries by ending (com, co.uk)."),
    )),
    ("OTHER", "", (
        _option("-h, --help", "Show this help.", action=HelpAction),
    )),
)

# (package, what uses it)
PACKAGES = (
    ("tabulate", "tables for --report, --top-domains, --query, --advanced-query"),
    ("matplotlib", "charts for --report and --analyze-query-trends"),
    ("pandas", "--analyze-query-trends"),
    ("seaborn", "grid styling on the charts"),
    ("rapidfuzz", "a faster --find-similar"),
    ("tld", "a more accurate --categorize-domains"),
)

# (what it does, arguments). Each command fits an 80-column terminal.
EXAMPLES = (
    ("Counts for every list and the query history", "--stats"),
    ("Save a copy of both databases", "--backup ~/pihole-backups"),
    ("Block two domains", '--add-blacklist "ads.example.com ad.example.net"'),
    ("The 5 clients with the most blocked queries", "--query clients --order-by blocked --limit 5"),
    ("Daily query trends for the last 60 days", "--analyze-query-trends 60"),
    ("Your own SQL", '--advanced-query "SELECT COUNT(*) FROM queries"'),
)

NOTES = (
    ("Pi-hole's databases belong to the pihole user. Run this script with sudo, or as a "
     "member of the pihole group."),
    "Several options can be given in one run.",
    "Ctrl+C stops the script with exit code 130. A duplicate removal that is cut short is undone.",
    "Exit codes: 0 done, 1 something failed, 2 bad option, 130 cancelled.",
    "After changing a domain list, run: sudo pihole reloaddns",
    ("Duplicates are exact entries in plain ASCII that differ only in letter case. Pi-hole "
     "stores exact entries in lowercase and never matches a copy with capital letters, so those "
     "copies are removed and the lowercase entry stays (the oldest one if none is lowercase). "
     "Regex and non-ASCII entries are never removed."),
    "Lists: /etc/pihole/gravity.db. Query history: /etc/pihole/pihole-FTL.db.",
    "Color turns off when the output is not a terminal or NO_COLOR is set.",
)


def help_text(prog: str, color: bool, width: int) -> str:
    c = Palette(color)
    head, flag, value, dim, reset = c.bold + c.cyan, c.green, c.magenta, c.dim, c.reset
    width = max(40, min(width, HELP_MAX_WIDTH))
    options = [option for _title, _intro, group in OPTION_SECTIONS for option in group]
    text_column = 2 + max(len(option.label) for option in options) + 2
    side_by_side = width - text_column >= HELP_MIN_TEXT_WIDTH
    if not side_by_side:
        # Deeper than the long flags, which start at column 8.
        text_column = 10
    pad = " " * text_column

    def wrap(text: str, room: int, **kwargs: Any) -> list[str]:
        # Flags, file names and commands stay in one piece.
        return textwrap.wrap(text, room, break_on_hyphens=False, break_long_words=False, **kwargs)

    def colored_label(option: Option) -> str:
        # Mirrors Option.label, whose plain length sets the column padding.
        long_flag = f"{flag}{option.flags[-1]}{reset}"
        name = f" {value}{option.value_name}{reset}" if option.value_name else ""
        if len(option.flags) == 1:
            return f"{' ' * 6}{long_flag}{name}"
        short = option.flags[0]
        return f"{flag}{short}{reset},{' ' * (5 - len(short))}{long_flag}{name}"

    def option_rows(option: Option) -> list[str]:
        text = wrap(option.text, width - text_column)
        notes = [f"{pad}{dim}{line}{reset}" for line in wrap(option.note, width - text_column)]
        if side_by_side:
            gap = " " * (text_column - 2 - len(option.label))
            first = [f"  {colored_label(option)}{gap}{text[0]}"]
            return first + [pad + line for line in text[1:]] + notes
        return [f"  {colored_label(option)}"] + [pad + line for line in text] + notes

    def paragraph(text: str, style: str = "", hang: str = "") -> list[str]:
        return [f"  {style}{line}{reset if style else ''}"
                for line in wrap(text, width - 2, subsequent_indent=hang)]

    lines = [
        "",
        f"{head}{prog}{reset}  Inspect and maintain Pi-hole's databases",
        "",
        f"{head}USAGE{reset}",
        f"  sudo python3 {prog} {value}OPTION{reset} [{value}OPTION{reset} ...]",
    ]
    for title, intro, group in OPTION_SECTIONS:
        lines += ["", f"{head}{title}{reset}"]
        if intro:
            lines += paragraph(intro, dim) + [""]
        for option in group:
            lines += option_rows(option)

    lines += ["", f"{head}EXAMPLES{reset}"]
    for comment, arguments in EXAMPLES:
        lines += [f"  {dim}# {comment}{reset}", f"  sudo python3 {prog} {arguments}"]

    name_width = max(len(name) for name, _use in PACKAGES) + 2
    lines += ["", f"{head}EXTRA PACKAGES{reset}"]
    lines += paragraph("Each one is needed only by the options named beside it. "
                       "Install any of them with: pip install NAME", dim) + [""]
    for name, use in PACKAGES:
        use_lines = wrap(use, width - 2 - name_width)
        lines.append(f"  {flag}{name}{reset}{' ' * (name_width - len(name))}{use_lines[0]}")
        lines += [" " * (2 + name_width) + line for line in use_lines[1:]]

    lines += ["", f"{head}GOOD TO KNOW{reset}"]
    for note in NOTES:
        lines += paragraph(note, hang="  ")
    lines += ["", f"  {dim}{REPO_URL}{reset}", ""]
    return "\n".join(lines)


def print_help(prog: str) -> None:
    print(help_text(prog, _color_wanted(sys.stdout), shutil.get_terminal_size((80, 24)).columns))


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        c = Palette(_color_wanted(sys.stderr))
        self.exit(2, f"{c.red}{c.bold}Error:{c.reset} {message}\n"
                     f"       Run {c.bold}{self.prog} --help{c.reset} to see the options.\n")


def build_parser() -> Parser:
    parser = Parser(add_help=False)
    for _title, _intro, group in OPTION_SECTIONS:
        for option in group:
            parser.add_argument(*option.flags, **option.parser_kwargs)
    return parser


def describe_entry(entry: ListEntry) -> str:
    state = "" if entry.enabled else ", disabled"
    comment = f', comment "{entry.comment}"' if entry.comment else ""
    return f"#{entry.id} {entry.domain} ({PiholeDBAdmin.get_list_type(entry.type)}{state}{comment})"


def duplicate_report(plan: DuplicatePlan) -> list[str]:
    lines = []
    if plan.overlaps:
        lines.append("On both an allow and a deny list (shown only; this alone removes nothing):")
        for allow, deny in plan.overlaps:
            lines += [f"  {describe_entry(allow)}", f"  {describe_entry(deny)}", ""]
    if plan.removals:
        lines.append("Duplicate entries. Pi-hole never matches the copies with capital letters:")
        for removal in plan.removals:
            lines += [f"  remove {describe_entry(removal.entry)}", f"    keep {describe_entry(removal.keeper)}"]
    return lines


def ask(question: str) -> bool | None:
    """True for yes, False for anything else, None when there is no input to read."""
    try:
        return input(question).strip().lower() in ("y", "yes")
    except EOFError:
        return None


def save_report(lines: list[str], logger: logging.Logger) -> None:
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "duplicate-domains.txt")
    if ask(f"\nSave this list to {path}? [y/N]: ") is not True:
        return
    try:
        with open(path, "w", encoding="utf-8") as report:
            report.write("\n".join(lines) + "\n")
    except OSError as e:
        logger.error(f"Could not save the list: {e}")
        return
    print(f"Saved the list to {path}")


def remove_duplicates(admin: PiholeDBAdmin, assume_yes: bool) -> None:
    plan = admin.find_duplicates()
    if plan is None:
        return
    lines = duplicate_report(plan)
    if lines:
        print("\n" + "\n".join(lines))
    if not plan.removals:
        print("No duplicate entries found.")
        return

    if not assume_yes:
        save_report(lines, admin.logger)
        answer = ask(f"\nRemove {len(plan.removals)} entries? [y/N]: ")
        if answer is None:
            print("\nNo answer, so nothing was removed. Add --yes to remove without asking.")
            return
        if not answer:
            print("Nothing was removed.")
            return

    result = admin.remove_duplicates(plan)
    if result is None:
        return
    removed, skipped = result
    for entry in skipped:
        print(f"Skipped {describe_entry(entry)}: it changed after it was shown.")
    print(f"Removed {len(removed)} entries.")
    if removed:
        print("Pi-hole uses the change after you run: sudo pihole reloaddns")


def extend_path() -> None:
    # cron starts jobs with PATH=/usr/bin:/bin. Pi-hole's own cron jobs add these two
    # folders, which hold the pihole command and system tools it calls.
    folders = os.environ.get("PATH", "").split(os.pathsep)
    folders += [folder for folder in ("/usr/sbin", "/usr/local/bin") if folder not in folders]
    os.environ["PATH"] = os.pathsep.join(folders)


class ErrorCounter(logging.Handler):
    """Counts the errors logged; every command reports a failure through the logger."""

    def __init__(self) -> None:
        super().__init__(logging.ERROR)
        self.count = 0

    def emit(self, record: logging.LogRecord) -> None:
        self.count += 1


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        print_help(parser.prog)
        sys.exit(1)

    extend_path()
    admin = PiholeDBAdmin()
    errors = ErrorCounter()
    admin.logger.addHandler(errors)

    try:
        if args.optimize:
            admin.optimize_database()

        if args.backup:
            admin.backup_database(args.backup)

        if args.stats:
            stats = admin.get_statistics()
            print("\nPi-hole Database Statistics:")
            print("============================")
            print(f"Generated on: {stats.get('stats_generated_at', 'Unknown')}\n")

            categories = {
                "Domains": ["total_domains", "whitelisted_domains", "blacklisted_domains",
                            "regex_whitelist", "regex_blacklist"],
                "Adlists": ["total_adlists", "adlist_urls"],
                "Gravity": ["gravity_count", "last_gravity_update"],
                "Queries": ["total_queries", "blocked_queries", "forwarded_queries",
                            "cached_queries", "blocking_percentage"]
            }

            for category, keys in categories.items():
                print(f"\n{category}:")
                print("-" * (len(category) + 1))
                for key in keys:
                    if key in stats:
                        formatted_key = key.replace('_', ' ').title()
                        value = stats[key]
                        if isinstance(value, (int, float)):
                            if key == "blocking_percentage":
                                print(f"  {formatted_key}: {value:.2f}%")
                            else:
                                print(f"  {formatted_key}: {value:,}")
                        else:
                            print(f"  {formatted_key}: {value}")

        if args.clean is not None:
            admin.clean_old_data(args.clean)

        if args.add_whitelist:
            domains = args.add_whitelist.split()
            admin.add_domains_to_list(domains, 0)

        if args.add_blacklist:
            domains = args.add_blacklist.split()
            admin.add_domains_to_list(domains, 1)

        if args.remove_whitelist:
            domains = args.remove_whitelist.split()
            admin.remove_domains_from_list(domains, 0)

        if args.remove_blacklist:
            domains = args.remove_blacklist.split()
            admin.remove_domains_from_list(domains, 1)

        if args.update_gravity:
            admin.update_gravity()

        if args.top_domains:
            top_blocked = admin.analyze_top_domains(args.top_domains, blocked=True)
            top_allowed = admin.analyze_top_domains(args.top_domains, blocked=False)
            print("\nTop Blocked Domains:")
            print(_grid(top_blocked))
            print("\nTop Allowed Domains:")
            print(_grid(top_allowed))

        if args.query:
            query_type = args.query
            order_by = args.order_by or 'queries'
            limit = args.limit

            results = admin.run_simplified_query(query_type, order_by, limit)
            if results:
                print(f"\nTop {limit} {query_type.capitalize()} (ordered by {order_by}):")
                print(_grid(results))

        if args.advanced_query:
            results = admin.run_custom_query(args.advanced_query)
            if results:
                print("\nAdvanced Query Results:")
                print(_grid(results))

        if args.report:
            admin.generate_report()

        if args.check_updates:
            admin.check_for_updates()

        if args.remove_duplicates:
            remove_duplicates(admin, args.yes)

        if args.find_similar:
            similar_domains = admin.find_similar_domains(args.find_similar)
            if similar_domains:
                print("\nSimilar Domains:")
                for domain, matches in similar_domains.items():
                    print(f"\nDomain: {domain}")
                    print("Similar Matches:")
                    for match in matches:
                        print(f"  - {match[0]} (Type: {match[1]}, Similarity: {match[2]}%)")
            else:
                print("No similar domains found.")

        if args.categorize_domains:
            categories = admin.categorize_domains()
            if categories:
                print("\nDomain Categories:")
                for category, domains in categories.items():
                    print(f"\n{category}:")
                    for domain in domains:
                        print(f"  - {domain}")
            else:
                print("No categories found or an error occurred during categorization.")

        if args.analyze_query_trends:
            df = admin.analyze_query_trends(args.analyze_query_trends)
            if df is not None and not df.empty:
                print("\nQuery Trends Analysis:")
                print(df.to_string(index=False))
                admin.plot_query_trends(df)
            else:
                print("No data available for query trends analysis.")

    finally:
        admin.logger.removeHandler(errors)
        admin.close_pools()
    return 1 if errors.count > 0 else 0


def run() -> None:
    # Matches pi.py and adlist.py: Ctrl+C ends with a short message and exit code 130. Database
    # work cut short is rolled back by SQLite, and a duplicate removal by its own transaction.
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    run()
