#!/bin/bash

clear

# Create myScripts directory if not exist.
if [ ! -d "$HOME/myScripts" ]; then
    mkdir -p "$HOME/myScripts"
    clear
fi

# Change working directory to "$HOME/myScripts"
pushd "$HOME/myScripts"

# Make user input case insensitive
shopt -s nocasematch

# Get the user's input
echo -e "Install script for SlyFox1186's RegEx blacklist filters\\n\\nPlease choose an option: [A]dd or [R]emove: "
read a
clear
if [[ $a == "A" ]]; then
    echo -e "Adding custom RegEx filters to Pi-hole.\\n"
    sleep 3
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/install-regex-blacklist.py' | sudo python3
elif [[ $a == "R" ]]; then
    echo -e "Removing custom RegEx filters from Pi-hole.\\n"
    sleep 3
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/uninstall-regex-blacklist.py' | sudo python3
else
    echo -e "Syntax failure!\\nYou must input either the letter 'A' or 'R'\\nTry running the commands again."
fi

# CHANGE WORKING DIRECTORY TO THE USER'S "$HOME"
pushd "$HOME"

# DELETE THE TEMP DIRECTORY "$HOME/myScripts"
if [ -d "$HOME/myScripts" ]; then
    rm -R "$HOME/myScripts"
fi

echo -e "\\nScript completed!"
