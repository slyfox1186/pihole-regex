#!/usr/bin/env bash

# Define necessary variables
user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'  # Set your desired user agent for HTTP requests
slyfox_url='https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlists.txt'  # Replace with the actual URL
fb_base_url='https://v.firebog.net/hosts/lists.php?type'  # Replace with the actual URL

# Comments for each adlist
c1='SlyADL - SlyFox1186 AdList - github.com/slyfox1186/pihole-regex'
c2='SlyADL - Firebog tick AdList - github.com/slyfox1186/pihole-regex'
c3='SlyADL - Firebog non-crossed AdList - github.com/slyfox1186/pihole-regex'
c4='SlyADL - Firebog all AdList - github.com/slyfox1186/pihole-regex'

# Path to Pi-hole's Gravity database
gravity='/etc/pihole/gravity.db'

# Function for handling failures
fail_fn()
{
    local message=$1
    printf "\n%s\n\n" "[ERROR] ${message}"
    exit 1
}

# Function to update Pi-hole's Gravity database
update_gravity()
{
    local choice

    printf "\n%s\n\n%s\n%s\n\n" \
        'Would you like to update the Gravity database? (Recommended)' \
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
                update_gravity
                ;;
    esac
}
# Function to choose adlist and add them to the database
choose_adlist_fn()
{
    local choice
    clear

    # Prompt the user to select the adlist
    printf "%s\n\n%s\n\n%s\n%s\n%s\n%s\n\n%s\n%s\n%s\n\n" \
        'Choose an option below to insert their contents into Pi-hole'\''s database.' \
        '[1] SlyFox1186'\''s Personal Adlist Collection - The below adlists are included:' \
        '   - Firebog'\''s [Ticked]' \
        '   - The BlockList Project' \
        '   - Perflyst' \
        '   - YouTube-4-Pi-hole' \
        '[2] Firebog:    [Ticked] - Perfect for system admins with minimal spare time.' \
        '[3] Firebog:    [Non-Crossed] - These domains are generally less safe than the [Ticked] list and most likely have an increased risk of false positives.' \
        '[4] Firebog:    [All] - False positives are very likely and will require much more effort than the average system admin would wish to spend fixing a database.'
    read -p 'Your choices are (1 to 4): ' choice

    case "${choice}" in
        1)  add_adlist_from_url "${slyfox_url}" "${c1}";;
        2)  add_adlist_from_url "${fb_base_url}=tick" "${c2}";;
        3)  add_adlist_from_url "${fb_base_url}=nocross" "${c3}";;
        4)  add_adlist_from_url "${fb_base_url}=all" "${c4}";;
        *)
            unset choice
            clear
            choose_adlist_fn
            ;;
    esac
}

# Function to add adlist from URL
add_adlist_from_url()
{
    local url=$1
    local comment=$2
    local adlist_file=$(mktemp)

    # Download the adlist
    curl -A "${user_agent}" -Lso "${adlist_file}" "${url}"
    if [ $? -ne 0 ]; then
        echo "Failed to download adlist from ${url}"
        return 1
    fi

    # Process and insert adlists
    sed -i -e '/^#/d' -e '/^$/d' "${adlist_file}"
    sort -o "${adlist_file}" "${adlist_file}"

    while read line
    do
        echo "Adding ${line} to the database"
        sqlite3 "${gravity}" "INSERT OR IGNORE INTO adlist (address, comment) VALUES ('${line}','${comment}')"
    done < "${adlist_file}"

    # Clean up
    rm "${adlist_file}"
}

# Function to remove adlists added by this script
rm_adlists_fn()
{
    if sqlite3 "${gravity}" "DELETE FROM adlist WHERE comment LIKE 'SlyADL%'"; then
        clear
        echo 'Success! All of the adlists added by this script have been removed from Pi-hole'\''s Gravity database.'
        sleep 3
    else
        fail_fn 'Unable to delete the adlists added by this script from Pi-hole'\''s Gravity database.'
    fi
}

# Main logic to call functions based on user choice
choose_action_fn()
{
    local choice
    clear

    printf "%s\n\n%s\n%s\n%s\n\n" \
        'Choose an action:' \
        '[1] Add adlists' \
        '[2] Remove all adlists added by this script' \
        '[3] Exit'

    read -p 'Enter your choice (1-3): ' choice

    case "${choice}" in
        1) choose_adlist_fn;;
        2) rm_adlists_fn;;
        3) exit;;
        *)
            unset choice
            choose_action_fn
            ;;
    esac
}

# Starting the script with the action choice
choose_action_fn

# Prompt the user to update the gravity database
update_gravity
