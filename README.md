## RegEx and Exact Filters for Pi-hole
* [Exact Blacklist](https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/domains/blacklist/exact-blacklist.txt)
* [Exact Whitelist](https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/domains/whitelist/exact-whitelist.txt)
* [Exact Blacklist](https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/domains/blacklist/regex-blacklist.txt)
* [Exact Whitelist](https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/domains/whitelist/regex-whitelist.txt)

Filters for use with Pi-hole v5+ (FTLDNS).

The purpose of this filter list is to compliment your existing blocklist using powerful regular expressions that can cover a broad range of domains in one go.

All commands need to be entered via a Terminal after logging in and you need to have [**Python v3.6 or higher**] installed to execute the curl commands below. You can use PuTTY or your SSH client of choice if you're not on the pc running Pi-hole.

### Add or Remove RegEx and Exact Pi-hole Filters
```
wget -q - -i https://pihole.optimizethis.net; . run.sh

```
