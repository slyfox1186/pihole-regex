#!/bin/bash

clear

# GET THE USER'S INPUT
read -p 'RegEx Blacklist >> [A]dd [R]emove [S]kip: ' choice
clear

case "$choice" in
    ([Aa])      curl -sSL 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/regex-blacklist.py' | python3;;

    ([Rr])      curl -sSL 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/regex-blacklist.py' | python3;;
    ([Ss])      return 0;;
    *)
                printf "%s\n\n" 'Bad user input. Restarting script...'
                unset choice
                sleep 2
                clear
                sudo bash 'pihole-regex/regex-blacklist.sh'
                ;;
esac

unset choice

echo
read -p 'Press Enter to continue: '
