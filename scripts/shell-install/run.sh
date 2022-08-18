#!/bin/bash

# Make user input case insensitive
clear; shopt -s nocasematch

# Delete: The useless index.html file
if [ -f index.html ]; then
    rm index.html
fi

# Create: pihole-regex directory if not exist
if [ -d pihole-regex ]; then
    rm -R pihole-regex
fi

# Make pihole-regex directory
mkdir -p pihole-regex

# If files exist move them to the pihole-regex directory
SHELL_FILES='exact-blacklist.sh exact-whitelist.sh regex-blacklist.sh regex-whitelist.sh'
FILES=( $SHELL_FILES run.sh )
# move all the scripts in the array FILES to the pihole-regex directory
for i in ${FILES[@]}; do
    if [ -f $i ]; then
        mv -f $i pihole-regex/$i
        clear
    fi
done

# change working directory to pihole-regex
pushd pihole-regex

# execute all scripts
SUB_FILES=( $SHELL_FILES )
for i in ${SUB_FILES[@]}; do
    . "$i"
done

# return user to starting directory
popd
