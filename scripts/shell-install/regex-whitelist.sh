#!/bin/bash

# make user input case insensitive
shopt -s nocasematch

# Get user's input
clear
read -p 'RegEx Whitelist >> [A]dd [R]emove [S]kip: ' iChoice
clear
if [[ "$iChoice" == "A" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/regex-whitelist.py' | sudo python3
elif [[ "$iChoice" == "R" ]]; then
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/regex-whitelist.py' | sudo python3
fi

# remove all remaining files that were downloaded by wget
if [ -d pihole-regex ]; then rm -R pihole-regex; fi

echo -e "\\n"
echo "Restart Pihole's DNS?"
echo
echo '[Y]es'
echo '[N]o'
read uChoice
clear
if [[ "$uChoice" == "Y" ]]; then
    sudo pihole restartdns
fi

echo -e "\\nMake sure to star this repository and show your support!"
echo -e "Github Profile: https://github.com/slyfox1186/pihole-regex\\n"
