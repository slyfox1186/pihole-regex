## RegEx and Exact Filters for Pi-hole
Customized RegEx and exact filters for use with Pi-hole v5+ (FTLDNS).

The purpose of this filter list is to compliment your existing blocklist's using powerful regular expressions that can cover a broad range of domains in one go.

All commands need to be entered via a Terminal after logging in and you need to have [**Python v3.6 or higher**] installed to execute the curl commands below. You can use PuTTY or your SSH client of choice if you're not on the pc running Pi-hole.

### Add/Remove ALL lists
```
wget -c -q -i https://optimizethis.net
. exact-blacklist.sh && \
. exact-whitelist.sh && \
. regex-blacklist.sh && \
. regex-whitelist.sh

```

#### Add/Remove `RegEx Blacklist`:
```
curl https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-install/regex-blacklist.sh > regex-blacklist.sh
. regex-blacklist.sh

```

#### Add/Remove `Exact Blacklist`:
```
curl https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-install/exact-blacklist.sh > exact-blacklist.sh
. exact-blacklist.sh

```

#### Add/Remove `RegEx Whitelist`:
```
curl https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-install/regex-whitelist.sh > regex-whitelist.sh
. regex-whitelist.sh

```

#### Add/Remove `Exact Whitelist`:
```
curl https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-install/exact-whitelist.sh > exact-whitelist.sh
. exact-whitelist.sh

```
