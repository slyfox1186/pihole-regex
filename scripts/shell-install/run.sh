#!/bin/bash

sleep 1
clear

FILE_DIR="$HOME/pihole.regex"

# Delete: The useless index.html file
if [ -f index.html ]; then
    rm index.html
    clear
fi

# Create: $FILE_DIR directory if not exist
if [ ! -d $FILE_DIR ]; then
    mkdir -p "$FILE_DIR"
fi

## Verify: Files exist and then move them to $HOME/pihole.regex
# Verify: exact-blacklist.sh
if [ -f exact-blacklist.sh ]; then
    mv 'exact-blacklist.sh' "$FILE_DIR/exact-blacklist.sh"
    clear
else
    clear
    echo -e "\\nFailed to download: exact-blacklist.sh\\n"
    read -p 'Press enter to exit.'
    exit 1
fi

# Verify: exact-whitelist.sh
if [ -f exact-whitelist.sh ]; then
    mv 'exact-whitelist.sh' "$FILE_DIR/exact-whitelist.sh"
    clear
else
    clear
    echo -e "\\nFailed to download: exact-whitelist.sh\\n"
    read -p 'Press enter to exit.'
    exit 1
fi

# Verify: regex-blacklist.sh
if [ -f regex-blacklist.sh ]; then
    mv 'regex-blacklist.sh' "$FILE_DIR/regex-blacklist.sh"
    clear
else
    clear
    echo -e "\\nFailed to download: regex-blacklist.sh\\n"
    read -p 'Press enter to exit.'
    exit 1
fi

# Verify: regex-whitelist.sh
if [ -f regex-whitelist.sh ]; then
    mv 'regex-whitelist.sh' "$FILE_DIR/regex-whitelist.sh"
    clear
else
    clear
    echo -e "\\nFailed to download: regex-whitelist.sh\\n"
    read -p 'Press enter to exit.'
    exit 1
fi

# Verify: run.sh
if [ -f run.sh ]; then
    mv 'run.sh' "$FILE_DIR/run.sh"
    clear
else
    clear
    echo -e "\\nFailed to download: run.sh\\n"
    read -p 'Press enter to exit.'
    exit 1
fi

# Change working directory to "$HOME/pihole.regex"
cd "$HOME/pihole.regex"

# Make user input case insensitive
shopt -s nocasematch

# Source each script one at a time
. exact-blacklist.sh && \
. exact-whitelist.sh && \
. regex-blacklist.sh && \
. regex-whitelist.sh
