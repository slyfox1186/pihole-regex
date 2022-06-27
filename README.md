## RegEx Filters for Pi-hole
Customized RegEx and exact filters for use with Pi-hole v5+ (FTLDNS).

The purpose of this filter list is to compliment your existing blocklist's using powerful regular expressions that can cover a broad range of domains in one go.

All commands need to be entered via a Terminal after logging in and you need to have [**Python v3.6 or higher**] installed to execute the curl commands below. You can use PuTTY or your SSH client of choice if you're not on the pc running Pi-hole.

### Add/Update the RegEx filters to Pi-hole:
```
curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/install-regex-blacklist.py' | sudo python3
```

### Remove RegEx filters from Pi-hole:
```
curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/uninstall-regex-blacklist.py' | sudo python3
```

### Add exact whitelist filters to Pi-hole:
```
git clone 'https://github.com/slyfox1186/pihole.regex.git'
sudo python3 'pihole.regex/scripts/install-exact-whitelist.py'
```
### Remove exact whitelist filters from Pi-hole:
```
git clone 'https://github.com/slyfox1186/pihole.regex.git'
sudo python3 'pihole.regex/scripts/uninstall-exact-whitelist.py'
```
