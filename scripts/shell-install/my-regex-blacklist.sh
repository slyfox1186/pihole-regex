#!/bin/bash

# make user input case insensitive
shopt -s nocasematch

# Get user's input
clear
echo 'My RegEx Blacklist: [A]dd [R]emove [S]kip'
read i
clear
if [[ $i == "A" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/my-regex-blacklist.py' | sudo python3
else
    [[ $i == "R" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/my-regex-blacklist.py' | sudo python3
fi

echo -e "\\n"
read -t 30 -p 'Press Enter to continue...'
