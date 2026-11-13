#!/usr/bin/env python3
"""Add, remove, browse, search and back up the SlyFox1186 domain lists in Pi-hole.

Uses only the Python standard library because it is started with
`sudo python3 pi.py`, and sudo selects the system Python, which has no
third-party packages. Supports Python 3.9+ and Pi-hole v5 and v6 databases.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.request
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import NoReturn

VERSION = "3.0.0"
DEFAULT_DB = "/etc/pihole/gravity.db"
REPO_URL = "https://github.com/slyfox1186/pihole-regex"
RAW_BASE = "https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains"
USER_AGENT = f"pihole-regex/{VERSION} (+{REPO_URL})"
DB_TIMEOUT = 30
HTTP_TIMEOUT = 20
PREVIEW_LIMIT = 12

EXIT_OK, EXIT_ERROR, EXIT_USAGE, EXIT_CANCELLED = 0, 1, 2, 130


class AppError(Exception):
    """A failure with a message meant for the user; nothing has been changed."""


@dataclass(frozen=True)
class Kind:
    """One of Pi-hole's four domain lists and the repository file that feeds it."""
    type: int
    key: str
    title: str
    file: str
    # Comments of entries this script adds start with this tag, which is how
    # its entries are told apart from ones the user added.
    tag: str
    aliases: tuple[str, ...]

    @property
    def url(self) -> str:
        return f"{RAW_BASE}/{self.file}"


KINDS = (
    Kind(0, "exact-allow", "Exact allowlist", "exact-whitelist.sql", "SlyEWL",
         ("ea", "exact-whitelist", "allow", "whitelist")),
    Kind(1, "exact-deny", "Exact denylist", "exact-blacklist.sql", "SlyEBL",
         ("ed", "exact-blacklist", "deny", "blacklist")),
    Kind(2, "regex-allow", "Regex allowlist", "regex-whitelist.sql", "SlyRWL",
         ("ra", "regex-whitelist")),
    Kind(3, "regex-deny", "Regex denylist", "regex-blacklist.sql", "SlyRBL",
         ("rd", "regex-blacklist")),
)
KIND_BY_TYPE = {kind.type: kind for kind in KINDS}
KIND_BY_NAME = {name: kind for kind in KINDS for name in (kind.key, *kind.aliases)}


# ---------------------------------------------------------------------------
# Terminal output
# ---------------------------------------------------------------------------

class Palette:
    def __init__(self, enabled: bool) -> None:
        def code(n: int) -> str:
            return f"\033[{n}m" if enabled else ""

        self.reset, self.bold, self.dim = code(0), code(1), code(2)
        self.red, self.green, self.yellow = code(31), code(32), code(33)
        self.blue, self.magenta, self.cyan = code(34), code(35), code(36)


def _color_wanted(argv: list[str]) -> bool:
    # Follows the NO_COLOR convention (https://no-color.org) and keeps escape
    # codes out of pipes and log files.
    return (sys.stdout.isatty() and os.environ.get("NO_COLOR", "") == ""
            and os.environ.get("TERM") != "dumb" and "--no-color" not in argv)


C = Palette(_color_wanted(sys.argv))
INTERACTIVE = sys.stdin.isatty() and sys.stdout.isatty()
UNICODE = str(getattr(sys.stdout, "encoding", None) or "").lower().replace("-", "") in ("utf8", "utf16")
RULE = "─" if UNICODE else "-"


def term_width() -> int:
    return shutil.get_terminal_size((100, 24)).columns if sys.stdout.isatty() else 10_000


def heading(text: str) -> None:
    print(f"\n{C.bold}{C.cyan}{text}{C.reset}")


def success(text: str) -> None:
    print(f"{C.green}{text}{C.reset}")


def note(text: str) -> None:
    print(f"{C.dim}{text}{C.reset}")


def warn(text: str) -> None:
    sys.stdout.flush()  # keep stdout and stderr in order when both are piped
    print(f"{C.yellow}Warning:{C.reset} {text}", file=sys.stderr)


def error(text: str) -> None:
    sys.stdout.flush()
    print(f"{C.red}{C.bold}Error:{C.reset} {text}", file=sys.stderr)


def fit(text: str, width: int, *, middle: bool = False) -> str:
    if width < 8 or len(text) <= width:
        return text
    if middle:
        keep = width - 3
        return f"{text[:keep // 2]}...{text[-(keep - keep // 2):]}"
    return text[:width - 3] + "..."


