#!/bin/bash

# Get user's input
clear
echo -e "[i] Exact Blacklist Filters: [A]dd [R]emove [S]kip"
read answer
clear
if [[ $answer == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/exact-blacklist.py' | sudo python3
    echo -e "[i] The Exact Blacklist Filters have been added.\\n\\n"
elif [[ $answer == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/exact-blacklist.py' | sudo python3
    echo -e "[i] The Exact Blacklist Filters have been removed.\\n\\n"
elif [[ $answer == "S" ]]; then
    clear
    echo -e "[i] Skipping ahead!\\n"
fi

sleep 2
