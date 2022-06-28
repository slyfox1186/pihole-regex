#!/bin/bash

clear

# Change to user's home directory
cd $HOME

# Create $HOME/myScripts directory if not exist
if [ ! -d $HOME/myScripts ]; then
    mkdir -pv $HOME/myScripts
fi

# Change to $HOME/myScripts directory
cd $HOME/myScripts

# Make user input case insensitive
shopt -s nocasematch

# Get user input
echo "Please choose an option: [A]dd or [R]emove the custom RegEx blacklist filters: "
read myChoice
if [ "$myChoice" == "A" ]; then
    echo -e "Adding the custom RegEx filters to Pi-hole.\\n"
    sleep 3
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/install-regex-blacklist.py' | sudo /usr/bin/python3
elif [ "$myChoice" == "R" ]; then
    echo -e "Removing the custom RegEx filters from Pi-hole.\\n"
    sleep 3
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/uninstall-regex-blacklist.py' | sudo /usr/bin/python3
else
    echo -e "Syntax failure!\\nYou must input either the letter 'A' or 'R'\\nTry running the commands again."
    exit 1
fi
