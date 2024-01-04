## A collection of *RegEx* and *Exact* filters for use with Pi-hole® v5+ *FTLDNS*

The ***purpose*** of this repository is to compliment your existing **Pi-hole** filters using ***powerful*** regular expressions (**RegEx**) that cover a broad range of domains ***in one go***. Included are an optional customized list of **Exact** filters and the ability to add or remove entries from the **Adlist Group**.

# Updates
### The Adlist script is now solely a python3 script. It will only do the following.
  1. If an adlist is not found in the pi-hole database and is found in the adlist text file add the domain to the adlist database.
  2. If an adlist is not found in the pi-hole database and is NOT found in the adlist text file then remove it ONLY if it has a comment that begins with the text "SlyADL", otherwise, leave it alone as it was most likely added manually by the user or some other script.
  3. Print the changes being made to the terminal so the user can clearly understand what is happening.
  4. Prompt the user to update the Gravity database if changes were made.

## Filter Lists

| Script Names | Raw Links |
| :----: | :----: |
| Adlists | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlist/adlists.txt) |
| Exact Blacklist | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/blacklist/exact-blacklist.txt) |
| Exact Whitelist | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/whitelist/exact-whitelist.txt) |
| RegEx Blacklist | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/blacklist/regex-blacklist.txt) |
| RegEx Whitelist | [Link](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/whitelist/regex-whitelist.txt) |

## Requirements and other important information
**Made for:** Pi-hole (FTLDNS) v5+
  - Website: [https://pi-hole.net/](https://pi-hole.net/)

### Required Packages
```bash
sudo apt -y install curl python3 sqlite3 wget
```

### Adlist info
  - If you choose the `remove adlists` option it should *only* affect the lists added by this script.


## If you're *not* on the PC that's running Pi-hole
* **Use your ssh client of choice (examples below)**
  - **[OpenSSH](https://www.openssh.com/)**
  - **[PuTTY](https://www.putty.org/)**
  - **[Termius](https://termius.com/)**

## **The user will be prompted to press a key to advance their choices**
* **Input examples**
  - **[A]** to ***Add***
  - **[R]** to ***Remove***
  - **[S]** to ***Skip***
  - ***Any number***

## To execute, run one of the below commands

### RegEx and Exact Lists
```
wget -qN - -i https://pi.optimizethis.net; sudo bash run.sh
```
### Adlists
```
curl -Lso adlist.py https://ad.optimizethis.net; sudo python3 adlist.py
```
