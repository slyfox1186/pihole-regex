## A collection of *RegEx* and *Exact* filters for use with Pi-hole® v5+ *FTLDNS*

The ***purpose*** of this repository is to compliment your existing **Pi-hole** filters using ***powerful*** regular expressions (**RegEx**) that cover a broad range of domains ***in one go***. Included are an optional customized list of **Exact** filters and the ability to add or remove entries from the **Adlist Group**.

# Updates
### The Adlist script is now solely a python3 and SQL script. It will only do the following.
  1. If an adlist is not found in the pi-hole database and is found in the adlist text file add the domain to the adlist database.
  2. If an adlist is not found in the pi-hole database and is NOT found in the adlist text file then remove it ONLY if it has a comment that begins with the text "SlyADL", otherwise, leave it alone as it was most likely added manually by the user or some other script.
  3. Print the changes being made to the terminal so the user can clearly understand what is happening.
  4. Prompt the user to update the Gravity database if changes were made.
### The exact and regex lists are now solely a python3 and SQL script. They will only do the following.
  1. If a domain is not found in the pi-hole database and is found in the respective SQL file then add the domain to the database.
  2. If a domain is not found in the pi-hole database and is NOT found in the respective SQL file then remove it ONLY if it has a comment that begins with the text "SlyEWL, SlyEBL, SlyRWL, or SlyRBL", otherwise, leave it alone as it was most likely added manually by the user or some other script.
  3. All domains will now process each list consecutively without the need for user interaction. What needs to be added and removed will be according to the respective domain SQL files.
  4. Prompt the user to restart the pi-hole dns resolver.
### All script changes
  1. Prompt the user to update pi-hole if an update is detected.

## Filter Lists

| Script Names | Raw Links |
| :----: | :----: |
| Adlists | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlists.txt) |
| Exact Whitelist | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-whitelist.sql) |
| Exact Blacklist | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/exact-blacklist.sql) |
| RegEx Whitelist | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/regex-whitelist.sql) |
| RegEx Blacklist | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/regex-blacklist.sql) |

## Requirements and other important information
**Made for:** Pi-hole (FTLDNS) v5+
  - Website: [https://pi-hole.net/](https://pi-hole.net/)

### Required Packages
```bash
sudo apt -y install curl python3 sqlite3 wget
```

## If you're *not* on the PC that's running Pi-hole
* **Use your ssh client of choice (examples below)**
  - **[OpenSSH](https://www.openssh.com/)**
  - **[PuTTY](https://www.putty.org/)**
  - **[Termius](https://termius.com/)**

## To execute, run each of the below commands

### RegEx and Exact Lists
```
curl -Lso run.sh https://pihole.optimizethis.net; bash run.sh
```
### Adlists
```
curl -Lso adlist.py https://ad.optimizethis.net; sudo python3 adlist.py
```
