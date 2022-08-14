#!/bin/bash

clear

# Get user's input
echo -e "Exact Whitelist Filters: [A]dd [R]emove [S]kip"
read a
clear
if [[ $a == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/exact-whitelist.py' | sudo python3
    echo -e "[i] The Exact Whitelist Filters have been added.\\n\\n"
elif [[ $a == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/exact-whitelist.py' | sudo python3
    echo -e "[i] The Exact Whitelist Filters have been removed.\\n\\n"
elif [[ $a == "S" ]]; then
    clear
    echo -e "Skipping ahead!\\n"
fi

sleep 1
