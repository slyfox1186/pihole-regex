## RegEx with Exact Filters for Pi-hole's (FTLDNS) Ad Blocker

The *purpose* of this repository is to compliment your existing **Pi-hole** ***(FTLDNS)*** filters using ***powerful regular expressions*** **AKA** ***[RegEx]*** that cover a **broad range of domains** ***in one go*** while also including a **customized list** of **Exact filters**.

* Made for: **Pi-hole (FTLDNS) v5+**
* Required: **Python3 v3.6+**

* To enter commands use: **Terminal**
* If you're not using the **PC** that's running **Pi-hole** you can use
    - **PuTTY:** *Windows*
    - **SSH Client:** *Linux*

## The Filter Lists
  - ***[Exact Blacklist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/blacklist/exact-blacklist.txt)***
  - ***[Exact Whitelist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/whitelist/exact-whitelist.txt)***
  - ***[RegEx Blacklist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/blacklist/regex-blacklist.txt)***
  - ***[RegEx Whitelist](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains/whitelist/regex-whitelist.txt)***

## User options: [ Add | Remove | Skip ]

* The script will prompt the user to press one of three keys.

```
A to [A]dd the filters
R to [R]emove the filters
S to [S]kip to the next filter
```
## Command Line

* Click the copy button to the right and paste this into a terminal to execute
```
wget -qN - -i https://pihole.optimizethis.net; sudo bash run.sh

```
