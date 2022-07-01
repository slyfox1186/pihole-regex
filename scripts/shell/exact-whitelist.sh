#!/bin/bash

clear

# Create myScripts directory if not exist.
if [ ! -d "$HOME/myScripts" ]; then
    mkdir -p "$HOME/myScripts"
    clear
fi

# Change working directory to "myScripts"
pushd "$HOME/myScripts"

# Make user input case insensitive
shopt -s nocasematch

# Get the user's input
echo -e "Install script for SlyFox1186's Exact whitelist filters\\n\\nPlease choose an option: [A]dd or [R]emove: "
read a
clear
if [[ $a == "A" ]]; then
    echo -e "Adding custom Exact whitelist filters to Pi-hole.\\n"
    sleep 3
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/install-exact-whitelist.py' | sudo python3
else
    echo -e "Removing custom Exact whitelist filters from Pi-hole.\\n"
    sleep 3
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/uninstall-exact-whitelist.py' | sudo python3
fi

# Change working directory to the user's "$HOME"
pushd "$HOME"

# Delete the temp directory "$HOME/myScripts"
if [ -d "$HOME/myScripts" ]; then
    rm -R "$HOME/myScripts"
fi

echo -e "\\nScript completed!"
