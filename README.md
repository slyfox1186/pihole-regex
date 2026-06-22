# Pi-hole® v6+ FTLDNS: Advanced Filter Collection
- Maximize the efficiency of your Pi-hole setup with our extensive collection of Regular Expressions (RegEx) and Exact Match filters. Designed to block a broad range of domains effectively, our filters simplify your blocking strategy by minimizing the need for numerous individual entries. Additionally, this repository includes customizable Exact Match filters for precise domain blocking and tools to facilitate the easy management of Adlist Group entries.

## Last updated on 03.10.2025:
- Added the new commands for pi-hole's version 6+
- You NEED to update to the latest version to use both scripts to their full potential

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
- **[Termius](https://termius.com/)** - A versatile SSH client for Android, iOS, and Desktop.

## Installation
Follow these steps to apply the advanced filter collection to your Pi-hole setup:

### Required pip packages
The installer scripts (`pi.py` and `adlist.py`) only need two packages:
```bash
pip install colorama requests
```

### RegEx and Exact Lists
Download and execute the installation script for RegEx and Exact Match filters:

```bash
curl -LSso pi.py https://pi.optimizethis.net
sudo python3 pi.py
```

### Adlists
To apply the Adlists filters, download and run the corresponding script:

```bash
curl -LSso adlist.py https://adlist.optimizethis.net
sudo python3 adlist.py
```

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
