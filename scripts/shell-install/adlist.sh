#!/bin/bash
# shellcheck disable=SC2162

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
    echo 'You must run this script as root/sudo.'
    echo
    exit 1
fi

if ! which 'sqlite3'; then
    echo 'sqlite3 must be installed to run this script.'
    echo
    exit 1
fi

# Delete any extra files that were downloaded alongside the other scripts that have no uses.
if [ -f 'index.html' ] || [ -f 'urls.txt' ]; then
    rm 'index.html' 'urls.txt'
fi

# Make user input case insensitive
shopt -s nocasematch

# Set a failure function
fail_fn()
{
    printf "\n%s\n\n%s\n%s\n\n" \
        "[x] $1" \
        'Please enter a support ticket at: ' \
        'https://github.com/slyfox1186/pihole-regex/issues'
    exit 1
}

# Function to exit script
fn_done()
{
    printf "\n%s\n\n%s\n%s\n\n" \
        '[i] The script has completed.' \
        'Please make sure to star this repo to show your support!' \
        'https://github.com/slyfox1186/pihole-regex'
    exit 0
}

# Function to prompt the user to restart Pi-hole's DNS resolver
fn_dns()
{
    local dns_choice
    printf "\n%s\n\n%s\n%s\n\n" \
        'Would you like to restart Pi-hole'\''s DNS resolver? (Recommended)' \
        '[1] Yes' \
        '[2] No'
    read -p 'Enter a number: ' dns_choice
    clear
    if [[ "$dns_choice" -eq '1' ]]; then
        sudo pihole restartdns
    fi
}

# Function to prompt the user to update Gravity's database
fn_gravity()
{
    local gravity_choice
    printf "\n%s\n\n%s\n%s\n\n" \
        'Would you like to update Gravity'\''s database? (Recommended to enable any changes made)' \
        '[1] Yes' \
        '[2] No'
    read -p 'Your choices are (1 or 2): ' gravity_choice
    clear
    if [[ "$gravity_choice" -eq '1' ]]; then
        pihole -g
    fi
}

# Set adlist url variable
ad_url='https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlist/adlists.txt'
# Set the comments
c1='SlyADL - SlyFox1186 + Firebog'\''s Ticked + Non-Crossed'
c2='SlyADL - Firebog - Ticked'
c3='SlyADL - Firebog - Non-Crossed'
c4='SlyADL - Firebog - All'
url_base='https://v.firebog.net/hosts/lists.php?type'
gravity="$(sudo find /etc -type f -name gravity.db)"

# If necessary change the value of the GRAVITY variable to the full path of the 'gravity.db' file
if [ -x "$gravity" ]; then
    fail_fn 'Unable to find the full path of the "gravity.db" file in the /etc folder.'
fi

# Store the online adlist file that contains all of the urls of interest in the system's tmp
# folder to keep things tidy while the script parses each line of text looking for valid urls
# while discarding any lines that begin with a hashtag '#' or are blank
list='/tmp/adlist.txt'
ua="--user-agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'"

# Prompt the user with choice 1
printf "\n%s\n\n%s\n\n%s\n%s\n%s\n\n" \
    'Modify the Pi-hole Adlist Group' \
    'Enter one of the selections.' \
    '[1] Add domains' \
    '[2] Remove all domains (This should only delete lists added by this script)' \
    '[3] Exit'
read -p 'Your choices are (1 to 3): ' ad_choice_1

case "$ad_choice_1" in
    1)
        clear
        ;;
    2)
        if sqlite3 "$gravity" "DELETE FROM adlist WHERE comment LIKE '%SlyADL%'"; then
            echo 'Success: All adlists have been removed from Pi-hole.'
            fn_gravity
            fn_dns
            fn_done
        else
            fail_fn 'Unable to delete the adlists from Gravity'\''s database.'
        fi
        ;;
    3)
        fn_done
        ;;
    *)
        clear
        fail_fn 'Bad user input.'
        ;;
esac

# Prompt the user with choice 2
printf "%s\n\n%s\n%s\n%s\n%s\n\n" \
    'Choose from the adlists below to insert their contents into the Gravity database.' \
    '[1] SlyFox1186: [Personal Adlist] - Self made with lists from the good work of others. (Includes: Firebog Ticked).' \
    '[2] Firebog:    [Ticked] - Perfect for system admins with little time available to fix database issues.' \
    '[3] Firebog:    [Non-Crossed] - These domains are generally less safe than the "Tick" list and most likely have an increased risk of false positives.' \
    '[4] Firebog:    [All] - False positives are very likely and will required much more effort than the average system admin would wish to spend fixing a database.'
read -p 'Your choices are (1 to 4): ' ad_choice_2
clear

case "$ad_choice_2" in
    1)
        wget "$ua" -qO - "$ad_url" |
        sed '/^#/ d' | sed '/^$/ d' > "$list"
        cat < "$list" | xargs -n1 -I{} sqlite3 "$gravity" \
        "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"$c1\")"
        ;;
    2)
        wget "$ua" -qO - "$url_base"=tick |
        sed '/^#/ d' | sed '/^$/ d' > "$list"
        cat < "$list" | xargs -n1 -I{} sqlite3 "$gravity" \
        "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"$c2\")"
        ;;
    3)
        wget "$ua" -qO - "$url_base"=nocross |
        sed '/^#/ d' | sed '/^$/ d' > "$list"
        cat < "$list" | xargs -n1 -I{} sqlite3 "$gravity" \
        "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"$c3\")"
        ;;
    4)
        wget "$ua" -qO - "$url_base"=all |
        sed '/^#/ d' | sed '/^$/ d' > "$list"
        cat < "$list" | xargs -n1 -I{} sqlite3 "$gravity" \
        "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"$c4\")"
        ;;
    *)
        fail_fn 'Bad user input.'
esac

# Prompt the user to update Gravity's database
fn_gravity
# Prompt the user to restart Pi-hole's DNS
fn_dns
rm -f "$0"
# Show exit message
fn_done
