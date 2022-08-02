## RegEx and Exact Filters for Pi-hole
Customized RegEx and exact filters for use with Pi-hole v5+ (FTLDNS).

The purpose of this filter list is to compliment your existing blocklist's using powerful regular expressions that can cover a broad range of domains in one go.

All commands need to be entered via a Terminal after logging in and you need to have [**Python v3.6 or higher**] installed to execute the curl commands below. You can use PuTTY or your SSH client of choice if you're not on the pc running Pi-hole.

### Add or Remove [ RegEx Blacklist ] filters:
```
sudo wget -c -O regex-blacklist.sh https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-install/regex-blacklist.sh && ./regex-blacklist.sh

```

### Add or Remove [ Exact Blacklist ] filters:
```
sudo wget -c -O exact-blacklist.sh https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-install/exact-blacklist.sh && ./exact-blacklist.sh

```

### Add or Remove [ RegEx Whitelist ] filters:
```
sudo wget -c -O regex-whitelist.sh https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-install/regex-whitelist.sh && ./regex-whitelist.sh

```

### Add or Remove [ Exact Whitelist ] filters:
```
sudo wget -c -O exact-whitelist.sh https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-install/exact-whitelist.sh && ./exact-whitelist.sh

```
