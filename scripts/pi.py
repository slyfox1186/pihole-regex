#!/usr/bin/env python3

import logging
import os
import re
import requests
import sqlite3
import textwrap
import time
from colorama import init, Fore, Style
from contextlib import contextmanager
from datetime import datetime
from tabulate import tabulate
from textwrap import shorten

# Initialize colorama, fallback to no-color if terminal doesn't support ANSI escape codes
init()

PIHOLE_DB_PATH = '/etc/pihole/gravity.db'
RETRY_COUNT = 5
RETRY_DELAY = 2
LOG_FILE = 'pihole_regex.log'

URLS = {
    0: 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-whitelist.sql',
    1: 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-blacklist.sql',
    2: 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/regex-whitelist.sql',
    3: 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/regex-blacklist.sql'
}

class SingleTimeStampLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self.first_log = True

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        if self.first_log:
            timestamp = datetime.now().strftime('[%m-%d-%Y %I:%M:%S %p]')
            print(f"{Fore.CYAN}{timestamp}{Style.RESET_ALL}")
            self.first_log = False
        
        if level == logging.INFO:
            label = f"{Fore.GREEN}[INFO]{Style.RESET_ALL}"
        elif level == logging.ERROR:
            label = f"{Fore.RED}[ERROR]{Style.RESET_ALL}"
        elif level == logging.WARNING:
            label = f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL}"
        elif level == logging.REMOVED:
            label = f"{Fore.MAGENTA}[REMOVED]{Style.RESET_ALL}"
        else:
            label = f"[{logging.getLevelName(level)}]"
        
        colored_msg = f"{label} {msg}"
        super()._log(level, colored_msg, args, exc_info, extra, stack_info)

logging.REMOVED = 25
logging.addLevelName(logging.REMOVED, "REMOVED")

