#!/bin/bash

# Make user input case insensitive
clear; shopt -s nocasematch

# Delete the useless index.html file
if [ -e 'index.html' ]; then
    rm 'index.html'
fi

# Create: delete pihole-regex directory if exists
if [ -d 'pihole-regex' ]; then
    rm -R 'pihole-regex'
fi

# Make pihole-regex directory
mkdir -p 'pihole-regex'

# change pihole-regex directory
cd 'pihole-regex'
clear

# execute all shell scripts
FILES=( exact-blacklist.sh exact-whitelist.sh regex-blacklist.sh regex-whitelist.sh )
for i in ${FILES[@]}; do
    . $i
done
