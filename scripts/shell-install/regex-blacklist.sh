#!/bin/bash

# make user input case insensitive
shopt -s nocasematch

# Get user's input
clear
echo 'RegEx Blacklist: [A]dd [R]emove [S]kip'
read i
clear
if [[ $i == "A" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/regex-blacklist.py' | sudo python3
elif [[ $i == "R" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/regex-blacklist.py' | sudo python3
elif [[ $i == "S" ]]; then
    clear
    echo '[i] Loading: RegEx Whitelist'
    sleep 1
    exit 0
fi

echo -e "\\n"
read -t 30 -p 'Press Enter to continue...'
exit 0
