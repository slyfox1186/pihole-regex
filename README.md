## A collection of *RegEx* and *Exact* filters for use with Pi-hole® v5+ *FTLDNS*

The ***purpose*** of this repository is to compliment your existing **Pi-hole** filters using ***powerful*** regular expressions (**RegEx**) that cover a broad range of domains ***in one go***. Included are an optional customized list of **Exact** filters and the ability to add or remove entries from the **Adlist Group**.

#### Major Updates: A series of major tweaking was performed from 02.01.23-02.04.23
  - **Regarding the Adlists:**
1. Using the wonderful pihole_adlist_tool I **cut out almost 75% of the total domains blocked** due to the **extremely low hit count over the last 2 months** (of very active internet use in my household). The domains in the adlist that are no longer there produced a maximum of **1 hit each** and had a max total **unique domain coverage of 4** compared to the **hundreds of unique domains** that the other adlists registered.

  - **Regarding the Exact & RegEx lists: The following was modified:**

1. Duplicate entries that were already covered by the adlists were removed.
2. Domains that shared likeness were put into the RegEx lists to free up the total length of the Exact lists (tested and working).
3. My own white and blacklist entries were added with the ability to bypass video ads on yahoo.com and serverly cut back video ads on twitch.tv as well.

## The filter lists
  - **[Adlist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlist/adlists.txt)**
  - **[Exact Blacklist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/blacklist/exact-blacklist.txt)**
  - **[Exact Whitelist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/whitelist/exact-whitelist.txt)**
  - **[RegEx Blacklist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/blacklist/regex-blacklist.txt)**
  - **[RegEx Whitelist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/whitelist/regex-whitelist.txt)**
  
## Requirements and other important information
* **Made for:** Pi-hole (FTLDNS) v5+
  - Website: [https://pi-hole.net/](https://pi-hole.net/)

* **Required Packages:**
  - **Python3**
    - sudo apt install python3
  - **SQLite3**
    - sudo apt install sqlite3

* **Adlist info:** If you choose the "remove adlists" option it should only affect the lists added by this script.

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

### RegEx and Exact
```
wget -qN - -i https://pi.optimizethis.net; sudo bash run.sh
```
### Adlists
```
wget -qO adlist.sh https://adlist.optimizethis.net; sudo bash adlist.sh
```
