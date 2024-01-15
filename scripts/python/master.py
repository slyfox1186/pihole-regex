#!/usr/bin/env python3

import requests
import sqlite3
import sys
import os
import time

# Clear the terminal screen
def clear_screen():
    if os.name == 'nt':  # for Windows
        os.system('cls')
    else:  # for Linux and macOS
        os.system('clear')

# Pi-hole database location and other constants
pihole_db_path = '/etc/pihole/gravity.db'
retry_count = 5  # Number of retries
retry_delay = 2  # Delay in seconds between retries

# URLs of SQL files for each domain type
urls = {
    0: 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-whitelist.sql',
    1: 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-blacklist.sql',
    2: 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/regex-whitelist.sql',
    3: 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/regex-blacklist.sql'
}

def get_domains_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip().split('\n')
    else:
        print(f"Failed to download domains from {url}")
        return []

def domain_exists(cursor, domain, domain_type):
    cursor.execute("SELECT EXISTS(SELECT 1 FROM domainlist WHERE domain = ? AND type = ? LIMIT 1)", (domain, domain_type))
    return cursor.fetchone()[0]

def add_or_remove_domains(domains, domain_type, add=True):
    added_count = 0
    removed_count = 0
    skipped_count = 0
    attempts = 0
    changes_made = False

    while attempts < retry_count:
        try:
            conn = sqlite3.connect(pihole_db_path, timeout=20)  # Increased timeout
            cursor = conn.cursor()

            # Start transaction
            cursor.execute("BEGIN TRANSACTION;")

            for domain in domains:
                parts = domain.split(' -- ')
                domain_name = parts[0].strip()

                if add:
                    if not domain_exists(cursor, domain_name, domain_type):
                        comment = ''
                        if domain_type == 0:  # Exact Whitelist
                            comment = 'SlyEWL - ' + parts[1].strip() if len(parts) > 1 else ''
                        elif domain_type == 1:  # Exact Blacklist
                            comment = 'SlyEBL - ' + parts[1].strip() if len(parts) > 1 else ''
                        elif domain_type == 2:  # Regex Whitelist
                            comment = 'SlyRWL - ' + parts[1].strip() if len(parts) > 1 else ''
                        elif domain_type == 3:  # Regex Blacklist
                            comment = 'SlyRBL - ' + parts[1].strip() if len(parts) > 1 else ''
                        cursor.execute("INSERT INTO domainlist (type, domain, enabled, comment) VALUES (?, ?, 1, ?)", (domain_type, domain_name, comment))
                        print(f"Added: {domain_name}")
                        added_count += 1
                        changes_made = True
                    else:
                        print(f"Skipped (already exists): {domain_name}")
                        skipped_count += 1
                else:
                    if domain_exists(cursor, domain_name, domain_type):
                        cursor.execute("DELETE FROM domainlist WHERE type = ? AND domain = ?", (domain_type, domain_name))
                        print(f"Removed: {domain_name}")
                        removed_count += 1
                        changes_made = True
                    else:
                        print(f"Skipped (not found): {domain_name}")
                        skipped_count += 1

            # Commit transaction
            conn.commit()

            # Close connection
            conn.close()
            break  # Break the loop if successful
        except sqlite3.OperationalError as e:
            if str(e) == "database is locked":
                attempts += 1
                print(f"Database is locked, retrying in {retry_delay} seconds... (Attempt {attempts}/{retry_count})")
                time.sleep(retry_delay)
            else:
                print(f"Error: {e}")
                break
        except Exception as e:
            print(f"Error: {e}")
            break

    # Check if all retries have been exhausted
    if attempts == retry_count:
        print("\nFailed to update the database after several retries.")
        return

    print("\nSummary:")
    print(f"Domains Added: {added_count}")
    print(f"Domains Removed: {removed_count}")
    print(f"Domains Skipped: {skipped_count}")

    return changes_made

def list_domains(domain_type):
    try:
        conn = sqlite3.connect(pihole_db_path)
        cursor = conn.cursor()
        
        if domain_type == 4:
            print("All domains:")
            for type_num in urls.keys():
                cursor.execute("SELECT domain FROM domainlist WHERE type = ?", (type_num,))
                domains = cursor.fetchall()
                if domains:
                    print(f"Domain type {type_num}:")
                    for domain in domains:
                        print(domain[0])
        else:
            cursor.execute("SELECT domain FROM domainlist WHERE type = ?", (domain_type,))
            domains = cursor.fetchall()
            if domains:
                print(f"Domains for type {domain_type}:")
                for domain in domains:
                    print(domain[0])
            else:
                print("No domains found for the selected type.")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

def clear_domains(domain_type):
    try:
        conn = sqlite3.connect(pihole_db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM domainlist WHERE type = ?", (domain_type,))
        conn.commit()
        conn.close()
        print("All domains cleared.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    clear_screen()  # Clear the screen when the script first starts

    print("Options: add, remove, list")
    action = input("Choose an action: ").strip().lower()

    clear_screen()  # Clear the screen after the user chooses an action

    changes_made = False
    if action == 'add':
        print("Add domains")
        print("0: Exact Whitelist\n1: Exact Blacklist\n2: Regex Whitelist\n3: Regex Blacklist\n4: All")
        domain_type = int(input("Choose an option: "))
        if domain_type not in urls and domain_type != 4:
            print("Invalid domain type. Exiting.")
            return

        if domain_type == 4:
            for type_num in urls.keys():
                domains = get_domains_from_url(urls[type_num])
                if domains:
                    changes_made |= add_or_remove_domains(domains, type_num, add=True)
        else:
            domains = get_domains_from_url(urls[domain_type])
            if not domains:
                print("\nNo domains to process. Exiting.")
                return
            changes_made |= add_or_remove_domains(domains, domain_type, add=True)
    elif action == 'remove':
        print("Remove domains")
        print("0: Exact Whitelist\n1: Exact Blacklist\n2: Regex Whitelist\n3: Regex Blacklist\n4: All")
        remove_option = int(input("Choose an option: "))
        if remove_option == 4:
            for type_num in urls.keys():
                domains = get_domains_from_url(urls[type_num])
                if domains:
                    changes_made |= add_or_remove_domains(domains, type_num, add=False)
        elif remove_option in urls.keys():
            domains = get_domains_from_url(urls[remove_option])
            if not domains:
                print("\nNo domains to process. Exiting.")
                return
            changes_made |= add_or_remove_domains(domains, remove_option, add=False)
        else:
            print("\nInvalid option. Exiting.")
            return
    elif action == 'list':
        print("List domains")
        print("0: Exact Whitelist\n1: Exact Blacklist\n2: Regex Whitelist\n3: Regex Blacklist\n4: All")
        domain_type = int(input("Choose an option: "))
        if domain_type not in urls and domain_type != 4:
            print("Invalid domain type. Exiting.")
            return
        if domain_type == 4:
            for type_num in urls.keys():
                list_domains(type_num)
        else:
            list_domains(domain_type)
    else:
        print("\nInvalid action. Exiting.")
        return

    if changes_made:
        restart_pihole_dns()

    print("\nMake sure to star this repository to show your support!")
    print("https://github.com/slyfox1186/pihole-regex")

def restart_pihole_dns():
    restart_option = input("\nRestart Pi-hole DNS resolver? (yes/no): ").strip().lower()
    if restart_option == 'yes':
        os.system('pihole restartdns')

if __name__ == "__main__":
    main()
