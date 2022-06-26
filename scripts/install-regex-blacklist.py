#!/usr/bin/env python3

import json
import os
import time
import sqlite3
import subprocess
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def fetch_url(url):

    if not url:
        return

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}

    print('[i] Fetching:', url)

    try:
        response = urlopen(Request(url, headers=headers))
    except HTTPError as e:
        print('[E] HTTP Error:', e.code, 'whilst fetching', url)
        return
    except URLError as e:
        print('[E] URL Error:', e.reason, 'whilst fetching', url)
        return

    # Read and decode
    response = response.read().decode('UTF-8').replace('\r\n', '\n')

    # If there is data
    if response:
        # Strip leading and trailing whitespace
        response = '\n'.join(x for x in map(str.strip, response.splitlines()))

    # Return the hosts
    return response


url_RegExStrings_remote = 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/domains/regex-blacklist.txt'
install_comment = 'sly99'

cmd_restart = ['pihole', 'restartdns', 'reload']

db_exists = False
conn = None
c = None

RegExStrings_remote = set()
RegExStrings_local = set()
RegExStrings_slyfox1186_local = set()
RegExStrings_legacy_slyfox1186 = set()
RegExStrings_remove = set()

# Start the docker directory override
print('[i] Checking if Pi-hole is running inside a docker container.')

# Initialise the docker variables
docker_id = None
docker_mnt = None
docker_mnt_src = None

# Check to see whether the default "pihole" docker container is active
try:
    docker_id = subprocess.run(['docker', 'ps', '--filter', 'name=pihole', '-q'],
                               stdout=subprocess.PIPE, universal_newlines=True).stdout.strip()
# Exception for if docker is not installed
except FileNotFoundError:
    pass

# If a pihole docker container was found, locate the first mount
if docker_id:
    docker_mnt = subprocess.run(['docker', 'inspect', '--format', '{{ (json .Mounts) }}', docker_id],
                                stdout=subprocess.PIPE, universal_newlines=True).stdout.strip()
    # Convert output to JSON and iterate through each dict
    for json_dict in json.loads(docker_mnt):
        # If this mount's destination is /etc/pihole
        if json_dict['Destination'] == r'/etc/pihole':
            # Use the source path as our target
            docker_mnt_src = json_dict['Source']
            break

    # If we successfully found the mount
    if docker_mnt_src:
        print('[i] Pi-hole is running through docker.')
        # Prepend restart commands
        cmd_restart[0:0] = ['docker', 'exec', '-i', 'pihole']
else:
    print('[i] Running in physical installation mode.')

# Set paths
path_pihole = docker_mnt_src if docker_mnt_src else r'/etc/pihole'
path_legacy_regex = os.path.join(path_pihole, 'regex.list')
path_legacy_slyfox1186_regex = os.path.join(path_pihole, 'slyfox1186-regex.list')
path_pihole_db = os.path.join(path_pihole, 'gravity.db')

# Check that Pi-hole path exists
if os.path.exists(path_pihole):
    print("[i] Pi-hole's path has been located!")
else:
    print(f'[e] {path_pihole} was not found.')
    exit(1)

# Check for write access to /etc/pihole
if os.access(path_pihole, os.X_OK | os.W_OK):
    print(f'[i] The script has write access to {path_pihole}.')
else:
    print(f'[e] The script does not have write access available for {path_pihole}. Please re-run the script as a privileged user.')
    exit(1)

# Determine whether we are using DB or not
if os.path.isfile(path_pihole_db) and os.path.getsize(path_pihole_db) > 0:
    db_exists = True
    print('[i] Gravity database found.')
else:
    print('[i] Legacy regex.list found.')

# Fetch the remote RegExStrings
str_RegExStrings_remote = fetch_url(url_RegExStrings_remote)

# If RegExStrings were fetched, remove any comments and add to set
if str_RegExStrings_remote:
    RegExStrings_remote.update(x for x in map(str.strip, str_RegExStrings_remote.splitlines()) if x and x[:1] != '#')
    print(f'[i] {len(RegExStrings_remote)} RegExStrings collected from {url_RegExStrings_remote}')
else:
    print('[i] No remote RegExStrings were found.')
    exit(1)

