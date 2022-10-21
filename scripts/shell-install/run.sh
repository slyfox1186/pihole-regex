#!/bin/bash

clear

# Delete any useless files that get downloaded.
if [ -f index.html ] || [ -f urls.txt ]; then rm index.html urls.txt; fi

# Delete the pihole-regex folder if it already exists.
if [ -d pihole-regex ]; then rm -R pihole-regex; fi

# Create the pihole-regex folder to store the downloaded files in.
mkdir -p pihole-regex

FILES='exact-blacklist.sh exact-whitelist.sh regex-blacklist.sh regex-whitelist.sh'
ADD_FILE=( $FILES run.sh )
# If the shell scripts exist, move them to the pihole-regex dir
for i in ${ADD_FILE[@]}; do
    if [ -f "$i" ]; then mv -f $i pihole-regex; fi
done

# execute all scripts in pihole-regex
for i in ${FILES[@]}; do
    source pihole-regex/$i
done
