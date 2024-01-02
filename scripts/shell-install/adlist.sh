#!/usr/bin/env bash
# shellcheck disable=SC2162

#################################################################################################################################################
##
## Purpose:
##           - Add or remove adlists from Pi-hole's Gravity database.
##
## Important: 
##           - You must keep the text "SlyADL - " located in the comment boxes next to each adlist the same if it was added by this script.
##           - This is because if you tell the script to remove the domains added by this script it will look for that exact string in each
##           - adlists comment box to identify what domains should be removed and what the script should ignore, otherwise you will not be happy
##           - when all of the adlists you added by some other method are now missing.
##
################################################################################################################################################

clear

cwd="${PWD}"

# SET GITHUB REPO URL VARIABLE
web_repo='https://github.com/slyfox1186/pihole-regex'

# SET SLYFOX1186'S ADLIST URL VARIABLE
slyfox_url='https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlists.txt'

# SET THE ADLIST COMMENTS VARIABLES
c1='SlyADL - SlyFox1186 + Firebog'\''s Ticked'
c2='SlyADL - Firebog - Tick Lists'
c3='SlyADL - Firebog - Non-Crossed Lists'
c4='SlyADL - Firebog - All Lists'

# SET CURL COMMAND USER AGENT STRING
user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# STORE TEMPORARY FILES AND DIRECTORIES IN VARIABLES
random_dir="$(mktemp -d)"
sly_adlist='slyfox_adlist.txt'
fb_adlist='firebog_adlist.txt'
fb_base_url='https://v.firebog.net/hosts/lists.php?type'
gravity="$(find /etc/ -type f -name 'gravity.db')"

# DELETE ANY USELESS FILES THAT WERE DOWNLOADED WITH THE ADLIST SCRIPT
if [ -f 'index.html' ] || [ -f 'urls.txt' ]; then
    rm 'index.html' 'urls.txt' 2>/dev/null
fi

# MOVE THIS SCRIPT TO THE RANDOM DIRECTORY TO AVOID ISSUES WITH THE USERS FILES
if [ -f 'adlist.sh' ]; then
    mv "${random_dir}/adlist.sh"
fi

# CD INTO THE RANDOM DIRECTORY
cd "${random_dir}" || exit 1

# INSTALL SQLITE3 USING APT PACKAGE MANAGER IF NOT INSTALLED
if ! type -P sqlite3 &>/dev/null; then
    apt -y install sqlite3
    clear
fi

# FUNCTION TO SHOW THE EXIT MESSAGE
exit_message_fn()
{
    printf "\n%s\n\n%s\n%s\n\n"                                          \
        '[i] The script has finished.'                                   \
        'Please make sure to star this repository to show your support!' \
        "${web_repo}"
    rm -fr "${random_dir}"
    exit 0
}

# FUNCTION TO REPORT FAILURES
fail_fn()
{
    printf "\n%s\n\n%s\n%s\n\n"                                      \
        "[x] ${1}"                                                   \
        'Please submit a support issue for any unexpected bugs at: ' \
        "${web_repo}/issues"
    exit 1
}

#
# HAVE THE USER SELECT THE ADLIST PACKAGE THEY WANT TO INSTALL
#

choose_adlist_fn()
{
    local choice
    clear

    # PROMPT THE USER TO SELECT THE ADLIST
    printf "%s\n\n%s\n\n%s\n%s\n%s\n%s\n\n%s\n%s\n%s\n\n"                                                                                                         \
        'Choose an option below to insert their contents into Gravity'\''s database.'                                                                             \
        '[1] SlyFox1186'\''s Personal Adlist Collection - The below adlists are included:'                                                                        \
        '   - Firebog'\''s [Ticked]'                                                                                                                              \
        '   - The BlockList Project'                                                                                                                              \
        '   - Perflyst'                                                                                                                                           \
        '   - YouTube-4-Pi-hole'                                                                                                                                  \
        '[2] Firebog:    [Ticked] - Perfect for system admins with minimal spare time to fix database issues.'                                                    \
        '[3] Firebog:    [Non-Crossed] - These domains are generally less safe than the [Ticked] list and most likely have an increased risk of false positives.' \
        '[4] Firebog:    [All] - False positives are very likely and will require much more effort than the average system admin would wish to spend fixing a database.'
    read -p 'Your choices are (1 to 4): ' choice

    case "${choice}" in
        1)
                curl -A "${user_agent}" -Lso "${sly_adlist}" "${slyfox_url}"
                sed -i -e '/^#/ d' -i -e '/^$/ d' -i -e '/^$/d' "${sly_adlist}"
                sort -o "${sly_adlist}" "${sly_adlist}" 2>/dev/null
                cat < "${sly_adlist}" | xargs -I{} sqlite3 "${gravity}" 2>/dev/null \
                    "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"${c1}\")"
                ;;
        2)
                curl -A "${user_agent}" -Lso "${fb_adlist}" "${fb_base_url}"'=tick'
                sed -i -e '/^#/ d' -i -e '/^$/ d' -i -e '/^$/d' "${fb_adlist}"
                sort -o "${fb_adlist}" "${fb_adlist}" 2>/dev/null
                cat < "${fb_adlist}" | xargs -I{} sqlite3 "${gravity}" 2>/dev/null \
                    "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"${c2}\")"
                ;;
        3)
                curl -A "${user_agent}" -Lso "${fb_adlist}" "${fb_base_url}"'=nocross'
                sed -i -e '/^#/ d' -i -e '/^$/ d' -i -e '/^$/d' "${fb_adlist}"
                sort -o "${fb_adlist}" "${fb_adlist}" 2>/dev/null
                cat < "${fb_adlist}" | xargs -I{} sqlite3 "${gravity}" 2>/dev/null \
                    "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"${c3}\")"
                ;;
        4)
                curl -A "${user_agent}" -Lso "${fb_adlist}" "${fb_base_url}"'=all'
                sed -i -e '/^#/ d' -i -e '/^$/ d' -i -e '/^$/d' "${fb_adlist}"
                sort -o "${fb_adlist}" "${fb_adlist}" 2>/dev/null
                cat < "${fb_adlist}" | xargs -I{} sqlite3 "${gravity}" 2>/dev/null \
                    "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('{}',\"${c4}\")"
                ;; 
        *)      fail_fn 'Bad user input.';;
    esac
}

