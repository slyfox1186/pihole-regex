#!/bin/bash

sleep 1
clear

# Make user input case insensitive
shopt -s nocasematch

# Set directory variable
FILE_DIR="$HOME/pihole.regex"

# Delete: The useless index.html file
if [ -f index.html ]; then
    rm index.html
else
    clear
    echo 'index.html was not found'
    read -p 'Press Enter to exit.'
    exit 1
fi

# Create: $FILE_DIR directory if not exist
if [ ! -d $FILE_DIR ]; then
    mkdir -p "$FILE_DIR"
fi

# Verify: If files exist and move them to $HOME/pihole.regex
FILES1=(exact-blacklist.sh exact-whitelist.sh regex-blacklist.sh regex-whitelist.sh run.sh)

for i in ${FILES1[@]}; do
  if [ -f $i ]; then
      mv "$i" "$FILE_DIR/$i"
  else
      clear
      echo -e "\\nFailed to download: $i\\n"
      read -p 'Press enter to exit.'
      exit 1
  fi
done

echo
read -p 'Press enter to exit.'
clear

FILES2=(exact-blacklist.sh exact-whitelist.sh regex-blacklist.sh regex-whitelist.sh)

for arg in ${FILES2[@]}; do
    echo File: "$FILE_DIR/$arg"
    . "$FILE_DIR/$arg"
done
