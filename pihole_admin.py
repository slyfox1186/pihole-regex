#!/usr/bin/env python3
# pihole_admin.py

import argparse
import logging
import matplotlib.pyplot as plt
import os
import pandas as pd
import re
import requests
import sqlite3
import subprocess
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from functools import lru_cache
from fuzzywuzzy import fuzz
from tabulate import tabulate
from typing import Any, Dict, List, Optional, Tuple

# Try to import seaborn, use fallback if not available
try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    logging.warning("Seaborn is not installed. Using matplotlib for plotting. For enhanced visualizations, install seaborn: pip install seaborn")

# Try to import tld, use a simple fallback if not available
try:
    from tld import get_tld
    TLD_AVAILABLE = True
except ImportError:
    TLD_AVAILABLE = False
    logging.warning("tld package is not installed. Using a simple TLD extraction method. For better TLD extraction, install tld: pip install tld")

    def get_tld(url, as_object=False, fail_silently=False):
        """Simple TLD extraction fallback."""
        parts = url.split('.')
        if len(parts) > 1:
            return '.'.join(parts[-2:])
        return url


class DatabaseConnectionPool:
    def __init__(self, db_path: str, max_connections: int = 5):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = []
        self.lock = False  # Simple lock mechanism

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
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_path, f"{db_name}_backup_{timestamp}.db")

            try:
                start_time = time.time()
                with self._get_connection(db) as conn:
                    backup = sqlite3.connect(backup_file)
                    conn.backup(backup)
                    backup.close()
                backup_time = time.time() - start_time
                backup_size = os.path.getsize(backup_file) / (1024 * 1024)  # Size in MB
                self.logger.info(f"Database {db_name} backup completed in {backup_time:.2f} seconds")
                self.logger.info(f"Backup size: {backup_size:.2f} MB")
            except sqlite3.Error as e:
                self.logger.error(f"Failed to backup database {db}: {e}")
            except OSError as e:
                self.logger.error(f"Failed to access backup file {backup_file}: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        self.logger.info("Fetching database statistics...")
        stats = {}
        stats['stats_generated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with self._get_connection(self.gravity_db_pool.db_path) as conn:
                cursor = conn.cursor()

                def safe_execute(query: str, default=0) -> Any:
                    try:
                        cursor.execute(query)
                        result = cursor.fetchone()
                        return int(result[0]) if result and result[0] is not None else default
                    except sqlite3.OperationalError as e:
                        self.logger.warning(f"Query failed: {query}. Error: {e}")
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
                        last_updated = datetime.fromtimestamp(int(result[0]))
                        stats['last_gravity_update'] = last_updated.strftime("%m-%d-%Y %I:%M:%S %p")
                    except (ValueError, OSError):
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
                    cursor.execute("SELECT COUNT(*) FROM queries WHERE status IN (1,4,5,6,7,8,9,10,11)").fetchone()[0] or 0)
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
                cutoff_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())

                cursor.execute("SELECT COUNT(*) FROM query_storage WHERE timestamp < ?", (cutoff_timestamp,))
                queries_to_delete = cursor.fetchone()[0] or 0

                cursor.execute("DELETE FROM query_storage WHERE timestamp < ?", (cutoff_timestamp,))
                conn.commit()

            self.logger.info(f"Deleted {queries_to_delete} old queries.")
            self.logger.info("Old data cleaned successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error cleaning old data: {e}")

    def add_domains_to_list(self, domains: List[str], list_type: int) -> None:
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

    def remove_domains_from_list(self, domains: List[str], list_type: int) -> None:
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
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during gravity update: {e}")

    def analyze_top_domains(self, limit: int = 10, blocked: bool = True) -> List[Dict[str, Any]]:
        status_codes = (1, 4, 5, 6, 7, 8, 9, 10, 11) if blocked else (2, 3)
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

    def run_custom_query(self, query: str) -> List[Dict[str, Any]]:
        self.logger.info("Running custom query...")
        results = []
        try:
            with self._get_connection(self.query_db_pool.db_path) as conn:
                cursor = conn.cursor()
                start_time = time.time()
                cursor.execute(query)
                query_time = time.time() - start_time
                columns = [description[0] for description in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            self.logger.info(f"Custom query executed successfully in {query_time:.2f} seconds.")
        except sqlite3.Error as e:
            self.logger.error(f"Error executing custom query: {e}")
        return results

    def run_simplified_query(self, query_type: str, order_by: str, limit: int) -> List[Dict[str, Any]]:
        valid_query_types = ['domains', 'clients']
        if query_type not in valid_query_types:
            self.logger.error(f"Invalid query type: {query_type}. Must be one of {valid_query_types}.")
            return []

        if order_by not in ['queries', 'blocked']:
            self.logger.warning(f"Invalid order_by: {order_by}. Defaulting to 'queries'.")
            order_by = 'queries'

        self.logger.info(f"Running simplified query: type={query_type}, order_by={order_by}, limit={limit}")

        try:
            with self._get_connection(self.query_db_pool.db_path) as conn:
                cursor = conn.cursor()
                if query_type == 'domains':
                    if order_by == 'blocked':
                        query = """
                            SELECT domain, COUNT(*) as total_queries,
                                   SUM(CASE WHEN status IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as blocked_queries
                            FROM queries
                            GROUP BY domain
                            ORDER BY blocked_queries DESC
                            LIMIT ?
                        """
                    else:
                        query = """
                            SELECT domain, COUNT(*) as total_queries,
                                   SUM(CASE WHEN status IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as blocked_queries
                            FROM queries
                            GROUP BY domain
                            ORDER BY total_queries DESC
                            LIMIT ?
                        """
                elif query_type == 'clients':
                    if order_by == 'blocked':
                        query = """
                            SELECT client, COUNT(*) as total_queries,
                                   SUM(CASE WHEN status IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as blocked_queries
                            FROM queries
                            GROUP BY client
                            ORDER BY blocked_queries DESC
                            LIMIT ?
                        """
                    else:
                        query = """
                            SELECT client, COUNT(*) as total_queries,
                                   SUM(CASE WHEN status IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as blocked_queries
                            FROM queries
                            GROUP BY client
                            ORDER BY total_queries DESC
                            LIMIT ?
                        """

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
        report.append(tabulate(top_blocked_domains, headers="keys", tablefmt="grid"))
        report.append("\nTop 10 Allowed Domains:\n")
        report.append(tabulate(top_allowed_domains, headers="keys", tablefmt="grid"))

        report_str = "\n".join(report)
        print(report_str)

        self.generate_charts(top_blocked_domains, top_allowed_domains)

        self.logger.info("Comprehensive report generated.")
        return report_str

    def generate_charts(self, top_blocked_domains: List[Dict[str, Any]],
                        top_allowed_domains: List[Dict[str, Any]]):
        try:
            plt.figure(figsize=(14, 7))
            if SEABORN_AVAILABLE:
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
            chart_path = 'pihole_domain_stats.png'
            plt.savefig(chart_path)
            plt.close()
            self.logger.info(f"Charts saved as {chart_path}")
        except Exception as e:
            self.logger.error(f"Error generating charts: {e}")

    def check_for_updates(self) -> None:
        self.logger.info("Checking for Pi-hole updates...")
        try:
            # Get current Pi-hole version
            result = subprocess.run(["pihole", "-v"], capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"Failed to get current Pi-hole version: {result.stderr.strip()}")
                return

            current_version_match = re.search(r'Pi-hole version is (\S+)', result.stdout)
            if not current_version_match:
                self.logger.error("Could not parse current Pi-hole version.")
                return

            current_version = current_version_match.group(1).strip()
            self.logger.info(f"Current Pi-hole version: {current_version}")

            # Get latest Pi-hole version from GitHub
            response = requests.get("https://api.github.com/repos/pi-hole/pi-hole/releases/latest", timeout=10)
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch latest Pi-hole version: HTTP {response.status_code}")
                return

            latest_version = response.json().get("tag_name", "").strip()
            if not latest_version:
                self.logger.error("Could not parse latest Pi-hole version from GitHub.")
                return

            self.logger.info(f"Latest Pi-hole version: {latest_version}")

            if current_version != latest_version:
                self.logger.info(f"Update available: {latest_version} (current: {current_version})")
                user_input = input("\nDo you want to update Pi-hole? (y/n): ").lower().strip()
                if user_input == 'y':
                    self.update_pihole()
                else:
                    self.logger.info("Update skipped by user.")
            else:
                self.logger.info("Pi-hole is up to date.")
        except requests.RequestException as e:
            self.logger.error(f"Network error while checking for updates: {e}")
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")

    def update_pihole(self) -> None:
        self.logger.info("Updating Pi-hole...")
        try:
            result = subprocess.run(["pihole", "-up"], capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info("Pi-hole updated successfully.")
                self.logger.debug(f"Update output: {result.stdout}")
                print("Pi-hole has been successfully updated.")
            else:
                self.logger.error("Pi-hole update failed.")
                self.logger.error(f"Update error: {result.stderr}")
                print("Failed to update Pi-hole. Please check the logs for more information.")
        except FileNotFoundError:
            self.logger.error("Pi-hole command not found. Ensure Pi-hole is installed and accessible.")
        except Exception as e:
            self.logger.error(f"Error during Pi-hole update: {e}")
            print(f"An error occurred during the update process: {e}")

    def remove_duplicate_domains(self) -> List[List[Tuple[int, str, str]]]:
        self.logger.info("Searching for duplicate domains...")
        duplicates = []
        try:
            with self._get_connection(self.gravity_db_pool.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT id, domain, type FROM domainlist")
                all_domains = cursor.fetchall()

                domain_map = defaultdict(list)
                for id, domain, type_value in all_domains:
                    normalized = self.normalize_domain(domain)
                    domain_map[normalized].append((id, domain, self.get_list_type(type_value)))

                for domain, entries in domain_map.items():
                    if len(entries) > 1:
                        duplicates.append(entries)

            total_duplicates = sum(len(group) - 1 for group in duplicates)
            self.logger.info(f"Found {total_duplicates} duplicate entries.")
            return duplicates
        except sqlite3.Error as e:
            self.logger.error(f"Error searching for duplicate domains: {e}")
            return []

    @staticmethod
    def normalize_domain(domain: str) -> str:
        domain = domain.lower().strip()
        domain = re.sub(r'^(https?://)?(www\.)?', '', domain)
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

    def find_similar_domains(self, similarity_threshold: int) -> Dict[str, List[Tuple[str, str, int]]]:
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

            def compare_domains(start_index: int, chunk: List[Tuple[str, int]]) -> List[Tuple[str, str, int]]:
                results = []
                for offset, (domain1, _type1) in enumerate(chunk):
                    i = start_index + offset
                    for domain2, _type2 in domains[i + 1:]:
                        similarity = fuzz.ratio(domain1, domain2)
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
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return {}

    def get_list_type_by_domain(self, domain: str) -> str:
        try:
            with self._get_connection(self.gravity_db_pool.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT type FROM domainlist WHERE domain = ? LIMIT 1", (domain,))
                result = cursor.fetchone()
                if result:
                    return self.get_list_type(result[0])
                else:
                    return "unknown list type"
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving list type for domain {domain}: {e}")
            return "unknown list type"

    def categorize_domains(self) -> Dict[str, List[str]]:
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

        for domain in domains:
            try:
                tld_info = get_tld(domain, as_object=True, fail_silently=True)
                if tld_info:
                    category = tld_info.suffix
                else:
                    category = "Unknown"
            except Exception:
                category = "Unknown"
            categories[category].append(domain)

        self.logger.info(f"Domains categorized into {len(categories)} categories.")
        return dict(categories)

    def analyze_query_trends(self, days: int = 30) -> Optional[pd.DataFrame]:
        self.logger.info(f"Analyzing query trends for the last {days} days...")
        try:
            with self._get_connection(self.query_db_pool.db_path) as conn:
                query = f"""
                    SELECT date(timestamp, 'unixepoch') as date,
                           COUNT(*) as total_queries,
                           SUM(CASE WHEN status IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as blocked_queries
                    FROM queries
                    WHERE timestamp >= strftime('%s', 'now', '-{days} days')
                    GROUP BY date
                    ORDER BY date
                """
                df = pd.read_sql_query(query, conn)
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
            plt.figure(figsize=(14, 8))
            if SEABORN_AVAILABLE:
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
            chart_path = 'pihole_query_trends.png'
            plt.savefig(chart_path)
            plt.close()
            self.logger.info(f"Query trend chart saved as {chart_path}")
        except Exception as e:
            self.logger.error(f"Error plotting query trends: {e}")


def main():
    script_name = os.path.basename(sys.argv[0])

    examples = f"""
Examples:
  {script_name} --add-blacklist "badsite.com malware.org"
  {script_name} --add-whitelist "example.com another-example.com"
  {script_name} --advanced-query "SELECT domain, COUNT(*) as count FROM queries GROUP BY domain ORDER BY count DESC LIMIT 10"
  {script_name} --analyze-query-trends 60
  {script_name} --backup /path/to/backup/folder
  {script_name} --categorize-domains
  {script_name} --check-updates
  {script_name} --clean 30
  {script_name} --find-similar 90
  {script_name} --optimize
  {script_name} --query clients --order-by blocked --limit 5
  {script_name} --query domains --limit 10
  {script_name} --remove-blacklist "badsite.com"
  {script_name} --remove-duplicates
  {script_name} --remove-whitelist "example.com"
  {script_name} --report
  {script_name} --stats
  {script_name} --top-domains 20
  {script_name} --update-gravity
    """

    parser = argparse.ArgumentParser(description="Pi-hole Database Administrator",
                                     epilog=examples,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("--optimize", "-o", action="store_true", help="Optimize the database")
    parser.add_argument("--backup", "-b", metavar="PATH", help="Backup the database to the specified path")
    parser.add_argument("--stats", "-s", action="store_true", help="Get database statistics")
    parser.add_argument("--clean", "-c", type=int, metavar="DAYS", help="Clean data older than specified days")
    parser.add_argument("--add-whitelist", "-aw", type=str, help="Add domains to whitelist (space-separated, enclose in quotes)")
    parser.add_argument("--add-blacklist", "-ab", type=str, help="Add domains to blacklist (space-separated, enclose in quotes)")
    parser.add_argument("--remove-whitelist", "-rw", type=str, help="Remove domains from whitelist (space-separated, enclose in quotes)")
    parser.add_argument("--remove-blacklist", "-rb", type=str, help="Remove domains from blacklist (space-separated, enclose in quotes)")
    parser.add_argument("--update-gravity", "-g", action="store_true", help="Update gravity")
    parser.add_argument("--top-domains", "-td", type=int, metavar="LIMIT", help="Analyze top domains")
    parser.add_argument("--query", "-q", choices=['domains', 'clients'], help="Run a simplified query on the Pi-hole database. Types: domains, clients")
    parser.add_argument("--order-by", choices=['queries', 'blocked'], help="Order results by total queries or blocked queries")
    parser.add_argument("--limit", type=int, default=10, help="Limit the number of results (default: 10)")
    parser.add_argument("--advanced-query", "-aq", metavar="QUERY", help="Run an advanced SQL query on the Pi-hole database")
    parser.add_argument("--report", "-r", action="store_true", help="Generate a comprehensive report")
    parser.add_argument("--check-updates", "-u", action="store_true", help="Check for Pi-hole updates")
    parser.add_argument("--remove-duplicates", "-rd", action="store_true", help="Remove duplicate domains across all lists")
    parser.add_argument("--find-similar", "-fs", type=int, metavar="THRESHOLD",
                        help="Find similar domains based on the specified similarity threshold (e.g., 90 for 90% similarity)")
    parser.add_argument("--categorize-domains", "-cd", action="store_true", help="Categorize domains into categories")
    parser.add_argument("--analyze-query-trends", "-aqt", type=int, metavar="DAYS",
                        help="Analyze query trends for the last specified number of days")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    admin = PiholeDBAdmin()

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
            print(tabulate(top_blocked, headers="keys", tablefmt="grid"))
            print("\nTop Allowed Domains:")
            print(tabulate(top_allowed, headers="keys", tablefmt="grid"))

        if args.query:
            query_type = args.query
            order_by = args.order_by or 'queries'
            limit = args.limit

            results = admin.run_simplified_query(query_type, order_by, limit)
            if results:
                print(f"\nTop {limit} {query_type.capitalize()} (ordered by {order_by}):")
                print(tabulate(results, headers="keys", tablefmt="grid"))

        if args.advanced_query:
            results = admin.run_custom_query(args.advanced_query)
            if results:
                print("\nAdvanced Query Results:")
                print(tabulate(results, headers="keys", tablefmt="grid"))

        if args.report:
            admin.generate_report()

        if args.check_updates:
            admin.check_for_updates()

        if args.remove_duplicates:
            duplicate_groups = admin.remove_duplicate_domains()
            if duplicate_groups:
                print("\nFound Duplicate Domain Groups:")
                for i, group in enumerate(duplicate_groups, start=1):
                    print(f"\nGroup {i}:")
                    for entry in group:
                        print(f"  - {entry[1]} (ID: {entry[0]}, Type: {entry[2]})")

                create_log = input("\nDo you want to create an output log file with these results? (y/n): ").lower().strip()
                if create_log == 'y':
                    script_dir = os.path.dirname(os.path.realpath(__file__))
                    log_file_path = os.path.join(script_dir, 'duplicate-domains.txt')
                    try:
                        with open(log_file_path, 'w') as log_file:
                            log_file.write("Found Duplicate Domain Groups:\n")
                            for i, group in enumerate(duplicate_groups, start=1):
                                log_file.write(f"\nGroup {i}:\n")
                                for entry in group:
                                    log_file.write(f"  - {entry[1]} (ID: {entry[0]}, Type: {entry[2]})\n")
                        print(f"Log file created at: {log_file_path}")
                    except OSError as e:
                        admin.logger.error(f"Failed to write log file: {e}")
            else:
                print("No duplicate domains found.")

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
        admin.close_pools()


if __name__ == "__main__":
    main()
