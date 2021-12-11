## RegEx Filters for Pi-hole
Customized RegEx filters for use with Pi-hole v4+ (FTLDNS).

The purpose of this filter list is to compliment your existing blocklist's using powerful regular expressions that can cover a broad range of domains in one go.

All commands need to be entered via a Terminal after logging in and you need to have [**Python v3.6 or higher**] installed to execute the curl commands below. You can use PuTTY or your SSH client of choice if you're not on the pc running Pi-hole.

### Add/Update the RegEx filters to Pi-hole:
```
/usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.youtube.blocklist/main/install.py' | sudo /usr/bin/python3 & \
/usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.youtube.blocklist/main/uninstall.py' | sudo /usr/bin/python3
```

### Remove RegEx filters from Pi-hole:
```
/usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.youtube.blocklist/main/uninstall.py' | sudo /usr/bin/python3
```

### Add whitelist filters to Pi-hole:
```
git clone 'https://github.com/slyfox1186/pihole.youtube.blocklist.git'
sudo python3 'https://raw.githubusercontent.com/slyfox1186/pihole.youtube.blocklist/main/whitelist/scripts/whitelist.py'
```

### Keep these RegEx filters up-to-date with cron (optional)
Instructions to create a cron job to auto update the RegEx filters every Sunday at 05:00 AM (adjust as needed):

1. Edit the root user's crontab: `sudo crontab -u root -e`

2. Enter the following:
```
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
0 5 * * 0 /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.youtube.blocklist/main/uninstall.py' | sudo /usr/bin/python3 && \
/usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.youtube.blocklist/main/install.py' | sudo /usr/bin/python3
```
3. Save changes

### Removing the manually created cron job
If this script is the only thing you've added to the root user's crontab, you can run:

`sudo crontab -u root -r`

Otherwise, run:

`sudo crontab -u root -e` and manually remove the four lines listed above in the install instructions.
