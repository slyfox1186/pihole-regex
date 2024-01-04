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

cleanup_fn() { sudo rm -fr "${random_dir}"; }

# Create a random directory
random_dir="${PWD}/tmp.fasf09asfkpjamsfa090okmagfp"

if [ -d "${random_dir}" ]; then
    sudo rm -fr "${random_dir}"
fi
mkdir -p "${random_dir}"

# Change into the random directory before downloading the other files
cd "${random_dir}"

# Create a tmp file that stores the URL of all the required shell scripts
cat > 'urls.txt' <<EOF
https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python/exact-whitelist.py
https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python/exact-blacklist.py
https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python/regex-whitelist.py
https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python/regex-blacklist.py
EOF

# Download the required shell scripts using wget
wget -qN - -i 'urls.txt'

# Define the variables and arrays
scripts=('exact-blacklist.py' 'exact-whitelist.py' 'regex-whitelist.py' 'regex-blacklist.py')

# Execute all of the shell scripts in the pihole-regex folder
for f in ${scripts[@]}
do
    sudo python3 "${f}"
done

# Cleanup the leftover files and folders
cleanup_fn

# Show the user the exit message
exit_fn
