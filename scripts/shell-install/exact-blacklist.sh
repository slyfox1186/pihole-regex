#!/bin/bash

clear

# Get the user's input
echo -e "Exact Blacklist Filters: [A]dd [R]emove [E]xit"
read a
clear
if [[ $a == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/exact-blacklist.py' | sudo python3
    echo '[i] The Exact Blacklist Filters have been added.'
elif [[ $a == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/exact-blacklist.py' | sudo python3
    echo '[i] The Exact Blacklist Filters have been removed.'
elif [[ $a == "E" ]]; then
    exit 0
fi

echo -e "\\n"
read -p '[i] Press enter to continue.'
clear
