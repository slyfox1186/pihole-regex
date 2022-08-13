#!/bin/bash

clear

# Delete the arbitrary index.html file
if [ -f index.html ]; then
    rm index.html
    clear
fi

# Create "$HOME/pihole.regex" directory if not exist.
if [ ! -d "$HOME/pihole.regex" ]; then
    mkdir -p "$HOME/pihole.regex"
fi

# Change working directory to "$HOME/pihole.regex"
cd "$HOME/pihole.regex"

# Make user input case insensitive
shopt -s nocasematch

# Get the user's input
echo -e "\\nExact Blacklist Filters: [A]dd [R]emove [E]xit"
read a
clear
if [[ $a == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/exact-blacklist.py' | sudo python3
    echo '[i] The Exact Blacklist Filters have been added.'
elif [[ $a == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/exact-blacklist.py' | sudo python3
    echo '[i] The Exact Blacklist Filters have been removed.'
elif [[ $a == "E" ]]; then
    exit 1
fi

echo -e "\\n"
read -p '[i] Press enter to continue.'
clear
