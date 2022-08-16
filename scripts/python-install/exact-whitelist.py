#!/usr/bin/env python3

import os
import argparse
import sqlite3
import subprocess
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import time

today = int(time.time())

def fetch_whitelist_url(url):

    if not url:
        return

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0'}

    try:
        response = urlopen(Request(url, headers=headers))
    except HTTPError as e:
        print('[X] HTTP Error:', e.code, 'whilst fetching', url)
        print('\n')
        print('\n')
        exit(1)
    except URLError as e:
        print('[X] URL Error:', e.reason, 'whilst fetching', url)
        print('\n')
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
        subprocess.call(['pihole', '-g'], stdout=subprocess.DEVNULL)

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir", type=dir_path, help="Optional: Pi-hole /etc directory")
parser.add_argument("-D", "--docker",  action='store_true', help="Optional: Set if you're using Pi-hole in a Docker environment.")
args = parser.parse_args()

if args.dir:
    pihole_location = args.dir
else:
    pihole_location = r'/etc/pihole'

whitelist_remote_url = 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/domains/whitelist/exact-whitelist.txt'
remote_sql_url = 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/domains/whitelist/exact-whitelist.sql'
gravity_whitelist_location = os.path.join(pihole_location, 'whitelist.txt')
gravity_db_location = os.path.join(pihole_location, 'gravity.db')
slyfox1186_whitelist_location = os.path.join(pihole_location, 'slyfox1186-whitelist.txt')

db_exists = False
sqliteConnection = None
cursor = None

whitelist_remote = set()
whitelist_local = set()
whitelist_slyfox1186_local = set()
whitelist_old_slyfox1186 = set()

os.system('clear')
print('\n')
print("Add the Exact Whitelist filters to Gravity's database.")
print('\n')

# Check if the pihole path exists
if os.path.exists(pihole_location):
    print("[i] Pi-hole's path was found.")
else:
    # print(f'[X] {pihole_location} was not found')

    print("[X] {} was not found".format(pihole_location))
    print('\n')
    exit(1)

# Check for write access to /etc/pihole
if os.access(pihole_location, os.X_OK | os.W_OK):
    print("[i] Write access to {} verified." .format(pihole_location))
    whitelist_str = fetch_whitelist_url(whitelist_remote_url)
    remote_whitelist_lines = whitelist_str.count('\n')
    remote_whitelist_lines += 1
else:
    print("[X] Write access is not available for {}. Please run the script as a privileged user." .format(
        pihole_location))
    print('\n')
    print('\n')
    exit(1)

# Determine whether we are using database or not
if os.path.isfile(gravity_db_location) and os.path.getsize(gravity_db_location) > 0:
    db_exists = True
    print('[i] The Gravity database was found.')

    remote_sql_str = fetch_whitelist_url(remote_sql_url)
    remote_sql_lines = remote_sql_str.count('\n')
    remote_sql_lines += 1

    if len(remote_sql_str) > 0:
        print("[i] {} domains and {} SQL queries discovered." .format(
            remote_whitelist_lines, remote_sql_lines))
    else:
        print('[X] No remote SQL queries found.')
        print('\n')
        print('\n')
        exit(1)
else:
    print('[i] Legacy Pi-hole detected (version older than 5.0).')

# If domains were fetched, remove any comments and add to set
if whitelist_str:
    whitelist_remote.update(x for x in map(
        str.strip, whitelist_str.splitlines()) if x and x[:1] != '#')
else:
    print('[X] No remote domains were found.')
    print('\n')
    exit(1)