#
# REMOVE THE ADLISTS ADDED BY THIS SCRIPT IF SELECTED
#

rm_adlists_fn()
{
    if sqlite3 "${gravity}" "DELETE FROM adlist WHERE comment LIKE '%SlyADL%'"; then
        clear
        echo 'Success! All of the adlists added by this script have been removed from Pi-hole'\''s Gravity database.'
        sleep 3
        call_functions_fn
    else
        fail_fn 'Unable to delete the adlists added by this script from Gravity'\''s database.'
    fi
}

#
# FUNCTION TO PROMPT THE USER TO RESTART PIHOLE'S DNS RESOLVER
#

dns_restart_fn()
{
    local choice
    clear

    printf "\n%s\n\n%s\n%s\n\n"                                              \
        'Would you like to restart Pi-hole'\''s DNS resolver? (recommended)' \
        '[1] Yes'                                                            \
        '[2] No'
    read -p 'Enter a number: ' choice
    clear

    case "${choice}" in
        1)      pihole restartdns;;
        2)      return 0;;
       '')      pihole restartdns;;
        *)
                unset choice
                dns_restart_fn
                ;;
    esac
}

# FUNCTION TO PROMPT THE USER TO UPDATE PI-HOLES GRAVITY DATABASE
gravity_update_fn()
{
    local choice
    clear

    printf "%s\n\n%s\n%s\n\n"                                          \
        'Would you like to update the Gravity database? (recommended)' \
        '[1] Yes' \
        '[2] No'
    read -p 'Your choices are (1 or 2): ' choice
    clear

    case "${choice}" in
        1)      pihole -g;;
        2)      echo;;
        "")     pihole -g;;
        *)
                unset choice
                gravity_update_fn
                ;;
    esac
}

# MAKE SURE THE SCRIPT WAS ABLE TO LOCATE THE FULL PATH TO PIHOLE'S GRAVITY.DB FILE
if [ -z "${gravity}" ]; then
    fail_fn 'Failed to locate the file: gravity.db'
fi

choose_action_fn()
{
    local choice
    clear

    # PROMPT THE USER TO MODIFY THE PIHOLE DATABASE
    printf "%s\n\n%s\n\n%s\n%s\n%s\n\n"                                                           \
        'This will modify Pi-hole'\''s adlists stored in the Gravity database'                    \
        'Enter one of the following selections.'                                                  \
        '[1] Add domains'                                                                         \
        '[2] Remove all domains (only the ones previously added by this script)'                  \
        '[3] Exit'

    read -p 'Your choices are (1 to 3): ' choice
    clear

    case "${choice}" in
        1)      choose_adlist_fn;;
        2)      rm_adlists_fn;;

        3)      exit_message_fn;;
        *)
                unset choice
                choose_action_fn
                ;;
    esac
}
choose_action_fn
clear

#
# CALL THE REMAINING FUNCTIONS TO FINISH UP THE PROCESS
#

# PROMPT THE USER TO UPDATE PI-HOLE'S GRAVITY DATABASE
gravity_update_fn
# PROMPT THE USER TO RESTART PI-HOLE'S DNS RESOLVER
dns_restart_fn
# SHOW THE EXIT MESSAGE
exit_message_fn
