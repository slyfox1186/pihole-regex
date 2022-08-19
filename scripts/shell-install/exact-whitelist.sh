#!/bin/bash

# Get user's input
clear
echo 'Exact Whitelist: [A]dd [R]emove [S]kip'
read i
clear
if [[ $i == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/exact-whitelist.py' | sudo python3
elif [[ $i == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/exact-whitelist.py' | sudo python3
elif [[ $i == "S" ]]; then
    clear
    echo '[i] Skipping ahead!'
    sleep 1
    . regex-blacklist.sh
fi

read -t 30 -p 'Press Enter to continue...'
