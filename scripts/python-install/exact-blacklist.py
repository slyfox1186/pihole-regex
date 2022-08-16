#!/usr/bin/env python3

import os
import argparse
import sqlite3
import subprocess
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import time

today = int(time.time())

def fetch_blacklist_url(url):

    if not url:
        return

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0'}

    try:
        response = urlopen(Request(url, headers=headers))
    except HTTPError as e:
        print('[X] HTTP Error:', e.code, 'whilst Fetching', url)
        print('\n')
        exit(1)
    except URLError as e:
        print('[X] URL Error:', e.reason, 'whilst Fetching', url)
        print('\n')
        exit(1)

    # Read and decode
    response = response.read().decode('UTF-8').replace('\r\n', '\n')

    # If there is data
    if response:
        # Strip leading and trailing blackspace
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
parser.Add_argument('-d', '--dir', type=dir_path, help='optional: Pi-hole etc directory')
parser.Add_argument('-D', '--docker',  action='store_true', help="optional: set if you're using Pi-hole in docker environment")
args = parser.parse_args()

if args.dir:
    pihole_location = args.dir
else:
    pihole_location = r'/etc/pihole'

blacklist_remote_url = 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/domains/blacklist/exact-blacklist.txt'
remote_sql_url = 'https://raw.githubusercontent.com/slyfox1186/pihole.regex/main/domains/blacklist/exact-blacklist.sql'
gravity_blacklist_location = os.path.join(pihole_location, 'blacklist.txt')
gravity_db_location = os.path.join(pihole_location, 'gravity.db')
slyfox1186_blacklist_location = os.path.join(pihole_location, 'slyfox1186-blacklist.txt')

db_exists = False
sqlite_connection = None
cursor = None

blacklist_remote = set()
blacklist_local = set()
blacklist_slyfox1186_local = set()
blacklist_old_slyfox1186 = set()

os.system('clear')
print('\n')
print("This script will download and add domains from the repo to the Pi-hole's Blacklist.")
print('\n')

# Check for pihole path exsists
if os.path.exists(pihole_location):
    print('[i] Pi-hole path exists')
else:
    # print(f'[X] {pihole_location} was not found')
    print("[X] {} was not found" .format(pihole_location))
    print('\n')
    exit(1)

# Check for write access to /etc/pihole
if os.access(pihole_location, os.X_OK | os.W_OK):
    print("[i] Write access to {} verified" .format(pihole_location))
    blacklist_str = fetch_blacklist_url(blacklist_remote_url)
    remote_blacklist_lines = blacklist_str.count('\n')
    remote_blacklist_lines += 1
else:
    print("[X] Write access is not available for {}. Please run as root or other privileged user" .format(
        pihole_location))
    print('\n')
    exit(1)

# Determine whether we are using database or not
if os.path.isfile(gravity_db_location) and os.path.getsize(gravity_db_location) > 0:
    db_exists = True
    print('[i] Pi-Hole Gravity database found')

    remote_sql_str = fetch_blacklist_url(remote_sql_url)
    remote_sql_lines = remote_sql_str.count('\n')
    remote_sql_lines += 1

    if len(remote_sql_str) > 0:
        print("[i] {} domains and {} SQL queries discovered." .format(
            remote_blacklist_lines, remote_sql_lines))
    else:
        print('[X] No remote SQL queries found.')
        print('\n')
        exit(1)
else:
    print('[i] Legacy Pi-hole detected (Version older than 5.0)')

# If domains were Fetched, remove any comments and add to set
if blacklist_str:
    blacklist_remote.update(x for x in map(
        str.strip, blacklist_str.splitlines()) if x and x[:1] != '#')
else:
    print('[X] No remote domains were found.')
    print('\n')
    exit(1)

