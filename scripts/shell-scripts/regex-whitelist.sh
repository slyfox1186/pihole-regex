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
echo -e "Install script for SlyFox1186's RegEx whitelist filters\\n\\nPlease choose an option: [A]dd or [R]emove: "
read a
if [[ $a == "A" ]]; then
    clear
    echo -e "Adding custom RegEx whitelist filters to Pi-hole.\\n"
    sleep 3
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/install-regex-whitelist.py' | sudo python3
else
    clear
    echo -e "Removing custom RegEx whitelist filters from Pi-hole.\\n"
    sleep 3
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/uninstall-regex-whitelist.py' | sudo python3
fi

# PROMPT USER SCRIPT IS COMPLETE
echo -e "Script Complete!\\n"
read -p "Press Enter to continue."

# CHANGE WORKING DIRECTORY TO THE USER'S "$HOME"
pushd "$HOME"

# DELETE THE TEMP DIRECTORY "$HOME/myScripts"
if [ -d "$HOME/myScripts" ]; then
    rm -R "$HOME/myScripts"
fi

# DELETE THE TEMP SCRIPT "$HOME/regex-whitelist.sh"
if [ -f "$HOME/regex-whitelist.sh" ]; then
    rm "$HOME/regex-whitelist.sh"
fi

# PRINT DIRECTORY LIST
ls -1A --color
