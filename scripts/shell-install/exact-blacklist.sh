#!/bin/bash

clear

# Create "$HOME/pihole.regex" directory if not exist.
if [ ! -d "$HOME/pihole.regex" ]; then
    mkdir -p "$HOME/pihole.regex"
fi

# Change working directory to "$HOME/pihole.regex"
cd "$HOME/pihole.regex"

# Make user input case insensitive
shopt -s nocasematch

# Get the user's input
# echo -e "Please choose an option: [A]dd or [R]emove [exact blacklist] filters\\n"
echo -e "[i] Exact Blacklist filters\\n\\nChoose an option: [A]dd , [R]emove or [E]xit"
read a
clear
if [[ $a == "A" ]]; then
    /usr/bin/curl -sSl "https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/exact-blacklist.py" | sudo python3
    echo '[i] The Exact Blacklist filters have been added.'
elif [[ $a == "R" ]]; then
    /usr/bin/curl -sSl "https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/exact-blacklist.py" | sudo python3
    echo '[i] The Exact Blacklist filters have been removed.'
elif [[ $a == "E" ]]; then
    read -p "exit"
    exit 1
fi

echo -e "\\n\\n"
read -p 'Press Enter to continue.'
clear
