#!/bin/bash

# Get user's input
clear
echo -e "[i] RegEx Whitelist: [A]dd [R]emove [S]kip"
read answer
clear
if [[ $answer == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/regex-whitelist.py' | sudo python3
    echo -e "\\n[i] The RegEx Whitelist filters were added to Pi-hole\\n"
elif [[ $answer == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/regex-whitelist.py' | sudo python3
    echo -e "\\n[i] The RegEx Whitelist filters were removed from Pi-hole\\n"
elif [[ $answer == "S" ]]; then
    clear
    echo -e "[i] Finishing up!\\n"
    sleep 3
    exit 0
fi

read -t 30 -p 'Press Enter to continue...'
