#!/bin/bash

# Get user's input
clear
echo -e "[i] RegEx Blacklist Filters: [A]dd [R]emove [S]kip"
read answer
clear
if [[ $answer == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/regex-blacklist.py' | sudo python3
    echo -e "[i] The RegEx Blacklist Filters were added to pi-hole.\\n"
elif [[ $answer == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/regex-blacklist.py' | sudo python3
    echo -e "[i] The RegEx Blacklist Filters were removed from pi-hole.\\n"
elif [[ $answer == "S" ]]; then
    clear
    echo -e "[i] Skipping ahead!\\n"
fi

read -p 'Press Enter to continue...'
