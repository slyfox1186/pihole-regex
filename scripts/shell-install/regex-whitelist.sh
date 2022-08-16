#!/bin/bash

# Get user's input
clear
echo -e "[i] RegEx Whitelist Filters: [A]dd [R]emove [S]kip"
read answer
clear
if [[ $answer == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/regex-whitelist.py' | sudo python3
    echo -e "[i] The RegEx Whitelist Filters were added to pi-hole.\\n"
elif [[ $answer == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/regex-whitelist.py' | sudo python3
    echo -e "[i] The RegEx Whitelist Filters were removed from pi-hole.\\n"
elif [[ $answer == "S" ]]; then
    clear
    echo -e "[i] Finishing up!\\n"
fi

sleep 3
