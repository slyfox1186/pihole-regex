# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Curated Pi-hole v6+ filter data (`domains/`) plus Python scripts that write it into a Pi-hole's
SQLite databases. There is no build, package, test suite or CI. The list files are the product.

## Pushing to `main` ships to users

`scripts/pi.py` and `scripts/adlist.py` do not read the local `domains/` files. They download them
from `https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/...` at run time
(`URLS` in `pi.py`, `REMOTE_URL` in `adlist.py`). Any list edit pushed to `main` reaches every user
on their next run, and renaming or moving a file under `domains/` breaks every installed copy.

## List file format (`domains/*.sql`)

Despite the extension these are plain text, one entry per line: `pattern -- comment`. Lines starting
with `#` and blank lines are skipped. The split is on the literal ` -- ` (spaces included).

| File | Pi-hole `domainlist.type` | Comment prefix written by `pi.py` |
|---|---|---|
| `exact-whitelist.sql` | 0 | `SlyEWL` |
| `exact-blacklist.sql` | 1 | `SlyEBL` |
| `regex-whitelist.sql` | 2 | `SlyRWL` |
| `regex-blacklist.sql` | 3 | `SlyRBL` |

Regex entries are PCRE2 as evaluated by Pi-hole FTL. House style anchors with `(\.|^)name\.tld$` and
escapes every literal dot. `domains/adlists.txt` is one blocklist URL per line under `#` section
headers; its banner carries a hand-maintained `Updated: MM.DD.YY` line, and README has a
hand-maintained "Last updated" line.

## Sync semantics (why removals need care)

- `adlist.py` is a true sync: inserts remote URLs missing locally, and deletes local `adlist` rows
  whose `comment LIKE 'SlyADL%'` that are no longer in the remote file. User-added adlists are left
  alone because they lack the `SlyADL` tag.
- `pi.py` is not a sync. `add` inserts entries that are missing; `remove` deletes entries that are
  *currently in* the remote file. Deleting a line from a `.sql` file therefore orphans that entry in
  users' databases with no automatic cleanup path.
- Both scripts are interactive (`input()` menus), target the hardcoded `/etc/pihole/gravity.db`,
  retry on `database is locked`, and offer `pihole -g` / `pihole reloaddns` afterwards.
- `pi.py` configures logging at import time and creates `pihole_regex.log` in the CWD; `adlist.py`
  writes `pihole_adlist.log`.
- Users fetch each installer as a single file (`curl ... -o pi.py && sudo python3 pi.py`), so both
  must stay self-contained: no imports of sibling modules, and no third-party deps beyond `requests`
  and `colorama`.

## `pihole_admin.py` (repo root)

Standalone argparse CLI over `/etc/pihole/gravity.db` and `/etc/pihole/pihole-FTL.db`; not fetched by
the installers. Notes that span the file:

- Flags combine; `main()` runs them in a fixed order, not the order given on the command line.
- Heavy deps (matplotlib, seaborn, pandas, rapidfuzz/fuzzywuzzy, tld) are imported lazily in helper
  functions with fallbacks, so `--stats`, `--backup`, `--optimize` need only `requests` + `tabulate`.
  Keep new optional deps lazy the same way.
- `BLOCKED_STATUS_CODES` is the single definition of FTL "blocked" statuses; reuse it in queries.
- `PiholeDBAdmin(gravity_db_path, query_db_path)` takes paths, so it can be exercised against copies.
- `--remove-duplicates` only reports duplicates; it deletes nothing. `--clean DAYS` deletes from
  `query_storage`. `--advanced-query` executes arbitrary SQL against the FTL DB.
- Charts (`pihole_domain_stats.png`, `pihole_query_trends.png`) are written to the CWD.

## Commands

No project Conda env exists. The linter is stdlib-only; the other scripts need `requests`,
`colorama` (installers) and `tabulate` (admin), per `requirements.txt`.

```bash
# Lint the four .sql lists (control chars, duplicates, PCRE2 compile errors,
# regex-vs-exact and whitelist-vs-blacklist overlaps). Exit 0 clean, 1 warnings, 2 errors.
# Regex checks need pcre2grep on PATH and are skipped with a warning otherwise.
/home/jman/miniconda3/bin/python scripts/lint_domain_lists.py --verbose

# Syntax check every script
/home/jman/miniconda3/bin/python -m py_compile pihole_admin.py scripts/*.py

/home/jman/miniconda3/bin/python pihole_admin.py --help
```

Run the linter after any `.sql` edit. It does not check `adlists.txt`; verify new adlist URLs return
200 by hand. The scripts cannot run meaningfully off a Pi-hole host: test DB logic against a scratch
copy of `gravity.db` (pass paths to `PiholeDBAdmin`, or patch `PIHOLE_DB_PATH` in the installers),
never against `/etc/pihole`.

## Conventions

- Commit subjects are short imperative sentences; list-only changes are prefixed with the list name,
  e.g. `adlists: add HaGeZi Threat Intelligence Feeds (tif.txt) security layer`.
- When adding or removing adlist sources, update the `Added:` notes in the `adlists.txt` banner and
  its `Updated:` date.
- `CLAUDE.md` and `JEFF_START_HERE.md` are gitignored on purpose; keep them out of commits.