def render_table(headers: list[str], rows: list[list[str | tuple[str, str]]], *, flex: int) -> str:
    """Align columns on visible text; column `flex` absorbs the terminal width."""
    plain = [[c if isinstance(c, str) else c[0] for c in row] for row in rows]
    widths = [max([len(h)] + [len(r[i]) for r in plain]) for i, h in enumerate(headers)]
    fixed = sum(w for i, w in enumerate(widths) if i != flex) + 2 * len(headers) + 2
    widths[flex] = max(12, min(widths[flex], term_width() - fixed))
    lines = ["  " + "  ".join(f"{C.dim}{h:<{widths[i]}}{C.reset}" for i, h in enumerate(headers)).rstrip()]
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            text, color = (cell, "") if isinstance(cell, str) else cell
            text = fit(text, widths[i])
            pad = " " * (widths[i] - len(text))
            cells.append(f"{color}{text}{C.reset if color else ''}{pad}")
        lines.append(("  " + "  ".join(cells)).rstrip())
    return "\n".join(lines)


def page(text: str) -> None:
    """Show long output through `less` in a terminal so it can be scrolled."""
    height = shutil.get_terminal_size((100, 24)).lines
    pager = shutil.which("less")
    if INTERACTIVE and pager and text.count("\n") > height - 2:
        # -R keeps colors, -F exits when it fits, -X leaves the text on screen.
        subprocess.run([pager, "-RFX"], input=text.encode(), check=False)
    else:
        print(text)


def clear_screen() -> None:
    if INTERACTIVE:
        # Home and clear without erasing scrollback.
        print("\033[H\033[2J", end="")


def ask(prompt: str) -> str:
    return input(f"{C.bold}{prompt}{C.reset} ").strip()


