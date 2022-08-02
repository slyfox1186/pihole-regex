#!/usr/bin/env python3

import json
import os
import sqlite3
import subprocess
import time
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


url_exactps_remote = 'https://raw.githubusercontent.com/slyfox1186/pihole.exact/main/domains/blacklist/exact-blacklist.txt'
install_comment = 'SlyEBL'

cmd_restart = ['pihole', 'restartdns', 'reload']

db_exists = False
conn = None
c = None

exactps_remote = set()
exactps_local = set()
exactps_slyfox1186_local = set()
exactps_legacy_slyfox1186 = set()
exactps_remove = set()

# Start the docker directory override
print('[i] Checking for "pihole" docker container')

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
        print('[i] Running in docker installation mode.')
        # Prepend restart commands
        cmd_restart[0:0] = ['docker', 'exec', '-i', 'pihole']
else:
    print('[i] Running in physical installation mode.')

# Set paths
path_pihole = docker_mnt_src if docker_mnt_src else r'/etc/pihole'
path_legacy_exact = os.path.join(path_pihole, 'exact.list')
path_legacy_slyfox1186_exact = os.path.join(path_pihole, 'slyfox1186-exact.list')
path_pihole_db = os.path.join(path_pihole, 'gravity.db')

# Check that pi-hole path exists
if os.path.exists(path_pihole):
    print('[i] Pi-hole path exists.')
else:
    print(f'[e] {path_pihole} was not found')
    exit(1)

# Check for write access to /etc/pihole
if os.access(path_pihole, os.X_OK | os.W_OK):
    print(f'[i] Write access to {path_pihole} verified')
else:
    print(f'[e] Write access is not available for {path_pihole}. Please run as root or other privileged user')
    exit(1)

# Determine whether we are using DB or not
if os.path.isfile(path_pihole_db) and os.path.getsize(path_pihole_db) > 0:
    db_exists = True
    print('[i] DB detected')
else:
    print('[i] Legacy exact.list detected')

# Fetch the remote exactps
str_exactps_remote = fetch_url(url_exactps_remote)

# If exactps were fetched, remove any comments and add to set
if str_exactps_remote:
    exactps_remote.update(x for x in map(str.strip, str_exactps_remote.splitlines()) if x and x[:1] != '#')
    print(f'[i] {len(exactps_remote)} exactps collected from {url_exactps_remote}')
else:
    print('[i] No remote exactps were found.')
    exit(1)

if db_exists:
    # Create a DB connection
    print(f'[i] Connecting to {path_pihole_db}')

    try:
        conn = sqlite3.connect(path_pihole_db)
    except sqlite3.Error as e:
        print(e)
        exit(1)

    # Create a cursor object
    c = conn.cursor()

    # Identifying slyfox1186 exactps
    print("[i] Removing slyfox1186's exactps")
    c.executemany('DELETE FROM domainlist '
                  'WHERE type = 1 '
                  'AND (domain in (?) OR comment = ?)',
                  [(x, install_comment) for x in exactps_remote])

    conn.commit()

    print('[i] Restarting Pi-hole')
    subprocess.run(cmd_restart, stdout=subprocess.DEVNULL)

    # Prepare final result
    print('[i] Done - Please see your installed exactps below\n')

    c.execute('Select domain FROM domainlist WHERE type = 1')
    final_results = c.fetchall()
    exactps_local.update(x[0] for x in final_results)

    print(*sorted(exactps_local), sep='\n')

    conn.close()

else:
    # If exact.list exists and is not empty
    # Read it and add to a set
    if os.path.isfile(path_legacy_exact) and os.path.getsize(path_legacy_exact) > 0:
        print('[i] Collecting existing entries from exact.list')
        with open(path_legacy_exact, 'r') as fRead:
            exactps_local.update(x for x in map(str.strip, fRead) if x and x[:1] != '#')

    # If the local exactp set is not empty
    if exactps_local:
        print(f'[i] {len(exactps_local)} existing exactps identified')
        # If we have a record of the previous legacy install
        if os.path.isfile(path_legacy_slyfox1186_exact) and os.path.getsize(path_legacy_slyfox1186_exact) > 0:
            print('[i] Existing slyfox1186-exact install identified')
            with open(path_legacy_slyfox1186_exact, 'r') as fOpen:
                exactps_legacy_slyfox1186.update(x for x in map(str.strip, fOpen) if x and x[:1] != '#')

                if exactps_legacy_slyfox1186:
                    print(f'[i] Removing exactps found in {path_legacy_slyfox1186_exact}')
                    exactps_local.difference_update(exactps_legacy_slyfox1186)

            # Remove slyfox1186-exact.list as it will no longer be required
            os.remove(path_legacy_slyfox1186_exact)
        else:
            print('[i] Removing exactps that match the remote repo')
            exactps_local.difference_update(exactps_remote)

    # Output to exact.list
    print(f'[i] Outputting {len(exactps_local)} exactps to {path_legacy_exact}')
    with open(path_legacy_exact, 'w') as fWrite:
        for line in sorted(exactps_local):
            fWrite.write(f'{line}\n')

    print('[i] Restarting Pi-hole')
    subprocess.run(cmd_restart, stdout=subprocess.DEVNULL)

    # Prepare final result
    print('[i] Done - Please see your installed exactps below\n')
    with open(path_legacy_exact, 'r') as fOpen:
        for line in fOpen:
            print(line, end='')
