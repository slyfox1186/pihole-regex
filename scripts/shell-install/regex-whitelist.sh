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
echo '[1] Yes'
echo '[2] No'
read a
clear
if [ "$a" == "1" ]; then
    pihole restartdns
fi

echo -e "Done!\\n"
echo 'Make sure to star this repository and show your support!'
echo -e "Github Profile: https://github.com/slyfox1186/pihole-regex\\n"
