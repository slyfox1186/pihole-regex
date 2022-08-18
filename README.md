## RegEx and Exact filters for Pi-hole

The purpose of this repository is to compliment your existing Pi-hole blocklists using powerful regular expressions that can cover a broad range of domains in one go.

All commands need to be entered via a Terminal after logging in and you need to have [**Python v3.6 or higher**] installed to execute the commands below. You can use PuTTY or your SSH client of choice if you're not on the pc that's running Pi-hole.

* Filters for use with Pi-hole v5+ (FTLDNS)
* The Filter Lists
  - [Exact Blacklist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/blacklist/exact-blacklist.txt)
  - [Exact Whitelist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/whitelist/exact-whitelist.txt)
  - [RegEx Blacklist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/blacklist/regex-blacklist.txt)
  - [RegEx Whitelist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/whitelist/regex-whitelist.txt)

## User options: [ Add | Remove | Skip ]

* The script will prompt the user to press one of three keys.

```
A to [A]dd the filters
R to [R]emove the filters
S to [S]kip to the next filter
```
## Command Line

* Click the copy button to the right and paste this into a terminal to execute
```
wget -qN - -i https://pihole.optimizethis.net; sudo bash run.sh

```
