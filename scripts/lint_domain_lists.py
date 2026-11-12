#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import unicodedata
import urllib.request
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

DOMAINS_DIR = Path(__file__).resolve().parent.parent / "domains"
LIST_NAMES = {
    "exact_whitelist": "exact-whitelist.sql",
    "exact_blacklist": "exact-blacklist.sql",
    "regex_whitelist": "regex-whitelist.sql",
    "regex_blacklist": "regex-blacklist.sql",
}

COMMON_PREFIXES = ("(\\.|^)", "(^|\\.)", "(?:^|\\.)")

# Pi-hole FTL compiles regexes with TRE, not PCRE. After "(?" TRE accepts only
# flag letters (i, n, r, U, -) ending in ":" or ")", or a "#" comment; anything
# else, such as a lookahead "(?!", fails to compile and the entry never applies.
TRE_BAD_EXTENSION = re.compile(r"(?<!\\)\(\?(?!#|[inrU-]*[:)])")
HOSTNAME_LABEL = re.compile(r"^[a-z0-9_]([a-z0-9_-]{0,61}[a-z0-9_])?$")
IANA_TLDS_URL = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:159.0) Gecko/20100101 Firefox/159.0"


@dataclass(frozen=True)
class Entry:
    file: Path
    line_no: int
    pattern: str
    comment: str
    raw: str


def parse_entries(path: Path) -> list[Entry]:
    entries: list[Entry] = []
    text = path.read_text(errors="replace")
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip("\n")
        if not line.strip():
            continue
        if line.lstrip().startswith("#"):
            continue
        if " -- " in line:
            pattern, comment = line.split(" -- ", 1)
        else:
            pattern, comment = line, ""
        entries.append(
            Entry(
                file=path,
                line_no=line_no,
                pattern=pattern.strip(),
                comment=comment.strip(),
                raw=raw,
            )
        )
    return entries


def iter_control_chars(text: str) -> Iterable[tuple[int, str]]:
    for idx, ch in enumerate(text):
        if ch in ("\t", "\n", "\r"):
            continue
        if unicodedata.category(ch) in {"Cc", "Cf"}:
            yield idx, ch


def normalize_regex_for_overlap(pattern: str) -> str:
    p = pattern.strip()
    p = p.removeprefix("^")
    for prefix in COMMON_PREFIXES:
        if p.startswith(prefix):
            p = p[len(prefix) :]
            break
    return p


def find_suspicious_unescaped_dots(pattern: str) -> list[int]:
    indices: list[int] = []
    in_class = False
    escaped = False
    for idx, ch in enumerate(pattern):
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == "[" and not in_class:
            in_class = True
            continue
        if ch == "]" and in_class:
            in_class = False
            continue
        if in_class:
            continue
        if ch != ".":
            continue

        nxt = pattern[idx + 1] if idx + 1 < len(pattern) else ""
        if nxt in {"*", "+", "?", "{"}:
            continue
        indices.append(idx)
    return indices


class FtlUnavailable(Exception):
    """pihole-FTL is on PATH but its regex test did not give a recognizable answer."""


