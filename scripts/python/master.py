#!/usr/bin/env python3

import requests
import sqlite3
import os
import time
from contextlib import contextmanager
from colorama import init, Fore, Style

init()

PIHOLE_DB_PATH = '/etc/pihole/gravity.db'
RETRY_COUNT = 5
RETRY_DELAY = 2

URLS = {
    0: 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-whitelist.sql',
    1: 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-blacklist.sql',
    2: 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/regex-whitelist.sql',
    3: 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/regex-blacklist.sql'
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_domains_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return [line.strip() for line in response.text.strip().split('\n') if line.strip() and not line.startswith('#')]
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Failed to download domains from {url}: {e}{Style.RESET_ALL}")
        return []

@contextmanager
def db_connection():
    conn = None
    try:
        conn = sqlite3.connect(PIHOLE_DB_PATH, timeout=20)
        yield conn
    finally:
        if conn:
            conn.close()

def domain_exists(cursor, domain, domain_type):
    cursor.execute("SELECT EXISTS(SELECT 1 FROM domainlist WHERE domain = ? AND type = ? LIMIT 1)", (domain, domain_type))
    return cursor.fetchone()[0]

def add_or_remove_domains(domains, domain_type, add=True):
    added_count = removed_count = skipped_count = attempts = 0
    changes_made = False

    while attempts < RETRY_COUNT:
        try:
            with db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("BEGIN TRANSACTION;")

                for domain in domains:
                    parts = domain.split(' -- ')
                    domain_name = parts[0].strip()
                    comment = ('SlyEWL - ' if domain_type == 0 else 'SlyEBL - ' if domain_type == 1 else 'SlyRWL - ' if domain_type == 2 else 'SlyRBL - ') + parts[1].strip() if len(parts) > 1 else ''

                    if add:
                        if not domain_exists(cursor, domain_name, domain_type):
                            cursor.execute("INSERT INTO domainlist (type, domain, enabled, comment) VALUES (?, ?, 1, ?)", (domain_type, domain_name, comment))
                            print(f"{Fore.GREEN}Added: {domain_name}{Style.RESET_ALL}")
                            added_count += 1
                            changes_made = True
                        else:
                            print(f"{Fore.YELLOW}Skipped (already exists): {domain_name}{Style.RESET_ALL}")
                            skipped_count += 1
                    else:
                        if domain_exists(cursor, domain_name, domain_type):
                            cursor.execute("DELETE FROM domainlist WHERE type = ? AND domain = ?", (domain_type, domain_name))
                            print(f"{Fore.RED}Removed: {domain_name}{Style.RESET_ALL}")
                            removed_count += 1
                            changes_made = True
                        else:
                            print(f"{Fore.YELLOW}Skipped (not found): {domain_name}{Style.RESET_ALL}")
                            skipped_count += 1

                conn.commit()
                break
        except sqlite3.OperationalError as e:
            if str(e) == "database is locked":
                attempts += 1
                print(f"{Fore.MAGENTA}Database is locked, retrying in {RETRY_DELAY} seconds... (Attempt {attempts}/{RETRY_COUNT}){Style.RESET_ALL}")
                time.sleep(RETRY_DELAY)
            else:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                break
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            break

    if attempts == RETRY_COUNT:
        print(f"{Fore.RED}Failed to update the database after several retries.{Style.RESET_ALL}")

    return added_count, removed_count, skipped_count, changes_made

def add_domain(domain_type):
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            domain = input("Enter the domain to add: ")
            cursor.execute("INSERT INTO domainlist (type, domain, enabled) VALUES (?, ?, 1)", (domain_type, domain))
            conn.commit()
            print(f"{Fore.GREEN}Domain {domain} added successfully.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    if input("Restart Pi-hole DNS resolver? (yes/no): ").strip().lower() == 'yes':
        os.system('pihole restartdns')

def remove_domain(domain_type):
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            domain = input("Enter the domain to remove: ")
            cursor.execute("DELETE FROM domainlist WHERE type = ? AND domain = ?", (domain_type, domain))
            conn.commit()
            print(f"{Fore.RED}Domain {domain} removed successfully.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    if input("Restart Pi-hole DNS resolver? (yes/no): ").strip().lower() == 'yes':
        os.system('pihole restartdns')

def list_domains(domain_type):
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT domain FROM domainlist WHERE type = ?", (domain_type,))
            domains = cursor.fetchall()
            if domains:
                print(f"{Fore.CYAN}Current domains found in the database:{Style.RESET_ALL}")
                for domain in domains:
                    print(f"{Fore.CYAN}{domain[0]}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}No domains found in the database.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

def clear_domains(domain_type):
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM domainlist WHERE type = ?", (domain_type,))
            conn.commit()
            print(f"{Fore.RED}All domains cleared.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

def restart_pihole_dns():
    restart_option = input(f"{Fore.MAGENTA}Restart Pi-hole DNS resolver? (yes/no): {Style.RESET_ALL}").strip().lower()
    if restart_option == 'yes':
        os.system('pihole restartdns')
        print()

def main():
    clear_screen()

    print(f"{Fore.CYAN}Options: add, remove, list{Style.RESET_ALL}")
    action = input(f"{Fore.MAGENTA}Choose an action: {Style.RESET_ALL}").strip().lower()
    clear_screen()

    changes_made = False
    added_total = removed_total = skipped_total = 0

    if action == 'add':
        print(f"{Fore.CYAN}Add domains{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}0: Exact Whitelist\n1: Exact Blacklist\n2: Regex Whitelist\n3: Regex Blacklist\n4: All{Style.RESET_ALL}")
        domain_type = int(input(f"{Fore.MAGENTA}Choose an option: {Style.RESET_ALL}"))
        clear_screen()
        if domain_type not in URLS and domain_type != 4:
            print(f"{Fore.RED}Invalid domain type. Exiting.{Style.RESET_ALL}")
            return

        if domain_type == 4:
            for type_num in URLS:
                domains = get_domains_from_url(URLS[type_num])
                if domains:
                    added, removed, skipped, changes = add_or_remove_domains(domains, type_num, add=True)
                    added_total += added
                    removed_total += removed
                    skipped_total += skipped
                    changes_made |= changes
        else:
            domains = get_domains_from_url(URLS[domain_type])
            if not domains:
                print(f"{Fore.YELLOW}No domains to process. Exiting.{Style.RESET_ALL}")
                return
            added_total, removed_total, skipped_total, changes_made = add_or_remove_domains(domains, domain_type, add=True)
    elif action == 'remove':
        print(f"{Fore.CYAN}Remove domains{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}0: Exact Whitelist\n1: Exact Blacklist\n2: Regex Whitelist\n3: Regex Blacklist\n4: All{Style.RESET_ALL}")
        remove_option = int(input(f"{Fore.MAGENTA}Choose an option: {Style.RESET_ALL}"))
        clear_screen()
        if remove_option == 4:
            for type_num in URLS:
                domains = get_domains_from_url(URLS[type_num])
                if domains:
                    added, removed, skipped, changes = add_or_remove_domains(domains, type_num, add=False)
                    added_total += added
                    removed_total += removed
                    skipped_total += skipped
                    changes_made |= changes
        elif remove_option in URLS:
            domains = get_domains_from_url(URLS[remove_option])
            if not domains:
                print(f"{Fore.YELLOW}No domains to process. Exiting.{Style.RESET_ALL}")
                return
            added_total, removed_total, skipped_total, changes_made = add_or_remove_domains(domains, remove_option, add=False)
        else:
            print(f"{Fore.RED}Invalid option. Exiting.{Style.RESET_ALL}")
            return
    elif action == 'list':
        print(f"{Fore.CYAN}List domains{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}0: Exact Whitelist\n1: Exact Blacklist\n2: Regex Whitelist\n3: Regex Blacklist\n4: All{Style.RESET_ALL}")
        domain_type = int(input(f"{Fore.MAGENTA}Choose an option: {Style.RESET_ALL}"))
        clear_screen()
        if domain_type not in URLS and domain_type != 4:
            print(f"{Fore.RED}Invalid domain type. Exiting.{Style.RESET_ALL}")
            return
        if domain_type == 4:
            for type_num in URLS:
                list_domains(type_num)
        else:
            list_domains(domain_type)
    else:
        print(f"{Fore.RED}Invalid action. Exiting.{Style.RESET_ALL}")
        return

    print()
    print(f"{Fore.CYAN}Summary:{Style.RESET_ALL}")
    print(f"Total Domains Added: {Fore.GREEN}{added_total}{Style.RESET_ALL}")
    print(f"Total Domains Removed: {Fore.RED}{removed_total}{Style.RESET_ALL}")
    print(f"Total Domains Skipped: {Fore.YELLOW}{skipped_total}{Style.RESET_ALL}")

    print()
    if changes_made:
        restart_pihole_dns()

    print(f"{Fore.CYAN}Make sure to star this repository to show your support!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}https://github.com/slyfox1186/pihole-regex{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