if db_exists:
    # Connect to Gravity's database
    print(f'[i] Connecting to {path_pihole_db}')

    try:
        conn = sqlite3.connect(path_pihole_db)
    except sqlite3.Error as e:
        print(e)
        exit(1)

    # Create a cursor object
    c = conn.cursor()

    # Add / update remote RegExStrings
    print("[i] Updating the RegExStrings in Gravity's database.")

    c.executemany('INSERT OR IGNORE INTO domainlist (type, domain, enabled, comment) '
                  'VALUES (3, ?, 1, ?)',
                  [(x, install_comment) for x in sorted(RegExStrings_remote)])
    c.executemany('UPDATE domainlist '
                  'SET comment = ? WHERE domain in (?) AND comment != ?',
                  [(install_comment, x, install_comment) for x in sorted(RegExStrings_remote)])

    conn.commit()

    # Fetch all current slyfox1186 RegExStrings in the local db
    c.execute('SELECT domain FROM domainlist WHERE type = 3 AND comment = ?', (install_comment,))
    RegExStrings_slyfox1186_local_results = c.fetchall()
    RegExStrings_slyfox1186_local.update([x[0] for x in RegExStrings_slyfox1186_local_results])

    # Remove any local entries that do not exist in the remote list
    # (will only work for previous installs where we've set the comment field)
    print('[i] Removeing old RegExStrings from Gravity.')
    RegExStrings_remove = RegExStrings_slyfox1186_local.difference(RegExStrings_remote)

    if RegExStrings_remove:
        print('[i] Removeing old RegExStrings from Gravity.')
        c.executemany('DELETE FROM domainlist WHERE type = 3 AND domain in (?)', [(x,) for x in RegExStrings_remove])
        conn.commit()

    # Delete slyfox1186-regex.list as if we've migrated to the db, it's no longer needed
    if os.path.exists(path_legacy_slyfox1186_regex):
        os.remove(path_legacy_slyfox1186_regex)

    print('[i] Pi-hole must restart... please wait for it to boot.')
    subprocess.run(cmd_restart, stdout=subprocess.DEVNULL)
    print('\n')

    # Prepare final result
    print("[i] Pi-hole is now running! Script complete!\n")

    c.execute('Select domain FROM domainlist WHERE type = 3')
    final_results = c.fetchall()
    RegExStrings_local.update(x[0] for x in final_results)

    print(*sorted(RegExStrings_local), sep='\n')

    conn.close()

else:
    # If regex.list exists and is not empty, read it and add to a set.
    if os.path.isfile(path_legacy_regex) and os.path.getsize(path_legacy_regex) > 0:
        print('[i] The script is analyzing the current regex.list')
        with open(path_legacy_regex, 'r') as fRead:
            RegExStrings_local.update(x for x in map(str.strip, fRead) if x and x[:1] != '#')

    # If the local regexp set is not empty
    if RegExStrings_local:
        print(f'[i] {len(RegExStrings_local)} existing RegExStrings identified')
        # If we have a record of a previous legacy install
        if os.path.isfile(path_legacy_slyfox1186_regex) and os.path.getsize(path_legacy_slyfox1186_regex) > 0:
            print('[i] An existing slyfox1186-regex installation was found.')
            # Read the previously installed RegExStrings to a set
            with open(path_legacy_slyfox1186_regex, 'r') as fOpen:
                RegExStrings_legacy_slyfox1186.update(x for x in map(str.strip, fOpen) if x and x[:1] != '#')

                if RegExStrings_legacy_slyfox1186:
                    print('[i] The script is removing previously installed RegExStrings')
                    RegExStrings_local.difference_update(RegExStrings_legacy_slyfox1186)

    # Add remote RegExStrings to local RegExStrings
    print(f'[i] Syncing with {url_RegExStrings_remote}')
    RegExStrings_local.update(RegExStrings_remote)

    # Output to regex.list
    print(f'[i] Outputting {len(RegExStrings_local)} RegExStrings to {path_legacy_regex}')
    with open(path_legacy_regex, 'w') as fWrite:
        for line in sorted(RegExStrings_local):
            fWrite.write(f'{line}\n')

    # Output slyfox1186 remote RegExStrings to slyfox1186-regex.list
    # for future install / uninstall
    with open(path_legacy_slyfox1186_regex, 'w') as fWrite:
        for line in sorted(RegExStrings_remote):
            fWrite.write(f'{line}\n')

    print('[i] Pi-hole must be restarted. Please give it time to reboot.')
    print('[i] Pi-hole must restart... please wait for it to boot.')
    subprocess.run(cmd_restart, stdout=subprocess.DEVNULL)
    
# Prepare final result
    print("[i] Pi-hole is now running! Script complete!\n")
    with open(path_legacy_regex, 'r') as fOpen:
        for line in fOpen:
            print(line, end='')
