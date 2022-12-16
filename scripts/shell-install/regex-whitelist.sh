#!/bin/bash

# make user input case insensitive
shopt -s nocasematch

# Get user's input
clear
read -p 'RegEx Whitelist >> [A]dd [R]emove [S]kip: ' iChoice
clear
if [[ "${iChoice}" == "A" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/regex-whitelist.py' | sudo python3
elif [[ "${iChoice}" == "R" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/regex-whitelist.py' | sudo python3
elif [[ "${iChoice}" == "S" ]]; then
    clear
fi

# remove all remaining files that were downloaded by wget
if [ -d 'pihole-regex' ]; then rm -R 'pihole-regex'; fi

echo -e "\\n"
read -p 'Press enter to continue.'
clear

echo -e "Restart Pihole's DNS?\\n"
read -p '[Y]es or [N]o' uChoice
clear
if [[ "${uChoice}" == "Y" ]]; then pihole restartdns; fi

echo -e "\\nMake sure to star this repository and show your support!"
echo -e "GitHub Repo:  https://github.com/slyfox1186/pihole-regex\\n"
