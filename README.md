# Pi-hole® v6+ FTLDNS: Advanced Filter Collection
- Maximize the efficiency of your Pi-hole setup with our extensive collection of Regular Expressions (RegEx) and Exact Match filters. Designed to block a broad range of domains effectively, our filters simplify your blocking strategy by minimizing the need for numerous individual entries. Additionally, this repository includes customizable Exact Match filters for precise domain blocking and tools to facilitate the easy management of Adlist Group entries.

## Last updated on 11.12.2026:
- `pi.py` and `adlist.py` were rebuilt: an interactive menu, command-line options for every task, previews before any change, and color help (`--help`)
- `adlist.py` can now remove one, several or all of its adlists, and turn them off or on
- Neither script needs any pip packages anymore

## Quick Links
- **[Pi-hole Official Website](https://pi-hole.net/)** - Your starting point for Pi-hole setup and comprehensive information.

## Filter Lists Overview
Our expertly curated filter lists are tailored to bolster your Pi-hole's domain blocking capabilities. Each list is focused on eliminating specific types of unwanted content, offering a more refined and efficient filtering approach:

| Script Name         | Access Link                                                                                     |
|---------------------|-------------------------------------------------------------------------------------------------|
| Adlists             | [View](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlists.txt)       |
| Exact Whitelist     | [View](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-whitelist.sql) |
| Exact Blacklist     | [View](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-blacklist.sql) |
| RegEx Whitelist     | [View](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/regex-whitelist.sql) |
| RegEx Blacklist     | [View](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/regex-blacklist.sql) |

## Getting Started
### Compatibility
This collection is compatible with Pi-hole (FTLDNS) version 5 and newer.

### Remote Management Tools
For managing your Pi-hole remotely, consider using one of the following SSH clients:

- **[OpenSSH](https://www.openssh.com/)** - A secure shell for remote management.
- **[PuTTY](https://www.putty.org/)** - A popular SSH and telnet client for Windows.
- **[Termius](https://termius.com/)** - An SSH client for Android, iOS, and desktop systems.

### Requirements
Both scripts need only Python 3.9 or newer, which Pi-hole's supported systems already have. There is nothing to install with pip.

### RegEx and Exact Lists
Download and run `pi.py`. With no options it opens a menu:

```bash
curl -LSso pi.py https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/pi.py
sudo python3 pi.py
```

Every menu task is also a command-line option:

```bash
sudo python3 pi.py -a              # add or update all four lists
sudo python3 pi.py -a exact-deny   # only the exact denylist
sudo python3 pi.py -r rd -n        # preview removing the regex denylist entries
sudo python3 pi.py -s netflix      # search the lists in Pi-hole
sudo python3 pi.py -b              # back up Pi-hole's database
sudo python3 pi.py --help          # every option
```

### Adlists
Download and run `adlist.py`. With no options it adds every adlist Pi-hole is missing:

```bash
curl -LSso adlist.py https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/adlist.py
sudo python3 adlist.py
```

To see, remove or switch off individual adlists:

```bash
sudo python3 adlist.py --list         # every adlist with its number and status
sudo python3 adlist.py -a             # add missing lists; keep retired lists
sudo python3 adlist.py -r 4,7         # remove adlists 4 and 7
sudo python3 adlist.py -r             # remove all managed adlists (asks first)
sudo python3 adlist.py --remove-all   # remove all of them (asks first)
sudo python3 adlist.py -d 12          # turn adlist 12 off but keep it
sudo python3 adlist.py -d             # turn all managed adlists off
sudo python3 adlist.py -e all         # turn all managed adlists back on
sudo python3 adlist.py --help         # every option
```

For `--add`, `--remove`, `--enable` and `--disable`, omit the items or pass
`all` by itself (case-insensitive) to select all applicable lists. Adding selects
the repository's lists; the other actions select only installed lists managed by
this script, including retired lists. Numbers and URLs still select individual
lists. Quote shell variables used as selections: `-r "$ITEMS"` rejects an empty
value, while `-r $ITEMS` with an empty variable means remove all. `--yes` skips
the removal confirmation.

Both scripts only change entries they added themselves, which are tagged in their comment. Entries you added to Pi-hole yourself are never touched. Add `--dry-run` to any change to see it first.

## Advanced: Pi-hole Database Administrator
`pihole_admin.py` is an optional power-user toolkit for managing the Pi-hole
databases directly (statistics, backups, optimization, duplicate detection,
query analysis, and reporting).

Install its dependencies (or run `pip install -r requirements.txt` for everything):
```bash
pip install requests tabulate          # core commands
pip install matplotlib pandas seaborn  # --report, --analyze-query-trends charts
pip install rapidfuzz tld              # --find-similar, --categorize-domains
```
The optional packages are loaded only when needed, so commands such as
`--stats`, `--backup`, and `--optimize` work with just `requests` and `tabulate`.

```bash
python3 pihole_admin.py --stats
python3 pihole_admin.py --report
python3 pihole_admin.py --help     # full list of commands
```

## Linting the filter lists
`scripts/lint_domain_lists.py` checks the `.sql` lists for control characters,
duplicate patterns, invalid regexes, and whitelist/blacklist overlaps. The regex
checks use `pcre2grep` (skipped with a warning if it is not installed):
```bash
python3 scripts/lint_domain_lists.py
```
