#!/bin/bash

# This script will prompt the user to add or remove the domains in your Pi-hole's Adlists
# Comments are optional, you can remove them from being added to Pi-hole by placing a #
# in front of each variable. Example: COMMENT1 >> #COMMENT1

# Make user input case insensitive
shopt -s nocasematch

# Change this to the full path of gravity's database if the one below is wrong
DB_FILE='/etc/pihole/gravity.db'

# Display the script's purpose in terminal
clear
echo -e "This script will modify your Pi-hole's Adlists\\n"

# Prompt the user with Adlist option 1
echo -e "What do you want to do?\\n"
echo '[1] Add domains'
echo '[2] Remove all domains (Beware! This literally means ALL found lists.)'
echo '[3] Exit'
read a
if [[ "$a" == "1" ]]; then
    echo 'Continuing'
    clear
elif [[ "$a" == "2" ]]; then
    sqlite3 "$DB_FILE" "DELETE FROM adlist"
    clear
    echo -e "All domains have been removed from Pi-hole's adlists\\n"
    exit
elif [[ "$a" == "3" ]]; then
    clear
    exit
else
    echo -e "Warning: Bad user input\\n"
    read -p 'Press Enter to start over.'
    clear
    bash "$0"
    exit 1
fi

URL1='https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlist/adlists.txt'
COMMENT1='SlyFox1186 - Firebog + Other'
URL2='https://v.firebog.net/hosts/lists.php?type=tick'
COMMENT2='Firebog - Ticked'
URL3='https://v.firebog.net/hosts/lists.php?type=nocross'
COMMENT3='Firebog - Non-crossed'
URL4='https://v.firebog.net/hosts/lists.php?type=all'
COMMENT4='Firebog - All'
# SET OUTPUT FILE LOCATION
AD_TMP='/tmp/adlist.txt'

# Prompt the user with Adlist option 2
echo -e "Choose which adlist to import into Pi-hole\\n"
echo "[1] SlyFox1186 (Recommended. Sly's personal lists with \"Firebog's - Ticked + Non-Crossed\")"
echo '[2] Firebog: Ticked (Recommended for builds with little oversight.)'
echo '[3] Firebog: Ticked + Non-Crossed (Similar to the "Ticked List" but may need more attention.)'
echo '[4] Firebog: All (Not recommended. False positives abound!)'
read b
clear
if [[ "$b" == "1" ]]; then
    wget --user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0' -qO - "$URL1" |
    sed '/^#/ d' | sed '/^$/ d' > "$AD_TMP"
    cat "$AD_TMP" |
    xargs -n1 -I {} sqlite3 "$DB_FILE" "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}','$COMMENT1')"
elif [[ "$b" == "2" ]]; then
    wget --user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0' -qO - "$URL2" |
    sed '/^#/ d' | sed '/^$/ d' > "$AD_TMP"
    cat "$AD_TMP" |
    xargs -n1 -I {} sqlite3 "$DB_FILE" "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}','$COMMENT2')"
elif [[ "$b" == "3" ]]; then
    wget --user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0' -qO - "$URL3" |
    sed '/^#/ d' | sed '/^$/ d' > "$AD_TMP"
    cat "$AD_TMP" |
    xargs -n1 -I {} sqlite3 "$DB_FILE" "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}','$COMMENT3')"
elif [[ "$b" == "4" ]]; then
    wget --user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0' -qO - "$URL4" |
    sed '/^#/ d' | sed '/^$/ d' > "$AD_TMP"
    cat "$AD_TMP" |
    xargs -n1 -I {} sqlite3 "$DB_FILE" "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}','$COMMENT4')"
else
    echo -e "Warning: Bad user input...\\n"
    read -p 'Press Enter to start over.'
    clear
    bash "$0"
    exit 1
fi

# Prompt the user to update Gravity's database
clear
echo -e "Update Gravity?\\n"
echo '[1] Yes'
echo '[2] No'
read c
clear
if [[ "$c" == "1" ]]; then
    pihole -g
    echo -e "\\nDone!\\n"
else
    exit
fi

if [ if "$AD_TMP" ]; then rm "$AD_TMP"; fi

UNSET AD_TMP COMMENT1 COMMENT2 COMMENT3 COMMENT4 DB_FILE URL1 URL2 URL3 URL4
