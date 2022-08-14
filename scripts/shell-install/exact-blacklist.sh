#!/bin/bash

clear

# Get user's input
echo -e "Exact Blacklist Filters: [A]dd [R]emove [S]kip"
read a
clear
if [[ $a == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/exact-blacklist.py' | sudo python3
    echo -e "[i] The Exact Blacklist Filters have been added.\\n"
elif [[ $a == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/exact-blacklist.py' | sudo python3
    echo -e "[i] The Exact Blacklist Filters have been removed.\\n"
elif [[ $a == "S" ]]; then
    clear
    echo -e "Skipping ahead!\\n\\n"
fi

sleep 1
