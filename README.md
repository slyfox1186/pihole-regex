## A collection of *RegEx* and *Exact* filters for use with Pi-hole® v5+ *FTLDNS*

The ***purpose*** of this repository is to compliment your existing **Pi-hole** filters using ***powerful*** regular expressions (**RegEx**) that cover a broad range of domains ***in one go***. Included are an optional customized list of **Exact** filters and the ability to add or remove entries from the **Adlist Group**.

## Filter Lists

| Script Names | Raw Links |
| :----: | :----: |
| Adlists | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlists.txt) |
| Exact Whitelist | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-whitelist.sql) |
| Exact Blacklist | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-blacklist.sql) |
| RegEx Whitelist | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/regex-whitelist.sql) |
| RegEx Blacklist | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/regex-blacklist.sql) |

## Requirements and other important information
**Made for:** Pi-hole (FTLDNS) v5+
  - Website: [https://pi-hole.net/](https://pi-hole.net/)

### Required Packages
```bash
sudo apt install curl python3 sqlite3
```

## If you're *not* on the PC that's running Pi-hole
* **Use your ssh client of choice (examples below)**
  - **[OpenSSH](https://www.openssh.com/)**
  - **[PuTTY](https://www.putty.org/)**
  - **[Termius](https://termius.com/)**

## To execute, run each of the below commands

### RegEx and Exact Lists
```
curl -Lso pi.py https://pi.optimizethis.net; sudo python3 pi.py
```
### Adlists
```
curl -Lso adlist.py https://ad.optimizethis.net; sudo python3 adlist.py
```
