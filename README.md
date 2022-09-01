## A collection of *RegEx* and *Exact* filters for use with Pi-Hole® *FTLDNS*

The *purpose* of this repository is to compliment your existing **Pi-Hole** filters using ***powerful*** regular expressions (**RegEx**) that cover a broad range of domains ***in one go***. Included are an optional customized list of **Exact** filters and the ability to add or remove entries from the **Adlist Group**.

## The filter lists
  - **[Exact Blacklist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/blacklist/exact-blacklist.txt)**
  - **[Exact Whitelist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/whitelist/exact-whitelist.txt)**
  - **[RegEx Blacklist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/blacklist/regex-blacklist.txt)**
  - **[RegEx Whitelist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/whitelist/regex-whitelist.txt)**
  - **[Adlists](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlist/adlists.txt)**

## Requirements and other important information
* **Made for:** Pi-Hole (FTLDNS) v5+
  - Website: [https://pi-hole.net/](https://pi-hole.net/)

* **Required Packages:**
  - **Python3**
    - sudo apt install python3
  - **SQLite3**
    - sudo apt install sqlite3

* **Adlist info:** If you choose to remove the adlist it will remove ***ALL*** of the entries (not just mine).

## If you're *not* on the PC that's running Pi-Hole
* **Use your ssh client of choice (examples below)**
  - **[PuTTY](https://www.putty.org/)**
  - **[OpenSSH](https://www.openssh.com/)**
  - **[Termius](https://termius.com/)**

## **The user will be prompted to press a key to advance their choices**
* **Input examples**
  - **[A]** to ***Add***
  - **[R]** to ***Remove***
  - **[S]** to ***Skip***
  - ***Any number***

## To execute, run one of the below commands

### RegEx and Exact
```
wget -qN - -i https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/urls.txt; sudo bash run.sh

```
### Adlists
```
wget -qN https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/shell-install/adlist.sh; sudo bash adlist.sh

```
