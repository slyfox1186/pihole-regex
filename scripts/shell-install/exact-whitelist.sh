#!/bin/bash

# Get user's input
clear
echo '[i] Exact Whitelist: [A]dd [R]emove [S]kip'
read answer
clear
if [[ $answer == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/exact-whitelist.py' | sudo python3
elif [[ $answer == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/exact-whitelist.py' | sudo python3
elif [[ $answer == "S" ]]; then
    clear
    echo -e "[i] Skipping ahead!\\n"
    sleep 3
    . regex-blacklist.sh
    exit 0
fi

read -t 30 -p 'Press Enter to continue...'
