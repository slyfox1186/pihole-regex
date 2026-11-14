# Pi-hole® v6+ FTLDNS: Advanced Filter Collection
- Maximize the efficiency of your Pi-hole setup with our extensive collection of Regular Expressions (RegEx) and Exact Match filters. Designed to block a broad range of domains effectively, our filters simplify your blocking strategy by minimizing the need for numerous individual entries. Additionally, this repository includes customizable Exact Match filters for precise domain blocking and tools to facilitate the easy management of Adlist Group entries.

## Last updated on 11.14.2026:
Every entry now has a description that says what the domain is and what it does, backed by sources you can check in [docs/domain-notes-sources.md](docs/domain-notes-sources.md). While checking every entry we also fixed four rules:

- Twitch extensions work again. A blocked Twitch server turned out to be the one that loads every extension, not an ad server.
- The LG Channels app on LG TVs can start again. Two LG services it needs were blocked; LG's tracking services stay blocked.
- Removed the allow for `pagecdn.io`. That domain no longer hosts code libraries and now sends visitors somewhere else.
- Fixed a rule so Apple's Swift Playgrounds downloads are allowed.

To get these changes, run `sudo python3 pi.py -a`. It also updates the descriptions on entries it manages.

## Updated on 11.13.2026:
This update is a full review of every domain in these lists. Companies move their services to new servers over time, so an entry that was right when it was added can fall out of date. We checked each one against how things work today and brought the lists up to date:

- Retired six blocklists whose author stopped maintaining them. The other malware and scam lists stay in place.
- Tightened an allow rule so a group of websites linked to a 2024 attack on websites is now blocked.
- Now blocks more ad and tracking services, including a few that the other lists in this collection were not catching.
- Removed blocks that affected a Windows Update service, LG TV updates and apps, the LG ThinQ app, some smart home appliances, county property records and sports scores.
- Removed entries for websites that no longer exist and improved the entry descriptions.
- Removed three broad rules that blocked college student portals, Maryland's unemployment website and other sites whose names start with `banner`, `beacon` or `affiliate`.
- Stopped blocking Brazilian law firm websites (`.adv.br`), the Jamaica tax portal and CCleaner's update server.
- Now blocks Microsoft Office telemetry that an older allow entry let through.

To get these changes, download fresh copies of `pi.py` and `adlist.py` with the `curl` commands below, then run `sudo python3 pi.py -a` and `sudo python3 adlist.py`. The new `pi.py` also updates the descriptions on entries it manages.

## Updated on 11.12.2026:
- Full audit of all five lists. Four allowlist regexes that Pi-hole could never load (they used lookaheads, which Pi-hole's regex engine does not support) were removed or rewritten
- Removed blocks that broke real services: YouTube playback and embeds, the whole `.xyz` domain, catch-all rules for Amazon AWS load balancers and US API endpoints, Snapchat, Steam sign-in, Prime Video, Philips Hue setup, LG and Samsung TV cover art, sign-in and updates
- Removed allow rules that reopened ads, trackers and phishing (`accounts.` on any domain, the Microsoft catch-all, Yahoo and Algolia analytics)
- Adlists: added HaGeZi Multi PRO, replaced the retired URLhaus hostfile with its malware-filter mirror, and dropped lists that were stale, duplicated or made for AdGuard Home, including the Block List Project YouTube list, which blocked YouTube's video servers
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

Each entry's description says what the domain is and what it does. The sources behind every description are listed in [docs/domain-notes-sources.md](docs/domain-notes-sources.md).

## Getting Started
### Compatibility
This collection is built and tested for Pi-hole (FTLDNS) version 6 or newer. Several adlists use the Adblock format (`||example.com^`), which needs FTL v5.22 or newer.

### Remote Management Tools
For managing your Pi-hole remotely, consider using one of the following SSH clients:

- **[OpenSSH](https://www.openssh.com/)** - A secure shell for remote management.
- **[PuTTY](https://www.putty.org/)** - A popular SSH and telnet client for Windows.
- **[Termius](https://termius.com/)** - An SSH client for Android, iOS, and desktop systems.

### Requirements
Both scripts need only Python 3.9 or newer, which Pi-hole's supported systems already have. There is nothing to install with pip.

### Recursive DNS with unbound (optional)
Pi-hole normally passes the lookups it does not block to an outside DNS provider. If you would rather not depend on one, Pi-hole can use its own recursive resolver, unbound, running on the same machine. Pi-hole's official guide walks through the setup and how to test it: [Pi-hole documentation: unbound](https://docs.pi-hole.net/guides/dns/unbound/).

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

Both scripts only change entries they manage, which are tagged in their comment. Entries you added with a comment of your own are never touched. Older versions of `pi.py` left some comments empty, so `pi.py` also takes over an entry that has no comment and matches one of the repository's domains. Add `--dry-run` to any change to see it first.

## Advanced: Pi-hole Database Administrator
`pihole_admin.py` is an optional power-user toolkit for managing the Pi-hole
databases directly (statistics, backups, optimization, duplicate detection,
query analysis, and reporting).

Install its dependencies (or run `pip install -r requirements.txt` for everything):
```bash
pip install requests tabulate          # result tables, --check-updates
pip install matplotlib pandas seaborn  # --report, --analyze-query-trends charts
pip install rapidfuzz tld              # --find-similar, --categorize-domains
```
Each package is loaded only when a command needs it, so `--help`, `--stats`,
`--backup`, and `--optimize` work with none of them installed. `--help` lists
which options need which package.

```bash
python3 pihole_admin.py --stats
python3 pihole_admin.py --report
python3 pihole_admin.py --help     # full list of commands
```

## Linting the filter lists
`scripts/lint_domain_lists.py` checks the `.sql` lists for control characters,
duplicate patterns, invalid hostnames, invalid regexes, and whitelist/blacklist
overlaps. Pi-hole compiles regexes with the TRE engine, which has no lookahead or
lookbehind, so the linter rejects those. When `pihole-FTL` is installed it also
compiles every regex with Pi-hole's own engine. The overlap checks use `pcre2grep`
(skipped with a warning if it is not installed):
```bash
python3 scripts/lint_domain_lists.py
python3 scripts/lint_domain_lists.py --check-tlds   # also check top-level domains against IANA's list
```
