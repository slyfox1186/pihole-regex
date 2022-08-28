#!/bin/bash

# This script will prompt the user to add or remove the listed domains to your Pi-hole's adlists

clear

# make user input case insensitive
shopt -s nocasematch

# only change these if they are wrong
GRAVITY='/etc/pihole/gravity.db'

# Add or remove Pi-hole's adlists
# Replace the variables below with the URL(s) of the adlists you wish to add
# Comments are optional, you can remove them from the script or place a # in front of the line

# prompt the user with the script's purpose
echo -e "This script modify your Pi-hole's adlists\\n"

# prompt user with adlist option 1
echo -e "What do you want to do?\\n"
echo '[1] Add domains'
echo '[2] Remove all domains'
read a
if [[ "$a" == "1" ]] || [[ "$a" == "2" ]]; then
    echo 'Continuing'
    clear
else
    echo 'Warning: Bad user input'
    echo
    read -p 'Press Enter to start over.'
    . "$0"
fi

# if remove was chosen then do so and exit script
if [[ "$a" == "2" ]]; then
    sqlite3 "$GRAVITY" "DELETE FROM adlist"
    echo -e "All domains have been removed from Pi-hole's adlists\\n"
    exit
fi

# prompt user with adlist option 2
echo -e "Choose which adlist to import into Pi-hole\\n"
echo '[1] Firebog: Ticked'
echo '[2] Firebog: Ticked + Non-Crossed'
echo '[3] Firebog: All'
echo '[4] SlyFox1186'
read i
clear
if [[ "$i" == "1" ]]; then
    URL1='https://v.firebog.net/hosts/lists.php?type=tick'
    COMMENT1='Firebog - Ticked'
    wget --user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0' -qNO - "$URL1" |
    sed '/^#/ d' | sed '/^$/ d' > '/tmp/adlist.txt'
    cat '/tmp/adlist.txt' |
    xargs -n1 -I {} sqlite3 "$GRAVITY" "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}','$COMMENT1')"
elif [[ "$i" == "2" ]]; then
    URL1='https://v.firebog.net/hosts/lists.php?type=tick'
    COMMENT1='Firebog - Ticked'
    URL2='https://v.firebog.net/hosts/lists.php?type=nocross'
    COMMENT2='Firebog - Non-crossed'
    wget --user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0' -qNO - "$URL1" |
    sed '/^#/ d' | sed '/^$/ d' > '/tmp/adlist.txt'
    cat '/tmp/adlist.txt' |
    xargs -n1 -I {} sqlite3 "$GRAVITY" "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}','$COMMENT1')"
    wget --user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0' -qNO - "$URL2" |
    sed '/^#/ d' | sed '/^$/ d' > '/tmp/adlist.txt'
    cat '/tmp/adlist.txt' |
    xargs -n1 -I {} sqlite3 "$GRAVITY" "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}','$COMMENT2')"
elif [[ "$i" == "3" ]]; then
    URL3='https://v.firebog.net/hosts/lists.php?type=all'
    COMMENT3='Firebog - All'
    wget --user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0' -qNO - "$URL3" |
    sed '/^#/ d' | sed '/^$/ d' > '/tmp/adlist.txt'
    cat '/tmp/adlist.txt' |
    xargs -n1 -I {} sqlite3 "$GRAVITY" "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}','$COMMENT3')"
elif [[ "$i" == "4" ]]; then
    URL4='https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlist/adlists.txt'
    COMMENT4='SlyFox1186 - Firebog + Other'
    wget --user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0' -qNO - "$URL4" |
    sed '/^#/ d' | sed '/^$/ d' > '/tmp/adlist.txt'
    cat '/tmp/adlist.txt' |
    xargs -n1 -I {} sqlite3 "$GRAVITY" "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}','$COMMENT4')"
else
    echo -e "Warning: Bad user input...\\n"
    read -p 'Press Enter to start over.'
    . "$0"
fi

clear
echo -e "Update Gravity?\\n"
read -p '[Y]es or [N]o: ' up
clear
if [[ "$up" == "Y" ]]; then
    pihole -g
else
    echo -e "\\n\\nDone!"
fi
