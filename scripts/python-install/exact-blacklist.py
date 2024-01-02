#!/usr/bin/env python3

import os
import argparse
import sqlite3
import subprocess
import requests
import time

def fetch_blacklist_url(url):
    if not url:
        return None

    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        domains = []
        for line in response.text.strip().split("\n"):
            if not line.startswith("#") and line.strip():
                domains.append(line.strip())
        return domains
    except requests.exceptions.RequestException as e:
        print(f'[X] Error fetching URL {url}: {e}')
        return None

    if not url:
        return None

    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text.strip().split("\n")
    except requests.exceptions.RequestException as e:
        print(f"[X] Error fetching URL {url}: {e}")
        return None

def restart_pihole(docker):
    command = ["docker", "exec", "-it", "pihole", "pihole", "restartdns", "reload"] if docker else ["pihole", "-g"]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def update_database(db_path, domains):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            for domain in domains:
                # Assuming the domain variable now holds a exact string
                cursor.execute("INSERT OR IGNORE INTO domainlist (type, domain, enabled, date_added, comment) VALUES (?, ?, ?, ?, ?)", 
                               (1, domain, 1, int(time.time()), "SlyEBL - github.com/slyfox1186/pihole-exact"))
                print(f"Added exact: {domain}")
    except sqlite3.Error as e:
        print(f"[X] Database error: {e}")
        return

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            for domain in domains:
                cursor.execute("INSERT OR IGNORE INTO domainlist (type, domain, enabled, date_added, comment) VALUES (?, ?, ?, ?, ?)", (1, domain, 1, int(time.time()), "Added exact: "))
                print(f"Added exact: {domain}")
    except sqlite3.Error as e:
        print(f"[X] Database error: {e}")
        return

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="Pi-hole /etc directory", default="/etc/pihole")
    parser.add_argument("-D", "--docker", action="store_true", help="Use if Pi-hole is in a Docker environment")
    return parser.parse_args()

def main():
    args = parse_arguments()
    db_path = os.path.join(args.dir, "gravity.db")

    blacklist_url = "https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-blacklist.txt"
    domains = fetch_blacklist_url(blacklist_url)
    if domains:
        update_database(db_path, domains)
        restart_pihole(args.docker)
        print("[i] Pi-hole blacklist updated and DNS service restarted.")
    else:
        print("[X] No domains to update.")

if __name__ == "__main__":
    main()
