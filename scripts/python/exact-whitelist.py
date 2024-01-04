#!/usr/bin/env python3

import sqlite3
import requests
import subprocess
import sys

# URL of the remote SQL file
SQL_FILE_URL = 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-whitelist.sql'

# Local path of the Pi-hole gravity.db file
GRAVITY_DB_PATH = '/etc/pihole/gravity.db'

def download_sql_file(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.split('\n')

def process_sql_line(line):
    if line.startswith('#') or line.strip() == '':
        return None, None
    parts = line.split(' -- ')
    domain = parts[0].strip()
    comment = 'SlyEWL - ' + parts[1].strip() if len(parts) > 1 else 'SlyEWL -'
    return domain, comment

def update_pihole_db(domains_to_update):
    conn = sqlite3.connect(GRAVITY_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT domain, comment FROM domainlist WHERE type=0")
    existing_domains = {row[0]: row[1] for row in cursor.fetchall()}

    added = []
    removed = []

    # Add new domains or update existing ones
    for domain, comment in domains_to_update.items():
        if domain in existing_domains:
            if existing_domains[domain].startswith('SlyEWL'):
                if existing_domains[domain] != comment:
                    cursor.execute("DELETE FROM domainlist WHERE domain=?", (domain,))
                    removed.append((domain, existing_domains[domain].replace('SlyEWL - ', '')))
            else:
                cursor.execute("INSERT INTO domainlist (type, domain, comment) VALUES (?, ?, ?)", (0, domain, comment))
                added.append((domain, comment.replace('SlyEWL - ', '')))

    # Remove domains that are no longer in the SQL file
    for domain, comment in existing_domains.items():
        if domain not in domains_to_update and comment.startswith('SlyEWL'):
            cursor.execute("DELETE FROM domainlist WHERE domain=?", (domain,))
            removed.append((domain, comment.replace('SlyEWL - ', '')))

    conn.commit()
    conn.close()
    return added, removed

def check_for_updates():
    result = subprocess.run(['pihole', '-v', '-c'], capture_output=True, text=True)
    return 'Update available!' in result.stdout

def restart_dns_resolver():
    subprocess.run(['pihole', 'restartdns', 'reload'], check=True)

def main():
    try:
        sql_lines = download_sql_file(SQL_FILE_URL)
        domains_to_update = {d: c for d, c in (process_sql_line(l) for l in sql_lines) if d}

        added, removed = update_pihole_db(domains_to_update)
        if added:
            print("\nAdded domains:")
            for domain, comment in added:
                print(f"{domain} -- {comment}")
        if removed:
            print("\nRemoved domains:")
            for domain, comment in removed:
                print(f"{domain} -- {comment}")

        if check_for_updates() and user_confirm("Pi-hole update available. Do you want to update? (yes/no): "):
            subprocess.run(['pihole', '-up'], check=True)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # Wait for 3 seconds before the script ends
        time.sleep(3)

if __name__ == "__main__":
    main()