if db_exists:
    print('[i] Connecting to Gravity.')
    try: # Try to create a database connection
        sqlite_connection = sqlite3.connect(gravity_db_location)
        cursor = sqlite_connection.cursor()
        print('[i] Successfully Connected to Gravity.')
        #
        print('[i] Checking Gravity for domains added by script.')
        # Check Gravity database for domains added by script
        GravityScript_before = cursor.execute(" SELECT * FROM domainlist WHERE type = 1 AND comment LIKE '%SlyEBL%' ")
        # Fetch all matching entries which will create a tuple for us
        GravScript_BeforeTUP = GravityScript_before.fetchall()
        # Number of domains in database from script
        GravScript_BeforeTUPlen = len(GravScript_BeforeTUP)
        print("[i] {} Domains from script in Blacklist already." .format(GravScript_BeforeTUPlen))
        #
        # make `remote_sql_str` a tuple so we can easily compare
        NewblackTUP = remote_sql_str.split('\n')
        # Number of domains that would be added by script
        NewblackListlen = len(NewblackTUP)
        #
        # get domains from NewblackTUP and make an ordered list (a list we can use predictably)
        nW = [None] * NewblackListlen
        nwl = 0 # keep a count
        NewWL = [None]
        NewblackList = [None] * NewblackListlen
        for NewblackDomain in NewblackTUP: # for each line found domains.sql
            nW[nwl] = NewblackDomain # add line to a controlled list
            RemoveBrace = nW[nwl].replace('(', '') # remove (
            RemoveBraces10 = RemoveBrace.replace(')', '') # remove )
            NewWL = RemoveBraces10.split(', ') # split at commas to create a list
            NewblackList[nwl] = NewWL[1].replace('\'', '') # remove ' from domain and add to list
            # uncomment to see list of sql varables being imported
            # print(nW[nwl])
            # uncomment to see list of domains being imported
            # print(NewblackList[nwl])
            nwl += 1 # count + 1
        # check database for user added exact Blacklisted domains
        print('[i] Checking Gravity for domains added by user that are also in script.')
        # Check Gravity database for exact Blacklisted domains added by user
        User_add = cursor.execute(" SELECT * FROM domainlist WHERE type = 1 AND comment NOT LIKE '%SlyEBL%' ")
        User_AddTUP = User_Add.fetchall()
        User_AddTUPlen = len(User_AddTUP)
        #
        #
        # check if  Blacklisted domains added by user are in script
        User_AddList = [None] * User_AddTUPlen # create a list that has the same size as the tuple is it compared to
        uA = 0 # used to count User added domains in our script
        uagl = False
        for User_AddInGravity in User_AddTUP: # for every Blacklisted domain we found in the database do:
           if User_AddInGravity[2] in NewblackList: # if the domain we found added by user IS IN our New list count it
               User_AddList[uA] = User_AddInGravity[2] # add the domain we found to the list we created
               uagl = True
               uA += 1 # bump count if domain added (starts @ 0)
        #
        uA -= 1 # subtract 1 so the count doesn't put us out of range
        InGravityUser_AddListCount = uA # save our count here so we know how many we have later
        # Make us aware of User added domains that are also in our script
        if uagl == True: # if we found user added domains from our list in Gravity do:
            print('[i] {} domain(s) added by the user that would be added by script.\n' .format(InGravityUser_AddListCount+1)) # we have to add 1 for humans cause count starts @ 0
            a = 0
            while uA >= 0: # remember that counter now we make it go backwards to 0
                a += 1 # counter for number output to screen
                print('    {}. {}' .format(a, User_AddList[uA])) # Show us what we found
                uA -= 1 # go backwards
        else: # If we don't find any
            InGravityUser_AddListCount = 0 # make sure this is 0
            print('[i] Found {} domains added by the user that would be added by script.' .format(InGravityUser_AddListCount)) # notify of negative result
        #
        #
        # Check Gravity database for domains added by script that are not in New script
        InGravityNotNewList = [None] * GravScript_BeforeTUPlen # create a list that has the same size as the tuple is it compared to
        GravScript_BeforeList = [None] * GravScript_BeforeTUPlen
        z = 0
        if uagl == True:
            print('\n')
        
        print('[i] Checking Gravity for domains previously added by script that are NOT in New script.')
        ignl = False
        a = 0
        for InGravityNotNew in GravScript_BeforeTUP: # for every domain previously added by script
            GravScript_BeforeList[a] = InGravityNotNew[2] # take domains from Gravity and put them in a list for later
            a += 1
            if not InGravityNotNew[2] in NewblackList: # make sure it is not in New script
               InGravityNotNewList[z] = InGravityNotNew # add not found to list for later
               ignl = True
               z += 1
        #
        z -= 1
        InGravityNotNewListCount = z
        # If In Gravity because of script but NOT in the New list Prompt for removal
        if ignl == True:
            print('[i] {} domain(s) added previously by script that are not in New script.\n' .format(InGravityNotNewListCount+1))
            a = 0
            while z >= 0:
                a += 1
                print('    deleting {}' .format(InGravityNotNewList[z][2]))
                # print all data retrieved from database about domain to be removed
                # print(InGravityNotNewList[z])
                # ability to remove old
                sql_delete = " DELETE FROM domainlist WHERE type = 1 AND id = '{}' "  .format(INgravityNOTnewList[z][0])
                cursor.executescript(sql_delete)
                z -= 1
        # If not keep going
        else:
            InGravityNotNewListCount = 0
            print('[i] Found {} domain(s) added previously by script that are not in script.' .format(InGravityNotNewListCount))
        #
        #
        # Check Gravity database for New domains to be added by script
        InNew_NotGravityList = [None] * NewblackListlen
        w = 0
        if ignl == True:
            print('\n')
        #
        print('[i] Checking script for domains not in Gravity.')
        ilng = False
        for InNew_NotGravity in NewblackList: # for every domain in the New script
            if not InNew_NotGravity in GravScript_BeforeList and not InNew_NotGravity in User_AddList: # make sure it is not in Gravity or added by user
                InNew_NotGravityList[w] = InNew_NotGravity # add domain to list we created
                ilng = True
                w += 1
        #
        w -= 1
        InNew_NotGravityListCount = w
        # If there are domains in New list that are NOT in Gravity
        if ilng == True: # add domains that are missing from New script and not user additions
            print('[i] {} domain(s) NOT in Gravity that are in New script.\n' .format(InNew_NotGravityListCount+1))
            a = 0
            while w >= 0:
                a += 1
                for addNewblackDomain in NewblackList:
                    if addNewblackDomain in InNew_NotGravityList:
                        print('    - adding {}' .format(AddNewblackDomain))
                        # print(AddNewblackDomain)
                        sql_index = NewblackList.index(AddNewblackDomain)
                        # print(sql_index)
                        # print(nW[sql_index])
                        # Ability to add new
                        sql_add = " INSERT OR IGNORE INTO domainlist (type, domain, enabled, comment) VALUES {} "  .format(nW[SQL_Index])
                        cursor.executescript(sql_add)
                        w -= 1
            # Re-Check Gravity database for domains added by script after we update it
            GravityScript_After = cursor.execute(" SELECT * FROM domainlist WHERE type = 1 AND comment LIKE '%SlyEBL%' ")
            # Fetch all matching entries which will create a tuple for us
            GravScript_AfterTUP = GravityScript_After.fetchall()
            # Number of domains in database from script
            GravScript_AfterTUPlen = len(GravScript_AfterTUP)

            gsa = False
            ASG = InNew_NotGravityListCount
            ASGCOUNT = 0
            GravScript_AfterList = [None] * GravScript_AfterTUPlen

            print('[i] Checking Gravity for domains added by other methods.')

            for GravScript_AfterDomain in GravScript_AfterTUP:
                GravScript_AfterList[ASGCOUNT] = GravScript_AfterTUP[ASGCOUNT][2]
                ASGCOUNT += 1

            while ASG >= 0:
                if InNew_NotGravityList[ASG] in GravScript_AfterList:
                    print('    - Found  {} ' .format(InNew_NotGravityList[ASG]))
                    gsa = True
                ASG = ASG - 1

            if gsa == True:
                # All domains are accounted for.
                print('[i] All {} domains to be added by script have been discovered in Gravity.'.format(NewblackListlen))

            else:
                print("\n[i] All {} New domain(s) have not been added to Gravity." .format(InNew_NotGravityListCount+1))

        else: # We should be done now
            # Do Nothing and exit. All domains are accounted for.
            print("[i] All {} domains to be added by script have been discovered in Gravity" .format(NewblackListlen)) 
        # Find total Blacklisted domains (regex)
        total_domains_R = cursor.execute(" SELECT * FROM domainlist WHERE type = 1 ")
        tdr = len(total_domains_R.fetchall())
        # Find total Blacklisted domains (exact)
        total_domains_E = cursor.execute(" SELECT * FROM domainlist WHERE type = 1 ")
        tde = len(total_domains_E.fetchall())
        total_domains = tdr + tde
        print("[i] There are a total of {} domains in your Blacklist (regex({}) & exact({}))" .format(total_domains, tdr, tde))
        sqlite_connection.close()
        print('[i] The connection to the Gravity database has closed.')
        if ilng == True:
            print('[i] Please wait for the Pi-hole server to restart.')
            restart_pihole(args.docker)

    except sqlite3.Error as error:
        print('[X] Failed to insert domains into Gravity database', error)
        print('\n')
        exit(1)

    finally:
        print('\n')
        print('[i] Pi-hole is currently running.')
        print('\n')
        print('[i] Make sure to star this repository to show your support! It helps keep me motivated!')
        print('[i] https://github.com/slyfox1186/pihole.regex')
        print('\n')

