#!/bin/bash

clear

# GET THE USER'S INPUT
read -p 'Exact Whitelist >> [A]dd [R]emove [S]kip: ' choice
clear

case "$choice" in
    ([Aa])      curl -sSL 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/exact-whitelist.py' | python3;;

    ([Rr])      curl -sSL 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/exact-whitelist.py' | python3;;
    ([Ss])      return 0;;
    *)
                printf "%s\n\n" 'Bad user input. Restarting script...'
                unset choice
                sleep 2
                clear
                sudo bash 'pihole-regex/exact-whitelist.sh'
                ;;
esac

unset choice

echo
read -p 'Press Enter to continue: '
