#!/bin/bash

# Get user's input
clear
echo -e "[i] Exact Whitelist: [A]dd [R]emove [S]kip"
read answer
clear
if [[ $answer == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/exact-whitelist.py' | sudo python3
    echo -e "[i] The [Exact Whitelist] filters were added to Pi-hole\\n"
elif [[ $answer == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/exact-whitelist.py' | sudo python3
    echo -e "[i] The [Exact Whitelist] filters were removed from Pi-hole\\n"
elif [[ $answer == "S" ]]; then
    clear
    echo -e "[i] Skipping ahead!\\n"
fi

sleep 2
