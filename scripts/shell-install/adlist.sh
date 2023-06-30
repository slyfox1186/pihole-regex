#!/bin/bash
# shellcheck disable=SC2162

################################################################################################################################
##
## Purpose: Add or remove Adlists from Pi-hole's database.
##
## Important: Make SURE to keep the text 'SlyADL - ' in the front of any comment you customize that were added by THIS script.
##           - This is because when you tell the script to remove domains it looks for that exact string in each domain's comment
##           - section as a way to identify what domains need removing and what needs to be ignored.
##
################################################################################################################################

clear

# MAKE USER INPUT CASE INSENSITIVE
shopt -s nocasematch

# INSTALL SQLITE3 IF MISSING
if ! which sqlite3 &>/dev/null; then
    sudo apt -y install sqlite3
    clear
fi

# DELETE ANY USELESS FILES THAT WERE DOWNLOADED ALONGSIDE THE OTHER SCRIPTS
if [ -f index.html ] || [ -f urls.txt ]; then
    sudo rm index.html urls.txt 2>/dev/null
fi

# FAILURE FUNCTION
fail_fn()
{
    printf "\n%s\n\n%s\n%s\n\n" \
        "[x] $1" \
        'Please enter a support ticket at: ' \
        'https://github.com/slyfox1186/pihole-regex/issues'
    exit 1
}

# EXIT FUNCTION
exit_fn()
{
    printf "\n%s\n\n%s\n%s\n\n" \
        '[i] The script has completed.' \
        'Please make sure to star this repo to show your support!' \
        'https://github.com/slyfox1186/pihole-regex'
    exit 0
}

# SET THE FUNCTION TO RESTART PIHOLE'S DNS
dns_fn()
{
    local choice

    printf "\n%s\n\n%s\n%s\n\n" \
        'Would you like to restart Pi-hole'\''s DNS resolver? (Recommended)' \
        '[1] Yes' \
        '[2] No'
    read -p 'Enter a number: ' choice

    clear

    case "$choice" in
        1)      sudo pihole restartdns;;
        2)      echo;;
        *)
                unset choice
                clear
                gravity_fn
                ;;
    esac
}

# Set the function to prompt the user to update Gravity's database
gravity_fn()
{
    local choice

    printf "\n%s\n\n%s\n%s\n\n" \
        'Would you like to update Gravity'\''s database? (Recommended)' \
        '[1] Yes' \
        '[2] No'
    read -p 'Your choices are (1 or 2): ' choice

    clear

    case "$choice" in
        1)      sudo pihole -g;;
        2)      echo;;
        *)
                unset choice
                clear
                gravity_fn
                ;;
    esac
}

# SET ADLIST URL VARIABLES
slyfox_url='https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlist/adlists.txt'

# SET THE COMMENTS
c1='SlyADL - SlyFox1186 + Firebog'\''s safe list'
c2='SlyADL - Firebog - Ticked'
c3='SlyADL - Firebog - Non-Crossed'
c4='SlyADL - Firebog - All'

# SET ADDITIONAL VARS
user_agent='--user-agent='\''Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'\'''
sly_adlist=/tmp/sly_adlist.txt
fb_adlist=/tmp/firebog_tick_adlist.txt
fb_url_base='https://v.firebog.net/hosts/lists.php?type'
gravity="$(sudo find /etc/pihole -type f -name gravity.db)"

# IF NECESSARY CHANGE THE VALUE OF THE GRAVITY VARIABLE TO THE FULL PATH OF THE 'GRAVITY.DB' FILE
if [ -z "$gravity" ]; then
    fail_fn "Unable to find the database file: $gravity"
fi

# PROMPT THE USER TO MODIFY THE PIHOLE DATABASE
printf "%s\n\n%s\n\n%s\n%s\n%s\n\n" \
    'Modify the Pi-hole Adlist Group' \
    'Enter one of the selections.' \
    '[1] Add domains' \
    '[2] Remove all domains (This should only delete lists added by this script)' \
    '[3] Exit'

