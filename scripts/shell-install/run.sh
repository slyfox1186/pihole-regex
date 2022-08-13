#!/bin/bash

sleep 1
clear

FILE_DIR="$HOME/pihole.regex"

# Delete the useless index.html file that is downloaded
if [ -f index.html ]; then
    rm index.html
    clear
fi

# Create $FILE_DIR directory if not exist
if [ ! -d $FILE_DIR ]; then
    mkdir -p "$FILE_DIR"
fi

# Move scripts to to $FILE_DIR
if [ -f exact-blacklist.sh ]; then
    mv 'exact-blacklist.sh' "$FILE_DIR/exact-blacklist.sh"
    clear
fi

if [ -f exact-whitelist.sh ]; then
    mv 'exact-whitelist.sh' "$FILE_DIR/exact-whitelist.sh"
    clear
fi

if [ -f regex-blacklist.sh ]; then
    mv 'regex-blacklist.sh' "$FILE_DIR/regex-blacklist.sh"
    clear
fi

if [ -f regex-whitelist.sh ]; then
    mv 'regex-whitelist.sh' "$FILE_DIR/regex-whitelist.sh"
    clear
fi

if [ -f $FILE_DIR/exact-blacklist.sh ] 

# Change working directory to "$HOME/pihole.regex"
cd "$HOME/pihole.regex"

# Make user input case insensitive
shopt -s nocasematch

# Source each script one at a time
. exact-blacklist.sh && \
. exact-whitelist.sh && \
. regex-blacklist.sh && \
. regex-whitelist.sh
