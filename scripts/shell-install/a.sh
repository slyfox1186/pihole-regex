#!/usr/bin/env bash
#shellcheck disable=SC2068,SC1090,SC2162

clear

if [ $EUID -eq 0 ]; then
    printf "%s\n\n" 'You must run this script WITHOUT root/sudo'
    exit 1
fi

exit_fn()
{
    printf "\n%s\n\n%s\n\n" \
        'Make sure to star this repository to show your support!' \
        'GitHub: https://github.com/slyfox1186/pihole-regex'
    exit 0
}

cleanup_fn()
{
    local choice
    clear

    printf "%s\n\n%s\n%s\n\n" \
        'Would you like to restart Pi-hole'\''s DNS resolver? (recommended)' \
        '[1] Yes' \
        '[2] No'
    read -p 'Your choices are (1 or 2): ' choice
    clear

    case "${choice}" in
        1)      sudo pihole restartdns;;
        2)      clear;;
        "")     sudo pihole restartdns;;
        *)      
                unset choice
                cleanup_fn
                ;;
    esac
    sudo rm -fr "${random_dir}"
}

# Create a random directory
random_dir="${PWD}/tmp.fasf09asfkpjamsfa090okmagfp"

if [ -d "${random_dir}" ]; then
    sudo rm -fr "${random_dir}"
fi
mkdir -p "${random_dir}"

# Change into the random directory before downloading the other files
cd "${random_dir}"

# Create a tmp file that stores the URL of all the required shell scripts
cat > wget.txt <<EOF
https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-install/exact-blacklist.sh
https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-install/exact-whitelist.sh
https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-install/regex-blacklist.sh
https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-install/regex-whitelist.sh
https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/shell-install/a.sh
EOF

# Download the required shell scripts using wget
wget -qN - -i 'wget.txt'
bash run.sh

# Define the variables and arrays
scripts=('exact-blacklist.sh' 'exact-whitelist.sh' 'regex-blacklist.sh' 'regex-whitelist.sh')

# Execute all of the shell scripts in the pihole-regex folder
for f in ${scripts[@]}
do
    source "${f}"
done

# Cleanup the leftover files and folders
cleanup_fn

# Show the user the exit message
exit_fn
