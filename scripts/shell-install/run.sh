#!/bin/bash

clear

# Make user input case insensitive
shopt -s nocasematch

# Set directory variable
FILE_DIR="$HOME/pihole.regex"

# Delete: The useless index.html file
if [ -f index.html ]; then
    rm index.html
fi

# Create: $FILE_DIR directory if not exist
if [ -d $FILE_DIR ]; then
    rm -R "$FILE_DIR"
else
    mkdir -p "$FILE_DIR"
fi

# Verify: If files exist move them to $HOME/pihole.regex
SHELL_FILES='exact-blacklist.sh exact-whitelist.sh regex-blacklist.sh regex-whitelist.sh'
FILES=($SHELL_FILES run.sh)

for i in ${FILES[@]}; do
  if [ -f $HOME/$i ]; then
      mv -f "$HOME/$i" "$FILE_DIR/$i"
  fi
done

sleep 3
clear

SUB_FILES=($SHELL_FILES)

for i in ${SUB_FILES[@]}; do
    . "$FILE_DIR/$i"
done
