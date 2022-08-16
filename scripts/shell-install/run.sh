#!/bin/bash

clear

# Make user input case insensitive
shopt -s nocasematch

# Set directory variable
FILE_DIR="/root/pihole.regex"
pushd $FILE_DIR; clear

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

# If files exist move them to /root/pihole.regex
SHELL_FILES='exact-blacklist.sh exact-whitelist.sh regex-blacklist.sh regex-whitelist.sh'
FILES=( $SHELL_FILES run.sh )
# move all the scripts in the array FILES to /root/pihole.regex
for i in ${FILES[@]}; do
  if [ -f $i ]; then
      mv -f "$i" "$FILE_DIR/$i"
      clear
  fi
done

# execute all scripts in array
SUB_FILES=( $SHELL_FILES )
for i in ${SUB_FILES[@]}; do
    . "$FILE_DIR/$i"
done

popd
