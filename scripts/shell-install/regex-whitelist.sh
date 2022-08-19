#!/bin/bash

# Get user's input
clear
echo 'RegEx Whitelist: [A]dd [R]emove [S]kip'
read answer
clear
if [[ $answer == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/regex-whitelist.py' | sudo python3
elif [[ $answer == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/regex-whitelist.py' | sudo python3
elif [[ $answer == "S" ]]; then
    clear
    echo -e "Done!\\n"
    echo -e "Make sure to star this repository and show your support!"
    echo -e "https://github.com/slyfox1186/pihole-regex\\n"
    read -t 30 -p "Press [Enter] to exit the shell."
    exit 0
fi
