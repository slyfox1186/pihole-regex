#!/bin/bash

clear

# Delete any useless files that get downloaded.
if [ -f 'index.html' ]; then rm 'index.html'; fi
if [ -f 'urls.txt' ]; then rm 'urls.txt'; fi

# Delete the pihole-regex folder if it already exists.
if [ -d pihole-regex ]; then rm -R pihole-regex; fi

# If needed (re)create the pihole-regex folder to store the downloaded files in.
mkdir -p 'pihole-regex'

# define variables
ADD_FILE=( exact-blacklist.sh exact-whitelist.sh regex-blacklist.sh regex-whitelist.sh run.sh )
# If the shell scripts exist, move them to the pihole-regex dir.
for i in "${ADD_FILE[@]}"; do
    if [ -f "${i}" ]; then
        mv -f "${i}" 'pihole-regex'
    else
        clear
        echo 'Script error: The shell scripts were not found.'
        echo
        echo 'Please report this on my GitHub Issues page.'
        echo 'https://github.com/slyfox1186/pihole-regex/issues'
        echo
        exit 1
    fi
done

# execute all scripts in pihole-regex.
for script in "${FILES[@]}"; do source pihole-regex/"${script}"; done