else:

    if os.path.isfile(gravity_blacklist_location) and os.path.getsize(gravity_blacklist_location) > 0:
        print('[i] Collecting existing entries from Blacklist.txt')
        with open(gravity_blacklist_location, 'r') as fRead:
            blacklist_local.update(x for x in map(
                str.strip, fRead) if x and x[:1] != '#')

    if blacklist_local:
        print("[i] {} existing Blacklists identified" .format(
            len(blacklist_local)))
        if os.path.isfile(slyfox1186_blacklist_location) and os.path.getsize(slyfox1186_blacklist_location) > 0:
            print('[i] Existing slyfox1186-blacklist install identified.')
            with open(slyfox1186_blacklist_location, 'r') as fOpen:
                blacklist_old_slyfox1186.update(x for x in map(
                    str.strip, fOpen) if x and x[:1] != '#')

                if blacklist_old_slyfox1186:
                    print('[i] Removing previously installed Blacklist')
                    blacklist_local.difference_update(blacklist_old_slyfox1186)

    print("[i] Syncing with {}" .format(blacklist_remote_url))
    blacklist_local.update(blacklist_remote)

    print("[i] Outputting {} domains to {}" .format(
        len(blacklist_local), gravity_blacklist_location))
    with open(gravity_blacklist_location, 'w') as fWrite:
        for line in sorted(blacklist_local):
            fWrite.write("{}\n" .format(line))

    with open(slyfox1186_blacklist_location, 'w') as fWrite:
        for line in sorted(blacklist_remote):
            fWrite.write("{}\n" .format(line))

    print('[i] The Exact Blacklist filters were added to Pi-Hole.\n')
    print('[i] Please wait for the Pi-hole server to restart.')
    restart_pihole(args.docker)
    print('\n')
    print('[i] Pi-hole is currently running.')
    print('\n')
    print('[i] Make sure to star this repository to show your support! It helps keep me motivated!')
    print('[i] https://github.com/slyfox1186/pihole.regex')
    print('\n')
