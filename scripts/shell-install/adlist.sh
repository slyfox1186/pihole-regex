#!/bin/bash

clear

#####################################################################################################################
##
## Purpose: Add or remove adlists from Pi-hole's database.
##
## About info
##
## Important: Whatever you do make SURE to keep the text 'SlyADL - ' in the front of any comment you customize.
##  - The reason for this is because when you tell the script to remove domains it looks for that exact string
##  - in each domain's comment section as a way to identify what domains need removing and what needs to be ignored.
##

# VERIFY THE SCRIPT HAS ROOT ACCESS BEFORE CONTINUING
if [[ "${EUID}" -gt '0' ]]; then
    echo 'You must run this script as root/sudo'
    echo
    exit 1
fi

if ! which sqlite3; then
    echo 'sqlite3 must be installed to run this script.'
    echo
    exit 1
fi

# Delete any extra files that were downloaded alongside the other scripts that have no uses.
if [[ -f 'index.html' ]]; then rm 'index.html'; fi
if [[ -f 'urls.txt' ]]; then rm 'urls.txt'; fi

# Make user input case insensitive
shopt -s nocasematch

# Function to exit script
fn_done()
{
    clear
    echo 'The script has completed.'
    echo
    echo 'Please make sure you report any issues on my GitHub page!'
    echo 'https://github.com/slyfox1186/pihole-regex/issues'
    echo
    exit
}

# Function to prompt the user to restart Pi-hole's DNS resolver
fn_dns()
{
    clear
    echo 'Would you like to restart Pi-hole'\''s DNS resolver? (Recommended)'
    echo
    echo '[1] Yes'
    echo '[2] No'
    echo
    read -p 'Enter a number: ' rChoice
    clear
    if [[ "${rChoice}" == "1" ]]; then pihole restartdns; fi
}

# Function to prompt the user to update Gravity's database
fn_gravity()
{
    clear
    echo 'Would you like to update Gravity'\''s database? (Recommended to enable any changes made)'
    echo
    echo '[1] Yes'
    echo '[2] No'
    echo
    read -p 'Enter a number: ' gChoice
    clear
    if [[ "${gChoice}" == "1" ]]; then pihole -g; fi
}

# Set adlist url variable
AD_URL='https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlist/adlists.txt'
# Set the comments
C1='SlyADL - SlyFox1186 + Firebog'\''s Ticked + Non-Crossed'
C2='SlyADL - Firebog - Ticked'
C3='SlyADL - Firebog - Non-Crossed'
C4='SlyADL - Firebog - All'
URL_BASE='https://v.firebog.net/hosts/lists.php?type'
GRAVITY='/etc/pihole/gravity.db'
# If necessary change the value of the GRAVITY variable to the full path of the 'gravity.db' file
if [[ ! -f "${GRAVITY}" ]]; then
    clear
    echo "Warning: The '\${GRAVITY}' variable is not pointing to the full path of 'gravity.db' file."
    echo 'Info: Please make appropriate changes to the script and try again.'
    echo
    read -p 'Press Enter to exit.'
    exit 1
fi

# Store the online adlist file that contains all of the urls of interest in the system's tmp
# folder to keep things tidy while the script parses each line of text looking for valid urls
# while discarding any lines that begin with a hashtag '#' or are blank
LIST='/tmp/adlist.txt'
UA="--user-agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0'"

# Display the script's purpose in terminal
clear
echo 'Modify the Pi-hole Adlist Group'
echo

# Prompt the user with choice 1
echo 'Enter one of the selections.'
echo
echo '[1] Add domains'
echo '[2] Remove all domains (This should only delete lists added by this script.)'
echo '[3] Exit'
read CHOICE
if [[ "${CHOICE}" == "1" ]]; then
    clear
elif [[ "${CHOICE}" == "2" ]]; then
    sqlite3 '/etc/pihole/gravity.db' "DELETE FROM adlist WHERE comment LIKE '%SlyADL%'"
    clear
    echo 'All adlists have been removed from Pi-hole.'
    sleep 2
    fn_gravity
    fn_dns
    fn_done
elif [[ "${CHOICE}" == "3" ]]; then
    clear
    exit
else
    echo -e "Warning: Bad user input\\n"
    read -p 'Press Enter to start over.'
    clear
    unset CHOICE
    bash "${0}"
    exit 1
fi

# Prompt the user with choice 2
echo 'Choose from the adlists below to insert their content into Gravity'\''s database'
echo
echo '[1] SlyFox1186: [Personal Adlist] - Self made with lists from the good work of others. (Includes Firebog: Ticked + Non-Crossed).'
echo '[2] Firebog:    [Ticked] - Perfect for system admins with little time available to fix database issues.'
echo '[3] Firebog:    [Non-Crossed] - These domains are generally less safe than the "Tick" list and most likely have an increased risk of false positives.'
echo '[4] Firebog:    [All] - False positives are very likely and will required much more effort than the average system admin would wish to spend fixing a database.'
read CHOICE
clear
if [[ "${CHOICE}" == "1" ]]; then
    wget "${UA}" -qO - "${AD_URL}" |
    sed '/^#/ d' | sed '/^$/ d' > "${LIST}"
    cat < "${LIST}" |
    xargs -n1 -I {} sqlite3 "${GRAVITY}" \
    "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"${C1}\")"
elif [[ "${CHOICE}" == "2" ]]; then
    wget "${UA}" -qO - "${URL_BASE}"=tick |
    sed '/^#/ d' | sed '/^$/ d' > "${LIST}"
    cat < "${LIST}" |
    xargs -n1 -I {} sqlite3 "${GRAVITY}" \
    "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"${C2}\")"
elif [[ "${CHOICE}" == "3" ]]; then
    wget "${UA}" -qO - "${URL_BASE}"=nocross |
    sed '/^#/ d' | sed '/^$/ d' > "${LIST}"
    cat < "${LIST}" |
    xargs -n1 -I {} sqlite3 "${GRAVITY}" \
    "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"${C3}\")"
elif [[ "${CHOICE}" == "4" ]]; then
    wget "${UA}" -qO - "${URL_BASE}"=all |
    sed '/^#/ d' | sed '/^$/ d' > "${LIST}"
    cat < "${LIST}" |
    xargs -n1 -I {} sqlite3 "${GRAVITY}" \
    "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"${C4}\")"
else
    clear; read -t 4 -p 'Warning: Bad user input...starting over...'
    clear; bash "${0}"
    exit 1
fi

# Prompt the user to update Gravity's database
fn_gravity
# Prompt the user to restart Pi-hole's DNS
fn_dns
# Show exit message
fn_done
