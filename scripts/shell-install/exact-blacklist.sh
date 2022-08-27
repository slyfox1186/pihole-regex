#!/bin/bash

# make user input case insensitive
shopt -s nocasematch

# Get user's input
clear
echo 'Exact Blacklist: [A]dd [R]emove [S]kip'
read i
clear
if [[ $i == "A" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/exact-blacklist.py'L | sudo python3
elif [[ $i == "R" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/exact-blacklist.py'L | sudo python3
elif [[ $i == "S" ]]; then
    bash exact-whitelist.sh
    exit
fi

echo
read -t 30 -p 'Press Enter to continue.'
