## RegEx with Exact Filters for Pi-hole's (FTLDNS) Ad Blocker

The ***purpose of this repository*** is to ***compliment*** your existing **Pi-hole DNS filters** using ***powerful regular expressions*** that can cover a broad range of domains in one go with a customized list of **exact filters** included.

* **Filters made for:** ***Pi-hole (FTLDNS) v5+***
* **Required:** ***Python3 v3.6+***

* **Enter commands using a** ***terminal***
  * If you're not alread on the PC that's running the Pi-hole server
    - You can use
        - **PuTTY (for Windows)**
        - **SSH Client of choice**

* **The Filter Lists**
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
