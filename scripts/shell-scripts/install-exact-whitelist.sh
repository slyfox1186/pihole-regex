#!/bin/bash

clear

# Create $HOME/myScripts directory if it doesn't exist
if [ ! -d $HOME/myScripts ]; then
    mkdir -pv $HOME/myScripts
fi

# Change the working directory to $HOME/myScripts
cd $HOME/myScripts

# Delete any leftover files from previous runs.
if [ -d pihole.regex ]; then
    rm -R pihole.regex
fi

# Make user input case insensitive
shopt -s nocasematch

# Get the user's input
echo -e "SlyFox1186's shell script for adding or removing the exact whitelist repository domains for Pi-hole.\\n\\n"
echo "Choose an option: [A]dd or [R]emove the repository whitelist.txt: "
read a
if [[ $a == "A" ]]; then
    clear
    echo -e "Adding exact whitelist domains to Pi-hole.\\n"
    sleep 3
    git clone 'https://github.com/slyfox1186/pihole.regex.git'
    python3 'pihole.regex/scripts/install-exact-whitelist.py'
    echo -e "\\nScript complete!\\nReload your Pi-hole's web interface to see the changes."
elif [[ $a == "R" ]]; then
    clear
    echo -e "Removing the exact whitelist domains from Pi-hole.\\n"
    sleep 3
    git clone 'https://github.com/slyfox1186/pihole.regex.git'
    python3 'pihole.regex/scripts/uninstall-exact-whitelist.py'
    echo -e "\\nScript complete!\\nReload your Pi-hole's web interface to see the changes."
else
    echo -e "Syntax failure!\\nYou must input either the letter 'A' or 'R'\\nTry running the commands again."
    exit 1
fi
