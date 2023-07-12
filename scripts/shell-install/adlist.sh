#!/bin/bash
# shellcheck disable=SC2162

################################################################################################################################
##
## Purpose: Add or remove Adlists from Pi-hole's database.
##
## Important: Make SURE to keep the text 'SlyADL - ' in the front of any comment you customize that was added by THIS script.
##           - This is because when you tell the script to remove domains it looks for that exact string in each domain's comment
##           - section as a way to identify what domains need removing and what needs to be ignored.
##
################################################################################################################################

clear

# INSTALL SQLITE3 USING APT PACKAGE MANAGER IF NOT INSTALLED
if ! which sqlite3 &>/dev/null; then
    sudo apt -y install sqlite3
    clear
fi

# SET GITHUB REPO URL VARIABLE
repo=https://github.com/slyfox1186/pihole-regex

# SET SLYFOX1186'S ADLIST URL VARIABLE
slyfox_url=https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlist/adlists.txt

# SET THE ADLIST COMMENTS VARIABLES
c1='SlyADL - SlyFox1186 + Firebog'\''s Ticked'
c2='SlyADL - Firebog - Tick Lists'
c3='SlyADL - Firebog - Non-Crossed Lists'
c4='SlyADL - Firebog - All Lists'

# SET CURL COMMAND VARIABLE
user_agent='--user-agent='\''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'\'''

# STORE TEMPORARY FILES AND DIRECTORIES IN VARIABLES
tmp_dir="$(mktemp -d)"
sly_adlist="$tmp_dir"/sly_adlist.txt
fb_adlist="$tmp_dir"/firebog_adlist.txt
fb_url_base=https://v.firebog.net/hosts/lists.php?type
gravity="$(sudo find /etc -type f -name gravity.db)"

# DELETE ANY USELESS FILES THAT WERE DOWNLOADED WITH THE ADLIST SCRIPT
if [ -f index.html ] || [ -f urls.txt ]; then
    sudo rm index.html urls.txt 2>/dev/null
fi

# FUNCTION TO SHOW THE EXIT MESSAGE
exit_message_fn()
{
    printf "\n%s\n\n%s\n%s\n\n" \
        '[i] The script has finished.' \
        'Please make sure to star this repo to show your support!' \
        "$repo"
}

# FUNCTION TO REPORT FAILURES
fail_fn()
{
    printf "\n%s\n\n%s\n%s\n\n" \
        "[x] $1" \
        'Please submit a support issue for any unexpected bugs at: ' \
        "$repo/issues"
    exit 1
}

# FUNCTION TO PROMPT THE USER TO RESTART PIHOLE'S DNS
dns_fn()
{
    local choice
    clear

    printf "\n%s\n\n%s\n%s\n\n" \
        "Would you like to restart Pi-hole's DNS resolver? (Recommended)" \
        '[1] Yes' \
        '[2] No'
    read -p 'Enter a number: ' choice
    clear

    case "$choice" in
        1)      sudo pihole restartdns;;
        2)      echo;;
       '')      sudo pihole restartdns;;
        *)      
                clear
                printf "%s\n\n" 'Bad user input. Reverting script...'
                sleep 3
                unset choice
                dns_fn
                ;;
    esac
}

# FUNCTION TO PROMPT THE USER TO UPDATE PI-HOLES GRAVITY DATABASE
gravity_fn()
{
    local choice
    clear

    printf "%s\n\n%s\n%s\n\n" \
        "Would you like to update Gravity's database? (Recommended)" \
        '[1] Yes' \
        '[2] No'
    read -p 'Your choices are (1 or 2): ' choice

    clear

    case "$choice" in
        1)      sudo pihole -g;;
        2)      echo;;
        '')     sudo pihole -g;;
        *)
                clear
                printf "%s\n\n" 'Bad user input. Reverting script...'
                sleep 3
                unset choice
                gravity_fn
                ;;
    esac
}

# MAKE SURE THE SCRIPT WAS ABLE TO LOCATE THE FULL PATH TO PIHOLE'S GRAVITY.DB FILE
if [ -z "$gravity" ]; then
    fail_fn 'Unable to locate the "gravity.db" file.'
fi

exit_commands_fn()
{
    clear
    # PROMPT THE USER TO UPDATE PI-HOLE'S GRAVITY DATABASE
    gravity_fn
    # PROMPT THE USER TO RESTART PI-HOLE'S DNS RESOLVER
    dns_fn
    # SHOW THE EXIT MESSAGE
    exit_message_fn
    # REMOVE THE TEMPORARY FILES AND DIRECTORIES CREATED BY THE SCRIPT
    sudo rm -fr "$0" "$tmp_dir"
    exit 0
}

