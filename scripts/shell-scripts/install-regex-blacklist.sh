#!/bin/bash

clear

# Change the working directory to user's home
cd ~

# Create ~/myScripts directory if it doesn't exist
if [ ! -d ~/myScripts ]; then
    mkdir -pv ~/myScripts
fi

# Change the working directory to the ~/myScripts directory
cd ~/myScripts

# Delete any leftover files from previous runs.
if [ -d pihole.regex ]; then
    rm -R pihole.regex
fi

# Make user input case insensitive
shopt -s nocasematch
# Get the user input
echo -e "SlyFox1186's RegEx blacklist filters\\n\\nPlease choose an option: [A]dd or [R]emove: "
read a
if [[ $a == "A" ]]; then
    clear
    echo -e "Adding custom RegEx filters to Pi-hole.\\n"
    sleep 3
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/install-regex-blacklist.py' | sudo /usr/bin/python3
elif [[ $a == "R" ]]; then
    clear
    echo -e "Removing custom RegEx filters from Pi-hole.\\n"
    sleep 3
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/uninstall-regex-blacklist.py' | sudo /usr/bin/python3
else
    echo -e "Syntax failure!\\nYou must input either the letter 'A' or 'R'\\nTry running the commands again."
    exit 1
fi
