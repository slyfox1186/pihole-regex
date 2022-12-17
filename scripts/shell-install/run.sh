#!/bin/bash

clear

# Delete any useless files that get downloaded.
if [ -f 'index.html' ]; then rm 'index.html'; fi
if [ -f 'urls.txt' ]; then rm 'urls.txt'; fi

# Delete the pihole-regex folder if it already exists.
if [ -d 'pihole-regex' ]; then rm -r 'pihole-regex'; fi

# Create the pihole-regex folder to store the downloaded files in.
mkdir -p 'pihole-regex'

# define variables
SCRIPTS='exact-blacklist.sh exact-whitelist.sh regex-blacklist.sh regex-whitelist.sh'
MOVE_FILES=( ${SCRIPTS} run.sh )
# If the shell scripts exist, move them to the pihole-regex dir
for i in "${MOVE_FILES[@]}"
do
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

# remove variable 'i' since it is reused in the next step
unset i

# execute all scripts in the pihole-regex folder
for i in ${SCRIPTS[@]}; do source 'pihole-regex'/"${i}"; done

# remove all files that were downloaded
if [ -d 'pihole-regex' ]; then rm -R 'pihole-regex'; fi

echo
read -p 'Press enter to continue: '
clear

echo 'Restart Pihole'\''s DNS?'
echo
read -p '[Y]es or [N]o: ' uChoice
clear
if [[ "${uChoice}" == "Y" ]]; then pihole restartdns; fi

echo
echo 'Make sure to star this repository to show your support!'
echo 'GitHub Repository:  https://github.com/slyfox1186/pihole-regex'
echo
