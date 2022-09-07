#!/bin/bash

# make user input case insensitive
shopt -s nocasematch

# Get user's input
clear
echo 'RegEx Whitelist: [A]dd [R]emove [S]kip'
read i
clear
if [[ "$i" == "A" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/regex-whitelist.py' | sudo python3
elif [[ "$i" == "R" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/regex-whitelist.py' | sudo python3
elif [[ "$i" == "S" ]]; then
     clear
fi

clear
echo -e "Restart Pihole's DNS?\\n"
read -p '[Y]es or [N]o' a
clear
if [[ "$a" == "Y" ]]; then
    pihole restartdns
fi

echo -e "\\nMake sure to star this repository and show your support!"
echo -e "Github Profile: https://github.com/slyfox1186/pihole-regex\\n"
