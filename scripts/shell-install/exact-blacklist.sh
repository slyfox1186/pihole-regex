#!/usr/bin/env bash

user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

user_prompt_fn()
{
    local choice
    clear

    read -p 'Exact Blacklist >> [A]dd [R]emove [S]kip: ' choice
    clear
    
    case "$choice" in
        ([Aa])      curl -A "${user_agent}" -sSL 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/exact-blacklist.py' | python3;;
    
        ([Rr])      curl -A "${user_agent}" -sSL 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/exact-blacklist.py' | python3;;
        ([Ss])      return 0;;
        *)
                    unset choice
                    clear
                    user_prompt_fn
                    ;;
    esac
}
user_prompt_fn

echo
read -p 'Press Enter to continue: '
