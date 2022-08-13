#!/bin/bash

clear

FILE_DIR="$HOME/pihole.RegEx"

# Change working directory to "$FILE_DIR"
cd "$FILE_DIR"

# Get the user's input
echo -e "\\nRegEx Whitelist Filters: [A]dd [R]emove [S]kip"
read a
clear
if [[ $a == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/regex-whitelist.py' | sudo python3
    echo -e "[i] The RegEx Whitelist Filters were added to pi-hole.\\n"
elif [[ $a == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/regex-whitelist.py' | sudo python3
    echo -e "[i] The RegEx Whitelist Filters were removed from pi-hole.\\n"
elif [[ $a == "S" ]]; then
    clear
    echo -e "Skipping ahead!\\n"
fi

read -p '[i] Press enter to continue.'
clear
