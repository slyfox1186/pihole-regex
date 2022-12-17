#!/bin/bash

# make user input case insensitive
shopt -s nocasematch

# Get user's input
clear
read -p 'Exact Blacklist >> [A]dd [R]emove [S]kip: ' iChoice
clear
if [[ "${iChoice}" == "A" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/exact-blacklist.py' | sudo python3
elif [[ "${iChoice}" == "R" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/exact-blacklist.py' | sudo python3
elif [[ "${iChoice}" == "S" ]]; then
    source 'pihole-regex/exact-whitelist.sh'
    exit
else
    echo 'Input error: Please try again.'
    echo
    read -p 'Press enter to start over.'
    unset iChoice
    bash 'pihole-regex/exact-blacklist.sh'
    exit 1
fi

echo
read -t 30 -p 'Press Enter to continue: '
