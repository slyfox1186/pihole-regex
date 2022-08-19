#!/bin/bash

# Get user's input
clear
echo 'Exact Blacklist: [A]dd [R]emove [S]kip'
read answer
clear
if [[ $answer == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/exact-blacklist.py' | sudo python3
elif [[ $answer == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/exact-blacklist.py' | sudo python3
elif [[ $answer == "S" ]]; then
    clear
    echo '[i] Skipping ahead!'
    sleep 1
    . exact-whitelist.sh
fi

read -t 30 -p 'Press [Enter] to continue...'
