## Pi-hole (FTLDNS): RegEx and Exact filters for networkwide ad blocking

The ***purpose*** of this repository is to compliment your existing **Pi-hole's** filters using ***powerful*** **regular expressions** (**AKA RegEx**) that covers a **broad range of domains** in one go. Included with the RegEx filters are a *customized list* of **Exact filters**.

A ***optional*** script to add or remove entries from Pi-hole's **Adlists** is also included.

## The Filter Lists
  - **[Exact Blacklist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/blacklist/exact-blacklist.txt)**
  - **[Exact Whitelist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/whitelist/exact-whitelist.txt)**
  - **[RegEx Blacklist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/blacklist/regex-blacklist.txt)**
  - **[RegEx Whitelist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/whitelist/regex-whitelist.txt)**
  - **[Adlists](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/adlist/adlists.txt)**

## Requirements and other important information
* **Made for:** Pi-hole (FTLDNS) v5+
* **Required Packages:** Python3 v3.6+
* **Command input:** Terminal

### **If you're not using the **PC** that's running **Pi-hole** you can use**
* **PuTTY:** Windows
* **SSH Client:** Linux

### **To steer the outcome of each script the user will be prompted to press a key to advance their choices**
* **Input examples**
  - **[A]** to ***Add***
  - **[R]** to ***Remove***
  - **[S]** to ***Skip***
  - ***Any set of numbers***

## To execute a script run one of the below commands in terminal

### RegEx and Exact
```
wget -qN - -i https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/urls.txt; sudo bash run.sh

```
### Adlists
```
wget -qN https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/shell-install/adlist.sh; sudo bash adlist.sh

```