if db_exists:
    # Create a database connection
    print("[i] Establishing a connection to Gravity's database.")

    try: # Try to create a database connection
        sqliteConnection = sqlite3.connect(gravity_db_location)
        cursor = sqliteConnection.cursor()
        print('[i] Successfully Connected to Gravity.')
        #
        print('[i] Checking Gravity for domains added by script.')
        # Check Gravity database for domains added by script
        gravityScript_before = cursor.execute(" SELECT * FROM domainlist WHERE type = 0 AND comment LIKE '%SlyEWL%' ")
        # Fetch all matching entries which will create a tuple for us
        gravScriptBeforeTUP = gravityScript_before.fetchall()
        # Number of domains in database from script
        gravScriptBeforeTUPlen = len(gravScriptBeforeTUP)
        print('[i] {} domains from the script are already in the whitelist.' .format(gravScriptBeforeTUPlen))
        #
        # Make `remote_sql_str` a tuple so we can easily compare
        newWhiteTUP = remote_sql_str.split('\n')
        # Number of domains that would be added by script
        newWhiteListlen = len(newWhiteTUP)
        #
        # Get domains from newWhiteTUP and make an ordered list (a list we can use predictably)
        nW = [None] * newWhiteListlen
        nwl = 0 # keep a count
        newWL = [None]
        newWhiteList = [None] * newWhiteListlen
        for newWhiteDomain in newWhiteTUP: # For each line found domains.sql
            nW[nwl] = newWhiteDomain # Add line to a controlled list
            removeBrace = nW[nwl].replace('(', '') # Remove (
            removeBraces10 = removeBrace.replace(')', '') # Remove )
            newWL = removeBraces10.split(', ') # Split at commas to create a list
            newWhiteList[nwl] = newWL[1].replace('\'', '') # Remove ' from domain and add to list
            # Uncomment to see list of sql varables being imported
            print(nW[nwl])
            # Uncomment to see list of domains being imported
            print(newWhiteList[nwl])
            nwl += 1 # count + 1
        # Check database for user added exact whitelisted domains
        print('[i] Checking Gravity for domains added by a user earlier that are also in the script.')
        # Check Gravity database for exact whitelisted domains added by user
        user_add = cursor.execute(" SELECT * FROM domainlist WHERE type = 0 AND comment NOT LIKE '%SlyEWL%' ")
        userAddTUP = user_add.fetchall()
        userAddTUPlen = len(userAddTUP)
        #
        #
        # Check if whitelisted domains added by user are in script
        userAddList = [None] * userAddTUPlen # Create a list that has the same size as the tuple is it compared to
        uA = 0 # Used to count User Added domains in our script
        uagl = False
        for userAddINgravity in userAddTUP: # For every whitelisted domain we found in the database do:
           if userAddINgravity[2] in newWhiteList: # If the domain we found added by user IS IN our new list count it
               userAddList[uA] = userAddINgravity[2] # Add the domain we found to the list we created
               uagl = True
               uA += 1 # Bump count if domain added (starts @ 0)
        #
        uA -= 1 # Subtract 1 so the count doesn't put us out of range
        INgravityUSERaddListCount = uA # Save our count here so we know how many we have later
        # Make us aware of User Added domains that are also in our script
        if uagl == True: # If we found user added domains from our list in gravity do:
            print('[i] {} domain(s) added by the user that would be added by script.\n' .format(INgravityUSERaddListCount+1)) # We have to add 1 for humans cause count starts @ 0
            a = 0
            while uA >= 0: # Remember that counter now we make it go backwards to 0
                a += 1 # Counter for number output to screen
                print('    {}. {}' .format(a, userAddList[uA])) # Show us what we found
                uA -= 1 # Go backwards
        else: # If we don't find any
            INgravityUSERaddListCount = 0 # Make sure this is 0
            print('[i] Found {} domains added by a user that will be added by the script.' .format(INgravityUSERaddListCount)) # Notify of negative result
        #
        #
        # Check Gravity database for domains added by script that are not in new script
        INgravityNOTnewList = [None] * gravScriptBeforeTUPlen # Create a list that has the same size as the tuple is it compared to
        gravScriptBeforeList = [None] * gravScriptBeforeTUPlen
        z = 0
        if uagl == True:
            print('\n')

        print('[i] Checking Gravity for domains previously added by script that are NOT in new script.')
        ignl = False
        a = 0
        for INgravityNOTnew in gravScriptBeforeTUP: # For every domain previously added by script
            gravScriptBeforeList[a] = INgravityNOTnew[2] # Take domains from gravity and put them in a list for later
            a += 1
            if not INgravityNOTnew[2] in newWhiteList: # Make sure it is not in new script
               INgravityNOTnewList[z] = INgravityNOTnew # Add not found to list for later
               ignl = True
               z += 1
        #
        z -= 1
        INgravityNOTnewListCount = z
        # If in Gravity because of script but NOT in the new list Prompt for removal
        if ignl == True:
            print('[i] {} domain(s) added previously by script that are not in new script.\n' .format(INgravityNOTnewListCount+1))
            a = 0
            while z >= 0:
                a += 1
                print('    deleting {}' .format(INgravityNOTnewList[z][2]))
                # Print all data retrieved from database about domain to be removed
                print(INgravityNOTnewList[z])
                # Ability to remove old
                sql_delete = " DELETE FROM domainlist WHERE type = 0 AND id = '{}' "  .format(INgravityNOTnewList[z][0])
                cursor.executescript(sql_delete)
                z -= 1
        # If not keep going
        else:
            INgravityNOTnewListCount = 0
            print('[i] Found {} domains added previously by the script that are not in the script.' .format(INgravityNOTnewListCount))
        #
        #
        # Check Gravity database for new domains to be added by script
        INnewNOTgravityList = [None] * newWhiteListlen
        w = 0
        if ignl == True:
            print('\n')
        #
        print('[i] Checking script for domains not in Gravity.')
        ilng = False
        for INnewNOTgravity in newWhiteList: # For every domain in the new script
            if not INnewNOTgravity in gravScriptBeforeList and not INnewNOTgravity in userAddList: # Make sure it is not in gravity or added by user
                INnewNOTgravityList[w] = INnewNOTgravity # Add domain to list we created
                ilng = True
                w += 1
        #
        w -= 1
        INnewNOTgravityListCount = w
        # If there are domains in new list that are NOT in Gravity
        if ilng == True: # Add domains that are missing from new script and not user additions
            print("[i] {} domain's NOT in Gravity that are in the new scripts.\n" .format(INnewNOTgravityListCount+1))
            a = 0
            while w >= 0:
                a += 1
                for addNewWhiteDomain in newWhiteList:
                    if addNewWhiteDomain in INnewNOTgravityList:
                        # print('    - Adding {}' .format(addNewWhiteDomain))
                        # print(addNewWhiteDomain)
                        sql_index = newWhiteList.index(addNewWhiteDomain)
                        # print(sql_index)
                        # print(nW[sql_index])
                        # Ability to add new
                        sql_add = " INSERT OR IGNORE INTO domainlist (type, domain, enabled, comment) VALUES {} "  .format(nW[sql_index])
                        cursor.executescript(sql_add)
                        w -= 1
            # Re-Check Gravity database for domains added by script after we update it
            gravityScript_after = cursor.execute(" SELECT * FROM domainlist WHERE type = 0 AND comment LIKE '%SlyEWL%' ")
            # Fetch all matching entries which will create a tuple for us
            gravScriptAfterTUP = gravityScript_after.fetchall()
            # Number of domains in database from script
            gravScriptAfterTUPlen = len(gravScriptAfterTUP)

            gsa = False
            ASG = INnewNOTgravityListCount
            ASGCOUNT = 0
            gravScriptAfterList = [None] * gravScriptAfterTUPlen

            print('\n[i] Checking Gravity for newly added domains.\n')

            for gravScriptAfterDomain in gravScriptAfterTUP:
                gravScriptAfterList[ASGCOUNT] = gravScriptAfterTUP[ASGCOUNT][2]
                ASGCOUNT += 1

            while ASG >= 0:
                if INnewNOTgravityList[ASG] in gravScriptAfterList:
                    print('    - Found  {} ' .format(INnewNOTgravityList[ASG]))
                    gsa = True
                ASG = ASG - 1

            if gsa == True:
                # All domains are accounted for.
                print("\n[i] All {} missing domains were added to Gravity's database." .format(newWhiteListlen))

            else:
                print("\n[i] All {} new domains were removed from Gravity's database." .format(INnewNOTgravityListCount+1))

        else: # We should be done now
            # Do nothing and exit. All domains are accounted for.
            print("[i] All {} domains to be added by script have been discovered in Gravity." .format(newWhiteListlen))
        # Find total whitelisted domains (regex)
        total_domains_R = cursor.execute(" SELECT * FROM domainlist WHERE type = 2 ")
        tdr = len(total_domains_R.fetchall())
        # Find total whitelisted domains (exact)
        total_domains_E = cursor.execute(" SELECT * FROM domainlist WHERE type = 0 ")
        tde = len(total_domains_E.fetchall())
        total_domains = tdr + tde
        print("[i] There are a total of {} domains in your whitelist (regex({}) & exact({}))." .format(total_domains, tdr, tde))
        sqliteConnection.close()
        print("[i] The connection to the Gravity database has closed.")
        time.sleep(2)
        if ilng == True:
            print('[i] Please wait for the Pi-hole server to restart.')
            restart_pihole(args.docker)

    except sqlite3.Error as error:
        print("[X] Failed to insert domains into Gravity's database.", error)
        print('\n')
        exit(1)

    finally:
        print('[i] Pi-hole is currently running.')
        print('\n')
        print('[i] Make sure to star this repository to show your support! It helps keep me motivated!')
        print('[i] https://github.com/slyfox1186/pihole.regex')
        print('\n')

