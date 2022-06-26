#!/bin/bash

clear

# Get user input
read -p "Make a choice: [I]nstall or [U]ninstall RegEx filters: " myChoice

# Make user input case insensitive
shopt -s nocasematch
if [ "$myChoice" == "I" ]; then
    echo -e "Adding RegEx to Pi-hole.\\n"
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/install-regex-blacklist.py' | /usr/bin/python3
elif [ "$myChoice" == "U" ]; then
    echo -e "Removing RegEx from Pi-hole.\\n"
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/uninstall-regex-blacklist.py' | /usr/bin/python3
else
    echo 'Syntax failure'
    exit 1
fi
