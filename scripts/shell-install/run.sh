#!/bin/bash

# delete the useless index.html file that is downloaded
if [ -f index.html ]; then rm index.html; fi

# Delete & create pihole-regex directory if not exist
if [ -d pihole-regex ]; then rm -R pihole-regex; fi

# make pihole-regex directory
mkdir -p pihole-regex

SHELL_FILES='exact-blacklist.sh exact-whitelist.sh regex-blacklist.sh regex-whitelist.sh'
FILES=( $SHELL_FILES run.sh )
# if the shell scripts exist, move them to the pihole-regex dir
for i in ${FILES[@]}; do
    if [ -f $i ]; then
        mv -f $i pihole-regex/$i
    fi
done

# execute all scripts in pihole-regex
SUB_FILES=( $SHELL_FILES )
for i in ${SUB_FILES[@]}; do
    . pihole-regex/$i
done
