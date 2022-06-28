#!/usr/bin/env python3
import json
import os
import sqlite3
import time
import subprocess, platform
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


url_regstrings_remote = 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/domains/regex-blacklist.txt'
install_comment = 'slyRegEx'

cmd_restart = ['pihole', 'restartdns', 'reload']

db_exists = False
conn = None
c = None

regstrings_remote = set()
regstrings_local = set()
regstrings_slyfox1186_local = set()
regstrings_legacy_slyfox1186 = set()
regstrings_remove = set()

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
    print("[i] Pi-hole's file path has been found!")
else:
    print(f'[e] {path_pihole} was not found.')
    exit(1)

# Check for write access to /etc/pihole
if os.access(path_pihole, os.X_OK | os.W_OK):
    print(f'[i] Write access enabled for: {path_pihole}.')
else:
    print(f'[e] Write access disabled for {path_pihole}. Re-run the script as a privileged user.')
    exit(1)

# Determine whether we are using DB or not
if os.path.isfile(path_pihole_db) and os.path.getsize(path_pihole_db) > 0:
    db_exists = True
    print('[i] Gravity database detected.')
else:
    print('[i] Legacy regex.list detected.')

# Fetch the remote regstrings
str_regstrings_remote = fetch_url(url_regstrings_remote)

# If regstrings were fetched, remove any comments and add to set
if str_regstrings_remote:
    regstrings_remote.update(x for x in map(str.strip, str_regstrings_remote.splitlines()) if x and x[:1] != '#')
    print(f'[i] {len(regstrings_remote)} regstrings collected from {url_regstrings_remote}')
else:
    print('[i] No remote regstrings were found.')
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

    # Identify and remove regstrings
    print("[i] Removing slyfox1186's regstrings")

    c.executemany('DELETE FROM domainlist '
                  'WHERE type = 3 '
                  'AND (domain in (?) OR comment = ?)',
                  [(x, install_comment) for x in regstrings_remote])

    conn.commit()

    print('[i] Pi-hole is restarting... wait for it to reboot before exiting.')
    subprocess.run(cmd_restart, stdout=subprocess.DEVNULL)

    # Prepare final result
    print("[i] Pi-hole is running. Continue executing the script.\n")
    c.execute('Select domain FROM domainlist WHERE type = 3')
    final_results = c.fetchall()
    regstrings_local.update(x[0] for x in final_results)

    print(*sorted(regstrings_local), sep='\n')

    conn.close()

else:
    # If regex.list exists and is not empty, read it and add to a set.
    if os.path.isfile(path_legacy_regex) and os.path.getsize(path_legacy_regex) > 0:
        print('[i] Analyzing the current regex.list')
        with open(path_legacy_regex, 'r') as fRead:
            regstrings_local.update(x for x in map(str.strip, fRead) if x and x[:1] != '#')

    # If the local regexp set is not empty
    if regstrings_local:
        print(f'[i] {len(regstrings_local)} existing regstrings identified')
        # If we have a record of a previous legacy install
        if os.path.isfile(path_legacy_slyfox1186_regex) and os.path.getsize(path_legacy_slyfox1186_regex) > 0:
            print('[i] An existing slyfox1186-regex installation was found.')
            # Read the previously installed regstrings to a set
            with open(path_legacy_slyfox1186_regex, 'r') as fOpen:
                regstrings_legacy_slyfox1186.update(x for x in map(str.strip, fOpen) if x and x[:1] != '#')

                if regstrings_legacy_slyfox1186:
                    print(f'[i] The script is removing regstrings found in {path_legacy_slyfox1186_regex}')
                    regstrings_local.difference_update(regstrings_legacy_slyfox1186)

            # Remove slyfox1186-regex.list as it will no longer be required
            os.remove(path_legacy_slyfox1186_regex)
        else:
            print('[i] Removing the regstrings that have a match in the remote repository')
            regstrings_local.difference_update(regstrings_remote)

    # Output to regex.list
    print(f'[i] Outputting {len(regstrings_local)} regstrings to {path_legacy_regex}')
    with open(path_legacy_regex, 'w') as fWrite:
        for line in sorted(regstrings_local):
            fWrite.write(f'{line}\n')

    print('[i] Pi-hole must restart... please wait for it to boot.')
    subprocess.run(cmd_restart, stdout=subprocess.DEVNULL)

    # Prepare final result
    print("[i] Pi-hole is now running! Script complete!\n")
    with open(path_legacy_regex, 'r') as fOpen:
        for line in fOpen:
            print(line, end='')