def ftl_compile_error(pattern: str) -> str | None:
    """Compile with Pi-hole FTL's own engine; return its message if the regex is invalid.

    `pihole-FTL regex-test` exits 0 (match) or 2 (no match) after printing
    "Compiled regex filter", and exits 1 with "Invalid regex" when compiling fails.
    Anything else raises FtlUnavailable, so a broken FTL is never read as a pass.
    """
    try:
        proc = subprocess.run(
            ["pihole-FTL", "regex-test", "example.com", pattern],
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise FtlUnavailable(str(exc)) from exc
    output = proc.stdout + proc.stderr
    if proc.returncode in (0, 2) and "Compiled regex filter" in output:
        return None
    if proc.returncode == 1:
        for line in output.splitlines():
            if line.startswith("Invalid regex"):
                return line.strip()
    raise FtlUnavailable(f"unexpected result (exit {proc.returncode}): {output.strip()[:200]}")


def ftl_self_test() -> None:
    """Prove pihole-FTL accepts a valid regex and rejects an invalid one before trusting it."""
    if ftl_compile_error(r"^ok\.example\.com$") is not None:
        raise FtlUnavailable("it rejected a valid test regex")
    if ftl_compile_error("(abc") is None:
        raise FtlUnavailable("it accepted an invalid test regex")


def hostname_problem(name: str) -> str | None:
    if len(name) > 253:
        return "longer than 253 characters"
    labels = name.lower().split(".")
    if len(labels) < 2:
        return "has no top-level domain"
    for label in labels:
        if not HOSTNAME_LABEL.match(label):
            return f"invalid label {label!r}"
    tld = labels[-1]
    if not (tld.isalpha() or tld.startswith("xn--")):
        return f"top-level domain {tld!r} is not alphabetic"
    return None


def fetch_iana_tlds() -> set[str]:
    request = urllib.request.Request(IANA_TLDS_URL, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            text = response.read().decode("ascii", "replace")
    except OSError as exc:
        raise SystemExit(f"--check-tlds: could not download {IANA_TLDS_URL}: {exc}") from exc
    tlds = {line.strip().lower() for line in text.splitlines() if line.strip() and not line.startswith("#")}
    if len(tlds) < 100:
        raise SystemExit(f"--check-tlds: {IANA_TLDS_URL} returned only {len(tlds)} entries; refusing to use it.")
    return tlds


def pcre2grep_matches(pattern: str, subjects: list[str]) -> tuple[int, list[str], str]:
    proc = subprocess.run(
        ["pcre2grep", "-n", pattern],
        input="\n".join(subjects) + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode == 2:
        return proc.returncode, [], proc.stderr.strip()

    matches: list[str] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        if ":" in line:
            _, rest = line.split(":", 1)
            matches.append(rest)
        else:
            matches.append(line)
    return proc.returncode, matches, ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint Pi-hole domain list files for overlaps and regex issues.")
    parser.add_argument("--verbose", action="store_true", help="Print more details.")
    parser.add_argument("--domains-dir", type=Path, default=DOMAINS_DIR,
                        help="Folder holding the four .sql lists (default: the repository's domains/).")
    parser.add_argument("--check-tlds", action="store_true",
                        help="Also check every exact entry's top-level domain against IANA's root list (downloads it).")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    exceptions: list[str] = []

    lists = {name: parse_entries(args.domains_dir / file) for name, file in LIST_NAMES.items()}
    have_ftl = shutil.which("pihole-FTL") is not None
    if have_ftl:
        try:
            ftl_self_test()
        except FtlUnavailable as exc:
            errors.append(f"pihole-FTL is installed but its regex test does not work, so regexes were not "
                          f"compiled with Pi-hole's engine: {exc}")
            have_ftl = False

    # pcre2grep powers the regex compile/conflict checks; degrade gracefully if absent.
    have_pcre2grep = shutil.which("pcre2grep") is not None
    if not have_pcre2grep:
        warnings.append(
            "pcre2grep not found on PATH; skipping regex compile and regex-vs-exact "
            "checks. Install it (e.g. 'apt install pcre2-utils' or 'brew install pcre2')."
        )

    # 1) Control/non-printable characters
    for name, entries in lists.items():
        for entry in entries:
            bad = list(iter_control_chars(entry.pattern + entry.comment))
            if bad:
                preview = entry.pattern.encode("unicode_escape").decode("ascii")
                errors.append(
                    f"{entry.file.name}:{entry.line_no}: contains control/format characters; pattern={preview}"
                )

    # 2) Exact duplicate patterns within a file
    for name, entries in lists.items():
        by_pattern: dict[str, list[Entry]] = {}
        for entry in entries:
            by_pattern.setdefault(entry.pattern, []).append(entry)
        for pat, group in by_pattern.items():
            if len(group) <= 1:
                continue
            locs = ", ".join(f"{e.file.name}:{e.line_no}" for e in group)
            warnings.append(f"Duplicate pattern in {name}: {pat} ({locs})")

    # 2b) Exact entries must be hostnames Pi-hole can ever be asked for
    tlds = fetch_iana_tlds() if args.check_tlds else set()
    for name in ("exact_whitelist", "exact_blacklist"):
        for entry in lists[name]:
            problem = hostname_problem(entry.pattern)
            if problem is None and tlds:
                tld = entry.pattern.lower().rsplit(".", 1)[-1]
                if tld not in tlds:
                    problem = f"top-level domain {tld!r} does not exist (IANA root list)"
            if problem:
                errors.append(f"{entry.file.name}:{entry.line_no}: not a valid hostname, {problem}: {entry.pattern}")

    # 3) Regex compile check + suspicious heuristics
    for name in ("regex_whitelist", "regex_blacklist"):
        for entry in lists[name]:
            # FTL's own compile is authoritative; the text scan only runs without it.
            if not have_ftl and TRE_BAD_EXTENSION.search(entry.pattern):
                errors.append(
                    f"{entry.file.name}:{entry.line_no}: Pi-hole's regex engine (TRE) has no lookaround or other "
                    f"'(?' extensions besides '(?:', '(?#...)' and flags: {entry.pattern}"
                )
                continue
            if have_ftl:
                try:
                    message = ftl_compile_error(entry.pattern)
                except FtlUnavailable as exc:
                    errors.append(f"{entry.file.name}:{entry.line_no}: pihole-FTL stopped answering; "
                                  f"the remaining regexes were not compiled with it: {exc}")
                    have_ftl = False
                    message = None
                if message:
                    errors.append(f"{entry.file.name}:{entry.line_no}: pihole-FTL rejects this regex: {message}")
                    continue
            if have_pcre2grep:
                rc, _, err = pcre2grep_matches(entry.pattern, ["example.com"])
                if rc == 2:
                    errors.append(f"{entry.file.name}:{entry.line_no}: PCRE2 compile error: {err}")
                    continue

            if "\\c" in entry.pattern:
                warnings.append(f"{entry.file.name}:{entry.line_no}: contains \\\\c escape (often accidental): {entry.pattern}")
            if "\\s" in entry.pattern:
                warnings.append(f"{entry.file.name}:{entry.line_no}: contains \\\\s (domains never contain whitespace): {entry.pattern}")

            dots = find_suspicious_unescaped_dots(entry.pattern)
            if dots:
                caret = ", ".join(str(i) for i in dots[:10])
                warnings.append(f"{entry.file.name}:{entry.line_no}: suspicious unescaped '.' at offsets {caret}: {entry.pattern}")

    # 4) Regex-vs-exact conflicts
    if have_pcre2grep:
        exact_wl = [e.pattern for e in lists["exact_whitelist"]]
        exact_bl = [e.pattern for e in lists["exact_blacklist"]]

        for entry in lists["regex_blacklist"]:
            rc, matches, err = pcre2grep_matches(entry.pattern, exact_wl)
            if rc == 2:
                continue
            if matches:
                # An exact allow inside a regex deny is how Pi-hole carves out an
                # exception (allow always wins), so it is reported, not failed.
                sample = ", ".join(matches[:5])
                exceptions.append(
                    f"{entry.file.name}:{entry.line_no}: exact whitelist exceptions to this regex ({len(matches)}): {sample}"
                )

        for entry in lists["regex_whitelist"]:
            rc, matches, err = pcre2grep_matches(entry.pattern, exact_bl)
            if rc == 2:
                continue
            if matches:
                sample = ", ".join(matches[:5])
                warnings.append(
                    f"{entry.file.name}:{entry.line_no}: regex whitelist matches exact blacklist ({len(matches)}): {sample}"
                )

    # 5) Regex whitelist vs regex blacklist overlap (normalized)
    wl_norm: dict[str, Entry] = {}
    for entry in lists["regex_whitelist"]:
        wl_norm.setdefault(normalize_regex_for_overlap(entry.pattern), entry)

    for entry in lists["regex_blacklist"]:
        key = normalize_regex_for_overlap(entry.pattern)
        if key in wl_norm:
            other = wl_norm[key]
            warnings.append(
                f"regex overlap: {entry.file.name}:{entry.line_no} <-> {other.file.name}:{other.line_no} (normalized={key})"
            )

    # Report
    if errors:
        print("ERRORS:")
        for msg in errors:
            print(f"  - {msg}")
        print()

    if warnings:
        print("WARNINGS:")
        for msg in warnings:
            print(f"  - {msg}")
        print()

    if exceptions and (args.verbose or errors or warnings):
        print("EXCEPTIONS (intended):")
        for msg in exceptions:
            print(f"  - {msg}")
        print()

    if not errors and not warnings:
        engine = "pihole-FTL" if have_ftl else "static TRE rules"
        print(f"OK: no issues found (regexes checked with {engine}; "
              f"{len(exceptions)} regex blacklist rule(s) have exact whitelist exceptions).")
        return 0

    if args.verbose:
        counts = {k: len(v) for k, v in lists.items()}
        print("INFO:")
        for name, count in counts.items():
            print(f"  - {name}: {count} entries")

    # Treat errors as hard failures; warnings still non-zero so CI can catch drift.
    return 2 if errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

