#!/bin/bash

clear

# Get user's input
echo -e "RegEx Blacklist Filters: [A]dd [R]emove [S]kip"
read a
clear
if [[ $a == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/regex-blacklist.py' | sudo python3
    echo -e "[i] The RegEx Blacklist Filters were added to pi-hole.\\n\\n"
elif [[ $a == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/regex-blacklist.py' | sudo python3
    echo -e "[i] The RegEx Blacklist Filters were removed from pi-hole.\\n\\n"
elif [[ $a == "S" ]]; then
    clear
    echo -e "Skipping ahead!\\n\\n"
fi

sleep 3
clear
