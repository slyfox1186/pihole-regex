#!/bin/bash

# Get user's input
clear
echo 'RegEx Blacklist: [A]dd [R]emove [S]kip'
read i
clear
if [[ $i == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/regex-blacklist.py' | sudo python3
elif [[ $i == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/regex-blacklist.py' | sudo python3
elif [[ $i == "S" ]]; then
    clear
    echo '[i] Loading: RegEx Whitelist'
    sleep 1
    . pihole-regex/regex-whitelist.sh
    exit 0
fi

read -t 30 -p 'Press Enter to continue...'
