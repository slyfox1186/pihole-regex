Got it, here's the updated markdown script with the announcement of the new "pihole_admin.py" script:

# Pi-hole® v5+ FTLDNS: Advanced Filter Collection
Maximize the efficiency of your Pi-hole setup with our extensive collection of Regular Expressions (RegEx) and Exact Match filters. Designed to block a broad range of domains effectively, our filters simplify your blocking strategy by minimizing the need for numerous individual entries. Additionally, this repository includes customizable Exact Match filters for precise domain blocking and tools to facilitate the easy management of Adlist Group entries.

## Announcement: New Pi-hole Database Management Tool
We're excited to announce the addition of a new script to our Pi-hole toolset! The "pihole_admin.py" script is a powerful Python-based tool that provides advanced management capabilities for your Pi-hole database. Some of the key features include:

- Optimize the Pi-hole database to reduce size and fragmentation
- Backup the Pi-hole database to a specified location
- Fetch comprehensive statistics about your Pi-hole setup
- Clean up old data from the query storage
- Add or remove domains from the whitelist and blacklist
- Update the gravity database
- Analyze top blocked and allowed domains
- Run custom SQL queries on the Pi-hole databases
- Check for Pi-hole updates
- Remove duplicate domains across all lists
- Find similar domains based on a specified similarity threshold

This tool is designed to simplify the management of your Pi-hole and provide deeper insights into your network's activity. You can find the script in our GitHub repository at [link-to-script].

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

### Prerequisites
To get started, ensure your system meets the following requirements:

```bash
sudo apt-get update
sudo apt-get install -y curl python3 python3-colorama sqlite3
```

Another way to install the colorama module:

```bash
pip install colorama
```

### Remote Management Tools
For managing your Pi-hole remotely, consider using one of the following SSH clients:

- **[OpenSSH](https://www.openssh.com/)** - A secure shell for remote management.
- **[PuTTY](https://www.putty.org/)** - A popular SSH and telnet client for Windows.
- **[Termius](https://termius.com/)** - A versatile SSH client for Android, iOS, and Desktop.

## Installation
Follow these steps to apply the advanced filter collection to your Pi-hole setup:

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
