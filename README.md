# Pi-hole® v5+ FTLDNS: Advanced Filter Collection

Enhance your Pi-hole setup with our comprehensive collection of Regular Expressions (RegEx) and Exact Match filters. These filters are meticulously crafted to block a wide spectrum of domains efficiently, reducing the need for multiple individual entries. This repository also provides customizable Exact Match filters for targeted domain blocking and tools for easy management of the Adlist Group entries.

## Quick Links

- **[Pi-hole Official Website](https://pi-hole.net/)** - Start here for Pi-hole setup and information.

## Filter Lists Overview

Utilize our curated filter lists to enhance your Pi-hole's blocking capabilities. Each list targets specific types of unwanted content, allowing for more effective and precise control:

| Script Name        | Access Link |
|--------------------|-------------|
| Adlists            | [View](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlists.txt) |
| Exact Whitelist    | [View](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-whitelist.sql) |
| Exact Blacklist    | [View](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-blacklist.sql) |
| RegEx Whitelist    | [View](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/regex-whitelist.sql) |
| RegEx Blacklist    | [View](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/regex-blacklist.sql) |

## Getting Started

### Compatibility

- **Designed for:** Pi-hole (FTLDNS) version 5 and above.

### Prerequisites

Before starting, ensure your system has the necessary packages:

```bash
apt-get install curl python3 sqlite3
```

### Remote Management

If your Pi-hole setup is remote, consider using an SSH client for access:

- **[OpenSSH](https://www.openssh.com/)**
- **[PuTTY](https://www.putty.org/)**
- **[Termius](https://termius.com/)**

## Installation

Execute the following commands to apply the filters to your Pi-hole setup:

### RegEx and Exact Lists

```bash
curl -Lso pi.py https://pi.optimizethis.net; python3 pi.py
```

### Adlists

```bash
curl -Lso adlist.py https://adlist.optimizethis.net; python3 adlist.py
```
