#!/usr/bin/env bash

clear

random_dir="$(mktemp -d)"

exit_fn()
{
    printf "\n%s\n\n%s\n\n"                                       \
        'Make sure to star this repository to show your support!' \
        'GitHub: https://github.com/slyfox1186/pihole-regex'
    exit 0
}

fail_fn()
{
    clear
    printf "%s\n\n%s\n%s\n\n"                          \
        "${1}"                                         \
        'Please report this on my GitHub Issues page.' \
        'https://github.com/slyfox1186/pihole-regex/issues'
    exit 1
}

cleanup_fn()
{
    local choice
    clear

    printf "%s\n\n%s\n%s\n\n"                                                \
        'Would you like to restart Pi-hole'\''s DNS resolver? (recommended)' \
        '[1] Yes'                                                            \
        '[2] No'
    read -p 'Your choices are (1 or 2): ' choice
    clear

    case "${choice}" in
        1)
                sudo rm -fr "${random_dir}"
                sudo pihole restartdns
                ;;
        2)      sudo rm -fr "${random_dir}";;
        "")
                sudo rm -fr "${random_dir}"
                sudo pihole restartdns
                ;;
        *)      
                unset choice
                clear
                exit_fn
                ;;
    esac
}

# Delete any useless files that get downloaded.
if [ -f 'index.html' ] || [ -f 'urls.txt' ]; then
    rm 'index.html' 'urls.txt' 2>/dev/null
fi

# Create the pihole-regex folder to store the downloaded files in.
mkdir -p "${random_dir}/pihole-regex"

# Define the variables and arrays
scripts='exact-blacklist.sh exact-whitelist.sh regex-blacklist.sh regex-whitelist.sh'
mv_scripts=("${scripts}" 'run.sh')

# If the shell scripts exist, move them to the pihole-regex dir
for f in ${mv_scripts[@]}
do
    if [ -f "${f}" ]; then
        if ! mv "${f}" "${random_dir}/pihole-regex"; then
            fail_fn 'Script error: Failed to move the shell scripts to the pihole-regex folder.'
        fi
    else
        fail_fn 'Script error: The shell scripts were not found.'
    fi
done

# Execute all of the shell scripts in the pihole-regex folder
for script in ${scripts[@]}
do
    source "${random_dir}/pihole-regex/${script}"
done

# Cleanup the leftover files and folders
cleanup_fn

# Show the user the exit message
exit_fn
