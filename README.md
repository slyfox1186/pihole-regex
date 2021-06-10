## Regex Filters for Pi-hole
This is a custom regex filter file for use with Pi-hole v4+ (FTLDNS).

The purpose of this list is to compliment your existing blocklists using powerful regular expressions that can cover a very broad range of domains.

All commands will need to be entered via a Terminal after logging in and you need to have [**Python v3.6 or higher**] installed.
Some programs you can use are PuTTY or your SSH client of choice if you're not on the server pc.

### Add to Pi-hole:
```
curl -sSl https://raw.githubusercontent.com/slyfox1186/pihole.youtube.blocklist/main/install.py | sudo python3
```

### Remove from Pi-hole:
```
curl -sSl https://raw.githubusercontent.com/slyfox1186/pihole.youtube.blocklist/main/uninstall.py | sudo python3
```

### False Positives ###
You must manually add the whitelist if you want to fix any mobile youtube issues with your phone or tablets. [whitelist file](https://raw.githubusercontent.com/slyfox1186/pihole.youtube.blocklist/main/whitelists/whitelist.list). Use the adlists tool and restart gravity to enable the script.

### Keep regexps up-to-date with cron (optional)
The following instructions will create a cron job to run every monday at 02:30 (adjust the time to suit your needs):

1. Edit the root user's crontab (`sudo crontab -u root -e`)

2. Enter the following:
```
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
30 2 * * 1 /usr/bin/curl -sSl https://raw.githubusercontent.com/slyfox1186/pihole.youtube.blocklist/main/install.py | sudo /usr/bin/python3
```
3. Save changes

#### Removing the manually created cron job
If this script is the only thing you've added to the root user's crontab, you can run:

`sudo crontab -u root -r`

Otherwise, run:

`sudo crontab -u root -e` and remove the three lines listed above in the install instructions.
