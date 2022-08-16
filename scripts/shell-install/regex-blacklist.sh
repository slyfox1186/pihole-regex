#!/bin/bash

# Get user's input
clear
echo -e "[i] RegEx Blacklist: [A]dd [R]emove [S]kip"
read answer
clear
if [[ $answer == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/regex-blacklist.py' | sudo python3
    echo -e "[i] The [RegEx Blacklist] filters were added to pi-hole\\n"
elif [[ $answer == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/regex-blacklist.py' | sudo python3
    echo -e "[i] The [RegEx Blacklist] filters were removed from Pi-hole\\n"
elif [[ $answer == "S" ]]; then
    clear
    echo -e "[i] Finishing up!\\n"
fi

read -t 3 -p "Press Enter to exit..."