else:

    if os.path.isfile(gravity_whitelist_location) and os.path.getsize(gravity_whitelist_location) > 0:
        print('[i] Collecting existing entries from the file whitelist.txt.')
        with open(gravity_whitelist_location, 'r') as fRead:
            whitelist_local.update(x for x in map(
                str.strip, fRead) if x and x[:1] != '#')

    if whitelist_local:
        print("[i] The script has located {} existing whitelisted domains." .format(
            len(whitelist_local)))

        if os.path.isfile(slyfox1186_whitelist_location) and os.path.getsize(slyfox1186_whitelist_location) > 0:
            print('[i] Existing slyfox1186-whitelist installation found.')
            with open(slyfox1186_whitelist_location, 'r') as fOpen:
                whitelist_old_slyfox1186.update(x for x in map(
                    str.strip, fOpen) if x and x[:1] != '#')

                if whitelist_old_slyfox1186:
                    print('[i] Removing previously installed whitelist.')
                    whitelist_local.difference_update(whitelist_old_slyfox1186)

    print("[i] Syncing with {}." .format(whitelist_remote_url))
    whitelist_local.update(whitelist_remote)

    print("[i] Outputting {} domains to {}." .format(
        len(whitelist_local), gravity_whitelist_location))
    with open(gravity_whitelist_location, 'w') as fWrite:
        for line in sorted(whitelist_local):
            fWrite.write("{}\n".format(line))

    with open(slyfox1186_whitelist_location, 'w') as fWrite:
        for line in sorted(whitelist_remote):
            fWrite.write("{}\n".format(line))

    print('[i] Please wait for the Pi-hole server to restart.')
    restart_pihole(args.docker)
    print('[i] Pi-hole is currently running.')
    print('\n')
    print('[i] Make sure to star this repository to show your support! It helps keep me motivated!')
    print('[i] https://github.com/slyfox1186/pihole.regex')
    print('\n')
