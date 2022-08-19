#!/bin/bash

# make user input case insensitive
shopt -s nocasematch

# Get user's input
clear
echo 'RegEx Whitelist: [A]dd [R]emove [S]kip'
read i
clear
if [[ $i == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/regex-whitelist.py' | sudo python3
elif [[ $i == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/regex-whitelist.py' | sudo python3
elif [[ $i == "S" ]]; then
    sleep 1
fi

echo
echo
echo 'Done!'
echo
echo 'Make sure to star this repository and show your support!'
echo 'Github Profile: https://github.com/slyfox1186/pihole-regex'
echo
echo
read -t 30 -p 'Press [Enter] to exit'
exit 0