# PROMPT THE USER TO MODIFY THE PIHOLE DATABASE
printf "%s\n\n%s\n\n%s\n%s\n%s\n\n" \
    'Modify the Pi-hole Adlist Group' \
    'Enter one of the following selections.' \
    '[1] Add domains' \
    '[2] Remove all domains (This should only delete Adlists that were added by this script)' \
    '[3] Exit'

read -p 'Your choices are (1 to 3): ' choice1
clear

case "$choice1" in
    1)      clear;;
    2)
            if sudo sqlite3 "$gravity" "DELETE FROM adlist WHERE comment LIKE '%SlyADL%'"; then
                clear
                echo 'Success: All Adlists added by this script have been removed from Pi-hole'\''s Gravity database.'
                sleep 3
                exit_commands_fn
            else
                fail_fn 'Unable to delete the Adlists added by this script from Gravity'\''s database.'
            fi
            ;;
    3)      exit_message_fn;;
    *)      fail_fn 'Bad user input.';;
esac

# PROMPT THE USER TO SELECT THE ADLIST
printf "%s\n%s\n\n%s\n%s\n%s\n%s\n\n" \
    'Choose from the Adlists below to insert their contents into the Gravity database.' \
    'Important: Only option 1 includes Adlists from: The Blocklist Project, Perflyst, and YouTube Blocklists.' \
    '[1] SlyFox1186: [Personal Adlists] Includes Adlists from Firebog'\''s Tick List, The BlockList Project, Perflyst, and YouTube 4 Pi-hole Blocklists.' \
    '[2] Firebog:    [Ticked] - Perfect for system admins with minimal spare time to fix database issues.' \
    '[3] Firebog:    [Non-Crossed] - These domains are generally less safe than the "Tick" list and most likely have an increased risk of false positives.' \
    '[4] Firebog:    [All] - False positives are very likely and will require much more effort than the average system admin would wish to spend fixing a database.'
read -p 'Your choices are (1 to 4): ' choice2

# CD INTO THE TEMPORARY DIRECTORY TO CREATE THE SCRIPTS NEEDED TO MODIFY THE GRAVITY DATABASE
cd "$tmp_dir" || exit 1
clear

case "$choice2" in
    1)
            curl -Lso "$sly_adlist" "$slyfox_url"
            sudo sed -i -e '/^#/ d' -i -e '/^$/ d' -i -e '/^$/d' "$sly_adlist"
            sudo sort -o "$sly_adlist" "$sly_adlist" 2>/dev/null
            sudo cat "$sly_adlist" | sudo xargs -I{} sudo sqlite3 "$gravity" 2>/dev/null \
                "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"$c1\")"
            ;;
    2)
            curl -Lso "$fb_adlist" "$fb_url_base"'=tick'
            sudo sed -i -e '/^#/ d' -i -e '/^$/ d' -i -e '/^$/d' "$fb_adlist"
            sudo sort -o "$fb_adlist" "$fb_adlist" 2>/dev/null
            sudo cat "$fb_adlist" | sudo xargs -I{} sudo sqlite3 "$gravity" 2>/dev/null \
                "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"$c1\")"
            ;;
    3)
            curl -Lso "$fb_adlist" "$fb_url_base"'=nocross'
            sudo sed -i -e '/^#/ d' -i -e '/^$/ d' -i -e '/^$/d' "$fb_adlist"
            sudo sort -o "$fb_adlist" "$fb_adlist" 2>/dev/null
            sudo cat "$fb_adlist" | sudo xargs -I{} sudo sqlite3 "$gravity" 2>/dev/null \
                "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"$c1\")"
            ;;
    4)
            curl -Lso "$fb_adlist" "$fb_url_base"'=all'
            sudo sed -i -e '/^#/ d' -i -e '/^$/ d' -i -e '/^$/d' "$fb_adlist"
            sudo sort -o "$fb_adlist" "$fb_adlist" 2>/dev/null
            sudo cat "$fb_adlist" | sudo xargs -I{} sudo sqlite3 "$gravity" 2>/dev/null \
                "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"$c1\")"
            ;; 
    *)      fail_fn 'Bad user input.';;
esac

# CALL THE REMAINING FUNCTIONS TO CLOSE OUT THE SCRIPT
exit_commands_fn