read -p 'Your choices are (1 to 3): ' choice1
clear

case "$choice1" in
    1)          clear;;
    2)
                if sudo sqlite3 "$gravity" "DELETE FROM adlist WHERE comment LIKE '%SlyADL%'"; then
                    clear
                    echo 'Success: All adlists have been removed from Pi-hole.'
                    gravity_fn
                    dns_fn
                    exit_fn
                else
                    fail_fn 'Unable to delete the adlists from Gravity'\''s database.'
                fi
                ;;
    3)          exit_fn;;
    *)          fail_fn 'Bad user input.';;
esac

# PROMPT THE USER TO SELECT THE ADLIST
printf "%s\n\n%s\n%s\n%s\n%s\n\n" \
    'Choose from the adlists below to insert their contents into the Gravity database.' \
    '[1] SlyFox1186: [Personal Adlist] - Self made with lists from the good work of others. (Includes: Firebog Ticked).' \
    '[2] Firebog:    [Ticked] - Perfect for system admins with little time available to fix database issues.' \
    '[3] Firebog:    [Non-Crossed] - These domains are generally less safe than the "Tick" list and most likely have an increased risk of false positives.' \
    '[4] Firebog:    [All] - False positives are very likely and will required much more effort than the average system admin would wish to spend fixing a database.'
read -p 'Your choices are (1 to 4): ' choice2
clear

case "$choice2" in
    1)
        wget "$user_agent" -qO "$sly_adlist" "$slyfox_url"
        wget "$user_agent" -qO "$fb_adlist" "$fb_url_base"=tick
        sudo tee < "$fb_adlist" -a "$sly_adlist"
        sudo sed -i -e '/^#/ d' -i -e '/^$/ d' -i -e '/^$/d' 2>/dev/null "$sly_adlist"
        sudo sort -o "$sly_adlist" "$sly_adlist"
        sudo cat < "$sly_adlist" | sudo xargs -n1 -I{} sudo sqlite3 "$gravity" 2>/dev/null \
            "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"$c1\")"
        ;;
    2)
        wget "$user_agent" -qO "$fb_adlist" "$fb_url_base"=tick |
        sudo sed -i -e '/^#/ d' -i -e '/^$/ d' -i -e '/^$/d' 2>/dev/null > "$fb_adlist"
        sudo sort -o "$fb_adlist" "$fb_adlist"
        sudo cat < "$fb_adlist" | sudo xargs -n1 -I{} sudo sqlite3 "$gravity" 2>/dev/null \
            "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"$c2\")"
        ;;
    3)
        wget "$user_agent" -qO "$fb_adlist" "$fb_url_base"=nocross |
        sudo sed -i -e '/^#/ d' -i -e '/^$/ d' -i -e '/^$/d' 2>/dev/null > "$fb_adlist"
        sudo sort -o "$fb_adlist" "$fb_adlist"
        sudo cat < "$fb_adlist" | sudo xargs -n1 -I{} sudo sqlite3 "$gravity" 2>/dev/null \
            "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"$c3\")"
        ;;
    4)
        wget "$user_agent" -qO "$fb_adlist" "$fb_url_base"=all |
        sudo sed -i -e '/^#/ d' -i -e '/^$/ d' -i -e '/^$/d' 2>/dev/null > "$fb_adlist"
        sudo sort -o "$fb_adlist" "$fb_adlist"
        sudo cat < "$fb_adlist" | sudo xargs -n1 -I{} sudo sqlite3 "$gravity" 2>/dev/null \
            "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"$c4\")"
        ;;
    *)
        fail_fn 'Bad user input.';;
esac

# REMOVE TEMPORARY FILES CREATED BY THE SCRIPT
sudo rm "$fb_adlist" "$sly_adlist"

# PROMPT THE USER TO UPDATE GRAVITY'S DATABASE
gravity_fn

# PROMPT THE USER TO RESTART PI-HOLE'S DNS
dns_fn

# SHOW EXIT MESSAGE
exit_fn
