#!/bin/bash

# Create "$HOME/tmp" directory if not exist.
if [ ! -d "$HOME/tmp" ]; then
    mkdir -p "$HOME/tmp"
fi

# Change working directory to "$HOME/tmp"
cd "$HOME/tmp"

# Make user input case insensitive
shopt -s nocasematch

# Get the user's input
echo -e "SlyFox1186's RegEx Blacklist Filters\\n\\nPlease choose an option: [A]dd or [R]emove: "
read a
clear
if [[ $a == "A" ]]; then
    echo -e "Adding custom RegEx blacklist filters to Pi-hole.\\n"
    sleep 3
    /usr/bin/curl -sSl https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/regex-blacklist.py | sudo python3
else
    echo -e "Removing custom RegEx blacklist filters from Pi-hole.\\n"
    sleep 3
    /usr/bin/curl -sSl https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/regex-blacklist.py | sudo python3
fi

echo -e "\\nScript complete!\\n"