def confirm(question: str, *, default: bool, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        warn(f"{question} Not asked because input is not a terminal; pass --yes to agree.")
        return False
    hint = "[Y/n]" if default else "[y/N]"
    while True:
        reply = input(f"{C.yellow}{question}{C.reset} {hint} ").strip().lower()
        if not reply:
            return default
        if reply in ("y", "yes"):
            return True
        if reply in ("n", "no"):
            return False
        print("Please answer y or n.")


def format_date(value: object) -> str:
    """Pi-hole stores epoch integers; versions of this script before 2026 stored ISO strings."""
    if value in (None, ""):
        return "-"
    try:
        return datetime.fromtimestamp(int(str(value)), tz=timezone.utc).astimezone().strftime("%Y-%m-%d")
    except (ValueError, OSError, OverflowError):
        return str(value)[:10]


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SourceEntry:
    domain: str
    note: str

    def comment(self, kind: Kind) -> str:
        return f"{kind.tag} - {self.note}" if self.note else kind.tag


@dataclass(frozen=True)
class Row:
    id: int
    type: int
    domain: str
    enabled: bool
    comment: str
    added: object


def fetch_source(kind: Kind) -> list[SourceEntry]:
    request = urllib.request.Request(kind.url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            text = response.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise AppError(f"Could not download {kind.url}: {getattr(exc, 'reason', exc)}") from exc
    entries: dict[str, SourceEntry] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        domain, _, comment = line.partition(" -- ")
        domain = domain.strip()
        if domain and domain not in entries:
            entries[domain] = SourceEntry(domain, comment.strip())
    if not entries:
        raise AppError(f"{kind.url} contained no entries.")
    return list(entries.values())


def fetch_sources(kinds: list[Kind]) -> dict[int, list[SourceEntry]]:
    with ThreadPoolExecutor(max_workers=len(kinds)) as pool:
        results = dict(zip((k.type for k in kinds), pool.map(fetch_source, kinds)))
    return results


def is_ours(row: Row, kind: Kind, source_domains: set[str]) -> bool:
    # Older versions of this script left the comment empty when the source
    # line had no note, so an empty comment on a source domain counts as ours.
    return row.comment.startswith(kind.tag) or (row.comment == "" and row.domain in source_domains)


class PiholeDB:
    def __init__(self, path: str, *, write: bool) -> None:
        self.path = Path(path)
        if not self.path.is_file():
            raise AppError(f"Pi-hole's database was not found at {self.path}. "
                           "Is Pi-hole installed on this machine? (--database sets another path)")
        needed = os.W_OK if write else os.R_OK
        if not os.access(self.path, needed) or (write and not os.access(self.path.parent, os.W_OK)):
            raise AppError(f"{'Changing' if write else 'Reading'} Pi-hole's lists needs root. "
                           "Run it again with sudo.")
        mode = "rw" if write else "ro"
        self.conn = sqlite3.connect(f"{self.path.resolve().as_uri()}?mode={mode}", uri=True,
                                    timeout=DB_TIMEOUT, isolation_level=None)
        tables = {r[0] for r in self.conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        if "domainlist" not in tables:
            self.conn.close()
            raise AppError(f"{self.path} is not a Pi-hole gravity database (it has no domainlist table).")

    def close(self) -> None:
        self.conn.close()

    def rows(self, types: list[int] | None = None, like: str | None = None) -> list[Row]:
        query = "SELECT id, type, domain, enabled, COALESCE(comment, ''), date_added FROM domainlist WHERE 1"
        params: list[object] = []
        if types is not None:
            query += f" AND type IN ({','.join('?' * len(types))})"
            params += types
        if like is not None:
            escaped = like.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            query += " AND (domain LIKE ? ESCAPE '\\' OR comment LIKE ? ESCAPE '\\')"
            params += [f"%{escaped}%"] * 2
        query += " ORDER BY type, domain COLLATE NOCASE"
        return [Row(int(i), int(t), str(d), bool(e), str(c), a)
                for i, t, d, e, c, a in self.conn.execute(query, params)]

    @contextmanager
    def transaction(self) -> Iterator[None]:
        # IMMEDIATE takes the write lock up front, so a busy database fails
        # before anything is changed rather than halfway through.
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            yield
        except BaseException:
            self.conn.execute("ROLLBACK")
            raise
        self.conn.execute("COMMIT")


def open_db(path: str, *, write: bool) -> PiholeDB:
    try:
        return PiholeDB(path, write=write)
    except sqlite3.DatabaseError as exc:
        raise AppError(f"Could not open {path}: {exc}") from exc


# ---------------------------------------------------------------------------
# Changes: planned, shown, then written in one transaction
# ---------------------------------------------------------------------------

@dataclass
class Plan:
    add: dict[int, list[SourceEntry]]
    remove: dict[int, list[Row]]
    # Entries this script added whose comment no longer matches the repository: older
    # versions left it empty, and the repository may since have corrected the note.
    tag: dict[int, list[tuple[Row, SourceEntry]]] = field(default_factory=dict)

    @property
    def empty(self) -> bool:
        return not any(self.add.values()) and not any(self.remove.values()) and not any(self.tag.values())

    def counts(self) -> tuple[int, int, int]:
        return (sum(map(len, self.add.values())), sum(map(len, self.remove.values())),
                sum(map(len, self.tag.values())))

    def show(self, verbose: bool) -> None:
        width = term_width() - 10
        for kind in KINDS:
            adds, removes = self.add.get(kind.type, []), self.remove.get(kind.type, [])
            tags = self.tag.get(kind.type, [])
            if not adds and not removes and not tags:
                continue
            parts = [f"{C.green}+{len(adds)} to add{C.reset}" if adds else "",
                     f"{C.red}-{len(removes)} to remove{C.reset}" if removes else "",
                     f"{C.blue}{len(tags)} comment{'' if len(tags) == 1 else 's'} to update{C.reset}"
                     if tags else ""]
            heading(f"{kind.title}")
            print("  " + "   ".join(p for p in parts if p))
            limit = None if verbose else PREVIEW_LIMIT
            for sign, color, names in (("+", C.green, [e.domain for e in adds]),
                                       ("-", C.red, [r.domain for r in removes])):
                for name in names[:limit]:
                    print(f"    {color}{sign}{C.reset} {fit(name, width, middle=True)}")
                if limit is not None and len(names) > limit:
                    note(f"    ... and {len(names) - limit} more (--verbose shows all)")


def apply_plan(db: PiholeDB, plan: Plan) -> tuple[int, int, int]:
    """Write the plan in one transaction; return how many entries were added, removed and updated."""
    try:
        with db.transaction():
            added = 0
            for type_, entries in plan.add.items():
                kind = KIND_BY_TYPE[type_]
                added += max(db.conn.executemany(
                    "INSERT OR IGNORE INTO domainlist (type, domain, enabled, comment, date_added, date_modified) "
                    "VALUES (?, ?, 1, ?, CAST(strftime('%s', 'now') AS INTEGER), "
                    "CAST(strftime('%s', 'now') AS INTEGER))",
                    [(type_, e.domain, e.comment(kind)) for e in entries]).rowcount, 0)
            # Only rewrite or remove an entry whose comment still reads as it did when the plan
            # was made, so an entry someone edits in Pi-hole meanwhile is left alone.
            updated = db.conn.executemany(
                "UPDATE domainlist SET comment = ? WHERE id = ? AND COALESCE(comment, '') = ?",
                [(entry.comment(KIND_BY_TYPE[type_]), row.id, row.comment)
                 for type_, pairs in plan.tag.items() for row, entry in pairs]).rowcount
            # Pi-hole's tr_domainlist_delete trigger removes the group links.
            removed = db.conn.executemany(
                "DELETE FROM domainlist WHERE id = ? AND COALESCE(comment, '') = ?",
                [(row.id, row.comment) for rows in plan.remove.values() for row in rows]).rowcount
    except sqlite3.OperationalError as exc:
        if "locked" in str(exc) or "busy" in str(exc):
            raise AppError(f"Pi-hole's database stayed busy for {DB_TIMEOUT} seconds "
                           "(gravity may be running). Try again shortly.") from exc
        raise AppError(f"Pi-hole's database refused the change: {exc}") from exc
    return added, max(removed, 0), max(updated, 0)


def reload_pihole(args: argparse.Namespace) -> int:
    if args.no_reload:
        note(f"Pi-hole uses the change after {C.bold}sudo pihole reloaddns{C.reset}{C.dim} runs.")
        return EXIT_OK
    if not confirm("Reload Pi-hole now so the change takes effect?", default=True, assume_yes=args.yes):
        note("Skipped. Run 'sudo pihole reloaddns' when you are ready.")
        return EXIT_OK
    pihole = shutil.which("pihole") or "/usr/local/bin/pihole"
    try:
        result = subprocess.run([pihole, "reloaddns"], check=False, capture_output=True, text=True)
    except OSError as exc:
        error(f"Could not run {pihole}: {exc}. Run 'sudo pihole reloaddns' yourself.")
        return EXIT_ERROR
    if result.returncode != 0:
        error(f"pihole reloaddns failed (exit {result.returncode}): "
              f"{(result.stderr or result.stdout).strip()}")
        return EXIT_ERROR
    success("Pi-hole reloaded. The change is live.")
    return EXIT_OK


def run_plan(args: argparse.Namespace, db: PiholeDB, plan: Plan, *, ask_first: str | None) -> int:
    try:
        if plan.empty:
            success("\nNothing to change. Pi-hole already matches.")
            return EXIT_OK
        plan.show(args.verbose)
        added, removed, tagged = plan.counts()
        if args.dry_run:
            print(f"\n{C.cyan}Dry run:{C.reset} {added} would be added, {removed} removed and {tagged} comments updated. "
                  "Nothing was changed.")
            return EXIT_OK
        print()
        if ask_first and not confirm(ask_first, default=False, assume_yes=args.yes):
            note("Cancelled. Nothing was changed.")
            return EXIT_OK
        planned = added + removed + tagged
        added, removed, updated = apply_plan(db, plan)
    finally:
        db.close()
    success(f"Saved: {added} added, {removed} removed" + (f", {updated} comments updated." if updated else "."))
    skipped = planned - added - removed - updated
    if skipped:
        note(f"{skipped} entr{'y' if skipped == 1 else 'ies'} changed in Pi-hole while this ran "
             "and were left as they are.")
    # Comment updates do not change filtering, so Pi-hole does not need to reload for them.
    return reload_pihole(args) if added or removed else EXIT_OK


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def parse_kinds(values: list[str]) -> list[Kind]:
    tokens = [t.strip().lower() for v in values for t in v.replace(",", " ").split()]
    if not tokens or "all" in tokens:
        return list(KINDS)
    chosen: list[Kind] = []
    for token in tokens:
        kind = KIND_BY_NAME.get(token)
        if kind is None:
            raise AppError(f"Unknown list '{token}'. Use exact-allow, exact-deny, regex-allow, "
                           "regex-deny or all (short forms: ea, ed, ra, rd).")
        if kind not in chosen:
            chosen.append(kind)
    return sorted(chosen, key=lambda k: k.type)


def cmd_add(args: argparse.Namespace, kinds: list[Kind]) -> int:
    db = open_db(args.database, write=not args.dry_run)
    try:
        note("Downloading the lists from GitHub...")
        sources = fetch_sources(kinds)
        existing = db.rows([k.type for k in kinds])
    except BaseException:
        db.close()
        raise
    plan = Plan({}, {})
    for kind in kinds:
        source = sources[kind.type]
        names = {e.domain for e in source}
        present = {r.domain for r in existing if r.type == kind.type}
        plan.add[kind.type] = [e for e in source if e.domain not in present]
        # Entries this script added that the repository has since dropped.
        plan.remove[kind.type] = [r for r in existing if r.type == kind.type
                                  and r.comment.startswith(kind.tag) and r.domain not in names]
        by_domain = {e.domain: e for e in source}
        plan.tag[kind.type] = [(r, by_domain[r.domain]) for r in existing if r.type == kind.type
                               and r.domain in names and (r.comment == "" or r.comment.startswith(kind.tag))
                               and r.comment != by_domain[r.domain].comment(kind)]
    return run_plan(args, db, plan, ask_first=None)


def cmd_remove(args: argparse.Namespace, kinds: list[Kind]) -> int:
    db = open_db(args.database, write=not args.dry_run)
    try:
        note("Downloading the lists from GitHub to recognise older entries...")
        try:
            sources = {t: {e.domain for e in entries} for t, entries in fetch_sources(kinds).items()}
        except AppError as exc:
            warn(f"{exc}\n         Only entries tagged by this script can be found without it.")
            sources = {k.type: set() for k in kinds}
        rows = db.rows([k.type for k in kinds])
    except BaseException:
        db.close()
        raise
    plan = Plan({}, {k.type: [r for r in rows if r.type == k.type and is_ours(r, k, sources[k.type])]
                     for k in kinds})
    _, total, _ = plan.counts()
    question = f"Remove these {total} entries from Pi-hole?"
    return run_plan(args, db, plan, ask_first=question)


def cmd_list(args: argparse.Namespace, kinds: list[Kind]) -> int:
    db = open_db(args.database, write=False)
    try:
        rows = db.rows([k.type for k in kinds])
    finally:
        db.close()
    blocks = []
    for kind in kinds:
        mine = [r for r in rows if r.type == kind.type]
        title = f"{C.bold}{C.cyan}{kind.title}{C.reset}  {C.dim}{len(mine)} entries{C.reset}"
        if not mine:
            blocks.append(f"\n{title}\n  {C.dim}(empty){C.reset}")
            continue
        table = render_table(
            ["Domain", "Status", "Added by", "Added", "Comment"],
            [[r.domain,
              ("on", C.green) if r.enabled else ("off", C.yellow),
              ("this repo", C.cyan) if r.comment.startswith(kind.tag) else ("you", C.magenta),
              format_date(r.added),
              r.comment.split(" - ", 1)[1] if r.comment.startswith(kind.tag + " - ") else r.comment]
             for r in mine],
            flex=4)
        blocks.append(f"\n{title}\n{table}")
    page("\n".join(blocks))
    return EXIT_OK


def cmd_search(args: argparse.Namespace, term: str) -> int:
    if not term.strip():
        raise AppError("Give some text to search for.")
    db = open_db(args.database, write=False)
    try:
        rows = db.rows(like=term.strip())
    finally:
        db.close()
    if not rows:
        print(f"\nNo entries match {C.bold}{term}{C.reset}.")
        return EXIT_OK
    table = render_table(
        ["Domain", "List", "Status", "Added", "Comment"],
        [[r.domain, KIND_BY_TYPE[r.type].title if r.type in KIND_BY_TYPE else str(r.type),
          ("on", C.green) if r.enabled else ("off", C.yellow), format_date(r.added), r.comment]
         for r in rows],
        flex=4)
    page(f"\n{C.bold}{C.cyan}{len(rows)} match{'es' if len(rows) != 1 else ''} for '{term}'{C.reset}\n{table}")
    return EXIT_OK


def cmd_stats(args: argparse.Namespace) -> int:
    db = open_db(args.database, write=False)
    try:
        rows = db.rows()
    finally:
        db.close()
    try:
        note("Downloading the lists from GitHub to compare...")
        sources: dict[int, list[SourceEntry]] | None = fetch_sources(list(KINDS))
    except AppError as exc:
        warn(f"{exc}\n         Repository counts are left out.")
        sources = None
    table_rows: list[list[str | tuple[str, str]]] = []
    for kind in KINDS:
        mine = [r for r in rows if r.type == kind.type]
        names = {e.domain for e in sources[kind.type]} if sources is not None else set()
        ours = [r for r in mine if is_ours(r, kind, names)]
        if sources is None:
            coverage: str | tuple[str, str] = "-"
        else:
            have = len(names & {r.domain for r in mine})
            coverage = (f"{have}/{len(names)}", C.green if have == len(names) else C.yellow)
        table_rows.append([kind.title, str(len(mine)), str(sum(r.enabled for r in mine)),
                           str(len(ours)), str(len(mine) - len(ours)), coverage])
    table_rows.append([("Total", C.bold), (str(len(rows)), C.bold), (str(sum(r.enabled for r in rows)), C.bold),
                       "", "", ""])
    heading("Pi-hole domain lists")
    print(render_table(["List", "Entries", "Enabled", "From repo", "Yours", "Repo installed"],
                       table_rows, flex=0))
    return EXIT_OK


def stamp() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y%m%d-%H%M%S")


def give_to_sudo_user(path: Path) -> None:
    """Under sudo, hand files written into the user's folders back to that user."""
    uid, gid = os.environ.get("SUDO_UID"), os.environ.get("SUDO_GID")
    if os.geteuid() == 0 and uid and gid and uid.isdigit() and gid.isdigit():
        os.chown(path, int(uid), int(gid))


def backup_to(db_path: str, target: Path) -> Path:
    db = open_db(db_path, write=False)
    try:
        target = target.expanduser().resolve()
        if target.is_dir():
            target = target / f"pihole-gravity-{stamp()}.db"
        if target.exists():
            raise AppError(f"{target} already exists. Choose another name.")
        dest = sqlite3.connect(target)
        try:
            # The online backup API copies a consistent snapshot even while
            # Pi-hole is writing; copying the file could catch it mid-write.
            db.conn.backup(dest)
        finally:
            dest.close()
    except (sqlite3.DatabaseError, OSError) as exc:
        raise AppError(f"Backup failed: {exc}") from exc
    finally:
        db.close()
    give_to_sudo_user(target)
    return target


def cmd_backup(args: argparse.Namespace, target: str) -> int:
    path = backup_to(args.database, Path(target or "."))
    size = path.stat().st_size / 1_048_576
    success(f"Backup saved: {path} ({size:.1f} MB)")
    return EXIT_OK


def cmd_restore(args: argparse.Namespace, source: str) -> int:
    path = Path(source).expanduser().resolve()
    if not path.is_file():
        raise AppError(f"{path} does not exist.")
    try:
        check = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)
        try:
            tables = {r[0] for r in check.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            healthy = check.execute("PRAGMA quick_check").fetchone()[0] == "ok"
            entries = check.execute("SELECT COUNT(*) FROM domainlist").fetchone()[0] if "domainlist" in tables else 0
        finally:
            check.close()
    except sqlite3.DatabaseError as exc:
        raise AppError(f"{path} is not a readable database: {exc}") from exc
    if not {"domainlist", "adlist", "gravity"} <= tables:
        raise AppError(f"{path} is not a Pi-hole gravity database.")
    if not healthy:
        raise AppError(f"{path} failed SQLite's integrity check, so it was not restored.")
    print(f"\nRestore {C.bold}{path}{C.reset} ({entries} domain entries) over {args.database}?")
    note("Everything in Pi-hole's current database is replaced: lists, adlists, groups and clients.")
    if args.dry_run:
        print(f"{C.cyan}Dry run:{C.reset} the backup is valid. Nothing was changed.")
        return EXIT_OK
    if not confirm("Replace the current database?", default=False, assume_yes=args.yes):
        note("Cancelled. Nothing was changed.")
        return EXIT_OK
    safety = backup_to(args.database, path.parent / f"pihole-gravity-before-restore-{stamp()}.db")
    note(f"Current database saved first: {safety}")
    db = open_db(args.database, write=True)
    src = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)
    try:
        src.backup(db.conn)
    except sqlite3.DatabaseError as exc:
        raise AppError(f"Restore failed: {exc}. The copy at {safety} is untouched.") from exc
    finally:
        src.close()
        db.close()
    success("Restored.")
    return reload_pihole(args)


# ---------------------------------------------------------------------------
# Interactive menu
# ---------------------------------------------------------------------------

MENU = (
    ("1", "Add or update", "add this repository's lists to Pi-hole"),
    ("2", "Remove", "take this repository's entries out of Pi-hole"),
    ("3", "Browse", "show what is in each list"),
    ("4", "Search", "find entries by domain or comment"),
    ("5", "Statistics", "counts for every list"),
    ("6", "Back up", "save a copy of Pi-hole's database"),
    ("7", "Restore", "put a saved copy back"),
    ("h", "Help", "command-line options"),
    ("q", "Quit", ""),
)


def dashboard(db_path: str) -> str:
    try:
        db = open_db(db_path, write=False)
        try:
            rows = db.rows()
        finally:
            db.close()
    except AppError as exc:
        return f"  {C.yellow}{exc}{C.reset}"
    lines = []
    for kind in KINDS:
        mine = [r for r in rows if r.type == kind.type]
        ours = sum(1 for r in mine if r.comment.startswith(kind.tag))
        lines.append(f"  {kind.title:<17} {C.bold}{len(mine):>5}{C.reset} entries  "
                     f"{C.dim}{ours} from this repo{C.reset}")
    return "\n".join(lines)


def banner(db_path: str) -> None:
    clear_screen()
    width = min(term_width(), 78)
    print(f"{C.bold}{C.cyan}  Pi-hole RegEx{C.reset}  {C.dim}v{VERSION}{C.reset}"
          f"{' ' * max(1, width - 40 - len(VERSION))}{C.dim}{REPO_URL.split('//')[1]}{C.reset}")
    print(f"  {C.dim}{RULE * (width - 2)}{C.reset}")
    print(dashboard(db_path))
    print(f"  {C.dim}{RULE * (width - 2)}{C.reset}")


def choose_kinds(action: str) -> list[Kind] | None:
    print(f"\n{C.bold}{action} which lists?{C.reset}")
    for i, kind in enumerate(KINDS, 1):
        print(f"  {C.green}{i}{C.reset}  {kind.title}")
    print(f"  {C.green}a{C.reset}  All four")
    while True:
        reply = ask("Choose 1-4 (commas for several), a for all, or Enter to go back:").lower()
        if not reply:
            return None
        if reply in ("a", "all"):
            return list(KINDS)
        picks = [p.strip() for p in reply.replace(",", " ").split()]
        if all(p.isdigit() and 1 <= int(p) <= len(KINDS) for p in picks):
            return [KINDS[i - 1] for i in sorted({int(p) for p in picks})]
        print(f"{C.yellow}Please enter numbers from 1 to 4, or a.{C.reset}")


def interactive(args: argparse.Namespace) -> int:
    while True:
        banner(args.database)
        print()
        for key, label, text in MENU:
            print(f"  {C.green}{C.bold}{key}{C.reset}  {label:<15}{C.dim}{text}{C.reset}")
        choice = ask("\nChoose an option:").lower()
        if choice in ("q", "quit", "exit"):
            return EXIT_OK
        try:
            if choice == "1":
                kinds = choose_kinds("Add or update")
                if kinds:
                    cmd_add(args, kinds)
            elif choice == "2":
                kinds = choose_kinds("Remove")
                if kinds:
                    cmd_remove(args, kinds)
            elif choice == "3":
                kinds = choose_kinds("Browse")
                if kinds:
                    cmd_list(args, kinds)
            elif choice == "4":
                term = ask("Search for:")
                if term:
                    cmd_search(args, term)
            elif choice == "5":
                cmd_stats(args)
            elif choice == "6":
                cmd_backup(args, ask("Save the backup where? (Enter = this folder):"))
            elif choice == "7":
                source = ask("Backup file to restore (Enter to go back):")
                if source:
                    cmd_restore(args, source)
            elif choice in ("h", "help", "?"):
                page(help_text())
            else:
                continue
        except AppError as exc:
            error(str(exc))
        reply = ask(f"\n{C.dim}Press Enter for the menu, or q to quit:{C.reset}").lower()
        if reply in ("q", "quit", "exit"):
            return EXIT_OK


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

def help_text() -> str:
    b, r, h, o, a, d = C.bold, C.reset, C.bold + C.cyan, C.green, C.magenta, C.dim

    def row(flags: str, arg: str, text: str) -> str:
        # Pad on the visible width; the color codes would otherwise skew the column.
        visible = len(flags) + (len(arg) + 1 if arg else 0)
        colored = ", ".join(f"{o}{flag}{r}" for flag in flags.split(", "))
        colored += f" {a}{arg}{r}" if arg else ""
        return f"  {colored}{' ' * (26 - visible)}{text}"

    options = "\n\n".join((
        row("-a, --add", "", "Add the repository's entries Pi-hole is missing.\n"
            "      No value: selects ALL four list types.\n"
            "      Optional values: 'all', list names, or short forms listed below.\n"
            f"      Examples: {b}--add{r}   {b}--add all{r}   {b}--add ed,rd{r}"),
        row("-r, --remove", "", f"Remove this repository's entries {d}(asks first){r}.\n"
            "      No value: selects ALL four list types.\n"
            "      Optional values: 'all', list names, or short forms listed below.\n"
            f"      Examples: {b}--remove{r}   {b}--remove all{r}   {b}--remove ed,rd{r}"),
        row("-l, --list", "", "Show the entries in Pi-hole.\n"
            "      No value: selects ALL four list types.\n"
            "      Optional values: 'all', list names, or short forms listed below.\n"
            f"      Examples: {b}--list{r}   {b}--list all{r}   {b}--list ed,rd{r}"),
        row("-s, --search", "TEXT", "Find entries by domain or comment"),
        row("-S, --stats", "", "Counts for every list"),
        row("-b, --backup", "", "Save a copy of Pi-hole's database.\n"
            "      No value: saves a new backup in the current directory.\n"
            "      Optional value: destination file or directory.\n"
            f"      Examples: {b}--backup{r}   {b}--backup ~/backups{r}"),
        row("--restore", "FILE", f"Put a saved copy back {d}(saves the current one first){r}"),
    ))
    modifiers = "\n".join((
        row("-n, --dry-run", "", "Show what would change, change nothing"),
        row("-y, --yes", "", f"Answer yes to every question {d}(for cron and scripts){r}"),
        row("-v, --verbose", "", "Show every entry in a change, not the first few"),
        row("--no-reload", "", f"Save changes but do not run {b}pihole reloaddns{r}"),
        row("--database", "PATH", f"Pi-hole database {d}(default {DEFAULT_DB}){r}"),
        row("--no-color", "", f"Plain output {d}(the NO_COLOR variable works too){r}"),
        row("-h, --help", "", "Show this help"),
        row("--version", "", "Show the version"),
    ))
    names = "\n".join(f"  {o}{k.key:<13}{r}{k.title:<17}{d}{', '.join(k.aliases[:1])}  ({k.file}){r}"
                      for k in KINDS)
    return f"""
{h}pi.py{r} {d}v{VERSION}{r}  Manage the SlyFox1186 domain lists in your Pi-hole

{h}USAGE{r}
  sudo python3 pi.py                 {d}# interactive menu{r}
  sudo python3 pi.py --list          {d}# show all four lists{r}
  sudo python3 pi.py --list ed,rd    {d}# show the two denylists{r}

{h}OPTIONS{r}
{options}

{h}LIST VALUES{r}  {d}list names or short forms, separated by commas or spaces{r}
  {o}{'all':<13}{r}All four list types {d}(literal value, for example: --list all){r}
{names}

{h}MODIFIERS{r}
{modifiers}

{h}EXAMPLES{r}
  sudo python3 pi.py -a                   {d}# add everything that is missing{r}
  sudo python3 pi.py -a exact-deny,rd     {d}# only the two denylists{r}
  sudo python3 pi.py -r regex-allow -n    {d}# preview removing the regex allowlist{r}
  sudo python3 pi.py -s netflix           {d}# find every entry mentioning netflix{r}
  sudo python3 pi.py -b ~/backups         {d}# back up into a folder{r}
  sudo python3 pi.py -a -y                {d}# unattended update, then reload Pi-hole{r}

{h}GOOD TO KNOW{r}
  Entries this script adds are tagged in their comment (SlyEWL, SlyEBL, SlyRWL, SlyRBL).
  {o}--remove{r} takes out tagged entries, and entries with no comment that match the
  repository's domains (older versions left comments empty). Entries with a comment
  of your own stay.
  {o}--add{r} also removes tagged entries the repository has since dropped, and updates
  their comments when the repository corrects them.
  Changes take effect after Pi-hole reloads; you are asked after each change.

  {d}Exit codes: 0 done, 1 error, 2 bad option, 130 cancelled.  {REPO_URL}{r}
"""


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        error(f"{message}\n       Run {C.bold}pi.py --help{C.reset} to see the options.")
        sys.exit(EXIT_USAGE)


class HelpAction(argparse.Action):
    def __init__(self, option_strings: list[str], dest: str, **kwargs: object) -> None:
        super().__init__(option_strings, dest, nargs=0, default=argparse.SUPPRESS)

    def __call__(self, parser, namespace, values, option_string=None):
        print(help_text())
        sys.exit(EXIT_OK)


def build_parser() -> Parser:
    parser = Parser(prog="pi.py", add_help=False, allow_abbrev=False)
    actions = parser.add_mutually_exclusive_group()
    for short, name in (("-a", "--add"), ("-r", "--remove"), ("-l", "--list")):
        actions.add_argument(short, name, nargs="*", action="append", metavar="LISTS")
    actions.add_argument("-s", "--search", metavar="TEXT")
    actions.add_argument("-S", "--stats", action="store_true")
    actions.add_argument("-b", "--backup", nargs="?", const="", metavar="PATH")
    actions.add_argument("--restore", metavar="FILE")
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-y", "--yes", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--no-reload", action="store_true")
    parser.add_argument("--database", default=DEFAULT_DB, metavar="PATH")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("-h", "--help", action=HelpAction)
    parser.add_argument("--version", action="version", version=f"pi.py {VERSION}")
    return parser


def flatten(groups: list[list[str]]) -> list[str]:
    return [value for group in groups for value in group]


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.add is not None:
        return cmd_add(args, parse_kinds(flatten(args.add)))
    if args.remove is not None:
        return cmd_remove(args, parse_kinds(flatten(args.remove)))
    if args.list is not None:
        return cmd_list(args, parse_kinds(flatten(args.list)))
    if args.search is not None:
        return cmd_search(args, args.search)
    if args.stats:
        return cmd_stats(args)
    if args.backup is not None:
        return cmd_backup(args, args.backup)
    if args.restore is not None:
        return cmd_restore(args, args.restore)
    if not INTERACTIVE:
        raise AppError("The menu needs a terminal. Use an option instead; run pi.py --help to see them.")
    return interactive(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AppError as exc:
        error(str(exc))
        sys.exit(EXIT_ERROR)
    except (KeyboardInterrupt, EOFError):
        print(f"\n{C.yellow}Cancelled.{C.reset}", file=sys.stderr)
        sys.exit(EXIT_CANCELLED)
