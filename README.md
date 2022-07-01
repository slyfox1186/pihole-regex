## RegEx Filters for Pi-hole
Customized RegEx and exact filters for use with Pi-hole v5+ (FTLDNS).

The purpose of this filter list is to compliment your existing blocklist's using powerful regular expressions that can cover a broad range of domains in one go.

All commands need to be entered via a Terminal after logging in and you need to have [**Python v3.6 or higher**] installed to execute the curl commands below. You can use PuTTY or your SSH client of choice if you're not on the pc running Pi-hole.

### Add or Remove the [RegEx Blacklist] filters:
```
curl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-scripts/regex-blacklist.sh' > 'regex-blacklist.sh'
source 'regex-blacklist.sh'
```

### Add or Remove the [RegEx Whitelist] filters:
```
curl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-scripts/regex-whitelist.sh' > 'regex-whitelist.sh'
source 'regex-whitelist.sh'
```

### Add or Remove the [Exact Whitelist] filters:
```
curl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-scripts/exact-whitelist.sh' > 'exact-whitelist.sh'
source 'exact-whitelist.sh'
```
