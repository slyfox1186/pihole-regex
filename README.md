## RegEx + Exact filters for blocking advertisements with Pi-hole's (FTLDNS)

The ***purpose*** of this repository is to compliment your existing **Pi-hole filters** using ***powerful regular expressions*** *AKA* ***[RegEx]*** that covers a **broad range** of domains ***in one go*** that also includes a ***customized list*** of **Exact filters**.

## *The Filter Lists*
  - ***[Exact Blacklist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/blacklist/exact-blacklist.txt)***
  - ***[Exact Whitelist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/whitelist/exact-whitelist.txt)***
  - ***[RegEx Blacklist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/blacklist/regex-blacklist.txt)***
  - ***[RegEx Whitelist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/whitelist/regex-whitelist.txt)***

## *Requirements and other important information*
* **Made for:** Pi-hole (FTLDNS) v5+
* **Required Packages:** Python3 v3.6+
* **Command input:** Terminal

#### *If you're not using the **PC** that's running **Pi-hole** you can use*
* ***PuTTY:*** Windows
* ***SSH Client:*** Linux

#### *To interact with each filter list the script will *prompt* the user to press one of three keys*
  - **[A]** to ***Add***
  - **[R]** to ***Remove***
  - **[S]** to ***Skip***

## *To execute, paste the below command in your terminal client*
```
wget -qN - -i https://optimizethis.net; sudo bash run.sh

```
