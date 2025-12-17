#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DOMAINS_DIR = Path(__file__).resolve().parent.parent / "domains"
LIST_FILES = {
    "exact_whitelist": DOMAINS_DIR / "exact-whitelist.sql",
    "exact_blacklist": DOMAINS_DIR / "exact-blacklist.sql",
    "regex_whitelist": DOMAINS_DIR / "regex-whitelist.sql",
    "regex_blacklist": DOMAINS_DIR / "regex-blacklist.sql",
}

COMMON_PREFIXES = ("(\\.|^)", "(^|\\.)", "(?:^|\\.)")


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
    if p.startswith("^"):
        p = p[1:]
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


def pcre2grep_matches(pattern: str, subjects: list[str]) -> tuple[int, list[str], str]:
    proc = subprocess.run(
        ["pcre2grep", "-n", pattern],
        input="\n".join(subjects) + "\n",
        text=True,
        capture_output=True,
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
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    lists = {name: parse_entries(path) for name, path in LIST_FILES.items()}

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

    # 3) Regex compile check + suspicious heuristics
    for name in ("regex_whitelist", "regex_blacklist"):
        for entry in lists[name]:
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
    exact_wl = [e.pattern for e in lists["exact_whitelist"]]
    exact_bl = [e.pattern for e in lists["exact_blacklist"]]

    for entry in lists["regex_blacklist"]:
        rc, matches, err = pcre2grep_matches(entry.pattern, exact_wl)
        if rc == 2:
            continue
        if matches:
            sample = ", ".join(matches[:5])
            warnings.append(
                f"{entry.file.name}:{entry.line_no}: regex blacklist matches exact whitelist ({len(matches)}): {sample}"
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

    if not errors and not warnings:
        print("OK: no issues found.")
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

