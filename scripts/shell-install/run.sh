#!/bin/bash

sleep 1
clear

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

# Verify: exact-whitelist.sh exists / was downloaded
if [ ! -f $FILE_DIR/exact-whitelist.sh ]; then
  if [ ! -f exact-whitelist.sh ]; then
    echo -e "\\nFile missing: exact-whitelist.sh\\nIt might not have been downloaded so check."
    read -p 'Press [Enter] to exit.'
    exit 1
  else
    mv 'exact-whitelist.sh' "$FILE_DIR/exact-whitelist.sh"
    clear
  fi
fi

# Verify: regex-blacklist.sh exists / was downloaded
if [ ! -f $FILE_DIR/regex-blacklist.sh ]; then
  if [ ! -f regex-blacklist.sh ]; then
    echo -e "\\nFile missing: regex-blacklist.sh\\nIt might not have been downloaded so check."
    read -p 'Press [Enter] to exit.'
    exit 1
  else
    mv 'regex-blacklist.sh' "$FILE_DIR/regex-blacklist.sh"
    clear
  fi
fi

# Verify: regex-whitelist.sh exists / was downloaded
if [ ! -f $FILE_DIR/regex-whitelist.sh ]; then
  if [ ! -f regex-whitelist.sh ]; then
    echo -e "\\nFile missing: regex-whitelist.sh\\nIt might not have been downloaded so check."
    read -p 'Press [Enter] to exit.'
    exit 1
  else
    mv 'regex-whitelist.sh' "$FILE_DIR/regex-whitelist.sh"
    clear
  fi
fi

# Verify: run.sh exists / was downloaded
if [ ! -f $FILE_DIR/run.sh ]; then
  if [ ! -f run.sh ]; then
    echo -e "\\nFile missing: run.sh\\nIt might not have been downloaded so check."
    read -p 'Press [Enter] to exit.'
    exit 1
  else
    mv 'run.sh' "$FILE_DIR/run.sh"
    clear
  fi
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
