#!/bin/bash

clear

FILE_DIR="$HOME/pihole.RegEx"

# Make user input case insensitive
shopt -s nocasematch

# Create "$FILE_DIR" directory if not exist.
if [ ! -d $FILE_DIR ]; then
    mkdir -p "$FILE_DIR"
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

# Change working directory to "$FILE_DIR"
cd "$FILE_DIR"

# Get the user's input
echo -e "\\nRegEx Whitelist Filters: [A]dd [R]emove [S]kip"
read a
clear
if [[ $a == "A" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-install/regex-Whitelist.py' | sudo python3
    echo '[i] The RegEx Whitelist Filters have been added.'
elif [[ $a == "R" ]]; then
    /usr/bin/curl -sSl 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/scripts/python-uninstall/regex-Whitelist.py' | sudo python3
    echo '[i] The RegEx Whitelist Filters were removed.'
elif [[ $a == "S" ]]; then
    clear
    echo 'Skipping ahead!'
fi

echo -e "\\n"
read -p '[i] Press enter to continue.'
clear
