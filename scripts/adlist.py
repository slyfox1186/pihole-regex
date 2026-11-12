#!/usr/bin/env python3
"""Install, remove, enable and disable the SlyFox1186 adlists in a local Pi-hole.

Uses only the Python standard library because it is started with
`sudo python3 adlist.py`, and sudo selects the system Python, which has no
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
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

VERSION = "2.0.0"
DEFAULT_DB = "/etc/pihole/gravity.db"
SOURCE_URL = "https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlists.txt"
REPO_URL = "https://github.com/slyfox1186/pihole-regex"
USER_AGENT = f"pihole-regex-adlist/{VERSION} (+{REPO_URL})"
# Every row this script creates carries this comment, and only rows whose
# comment starts with TAG are ever changed, so lists added by hand are safe.
TAG = "SlyADL"
COMMENT = f"{TAG} - SlyFox1186 AdList - github.com/slyfox1186/pihole-regex"
DB_TIMEOUT = 30
HTTP_TIMEOUT = 20

EXIT_OK, EXIT_ERROR, EXIT_USAGE, EXIT_CANCELLED = 0, 1, 2, 130


class AppError(Exception):
    """A failure with a message meant for the user; nothing has been changed."""


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


def heading(text: str) -> None:
    print(f"\n{C.bold}{C.cyan}{text}{C.reset}")


def info(text: str) -> None:
    print(text)


def success(text: str) -> None:
    print(f"{C.green}{text}{C.reset}")


def warn(text: str) -> None:
    sys.stdout.flush()  # keep stdout and stderr in order when both are piped
    print(f"{C.yellow}Warning:{C.reset} {text}", file=sys.stderr)


def error(text: str) -> None:
    sys.stdout.flush()
    print(f"{C.red}{C.bold}Error:{C.reset} {text}", file=sys.stderr)


def fit(text: str, width: int) -> str:
    """Shorten text to width with a middle ellipsis so both URL ends stay visible."""
    if width < 12 or len(text) <= width:
        return text
    keep = width - 3
    return f"{text[:keep // 2]}...{text[-(keep - keep // 2):]}"


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


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Row:
    """An adlist row in Pi-hole's database."""
    id: int
    address: str
    enabled: bool
    managed: bool
    domains: int


@dataclass(frozen=True)
class Entry:
    """A list this script knows about, numbered the way --list shows it."""
    number: int
    address: str
    in_source: bool
    row: Row | None

    @property
    def installed(self) -> bool:
        return self.row is not None


