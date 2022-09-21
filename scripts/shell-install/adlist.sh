#!/bin/bash
clear

## Script purpose: Add or remove Adlists from Pi-hole's database.

## About Section ##
# Comments are optional and can be removed by adding a (hashtag '#') before each variable below.
# Example: C1='SOMETHING' >> #C1='SOMETHING'
# Important: Whatever you do make SURE to keep the text 'SlyADL - ' in the front of any comment you customize.
#   - The reason for this is because when you tell the script to remove domains it looks for that exact string
#   - in each domain's comment section as a way to identify what domains need removing and what needs to be ignored.

#Detects if script are not running as root...
if [[ $EUID > 0 ]]; then
    if which sudo &>/dev/null; then
        echo "If prompted, please enter the password for \"$USER\" to re-run this script with root privileges."
        read -p 'Press Enter to continue.'
        clear; sudo $0 $*
        exit
    else
        echo 'Warning: The sudo command was not found.'
        echo 'Info: You will need to re-run the script with root privileges.'
        echo
        read -p 'Press Enter to exit.'
        exit 1
    fi
fi

# Make user input case insensitive
shopt -s nocasematch

# Delete any extra files that were downloaded with the other scripts that have no uses.
if [ -f 'index.html' ]; then rm 'index.html'; fi
if [ -f 'urls.txt' ]; then rm 'urls.txt'; fi
 
# SET AD_URL URL
AD_URL='https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlist/adlists.txt'
# SET THE COMMENTS
C1="SlyADL - SlyFox1186 + Firebog's Ticked + Non-Crossed"
C2='SlyADL - Firebog - Ticked'
C3='SlyADL - Firebog - Non-Crossed'
C4='SlyADL - Firebog - All'
URL_BASE='https://v.firebog.net/hosts/lists.php?type'
GRAVITY='/etc/pihole/gravity.db'
# If necessary change the value of the GRAVITY variable to the full path of the 'gravity.db' file
if [ ! -f "$GRAVITY" ]; then
    clear
    echo "Warning: The '$GRAVITY' variable is not pointing to the full path of 'gravity.db' file."
    echo 'Info: Please make appropriate changes to the script and try again.'
    echo
    read -p 'Press Enter to exit.'
    exit 1
fi

# Store the online adlist file that contains all of the urls of interest in the system's tmp
# folder to keep things tidy while the script parses each line of text looking for valid urls
# while discarding any lines that begin with a hashtag '#' or are blank
LIST='/tmp/adlist.txt'
UA="--user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33'"

# Display the script's purpose in terminal
clear
echo 'Modify the Pi-hole Adlist Group'
echo

# PROMPT THE USER WITH THE FIRST CHOICE
echo 'Enter one of the selections?'
echo
echo '[1] Add domains'
echo '[2] Remove all domains (This should only delete lists added by this script.)'
echo '[3] Exit'
read CHOICE
if [[ "$CHOICE" == "1" ]]; then
    clear
elif [[ "$CHOICE" == "2" ]]; then
    sqlite3 '/etc/pihole/gravity.db' "DELETE FROM adlist WHERE comment LIKE '%SlyADL%'"
    clear; echo 'All Adlists have been removed from Pi-hole. Please wait while Pi-hole updates Gravity.'
    pihole -g
    exit
elif [[ "$CHOICE" == "3" ]]; then
    clear; exit
else
    echo -e "Warning: Bad user input\\n"
    read -p 'Press Enter to start over.'
    clear; bash "$0"
    exit 1
fi

# Prompt the user with Adlist option 2
echo "Choose from the Adlists below to insert their content into Gravity's database"
echo
echo '[1] SlyFox1186: [Personal Adlist] - Self made with lists from the good work of others. (Includes Firebog: Ticked + Non-Crossed).'
echo '[2] Firebog:    [Ticked] - Perfect for system admins with little time available to fix database issues.'
echo '[3] Firebog:    [Non-Crossed] - These domains are generally less safe than the "Tick" list and most likely have an increased risk of false positives.'
echo '[4] Firebog:    [All] - False positives are very likely and will required much more effort than the average system admin would wish to spend fixing a database.'
read CHOICE
clear
if [[ "$CHOICE" == "1" ]]; then
    wget "$UA" -qO - "$AD_URL" |
    sed '/^#/ d' | sed '/^$/ d' > "$LIST"
    cat "$LIST" |
    xargs -n1 -I {} sqlite3 "$GRAVITY" \
    "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"$C1\")"
elif [[ "$CHOICE" == "2" ]]; then
    wget "$UA" -qO - "$URL_BASE"=tick |
    sed '/^#/ d' | sed '/^$/ d' > "$LIST"
    cat "$LIST" |
    xargs -n1 -I {} sqlite3 "$GRAVITY" \
    "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}','$C2')"
elif [[ "$CHOICE" == "3" ]]; then
    wget "$UA" -qO - "$URL_BASE"=nocross |
    sed '/^#/ d' | sed '/^$/ d' > "$LIST"
    cat "$LIST" |
    xargs -n1 -I {} sqlite3 "$GRAVITY" \
    "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}','$C3')"
elif [[ "$CHOICE" == "4" ]]; then
    wget "$UA" -qO - "$URL_BASE"=all |
    sed '/^#/ d' | sed '/^$/ d' > "$LIST"
    cat "$LIST" |
    xargs -n1 -I {} sqlite3 "$GRAVITY" \
    "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}','$C4')"
else
    clear; read -t 4 -p 'Warning: Bad user input...starting over...'
    clear; bash "$0"
    exit 1
fi

# Prompt the user to update Gravity's database
clear
echo 'Would you like to update Gravity? (Highly recommended)'
echo
echo '[1] Yes'
echo '[2] No'
read CHOICE
clear
if [[ "$CHOICE" != "2" ]]; then pihole -g; fi

echo
echo 'The script has completed.'
echo

# Unset all variables used
unset AD_URL C1 C2 C3 C4 URL_BASE GRAVITY CHOICE LIST UA