logging.setLoggerClass(SingleTimeStampLogger)
logging.basicConfig(
    format='%(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_domains_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        domains = [line.strip() for line in response.text.strip().split('\n') if line.strip() and not line.startswith('#')]
        return domains
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download domains from {url}: {e}")
        return []

@contextmanager
def db_connection():
    conn = None
    try:
        conn = sqlite3.connect(PIHOLE_DB_PATH)
        yield conn
    finally:
        if conn:
            conn.close()

def domain_exists(cursor, domain, domain_type):
    cursor.execute("SELECT 1 FROM domainlist WHERE domain = ? AND type = ?", (domain, domain_type))
    return cursor.fetchone() is not None

def add_or_remove_domains(domains, domain_type, add=True):
    added_count = removed_count = skipped_count = attempts = 0
    changes_made = False
    processed_domains = set()

    while attempts < RETRY_COUNT:
        try:
            with db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("BEGIN TRANSACTION;")

                skipped_domains = []
                for domain in domains:
                    parts = domain.split(' -- ')
                    domain_name = parts[0].strip()
                    comment = f"Sly{'EWL' if domain_type == 0 else 'EBL' if domain_type == 1 else 'RWL' if domain_type == 2 else 'RBL'} - {parts[1].strip()}" if len(parts) > 1 else ''

                    if domain_name not in processed_domains:
                        processed_domains.add(domain_name)
                        if add:
                            if not domain_exists(cursor, domain_name, domain_type):
                                cursor.execute("INSERT INTO domainlist (type, domain, enabled, comment, date_added, date_modified) VALUES (?, ?, 1, ?, ?, ?)",
                                               (domain_type, domain_name, comment, datetime.now(), datetime.now()))
                                added_count += 1
                                changes_made = True
                                logging.info(f"Added: {domain_name}")
                            else:
                                skipped_domains.append(domain_name)
                        else:
                            if domain_exists(cursor, domain_name, domain_type):
                                cursor.execute("DELETE FROM domainlist WHERE type = ? AND domain = ?", (domain_type, domain_name))
                                removed_count += 1
                                changes_made = True
                                logging.log(logging.REMOVED, f"Removed: {domain_name}")
                            else:
                                skipped_domains.append(domain_name)

                # Print the warning messages for skipped domains
                for domain in skipped_domains:
                    logging.warning(f"Skipped (already exists): {domain}")

                conn.commit()
                break
        except sqlite3.OperationalError as e:
            if str(e) == "database is locked":
                attempts += 1
                time.sleep(RETRY_DELAY)
            else:
                logging.error(f"SQLite error: {e}")
                break
        except Exception as e:
            logging.error(f"Error: {e}")
            break

    if attempts == RETRY_COUNT:
        logging.error("Failed to update the database after several retries.")

    return added_count, removed_count, skipped_count, changes_made

def add_domain(domain_type):
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            domain = input("Enter the domain to add: ")
            cursor.execute("INSERT INTO domainlist (type, domain, enabled, date_added, date_modified) VALUES (?, ?, 1, ?, ?)",
                           (domain_type, domain, datetime.now(), datetime.now()))
            conn.commit()
            logging.info(f"Domain {domain} added successfully.")
    except Exception as e:
        logging.error(f"Error: {e}")
    if input("Restart Pi-hole DNS resolver? (yes/no): ").strip().lower() == 'yes':
        restart_pihole_dns()

def remove_domain(domain_type):
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            domain = input("Enter the domain to remove: ")
            if domain_exists(cursor, domain, domain_type):
                cursor.execute("DELETE FROM domainlist WHERE type = ? AND domain = ?", (domain_type, domain))
                conn.commit()
                logging.log(logging.REMOVED, f"Domain {domain} removed successfully.")
            else:
                logging.warning(f"Skipped (doesn't exist): {domain}")
    except Exception as e:
        logging.error(f"Error: {e}")
    if input("Restart Pi-hole DNS resolver? (yes/no): ").strip().lower() == 'yes':
        restart_pihole_dns()

def list_domains(domain_type):
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT domain, comment, enabled, date_added, date_modified FROM domainlist WHERE type = ?", (domain_type,))
            domains = cursor.fetchall()
            if domains:
                logging.info("Current domains found in the database:")
                box_width = 90
                for row in domains:
                    domain_str = row[0]
                    comment = row[1]
                    enabled = row[2]
                    date_added = row[3]
                    date_modified = row[4]

                    # Try to parse the date_added and date_modified values
                    try:
                        date_added = datetime.strptime(date_added, '%Y-%m-%d %H:%M:%S.%f').strftime('%b-%d-%Y %I:%M:%S %p')
                    except ValueError:
                        date_added = datetime.fromtimestamp(int(date_added)).strftime('%b-%d-%Y %I:%M:%S %p')

                    try:
                        date_modified = datetime.strptime(date_modified, '%Y-%m-%d %H:%M:%S.%f').strftime('%b-%d-%Y %I:%M:%S %p')
                    except ValueError:
                        date_modified = datetime.fromtimestamp(int(date_modified)).strftime('%b-%d-%Y %I:%M:%S %p')

                    wrapped_comment = textwrap.wrap(comment, width=box_width - 4)

                    domain_info = f"┌{'─' * (box_width - 2)}┐\n"
                    domain_info += f"│ {domain_str:<{box_width - 4}} │\n"
                    domain_info += f"├{'─' * (box_width - 2)}┤\n"
                    for line in wrapped_comment:
                        domain_info += f"│ {line:<{box_width - 4}} │\n"
                    domain_info += f"│ Enabled: {'Yes' if enabled else 'No':<{box_width - 13}} │\n"
                    domain_info += f"│ Added: {date_added:<{box_width - 11}} │\n"
                    domain_info += f"│ Modified: {date_modified:<{box_width - 14}} │\n"
                    domain_info += f"└{'─' * (box_width - 2)}┘"

                    logging.info(domain_info)
            else:
                logging.warning("No domains found in the database.")
    except Exception as e:
        logging.error(f"Error: {e}")

def format_table(data, headers, column_widths):
    def format_row(row):
        return "| " + " | ".join(f"{cell:<{width}}" for cell, width in zip(row, column_widths)) + " |"

    separator = "+" + "+".join("-" * (width + 2) for width in column_widths) + "+"
    
    table = [separator]
    table.append(format_row(headers))
    table.append(separator)
    for row in data:
        table.append(format_row(row))
    table.append(separator)
    
    return "\n".join(table)

def search_domains(domain_type):
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            search_term = input("Enter the search term: ").lower()
            cursor.execute("SELECT domain, comment, enabled, date_added, date_modified, type FROM domainlist WHERE LOWER(domain) LIKE ? ORDER BY type",
                           (f"%{search_term}%",))
            domains = cursor.fetchall()
            if domains:
                logging.info(f"{Fore.CYAN}Search Results for '{search_term}':{Style.RESET_ALL}")
                
                grouped_results = {}
                for row in domains:
                    domain_type = row[5]
                    if domain_type not in grouped_results:
                        grouped_results[domain_type] = []
                    grouped_results[domain_type].append(row)
                
                for domain_type, results in grouped_results.items():
                    type_name = {0: "Exact Whitelist", 1: "Exact Blacklist", 2: "Regex Whitelist", 3: "Regex Blacklist"}.get(domain_type, "Unknown")
                    print(f"\n{Fore.YELLOW}{type_name}:{Style.RESET_ALL}")
                    
                    headers = ["Domain", "Comment", "Enabled", "Added", "Modified"]
                    column_widths = [40, 30, 7, 19, 19]
                    
                    table_data = []
                    for row in results:
                        domain_str = shorten(row[0], width=column_widths[0], placeholder="...")
                        comment = shorten(row[1], width=column_widths[1], placeholder="...")
                        enabled = "Yes" if row[2] else "No"
                        date_added = row[3][:19]  # Truncate milliseconds
                        date_modified = row[4][:19]  # Truncate milliseconds
                        
                        table_data.append([
                            domain_str,
                            comment,
                            enabled,
                            date_added,
                            date_modified
                        ])
                    
                    print(format_table(table_data, headers, column_widths))
                
                print(f"\n{Fore.CYAN}Total results: {len(domains)}{Style.RESET_ALL}")
                
                while True:
                    view_details = input("View full details for any domain? (y/n): ").lower().strip()
                    if view_details == 'y':
                        while True:
                            domain_to_view = input("Enter the domain (or 'exit' to return to main menu): ").strip().lower()
                            if domain_to_view == 'exit':
                                break
                            if domain_to_view:
                                matching_domains = []
                                for domain_type, results in grouped_results.items():
                                    for row in results:
                                        if domain_to_view in row[0].lower():
                                            matching_domains.append(row)
                                
                                if matching_domains:
                                    if len(matching_domains) > 1:
                                        print(f"\n{Fore.CYAN}Multiple matches found. Please choose:{Style.RESET_ALL}")
                                        for i, domain in enumerate(matching_domains, 1):
                                            print(f"{i}. {domain[0]}")
                                        choice = input("Enter the number of the domain to view (or 'all' to view all): ")
                                        if choice.lower() == 'all':
                                            domains_to_show = matching_domains
                                        else:
                                            try:
                                                index = int(choice) - 1
                                                domains_to_show = [matching_domains[index]]
                                            except (ValueError, IndexError):
                                                print(f"{Fore.RED}Invalid choice. Showing all matches.{Style.RESET_ALL}")
                                                domains_to_show = matching_domains
                                    else:
                                        domains_to_show = matching_domains

                                    for row in domains_to_show:
                                        print(f"\n{Fore.CYAN}Full details for {row[0]}:{Style.RESET_ALL}")
                                        print(f"Domain: {row[0]}")
                                        print(f"Comment: {row[1]}")
                                        print(f"Enabled: {Fore.GREEN if row[2] else Fore.RED}{row[2]}{Style.RESET_ALL}")
                                        print(f"Added: {row[3]}")
                                        print(f"Modified: {row[4]}")
                                        print(f"Type: {['Exact Whitelist', 'Exact Blacklist', 'Regex Whitelist', 'Regex Blacklist'][row[5]]}")
                                else:
                                    print(f"{Fore.RED}Domain not found in search results.{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.YELLOW}No domain entered. Please try again or type 'exit' to return to main menu.{Style.RESET_ALL}")
                    elif view_details == 'n':
                        break
                    else:
                        print(f"{Fore.YELLOW}Invalid input. Please enter 'y' or 'n'.{Style.RESET_ALL}")
            else:
                logging.warning(f"{Fore.YELLOW}No matching domains found.{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

def get_domain_statistics():
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT type, COUNT(*) FROM domainlist GROUP BY type")
            statistics = cursor.fetchall()
            if statistics:
                total_domains = sum(count for _, count in statistics)
                
                type_labels = {
                    0: "Exact Whitelist",
                    1: "Exact Blacklist",
                    2: "Regex Whitelist",
                    3: "Regex Blacklist"
                }
                
                print(f"\n{Fore.CYAN}Domain Statistics:{Style.RESET_ALL}")
                for domain_type, count in statistics:
                    percentage = (count / total_domains) * 100
                    label = type_labels.get(domain_type, f"Unknown Type {domain_type}")
                    print(f"{Fore.GREEN}{label:<20}{Style.RESET_ALL} | Count: {Fore.YELLOW}{count:<5}{Style.RESET_ALL} | Percentage: {Fore.MAGENTA}{percentage:.2f}%{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}No domain statistics found.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")

def backup_database():
    try:
        backup_filename = f"gravity_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        with open(PIHOLE_DB_PATH, 'rb') as src_file, open(backup_filename, 'wb') as dst_file:
            dst_file.write(src_file.read())
        logging.info(f"Database backup created: {backup_filename}")
    except Exception as e:
        logging.error(f"Error: {e}")

def restore_database():
    try:
        backup_filename = input("Enter the backup filename: ")
        with open(backup_filename, 'rb') as src_file, open(PIHOLE_DB_PATH, 'wb') as dst_file:
            dst_file.write(src_file.read())
        logging.info(f"Database restored from: {backup_filename}")
        restart_pihole_dns()
    except Exception as e:
        logging.error(f"Error: {e}")

def restart_pihole_dns():
    try:
        output = os.system('pihole restartdns')
        if output == 0:
            logging.info("Pi-hole DNS resolver restarted successfully.")
        else:
            logging.error("Failed to restart the Pi-hole DNS resolver.")
    except Exception as e:
        logging.error(f"Error restarting Pi-hole DNS: {e}")

def main():
    clear_screen()

    print(f"{Fore.CYAN}Options: add, remove, list, search, stats, backup, restore{Style.RESET_ALL}")
    action = input("Choose an action: ").strip().lower()
    clear_screen()

    changes_made = False
    added_total = removed_total = skipped_total = 0

    if action == 'add':
        logging.info("Add domains")
        print(f"{Fore.MAGENTA}0: Exact Whitelist\n1: Exact Blacklist\n2: Regex Whitelist\n3: Regex Blacklist\n4: All{Style.RESET_ALL}")
        domain_type = int(input("Choose an option: "))
        clear_screen()
        if domain_type not in URLS and domain_type != 4:
            logging.error("Invalid domain type. Exiting.")
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
                logging.warning("No domains to process. Exiting.")
                return
            added_total, removed_total, skipped_total, changes_made = add_or_remove_domains(domains, domain_type, add=True)
    elif action == 'remove':
        logging.info("Remove domains")
        print(f"{Fore.MAGENTA}0: Exact Whitelist\n1: Exact Blacklist\n2: Regex Whitelist\n3: Regex Blacklist\n4: All{Style.RESET_ALL}")
        remove_option = int(input("Choose an option: "))
        clear_screen()
        if remove_option == 4:
            for type_num in URLS:
                domains = get_domains_from_url(URLS[type_num])
        elif remove_option in URLS:
            domains = get_domains_from_url(URLS[remove_option])
            if not domains:
                logging.warning("No domains to process. Exiting.")
                return
            added_total, removed_total, skipped_total, changes_made = add_or_remove_domains(domains, remove_option, add=False)
        else:
            logging.error("Invalid option. Exiting.")
            return
    elif action == 'list':
        logging.info("List domains")
        print(f"{Fore.MAGENTA}0: Exact Whitelist\n1: Exact Blacklist\n2: Regex Whitelist\n3: Regex Blacklist\n4: All{Style.RESET_ALL}")
        domain_type = int(input("Choose an option: "))
        clear_screen()
        if domain_type not in URLS and domain_type != 4:
            logging.error("Invalid domain type. Exiting.")
            return
        if domain_type == 4:
            for type_num in URLS:
                list_domains(type_num)
        else:
            list_domains(domain_type)
    elif action == 'search':
        logging.info("Search domains")
        print(f"{Fore.MAGENTA}0: Exact Whitelist\n1: Exact Blacklist\n2: Regex Whitelist\n3: Regex Blacklist\n4: All{Style.RESET_ALL}")
        domain_type = int(input("Choose an option: "))
        clear_screen()
        if domain_type not in URLS and domain_type != 4:
            logging.error("Invalid domain type. Exiting.")
            return
        if domain_type == 4:
            for type_num in URLS:
                search_domains(type_num)
        else:
            search_domains(domain_type)
    elif action == 'stats':
        get_domain_statistics()
    elif action == 'backup':
        backup_database()
    elif action == 'restore':
        restore_database()
    else:
        logging.error("Invalid action. Exiting.")
        return

    print()  # Add an extra blank line before the summary
    print(f"{Fore.CYAN}Summary:{Style.RESET_ALL}")
    print(f"Total Domains Added: {Fore.GREEN}{added_total}{Style.RESET_ALL}")
    print(f"Total Domains Removed: {Fore.RED}{removed_total}{Style.RESET_ALL}")
    print(f"Total Domains Skipped: {Fore.YELLOW}{skipped_total}{Style.RESET_ALL}")

    if changes_made:
        print()  # Add a blank line before the restart prompt
        if input("Restart Pi-hole DNS resolver? (yes/no): ").strip().lower() == 'yes':
            restart_pihole_dns()

    print()  # Add an extra blank line before the final message
    print(f"{Fore.GREEN}Make sure to star this repository to show your support!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}https://github.com/slyfox1186/pihole-regex{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
