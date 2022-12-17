#!/bin/bash

# make user input case insensitive
shopt -s nocasematch

# Get user's input
clear
read -p 'RegEx Whitelist >> [A]dd [R]emove [S]kip: ' iChoice
clear
if [[ "${iChoice}" == "A" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/regex-whitelist.py' | python3
elif [[ "${iChoice}" == "R" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/regex-whitelist.py' | python3
elif [[ "${iChoice}" == "S" ]]; then
    clear
else
    echo 'Input error: Please try again.'
    echo
    read -p 'Press enter to start over.'
    unset iChoice
    bash 'pihole-regex/regex-whitelist.sh'
fi

echo
read -p 'Press Enter to continue: '
clear

echo 'Restart Pihole'\''s DNS?'
echo
read -p '[Y]es or [N]o: ' uChoice
clear
if [[ "${uChoice}" == "Y" ]]; then pihole restartdns; fi

# remove all files that were downloaded
if [ -d 'pihole-regex' ]; then rm -R 'pihole-regex'; fi

echo
echo 'Make sure to star this repository to show your support!'
echo 'GitHub Repository:  https://github.com/slyfox1186/pihole-regex'
echo
