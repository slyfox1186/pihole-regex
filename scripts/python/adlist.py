#!/usr/bin/env python3

import requests
import sqlite3
import os
import subprocess  # Importing the subprocess module

# Define the path to the Pi-hole database and the URL of the remote text file
PIHOLE_DB_PATH = '/etc/pihole/gravity.db'
REMOTE_URL = 'https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlists.txt'

def fetch_remote_domains():
    try:
        response = requests.get(REMOTE_URL)
        response.raise_for_status()
        return {line.strip() for line in response.text.split('\n') if line.strip() and not line.startswith('#')}
    except requests.RequestException as e:
        print(f"Error fetching remote domains: {e}")
        return set()

def fetch_local_domains():
    conn = sqlite3.connect(PIHOLE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT address FROM adlist")
    domains = {row[0] for row in cursor.fetchall()}
    conn.close()
    return domains

def update_gravity():
    print("Updating Pi-hole's gravity database...")
    subprocess.run(["pihole", "-g"])

def main():
    remote_domains = fetch_remote_domains()
    local_domains = fetch_local_domains()

    domains_to_add = remote_domains - local_domains
    domains_to_remove = set()

    conn = sqlite3.connect(PIHOLE_DB_PATH)
    cursor = conn.cursor()

    # Fetching domains with SlyADL comment for removal
    cursor.execute("SELECT address FROM adlist WHERE comment LIKE 'SlyADL%'")
    slyadl_domains = {row[0] for row in cursor.fetchall()}
    domains_to_remove = {domain for domain in slyadl_domains if domain not in remote_domains}

    # Print changes
    changes_made = False
    if domains_to_add:
        print("\nDomains to be Added:")
        for domain in domains_to_add:
            cursor.execute("INSERT INTO adlist (address, comment) VALUES (?, ?)", 
                           (domain, "SlyADL - SlyFox1186 AdList - github.com/slyfox1186/pihole-regex"))
            print(f" - Added: {domain}")
        changes_made = True
    else:
        print("\nNo new domains to add.")

    if domains_to_remove:
        print("\nDomains to be Removed:")
        for domain in domains_to_remove:
            cursor.execute("DELETE FROM adlist WHERE address = ? AND comment LIKE 'SlyADL%'", (domain,))
            print(f" - Removed: {domain}")
        changes_made = True
    else:
        print("\nNo domains to remove.")

    conn.commit()
    conn.close()

    # Ask user to update gravity if changes were made
    if changes_made:
        update = input("\nDo you want to update Pi-hole's gravity database now? (yes/no): ").strip().lower()
        if update == 'yes':
            update_gravity()
        else:
            print("\nThe Gravity update was skipped. Remember to update it manually.")

    # Print the message about starring the repository
    print("\nMake sure to star this repository to show your support!")
    print("https://github.com/slyfox1186/pihole-regex")

if __name__ == "__main__":
    main()
