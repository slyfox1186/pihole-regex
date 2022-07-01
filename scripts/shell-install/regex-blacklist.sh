#!/bin/bash

# Create tmp directory if not exist.
if [ ! -d "$HOME/tmp" ]; then
    mkdir -p "$HOME/tmp"
fi

# Change working directory to "$HOME/tmp"
pushd "$HOME/tmp"

# Make user input case insensitive
shopt -s nocasematch
clear

# Get the user's input
echo -e "Install script for SlyFox1186's RegEx blacklist filters\\n\\nPlease choose an option: [A]dd or [R]emove: "
read a
clear
if [[ $a == "A" ]]; then
    echo -e "Adding custom RegEx filters to Pi-hole.\\n"
    sleep 3
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/regex-blacklist.py' | sudo python3
elif [[ $a == "R" ]]; then
    echo -e "Removing custom RegEx filters from Pi-hole.\\n"
    sleep 3
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/regex-blacklist.py' | sudo python3
else
    echo -e "Syntax failure!\\nYou must input either the letter 'A' or 'R'\\nTry running the commands again."
fi

echo -e "\\nScript completed!"
