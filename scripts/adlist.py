#!/usr/bin/env python3

import logging
import os
import requests
import sqlite3
import subprocess
import time
from colorama import init, Fore, Style
from datetime import datetime

# Initialize colorama
init()

PIHOLE_DB_PATH = '/etc/pihole/gravity.db'
REMOTE_URL = 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlists.txt'
RETRY_COUNT = 5
RETRY_DELAY = 2
LOG_FILE = 'pihole_adlist.log'

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def fetch_remote_domains():
    try:
        print(f"{Fore.YELLOW}Fetching domains from remote URL...{Style.RESET_ALL}")
        response = requests.get(REMOTE_URL)
        response.raise_for_status()
        domains = {line.strip() for line in response.text.split('\n') if line.strip() and not line.startswith('#')}
        print(f"{Fore.GREEN}Successfully fetched {len(domains)} domains from remote URL.{Style.RESET_ALL}")
        logging.info(f"Successfully fetched {len(domains)} domains from remote URL.")
        return domains
    except requests.RequestException as e:
        print(f"{Fore.RED}Error fetching remote domains: {e}{Style.RESET_ALL}")
        logging.error(f"Error fetching remote domains: {e}")
        return set()

def fetch_local_domains(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT address FROM adlist")
    domains = {row[0] for row in cursor.fetchall()}
    print(f"{Fore.CYAN}Found {len(domains)} domains in local database.{Style.RESET_ALL}")
    logging.info(f"Found {len(domains)} domains in local database.")
    return domains

def restart_pihole_dns():
    try:
        print(f"{Fore.YELLOW}Attempting to restart Pi-hole DNS resolver...{Style.RESET_ALL}")
        
        # Execute the reload command
        print(f"{Fore.CYAN}Running 'pihole reloaddns' command - output will be displayed below:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        result = subprocess.run(["pihole", "reloaddns"], check=False)
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        if result.returncode == 0:
            print(f"{Fore.GREEN}Pi-hole DNS resolver restarted successfully.{Style.RESET_ALL}")
            logging.info("Pi-hole DNS resolver restarted successfully.")
            return True
        else:
            print(f"{Fore.RED}Failed to restart the Pi-hole DNS resolver. Exit code: {result.returncode}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Possible reasons for failure:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}1. This script is not running on the Pi-hole server{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}2. The 'pihole' command is not in your PATH{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}3. You may need to run this script with sudo privileges{Style.RESET_ALL}")
            logging.error(f"Failed to restart the Pi-hole DNS resolver. Exit code: {result.returncode}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Error restarting Pi-hole DNS: {e}{Style.RESET_ALL}")
        logging.error(f"Error restarting Pi-hole DNS: {e}")
        return False

def update_gravity():
    print(f"{Fore.YELLOW}Updating Pi-hole's gravity database...{Style.RESET_ALL}")
    try:
        # Run the command without capturing output so it displays in real-time
        print(f"{Fore.CYAN}Running 'pihole -g' command - output will be displayed below:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        result = subprocess.run(["pihole", "-g"], check=False)
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        if result.returncode == 0:
            print(f"{Fore.GREEN}Successfully updated Pi-hole's gravity database.{Style.RESET_ALL}")
            logging.info("Successfully updated Pi-hole's gravity database.")
            return True
        else:
            print(f"{Fore.RED}Failed to update Pi-hole's gravity database. Exit code: {result.returncode}{Style.RESET_ALL}")
            logging.error(f"Failed to update Pi-hole's gravity database. Exit code: {result.returncode}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Error updating Pi-hole's gravity database: {e}{Style.RESET_ALL}")
        logging.error(f"Error updating Pi-hole's gravity database: {e}")
        return False

def main():
    clear_screen()
    print(f"{Fore.CYAN}Pi-hole AdList Manager{Style.RESET_ALL}")
    print(f"{Fore.CYAN}====================={Style.RESET_ALL}")
    
    remote_domains = fetch_remote_domains()
    if not remote_domains:
        print(f"{Fore.RED}No domains fetched from remote URL. Exiting.{Style.RESET_ALL}")
        return

    attempts = 0
    while attempts < RETRY_COUNT:
        try:
            with sqlite3.connect(PIHOLE_DB_PATH) as conn:
                local_domains = fetch_local_domains(conn)
                domains_to_add = remote_domains - local_domains

                cursor = conn.cursor()
                cursor.execute("SELECT address FROM adlist WHERE comment LIKE 'SlyADL%'")
                slyadl_domains = {row[0] for row in cursor.fetchall()}
                domains_to_remove = slyadl_domains - remote_domains

                added_count = removed_count = 0
                changes_made = False

                if domains_to_add:
                    print(f"\n{Fore.GREEN}Domains to be Added:{Style.RESET_ALL}")
                    for domain in domains_to_add:
                        cursor.execute("INSERT INTO adlist (address, comment, enabled, date_added, date_modified) VALUES (?, ?, 1, ?, ?)",
                                    (domain, "SlyADL - SlyFox1186 AdList - github.com/slyfox1186/pihole-regex", datetime.now(), datetime.now()))
                        print(f" - Added: {domain}")
                        added_count += 1
                    changes_made = True
                else:
                    print(f"\n{Fore.YELLOW}No new domains to add.{Style.RESET_ALL}")

                if domains_to_remove:
                    print(f"\n{Fore.RED}Domains to be Removed:{Style.RESET_ALL}")
                    for domain in domains_to_remove:
                        cursor.execute("DELETE FROM adlist WHERE address = ? AND comment LIKE 'SlyADL%'", (domain,))
                        print(f" - Removed: {domain}")
                        removed_count += 1
                    changes_made = True
                else:
                    print(f"\n{Fore.YELLOW}No domains to remove.{Style.RESET_ALL}")

                conn.commit()
                break
        except sqlite3.OperationalError as e:
            if str(e) == "database is locked":
                attempts += 1
                print(f"{Fore.YELLOW}Database is locked. Retrying in {RETRY_DELAY} seconds... ({attempts}/{RETRY_COUNT}){Style.RESET_ALL}")
                time.sleep(RETRY_DELAY)
            else:
                print(f"{Fore.RED}SQLite error: {e}{Style.RESET_ALL}")
                logging.error(f"SQLite error: {e}")
                break
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            logging.error(f"Error: {e}")
            break

    if attempts == RETRY_COUNT:
        print(f"{Fore.RED}Failed to update the database after several retries.{Style.RESET_ALL}")
        logging.error("Failed to update the database after several retries.")
        return

    print(f"\n{Fore.CYAN}Summary:{Style.RESET_ALL}")
    print(f"Total Domains Added: {Fore.GREEN}{added_count}{Style.RESET_ALL}")
    print(f"Total Domains Removed: {Fore.RED}{removed_count}{Style.RESET_ALL}")

    if changes_made:
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Changes were made to the Pi-hole database.{Style.RESET_ALL}")
        update = input(f"{Fore.YELLOW}Do you want to update Pi-hole's gravity database now? (yes/no): {Style.RESET_ALL}").strip().lower()
        if update == 'yes':
            print()
            gravity_updated = update_gravity()
            
            if gravity_updated:
                restart = input(f"\n{Fore.YELLOW}Do you want to restart Pi-hole DNS resolver? (yes/no): {Style.RESET_ALL}").strip().lower()
                if restart == 'yes':
                    restart_pihole_dns()
            else:
                print(f"\n{Fore.YELLOW}Gravity update failed. DNS restart skipped.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}The Gravity update was skipped. Remember to update it manually.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    print(f"\n{Fore.GREEN}Make sure to star this repository to show your support!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}https://github.com/slyfox1186/pihole-regex{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
