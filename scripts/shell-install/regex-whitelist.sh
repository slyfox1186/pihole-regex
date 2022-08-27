#!/bin/bash

# make user input case insensitive
shopt -s nocasematch

# Get user's input
clear
echo 'RegEx Whitelist: [A]dd [R]emove [S]kip'
read i
clear
if [[ $i == "A" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/regex-whitelist.py' | sudo python3
else
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/regex-whitelist.py' | sudo python3
fi

echo
echo 'Done!'
echo
echo
echo 'Make sure to star this repository and show your support!'
echo 'Github Profile: https://github.com/slyfox1186/pihole-regex'
echo
read -p "Press Enter to restart Pi-hole's FTLDNS"

pihole -r
clear
pihole-g
