#!/bin/bash

clear

# GET THE USER'S INPUT
read -p 'Exact Blacklist >> [A]dd [R]emove [S]kip: ' choice
clear

case "$choice" in
    ([Aa])      curl -sSL 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/exact-blacklist.py' | python3;;

    ([Rr])      curl -sSL 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/exact-blacklist.py' | python3;;
    ([Ss])      return 0;;
    *)
                printf "%s\n\n" 'Bad user input. Restarting script...'
                unset choice
                sleep 2
                clear
                sudo bash "$0"
                ;;
esac

unset choice

echo
read -p 'Press Enter to continue: '
