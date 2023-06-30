#!/bin/bash

clear

exit_fn()
{
    clear
    printf "%s\n\n%s\n%s\n\n" \
        'Do you want to restart pihole'\''s DNS?' \
        '[1] Yes' \
        '[2] No'
    read -p 'Your choices are (1 or 2): ' rchoice
    clear

    case "$rchoice" in
        1)
                sudo rm -fr 'pihole-regex'
                sudo pihole restartdns
                ;;
        2)      sudo rm -fr 'pihole-regex';;
        '')
                sudo rm -fr 'pihole-regex'
                sudo pihole restartdns
                ;;
        *)      
                printf "%s\n\n" 'Bad user input. Restarting script...'
                unset rchoice
                sleep 2
                clear
                exit_fn
                ;;
    esac

    printf "\n%s\n\n%s\n\n" \
        'Make sure to star this repository to show your support!' \
        'GitHub: https://github.com/slyfox1186/pihole-regex'
    exit 0
}

# GET THE USER'S INPUT
read -p 'RegEx Whitelist >> [A]dd [R]emove [S]kip: ' choice
clear

case "$choice" in
    ([Aa])      curl -sSL 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-install/regex-whitelist.py' | python3;;

    ([Rr])      curl -sSL 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/python-uninstall/regex-whitelist.py' | python3;;
    ([Ss])      exit_fn;;
    *)
                printf "%s\n\n" 'Bad user input. Restarting script...'
                unset choice
                sleep 2
                clear
                sudo bash 'pihole-regex/regex-whitelist.sh'
                ;;
esac

unset choice

echo
read -p 'Press Enter to continue: '
exit_fn
