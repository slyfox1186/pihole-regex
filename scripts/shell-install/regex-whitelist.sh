#!/bin/bash

# Create "$HOME/tmp" directory if not exist.
if [ ! -d "$HOME/tmp" ]; then
    mkdir -p "$HOME/tmp"
fi

# Change working directory to "$HOME/tmp"
pushd "$HOME/tmp"

# Make user input case insensitive
shopt -s nocasematch; clear

# Get the user's input
echo -e "SlyFox1186's RegEx whitelist filters\\n\\nPlease choose an option: [A]dd or [R]emove: "
read a
clear
if [[ $a == "A" ]]; then
    echo -e "Adding custom RegEx whitelist filters to Pi-hole.\\n"
    sleep 3
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/regex-whitelist.py' | sudo python3
else
    echo -e "Removing custom RegEx whitelist filters from Pi-hole.\\n"
    sleep 3
    curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/regex-whitelist.py' | sudo python3
fi

echo -e "Script complete!\\n"
