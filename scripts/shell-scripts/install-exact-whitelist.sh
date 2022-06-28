#!/bin/bash

clear

# Create ~/myScripts directory if not exist
if [ ! -d ~/myScripts ]; then
    mkdir -pv ~/myScripts
fi

# Change to ~/myScripts directory
cd ~/myScripts

# Delete any leftover files from previous runs.
if [ -d pihole.regex ]; then
    rm -R pihole.regex
fi

# Download files and execute shell script
git clone 'https://github.com/slyfox1186/pihole.regex.git'
source 'pihole.regex/scripts/shell-scripts/install-exact-whitelist.sh'
