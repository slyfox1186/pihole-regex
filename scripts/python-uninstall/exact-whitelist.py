#!/usr/bin/env python3

import os
import argparse
import sqlite3
import subprocess
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import time

def fetch_whitelist_url(url):

    if not url:
        return

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}

    try:
        response = urlopen(Request(url, headers=headers))
    except HTTPError as e:
        print('[X] HTTP Error:', e.code, 'whilst fetching', url)
        print('\n')
        exit(1)
    except URLError as e:
        print('[X] URL Error:', e.reason, 'whilst fetching', url)
        print('\n')
        exit(1)

    # Read and decode
    response = response.read().decode('UTF-8').replace('\r\n', '\n')

    # If there is data
    if response:
        # Strip leading and trailing whitespace
        response = '\n'.join(x.strip() for x in response.splitlines())

    # Return the hosts
    return response


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def restart_pihole(docker):
    if docker is True:
        subprocess.call("docker exec -it pihole pihole restartdns reload",
                        shell=True, stdout=subprocess.DEVNULL)
    else:
        subprocess.call(['pihole', 'restartdns', 'reload'],
                        stdout=subprocess.DEVNULL)


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir", type=dir_path,
                    help="Optional: Pi-hole /etc directory")
parser.add_argument(
    "-D", "--docker",  action='store_true', help="Optional: Set if you're using Pi-hole in a Docker environment")
args = parser.parse_args()

if args.dir:
    pihole_location = args.dir
else:
    pihole_location = r'/etc/pihole'

whitelist_remote_url = 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/domains/whitelist/exact-whitelist.txt'
remote_sql_url = 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/domains/whitelist/exact-whitelist.sql'
gravity_whitelist_location = os.path.join(pihole_location, 'whitelist.txt')
gravity_db_location = os.path.join(pihole_location, 'gravity.db')
slyfox1186_whitelist_location = os.path.join(
    pihole_location, 'slyfox1186-whitelist.txt')

db_exists = False
sqliteConnection = None
cursor = None

whitelist_remote = set()
whitelist_local = set()
whitelist_slyfox1186_local = set()
whitelist_old_slyfox1186 = set()

os.system('clear')
print('''
If you are using Pi-hole 5.0 or later, this script will only remove domains that were added by itself.
Any other domains added by the user will remain uneffected.
''')

# Check for pihole path exsists
if os.path.exists(pihole_location):
    print("[i] Pi-hole's path exists.")
else:
    print("[X] {} was not found".format(pihole_location))
    print('\n')
    print('\n')
    exit(1)

# Check for write access to /etc/pihole
if os.access(pihole_location, os.X_OK | os.W_OK):
    print("[i] Write access to {} verified." .format(pihole_location))
    whitelist_str = fetch_whitelist_url(whitelist_remote_url)
    remote_whitelist_lines = whitelist_str.count('\n')
    remote_whitelist_lines += 1
else:
    print("[X] Write access is not available for {}. Please run the script as a privileged user." .format(pihole_location))
    print('\n')
    print('\n')
    exit(1)

# Determine whether we are using DB or not
if os.path.isfile(gravity_db_location) and os.path.getsize(gravity_db_location) > 0:
    db_exists = True
    print('[i] Pi-hole Gravity database found.')

    remote_sql_str = fetch_whitelist_url(remote_sql_url)
    remote_sql_lines = remote_sql_str.count('\n')
    remote_sql_lines += 1

    if len(remote_sql_str) > 0:
        print("[i] {} domains were discovered." .format(remote_whitelist_lines))
    else:
        print('[X] No remote SQL queries were found.')
        print('\n')
        print('\n')
        exit(1)
else:
    print('[i] Legacy Pi-hole detected (Version older than 5.0).')

if whitelist_str:
    whitelist_remote.update(x for x in map(
        str.strip, whitelist_str.splitlines()) if x and x[:1] != '#')
else:
    print('[X] No remote domains found.')
    print('\n')
    print('\n')
    exit(1)

if db_exists:
    # Create a DB connection
    print("[i] Connecting to Gravity's database.")

    try:
        sqliteConnection = sqlite3.connect(gravity_db_location)
        cursor = sqliteConnection.cursor()
        print("[i] Successfully connected to Gravity's database.")
        total_domains = cursor.execute(" SELECT * FROM domainlist WHERE type = 0 AND comment LIKE '%SlyEWL%' ")

        totalDomains = len(total_domains.fetchall())
        print("[i] There are a total of {} domains in your whitelist which were added by this script." .format(totalDomains))
        print('[i] Removing domains in the Gravity database.')
        cursor.execute (" DELETE FROM domainlist WHERE type = 0 AND comment LIKE '%SlyEWL%' ")

        sqliteConnection.commit()

        # We only removed domains we added so use total_domains
        print("[i] {} domains were removed." .format(totalDomains))
        remaining_domains = cursor.execute(" SELECT * FROM domainlist WHERE type = 0 OR type = 2 ")
        print("[i] There are a total of {} domains remaining in your whitelist." .format(len(remaining_domains.fetchall())))

        cursor.close()

    except sqlite3.Error as error:
        print("[X] Failed to remove domains from Gravity's database.", error)
        print('\n')
        print('\n')
        exit(1)

    finally:
        if (sqliteConnection):
            sqliteConnection.close()

            print("[i] The connection to the Gravity database has closed.")
            time.sleep(2)
            print('[i] Please wait for the Pi-hole server to restart.')
            restart_pihole(args.docker)
            print('[i] The Exact Whitelist Filters have been successfully removed from Gravity!')
            print('\n')
            print('Please make sure to star this repository to show support... it helps keep me motivated!')
            print('https://github.com/slyfox1186/pihole.regex')
else:
    if os.path.isfile(gravity_whitelist_location) and os.path.getsize(gravity_whitelist_location) > 0:
        print('[i] Collecting existing entries from whitelist.txt')
        with open(gravity_whitelist_location, 'r') as fRead:
            whitelist_local.update(x for x in map(
                str.strip, fRead) if x and x[:1] != '#')

    if whitelist_local:
        print("[i] {} existing whitelisted domains identified" .format(
            len(whitelist_local)))

        if os.path.isfile(slyfox1186_whitelist_location) and os.path.getsize(slyfox1186_whitelist_location) > 0:
            print('[i] Existing slyfox1186-whitelist installation located.')
            with open(slyfox1186_whitelist_location, 'r') as fOpen:
                whitelist_old_slyfox1186.update(x for x in map(
                    str.strip, fOpen) if x and x[:1] != '#')

                if whitelist_old_slyfox1186:
                    whitelist_local.difference_update(whitelist_old_slyfox1186)

            os.remove(slyfox1186_whitelist_location)

        else:
            print('[i] Removing all domains that match the remote repo.')
            whitelist_local.difference_update(whitelist_remote)

    print("[i] Adding exsisting {} domains to {}" .format(
        len(whitelist_local), gravity_whitelist_location))
    with open(gravity_whitelist_location, 'w') as fWrite:
        for line in sorted(whitelist_local):
            fWrite.write("{}\n".format(line))

    print('[i] Please wait for the Pi-hole server to restart.')
    restart_pihole(args.docker)
    print('[i] The Exact Whitelist Filters have been successfully removed from Gravity!')
    print('\n')
    print('Please make sure to star this repository to show support... it helps keep me motivated!')
    print('https://github.com/slyfox1186/pihole.regex')