def fetch_source(url: str) -> list[str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            text = response.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        reason = getattr(exc, "reason", exc)
        raise AppError(f"Could not download the adlist source {url}: {reason}") from exc

    urls: list[str] = []
    seen: set[str] = set()
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not line.startswith(("https://", "http://")) or any(ch.isspace() for ch in line):
            warn(f"Ignoring line {line_no} of the adlist source because it is not a URL: {line}")
            continue
        if line not in seen:
            seen.add(line)
            urls.append(line)
    if not urls:
        raise AppError(f"The adlist source {url} contained no adlist URLs.")
    return urls


class PiholeDB:
    def __init__(self, path: str, *, write: bool) -> None:
        db = Path(path)
        if not db.is_file():
            raise AppError(f"Pi-hole's database was not found at {db}. "
                           "Is Pi-hole installed on this machine? (--database sets another path)")
        needed = os.W_OK if write else os.R_OK
        if not os.access(db, needed) or (write and not os.access(db.parent, os.W_OK)):
            action = "Changing" if write else "Reading"
            raise AppError(f"{action} Pi-hole's adlists needs root. Run it again with sudo.")
        mode = "rw" if write else "ro"
        self.conn = sqlite3.connect(f"{db.resolve().as_uri()}?mode={mode}", uri=True,
                                    timeout=DB_TIMEOUT, isolation_level=None)
        columns = {row[1] for row in self.conn.execute("PRAGMA table_info(adlist)")}
        if "address" not in columns:
            raise AppError(f"{db} is not a Pi-hole gravity database (it has no adlist table).")
        # Pi-hole v6 also stores allowlists in this table (type 1); v5 has no type column.
        self._blocklists_only = "AND type = 0" if "type" in columns else ""
        self._domains = "number" if "number" in columns else "0"

    def close(self) -> None:
        self.conn.close()

    def rows(self) -> list[Row]:
        query = (f"SELECT id, address, enabled, COALESCE(comment, '') LIKE '{TAG}%', "
                 f"{self._domains} FROM adlist WHERE 1 {self._blocklists_only} ORDER BY id")
        return [Row(int(i), str(a), bool(e), bool(m), int(n or 0))
                for i, a, e, m, n in self.conn.execute(query)]

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

    def add(self, addresses: list[str]) -> None:
        self.conn.executemany(
            "INSERT INTO adlist (address, enabled, comment, date_added, date_modified) VALUES "
            "(?, 1, ?, CAST(strftime('%s', 'now') AS INTEGER), CAST(strftime('%s', 'now') AS INTEGER))",
            [(address, COMMENT) for address in addresses])

    def remove(self, ids: list[int]) -> None:
        # Pi-hole's tr_adlist_delete trigger removes the matching adlist_by_group rows.
        self.conn.executemany(f"DELETE FROM adlist WHERE id = ? AND comment LIKE '{TAG}%'",
                              [(i,) for i in ids])

    def set_enabled(self, ids: list[int], enabled: bool) -> None:
        self.conn.executemany(f"UPDATE adlist SET enabled = ? WHERE id = ? AND comment LIKE '{TAG}%'",
                              [(int(enabled), i) for i in ids])


class Catalog:
    """Source lists numbered 1..N in source order, then this script's installed
    lists that the source no longer has. The numbers are what --list prints."""

    def __init__(self, source: list[str] | None, rows: list[Row]) -> None:
        self.online = source is not None
        self.rows = rows
        by_address = {row.address: row for row in rows}
        self.entries: list[Entry] = []
        for address in source or []:
            self.entries.append(Entry(len(self.entries) + 1, address, True, by_address.get(address)))
        listed = set(source or [])
        for row in rows:
            if row.managed and row.address not in listed:
                self.entries.append(Entry(len(self.entries) + 1, row.address, False, row))
        self._by_number = {entry.number: entry for entry in self.entries}
        self._by_address = {entry.address: entry for entry in self.entries}

    def resolve(self, items: list[str], *, changing_rows: bool = True) -> list[Entry]:
        """Map all, numbers and URLs to entries, refusing requests with bad items.

        changing_rows is False for --add, where a list the user already added by
        hand simply counts as installed instead of being refused.
        """
        if items == ["all"]:
            if changing_rows:
                return [e for e in self.entries if e.row is not None and e.row.managed]
            return [e for e in self.entries if e.in_source]
        found: list[Entry] = []
        problems: list[str] = []
        for item in items:
            if item.isdigit():
                if not self.online:
                    problems.append(f"{item}: list numbers need the adlist source, which could not be "
                                    "downloaded. Use the adlist URL instead.")
                    continue
                entry = self._by_number.get(int(item))
                if entry is None:
                    problems.append(f"{item}: there is no list with that number (run --list).")
                    continue
            else:
                entry = self._by_address.get(item)
                if entry is None:
                    foreign = next((r for r in self.rows if r.address == item), None)
                    if foreign is not None:
                        problems.append(f"{item}: this adlist was not added by adlist.py, "
                                        "so it is left alone. Change it in Pi-hole's web interface.")
                    else:
                        problems.append(f"{item}: not a SlyFox1186 adlist and not in Pi-hole (run --list).")
                    continue
            if changing_rows and entry.row is not None and not entry.row.managed:
                problems.append(f"{item}: this adlist was added outside adlist.py, so it is left alone.")
                continue
            if entry not in found:
                found.append(entry)
        if problems:
            raise AppError("Nothing was changed:\n  " + "\n  ".join(problems))
        return found


# ---------------------------------------------------------------------------
# Plans: what will change, shown before anything is written
# ---------------------------------------------------------------------------

@dataclass
class Plan:
    add: list[Entry]
    remove: list[Entry]
    enable: list[Entry]
    disable: list[Entry]

    @property
    def empty(self) -> bool:
        return not (self.add or self.remove or self.enable or self.disable)

    def show(self) -> None:
        width = shutil.get_terminal_size((100, 24)).columns - 12 if sys.stdout.isatty() else 10_000
        groups = (("Add", C.green, self.add), ("Remove", C.red, self.remove),
                  ("Enable", C.green, self.enable), ("Disable", C.yellow, self.disable))
        for label, color, entries in groups:
            if entries:
                heading(f"{label} ({len(entries)}):")
                for entry in entries:
                    print(f"  {color}{entry.number:>3}{C.reset}  {fit(entry.address, width)}")


def apply(db: PiholeDB, plan: Plan) -> None:
    with db.transaction():
        if plan.add:
            db.add([e.address for e in plan.add])
        if plan.remove:
            db.remove([e.row.id for e in plan.remove if e.row])
        if plan.enable:
            db.set_enabled([e.row.id for e in plan.enable if e.row], True)
        if plan.disable:
            db.set_enabled([e.row.id for e in plan.disable if e.row], False)


def update_gravity(args: argparse.Namespace) -> int:
    if args.no_gravity:
        info(f"\nPi-hole keeps using the old lists until you run {C.bold}sudo pihole -g{C.reset}.")
        return EXIT_OK
    if not confirm("\nUpdate Pi-hole's gravity database now so the change takes effect?",
                   default=True, assume_yes=args.yes):
        info(f"Skipped. Run {C.bold}sudo pihole -g{C.reset} when you are ready.")
        return EXIT_OK
    pihole = shutil.which("pihole") or "/usr/local/bin/pihole"
    heading("Running pihole -g")
    try:
        result = subprocess.run([pihole, "-g"], check=False)
        if result.returncode != 0:
            error(f"pihole -g failed with exit code {result.returncode}. Check its output above.")
            return EXIT_ERROR
        # gravity.sh rebuilds the database but does not tell FTL to load it.
        subprocess.run([pihole, "reloadlists"], check=False, stdout=subprocess.DEVNULL)
    except OSError as exc:
        error(f"Could not run {pihole}: {exc}. Run 'sudo pihole -g' yourself.")
        return EXIT_ERROR
    success("Gravity updated. Pi-hole is using the new lists.")
    return EXIT_OK


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def split_items(values: list[list[str]]) -> list[str]:
    """Default omitted items to all; preserve explicit selections and reject empty ones."""
    if not any(values):
        return ["all"]
    items: list[str] = []
    for group in values:
        for value in group:
            for item in value.replace(",", " ").split():
                if item.lower() == "all":
                    item = "all"
                if item not in items:
                    items.append(item)
    if not items:
        raise AppError("No adlist numbers or URLs were given.")
    if "all" in items and len(items) > 1:
        raise AppError("Use all by itself, or give specific adlist numbers or URLs.")
    return items


def load(args: argparse.Namespace, *, write: bool, need_source: bool) -> tuple[PiholeDB, Catalog]:
    db = PiholeDB(args.database, write=write and not args.dry_run)
    try:
        source = fetch_source(SOURCE_URL)
    except AppError as exc:
        if need_source:
            db.close()
            raise
        warn(f"{exc}\n         Only lists already installed are shown, and numbers cannot be used.")
        source = None
    return db, Catalog(source, db.rows())


def cmd_list(args: argparse.Namespace) -> int:
    db, catalog = load(args, write=False, need_source=False)
    db.close()
    installed = [e for e in catalog.entries if e.installed]
    enabled = [e for e in installed if e.row and e.row.enabled]
    total = sum(1 for e in catalog.entries if e.in_source)
    heading("SlyFox1186 adlists")
    if catalog.online:
        info(f"{total} in the repository, {len(installed)} installed, {len(enabled)} enabled")
    status_width = 13
    width = shutil.get_terminal_size((100, 24)).columns - 34 if sys.stdout.isatty() else 10_000
    print(f"\n  {C.dim}{'#':>3}  {'Status':<{status_width}} {'Domains':>10}  Address{C.reset}")
    if not catalog.entries:
        info(f"  {C.dim}(no lists installed){C.reset}")
    for entry in catalog.entries:
        if entry.row is None:
            status, color, domains = "not installed", C.dim, "-"
        elif not entry.in_source:
            status, color, domains = "retired", C.magenta, f"{entry.row.domains:,}"
        else:
            status = "enabled" if entry.row.enabled else "disabled"
            color = C.green if entry.row.enabled else C.yellow
            domains = f"{entry.row.domains:,}"
        print(f"  {entry.number:>3}  {color}{status:<{status_width}}{C.reset} {domains:>10}  "
              f"{fit(entry.address, width)}")
    if any(not e.in_source for e in catalog.entries):
        info(f"\n{C.magenta}retired{C.reset}: no longer in the repository; the next plain run removes it.")
    info("\nDomain counts are from Pi-hole's last gravity update. "
         "Numbers can change when the repository changes, so scripts should use URLs.")
    return EXIT_OK


def run_plan(args: argparse.Namespace, db: PiholeDB, plan: Plan, *, ask: str | None = None) -> int:
    try:
        if plan.empty:
            success("\nNothing to change.")
            return EXIT_OK
        plan.show()
        if args.dry_run:
            info(f"\n{C.cyan}Dry run:{C.reset} nothing was changed.")
            return EXIT_OK
        if ask and not confirm(f"\n{ask}", default=False, assume_yes=args.yes):
            info("Cancelled. Nothing was changed.")
            return EXIT_OK
        try:
            apply(db, plan)
        except sqlite3.OperationalError as exc:
            if "locked" in str(exc) or "busy" in str(exc):
                raise AppError("Pi-hole's database stayed busy for "
                               f"{DB_TIMEOUT} seconds (gravity may be running). Try again shortly.") from exc
            raise AppError(f"Pi-hole's database refused the change: {exc}") from exc
    finally:
        db.close()
    counts = [f"{n} {verb}" for n, verb in ((len(plan.add), "added"), (len(plan.remove), "removed"),
                                            (len(plan.enable), "enabled"), (len(plan.disable), "disabled")) if n]
    success(f"\nSaved: {', '.join(counts)}.")
    return update_gravity(args)


def cmd_sync(args: argparse.Namespace) -> int:
    db, catalog = load(args, write=True, need_source=True)
    taken = {row.address for row in catalog.rows}
    plan = Plan(add=[e for e in catalog.entries if e.in_source and e.address not in taken],
                remove=[e for e in catalog.entries if not e.in_source],
                enable=[], disable=[])
    return run_plan(args, db, plan)


def cmd_add(args: argparse.Namespace) -> int:
    items = split_items(args.add)
    db, catalog = load(args, write=True, need_source=True)
    try:
        chosen = catalog.resolve(items, changing_rows=False)
        for entry in chosen:
            if entry.installed:
                info(f"{C.dim}Already installed:{C.reset} {entry.address}")
            elif not entry.in_source:
                raise AppError(f"{entry.address} is no longer in the repository and cannot be added.")
    except BaseException:
        db.close()
        raise
    return run_plan(args, db, Plan([e for e in chosen if not e.installed], [], [], []))


def cmd_remove(args: argparse.Namespace) -> int:
    items = ["all"] if args.remove_all else split_items(args.remove)
    db, catalog = load(args, write=True, need_source=False)
    try:
        chosen = catalog.resolve(items)
    except BaseException:
        db.close()
        raise
    if items == ["all"]:
        ask = f"Remove all {len(chosen)} adlists that adlist.py installed?"
    else:
        ask = None
        for entry in chosen:
            if not entry.installed:
                info(f"{C.dim}Not installed:{C.reset} {entry.address}")
    return run_plan(args, db, Plan([], [e for e in chosen if e.installed], [], []),
                    ask=ask if chosen else None)


def cmd_toggle(args: argparse.Namespace, enabled: bool) -> int:
    items = split_items(args.enable if enabled else args.disable)
    db, catalog = load(args, write=True, need_source=False)
    try:
        chosen = catalog.resolve(items)
    except BaseException:
        db.close()
        raise
    targets = []
    for entry in chosen:
        if entry.row is None:
            info(f"{C.dim}Not installed, so it cannot be {'enabled' if enabled else 'disabled'}:{C.reset} "
                 f"{entry.address}")
        elif entry.row.enabled == enabled:
            info(f"{C.dim}Already {'enabled' if enabled else 'disabled'}:{C.reset} {entry.address}")
        else:
            targets.append(entry)
    plan = Plan([], [], targets, []) if enabled else Plan([], [], [], targets)
    return run_plan(args, db, plan)


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
        return f"  {colored}{' ' * (24 - visible)}{text}"

    options = "\n".join((
        row("-l, --list", "", "Show every list with its number, status and domain count"),
        row("-a, --add", "[ITEMS]", "Add selected lists, or all missing lists"),
        row("-r, --remove", "[ITEMS]", "Remove selected lists, or all managed lists (asks for all)"),
        row("-R, --remove-all", "", f"Remove every list this script added {d}(asks first){r}"),
        row("-e, --enable", "[ITEMS]", "Turn selected lists back on, or all managed lists"),
        row("-d, --disable", "[ITEMS]", "Turn selected lists off, or all managed lists; keep them installed"),
    ))
    modifiers = "\n".join((
        row("-n, --dry-run", "", "Show what would change, change nothing"),
        row("-y, --yes", "", f"Answer yes to every question {d}(for cron and scripts){r}"),
        row("--no-gravity", "", f"Save the change but do not run {b}pihole -g{r}"),
        row("--database", "PATH", f"Pi-hole database to use {d}(default {DEFAULT_DB}){r}"),
        row("--no-color", "", f"Plain output {d}(the NO_COLOR variable works too){r}"),
        row("-h, --help", "", "Show this help"),
        row("--version", "", "Show the version"),
    ))
    return f"""
{h}adlist.py{r} {d}v{VERSION}{r}  Manage the SlyFox1186 adlists in your Pi-hole

{h}USAGE{r}
  sudo python3 adlist.py {d}[option] [modifiers]{r}

  With no option, adds every repository adlist that Pi-hole is missing and
  removes the ones this script added that the repository has since dropped.

{h}OPTIONS{r}
{options}

  {a}ITEMS{r} is one or more list numbers from {o}--list{r} or adlist URLs, separated by
  commas or spaces:  {b}-r 4{r}   {b}-r 4,7,12{r}   {b}-r "4, 7"{r}   {b}-r https://adaway.org/hosts.txt{r}
  Leave {a}ITEMS{r} out, or use {b}all{r} by itself, to select all applicable lists.
  For add, that means repository lists; for remove, enable and disable, it means
  installed lists managed by this script, including retired lists.

{h}MODIFIERS{r}
{modifiers}

{h}EXAMPLES{r}
  sudo python3 adlist.py                  {d}# install every missing list{r}
  sudo python3 adlist.py --list           {d}# see numbers and what is installed{r}
  sudo python3 adlist.py -a               {d}# add missing lists; keep retired lists{r}
  sudo python3 adlist.py -r 4,7           {d}# remove lists 4 and 7{r}
  sudo python3 adlist.py -r --dry-run     {d}# preview removing all managed lists{r}
  sudo python3 adlist.py -d               {d}# switch all managed lists off{r}
  sudo python3 adlist.py -e all           {d}# switch all managed lists back on{r}
  sudo python3 adlist.py -d 12            {d}# switch list 12 off{r}
  sudo python3 adlist.py -y               {d}# unattended install, then update gravity{r}

{h}GOOD TO KNOW{r}
  Only lists this script added (comment starting with "{TAG}") are ever changed.
  Lists you added yourself in Pi-hole are never touched.
  After any change you are offered {b}pihole -g{r}; Pi-hole uses the change only after it runs.
  A removed list comes back the next time you run adlist.py with no option.
  Disable a list instead if you want to keep it off.

  {d}Exit codes: 0 done, 1 error, 2 bad option, 130 cancelled.  {REPO_URL}{r}
"""


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        error(f"{message}\n       Run {C.bold}adlist.py --help{C.reset} to see the options.")
        sys.exit(EXIT_USAGE)


class HelpAction(argparse.Action):
    def __init__(self, option_strings: list[str], dest: str, **kwargs: object) -> None:
        super().__init__(option_strings, dest, nargs=0, default=argparse.SUPPRESS)

    def __call__(self, parser, namespace, values, option_string=None):
        print(help_text())
        sys.exit(EXIT_OK)


def build_parser() -> Parser:
    parser = Parser(prog="adlist.py", add_help=False, allow_abbrev=False)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("-l", "--list", action="store_true")
    for short, name in (("-a", "--add"), ("-r", "--remove"), ("-e", "--enable"), ("-d", "--disable")):
        actions.add_argument(short, name, nargs="*", action="append", metavar="ITEMS")
    actions.add_argument("-R", "--remove-all", action="store_true")
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-y", "--yes", action="store_true")
    parser.add_argument("--no-gravity", action="store_true")
    parser.add_argument("--database", default=DEFAULT_DB, metavar="PATH")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("-h", "--help", action=HelpAction)
    parser.add_argument("--version", action="version", version=f"adlist.py {VERSION}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.list:
        return cmd_list(args)
    if args.add is not None:
        return cmd_add(args)
    if args.remove is not None or args.remove_all:
        return cmd_remove(args)
    if args.enable is not None:
        return cmd_toggle(args, True)
    if args.disable is not None:
        return cmd_toggle(args, False)
    return cmd_sync(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AppError as exc:
        error(str(exc))
        sys.exit(EXIT_ERROR)
    except KeyboardInterrupt:
        print(f"\n{C.yellow}Cancelled.{C.reset} Nothing more was changed.", file=sys.stderr)
        sys.exit(EXIT_CANCELLED)
