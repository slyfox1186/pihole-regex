#!/bin/bash

# Create variable
URL=https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts

# Create "$HOME/tmp" directory if not exist.
if [ ! -d "$HOME/tmp" ]; then
    mkdir -p "$HOME/tmp"
fi

# Change working directory to "$HOME/tmp"
cd "$HOME/tmp"

# Make user input case insensitive
shopt -s nocasematch; clear

# Get the user's input
echo -e "SlyFox1186's exact whitelist filters\\n\\nPlease choose an option: [A]dd or [R]emove: "
read a
clear
if [[ $a == "A" ]]; then
    /usr/bin/curl -sSl "$URL/python-install/exact-whitelist.py" | sudo python3
    echo 'Script complete: The exact whitelist filters have been added.'
else
    /usr/bin/curl -sSl "$URL/python-uninstall/exact-whitelist.py" | sudo python3
    echo 'Script complete: The exact whitelist filters have been removed.'
fi
