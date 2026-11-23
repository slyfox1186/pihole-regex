# Domain list notes: sources and evidence

This page shows why each entry in `domains/` is allowed or blocked, and the sources behind its description.

- The description under each heading is the comment `pi.py` stores in Pi-hole for that entry. Adlist descriptions
  appear only here and in `adlists.txt`.
- Each entry has a table of evidence: what it shows, the evidence itself (quotes are copied word for word), and where
  it comes from.
- A "Status" line marks anything that is still unproven.

Checked on 2026-11-13, 2026-11-14, 2026-11-21 and 2026-11-22. Web pages were fetched without JavaScript and every
quote was confirmed on the live page that day. If a quote is no longer on a page, the page changed after that date.

## Contents

- [How the evidence was gathered](#how-the-evidence-was-gathered)
- [Change history](#change-history)
- [Open questions](#open-questions)
- [Exact allowlist: exact-whitelist.sql (282 entries)](#exact-allowlist-exact-whitelistsql-282-entries)
- [Exact blocklist: exact-blacklist.sql (20 entries)](#exact-blocklist-exact-blacklistsql-20-entries)
- [RegEx allowlist: regex-whitelist.sql (83 entries)](#regex-allowlist-regex-whitelistsql-83-entries)
- [RegEx blocklist: regex-blacklist.sql (27 entries)](#regex-blocklist-regex-blacklistsql-27-entries)
- [Adlists: adlists.txt (32 lists)](#adlists-adliststxt-32-lists)

## How the evidence was gathered

- DNS: a local recursive resolver (unbound), cross-checked against 1.1.1.1.
- TLS certificates: the organization field of a publicly trusted certificate identifies the operator; a domain-validated
  certificate (no organization) proves only control of the name and is not used as proof of ownership.
- Regex behavior: tested with Pi-hole's own engine (`pihole-FTL regex-test`), not a generic regex library.
- Blocklist membership: the maintainer's Pi-hole gravity database, the archived Block List Project lists and mmotti's
  original regex list.
- Lookups: the maintainer's Pi-hole query log since 2026-11-12, reported by device type only.
- Vendor and list-maintainer documents: Microsoft Learn, Apple's network requirements page, Pi-hole's forum list of
  commonly allowed domains, anudeep's allowlists, Perflyst's Smart TV lists, HaGeZi issues and others, each linked.
- The maintainer's own earlier notes count only as the maintainer's report, cited by the commit that added them.

A clause in a note stays only if a source below supports it. A role that could only be guessed from a host's name is
left out. Where the purpose of a host could not be proven, the note says so. DNS and corpus results are dated
observations: a name that returned NXDOMAIN may come back, and a rule with no current match may match new names.


## Change history

Newest first. Each change names the evidence behind it.

### 2026-11-22

Every entry in the four `.sql` lists was checked with `pihole -q` on Pi-hole v6 (FTL v6.9) right after a gravity update.
`pihole -q` also reports Adblock-style `||example.com^` lines for subdomains. A block entry counted as covered only when
an adlist in `adlists.txt` blocks it (the StevenBlack list that Pi-hole installs by default was not counted). A RegEx
block rule counted as covered only when the adlists block every name it can match, tested with a random subdomain of
each domain the rule names.

- Exact blocklist: removed `samsungcloudsolution.com`, `fkp`, `notice`, `noticecdn`, `oempprd`, `prov`, `sas` and
  `vdterms.samsungcloudsolution.com` (Perflyst's Smart TV list blocks all eight) and `snap.licdn.com` (AdAway and
  hostsVN block it).
- RegEx blocklist: the ViperSoftX rule now lists only the 11 of its 50 names whose subdomains no adlist blocks; HaGeZi
  Threat Intelligence Feeds blocks the other 39 with all subdomains. No other rule is fully covered: the lists block
  the bare Samsung, LG and Spotify names that some rules target, but not their subdomains, and the general rules
  (`ads`, `analytics`, `stats` and the like) match names no list contains.
- Exact allowlist: stopped allowing five tracking hosts that two or more adlists block: `79423.analytics.edgekey.net`
  (Akamai analytics), `appleglobal.102.112.2o7.net` (Adobe analytics), `mparticle.map.fastly.net` (mParticle),
  `romeccs.microsoft.com` (WindowsSpyBlocker and HaGeZi Multi PRO) and `widget-cdn.rpxnow.com`. The other allows that
  two lists block were kept because they keep a service working: Microsoft Defender's `spynet2` and `spynetalt`,
  Samsung's `lcprd1.samsungcloudsolution.net` connection test and LG's `us.rdx2.lgtvsdp.com` cover art.
- Allowlists: 247 exact and 78 RegEx allows unblock nothing today (no adlist, block rule or CNAME target blocks them).
  They were kept on purpose as a safety net for services such as Microsoft sign-in, Apple updates and Xbox Live, in
  case a list adds one of them later.

### 2026-11-21

A review of how the lists in this collection overlap. Each change below either removes a duplicate, removes a rule
that no longer matches anything, or narrows what the collection blocks by default.

Every adlist was downloaded on 2026-11-21 and compared using Pi-hole v6 matching (an Adblock-style
`||example.com^` line also covers subdomains; a hosts line covers only that name). Regexes were compiled and tested with
libtre, the regex library Pi-hole uses. The broad block rules were also tested against the Chrome UX Report list of
the one million most visited sites ([zakird/crux-top-lists](https://github.com/zakird/crux-top-lists)).

- Adlists removed: HaGeZi DGA 30 days, Gambling, URL Shortener and Referral. Together they were about 3.5 million of the
  collection's 6.1 million entries. HaGeZi describes URL Shortener as meant for high-security setups and recommends
  against DNS-level referral blocking, and this repository already allowed the most common shorteners. Anyone who wants
  these lists can still add them from HaGeZi's page.
- Adlists removed: HaGeZi native LG webOS, Roku and TikTok. HaGeZi Multi PRO already contained every domain in them
  except HaGeZi's own test hostname; HaGeZi's FAQ says the native tracker lists are built into each Multi tier.
- Adlists removed: FadeMind UncheckyAds (9 domains, 8 already in HaGeZi Multi PRO) and Perflyst Fire TV, Android tracking
  and Session Replay (last changed 2023-07-13, 2021-11-24 and 2020-05-14). Perflyst's Smart TV list stays.
- The DoH adlist's description now says what the file holds: HaGeZi's encrypted-DNS-only list. HaGeZi publishes the
  VPN and proxy version as a separate file.
- Regex allowlist: the Google rule no longer allows `dns.google.com`, which HaGeZi's encrypted DNS list blocks.
- Regex blocklist: removed 16 rules that matched none of 5.2 million blocklist names or the one million sites (ten
  provider patterns already noted as having no matches, and six domains that did not resolve on 2026-11-13); six rules
  whose domains HaGeZi Multi PRO already blocks with all subdomains; `^adserver-.*\.amazonaws\.com$`, which the
  general adserv rule already covers; and the general `count`, `pixel` and `mads` rules, which matched 20 popular sites
  that no list blocks (for example a government visa site and a bank). `deimos3.apple.com` is no longer blocked: the
  only source found lists it among Apple hosts to allow. The `getbeamer.com` rule was removed because HaGeZi Multi PRO
  already blocks its tracking hosts (`app`, `gmetrics` and `push`); the `gammaentertainment.com` rule was removed
  because its note rested on a single report and no list in the collection blocks it.
- Exact blocklist: removed 16 entries that HaGeZi Multi PRO or HaGeZi's encrypted DNS list already block with all
  subdomains, and 9 CloudFront and rackcdn hosts whose owner could not be confirmed.
- Exact allowlist: notes that named Block List Project now say which list in this collection blocks the domain today,
  or that none does, and the `beacons-npa.gov.uk` note now names HaGeZi Multi PRO. No allow entries were removed.

### 2026-11-14

Five changes were made because the evidence showed a block was breaking a real service, or an allow was no longer safe.
Everything else was kept as it was; the reason for each kept item is in its entry below.

- Unblocked `dxtkri2c61io4.cloudfront.net`. Twitch's Extension Supervisor (`supervisor.ext-twitch.tv`), which Twitch
  says it embeds whenever an extension loads, resolves to this CloudFront host, so blocking it broke every Twitch
  Extension. No evidence showed it serves ads. Source: Twitch's extension documentation and DNS from two resolvers.
- Unblocked `jc9wr0p5rbtco3ibchj4vnjz7z1lr1.ext-twitch.tv`. Twitch hosts every extension under ext-twitch.tv, and no
  source identifies this extension or shows it serves ads; the 2023 'video ads' label had no evidence behind it.
- Allowed `aic/eic/kic.cdplauncher.lgtvcommon.com` and `aic/eic/kic.lgchhomeapp.lgtvcommon.com`. A HaGeZi report
  (#11544, 2026-09-23) found the LG Channels app will not launch when they are blocked, and HaGeZi unblocked them while
  keeping LG's tracking hosts (`cdpbeacon`, `recommend` and others) blocked. Here they were blocked only by this
  repository's `lgtvcommon.com` rule. The tracking hosts stay blocked (checked with pihole-FTL).
- Removed the allow for `pagecdn.io`. On 2026-11-13 the domain served a script that hides from automated browsers
  and sends visitors to an address its server picks, and its library files came back empty even with browser-style
  request headers, so nothing can depend on it.
- Corrected the Apple developer CDN rule to allow `playground-cdn.apple.com` and `playground-assets-cdn.apple.com`,
  the Swift Playground hosts Apple documents; the old rule allowed only `playgrounds-` spellings.

## Open questions

Entries whose purpose is still unverified, or that need a decision.

### Needs a decision (1)

| List | Entry | Note | Why it is open |
| --- | --- | --- | --- |
| Exact blocklist | `qt2-ngfts.lge.com` | LG host sharing ngfts.lge.com's Akamai name - Proposed for blocking in HaGeZi #309; role unverified | It shares ngfts.lge.com's CNAME and 'SDP 2.0' page; blocking may affect LG Content Store images. The old 'file transfer' note had no source. |

### Purpose unverified (42)

| List | Entry | Note | Why it is open |
| --- | --- | --- | --- |
| Exact allowlist | `clients.config.office.net` | Microsoft 365 host under the documented *.office.net endpoint - Exact role unverified | Microsoft documents only the *.office.net wildcard. |
| Exact allowlist | `continuum.dds.microsoft.com` | Microsoft-run host - Purpose unverified (old note said Your Phone notification mirroring, no source found) | No Microsoft document names this host; the Your Phone claim in the old note has no source. |
| Exact allowlist | `emea.ng.msg.teams.microsoft.com` | Microsoft Teams host under the documented *.teams.microsoft.com endpoint - Exact role unverified | Its CNAME name mentions messaging; that is not a documented role. |
| Exact allowlist | `emea.pptservicescast.officeapps.live.com` | Microsoft 365 / Office Online host under the documented *.officeapps.live.com endpoint - Exact role unverified | Microsoft documents only the wildcard. |
| Exact allowlist | `mamservice.manage.microsoft.com` | Microsoft Intune host under the documented *.manage.microsoft.com - Exact role unverified | Microsoft documents only the *.manage.microsoft.com wildcard for Intune. |
| Exact allowlist | `mrs-efz.ms-acdc.office.com` | Microsoft 365 (office.com) service host - Exact role unverified | Only the *.office.com wildcard is documented. |
| Exact allowlist | `mscomajax.vo.msecnd.net` | Microsoft-run host (msecnd.net, required by Microsoft 365) - Exact role unverified | Microsoft documents only the *.msecnd.net wildcard; its root redirects to Microsoft's ASP.NET site. |
| Exact allowlist | `win1710.ipv6.microsoft.com` | Microsoft IPv6 host - Purpose unverified | No source names win1710.ipv6.microsoft.com; win10 and win1910 variants are documented as Teredo server names in Microsoft Q&amp;A, so this is an inference. |
| Exact blocklist | `aic.api.lgtviot.com` | LG webOS TV host (lgtviot.com) - Proposed for blocking in HaGeZi issue #309; role unverified | The old note said 'IoT telemetry'; no source states what the host does. |
| Exact blocklist | `aic.lgtviot.com` | LG webOS TV host (lgtviot.com) - Proposed for blocking in HaGeZi issue #309; role unverified | The old note said 'IoT telemetry'; no source states what the host does. |
| Exact blocklist | `aic.sports.lgtviot.com` | LG webOS TV host (lgtviot.com) - Listed in HaGeZi issue #309; role unverified | Only listed, no function stated. |
| Exact blocklist | `lgtvonline.lge.com` | LG webOS TV online service host - Role unverified | No source describes it. |
| Exact allowlist | `nine.plugins.plexapp.com` | Plex host - Pi-hole users list it for Plex | The source lists it among Plex domains without a role. |
| Exact allowlist | `o1.email.plex.tv` | Plex host - Pi-hole users list it for Plex | The source lists it among Plex domains without a role. |
| Exact allowlist | `o2.sg0.plex.tv` | Plex host - Pi-hole users list it for Plex | The source lists it among Plex domains without a role. |
| Exact allowlist | `tvthemes.plexapp.com.cdn.cloudflare.net` | Plex host - Pi-hole users list it for Plex | The source lists it among Plex domains without a role. |
| Exact allowlist | `api.gitkraken.com` | GitKraken host (gitkraken.com) | The original line called it 'GitHub - Advanced Git CLI Program'; its role is unverified. |
| Exact allowlist | `api.termius.com` | Termius SSH client host (redirects to termius.com) | The old note said it is required to sign in; not verified. |
| Exact allowlist | `gateway.cname.ustclug.org` | gateway.cname.ustclug.org - Role unverified | Kept from the 2022 'crucial CDN' set; nothing documents what points here. |
| Exact allowlist | `dualstack.osff.map.fastly.net` | Fastly host (map.fastly.net) - Which site uses it is unverified | No current CNAME in the lists points here; kept from the 2022 'crucial CDN' set. |
| Exact allowlist | `objects.githubusercontent.com` | GitHub content host | Exact role unverified. |
| Exact allowlist | `googlehosted.l.googleusercontent.com` | Google hosting CNAME target (googleusercontent.com) - Role unverified | No source describes it. |
| Exact allowlist | `edge.gycpi.b.yahoodns.net` | Yahoo-run edge host (yahoodns.net) | The old note said Yahoo breaks without it; not verified. |
| Exact allowlist | `rover.ebay.com` | eBay-run host (rover.ebay.com) | The old note said eBay links pass through it; not verified. |
| Exact allowlist | `static.opensubtitles.org` | OpenSubtitles host | Exact role unverified. |
| Exact allowlist | `yastatic.net` | Yandex-run host (redirects to yandex.ru) | Exact role unverified. |
| Exact blocklist | `events-test.redditmedia.com` | Reddit-run host - Maintainer labeled it an event collector; exact role unverified |  |
| Exact blocklist | `events-test-v2.redditmedia.com` | Reddit-run host - Maintainer labeled it an event collector; exact role unverified |  |
| Exact blocklist | `nevoai-iothub-54-prod.azure-devices.net` | Microsoft Azure IoT Hub instance named 'nevoai' - Customer unverified (old note: LG Smart TV) | Azure IoT Hub names do not show the customer. |
| RegEx allowlist | `(\.\|^)1drv\.ms$` | 1drv.ms and its subdomains | No fetched source names 1drv.ms; the old note said OneDrive short links. |
| RegEx allowlist | `^apps\.bdimg\.(com\|jomodns\.com)$` | apps.bdimg.com and apps.bdimg.jomodns.com | No fetched source; the old note said Baidu static file CDN. |
| RegEx allowlist | `^(winatp-gw-neu\|windows)\.microsoft\.com$` | Microsoft hosts winatp-gw-neu and windows.microsoft.com | Neither is in the cached Microsoft pages; the old note said Defender for Endpoint (Europe). |
| RegEx allowlist | `^(csp\|devicelistenerprod)\.microsoft\.com$` | Microsoft hosts csp and devicelistenerprod.microsoft.com - Purpose unverified | Neither host is in the cached Microsoft endpoint pages. |
| RegEx allowlist | `^d(27xxe7juh1us6\|2gatte9o95jao\|3a3ewgd1iewwz\|3ag4hukkh62yn\|83eunklitikj)\.cloudfront\.net$` | Five CloudFront hosts - The Pi-hole forum lists one for Signal; the rest are unverified | CloudFront certificates do not show customers; only d83eunklitikj (Signal) and d2gatte9o95jao (anudeep whitelist) are sourced. |
| RegEx allowlist | `^europe\.(cp\.wd\|smartscreen(-prod\|))\.microsoft\.com$` | Microsoft hosts europe.cp.wd, europe.smartscreen and europe.smartscreen-prod.microsoft.com | Microsoft documents SmartScreen hosts, but these Europe names are not in the cached pages. |
| RegEx allowlist | `(\.\|^)redd\.it$` | redd.it and its subdomains | No fetched source; the old note said Reddit images, video and short links. |
| RegEx blocklist | `(\.\|^)antivirushub\.com$` | antivirushub.com - Maintainer added it as a 1337x.to redirect domain; it resolved on 2026-11-13 | No source for the 1337x redirect claim; no blocklist in the maintainer's Pi-hole contains it. |
| RegEx blocklist | `(\.\|^)filesupdating\.com$` | filesupdating.com - Maintainer labeled it iTop VPN; it resolved on 2026-11-13 | No source describes it. |
| RegEx blocklist | `(\.\|^)samsungelectronics\.com$` | samsungelectronics.com - Perflyst's Samsung TV rules block it | Perflyst gives no description. |
| RegEx blocklist | `(\.\|^)samsungrm\.net$` | samsungrm.net - Perflyst's Samsung TV rules block it | Perflyst gives no description. |
| RegEx blocklist | `^[a-z0-9]+\.ssm[1-2]?\.internet\.sony\.tv$` | Sony TV hosts under ssm*.internet.sony.tv (the ssm hosts themselves stay reachable) | What the per-device subdomains do is unverified; Perflyst deliberately does not block the ssm hosts. |
| RegEx blocklist | `(\.\|^)tvinteractive\.tv$` | tvinteractive.tv - Perflyst's Smart TV rules block it | Perflyst gives no description; the old note said Vizio Inscape viewing data. |

## Exact allowlist: `exact-whitelist.sql` (282 entries)

### `arc.msn.com`

Microsoft Windows Spotlight - Lock screen images, tips and suggested apps; also listed for the Xbox Series X/S Store app

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Windows Spotlight content endpoint: "Windows Spotlight still tries to deliver new lock screen images and updated content but it fails; suggested apps, Microsoft account notifications, and Windows tips aren't downloaded. TLSv1.2/HTTPS/HTTP arc.msn.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints) |
| Context | Pi-hole users list it for the Xbox Series X/S Store app: the page lists `arc.msn.com` under the heading "Store App on Series X/S" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `clientconfig.passport.net`

Microsoft (passport.net) host - Microsoft lists it as a Windows Autopilot dependency; Pi-hole users list it for Xbox Live

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Listed by Microsoft as a Windows Autopilot dependency: "Windows Autopilot - WNS Dependencies Default Required False clientconfig.passport.net" | [learn.microsoft.com](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints) |
| Context | Pi-hole users list it for Xbox Live: the page lists `clientconfig.passport.net` under the heading "Xbox Live" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `clients.config.office.net`

Microsoft 365 host under the documented *.office.net endpoint - Exact role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | Covered by Microsoft 365's required *.office.net endpoint: "47 Default Required No *.office.net" | [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) |

Status: Purpose unverified. Microsoft documents only the *.office.net wildcard.

### `continuum.dds.microsoft.com`

Microsoft-run host - Purpose unverified (old note said Your Phone notification mirroring, no source found)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Observed | anudeep's whitelist lists it, without a description: "continuum.dds.microsoft.com" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |

Status: Purpose unverified. No Microsoft document names this host; the Your Phone claim in the old note has no source.

### `cp801.prod.do.dsp.mp.microsoft.com`

Microsoft Delivery Optimization host - Microsoft lists *.prod.do.dsp.mp.microsoft.com for Windows Update

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Matches Microsoft's documented Delivery Optimization endpoint *.prod.do.dsp.mp.microsoft.com: "Protocol Endpoint URL TLS 1.2 *.prod.do.dsp.mp.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting) |
| What it does | Delivery Optimization service wildcard: "Delivery Optimization Service *.do.dsp.mp.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints) |

### `geover.prod.do.dsp.mp.microsoft.com`

Microsoft Delivery Optimization host - Microsoft lists *.prod.do.dsp.mp.microsoft.com for Windows Update

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Matches Microsoft's documented Delivery Optimization endpoint *.prod.do.dsp.mp.microsoft.com: "Protocol Endpoint URL TLS 1.2 *.prod.do.dsp.mp.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting) |
| What it does | Delivery Optimization service wildcard: "Delivery Optimization Service *.do.dsp.mp.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints) |

### `geo-prod.do.dsp.mp.microsoft.com`

Microsoft Delivery Optimization host - Pi-hole users list it for the Microsoft Store

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft` | TLS certificate |
| What it does | Matches Microsoft's documented Delivery Optimization endpoint: "Delivery Optimization Service *.do.dsp.mp.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints) |
| Context | Pi-hole users list it for the Microsoft Store: the page lists `geo-prod.do.dsp.mp.microsoft.com` under the heading "Microsoft Store (Windows Store)" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `dev.virtualearth.net`

Microsoft Bing Maps host - Windows uses it to check for updates to offline maps

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Windows Maps endpoint: "The following endpoints are used to check for updates to maps that have been downloaded for offline use." | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions) |
| What it does | Named in that Maps list: "HTTPS/HTTP dev.virtualearth.net" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions) |
| Context | Pi-hole users list it for the Bing Maps Platform: the page lists `dev.virtualearth.net` under the heading "Bing Maps Platform" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `ecn.dev.virtualearth.net`

Microsoft Bing Maps host - In Windows' Maps endpoint list and required by Microsoft 365

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Windows Maps endpoint: "HTTPS/HTTP ecn.dev.virtualearth.net" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions) |
| Context | Required Microsoft 365 endpoint: "*.informationprotection.azure.com, ecn.dev.virtualearth.net" | [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) |
| Context | Pi-hole users list it for the Bing Maps Platform: the page lists `ecn.dev.virtualearth.net` under the heading "Bing Maps Platform" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `t0.ssl.ak.dynamic.tiles.virtualearth.net`

Microsoft Bing Maps host - Covered by Windows' Maps endpoint list

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Matches the Maps wildcard in Microsoft's Windows endpoint list: "HTTPS/HTTP *.ssl.ak.dynamic.tiles.virtualearth.net" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions) |
| Context | Pi-hole users list it for the Bing Maps Platform: the page lists `t0.ssl.ak.dynamic.tiles.virtualearth.net` under the heading "Bing Maps Platform" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `t0.ssl.ak.tiles.virtualearth.net`

Microsoft Bing Maps host - Covered by Windows' Maps endpoint list

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Matches the Maps wildcard in Microsoft's Windows endpoint list: "HTTPS/HTTP *.ssl.ak.tiles.virtualearth.net" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions) |
| Context | Pi-hole users list it for the Bing Maps Platform: the page lists `t0.ssl.ak.tiles.virtualearth.net` under the heading "Bing Maps Platform" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `displaycatalog.mp.microsoft.com`

Microsoft Store catalog - Without it apps cannot be installed or updated from the Store

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| If blocked | Microsoft: blocking it stops Store installs and updates: "If you turn off traffic for these endpoints, apps can't be installed or updated from the Microsoft Store. TLSv1.2/HTTPS/HTTP *displaycatalog.mp.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints) |

### `dl.delivery.mp.microsoft.com`

Microsoft download delivery - Windows Update, Microsoft Store and Edge downloads

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it (CNAME to Akamai; certificate is domain-validated only). DNS CNAME chain: `a1683.dscd.akamai.net.` | Direct check |
| What it does | Matches Microsoft's documented *.dl.delivery.mp.microsoft.com: "HTTP *.dl.delivery.mp.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting) |
| What it does | Edge downloads: "Edge Browser *.dl.delivery.mp.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints) |
| Context | Pi-hole users list it for the Microsoft Store: the page lists `dl.delivery.mp.microsoft.com` under the heading "Microsoft Store (Windows Store)" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `tlu.dl.delivery.mp.microsoft.com`

Microsoft download delivery host - Microsoft lists *.dl.delivery.mp.microsoft.com for Windows Update

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Matches Microsoft's documented *.dl.delivery.mp.microsoft.com: "HTTP *.dl.delivery.mp.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting) |
| Context | Pi-hole users list it for Windows 10 Update: the page lists `tlu.dl.delivery.mp.microsoft.com` under the heading "Windows 10 Update" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `dns.msftncsi.com`

Windows network connectivity check (NCSI) - If this lookup fails, Windows shows the network alert in the taskbar

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Microsoft: NCSI resolves this name: "NCSI sends another DNS request to resolve the address of the dns.msftncsi.com FQDN. If any of these requests fails, the network alert appears in the Task Bar" | [learn.microsoft.com](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/internet-explorer-edge-open-connect-corporate-public-network) |

### `ipv6.msftncsi.com`

Windows network connectivity check (NCSI) domain - Microsoft documents *.msftncsi.com for NCSI

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Microsoft documents *.msftncsi.com for NCSI: "*.msftncsi.com *.msftconnecttest.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/internet-explorer-edge-open-connect-corporate-public-network) |
| Context | Pi-hole users list it under Windows/Microsoft: the page lists `ipv6.msftncsi.com` under the heading "Windows/Microsoft" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `www.msftncsi.com`

Windows network connectivity check (NCSI) - Used by Windows 8.1 and earlier

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Microsoft: NCSI probe for Windows 8.1 and earlier: "Windows 8.1 or earlier versions: NCSI sends a DNS request to resolve the address of the www.msftncsi.com FQDN." | [learn.microsoft.com](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/internet-explorer-edge-open-connect-corporate-public-network) |

### `www.msftconnecttest.com`

Windows network connectivity check (NCSI) - Used by Windows 10 and later

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Microsoft: NCSI probe for Windows 10 and later: "Windows 10 or later versions: NCSI sends a DNS request to resolve the address of the www.msftconnecttest.com FQDN." | [learn.microsoft.com](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/internet-explorer-edge-open-connect-corporate-public-network) |

### `ecs.office.com`

Microsoft feature deployment service - Microsoft lists it as an Intune feature-deployment dependency

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Microsoft lists it as a feature deployment dependency: "Dependency - Feature Deployment Default Required False config.edge.skype.com ecs.office.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints) |

### `emea.ng.msg.teams.microsoft.com`

Microsoft Teams host under the documented *.teams.microsoft.com endpoint - Exact role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | Covered by Microsoft Teams' required *.teams.microsoft.com: "*.lync.com, *.teams.cloud.microsoft, *.teams.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) |

Status: Purpose unverified. Its CNAME name mentions messaging; that is not a documented role.

### `emea.pptservicescast.officeapps.live.com`

Microsoft 365 / Office Online host under the documented *.officeapps.live.com endpoint - Exact role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | Covered by Microsoft 365's required *.officeapps.live.com: "*.officeapps.live.com, *.online.office.com, office.live.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) |

Status: Purpose unverified. Microsoft documents only the wildcard.

### `fe3cr.delivery.mp.microsoft.com`

Microsoft update service - Microsoft lists it for Defender security updates

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft` | TLS certificate |
| What it does | Microsoft lists this Windows Update client URL for Defender updates: "https://fe3cr.delivery.mp.microsoft.com/ClientWebService/client.asmx" | [learn.microsoft.com](https://learn.microsoft.com/en-us/defender-endpoint/configure-network-connections-microsoft-defender-antivirus) |

### `sls.update.microsoft.com`

Microsoft Windows Update - Update service

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft` | TLS certificate |
| What it does | Matches Microsoft's documented *.update.microsoft.com: "*.update.microsoft.com *.delivery.mp.microsoft.com *.windowsupdate.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/defender-endpoint/configure-network-connections-microsoft-defender-antivirus) |
| Context | Pi-hole users list it for Windows 10 Update: the page lists `sls.update.microsoft.com` under the heading "Windows 10 Update" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `forms.office.com`

Microsoft Forms - Surveys and quizzes

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | The site serves Microsoft Forms. Title of the page the host serves: `Microsoft Forms` | Live web page |

### `g.live.com`

Microsoft OneDrive host - Pi-hole users also list it for backing up BitLocker keys to a Microsoft account

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | OneDrive endpoint: "anything that relies on g.live.com to get updated URL information no longer works" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints) |
| Context | Required for SharePoint Online and OneDrive: "36 Default Required No g.live.com, oneclient.sfx.ms" | [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) |
| Context | Pi-hole users list it for BitLocker key backup: the page lists `g.live.com` under the heading "Backup bitlocker recovery key to Microsoft account" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `has.spserv.microsoft.com`

Microsoft Device Health Attestation - Intune device health reporting

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Microsoft: Device Health Attestation endpoint: "continue to use the existing Device Health Attestation DHA endpoint 'has.spserv.microsoft.com' for device health attestation reporting" | [learn.microsoft.com](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints) |

### `i.s-microsoft.com`

Microsoft-run host (s-microsoft.com) - Microsoft lists *.s-microsoft.com for Windows Autopilot; Pi-hole users list it for Microsoft web pages

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | Microsoft lists *.s-microsoft.com as a Windows Autopilot dependency: "windowsphone.com *.s-microsoft.com c.s-microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints) |
| Context | Pi-hole users list it for Microsoft web pages: the page lists `i.s-microsoft.com` under the heading "Microsoft Web Pages (Outlook, Office365, Live, Microsoft.com...)" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `licensing.mp.microsoft.com`

Microsoft licensing - Windows online activation and app licensing

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Microsoft: used for activation and app licensing: "The following endpoint is used for online activation and some app licensing." | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints) |
| If blocked | Blocking breaks activation: "This action also blocks online activation and app licensing might not work. TLSv1.2/HTTPS/HTTP licensing.mp.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints) |

### `storeedgefd.dsx.mp.microsoft.com`

Microsoft Store - Loads the Store app's content

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Microsoft: needed to load Store content: "The following endpoints are needed to load the content in the Microsoft Store app. HTTPS livetileedge.dsx.mp.microsoft.com HTTP storeedgefd.dsx.mp.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints) |

### `login.live.com`

Microsoft account sign-in (Outlook.com, OneDrive and Microsoft account)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Microsoft lists it for consumer Outlook.com, OneDrive and Microsoft account: "Consumer Outlook.com, OneDrive, Device authentication, and Microsoft account Default Required False account.live.com login.live.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints) |
| What it does | The site is the Microsoft account sign-in page. Title of the page the host serves: `Sign in to your Microsoft account` | Live web page |

### `login.microsoftonline.com`

Microsoft Entra ID sign-in - Required by Microsoft 365

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Microsoft: authentication and identity: "Authentication and Identity, includes Microsoft Entra ID and Entra ID related services. Allow Required True login.microsoftonline.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints) |

### `logincdn.msauth.net`

Microsoft sign-in host (msauth.net) - Listed among Microsoft's OneDrive endpoints and required by Microsoft 365

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | Listed among Microsoft's OneDrive endpoints: "TLSv1.2/HTTPS/HTTP oneclient.sfx.ms HTTPS logincdn.msauth.net" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints) |
| Context | Microsoft 365 lists *.msauth.net as required for sign-in: "*.microsoftonline.com, *.msauth.net" | [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) |

### `onedrive.live.com`

Microsoft OneDrive - Listed among Microsoft's OneDrive endpoints

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | Listed among Microsoft's OneDrive endpoints: "TLSv1.2/HTTPS/HTTP g.live.com HTTP onedrive.live.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints) |

### `storage.live.com`

Microsoft OneDrive host - Microsoft 365 lists it for OneDrive supportability, telemetry and APIs

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Microsoft: OneDrive supportability, telemetry and APIs: "OneDrive for Business: supportability, telemetry, APIs, and embedded email links No storage.live.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) |

### `mamservice.manage.microsoft.com`

Microsoft Intune host under the documented *.manage.microsoft.com - Exact role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | Under Intune's documented *.manage.microsoft.com: "Note SSL traffic inspection isn't supported for '*.manage.microsoft.com'" | [learn.microsoft.com](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints) |

Status: Purpose unverified. Microsoft documents only the *.manage.microsoft.com wildcard for Intune.

### `r.manage.microsoft.com`

Microsoft Intune host under the documented *.manage.microsoft.com - Redirects to the Intune admin center

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | Under Intune's documented *.manage.microsoft.com: "Note SSL traffic inspection isn't supported for '*.manage.microsoft.com'" | [learn.microsoft.com](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints) |
| Observed | Its web page redirects to the Intune admin center. Title of the page the host serves: `Microsoft Intune admin center` | Live web page |

### `mrs-efz.ms-acdc.office.com`

Microsoft 365 (office.com) service host - Exact role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | Covered by Microsoft 365's required *.office.com: "147 Default Required No *.office.com, www.microsoft365.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) |

Status: Purpose unverified. Only the *.office.com wildcard is documented.

### `mscomajax.vo.msecnd.net`

Microsoft-run host (msecnd.net, required by Microsoft 365) - Exact role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft 365 lists *.msecnd.net as a required Microsoft domain: "*.msauthimages.net, *.msecnd.net" | [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) |
| Observed | Its root redirects to Microsoft's ASP.NET site. Address the host's web page ends at: `https://dotnet.microsoft.com/en-us/apps/aspnet` | Live web page |

Status: Purpose unverified. Microsoft documents only the *.msecnd.net wildcard; its root redirects to Microsoft's ASP.NET site.

### `officeci-mauservice.azurewebsites.net`

Microsoft AutoUpdate for Mac - Management control endpoint

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it (Azure web app with Microsoft certificate). TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Microsoft: Management Control endpoint for Microsoft AutoUpdate: "https://officeci-mauservice.azurewebsites.net/ ST Management Control endpoint for Microsoft AutoUpdate" | [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/enterprise/network-requests-in-office-2016-for-mac) |

### `presence.teams.live.com`

Microsoft Teams host (teams.live.com)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | teams.live.com is a Microsoft Teams endpoint: "TLSv1.2/HTTP teams.events.data.microsoft.com HTTP teams.live.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions) |

### `products.office.com`

Microsoft 365 product pages (now redirect to microsoft.com)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Observed | Redirects to the Microsoft 365 site. Address the host's web page ends at: `https://www.microsoft.com/en-us/microsoft-365` | Live web page |
| Context | Pi-hole users list it for Microsoft web pages: the page lists `products.office.com` under the heading "Microsoft Web Pages (Outlook, Office365, Live, Microsoft.com...)" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `res-1.cdn.office.net`

Microsoft 365 CDN host - Microsoft lists *.cdn.office.net for Microsoft 365 app updates

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | Microsoft lists *.cdn.office.net for Microsoft 365 app updates: "M365 app updates *.officecdn.microsoft.com *.cdn.office.net" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints) |

### `statics.teams.cdn.office.net`

Microsoft Teams host - Microsoft lists it for the Teams app

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | Microsoft: endpoint of the Teams application: "HTTP statics.teams.cdn.live.net HTTP statics.teams.cdn.office.net" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions) |

### `settings-win.data.microsoft.com`

Microsoft Windows settings service - Lets apps such as the Xbox app update their configuration

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft` | TLS certificate |
| What it does | Microsoft: dynamic app configuration endpoint: "The following endpoints are used as a way for apps to dynamically update their configuration. Apps such as System Initiated User Feedback and the Xbox app use it." | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints) |
| If blocked | Blocking may stop apps: "If you turn off traffic for this endpoint, an app that uses this endpoint might stop working." | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints) |

### `sharepoint.com`

Microsoft SharePoint Online and OneDrive for Business

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | Microsoft 365 required *.sharepoint.com: "31 Optimize Required Yes *.sharepoint.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) |

### `spynet2.microsoft.com`

Microsoft Defender SpyNet host - A 2011 article names spynet2 as a server Defender and Security Essentials contact; both share one CNAME

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Defender and Security Essentials use spynet2 to talk to Microsoft: "Spynet2.microsoft.com" | [www.ghacks.net](https://www.ghacks.net/2011/06/02/disabling-microsoft-spynet-in-windows7/) |
| Observed | Both names CNAME to the same Defender cloud-protection front end. DNS CNAME chain: `wd-prod-cp-us-east-1-fe.eastus.cloudapp.azure.com.` | Direct check |

Note: Neither host appears in Microsoft's current Defender connection page (fetched 2026-11-13).

### `spynetalt.microsoft.com`

Microsoft Defender SpyNet host - A 2011 article names spynet2 as a server Defender and Security Essentials contact; both share one CNAME

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Defender and Security Essentials use spynet2 to talk to Microsoft: "Spynet2.microsoft.com" | [www.ghacks.net](https://www.ghacks.net/2011/06/02/disabling-microsoft-spynet-in-windows7/) |
| Observed | Both names CNAME to the same Defender cloud-protection front end. DNS CNAME chain: `wd-prod-cp-us-east-1-fe.eastus.cloudapp.azure.com.` | Direct check |

Note: Neither host appears in Microsoft's current Defender connection page (fetched 2026-11-13).

### `substrate.office.com`

Microsoft 365 host - Microsoft lists it among Office endpoints in Windows

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | Listed among Microsoft's Office endpoints in Windows: "HTTP roaming.officeapps.live.com HTTPS/HTTP substrate.office.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions) |
| Observed | Its web path /mail/ and Outlook CNAME. DNS CNAME chain: `atm.outlook.mira.tm.svc.cloud.microsoft.` | Direct check |

### `teams.office.com`

Microsoft Teams (redirects to teams.microsoft.com)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Observed | Redirects to Teams. Address the host's web page ends at: `https://teams.microsoft.com/v2/` | Live web page |

### `win10.ipv6.microsoft.com`

Microsoft Teredo IPv6 server - Xbox networking on Windows uses Teredo

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Xbox troubleshooting guides treat it as the Teredo server Xbox networking needs: "Then type win10.ipv6.microsoft.com" | [www.drivereasy.com](https://www.drivereasy.com/knowledge/teredo-is-unable-to-qualify-xbox-window-10-solved/) |
| What it does | Microsoft Xbox networking: Xbox on Windows 10 uses Teredo for peer-to-peer traffic: "New Xbox experiences launching on Windows 10 will use Teredo for P2P" | [diswww.mit.edu](https://diswww.mit.edu/charon/nanog/179964) |

### `win1710.ipv6.microsoft.com`

Microsoft IPv6 host - Purpose unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Resolves in DNS from unbound. DNS status: `NOERROR` | DNS lookup |

Status: Purpose unverified. No source names win1710.ipv6.microsoft.com; win10 and win1910 variants are documented as Teredo server names in Microsoft Q&amp;A, so this is an inference.

### `windows.msn.com`

Microsoft Edge - Endpoint Microsoft lists for the Edge browser

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| Context | Microsoft lists it under Microsoft Edge: "Learn how to turn off traffic to all of the following endpoints for Microsoft Edge. TLSv1.2/HTTP edge.microsoft.com TLSv1.2/HTTP windows.msn.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints) |

### `xbox.ipv6.microsoft.com`

Microsoft Xbox Live - Listed as required for full Xbox Live functionality

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole's Xbox Live list: the page lists `xbox.ipv6.microsoft.com` under the heading "Full Functionality" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| What it does | Pi-hole forum: confirmed by Microsoft as required: "which were also confirmed by Microsoft as being required by Xbox Live for full functionality" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `analytics.dev.azure.com`

Microsoft Azure DevOps Analytics OData endpoint - Caught by the analytics regex

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Microsoft runs it. TLS certificate subject: `O = Microsoft Corporation` | TLS certificate |
| What it does | Microsoft: Analytics OData endpoint: "https://analytics.dev.azure.com/&lt;OrganizationName&gt;/&lt;ProjectName&gt;/_odata/version/$metadata" | [learn.microsoft.com](https://learn.microsoft.com/en-us/azure/devops/report/analytics/analytics-query-parts) |
| Why allowed | Matches this repo's analytics block regex. This repo's block regexes that match it (tested with pihole-FTL): `^analytics?[_.-]` | pihole-FTL test |

### `aic-ngfts.lge.com`

LG webOS TV - LG Content Store cover art; HaGeZi issue #309 reports cover art breaks when blocked

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | LG Electronics runs it. TLS certificate subject: `O = LG Electronics Inc.` | TLS certificate |
| If blocked | Reported in HaGeZi #309: "aic-ngfts.lge.com - _Breaks LG Content App Cover Art_" | [hagezi/dns-blocklists #309](https://github.com/hagezi/dns-blocklists/issues/309) |
| Observed | Looked up by the maintainer's LG webOS TV. Lookups on the maintainer's network, by device type (LG webOS TV): `10` | Pi-hole query log |

### `ngfts.lge.com`

LG webOS TV - LG Content Store thumbnails and cover art

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | LG Electronics runs it. TLS certificate subject: `O = LG Electronics Inc.` | TLS certificate |
| If blocked | Perflyst: blocking it stops thumbnails in the LG Content Store: "#ngfts.lge.com # blocks thumbnails from loading in the LG Content Store" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |
| If blocked | HaGeZi #309 report: "ngfts.lge.com - _Breaks LG Content App Cover Art_" | [hagezi/dns-blocklists #309](https://github.com/hagezi/dns-blocklists/issues/309) |

### `us.rdx2.lgtvsdp.com`

LG webOS TV (US) - LG Content Store cover art

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | LG Electronics runs it. TLS certificate subject: `O = LG Electronics Inc.` | TLS certificate |
| If blocked | HaGeZi #309 report: "us.rdx2.lgtvsdp.com - _Breaks LG Content App Cover Art_" | [hagezi/dns-blocklists #309](https://github.com/hagezi/dns-blocklists/issues/309) |

### `us.ibs.lgappstv.com`

LG webOS TV (US) - TV service location setting

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | LG Electronics runs it. TLS certificate subject: `O = LG Electronics Inc.` | TLS certificate |
| If blocked | HaGeZi #309 report: "us.ibs.lgappstv.com - _Needed for Service Location Area (Settings)_" | [hagezi/dns-blocklists #309](https://github.com/hagezi/dns-blocklists/issues/309) |

### `api-tv.spotify.com`

Spotify - API for the Spotify app on TVs and PlayStation 4

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Spotify runs it. TLS certificate subject: `O = Spotify AB` | TLS certificate |
| What it does | Perflyst: required for the TV and PS4 Spotify app: "#api-tv.spotify.com # required for TV and PS4 spotify app" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `applicast.ga.sony.net`

Sony Bravia TV - AppliCast app widget service; Perflyst says apps need it

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | The site identifies itself. Title of the page the host serves: `AppliCast Widgets Distribution Service` | Live web page |
| If blocked | Perflyst: needed for applications on Sony Bravia: the page lists `applicast.ga.sony.net` under the heading "needed for applications, if blocked error "no internet connection"" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `portal.store.sonyentertainmentnetwork.com`

Sony (Sony Interactive Entertainment) host - Perflyst says Bravia TV apps need it

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Sony Interactive Entertainment runs it. TLS certificate subject: `O = Sony Interactive Entertainment LLC` | TLS certificate |
| If blocked | Perflyst: needed for applications on Sony Bravia: the page lists `portal.store.sonyentertainmentnetwork.com` under the heading "needed for applications, if blocked error "no internet connection"" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `update.biv.sony.tv`

Sony Bravia TV - Software updates

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Perflyst: required for updates: "#update.biv.sony.tv # required for updates" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `auth.samsungosp.com`

Samsung TV - Samsung account sign-in

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Samsung runs it. TLS certificate subject: `Samsung Electronics` | TLS certificate |
| If blocked | Perflyst: Samsung accounts fail when blocked: "#auth.samsungosp.com # if blocked, samsung accounts will fail to authenticate" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `cdn.samsungcloudsolution.com`

Samsung TV - System update check

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Perflyst: system update check: "#cdn.samsungcloudsolution.com # System update check on Samsung UE40F5500" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |
| Observed | Looked up by the maintainer's Samsung device. Lookups on the maintainer's network, by device type (Samsung device): `22` | Pi-hole query log |

### `configprd.samsungcloudsolution.net`

Samsung TV host - Perflyst keeps it unblocked - Caught by the samsungcloudsolution.net regex

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Samsung runs it. TLS certificate subject: `Samsung Electronics` | TLS certificate |
| Context | Perflyst keeps it unblocked under Samsung: the page lists `configprd.samsungcloudsolution.net` under the heading "Samsung" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |
| Why allowed | Matches this repo's samsungcloudsolution.net block regex. This repo's block regexes that match it (tested with pihole-FTL): `samsungcloudsolution` | pihole-FTL test |

### `lcprd1.samsungcloudsolution.net`

Samsung TV - Network connection test (no tracking per Perflyst) - Caught by the samsungcloudsolution.net regex

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Samsung runs it. TLS certificate subject: `Samsung Electronics` | TLS certificate |
| What it does | Perflyst: ping test, no beaconing: "#lcprd1.samsungcloudsolution.net # ping test, no beaconing" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |
| Why allowed | Matches this repo's samsungcloudsolution.net block regex. This repo's block regexes that match it (tested with pihole-FTL): `samsungcloudsolution` | pihole-FTL test |
| Observed | Looked up 776 times by the maintainer's Samsung device. Lookups on the maintainer's network, by device type (Samsung device): `776` | Pi-hole query log |

### `time.samsungcloudsolution.com`

Samsung TV host - Plex, YouTube and Prime Video fail on some Samsung TVs without it (Perflyst)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Samsung runs it. TLS certificate subject: `Samsung Electronics` | TLS certificate |
| If blocked | Perflyst report: "#time.samsungcloudsolution.com # if blocked, services like Plex, YouTube and Amazon Video not working anymore on some Samsung TV's" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `gpm.samsungqbe.com`

Samsung TV host - Perflyst reports connection problems when blocked - Caught by the samsungqbe.com regex

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Samsung runs it. TLS certificate subject: `Samsung Electronics` | TLS certificate |
| If blocked | Perflyst report: "#gpm.samsungqbe.com # Numerous connection problems, e.g. #82" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |
| Why allowed | Matches this repo's samsungqbe.com block regex. This repo's block regexes that match it (tested with pihole-FTL): `samsungqbe` | pihole-FTL test |

### `osb-ussvc.samsungqbe.com`

Samsung TV host - Required for Samsung TV Plus (Perflyst) - Caught by the samsungqbe.com regex

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Samsung runs it. TLS certificate subject: `Samsung Electronics` | TLS certificate |
| If blocked | Perflyst: required for TV Plus: "#osb-ussvc.samsungqbe.com # required for TV Plus" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |
| Why allowed | Matches this repo's samsungqbe.com block regex. This repo's block regexes that match it (tested with pihole-FTL): `samsungqbe` | pihole-FTL test |

### `infolink.pavv.co.kr`

Samsung TV - App store and sign-in - Caught by the pavv.co.kr regex

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Samsung runs it. TLS certificate subject: `Samsung Electronics` | TLS certificate |
| If blocked | Perflyst report: "#infolink.pavv.co.kr # Needed for appstore and login on Samsung UE40F5500" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |
| Why allowed | Matches this repo's pavv.co.kr block regex. This repo's block regexes that match it (tested with pihole-FTL): `pavv` | pihole-FTL test |

### `avpro.global.yamaha.com`

Yamaha AV receivers - Firmware updates (blocking it stops updates on the RX-V685)

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Perflyst report: "#avpro.global.yamaha.com # Blocks system updates on RX-V685" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `deviceportal.nettvservices.com`

Philips TV (TP Vision) host - Perflyst says apps need it

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | TP Vision (Philips TV maker) runs it. TLS certificate subject: `O = TP Vision Europe B.V.` | TLS certificate |
| If blocked | Perflyst: needed for apps: "#deviceportal.nettvservices.com # needed for apps" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `epg.corio.com`

Philips TV host - Perflyst says apps need it

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Perflyst: needed for apps: "#epg.corio.com # needed for apps" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |
| Observed | DNS timed out on 2026-11-13 from the local resolver. DNS status: `no-answer` | DNS lookup |

Note: DNS gave no answer once on 2026-11-13; recheck.

### `www.ecdinterface.philips.com`

Philips-run host - Perflyst ties it to the Philips Hue Bridge

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Philips runs it. TLS certificate subject: `O = Philips International B.V.` | TLS certificate |
| Context | Perflyst: Philips Hue Bridge: "#www.ecdinterface.philips.com # Philips Hue Bridge" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `images.vizio.com`

Vizio TV host - Perflyst says Vizio smart TV features need it

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Perflyst: required for Vizio smart TV features: the page lists `images.vizio.com` under the heading "Required for Vizio smart tv features" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `vcs.vdspf.com`

Panasonic Viera TV - Firmware downloads (TV is told of new firmware but cannot install it when blocked)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Panasonic runs it. TLS certificate subject: `O = Panasonic` | TLS certificate |
| If blocked | Perflyst report: "#vcs.vdspf.com // if blocked, notified of new firmware but unable to download/install" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `itv.ard.de`

ARD (German public TV) - HbbTV red-button media library on smart TVs

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Suedwestrundfunk (an ARD broadcaster) holds its certificate. TLS certificate subject: `dwestrundfunk` | TLS certificate |
| What it does | Perflyst: ARD media library, HbbTV: "#itv.ard.de # ARD media lib - HBBTV" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `location-api.hdhomerun.com`

SiliconDust HDHomeRun TV tuner - Firmware updates

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Perflyst: required for firmware updates: "#location-api.hdhomerun.com # required for firmware update" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `tuner-api.hdhomerun.com`

SiliconDust HDHomeRun TV tuner - Firmware updates

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Perflyst: required for firmware updates: "#tuner-api.hdhomerun.com # required for firmware update" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `time-a.timefreq.bldrdoc.gov`

NIST host (CNAME time-a-b.nist.gov) - Perflyst lists it for Sharp smart TVs (Opera OS) and advises not blocking it

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | CNAME to NIST's time server. DNS CNAME chain: `time-a-b.nist.gov.` | Direct check |
| Context | Perflyst: used by Sharp Smart TV, not a good idea to block: "# time-a.timefreq.bldrdoc.gov # probably not a good idea to block this one" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |
| Context | Listed under Sharp Smart TV: the page lists `time-a.timefreq.bldrdoc.gov` under the heading "Sharp Smart TV using Opera OS (thanks to sml156)" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `appboot.netflix.com`

Netflix host - Netflix breaks when it is blocked (Perflyst, anudeep)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Netflix runs it. TLS certificate subject: `Netflix` | TLS certificate |
| If blocked | Perflyst: secure, api-global and appboot break Netflix: the page lists `appboot.netflix.com` under the heading "secure, api-global, and appboot break Netflix" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |
| Context | anudeep: domains needed for Netflix: the page lists `appboot.netflix.com` under the heading "Netflix - Domains needed for netlix to work correctly" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |

### `secure.netflix.com`

Netflix host - Netflix breaks when it is blocked (Perflyst)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Netflix runs it. TLS certificate subject: `Netflix` | TLS certificate |
| If blocked | Perflyst: secure, api-global and appboot break Netflix: the page lists `secure.netflix.com` under the heading "secure, api-global, and appboot break Netflix" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |
| Observed | Looked up by the maintainer's Samsung device and LG TV. Lookups on the maintainer's network, by device type (Samsung device): `12` | Pi-hole query log |

### `netflix.com`

Netflix - Main site

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Netflix runs it. TLS certificate subject: `Netflix` | TLS certificate |
| What it does | Site title. Title of the page the host serves: `Netflix` | Live web page |

### `nrdp.prod.cloud.netflix.com`

Netflix host - Maintainer added it to sign in on Nvidia Shield TV

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Netflix runs it. TLS certificate subject: `Netflix` | TLS certificate |
| If blocked | Maintainer's original reason: added the line `nrdp.prod.cloud.netflix.com` | [commit 6420fa3](https://github.com/slyfox1186/pihole-regex/commit/6420fa3) |
| Observed | Looked up by the maintainer's Samsung device and LG TV. Lookups on the maintainer's network, by device type (LG webOS TV): `26` | Pi-hole query log |

Status: The note repeats the maintainer's earlier report.

### `uiboot.netflix.com`

Netflix host - Maintainer added it to sign in on Nvidia Shield TV

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Netflix runs it. TLS certificate subject: `Netflix` | TLS certificate |
| If blocked | Maintainer's original reason: added the line `uiboot.netflix.com -- Required to login to NetFlix on Nvidia Shield` | [commit a913bbc](https://github.com/slyfox1186/pihole-regex/commit/a913bbc) |
| Observed | Looked up by the maintainer's Samsung device and LG TV. Lookups on the maintainer's network, by device type (Samsung device): `46` | Pi-hole query log |

Status: The note repeats the maintainer's earlier report.

### `win10.prod.http1.netflix.com`

Netflix host - Maintainer reported it is required for signing in

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Netflix runs it. TLS certificate subject: `Netflix` | TLS certificate |
| If blocked | Maintainer's original reason: added the line `win10.prod.http1.netflix.com` | [commit 34a8b8d](https://github.com/slyfox1186/pihole-regex/commit/34a8b8d) |

Status: The note repeats the maintainer's earlier report.

### `api.roku.com`

Roku host - Maintainer added it for Disney+ and other Roku apps

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Roku runs it. TLS certificate subject: `Roku` | TLS certificate |
| If blocked | Maintainer's original reason: added the line `api.roku.com -- Streaming on some Roku apps like Disney Plus` | [commit 52189ee](https://github.com/slyfox1186/pihole-regex/commit/52189ee) |

Status: The note repeats the maintainer's earlier report.

### `x-default-stgec.uplynk.com`

Uplynk host - Maintainer added it for Discovery+ playback on Nvidia Shield TV

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Maintainer's original reason: added the line `x-default-stgec.uplynk.com` | [commit 28ee6d6](https://github.com/slyfox1186/pihole-regex/commit/28ee6d6) |

Status: The note repeats the maintainer's earlier report.

### `assets.adobedtm.com`

Adobe-run host - Pi-hole users report Lowe's online checkout fails when it is blocked

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Adobe runs it. TLS certificate subject: `Adobe Inc.` | TLS certificate |
| If blocked | Pi-hole forum report: "Clicking "Start Secure Checkout" from the Shopping Cart on Lowe's website does not load anything." | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Observed | Looked up by the maintainer's desktop PC and iPhone. Lookups on the maintainer's network, by device type (Linux desktop PC): `6` | Pi-hole query log |
| Why allowed | Block List Project's ads list blocks it. Block List Project lists that contain it: `ads` | Block List Project archive |

### `auth.split.io`

Split.io host - The MyFitnessPal app cannot log in without it

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Pi-hole forum: these fix MyFitnessPal login: "## MyFitnessPal Mobile App These fixes login issue." | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Context | Listed under MyFitnessPal: the page lists `auth.split.io` under the heading "MyFitnessPal Mobile App" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

Note: The old note said Spotify; the source names MyFitnessPal.

### `sdk.split.io`

Split.io host - The MyFitnessPal app cannot log in without it

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Pi-hole forum: these fix MyFitnessPal login: "## MyFitnessPal Mobile App These fixes login issue." | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Context | Listed under MyFitnessPal: the page lists `sdk.split.io` under the heading "MyFitnessPal Mobile App" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

Note: The old note said EA Games; the source names MyFitnessPal.

### `viewer.content.glympse.com`

Glympse host - Papa John's 'Where's my pizza' order tracker needs it

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Pi-hole forum report: "The papa john's where's my pizza requires: viewer.content.glympse.com" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `gravatar.com`

Gravatar avatar site - Plex uses it for login pictures

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Pi-hole forum: Plex custom login pictures: "pihole allow gravatar.com # custom login pictures" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| What it does | Site title. Title of the page the host serves: `Avatar` | Live web page |

### `thetvdb.com`

TheTVDB - TV series metadata used by Plex

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Pi-hole forum: Plex TV series metadata: "pihole allow thetvdb.com # metadata for tv series" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| What it does | Site title. Title of the page the host serves: `TheTVDB.com` | Live web page |

### `apt.sonarr.tv`

Sonarr TV download manager host - Pi-hole users list it for Sonarr

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists it under Sonarr: the page lists `apt.sonarr.tv` under the heading "Sonarr" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `download.sonarr.tv`

Sonarr TV download manager host - Pi-hole users list it for Sonarr

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists it under Sonarr: the page lists `download.sonarr.tv` under the heading "Sonarr" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `forums.sonarr.tv`

Sonarr TV download manager - Forums

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists it under Sonarr: the page lists `forums.sonarr.tv` under the heading "Sonarr" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `services.sonarr.tv`

Sonarr TV download manager host - Pi-hole users list it for Sonarr

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists it under Sonarr: the page lists `services.sonarr.tv` under the heading "Sonarr" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `skyhook.sonarr.tv`

Sonarr TV download manager host - Pi-hole users list it for Sonarr

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists it under Sonarr: the page lists `skyhook.sonarr.tv` under the heading "Sonarr" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `chat.signal.org`

Signal messenger host - Pi-hole users list it for Signal

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Signal runs it. TLS certificate subject: `Signal Messenger` | TLS certificate |
| Context | Listed under Signal: the page lists `chat.signal.org` under the heading "Signal" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `contentproxy.signal.org`

Signal messenger host - Pi-hole users list it for Signal

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Listed under Signal: the page lists `contentproxy.signal.org` under the heading "Signal" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `storage.signal.org`

Signal messenger host - Pi-hole users list it for Signal

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Signal runs it. TLS certificate subject: `Signal Messenger` | TLS certificate |
| Context | Listed under Signal: the page lists `storage.signal.org` under the heading "Signal" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `updates2.signal.org`

Signal messenger host - Pi-hole users list it for Signal

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Signal runs it. TLS certificate subject: `Signal Messenger` | TLS certificate |
| Context | Listed under Signal: the page lists `updates2.signal.org` under the heading "Signal" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `check2.tsb.co.uk`

TSB Bank (UK) host - Pi-hole users list it for the TSB Mobile app; it CNAMEs to ThreatMetrix (online-metrix.net)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | TSB runs it. TLS certificate subject: `TSB Bank Plc` | TLS certificate |
| Context | Listed under TSB Mobile: the page lists `check2.tsb.co.uk` under the heading "TSB Mobile" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Observed | CNAME to ThreatMetrix (online-metrix.net) fraud-prevention service. DNS CNAME chain: `h-tsb.online-metrix.net.` | Direct check |
| Why allowed | Block List Project's tracking list blocks it. Block List Project lists that contain it: `tracking` | Block List Project archive |

### `chevrolet.com`

Chevrolet car maker's website

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | General Motors runs it. TLS certificate subject: `General Motors LLC` | TLS certificate |
| What it does | Site title. Title of the page the host serves: `Chevrolet` | Live web page |
| Context | Listed on the Pi-hole forum: the page lists `chevrolet.com` under the heading "Chevrolet" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `directvnow.com`

DirecTV Stream (formerly DirecTV Now) website

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | DirecTV runs it. TLS certificate subject: `DIRECTV` | TLS certificate |
| Context | Pi-hole forum lists it under DirectTV: the page lists `directvnow.com` under the heading "DirectTV" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `dl.dropboxusercontent.com`

Dropbox file host - Pi-hole users list it for Dropbox

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Dropbox runs it. TLS certificate subject: `Dropbox` | TLS certificate |
| Context | Listed under Dropbox: the page lists `dl.dropboxusercontent.com` under the heading "Dropbox" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `dl.dropbox.com`

Dropbox host - Listed in anudeep's allowlist

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Dropbox runs it. TLS certificate subject: `Dropbox` | TLS certificate |
| Observed | anudeep's whitelist lists it: "dl.dropbox.com" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |

### `dl.google.com`

Google downloads - Pi-hole users list it for Chrome updates on Ubuntu

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum: Google Chrome updates on Ubuntu: the page lists `dl.google.com` under the heading "Google Chrome (to update on ubuntu)" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Observed | Looked up by the maintainer's desktop PC. Lookups on the maintainer's network, by device type (Linux desktop PC): `4` | Pi-hole query log |

### `android.clients.google.com`

Google host - Pi-hole users list it for the Google Play Store

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists it under Google Play: the page lists `android.clients.google.com` under the heading "Google Play" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `redirector.gvt1.com`

Google host - Pi-hole users list it for Android TV

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists it under Android TV: the page lists `redirector.gvt1.com` under the heading "Android TV" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `entitlement.auth.adobe.com`

Adobe host - WatchESPN needs it (Pi-hole forum, anudeep)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Adobe runs it. TLS certificate subject: `Adobe Inc` | TLS certificate |
| If blocked | Pi-hole forum and anudeep list it under WatchESPN: the page lists `entitlement.auth.adobe.com` under the heading "WatchESPN" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `fpdownload.adobe.com`

Adobe host - WatchESPN needs it (Pi-hole forum, anudeep)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Adobe runs it. TLS certificate subject: `Adobe Inc` | TLS certificate |
| If blocked | Pi-hole forum and anudeep list it under WatchESPN: the page lists `fpdownload.adobe.com` under the heading "WatchESPN" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `gdlp01.c-wss.com`

Canon host - Pi-hole users list it for Canon printers

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Canon runs it. TLS certificate subject: `Canon Inc.` | TLS certificate |
| Context | Pi-hole forum lists it under Canon printers: the page lists `gdlp01.c-wss.com` under the heading "Cannon Printers" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `gfwsl.geforce.com`

Nvidia host - Pi-hole users list it for GeForce Experience

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Nvidia runs it. TLS certificate subject: `NVIDIA Corporation` | TLS certificate |
| Context | Listed under NVIDIA GeForce Experience: the page lists `gfwsl.geforce.com` under the heading "NVIDIA GeForce Experience" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `imagesak.secureserver.net`

GoDaddy - Webmail button images

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | GoDaddy runs it. TLS certificate subject: `GoDaddy Inc.` | TLS certificate |
| Context | Listed under GoDaddy webmail buttons: the page lists `imagesak.secureserver.net` under the heading "GoDaddy webmail buttons" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `json.bild.de`

Bild.de (German news, Axel Springer) host - Pi-hole users list it for Bild.de

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Axel Springer runs it. TLS certificate subject: `Axel Springer SE` | TLS certificate |
| Context | Listed under Bild DE: the page lists `json.bild.de` under the heading "Bild DE" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Why allowed | Block List Project's ads list blocks it. Block List Project lists that contain it: `ads` | Block List Project archive |

### `mobileandroidapi.punchh.com`

Punchh (PAR) host - Pi-hole users list it for Punchh loyalty apps (Farmer Boys, El Pollo Loco and others)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Punchh runs it. TLS certificate subject: `PUNCHH INC` | TLS certificate |
| Context | Listed under Punchh: the page lists `mobileandroidapi.punchh.com` under the heading "Punchh (Farmer Boys, El Pollo Loco, Capriotti's, etc.)" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Why allowed | Block List Project's ads list blocks it. Block List Project lists that contain it: `ads` | Block List Project archive |

### `nine.plugins.plexapp.com`

Plex host - Pi-hole users list it for Plex

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists it under Plex: the page lists `nine.plugins.plexapp.com` under the heading "Plex Domains" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

Status: Purpose unverified. The source lists it among Plex domains without a role.

### `o1.email.plex.tv`

Plex host - Pi-hole users list it for Plex

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists it under Plex: the page lists `o1.email.plex.tv` under the heading "Plex Domains" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

Status: Purpose unverified. The source lists it among Plex domains without a role.

### `o2.sg0.plex.tv`

Plex host - Pi-hole users list it for Plex

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists it under Plex: the page lists `o2.sg0.plex.tv` under the heading "Plex Domains" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

Status: Purpose unverified. The source lists it among Plex domains without a role.

### `tvthemes.plexapp.com.cdn.cloudflare.net`

Plex host - Pi-hole users list it for Plex

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists it under Plex: the page lists `tvthemes.plexapp.com.cdn.cloudflare.net` under the heading "Plex Domains" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

Status: Purpose unverified. The source lists it among Plex domains without a role.

### `plex.tv`

Plex main site

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Plex runs it. TLS certificate subject: `Plex GmbH` | TLS certificate |
| Context | Listed under Plex: the page lists `plex.tv` under the heading "Plex Domains" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `portal.fb.com`

Meta-run host - Pi-hole users list it for Facebook

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Meta runs it. TLS certificate subject: `Meta Platforms` | TLS certificate |
| Context | Pi-hole forum lists it under Facebook: the page lists `portal.fb.com` under the heading "Facebook, Facebook Messenger" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Why allowed | Block List Project's facebook list blocks it. Block List Project lists that contain it: `facebook` | Block List Project archive |

### `scontent.fgdl5-1.fna.fbcdn.net`

Facebook (Meta) host - Pi-hole users list it for Facebook

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Meta runs it. TLS certificate subject: `Meta Platforms` | TLS certificate |
| Context | Listed under Facebook, Facebook Messenger: the page lists `scontent.fgdl5-1.fna.fbcdn.net` under the heading "Facebook, Facebook Messenger" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Why allowed | Block List Project's facebook list blocks it. Block List Project lists that contain it: `facebook` | Block List Project archive |

### `s.mzstatic.com`

Apple static content host - Apple Music tracks fail without it; Apple lists it for Classroom

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Apple runs it. TLS certificate subject: `Apple Inc.` | TLS certificate |
| Context | Apple network requirements list it: "s.mzstatic.com 443 TCP iPadOS and macOS Classroom and Schoolwork device verification" | [support.apple.com](https://support.apple.com/en-us/101555) |
| If blocked | Pi-hole forum: Apple Music tracks fail when blocked: "Apple Music streaming tracks not playing with (s.mzstatic.com) blocked." | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `styles.redditmedia.com`

Reddit host - Pi-hole users list it for Reddit

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Reddit runs it. TLS certificate subject: `Reddit` | TLS certificate |
| Context | Listed under Reddit: the page lists `styles.redditmedia.com` under the heading "Reddit" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `tracking-protection.cdn.mozilla.net`

Mozilla host - Pi-hole users list it for Firefox Tracking Protection

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Listed under Mozilla Firefox Tracking Protection: the page lists `tracking-protection.cdn.mozilla.net` under the heading "Mozilla Firefox Tracking Protection" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `tracking.dpd.de`

DPD (Germany) - Parcel tracking

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Sendungsverfolgung` | Live web page |
| Context | Listed under DPD package tracking: the page lists `tracking.dpd.de` under the heading "Tracking Packages sent with DPD" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `v.w-x.co`

w-x.co host - Pi-hole users report weather.com videos do not play without it

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Pi-hole forum report: the page lists `v.w-x.co` under the heading "Videos not playing on weather.com" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Why allowed | Block List Project's ads list blocks it. Block List Project lists that contain it: `ads` | Block List Project archive |

### `www.appleiphonecell.com`

Apple-related host - Pi-hole users list it with captive.apple.com for iOS

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists it under iOS/Apple: the page lists `www.appleiphonecell.com` under the heading "iOS/Apple" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `weeklyad.target.com.edgesuite.net`

Target - Weekly ad pages (Akamai host)

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Listed under Target's Weekly Ads: the page lists `weeklyad.target.com.edgesuite.net` under the heading "Target's Weekly Ads" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

### `crl.entrust.net`

Entrust certificate revocation host - Maintainer added it for certificate validation

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Maintainer's original line: added the line `crl.entrust.net # Security certificate validation.` | [commit 9cbe2dd](https://github.com/slyfox1186/pihole-regex/commit/9cbe2dd) |

Status: The note repeats the maintainer's earlier report.

### `i.cdn.turner.com`

Turner CDN host - anudeep lists it for Adult Swim videos on Amazon Fire TV

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep: Adult Swim videos on Amazon Firestick: the page lists `i.cdn.turner.com` under the heading "Adult Swim Videos on Amazon Firestick" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |
| Observed | CNAME to Akamai. DNS CNAME chain: `akamaiedge` | Direct check |

### `pmd.cdn.turner.com`

Turner CDN host - anudeep lists it for Adult Swim videos on Amazon Fire TV

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep: Adult Swim videos on Amazon Firestick: the page lists `pmd.cdn.turner.com` under the heading "Adult Swim Videos on Amazon Firestick" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |
| Observed | Certificate. TLS certificate subject: `Warner Bros. Discovery` | TLS certificate |

### `z.cdn.turner.com`

Turner CDN host - anudeep lists it for Adult Swim on Fire TV and the Roku TNT app

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep: Adult Swim videos on Amazon Firestick: the page lists `z.cdn.turner.com` under the heading "Adult Swim Videos on Amazon Firestick" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |
| Observed | Certificate. TLS certificate subject: `Warner Bros. Discovery` | TLS certificate |

### `bit.ly`

Bitly - URL shortener

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep lists it under URL shorteners: the page lists `bit.ly` under the heading "URL shorteners" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |
| What it does | Site title. Title of the page the host serves: `Bitly` | Live web page |

### `goo.gl`

Google URL shortener domain - Listed by anudeep as a URL shortener

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep lists it under URL shorteners: the page lists `goo.gl` under the heading "URL shorteners" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |
| Observed | The root now answers 'Invalid Dynamic Link'. Title of the page the host serves: `Invalid Dynamic Link` | Live web page |

### `graph.instagram.com`

Instagram (Meta) host - Listed by anudeep under Facebook

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Meta runs it. TLS certificate subject: `Meta Platforms` | TLS certificate |
| Context | anudeep lists it under Facebook: the page lists `graph.instagram.com` under the heading "Facebook" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |
| Why allowed | Block List Project's facebook list blocks it. Block List Project lists that contain it: `facebook` | Block List Project archive |

### `lm.licenses.adobe.com`

Adobe - Software licence verification

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Adobe runs it. TLS certificate subject: `Adobe Inc.` | TLS certificate |
| What it does | anudeep: Adobe licence verification endpoints: the page lists `lm.licenses.adobe.com` under the heading "Adobe licence verification endpoints" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |

### `ota-downloads.nvidia.com`

Nvidia updates host (anudeep)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Nvidia runs it. TLS certificate subject: `NVIDIA Corporation` | TLS certificate |
| What it does | anudeep: Nvidia updates: the page lists `ota-downloads.nvidia.com` under the heading "Nvidia updates" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |

### `pgl.yoyo.org`

Peter Lowe's ad server list - Blocklist source site

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep lists it under hosts files: the page lists `pgl.yoyo.org` under the heading "Host files" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |

### `someonewhocares.org`

Dan Pollock's hosts file - Blocklist source site

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep lists it under hosts files: the page lists `someonewhocares.org` under the heading "Host files" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |

### `sysctl.org`

Cameleon hosts file (sysctl.org) - Blocklist source site

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep lists it under hosts files: the page lists `sysctl.org` under the heading "Host files" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |

### `winhelp2002.mvps.org`

MVPS hosts file - Blocklist source site

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep lists it under hosts files: the page lists `winhelp2002.mvps.org` under the heading "Host files" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |

### `v.firebog.net`

Firebog - Curated blocklist collection - Blocklist source site

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep lists it under hosts files: the page lists `v.firebog.net` under the heading "Host files" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |

### `stats.streamelements.com`

StreamElements chat statistics site - Caught by mmotti's original stats regex

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `StreamElements Chat Stats` | Live web page |
| Why allowed | mmotti's original regex list blocks it (tested with pihole-FTL). Mmotti's regexes that match it (tested with pihole-FTL): `^stat(s\|istics)?[0-9]*[_.-]` | pihole-FTL test |

### `adverts.ie`

Adverts.ie website - Caught by mmotti's original advert regex

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Adverts` | Live web page |
| Why allowed | mmotti's original regex list blocks it (tested with pihole-FTL). Mmotti's regexes that match it (tested with pihole-FTL): `^advert` | pihole-FTL test |
| Why allowed | Block List Project's ads list blocks it. Block List Project lists that contain it: `ads` | Block List Project archive |

### `anti-ad.net`

anti-AD - Chinese ad-filter list project site - Caught by mmotti's original ad regex

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `anti-AD` | Live web page |
| Why allowed | mmotti's original regex list blocks it (tested with pihole-FTL). Mmotti's regexes that match it (tested with pihole-FTL): `^ad([sxv]?[0-9]*\|system)` | pihole-FTL test |

### `www.ad.nl`

AD.nl (DPG Media) website - Caught by mmotti's original ad regex

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | DPG Media runs it. TLS certificate subject: `DPG Media Group NV` | TLS certificate |
| Why allowed | mmotti's original regex list blocks it (tested with pihole-FTL). Mmotti's regexes that match it (tested with pihole-FTL): `^ad([sxv]?[0-9]*\|system)` | pihole-FTL test |

### `beacons-npa.gov.uk`

Bannau Brycheiniog National Park Authority website - HaGeZi Pro blocks it

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Bannau Brycheiniog National Park Authority` | Live web page |
| Why allowed | mmotti's original regex list blocks it (tested with pihole-FTL). Mmotti's regexes that match it (tested with pihole-FTL): `^beacons?` | pihole-FTL test |
| Why allowed | HaGeZi Pro blocks it. Checked 2026-11-21: `pro.txt` contains `\|\|beacons-npa.gov.uk^` | Direct check |

### `mytaxes.ads.taj.gov.jm`

Jamaica government host - Maintainer described it as the Tax Administration Jamaica taxpayer portal - Caught by the ad regex

| Shows | Evidence | Source |
| --- | --- | --- |
| Why allowed | Matches this repo's ad block regex. This repo's block regexes that match it (tested with pihole-FTL): `adv[0-9]*` | pihole-FTL test |
| What it does | Maintainer's original line: added the line `mytaxes.ads.taj.gov.jm -- Tax Administration Jamaica taxpayer portal - Caught by the ad regex` | [commit d93c6dd](https://github.com/slyfox1186/pihole-regex/commit/d93c6dd) |

### `webmail.adv.oabsp.org.br`

OAB Sao Paulo webmail - Caught by the ad regex

| Shows | Evidence | Source |
| --- | --- | --- |
| Why allowed | Matches this repo's ad block regex. This repo's block regexes that match it (tested with pihole-FTL): `adv[0-9]*` | pihole-FTL test |
| What it does | Site title. Title of the page the host serves: `Webmail` | Live web page |

### `pixel-by-labcorp.zendesk.com`

Pixel by Labcorp help center (Zendesk) - Caught by mmotti's original pixel regex

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Redirects to Labcorp's support site. Address the host's web page ends at: `support.ondemand.labcorp.com` | Live web page |
| Why allowed | mmotti's original regex list blocks it (tested with pihole-FTL). Mmotti's regexes that match it (tested with pihole-FTL): `^pixels?` | pihole-FTL test |

### `stats-api.mlssoccer.com`

Major League Soccer - Match statistics on mlssoccer.com - Caught by the stats regex

| Shows | Evidence | Source |
| --- | --- | --- |
| Why allowed | Matches this repo's stats block regex. This repo's block regexes that match it (tested with pihole-FTL): `^stat` | pihole-FTL test |
| What it does | Maintainer's original line: added the line `stats-api.mlssoccer.com -- MLS match statistics on mlssoccer.com - Caught by the stats regex` | [commit 652f298](https://github.com/slyfox1186/pihole-regex/commit/652f298) |

### `stats-widgets.mlsdigital.net`

Major League Soccer - Match statistics on mlssoccer.com - Caught by the stats regex

| Shows | Evidence | Source |
| --- | --- | --- |
| Why allowed | Matches this repo's stats block regex. This repo's block regexes that match it (tested with pihole-FTL): `^stat` | pihole-FTL test |
| What it does | Maintainer's original line: added the line `stats-widgets.mlsdigital.net -- MLS match statistics widgets on mlssoccer.com - Caught by the stats regex` | [commit 652f298](https://github.com/slyfox1186/pihole-regex/commit/652f298) |

### `stats-prod.sidearmsports.com`

SIDEARM live stats site - Caught by the stats regex

| Shows | Evidence | Source |
| --- | --- | --- |
| Why allowed | Matches this repo's stats block regex. This repo's block regexes that match it (tested with pihole-FTL): `^stat` | pihole-FTL test |
| What it does | Site title. Title of the page the host serves: `SIDEARMLiveStats` | Live web page |

### `stats.foldingathome.org`

Folding@home - Project statistics site - Caught by mmotti's original stats regex

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Folding@home Statistics` | Live web page |
| Why allowed | mmotti's original regex list blocks it (tested with pihole-FTL). Mmotti's regexes that match it (tested with pihole-FTL): `^stat` | pihole-FTL test |

### `stats.stackexchange.com`

Cross Validated (stats.stackexchange.com) - Caught by mmotti's original stats regex

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Cross Validated` | Live web page |
| Why allowed | mmotti's original regex list blocks it (tested with pihole-FTL). Mmotti's regexes that match it (tested with pihole-FTL): `^stat` | pihole-FTL test |

### `ddns.net`

ddns.net dynamic DNS domain - HaGeZi's DynDNS list blocks it; only the bare domain is allowed

| Shows | Evidence | Source |
| --- | --- | --- |
| Why allowed | Block List Project's malware list blocks it. Block List Project lists that contain it: `malware` | Block List Project archive |
| Observed | No HTTPS site; DNS answers. DNS status: `NOERROR` | DNS lookup |
| Why allowed | HaGeZi's DynDNS list blocks it. Checked 2026-11-21: `dyndns.txt` contains `\|\|ddns.net^` | Direct check |

Note: Decision 2026-11-14: kept. Only the bare domain is allowed; customer hostnames under it stay blockable.

### `dyndns.org`

Dyn dynamic DNS domain (Oracle certificate) - HaGeZi's DynDNS list blocks it; only the bare domain is allowed

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Oracle certificate. TLS certificate subject: `Oracle Corporation` | TLS certificate |
| Why allowed | Block List Project's malware list blocks it. Block List Project lists that contain it: `malware` | Block List Project archive |
| What it does | Site. Title of the page the host serves: `My Dyn Account` | Live web page |
| Why allowed | HaGeZi's DynDNS list blocks it. Checked 2026-11-21: `dyndns.txt` contains `\|\|dyndns.org^` | Direct check |

Note: Decision 2026-11-14: kept. Only the bare domain is allowed; customer hostnames under it stay blockable.

### `fairuse.org`

fairuse.org - HaGeZi's DynDNS list blocks it as a dynamic DNS domain; only the bare domain is allowed

| Shows | Evidence | Source |
| --- | --- | --- |
| Why allowed | Block List Project's malware list blocks it. Block List Project lists that contain it: `malware` | Block List Project archive |
| What it does | Maintainer's original line: added the line `fairuse.org -- Fair use information site - Blocked by the Block List Project malware list` | [commit f3f9cbb](https://github.com/slyfox1186/pihole-regex/commit/f3f9cbb) |
| Why allowed | HaGeZi's DynDNS list blocks it. Checked 2026-11-21: `dyndns.txt` contains `\|\|fairuse.org^`. The earlier 'fair use information site' label had no source and was dropped. | Direct check |

### `g2a.com`

G2A.COM website - No list in this collection blocks it now; Block List Project's fraud list did until 11.13.2026

| Shows | Evidence | Source |
| --- | --- | --- |
| Why allowed | Block List Project's fraud list blocks it. Block List Project lists that contain it: `fraud` | Block List Project archive |
| Observed | Not blocked by this collection. Checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13. | Gravity check |

### `www.g2a.com`

G2A.COM website - No list in this collection blocks it now; Block List Project's fraud list did until 11.13.2026

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | G2A runs it. TLS certificate subject: `G2A.COM Limited` | TLS certificate |
| Why allowed | Block List Project's fraud list blocks it. Block List Project lists that contain it: `fraud` | Block List Project archive |
| Observed | Not blocked by this collection. Checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13. | Gravity check |

### `name.com`

Name.com domain registrar - No list in this collection blocks it now; Block List Project's redirect list did until 11.13.2026

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Domain Names` | Live web page |
| Why allowed | Block List Project's redirect list blocks it. Block List Project lists that contain it: `redirect` | Block List Project archive |
| Observed | Not blocked by this collection. Checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13. | Gravity check |

### `wallpapers.com`

Wallpapers.com - Free wallpaper site - No list in this collection blocks it now; Block List Project's fraud list did until 11.13.2026

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Wallpapers.com` | Live web page |
| Why allowed | Block List Project's fraud list blocks it. Block List Project lists that contain it: `fraud` | Block List Project archive |
| Observed | Not blocked by this collection. Checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13. | Gravity check |

### `www.wallpapers.com`

Wallpapers.com - Free wallpaper site - No list in this collection blocks it now; Block List Project's fraud list did until 11.13.2026

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Wallpapers.com` | Live web page |
| Why allowed | Block List Project's fraud list blocks it. Block List Project lists that contain it: `fraud` | Block List Project archive |
| Observed | Not blocked by this collection. Checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13. | Gravity check |

### `www.trustpilot.com`

Trustpilot website - No list in this collection blocks it now; Block List Project's scam and phishing lists did until 11.13.2026

| Shows | Evidence | Source |
| --- | --- | --- |
| Why allowed | Block List Project's scam list blocks it. Block List Project lists that contain it: `scam` | Block List Project archive |
| Why allowed | Block List Project's phishing list blocks it. Block List Project lists that contain it: `phishing` | Block List Project archive |
| Observed | Not blocked by this collection. Checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13. | Gravity check |

### `bitcoin.org`

Bitcoin project website - Prigent's cryptojacking list (Firebog) blocks it

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Bitcoin` | Live web page |
| Why allowed | Block List Project's crypto list blocks it. Block List Project lists that contain it: `crypto` | Block List Project archive |
| Why allowed | Prigent's cryptojacking list blocks it. Checked 2026-11-21: `https://v.firebog.net/hosts/Prigent-Crypto.txt` contains `bitcoin.org` | Direct check |

### `surveymonkey.com`

SurveyMonkey - Online surveys - No list in this collection blocks it now; Block List Project's malware list did until 11.13.2026

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `SurveyMonkey` | Live web page |
| Why allowed | Block List Project's malware list blocks it. Block List Project lists that contain it: `malware` | Block List Project archive |
| Observed | Not blocked by this collection. Checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13. | Gravity check |

### `secure.surveymonkey.com`

SurveyMonkey host - Listed in anudeep's allowlist

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | anudeep's whitelist lists it: "secure.surveymonkey.com" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |
| Why allowed | Block List Project's ads list blocks it. Block List Project lists that contain it: `ads` | Block List Project archive |

### `bufferapp.com`

Buffer - Social media management (redirects to buffer.com)

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Buffer` | Live web page |
| Why allowed | Block List Project's tracking list blocks it. Block List Project lists that contain it: `tracking` | Block List Project archive |

### `intercom.io`

Intercom website (redirects to intercom.com) - No list in this collection blocks it now; Block List Project's tracking list did until 11.13.2026

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Redirects to Intercom's site. Address the host's web page ends at: `intercom.com` | Live web page |
| Why allowed | Block List Project's tracking list blocks it. Block List Project lists that contain it: `tracking` | Block List Project archive |
| Observed | Not blocked by this collection. Checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13. | Gravity check |

### `insights-collector.gog.com`

GOG-run host - Maintainer reported GOG Galaxy updates need it

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | GOG runs it. TLS certificate subject: `GOG` | TLS certificate |
| Why allowed | Block List Project's tracking list blocks it. Block List Project lists that contain it: `tracking` | Block List Project archive |
| If blocked | Maintainer's first-hand report when it was added: added the line `insights-collector.gog.com -- GOG.com Galaxy updates` | [commit b7c12d6](https://github.com/slyfox1186/pihole-regex/commit/b7c12d6) |

Status: The note repeats the maintainer's earlier report. Decision 2026-11-14: kept. The only evidence is the maintainer's own first-hand breakage report; tracking lists block this one host, and allowing it is narrow.

### `t.paydaythegame.com`

PAYDAY 3 host - Maintainer reported the game needs it to load saved profiles

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Maintainer's original line: added the line `t.paydaythegame.com` | [commit 6df2dbb](https://github.com/slyfox1186/pihole-regex/commit/6df2dbb) |
| Why allowed | Block List Project's tracking list blocks it. Block List Project lists that contain it: `tracking` | Block List Project archive |
| If blocked | Maintainer's first-hand report when it was added: added the line `(0, 't.paydaythegame.com', 1, 'PayDay 3 is a video game and this domain is required to load into your saved profile - SlyEWL')` | [commit 997f633](https://github.com/slyfox1186/pihole-regex/commit/997f633) |

Status: The note repeats the maintainer's earlier report. Decision 2026-11-14: kept. The only evidence is the maintainer's own first-hand breakage report; tracking lists block this one host, and allowing it is narrow.

### `nvidia.tt.omtrdc.net`

Adobe-run host (omtrdc.net) for nvidia.com - Maintainer reported the Nvidia CUDA Toolkit site needs it

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Adobe runs omtrdc.net. TLS certificate subject: `Adobe Inc.` | TLS certificate |
| Context | Maintainer's earlier note: added the line `nvidia.tt.omtrdc.net -- Adobe Target for nvidia.com - Allowed for the Nvidia CUDA Toolkit website` | [commit 652f298](https://github.com/slyfox1186/pihole-regex/commit/652f298) |
| If blocked | Maintainer's first-hand report when it was added: added the line `nvidia.tt.omtrdc.net -- Nvidia CUDA SDK Toolkit Website` | [commit b871acb](https://github.com/slyfox1186/pihole-regex/commit/b871acb) |

Status: The note repeats the maintainer's earlier report. Decision 2026-11-14: kept. The only evidence is the maintainer's own first-hand breakage report; tracking lists block this one host, and allowing it is narrow.

### `7ba3f64df98de730df38846b54ecfbdf7f61f80f.cws.conviva.com`

Conviva host - Maintainer reported Disney+ watch history needs it

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Conviva runs it. TLS certificate subject: `Conviva Inc.` | TLS certificate |
| Why allowed | Block List Project's basic list blocks it. Block List Project lists that contain it: `basic` | Block List Project archive |
| Context | Maintainer's earlier note: added the line `7ba3f64df98de730df38846b54ecfbdf7f61f80f.cws.conviva.com -- Conviva video analytics host - Disney+ saves The Simpsons watch history through it` | [commit 0a7a3ac](https://github.com/slyfox1186/pihole-regex/commit/0a7a3ac) |
| If blocked | Maintainer's first-hand report when it was added: added the line `7ba3f64df98de730df38846b54ecfbdf7f61f80f.cws.conviva.com -- Saves your watch history for The Simpons on Disney Plus` | [commit 52189ee](https://github.com/slyfox1186/pihole-regex/commit/52189ee) |

Status: The note repeats the maintainer's earlier report. Decision 2026-11-14: kept. The only evidence is the maintainer's own first-hand breakage report; tracking lists block this one host, and allowing it is narrow.

### `privacyportal-de.onetrust.com`

OneTrust privacy portal host - Maintainer added it for Nvidia Shield TV

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Maintainer's original line: added the line `(0, 'privacyportal-de.onetrust.com', 1, 'Nvidia Shield TV - SlyEWL')` | [commit 873a89b](https://github.com/slyfox1186/pihole-regex/commit/873a89b) |
| What it does | Page title. Title of the page the host serves: `DS Portal` | Live web page |

### `js.stripe.com`

Stripe host - Maintainer added it for Indiegogo payments

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Stripe runs it. TLS certificate subject: `Stripe` | TLS certificate |
| If blocked | Maintainer's original line: added the line `(0, 'js.stripe.com', 1, 'Indiegogo - SlyEWL')` | [commit 873a89b](https://github.com/slyfox1186/pihole-regex/commit/873a89b) |
| Observed | Looked up 51 times by the maintainer's desktop PC. Lookups on the maintainer's network, by device type (Linux desktop PC): `51` | Pi-hole query log |

Status: The note repeats the maintainer's earlier report.

### `images.ctfassets.net`

ctfassets.net image host - Maintainer added it for AdultTime icons

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Maintainer's original line: added the line `(0, 'images.ctfassets.net', 1, 'AdultTime.com - Icons - SlyEWL')` | [commit c49ceeb](https://github.com/slyfox1186/pihole-regex/commit/c49ceeb) |

Status: The note repeats the maintainer's earlier report.

### `connect.ubisoft.com`

Ubisoft Connect - Maintainer reported it is needed to buy items in the Ubisoft desktop app

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Redirects to Ubisoft Connect. Title of the page the host serves: `Ubisoft Connect` | Live web page |
| If blocked | Maintainer's original line: added the line `(0, 'connect.ubisoft.com', 1, 'Required to buy items from the Ubisoft Desktop App - SlyEWL')` | [commit c49ceeb](https://github.com/slyfox1186/pihole-regex/commit/c49ceeb) |

### `connectivity.pod1.avatar.ext.hp.com`

HP host - Maintainer reported it is required to activate a new printer from the Windows app

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | HP runs it. TLS certificate subject: `HP Inc` | TLS certificate |
| If blocked | Maintainer's original line: added the line `connectivity.pod1.avatar.ext.hp.com -- HP Printers - Required to activate a new printer using the software app on Windows.` | [commit a913bbc](https://github.com/slyfox1186/pihole-regex/commit/a913bbc) |

### `bbuseruploads.s3.amazonaws.com`

Amazon S3 bucket - Maintainer added it to download x264 source code

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Maintainer's original line: added the line `bbuseruploads.s3.amazonaws.com -- Required to build the Linux package x264 from source code.` | [commit ac2658d](https://github.com/slyfox1186/pihole-regex/commit/ac2658d) |

Status: The note repeats the maintainer's earlier report.

### `d29g4g2dyqv443.cloudfront.net`

CloudFront host - Maintainer added it for the Nvidia CUDA Toolkit website

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Maintainer's original line: added the line `d29g4g2dyqv443.cloudfront.net -- Nvidia CUDA SDK Toolkit Website` | [commit b871acb](https://github.com/slyfox1186/pihole-regex/commit/b871acb) |

Status: The note repeats the maintainer's earlier report. CloudFront does not show the customer.

### `dirms4qsy6412.cloudfront.net`

CloudFront host - Maintainer added it for the Nvidia CUDA Toolkit website

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Maintainer's original line: added the line `dirms4qsy6412.cloudfront.net -- Nvidia CUDA SDK Toolkit Website` | [commit b871acb](https://github.com/slyfox1186/pihole-regex/commit/b871acb) |

Status: The note repeats the maintainer's earlier report. CloudFront does not show the customer.

### `dcape-na.amazon.com`

Amazon host - Maintainer added it to sign in to Amazon apps on Windows Subsystem for Android

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Maintainer's original line: added the line `dcape-na.amazon.com -- Required to login to Amazon using Windows Android Subsystem for Linux` | [commit b7c12d6](https://github.com/slyfox1186/pihole-regex/commit/b7c12d6) |
| Context | Perflyst lists it under Fire TV 'others (unknown usage)': the page lists `dcape-na.amazon.com` under the heading "others (unknown usage)" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/AmazonFireTV.txt) |

### `api.themoviedb.org`

The Movie Database (TMDB) API - Maintainer added it for Plex metadata

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Redirects to TMDB developer docs. Address the host's web page ends at: `developer.themoviedb.org` | Live web page |
| Context | Maintainer's original line: added the line `api.themoviedb.org -- Plex Media Server - The Movie Database metadata` | [commit f3f9cbb](https://github.com/slyfox1186/pihole-regex/commit/f3f9cbb) |

Status: The note repeats the maintainer's earlier report.

### `signin.nexon.com`

Nexon sign-in host - Maintainer added it for The First Descendant

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Nexon runs it. TLS certificate subject: `NEXON Korea Corporation` | TLS certificate |
| If blocked | Maintainer's original line: added the line `signin.nexon.com -- The First Decendant` | [commit b871acb](https://github.com/slyfox1186/pihole-regex/commit/b871acb) |

### `static-assets-prod.unrealengine.com`

Epic Games (unrealengine.com) host - Maintainer added it to load the Epic Games desktop app

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Maintainer's original line: added the line `static-assets-prod.unrealengine.com -- Load the Epic Games desktop app` | [commit 52189ee](https://github.com/slyfox1186/pihole-regex/commit/52189ee) |

Status: The note repeats the maintainer's earlier report.

### `static-cdn.jtvnw.net`

jtvnw.net host - Maintainer added it to load Twitch icons

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Maintainer's original line: added the line `static-cdn.jtvnw.net -- Required to load icons` | [commit 5c124ab](https://github.com/slyfox1186/pihole-regex/commit/5c124ab) |

Status: The note repeats the maintainer's earlier report.

### `sh.rustup.rs`

Rust - rustup installer script

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Maintainer's original line: added the line `sh.rustup.rs -- RustUp Linux Install Script` | [commit b871acb](https://github.com/slyfox1186/pihole-regex/commit/b871acb) |

### `static.rust-lang.org`

Rust host - Maintainer added it for the rustup install script

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Maintainer's original line: added the line `static.rust-lang.org -- RustUp Linux Install Script` | [commit b871acb](https://github.com/slyfox1186/pihole-regex/commit/b871acb) |

### `index.crates.io`

crates.io package index

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `The crates.io package index` | Live web page |

### `www.duplicatephotocleaner.com`

Duplicate Photo Cleaner - Duplicate photo finder app site

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Duplicate Photo` | Live web page |

### `www.vbsedit.com`

VbsEdit - VBScript editor

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `VbsEdit` | Live web page |

### `tcr9i.chat.openai.com`

OpenAI ChatGPT - Service host the maintainer added for the ChatGPT desktop app

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Maintainer's original line: added the line `tcr9i.chat.openai.com -- Allows you to send queries to the ChatGPT AI using their desktop app` | [commit 52189ee](https://github.com/slyfox1186/pihole-regex/commit/52189ee) |
| Observed | CNAME to openai.com. DNS CNAME chain: `openai.com.` | Direct check |

### `api.gitkraken.com`

GitKraken host (gitkraken.com)

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Responds over HTTPS. Address the host's web page ends at: `api.gitkraken.com` | Live web page |

Status: Purpose unverified. The original line called it 'GitHub - Advanced Git CLI Program'; its role is unverified.

### `api.termius.com`

Termius SSH client host (redirects to termius.com)

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Redirects to Termius. Title of the page the host serves: `Termius` | Live web page |

Status: Purpose unverified. The old note said it is required to sign in; not verified.

### `maxcdn.bootstrapcdn.com`

BootstrapCDN - A tested Bootstrap file matched Bootstrap's published integrity hash

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Integrity check. Library integrity check (full record): 2026-11-13: https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css has sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u, the integrity hash getbootstrap.com publishes for Bootstrap 3.3.7 | File comparison |

### `stackpath.bootstrapcdn.com`

BootstrapCDN - Serves Bootstrap files

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Integrity check. Library integrity check (full record): 2026-11-13: https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js returned 60,044 bytes of JavaScript whose header reads Bootstrap v4.5.2 (header checked, not hash-compared) | File comparison |

### `netdna.bootstrapcdn.com`

BootstrapCDN - Serves Font Awesome files

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Integrity check. Library integrity check (full record): 2026-11-13: https://netdna.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css returned 31,000 bytes of CSS whose header reads Font Awesome 4.7.0 (header checked, not hash-compared) | File comparison |

### `unpkg.com`

unpkg - npm package CDN; a tested jQuery file matched the official copy

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `UNPKG` | Live web page |
| What it does | Integrity check. Library integrity check (full record): 2026-11-13: https://unpkg.com/jquery@3.6.0/dist/jquery.min.js compared byte-for-byte with https://code.jquery.com/jquery-3.6.0.min.js: identical (SHA-256 tested ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e, reference ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e) | File comparison |

### `lib.baomitu.com`

baomitu.com public JavaScript library CDN (China) - A tested jQuery file matched the official copy

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Integrity check. Library integrity check (full record): 2026-11-13: https://lib.baomitu.com/jquery/3.6.0/jquery.min.js compared byte-for-byte with https://code.jquery.com/jquery-3.6.0.min.js: identical (SHA-256 tested ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e, reference ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e) | File comparison |

### `lib.baomitu.com.qh-cdn.com`

CNAME target of lib.baomitu.com - Kept so CNAME-inspecting blockers do not block that library CDN

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | lib.baomitu.com points here. DNS CNAME chain of `lib.baomitu.com`: `lib.baomitu.com.qh-cdn.com.` | Direct check |

### `libs.baidu.com`

Baidu public JavaScript library CDN (China) - A tested jQuery file matched the official copy

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Baidu runs it. TLS certificate subject: `Beijing Baidu Netcom` | TLS certificate |
| What it does | Integrity check. Library integrity check (full record): 2026-11-13: https://libs.baidu.com/jquery/2.0.0/jquery.min.js compared byte-for-byte with https://code.jquery.com/jquery-2.0.0.min.js after converting CRLF line endings: identical (SHA-256 tested 91e8044a4b1bfce3c131d5579965a9808b42cdb9a350a53928d54cd35d6c1451, reference d482871a5e948cb4884fa0972ea98a81abca057b6bd3f8c995a18c12487e761c) | File comparison |

### `developer.n.shifen.com`

Baidu host - CNAME target of libs.baidu.com

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Baidu certificate. TLS certificate subject: `Beijing Baidu Netcom` | TLS certificate |
| What it does | libs.baidu.com points here. DNS CNAME chain of `libs.baidu.com`: `developer.n.shifen.com.` | Direct check |

### `upcdn.b0.upaiyun.com`

Upyun (China) JavaScript library CDN - A tested jQuery file matched the official copy

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Page title is Upyun's JS library service. Title of the page the host serves: `JS` | Live web page |
| What it does | Integrity check. Library integrity check (full record): 2026-11-13: https://upcdn.b0.upaiyun.com/libs/jquery/jquery-2.0.2.min.js compared byte-for-byte with https://code.jquery.com/jquery-2.0.2.min.js: identical (SHA-256 tested 4d9586a075f082a04fd40178499c472012b351db4c1a4d210907a0891f7d8ad9, reference 4d9586a075f082a04fd40178499c472012b351db4c1a4d210907a0891f7d8ad9) | File comparison |

### `vo.aicdn.com`

CNAME target of upcdn.b0.upaiyun.com

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | upcdn.b0.upaiyun.com points here. DNS CNAME chain of `upcdn.b0.upaiyun.com`: `vo.aicdn.com.` | Direct check |

### `sdn.geekzu.org`

Geekzu public library CDN (China) - A tested jQuery file matched the official copy

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Integrity check. Library integrity check (full record): 2026-11-13: https://sdn.geekzu.org/ajax/ajax/libs/jquery/3.6.0/jquery.min.js compared byte-for-byte with https://code.jquery.com/jquery-3.6.0.min.js: identical (SHA-256 tested ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e, reference ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e) | File comparison |

### `sdn.inbond.gslb.geekzu.org`

geekzu.org host - Former CNAME target of sdn.geekzu.org

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Resolves via another Geekzu host. DNS CNAME chain: `outbond.gslb.geekzu.org.` | Direct check |
| Observed | sdn.geekzu.org no longer CNAMEs here. DNS status of `sdn.geekzu.org`: `NOERROR` | DNS lookup |

Note: Decision 2026-11-14: kept. No longer a current CNAME target, but no list in this repo's adlists blocks it, so the allow changes nothing.

### `fonts.loli.net`

loli.net Google Fonts mirror (China) - Served Google Fonts CSS when tested

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Integrity check. Library integrity check (full record): 2026-11-13: https://fonts.loli.net/css?family=Roboto returned Google Fonts CSS (@font-face rules for Roboto) | File comparison |

### `fonts.loli.net.cdn.cloudflare.net`

Cloudflare CNAME target of fonts.loli.net (Google Fonts mirror)

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | fonts.loli.net points here. DNS CNAME chain of `fonts.loli.net`: `fonts.loli.net.cdn.cloudflare.net.` | Direct check |

### `use.fontawesome.com`

Font Awesome - Icon font CDN (served Font Awesome 5.15.4 CSS when tested)

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Integrity check. Library integrity check (full record): 2026-11-13: https://use.fontawesome.com/releases/v5.15.4/css/all.css returned CSS whose header reads Font Awesome Free 5.15.4 (header checked, not hash-compared) | File comparison |

### `use.fontawesome.com.cdn.cloudflare.net`

Cloudflare CNAME target of use.fontawesome.com (Font Awesome)

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | use.fontawesome.com points here. DNS CNAME chain of `use.fontawesome.com`: `use.fontawesome.com.cdn.cloudflare.net.` | Direct check |

### `mathjax.rstudio.com`

MathJax library CDN on rstudio.com - Served MathJax 2.7.9 when tested

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Integrity check. Library integrity check (full record): 2026-11-13: https://mathjax.rstudio.com/latest/MathJax.js redirected to /2.7.9/MathJax.js, a file with the MathJax Consortium header: serves MathJax 2.7.9 | File comparison |

### `materialdesignicons.b-cdn.net`

Material Design Icons host - Redirects to jsDelivr

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Integrity check. Library integrity check (full record): 2026-11-13: https://materialdesignicons.b-cdn.net/ redirects to cdn.jsdelivr.net/mdi/ | File comparison |

### `mat1.gtimg.com`

Tencent static file host (China) - No list in this collection blocks it now; Block List Project's malware and abuse lists did until 11.13.2026

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Tencent certificate (Chinese company name). TLS certificate subject: `E8` | TLS certificate |
| Why allowed | Block List Project malware list. Block List Project lists that contain it: `malware` | Block List Project archive |
| Observed | Not blocked by this collection. Checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13. | Gravity check |

Note: Decision 2026-11-14: kept. Kept from the 2022 'crucial CDN' set; no list currently in this repo's adlists blocks it.

### `mat1.gtimg.com.tegsea.tc.qq.com`

Tencent host - Former CNAME target of mat1.gtimg.com

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Tencent certificate. TLS certificate subject: `Shenzhen Tencent Computer Systems` | TLS certificate |
| Observed | mat1.gtimg.com now resolves through a different chain. DNS CNAME chain of `mat1.gtimg.com`: `ovscdns` | Direct check |

Note: Decision 2026-11-14: kept. No longer a current CNAME target, but no list in this repo's adlists blocks it, so the allow changes nothing.

### `gateway.cname.ustclug.org`

gateway.cname.ustclug.org - Role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Resolves. DNS status: `NOERROR` | DNS lookup |

Status: Purpose unverified. Kept from the 2022 'crucial CDN' set; nothing documents what points here.

### `dualstack.osff.map.fastly.net`

Fastly host (map.fastly.net) - Which site uses it is unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Looked up once by the maintainer's iPhone. Lookups on the maintainer's network, by device type (iPhone): `1` | Pi-hole query log |

Status: Purpose unverified. No current CNAME in the lists points here; kept from the 2022 'crucial CDN' set.

### `jquery.com`

jQuery project website

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `jQuery` | Live web page |

### `players.brightcove.net`

Brightcove video player host - Listed in anudeep's allowlist

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Fastly CNAME for Brightcove. DNS CNAME chain: `dualstack.brightcove.map.fastly.net.` | Direct check |
| Context | anudeep's whitelist lists it: "players.brightcove.net" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |

### `ssl.p.jwpcdn.com`

JW Player host - Listed in anudeep's allowlist

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Fastly CNAME for JW Player. DNS CNAME chain: `jwplayer-dualstack.map.fastly.net.` | Direct check |
| Context | anudeep's whitelist lists it: "ssl.p.jwpcdn.com" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |

### `res.cloudinary.com`

Cloudinary host - Listed in anudeep's allowlist

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Cloudinary runs it. TLS certificate subject: `Cloudinary Ltd` | TLS certificate |
| Context | anudeep's whitelist lists it: "res.cloudinary.com" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |

### `imgix.net`

imgix.net - Listed in anudeep's allowlist

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep's whitelist lists it: "imgix.net" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |

Note: Only the bare domain; it has no HTTPS site.

### `lastfm-img2.akamaized.net`

Akamai host lastfm-img2 - Listed in anudeep's allowlist

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep's whitelist lists it: "lastfm-img2.akamaized.net" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |

### `hls.ted.com`

TED (ted.com) host - Listed in anudeep's allowlist

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep's whitelist lists it: "hls.ted.com" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |

### `vidtech.cbsinteractive.com`

CBS Interactive host - Redirects to avia.cbsivideo.com

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Redirects to avia.cbsivideo.com. Address the host's web page ends at: `avia.cbsivideo.com` | Live web page |
| Context | anudeep's whitelist lists it: "vidtech.cbsinteractive.com" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |

### `traffic.libsyn.com`

Libsyn (podcast hosting platform) host - Listed in anudeep's allowlist

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Libsyn runs it. TLS certificate subject: `LIBERATED SYNDICATION` | TLS certificate |
| Context | anudeep's whitelist lists it: "traffic.libsyn.com" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |

### `secure.avangate.com`

2Checkout (Verifone) host - Redirects to 2checkout.com

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Verifone runs it. TLS certificate subject: `Verifone` | TLS certificate |
| Observed | Redirects to 2Checkout. Address the host's web page ends at: `2checkout.com` | Live web page |

### `keystone.mwbsys.com`

Malwarebytes host - Virus definition updates fail when it is blocked (yhosts issue #163)

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | yhosts issue #163: "makes malwarebytes unable to install updated virus definitions" | [vokins/yhosts #163](https://github.com/vokins/yhosts/issues/163) |
| Context | anudeep's whitelist lists it: "keystone.mwbsys.com" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |

### `keyserver.ubuntu.com`

Ubuntu OpenPGP key server

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `OpenPGP Keyserver` | Live web page |

### `codeload.github.com`

GitHub host - Used by the maintainer's desktop PC

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Used by the maintainer's desktop PC. Lookups on the maintainer's network, by device type (Linux desktop PC): `4` | Pi-hole query log |

### `objects.githubusercontent.com`

GitHub content host

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Resolves. DNS status: `NOERROR` | DNS lookup |

Status: Purpose unverified. Exact role unverified.

### `raw.githubusercontent.com`

GitHub raw file host - This repo's scripts download their lists from it

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | pi.py downloads the lists from raw.githubusercontent.com: "raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains" | [slyfox1186/pihole-regex (GitHub)](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/pi.py) |
| Observed | Used by the maintainer's desktop PC. Lookups on the maintainer's network, by device type (Linux desktop PC): `69` | Pi-hole query log |

### `mirror.clarkson.edu`

Clarkson University mirror site

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `mirror.clarkson.edu` | Live web page |

### `mirror.umd.edu`

University of Maryland free software mirror

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `University of Maryland Free Software Mirror` | Live web page |

### `mirror.msys2.org`

MSYS2 package mirror - Redirects to repo.msys2.org

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Redirects to repo.msys2.org. Address the host's web page ends at: `repo.msys2.org` | Live web page |
| Context | Maintainer's original line: added the line `(0, 'mirror.msys2.org', 1, 'MSys2 - Required CDN for sourcing and build packages - SlyEWL')` | [commit f6af928](https://github.com/slyfox1186/pihole-regex/commit/f6af928) |

### `gs-loc.ls-apple.com.akadns.net`

Apple Location Services (Wi-Fi and cell positioning) - Target of gs-loc.apple.com

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Apple certificate. TLS certificate subject: `Apple Inc.` | TLS certificate |
| What it does | gs-loc.apple.com resolves to it. Related DNS lookup (full record): gs-loc.apple.com CNAME gs-loc-new.ls-apple.com.akadns.net CNAME gs-loc.ls-apple.com.akadns.net (unbound, 2026-11-13) | Direct check |
| What it does | Research paper on iOS location services: "to Apple server gs-loc.apple.com/clls/wloc , which responds with the locations of nearby Wi-Fi networks and cell towers" | [arxiv.org](https://arxiv.org/html/2610.21597v1) |
| Observed | Looked up by the maintainer's iPhone. Lookups on the maintainer's network, by device type (iPhone): `5` | Pi-hole query log |

### `icloud.com`

Apple iCloud website

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Apple runs it. TLS certificate subject: `Apple Inc.` | TLS certificate |
| What it does | Site title. Title of the page the host serves: `iCloud` | Live web page |
| Context | Apple lists *.icloud.com for iCloud services: "*.icloud.com 443 TCP iOS, iPadOS, tvOS, macOS, and visionOS iCloud services" | [support.apple.com](https://support.apple.com/en-us/101555) |

### `upload.appleschoolcontent.com`

Apple host - Apple lists it for SFTP uploads

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Apple's network requirements: "upload.appleschoolcontent.com 22 SSH - SFTP uploads" | [support.apple.com](https://support.apple.com/en-us/101555) |

### `play.google.com`

Google Play Store

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Redirects into the Play Store. Address the host's web page ends at: `play.google.com/store` | Live web page |
| Observed | Used by the maintainer's desktop PC. Lookups on the maintainer's network, by device type (Linux desktop PC): `67` | Pi-hole query log |

### `play-lh.googleusercontent.com`

Google host - Maintainer added it for the Google Play Store

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Maintainer's original line: added the line `play-lh.googleusercontent.com -- Google play Store` | [commit b7c12d6](https://github.com/slyfox1186/pihole-regex/commit/b7c12d6) |

Status: The note repeats the maintainer's earlier report.

### `lh3.googleusercontent.com`

Google user content host - Used heavily by the maintainer's desktop and iPhone

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Used heavily by the maintainer's desktop and iPhone. Lookups on the maintainer's network, by device type (Linux desktop PC): `152` | Pi-hole query log |

Note: The old note said Nvidia Shield TV apps break without it; no source found.

### `googlehosted.l.googleusercontent.com`

Google hosting CNAME target (googleusercontent.com) - Role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Resolves. DNS status: `NOERROR` | DNS lookup |

Status: Purpose unverified. No source describes it.

### `graph.oculus.com`

Oculus (Meta) host

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Meta runs it. TLS certificate subject: `Meta Platforms` | TLS certificate |
| Observed | CNAME into Facebook. DNS CNAME chain: `oculus.c10r.facebook.com.` | Direct check |
| Why allowed | Block List Project's Facebook list blocks it. Block List Project lists that contain it: `facebook` | Block List Project archive |

### `edge.gycpi.b.yahoodns.net`

Yahoo-run edge host (yahoodns.net)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Yahoo runs it. TLS certificate subject: `Yahoo Holdings` | TLS certificate |

Status: Purpose unverified. The old note said Yahoo breaks without it; not verified.

### `my.plexapp.com`

Plex host - Redirects to watch.plex.tv

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Redirect. Address the host's web page ends at: `watch.plex.tv` | Live web page |
| Why allowed | Block List Project's ads list blocks it. Block List Project lists that contain it: `ads` | Block List Project archive |

### `ws.audioscrobbler.com`

Last.fm API - Listed in anudeep's allowlist

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Last.fm API` | Live web page |
| Context | anudeep's whitelist lists it: "ws.audioscrobbler.com" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |

### `client-rapi.recombee.us`

Recombee host - Maintainer labeled it for AdultTime

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Responds 401 without a token. Address the host's web page ends at: `client-rapi.recombee.us` | Live web page |
| Context | Maintainer's earlier note: added the line `client-rapi.recombee.us -- Recombee recommendations API (AdultTime)` | [commit 652f298](https://github.com/slyfox1186/pihole-regex/commit/652f298) |

Status: The note repeats the maintainer's earlier report. Recombee documents client-rapi.recombee.com; the .us host is not documented.

### `members.adulttime.com`

AdultTime - Member sign-in site

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Redirects to AdultTime login. Address the host's web page ends at: `adulttime.com/en/login` | Live web page |

### `rover.ebay.com`

eBay-run host (rover.ebay.com)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | eBay runs it. TLS certificate subject: `eBay Inc.` | TLS certificate |

Status: Purpose unverified. The old note said eBay links pass through it; not verified.

### `best.aliexpress.com`

AliExpress shopping site

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Alibaba certificate. TLS certificate subject: `Alibaba` | TLS certificate |
| What it does | Site title. Title of the page the host serves: `AliExpress` | Live web page |

### `login.aliexpress.com`

AliExpress - Sign-in

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Alibaba certificate. TLS certificate subject: `Alibaba` | TLS certificate |
| Observed | Redirects to the login page. Address the host's web page ends at: `login` | Live web page |

### `www.aliexpress.com`

AliExpress shopping site

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Alibaba certificate. TLS certificate subject: `Alibaba` | TLS certificate |

### `play.kayosports.com.au`

Kayo Sports (Hubbl) host

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Hubbl (Kayo's owner) certificate. TLS certificate subject: `Hubbl Pty Ltd` | TLS certificate |

### `t.co`

t.co - X (Twitter) domain

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `t.co` | Live web page |

### `j.mp`

Bitly short link domain

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Bitly page. Title of the page the host serves: `Bitly` | Live web page |

### `tinyurl.com`

TinyURL - URL shortener

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `URL Shortener` | Live web page |

### `linkedin.com`

LinkedIn website

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | LinkedIn runs it. TLS certificate subject: `Linkedin Corporation` | TLS certificate |

### `pinterest.com`

Pinterest

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Pinterest runs it. TLS certificate subject: `Pinterest` | TLS certificate |
| What it does | Site title. Title of the page the host serves: `Pinterest` | Live web page |

### `color.adobe.com`

Adobe Color - Color palette tool

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Adobe runs it. TLS certificate subject: `Adobe Inc` | TLS certificate |
| What it does | Site title. Title of the page the host serves: `Color Palettes` | Live web page |

### `bugmenot.com`

BugMeNot - Shared logins for sites that force sign-up

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `BugMeNot` | Live web page |

### `giphy.com`

GIPHY website

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `GIPHY` | Live web page |

### `wikipedia.org`

Wikipedia

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Wikipedia` | Live web page |

### `wordpress.com`

WordPress.com website

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `WordPress.com` | Live web page |

### `wp.com`

wp.com - Redirects to wordpress.com

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Redirect. Address the host's web page ends at: `wordpress.com` | Live web page |

### `vimeo.com`

Vimeo - Video platform

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Vimeo` | Live web page |

### `society6.com`

Society6 - Artist-designed prints and home decor shop

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `Society6` | Live web page |

### `www.howtogeek.com`

How-To Geek - Technology help site

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `How-To Geek` | Live web page |

### `www.propublica.org`

ProPublica - Investigative journalism site

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `ProPublica` | Live web page |

### `www.shellcheck.net`

ShellCheck - Shell script checker

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `ShellCheck` | Live web page |

### `www.squaretrade.com`

SquareTrade (Allstate) - Product protection plans

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | SquareTrade runs it. TLS certificate subject: `SquareTrade` | TLS certificate |
| What it does | Site title. Title of the page the host serves: `Allstate Protection Plans` | Live web page |

### `www.solaredge.com`

SolarEdge website

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | SolarEdge runs it. TLS certificate subject: `SolarEdge Technologies` | TLS certificate |

### `dynupdate.no-ip.com`

No-IP host - Listed in anudeep's allowlist

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Root redirects to No-IP. Address the host's web page ends at: `noip.com` | Live web page |
| Context | anudeep's whitelist lists it: "dynupdate.no-ip.com" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |

### `medium.com`

Medium website

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Cloudflare challenge page. Title of the page the host serves: `Just a moment` | Live web page |

### `unsplash.com`

Unsplash website

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Bot-check page. Title of the page the host serves: `unsplash` | Live web page |

### `static.opensubtitles.org`

OpenSubtitles host

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Redirects into opensubtitles.org. Address the host's web page ends at: `opensubtitles.org` | Live web page |

Status: Purpose unverified. Exact role unverified.

### `www.opensubtitles.org`

OpenSubtitles website

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Bot-check page on opensubtitles.org. Address the host's web page ends at: `opensubtitles.org` | Live web page |

### `yastatic.net`

Yandex-run host (redirects to yandex.ru)

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Redirects to Yandex. Address the host's web page ends at: `yandex.ru` | Live web page |

Status: Purpose unverified. Exact role unverified.

### `imgs.xkcd.com`

xkcd host - Listed in anudeep's allowlist

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep's whitelist lists it: "imgs.xkcd.com" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |
| Observed | Fastly CNAME. DNS CNAME chain: `dualstack.i.ssl.global.fastly.net.` | Direct check |

### `d.adguard-dns.com`

AdGuard DNS server - HaGeZi's DoH list blocks it; iPhones with an AdGuard DNS profile cannot load Messages photos without it

| Shows | Evidence | Source |
| --- | --- | --- |
| Why allowed | HaGeZi's DoH/VPN/Proxy list blocks it. The list contains `\|\|adguard-dns.com^` (checked with `pihole -q` on 2026-11-15) | Direct check |
| Observed | Name and address. DNS answer `94.140.14.49`; the TLS certificate is domain-validated (`CN=*.d.adguard-dns.com`), so it does not name the owner | TLS certificate |
| Observed | Maintainer's iPhone. The phone uses an AdGuard DNS profile and asks the network only for this name. From 2026-11-14 20:56, when the DoH list was added, Pi-hole blocked it 1,010 times and photos in Messages stayed on "loading" on home Wi-Fi while they loaded on cellular. Allowing it on 2026-11-15 fixed the photos. | Direct check |

## Exact blocklist: `exact-blacklist.sql` (20 entries)

### `aic.api.lgtviot.com`

LG webOS TV host (lgtviot.com) - Proposed for blocking in HaGeZi issue #309; role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Reported from LG webOS TVs: "LG WebOS domains found on reddit and personally tested" | [hagezi/dns-blocklists #309](https://github.com/hagezi/dns-blocklists/issues/309) |
| Context | Listed in that report: "aic.api.lgtviot.com aic.lgtviot.com ngfts.lge.com" | [hagezi/dns-blocklists #309](https://github.com/hagezi/dns-blocklists/issues/309) |

Status: Purpose unverified. The old note said 'IoT telemetry'; no source states what the host does.

### `aic.lgtviot.com`

LG webOS TV host (lgtviot.com) - Proposed for blocking in HaGeZi issue #309; role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Reported from LG webOS TVs: "LG WebOS domains found on reddit and personally tested" | [hagezi/dns-blocklists #309](https://github.com/hagezi/dns-blocklists/issues/309) |
| Context | Listed in that report: "aic.api.lgtviot.com aic.lgtviot.com ngfts.lge.com" | [hagezi/dns-blocklists #309](https://github.com/hagezi/dns-blocklists/issues/309) |

Status: Purpose unverified. The old note said 'IoT telemetry'; no source states what the host does.

### `aic.sports.lgtviot.com`

LG webOS TV host (lgtviot.com) - Listed in HaGeZi issue #309; role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | HaGeZi #309 notes the name resolves: "aic.sports.lgtviot.com resolves" | [hagezi/dns-blocklists #309](https://github.com/hagezi/dns-blocklists/issues/309) |

Status: Purpose unverified. Only listed, no function stated.

### `qt2-ngfts.lge.com`

LG host sharing ngfts.lge.com's Akamai name - Proposed for blocking in HaGeZi #309; role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | LG Electronics runs it. TLS certificate subject: `O = LG Electronics Inc.` | TLS certificate |
| Context | Proposed in that LG webOS report: "canvas.tubitv.com qt2-ngfts.lge.com" | [hagezi/dns-blocklists #309](https://github.com/hagezi/dns-blocklists/issues/309) |
| Observed | Same Akamai host as the allowed ngfts.lge.com. DNS CNAME chain: `e6114.e21.akamaiedge.net.` | Direct check |

Status: Purpose unverified; needs the maintainer's decision. It shares ngfts.lge.com's CNAME and 'SDP 2.0' page; blocking may affect LG Content Store images. The old 'file transfer' note had no source.

### `www.ueiwsp.com`

Universal Electronics QuickSet Cloud API - LG TVs use it to detect HDMI devices; reports conflict on whether blocking breaks LG Universal Control

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Technical write-up of LG TV traffic: "www.ueiwsp.com is the QuickSet Cloud API from Universal Electronics, the company behind LG's device discovery and control feature that recognizes the soundbar or console plugged into an HDMI port" | [vdaluz.com](https://vdaluz.com/blog/lg-tv-telemetry-pihole-adblock-lists) |
| Context | Proposed for blocking in the LG webOS report (HaGeZi #309): "us.lgtvsdp.com www.ueiwsp.com" | [hagezi/dns-blocklists #309](https://github.com/hagezi/dns-blocklists/issues/309) |
| Observed | Looked up by the maintainer's Samsung device and LG TV. Lookups on the maintainer's network, by device type (Samsung device): `6` | Pi-hole query log |
| If blocked | A report that blocking it stops QuickSet remote-code lookup: "That is the UEI QuickSet code lookup, roughly every 5 to 10 minutes." | [lewisdoesstuff/lifesgoodwithoutspying #3](https://github.com/lewisdoesstuff/lifesgoodwithoutspying/issues/3) |
| If blocked | A tested report that Universal Control still worked with it blocked: "Universal Control all work, the last one with `ueiwsp.com` blocked" | [furkan-bayrak/lg-tv-blocklist #24](https://github.com/furkan-bayrak/lg-tv-blocklist/issues/24) |

Note: Decision 2026-11-14: kept. A HaGeZi #309 reporter blocked it with no breakage after testing; one later user also reported LG Universal Control still worked.

### `lgtvonline.lge.com`

LG webOS TV online service host - Role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Looked up by the maintainer's LG webOS TV. Lookups on the maintainer's network, by device type (LG webOS TV): `1` | Pi-hole query log |

Status: Purpose unverified. No source describes it.

### `datarouter.ol.epicgames.com`

Epic Games data collection (hardware, operating system and app performance data) - Data Router

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | HaGeZi issue #5301: "The domain is used by Epic Games for data collection, including hardware, operating system details, and application performance data." | [hagezi/dns-blocklists #5301](https://github.com/hagezi/dns-blocklists/issues/5301) |
| Context | Blocked by this repo as Epic telemetry: commit message: "Block Reddit event collectors and Epic Games telemetry" | [commit 10a4010](https://github.com/slyfox1186/pihole-regex/commit/10a4010) |
| Observed | Block List Project's tracking list also blocks it. Block List Project lists that contain it: `tracking` | Block List Project archive |

### `metric-public-service-prod.ol.epicgames.com`

Epic Games telemetry - Resolves to the same Data Router service

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | CNAME to Epic's datarouter service. DNS CNAME chain: `datarouter.cfef.live.use1a.on.epicgames.com.` | Direct check |
| Context | Blocked by this repo as Epic telemetry: commit message: "Epic Games telemetry" | [commit 10a4010](https://github.com/slyfox1186/pihole-regex/commit/10a4010) |
| Observed | Block List Project's tracking list also blocks it. Block List Project lists that contain it: `tracking` | Block List Project archive |

### `events-test.redditmedia.com`

Reddit-run host - Maintainer labeled it an event collector; exact role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Reddit runs it. TLS certificate subject: `Reddit` | TLS certificate |
| Context | Blocked by this repo as a Reddit event collector: commit message: "Block Reddit event collectors" | [commit 10a4010](https://github.com/slyfox1186/pihole-regex/commit/10a4010) |
| Context | Maintainer's earlier note: added the line `events-test.redditmedia.com -- Reddit event collector (same service as events.redditmedia.com)` | [commit 10a4010](https://github.com/slyfox1186/pihole-regex/commit/10a4010) |

Status: The note repeats the maintainer's earlier report; purpose unverified.

### `events-test-v2.redditmedia.com`

Reddit-run host - Maintainer labeled it an event collector; exact role unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Reddit runs it. TLS certificate subject: `Reddit` | TLS certificate |
| Context | Blocked by this repo as a Reddit event collector: commit message: "Block Reddit event collectors" | [commit 10a4010](https://github.com/slyfox1186/pihole-regex/commit/10a4010) |
| Context | Maintainer's earlier note: added the line `events-test-v2.redditmedia.com -- Reddit event collector (same service as events.redditmedia.com)` | [commit 10a4010](https://github.com/slyfox1186/pihole-regex/commit/10a4010) |

Status: The note repeats the maintainer's earlier report; purpose unverified.

### `usage.truenas.com`

TrueNAS analytics data collection host

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | TrueNAS security docs: "Analytics data collection to https://usage.truenas.com/submit" | [www.truenas.com](https://www.truenas.com/docs/solutions/optimizations/security/) |

### `banners.hangmyads.com`

HangMyAds ad network (Portugal) - Maintainer labeled this host as serving banner ads

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | HangMyAds is an ad network: "We are an Ad Network based in Portugal" | [hangmyads.com](https://hangmyads.com/) |
| Context | Blocked by this repo: commit message: "Block the HangMyAds ad network's banner host" | [commit 2c53c1f](https://github.com/slyfox1186/pihole-regex/commit/2c53c1f) |
| Observed | mmotti's original banner regex also blocks it. Mmotti's regexes that match it (tested with pihole-FTL): `banners` | pihole-FTL test |
| Context | Maintainer's earlier note: added the line `banners.hangmyads.com -- HangMyAds ad network banners` | [commit 2c53c1f](https://github.com/slyfox1186/pihole-regex/commit/2c53c1f) |

Status: The note repeats the maintainer's earlier report.

### `codes.iobit.com`

IObit host - Maintainer reported it serves in-app pop-up ads

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Akamai CNAME. DNS CNAME chain: `a117.dscd.akamai.net.` | Direct check |
| Context | Maintainer's earlier note: added the line `codes.iobit.com -- IObit desktop app pop-up ads` | [commit 0a7a3ac](https://github.com/slyfox1186/pihole-regex/commit/0a7a3ac) |

Status: The note repeats the maintainer's earlier report.

### `giveaway.iobit.com`

IObit host - Maintainer labeled it IObit promotions

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Resolves. DNS status: `NOERROR` | DNS lookup |
| Context | Maintainer's earlier note: added the line `giveaway.iobit.com -- IObit promotions` | [commit f3f9cbb](https://github.com/slyfox1186/pihole-regex/commit/f3f9cbb) |

Status: The note repeats the maintainer's earlier report.

### `survey.iobit.com`

IObit host - Maintainer labeled it IObit surveys

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Resolves. DNS status: `NOERROR` | DNS lookup |
| Context | Maintainer's earlier note: added the line `survey.iobit.com -- IObit surveys` | [commit f3f9cbb](https://github.com/slyfox1186/pihole-regex/commit/f3f9cbb) |

Status: The note repeats the maintainer's earlier report.

### `api.itopvpn.com`

iTop VPN host - Maintainer reported it as telemetry

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Maintainer's original line: added the line `(1, 'api.itopvpn.com', 1, 'iTop VPN Telemetry - SlyEBL')` | [commit c377502](https://github.com/slyfox1186/pihole-regex/commit/c377502) |
| Observed | Its root page redirects to google.com. Address the host's web page ends at: `www.google.com` | Live web page |

Status: The note repeats the maintainer's earlier report.

### `bench.utorrent.com`

uTorrent host - Maintainer reported it serves ads in the desktop app

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Older ad hostnames under it were in blocklists: added the line `i-1006.b-0.ad.bench.utorrent.com` | [commit d56660b](https://github.com/slyfox1186/pihole-regex/commit/d56660b) |
| Context | Maintainer's earlier note: added the line `bench.utorrent.com -- uTorrent desktop app ads` | [commit f3f9cbb](https://github.com/slyfox1186/pihole-regex/commit/f3f9cbb) |

Status: The note repeats the maintainer's earlier report.

### `prod.ups-ats.us-east-1.aolp-ds-prd.aws.oath.cloud`

oath.cloud host whose CNAME names an online-targeting service

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | CNAME to Oath's online targeting service. DNS CNAME chain: `dcs-online-targeting-prd.aws.oath.cloud.` | Direct check |

### `mindfieldonline.com`

MindField website - Maintainer reported it on an LG Smart TV

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title. Title of the page the host serves: `MindField` | Live web page |
| Context | Maintainer's earlier note: added the line `mindfieldonline.com -- Online survey panel (seen on LG Smart TV)` | [commit f3f9cbb](https://github.com/slyfox1186/pihole-regex/commit/f3f9cbb) |

Status: The note repeats the maintainer's earlier report. The query log since 2026-11-12 has no lookups.

### `nevoai-iothub-54-prod.azure-devices.net`

Microsoft Azure IoT Hub instance named 'nevoai' - Customer unverified (old note: LG Smart TV)

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Azure certificate. TLS certificate subject: `Microsoft Corporation` | TLS certificate |

Status: Purpose unverified. Azure IoT Hub names do not show the customer.

## RegEx allowlist: `regex-whitelist.sql` (83 entries)

### `(\.|^)1drv\.ms$`

1drv.ms and its subdomains

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `1drv.ms` | NOERROR | no | 0 |

</details>

Status: Purpose unverified. No fetched source names 1drv.ms; the old note said OneDrive short links.

### `^(account|accts|catalog|entitlement|eulatracking|lightswitch|priceengine)-public-service-prod[0-9]*\.(ak|ol)\.epicgames\.com$`

Epic Games hosts *-public-service-prod.ak/ol.epicgames.com for account, accts, catalog, entitlement, eulatracking, lightswitch and priceengine

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `eulatracking-public-service-prod06.ol.epicgames.com` | Pi-hole query log |

Note: Open-ended (prod[0-9]*).

### `(\.|^)messenger\.com$`

messenger.com and its subdomains - Pi-hole users list Messenger hosts for Facebook Messenger

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum Facebook and Messenger section: "## Facebook, Facebook Messenger" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `messenger.com` | NOERROR | no | 0 |

</details>

### `^(accounts|download|entitlement-public-service-prod\.ak|fg-matchmaking-public-service-live-c\.ol|graphql|launcher-public-service-prod06\.ol)\.epicgames\.com$`

Epic Games hosts accounts, download, entitlement-public-service-prod.ak, fg-matchmaking, graphql and launcher

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists graphql.epicgames.com: "graphql.epicgames.com" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (6)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `accounts.epicgames.com` | NOERROR | no | 0 |
| `download.epicgames.com` | NOERROR | no | 0 |
| `entitlement-public-service-prod.ak.epicgames.com` | NOERROR | no | 0 |
| `fg-matchmaking-public-service-live-c.ol.epicgames.com` | NOERROR | no | 0 |
| `graphql.epicgames.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `launcher-public-service-prod06.ol.epicgames.com` | NOERROR | no | 1 |

</details>

### `^ads-[a-z0-9-]+\.aylanetworks\.com$`

Ayla Networks smart-home IoT cloud - ads-* device hosts - Caught by the ad regex

| Shows | Evidence | Source |
| --- | --- | --- |
| Who runs it | Ayla describes its business: "Simplifying Smart Home IoT \| Ayla Networks" | [www.aylanetworks.com](https://www.aylanetworks.com/) |
| Observed | Seen on the maintainer's network: `ads-field.aylanetworks.com` | Pi-hole query log |

Note: The 652f298 audit traced these hosts to Shark, Fujitsu FGLair and Bradford White appliances.

### `^(affiliate|app|id|id-cdn)\.twitch\.tv$`

Twitch hosts affiliate, app, id and id-cdn.twitch.tv

<details>
<summary>Hosts this rule covers, checked one by one (4)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `affiliate.twitch.tv` | NOERROR | no | 0 |
| `app.twitch.tv` | NOERROR | no | 0 |
| `id-cdn.twitch.tv` | NOERROR | no | 0 |
| `id.twitch.tv` | NOERROR | no | 0 |

</details>

### `^(aic|eic|kic|ruc)\.service\.lgtvcommon\.com$|^(aic|eic|kic)\.cdpsvc\.lgtvcommon\.com$`

LG TV hosts aic/eic/kic/ruc.service and aic/eic/kic.cdpsvc.lgtvcommon.com - HaGeZi #309: aic hosts carry channel guide data

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | HaGeZi #309: guide data breaks without these: "aic.cdpsvc.lgtvcommon.com - _Prevents Internet Channel guide data from downloading_" | [hagezi/dns-blocklists #309](https://github.com/hagezi/dns-blocklists/issues/309) |
| If blocked | HaGeZi #309: OTA guide data: "aic.service.lgtvcommon.com - _Prevents local OTA Channel guide data from downloading_" | [hagezi/dns-blocklists #309](https://github.com/hagezi/dns-blocklists/issues/309) |
| Observed | Seen on the maintainer's network: `eic.service.lgtvcommon.com` | Pi-hole query log |
| What it does | HaGeZi accepted region variants of LG service hosts: "I presume any `*.service.lgtvcommon.com` domains are required for the same function, just different regions." | [hagezi/dns-blocklists #1807](https://github.com/hagezi/dns-blocklists/issues/1807) |

<details>
<summary>Hosts this rule covers, checked one by one (7)</summary>

- aic.cdpsvc.lgtvcommon.com: DNS NOERROR; named in https://github.com/hagezi/dns-blocklists/issues/309, https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
- aic.service.lgtvcommon.com: DNS NOERROR; named in https://github.com/hagezi/dns-blocklists/issues/309; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
- eic.cdpsvc.lgtvcommon.com: DNS NOERROR; named in https://github.com/hagezi/dns-blocklists/issues/309; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
- eic.service.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 1 lookups on the maintainer's network; would be blocked by this repo's deny regex
- kic.cdpsvc.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
- kic.service.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
- ruc.service.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex

</details>

### `^((www|drivers|download|account|community)\.)?amd\.com$`

AMD - amd.com and its www, drivers, download, account and community hosts

<details>
<summary>Hosts this rule covers, checked one by one (6)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `account.amd.com` | NOERROR | no | 0 |
| `amd.com` | NOERROR | no | 0 |
| `community.amd.com` | NOERROR | no | 0 |
| `download.amd.com` | NOERROR | no | 0 |
| `drivers.amd.com` | NOERROR | no | 0 |
| `www.amd.com` | NOERROR | no | 0 |

</details>

### `^(api\.flightproxy|authsvc|chatsvcagg|config|go\.trouter|presence)\.teams\.microsoft\.com$`

Microsoft Teams hosts (*.teams.microsoft.com, required by Microsoft 365): flightproxy, authsvc, chatsvcagg, config, trouter, presence

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Microsoft lists Teams' config host: "TLSv1.2/HTTPS/HTTP config.teams.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions) |
| Context | Microsoft 365 required *.teams.microsoft.com: "*.lync.com, *.teams.cloud.microsoft, *.teams.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) |

<details>
<summary>Hosts this rule covers, checked one by one (6)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `api.flightproxy.teams.microsoft.com` | NOERROR | no | 0 |
| `authsvc.teams.microsoft.com` | NOERROR | no | 0 |
| `chatsvcagg.teams.microsoft.com` | NOERROR | no | 0 |
| `go.trouter.teams.microsoft.com` | NOERROR | no | 0 |
| `presence.teams.microsoft.com` | NOERROR | no | 0 |

- config.teams.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions; 0 lookups on the maintainer's network

</details>

### `^(appleid|apps|audiocontentdownload|bpapi|business|captive|certs|configuration|crl|cssubmissions|deviceenrollment|diagassets|fba|gc|gdmf|gg|gs|gsa|gsp1|humb|identity|idmsa|ig|iprofiles|itunes|mdmenrollment|mesu|oscdn|osrecovery|ppq|radarsubmissions|school|serverstatus|skl|suconfig|sw(cdn|dist|download|scan)|sylvan|tbsc|valid|www|axm-app|deviceservices-external|gnf-mdn|gnf-mr|lcdn-(locator|registration)|sq-device|time(-ios|-macos)?|xp)\.apple\.com$`

Apple - 54 apple.com hosts, most in Apple's network requirements (software updates, captive portal check, time, enrollment)

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Apple: software update catalogs: "mesu.apple.com 443, 80 TCP iOS, iPadOS, tvOS, watchOS, macOS, and visionOS Hosts software update catalogs" | [support.apple.com](https://support.apple.com/en-us/101555) |
| What it does | Apple: captive portal check: "captive.apple.com 443, 80 TCP iOS, iPadOS, tvOS, macOS, and visionOS Internet connectivity validation for networks that use captive portals" | [support.apple.com](https://support.apple.com/en-us/101555) |
| What it does | Apple: time servers: "time.apple.com 123 UDP iOS, iPadOS, tvOS, macOS, and visionOS Used by devices to set their date and time" | [support.apple.com](https://support.apple.com/en-us/101555) |

<details>
<summary>Hosts this rule covers, checked one by one (54)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `apps.apple.com` | NOERROR | no | 0 |
| `audiocontentdownload.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `axm-app.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `bpapi.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `business.apple.com` | NOERROR | no | 0 |
| `certs.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `configuration.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 28 |
| `cssubmissions.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `diagassets.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `fba.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `gc.apple.com` | NOERROR | no | 0 |
| `gnf-mdn.apple.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `gnf-mr.apple.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `gsa.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 10 |
| `gsp1.apple.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 1 |
| `idmsa.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `lcdn-locator.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 4 |
| `radarsubmissions.apple.com` | NOERROR | no | 0 |
| `school.apple.com` | NOERROR | no | 0 |
| `serverstatus.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `sq-device.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `suconfig.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `sylvan.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `time-macos.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `valid.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 2 |

- appleid.apple.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- captive.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 2 lookups on the maintainer's network
- crl.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- deviceenrollment.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- deviceservices-external.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- gdmf.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 48 lookups on the maintainer's network
- gg.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- gs.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- humb.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 2 lookups on the maintainer's network
- identity.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- ig.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- iprofiles.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- itunes.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 2 lookups on the maintainer's network
- lcdn-registration.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- mdmenrollment.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- mesu.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 28 lookups on the maintainer's network
- oscdn.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- osrecovery.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- ppq.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- skl.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- swcdn.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- swdist.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- swdownload.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- swscan.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- tbsc.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- time-ios.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- time.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 11 lookups on the maintainer's network
- www.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- xp.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 40 lookups on the maintainer's network

</details>

Note: gc, apps, business, radarsubmissions and school are not in Apple's network page; each host's sources are listed per branch.

### `(\.|^)apple-(cloudkit|livephotoskit)\.com$`

Apple CloudKit and Live Photos kit domains (apple-cloudkit.com, apple-livephotoskit.com)

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Apple lists api.apple-cloudkit.com: "api.apple-cloudkit.com 443 TCP macOS App notarization" | [support.apple.com](https://support.apple.com/en-us/101555) |

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `apple-cloudkit.com` | NOERROR | no | 0 |
| `apple-livephotoskit.com` | NOERROR | no | 0 |

</details>

### `^apps\.bdimg\.(com|jomodns\.com)$`

apps.bdimg.com and apps.bdimg.jomodns.com

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `apps.bdimg.com` | NOERROR | no | 0 |
| `apps.bdimg.jomodns.com` | NOERROR | no | 0 |

</details>

Status: Purpose unverified. No fetched source; the old note said Baidu static file CDN.

### `^(apresolve|dealer|embed|global-dealer-ssl|login5|market|mobile-ap|open|play|spclient\.wg)\.spotify\.com$`

Spotify hosts apresolve, dealer, embed, global-dealer-ssl, login5, market, mobile-ap, open, play and spclient.wg.spotify.com

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists spclient.wg.spotify.com and apresolve under Spotify: the page lists `spclient.wg.spotify.com` under the heading "Spotify" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Observed | Seen on the maintainer's network: `dealer.spotify.com` | Pi-hole query log |

<details>
<summary>Hosts this rule covers, checked one by one (10)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `dealer.spotify.com` | NOERROR | no | 12 |
| `embed.spotify.com` | NOERROR | no | 0 |
| `global-dealer-ssl.spotify.com` | NOERROR | no | 0 |
| `login5.spotify.com` | NOERROR | no | 0 |
| `market.spotify.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `mobile-ap.spotify.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `open.spotify.com` | NOERROR | no | 6 |
| `play.spotify.com` | NOERROR | no | 0 |

- apresolve.spotify.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt, https://discourse.pi-hole.net/raw/212; 8 lookups on the maintainer's network
- spclient.wg.spotify.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt, https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

</details>

### `^(cert\.mgt|device\.auth|eds|help\.ui|licensing|notify|title\.(auth|mgt)|www|xflight|xkms|xsts\.auth)\.xboxlive\.com$`

Twelve xboxlive.com hosts - The Pi-hole forum lists them as required for full Xbox Live functionality

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole's Xbox Live list: the page lists `xsts.auth.xboxlive.com` under the heading "Full Functionality" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| What it does | Confirmed by Microsoft as required, per the forum: "which were also confirmed by Microsoft as being required by Xbox Live for full functionality" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (12)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `www.xboxlive.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |

- cert.mgt.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- device.auth.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- eds.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- help.ui.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- licensing.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- notify.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- title.auth.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- title.mgt.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- xflight.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- xkms.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- xsts.auth.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

</details>

### `^(audio4-fa|daily-mix|dailymix-images|download|encore|i|lineup-images|newjams-images|t|upgrade)\.scdn\.co$`

Spotify scdn.co hosts (audio4-fa, daily-mix, dailymix-images, download, encore, i, lineup-images, newjams-images, t, upgrade)

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `i.scdn.co` | Pi-hole query log |

<details>
<summary>Hosts this rule covers, checked one by one (10)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `audio4-fa.scdn.co` | NOERROR | no | 0 |
| `daily-mix.scdn.co` | NOERROR | no | 0 |
| `dailymix-images.scdn.co` | NOERROR | no | 0 |
| `download.scdn.co` | NOERROR | no | 0 |
| `encore.scdn.co` | NOERROR | no | 0 |
| `i.scdn.co` | NOERROR | no | 10 |
| `lineup-images.scdn.co` | NOERROR | no | 0 |
| `newjams-images.scdn.co` | NOERROR | no | 0 |
| `t.scdn.co` | NOERROR | no | 0 |
| `upgrade.scdn.co` | NOERROR | no | 0 |

</details>

### `^(aws|det-ta-g7g|todo-ta-g7g)\.amazon\.com$|^cognito-identity\.us-east-1\.amazonaws\.com$`

Amazon hosts aws, det-ta-g7g and todo-ta-g7g.amazon.com (anudeep lists the last two for Kindle) and cognito-identity (AWS authentication)

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep lists these under Amazon Kindle: the page lists `todo-ta-g7g.amazon.com` under the heading "Amazon Kindle" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |
| Observed | Seen on the maintainer's network: `todo-ta-g7g.amazon.com` | Pi-hole query log |
| What it does | AWS lists cognito-identity under authentication: "WorkSpaces Secure Browser authentication *.auth. { region} .amazoncognito.com cognito-identity." | [docs.aws.amazon.com](https://docs.aws.amazon.com/workspaces-web/latest/adminguide/allowed.html) |

<details>
<summary>Hosts this rule covers, checked one by one (4)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `aws.amazon.com` | NOERROR | no | 0 |
| `cognito-identity.us-east-1.amazonaws.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `det-ta-g7g.amazon.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |

- todo-ta-g7g.amazon.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt, https://perflyst.github.io/PiHoleBlocklist/AmazonFireTV.txt; 111 lookups on the maintainer's network

</details>

### `^(axm-adm-[a-z0-9-]+|enroll)\.apple\.com$`

Apple hosts axm-adm-*.apple.com and enroll.apple.com

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Apple's network page covers Apple Business device management: "Device management services to upload enrollment profiles" | [support.apple.com](https://support.apple.com/en-us/101555) |

Note: Open-ended (axm-adm-[a-z0-9-]+).

### `^(bam-sdk-configs|config-cd-dmgz)\.bamgrid\.com$`

bamgrid.com hosts bam-sdk-configs and config-cd-dmgz - Used on the maintainer's network

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `config-cd-dmgz.bamgrid.com` | Pi-hole query log |

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `bam-sdk-configs.bamgrid.com` | NOERROR | no | 1 |
| `config-cd-dmgz.bamgrid.com` | NOERROR | no | 14 |

</details>

Note: The old note said Disney+ app configuration; not documented here.

### `^(b-api|instagram\.c10r)\.facebook\.com$`

Facebook hosts b-api.facebook.com and instagram.c10r.facebook.com - Listed in community allowlists

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists b-api under Facebook: the page lists `b-api.facebook.com` under the heading "Facebook, Facebook Messenger" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `b-api.facebook.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `instagram.c10r.facebook.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |

</details>

### `^(benchmarks|commons|empoweringtrust|support\.benchmarks|www)\.ul\.com(\.cdn\.cloudflare\.net)?$`

Five ul.com hosts (benchmarks, support.benchmarks, www and two more) plus their Cloudflare CNAMEs

<details>
<summary>Hosts this rule covers, checked one by one (10)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `benchmarks.ul.com` | NOERROR | no | 0 |
| `benchmarks.ul.com.cdn.cloudflare.net` | NOERROR | no | 0 |
| `commons.ul.com` | NOERROR | no | 0 |
| `commons.ul.com.cdn.cloudflare.net` | NOERROR | no | 0 |
| `empoweringtrust.ul.com` | NOERROR | no | 0 |
| `empoweringtrust.ul.com.cdn.cloudflare.net` | NOERROR | no | 0 |
| `support.benchmarks.ul.com` | NOERROR | no | 0 |
| `support.benchmarks.ul.com.cdn.cloudflare.net` | NOERROR | no | 0 |
| `www.ul.com` | NOERROR | no | 0 |
| `www.ul.com.cdn.cloudflare.net` | NOERROR | no | 0 |

</details>

### `^(blog|business|careers|contests|dev|email|insights|meta|talent|www\.careers)\.stackoverflow\.com$`

Stack Overflow hosts blog, business, careers, contests, dev, email, insights, meta, talent and www.careers

<details>
<summary>Hosts this rule covers, checked one by one (10)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `blog.stackoverflow.com` | NOERROR | no | 0 |
| `business.stackoverflow.com` | NOERROR | no | 0 |
| `careers.stackoverflow.com` | NOERROR | no | 0 |
| `contests.stackoverflow.com` | NOERROR | no | 0 |
| `dev.stackoverflow.com` | NOERROR | no | 0 |
| `email.stackoverflow.com` | NOERROR | no | 0 |
| `insights.stackoverflow.com` | NOERROR | no | 0 |
| `meta.stackoverflow.com` | NOERROR | no | 0 |
| `talent.stackoverflow.com` | NOERROR | no | 0 |
| `www.careers.stackoverflow.com` | NOERROR | no | 0 |

</details>

### `^(blog|community(-cdn|-staging)?|d-cloudflare|docs|downloads(-staging)?|et|guide|help|learn|models(-r2)?)\.topazlabs\.com$`

Topaz Labs hosts (blog, community, docs, downloads, guide, help, learn, models and others)

<details>
<summary>Hosts this rule covers, checked one by one (14)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `blog.topazlabs.com` | NOERROR | no | 0 |
| `community-cdn.topazlabs.com` | NOERROR | no | 0 |
| `community-staging.topazlabs.com` | NOERROR | no | 0 |
| `community.topazlabs.com` | NOERROR | no | 0 |
| `d-cloudflare.topazlabs.com` | NOERROR | no | 0 |
| `docs.topazlabs.com` | NOERROR | no | 0 |
| `downloads-staging.topazlabs.com` | NOERROR | no | 0 |
| `downloads.topazlabs.com` | NOERROR | no | 0 |
| `et.topazlabs.com` | NOERROR | no | 0 |
| `guide.topazlabs.com` | NOERROR | no | 0 |
| `help.topazlabs.com` | NOERROR | no | 0 |
| `learn.topazlabs.com` | NOERROR | no | 0 |
| `models-r2.topazlabs.com` | NOERROR | no | 0 |
| `models.topazlabs.com` | NOERROR | no | 0 |

</details>

### `^(calendar|docs|home|inbox|clients[1-6]?|mail|meet|pay(|ments)|photos|sites|time|wallet|workspace|www)\.google\.com$`

Google hosts calendar, docs, home, inbox, clients, mail, meet, pay, photos, sites, time, wallet, workspace and www.google.com

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum: Google Maps and other Google services: the page lists `clients4.google.com` under the heading "Google Maps and other Google services" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Observed | Seen on the maintainer's network: `mail.google.com` | Pi-hole query log |

<details>
<summary>Hosts this rule covers, checked one by one (22)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `calendar.google.com` | NOERROR | no | 0 |
| `clients.google.com` | NOERROR | no | 0 |
| `clients1.google.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) | 1 |
| `clients5.google.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) | 0 |
| `clients6.google.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) | 60 |
| `dns.google.com` | NOERROR | no | 0 |
| `docs.google.com` | NOERROR | no | 2 |
| `home.google.com` | NOERROR | no | 0 |
| `inbox.google.com` | NOERROR | no | 65 |
| `mail.google.com` | NOERROR | no | 1245 |
| `meet.google.com` | NOERROR | no | 30 |
| `pay.google.com` | NOERROR | no | 0 |
| `payments.google.com` | NOERROR | no | 0 |
| `photos.google.com` | NOERROR | no | 0 |
| `sites.google.com` | NOERROR | no | 0 |
| `time.google.com` | NOERROR | no | 0 |
| `wallet.google.com` | NOERROR | no | 0 |
| `workspace.google.com` | NOERROR | no | 0 |
| `www.google.com` | NOERROR | no | 564 |

- clients2.google.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 12 lookups on the maintainer's network
- clients3.google.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 24 lookups on the maintainer's network
- clients4.google.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 14 lookups on the maintainer's network

</details>

### `^(alt[0-9]-)?mtalk\.google\.com$`

Google push notifications (mtalk.google.com and alt0-9-mtalk) - Pi-hole users list mtalk for Android app push

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum: push notifications: the page lists `mtalk.google.com` under the heading "Push Notification" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (11)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `alt0-mtalk.google.com` | NXDOMAIN | no | 0 |
| `alt1-mtalk.google.com` | NOERROR | no | 0 |
| `alt2-mtalk.google.com` | NOERROR | no | 0 |
| `alt3-mtalk.google.com` | NOERROR | no | 0 |
| `alt4-mtalk.google.com` | NOERROR | no | 0 |
| `alt5-mtalk.google.com` | NOERROR | no | 0 |
| `alt6-mtalk.google.com` | NOERROR | no | 0 |
| `alt7-mtalk.google.com` | NOERROR | no | 0 |
| `alt8-mtalk.google.com` | NOERROR | no | 0 |
| `alt9-mtalk.google.com` | NXDOMAIN | no | 0 |
| `mtalk.google.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 10 |

</details>

Note: alt0-mtalk and alt9-mtalk returned NXDOMAIN on 2026-11-13; allowing them is harmless.

### `^cdn\.(datatables\.net|discordapp\.com|embed\.ly|embedly\.com|materialdesignicons\.com|mathjax\.org|plyr\.io|signal\.org)$`

cdn. hosts of datatables.net, discordapp.com, embed.ly, embedly.com, materialdesignicons.com, mathjax.org, plyr.io and signal.org

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `cdn.discordapp.com` | Pi-hole query log |

<details>
<summary>Hosts this rule covers, checked one by one (8)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `cdn.datatables.net` | NOERROR | no | 0 |
| `cdn.discordapp.com` | NOERROR | no | 993 |
| `cdn.embed.ly` | NOERROR | no | 0 |
| `cdn.embedly.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) | 0 |
| `cdn.materialdesignicons.com` | NOERROR | no | 0 |
| `cdn.mathjax.org` | NOERROR | no | 0 |
| `cdn.plyr.io` | NOERROR | no | 0 |
| `cdn.signal.org` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |

</details>

### `^(cdn\.embed\.ly|cdn\.jsdelivr\.net|cdnjs\.loli\.net)\.cdn\.cloudflare\.net$`

Cloudflare CNAME names of cdn.embed.ly, cdn.jsdelivr.net and cdnjs.loli.net

<details>
<summary>Hosts this rule covers, checked one by one (3)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `cdn.embed.ly.cdn.cloudflare.net` | NOERROR | no | 0 |
| `cdn.jsdelivr.net.cdn.cloudflare.net` | NOERROR | no | 0 |
| `cdnjs.loli.net.cdn.cloudflare.net` | NOERROR | no | 0 |

</details>

### `^cdnjs\.(cloudflare\.com|loli\.net)$`

cdnjs.cloudflare.com and its China mirror cdnjs.loli.net - A tested jQuery file from the mirror matched the official copy

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `cdnjs.cloudflare.com` | Pi-hole query log |
| What it does | Integrity check of the loli.net mirror. Library integrity check (full record): 2026-11-13: https://cdnjs.loli.net/ajax/libs/jquery/3.6.0/jquery.min.js compared byte-for-byte with https://code.jquery.com/jquery-3.6.0.min.js: identical (SHA-256 tested ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e, reference ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e) | File comparison |

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `cdnjs.loli.net` | NOERROR | no | 0 |

- cdnjs.cloudflare.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://learn.microsoft.com/en-us/microsoft-365/enterprise/network-requests-in-office-2016-for-mac; 8 lookups on the maintainer's network

</details>

### `^(cdn-mobile\.api|images|players|silo|siloh|stitcher)\.pluto\.tv$`

Pluto TV hosts cdn-mobile.api, images, players, silo, siloh and stitcher.pluto.tv

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `players.pluto.tv` | Pi-hole query log |

<details>
<summary>Hosts this rule covers, checked one by one (6)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `cdn-mobile.api.pluto.tv` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `images.pluto.tv` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `players.pluto.tv` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 1 |
| `silo.pluto.tv` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `siloh.pluto.tv` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `stitcher.pluto.tv` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |

</details>

### `^(winatp-gw-neu|windows)\.microsoft\.com$`

Microsoft hosts winatp-gw-neu and windows.microsoft.com

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `winatp-gw-neu.microsoft.com` | NOERROR | no | 0 |
| `windows.microsoft.com` | NOERROR | no | 0 |

</details>

Status: Purpose unverified. Neither is in the cached Microsoft pages; the old note said Defender for Endpoint (Europe).

### `^(client\.wns|edge\.activity)\.windows\.com$`

Windows hosts client.wns and edge.activity.windows.com (Microsoft lists edge.activity)

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Microsoft lists edge.activity.windows.com: "edge.activity.windows.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions) |

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `client.wns.windows.com` | NOERROR | no | 0 |
| `edge.activity.windows.com` | NOERROR | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions) | 0 |

</details>

### `^(cloudsync-prod|reddit-uploaded-media|seedbox-react-infra|ubisoft-uplay-savegames|whispersystems-textsecure-attachments)\.s3(-accelerate)?\.amazonaws\.com$`

Five Amazon S3 buckets incl. cloudsync-prod (Origin save sync) and whispersystems-textsecure-attachments (listed under Signal)

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum: Signal attachments bucket: the page lists `whispersystems-textsecure-attachments.s3-accelerate.amazonaws.com` under the heading "Signal" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Context | Pi-hole forum: Origin save sync: the page lists `cloudsync-prod.s3.amazonaws.com` under the heading "Origin (Savegame-Sync)" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (10)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `cloudsync-prod.s3-accelerate.amazonaws.com` | NOERROR | no | 0 |
| `cloudsync-prod.s3.amazonaws.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `reddit-uploaded-media.s3-accelerate.amazonaws.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `reddit-uploaded-media.s3.amazonaws.com` | NOERROR | no | 0 |
| `seedbox-react-infra.s3-accelerate.amazonaws.com` | NOERROR | no | 0 |
| `seedbox-react-infra.s3.amazonaws.com` | NOERROR | no | 0 |
| `ubisoft-uplay-savegames.s3-accelerate.amazonaws.com` | NOERROR | no | 0 |
| `ubisoft-uplay-savegames.s3.amazonaws.com` | NOERROR | no | 0 |
| `whispersystems-textsecure-attachments.s3-accelerate.amazonaws.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `whispersystems-textsecure-attachments.s3.amazonaws.com` | NOERROR | no | 0 |

</details>

### `^code\.(bildstatic\.de|createjs\.com|jquery\.com)$`

code.bildstatic.de, code.createjs.com and code.jquery.com

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `code.jquery.com` | Pi-hole query log |

<details>
<summary>Hosts this rule covers, checked one by one (3)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `code.bildstatic.de` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `code.createjs.com` | NOERROR | no | 0 |
| `code.jquery.com` | NOERROR | no | 5 |

</details>

### `^((www|m|web|static|graph|b-graph|mqtt-mini|edge-mqtt|upload|connect)\.)?facebook\.com$|^connect\.facebook\.net$`

Facebook - facebook.com, its www, m, web, static, graph, b-graph, mqtt, upload and connect hosts, and connect.facebook.net

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum: Facebook and Messenger: the page lists `www.facebook.com` under the heading "Facebook, Facebook Messenger" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Observed | Seen on the maintainer's network: `www.facebook.com` | Pi-hole query log |

<details>
<summary>Hosts this rule covers, checked one by one (12)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `b-graph.facebook.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `connect.facebook.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `connect.facebook.net` | NOERROR | no | 6 |
| `facebook.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `m.facebook.com` | NOERROR | no | 0 |
| `mqtt-mini.facebook.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `static.facebook.com` | NOERROR | no | 0 |
| `upload.facebook.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `web.facebook.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 16 |
| `www.facebook.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 22 |

- edge-mqtt.facebook.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt, https://discourse.pi-hole.net/raw/212; 9 lookups on the maintainer's network
- graph.facebook.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt, https://discourse.pi-hole.net/raw/212; 24 lookups on the maintainer's network

</details>

Note: Decision 2026-11-14: kept. Facebook Login on other sites loads from connect.facebook.net; the old note says the Facebook Pixel tracker also loads from it.

### `^connectivitycheck\.(android|gstatic)\.com$`

Android internet connectivity check

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum: Android/Chrome: the page lists `connectivitycheck.gstatic.com` under the heading "Android/Chrome" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

- connectivitycheck.android.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- connectivitycheck.gstatic.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 2 lookups on the maintainer's network

</details>

### `^crl[3-4]\.digicert\.com$`

DigiCert certificate revocation lists (CRL) - Apple lists them for certificate validation

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Apple: certificate validation: "crl3.digicert.com 80 TCP iOS, iPadOS, tvOS, macOS, and visionOS Certificate validation" | [support.apple.com](https://support.apple.com/en-us/101555) |

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

- crl3.digicert.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- crl4.digicert.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

</details>

### `^(csp|devicelistenerprod)\.microsoft\.com$`

Microsoft hosts csp and devicelistenerprod.microsoft.com - Purpose unverified

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `csp.microsoft.com` | NOERROR | no | 0 |
| `devicelistenerprod.microsoft.com` | NOERROR | no | 0 |

</details>

Status: Purpose unverified. Neither host is in the cached Microsoft endpoint pages.

### `^d(27xxe7juh1us6|2gatte9o95jao|3a3ewgd1iewwz|3ag4hukkh62yn|83eunklitikj)\.cloudfront\.net$`

Five CloudFront hosts - The Pi-hole forum lists one for Signal; the rest are unverified

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum lists d83eunklitikj under Signal: the page lists `d83eunklitikj.cloudfront.net` under the heading "Signal" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (5)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `d27xxe7juh1us6.cloudfront.net` | NOERROR | no | 0 |
| `d2gatte9o95jao.cloudfront.net` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) | 0 |
| `d3a3ewgd1iewwz.cloudfront.net` | NOERROR | no | 0 |
| `d3ag4hukkh62yn.cloudfront.net` | NOERROR | no | 0 |
| `d83eunklitikj.cloudfront.net` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |

</details>

Status: Purpose unverified. CloudFront certificates do not show customers; only d83eunklitikj (Signal) and d2gatte9o95jao (anudeep whitelist) are sourced.

### `^(app|meta|pubsub|status|tvdb2|www)\.plex\.tv$|^pubsub\.plex\.bz$`

Plex hosts app, meta, pubsub, status, tvdb2 and www.plex.tv, and pubsub.plex.bz

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum: Plex domains: the page lists `pubsub.plex.tv` under the heading "Plex Domains" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (7)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `app.plex.tv` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `www.plex.tv` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |

- meta.plex.tv: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- pubsub.plex.bz: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- pubsub.plex.tv: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- status.plex.tv: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- tvdb2.plex.tv: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

</details>

### `(\.|^)dataplicity\.com$`

Dataplicity - Remote access to Raspberry Pi and other devices (dataplicity.com and subdomains)

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Dataplicity's site: "Diagnose and resolve field-device problems remotely." | [www.dataplicity.com](https://www.dataplicity.com/) |

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `dataplicity.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) | 0 |

</details>

### `^(devimages|xp|playgrounds?(-assets)?)-cdn\.apple\.com$`

Apple hosts devimages-cdn (Xcode components), xp-cdn (content caching reporting) and Swift Playground hosts (playground- and playgrounds- spellings)

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Apple: Xcode downloadable components: "devimages-cdn.apple.com 80, 443 TCP macOS Xcode downloadable components" | [support.apple.com](https://support.apple.com/en-us/101555) |
| What it does | Apple: xp-cdn is content caching reporting: "xp-cdn.apple.com 443 TCP macOS Reporting" | [support.apple.com](https://support.apple.com/en-us/101555) |
| What it does | Apple's documented Swift Playground hosts are singular: "playground-assets-cdn.apple.com 443 TCP iPadOS and macOS Swift Playground" | [support.apple.com](https://support.apple.com/en-us/101555) |

<details>
<summary>Hosts this rule covers, checked one by one (6)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `devimages-cdn.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `playground-assets-cdn.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `playground-cdn.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `playgrounds-assets-cdn.apple.com` | NOERROR | no | 0 |
| `playgrounds-cdn.apple.com` | NOERROR | no | 0 |
| `xp-cdn.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |

</details>

Note: Decision 2026-11-14: rule corrected to allow Apple's documented playground-cdn and playground-assets-cdn.

### `^(oops|www)\.redditmedia\.com$|^www\.redditstatic\.com$|^reddit\.map\.fastly\.net$`

Reddit hosts oops and www.redditmedia.com, www.redditstatic.com and reddit.map.fastly.net

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum: Reddit: the page lists `www.redditstatic.com` under the heading "Reddit" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (4)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `oops.redditmedia.com` | NOERROR | no | 0 |
| `reddit.map.fastly.net` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `www.redditmedia.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `www.redditstatic.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 9 |

</details>

### `^(disney\.(api|connections|content|images|playback)\.edge|playback-certs)\.bamgrid\.com$`

bamgrid.com hosts disney.api, connections, content, images and playback edge, and playback-certs - Used heavily on the maintainer's network

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `disney.api.edge.bamgrid.com` | Pi-hole query log |

<details>
<summary>Hosts this rule covers, checked one by one (6)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `disney.api.edge.bamgrid.com` | NOERROR | no | 273 |
| `disney.connections.edge.bamgrid.com` | NOERROR | no | 37 |
| `disney.content.edge.bamgrid.com` | NOERROR | no | 0 |
| `disney.images.edge.bamgrid.com` | NOERROR | no | 31 |
| `disney.playback.edge.bamgrid.com` | NOERROR | no | 34 |
| `playback-certs.bamgrid.com` | NOERROR | no | 20 |

</details>

### `^[a-z0-9]{10}(-dsn)?\.algolia\.net$|^[a-z0-9]{10}-[1-3]\.algolianet\.com$`

Algolia hostnames: 10 alphanumeric characters with .algolia.net or -dsn.algolia.net, or -1 to -3.algolianet.com

| Shows | Evidence | Source |
| --- | --- | --- |
| Scope | Example app host resolves and matches (pihole-FTL). Example hosts tested with DNS and pihole-FTL (full record): {"latency-dsn.algolia.net": {"dns": "NOERROR", "cname": ["dsn.latency.api.algolia.net.", "s10-use-1.algolia.net."], "ftl_match": false}, "bh4d9od16a-dsn.algolia.net": {"dns": "NOERROR", "cname": ["dsn.bh4d9od16a.api.algolia.net.", "s8-usc-1.algolia.net."], "ftl_match": true}, "bh4d9od16a-1.algolianet.com": {"dns": "NOERROR", "cname": ["c6-eu-1.algolianet.com."], "ftl_match": true}} | pihole-FTL test |

Note: Open-ended. The maintainer's earlier note tied it to AdultTime search.

### `^(download\.developer|ns\.itunes|static\.ips|vpp\.itunes)\.apple\.com$`

Apple hosts download.developer (Xcode components), ns.itunes, static.ips and vpp.itunes.apple.com

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Apple: Xcode components: "download.developer.apple.com 80, 443 TCP macOS Xcode downloadable components" | [support.apple.com](https://support.apple.com/en-us/101555) |

<details>
<summary>Hosts this rule covers, checked one by one (4)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `download.developer.apple.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |

- ns.itunes.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- static.ips.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- vpp.itunes.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

</details>

### `^[0-6]-edge-chat\.facebook\.com$`

Facebook hosts 0- to 6-edge-chat.facebook.com - Listed in anudeep's optional allowlist

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep lists them under Facebook: the page lists `0-edge-chat.facebook.com` under the heading "Facebook" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) |

<details>
<summary>Hosts this rule covers, checked one by one (7)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `0-edge-chat.facebook.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `1-edge-chat.facebook.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `2-edge-chat.facebook.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `3-edge-chat.facebook.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `4-edge-chat.facebook.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `5-edge-chat.facebook.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |
| `6-edge-chat.facebook.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) | 0 |

</details>

### `^(edge|fs|msedge\.api\.cdp|officecdnmac|officeclient|support|teams|vlscppe|whiteboard|www)\.microsoft\.com$`

Microsoft hosts edge, fs, msedge.api.cdp, officecdnmac, officeclient, support, teams, vlscppe, whiteboard and www.microsoft.com

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Microsoft Edge endpoint: "TLSv1.2/HTTP edge.microsoft.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints) |

<details>
<summary>Hosts this rule covers, checked one by one (10)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `officecdnmac.microsoft.com` | NOERROR | no | 0 |
| `vlscppe.microsoft.com` | NOERROR | no | 0 |
| `whiteboard.microsoft.com` | NOERROR | no | 0 |

- edge.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints, https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions; 0 lookups on the maintainer's network
- fs.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions; 0 lookups on the maintainer's network
- msedge.api.cdp.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- officeclient.microsoft.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, https://learn.microsoft.com/en-us/microsoft-365/enterprise/network-requests-in-office-2016-for-mac, https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- support.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/archive/blogs/clientsecurity/microsoft-spynet, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7; 0 lookups on the maintainer's network
- teams.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges; 0 lookups on the maintainer's network
- www.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services, https://learn.microsoft.com/en-us/defender-endpoint/configure-network-connections-microsoft-defender-antivirus, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions; 1 lookups on the maintainer's network

</details>

### `^europe\.(cp\.wd|smartscreen(-prod|))\.microsoft\.com$`

Microsoft hosts europe.cp.wd, europe.smartscreen and europe.smartscreen-prod.microsoft.com

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Microsoft documents SmartScreen hosts: "If you turn off traffic for these endpoints, SmartScreen notifications won't appear." | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints) |

<details>
<summary>Hosts this rule covers, checked one by one (3)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `europe.cp.wd.microsoft.com` | NOERROR | no | 0 |
| `europe.smartscreen-prod.microsoft.com` | NOERROR | no | 0 |
| `europe.smartscreen.microsoft.com` | NOERROR | no | 0 |

</details>

Status: Purpose unverified. Microsoft documents SmartScreen hosts, but these Europe names are not in the cached pages.

### `(\.|^)gammacdn\.com$`

gammacdn.com and its subdomains - Maintainer labeled it Gamma Entertainment (AdultTime) media

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Maintainer's earlier note: added the line `(\.\|^)gammacdn\.com$ -- Gamma Entertainment (AdultTime) media CDN` | [commit 0a7a3ac](https://github.com/slyfox1186/pihole-regex/commit/0a7a3ac) |

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `gammacdn.com` | NOERROR | no | 0 |

</details>

Status: The note repeats the maintainer's earlier report.

### `^(github\.com|github\.io|github\.githubassets\.com)$`

GitHub - github.com, github.io and github.githubassets.com

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `github.com` | Pi-hole query log |

<details>
<summary>Hosts this rule covers, checked one by one (3)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `github.githubassets.com` | NOERROR | no | 60 |
| `github.io` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) | 0 |

- github.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt, https://raw.githubusercontent.com/anudeepND/whitelist/master/README.md, https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://github.com/hagezi/dns-blocklists/issues/1216, https://github.com/hagezi/dns-blocklists/issues/995, https://github.com/hagezi/dns-blocklists/issues/309, https://github.com/hagezi/dns-blocklists/issues/309, https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt, https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV-AGH.txt, https://discourse.pi-hole.net/raw/212; 1506 lookups on the maintainer's network

</details>

### `^gsp-ssl\.ls\.apple\.com$|^gsp-ssl\.ls-apple\.com\.akadns\.net$`

Apple gsp-ssl.ls.apple.com and its Akamai name - Pi-hole users list it for the iOS Weather app

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum: iOS Weather app: the page lists `gsp-ssl.ls.apple.com` under the heading "iOS Weather app" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `gsp-ssl.ls-apple.com.akadns.net` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `gsp-ssl.ls.apple.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 50 |

</details>

### `^hbbtv\.(prosieben|redbutton|zdf|ard)\.de$`

HbbTV hosts of ProSieben, redbutton.de, ZDF and ARD (Perflyst lists three of them)

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Perflyst lists them: the page lists `hbbtv.zdf.de` under the heading "HBBTV" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

<details>
<summary>Hosts this rule covers, checked one by one (4)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `hbbtv.ard.de` | NOERROR | no | 0 |

- hbbtv.prosieben.de: DNS NOERROR; named in https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt, https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV-AGH.txt; 0 lookups on the maintainer's network
- hbbtv.redbutton.de: DNS NOERROR; named in https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt, https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV-AGH.txt; 0 lookups on the maintainer's network
- hbbtv.zdf.de: DNS NOERROR; named in https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt, https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV-AGH.txt; 0 lookups on the maintainer's network

</details>

Note: hbbtv.ard.de is not in Perflyst's list.

### `(^|\.)itunes(-apple)?\.com(\.akadns\.net)?$`

itunes.com, itunes-apple.com and their Akamai names (Apple)

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `bag-cdn.itunes-apple.com.akadns.net` | Pi-hole query log |

<details>
<summary>Hosts this rule covers, checked one by one (4)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `itunes-apple.com` | NXDOMAIN | no | 0 |
| `itunes-apple.com.akadns.net` | NOERROR | no | 0 |
| `itunes.com` | NOERROR | [support.apple.com](https://support.apple.com/en-us/101555) | 0 |
| `itunes.com.akadns.net` | NXDOMAIN | no | 0 |

</details>

### `(\.|^)lencr\.org$`

Let's Encrypt (lencr.org) - Data referenced inside its certificates

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Let's Encrypt docs: "We use it to host data that is referenced inside the certificates we issue." | [letsencrypt.org](https://letsencrypt.org/docs/lencr.org/) |

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `lencr.org` | NOERROR | no | 0 |

</details>

### `(\.|^)linuxtracker\.org$`

Linux Tracker - Torrent site for Linux distributions

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site text: "LINUX DISTRIBUTIONS. TOGETHER." | [linuxtracker.org](https://linuxtracker.org/) |

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `linuxtracker.org` | NOERROR | no | 0 |

</details>

### `(\.|^)mee6\.xyz$`

MEE6 Discord bot site (mee6.xyz)

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title: "Discord Bot \| MEE6" | [mee6.xyz](https://mee6.xyz/) |

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `mee6.xyz` | NOERROR | no | 0 |

</details>

### `^m\.(hotmail\.com|reddit\.com|reuters\.com|twitch\.tv|youtube\.com)$`

Mobile sites m.hotmail.com, m.reddit.com, m.reuters.com, m.twitch.tv and m.youtube.com

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `m.youtube.com` | Pi-hole query log |

<details>
<summary>Hosts this rule covers, checked one by one (5)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `m.hotmail.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `m.reddit.com` | NOERROR | no | 0 |
| `m.reuters.com` | NOERROR | no | 0 |
| `m.twitch.tv` | NOERROR | no | 0 |
| `m.youtube.com` | NOERROR | no | 5 |

</details>

### `^(www\.)?minecraft\.net$`

Minecraft website

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `minecraft.net` | NOERROR | no | 0 |
| `www.minecraft.net` | NOERROR | no | 0 |

</details>

### `^((mobile|www|upload)\.)?twitter\.com$`

twitter.com and its mobile, www and upload hosts - Pi-hole users list them for Twitter

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum: Twitter: the page lists `upload.twitter.com` under the heading "Twitter" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (4)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `mobile.twitter.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `upload.twitter.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |
| `www.twitter.com` | NOERROR | no | 0 |

- twitter.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/README.md, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

</details>

### `^(www\.)?(myqnapcloud|qnap)\.com$`

qnap.com and myqnapcloud.com with their www hosts

<details>
<summary>Hosts this rule covers, checked one by one (4)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `myqnapcloud.com` | NOERROR | no | 0 |
| `qnap.com` | NOERROR | no | 0 |
| `www.myqnapcloud.com` | NOERROR | no | 0 |
| `www.qnap.com` | NOERROR | no | 0 |

</details>

### `^(www\.)?no-ip\.com$`

No-IP website (no-ip.com and www)

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `no-ip.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) | 0 |
| `www.no-ip.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) | 0 |

</details>

### `^ns[12]\.dropbox\.com$`

Dropbox hosts ns1.dropbox.com and ns2.dropbox.com - Listed in community allowlists

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum: Dropbox: the page lists `ns1.dropbox.com` under the heading "Dropbox" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

- ns1.dropbox.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- ns2.dropbox.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

</details>

### `^(oauthaccountmanager|www|youtubei)\.googleapis\.com$`

Google hosts www, youtubei and oauthaccountmanager.googleapis.com - Pi-hole users list them for YouTube on iOS

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum: YouTube app for iOS: the page lists `youtubei.googleapis.com` under the heading "YouTube App for iOS" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |
| Observed | Seen on the maintainer's network: `oauthaccountmanager.googleapis.com` | Pi-hole query log |

<details>
<summary>Hosts this rule covers, checked one by one (3)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `oauthaccountmanager.googleapis.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 177 |
| `youtubei.googleapis.com` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 71 |

- www.googleapis.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 33 lookups on the maintainer's network

</details>

### `^ocsp[0-9]*\.(apple|digicert|verisign)\.com$|^ocsp\.entrust\.net$`

Certificate status (OCSP) hosts of Apple, DigiCert, VeriSign and Entrust

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `ocsp2.apple.com` | Pi-hole query log |

Note: Open-ended (ocsp[0-9]*).

### `^orderprocessor.*\.ol\.epicgames\.com$`

Epic Games orderprocessor* hosts - Maintainer reported they are needed to buy games

| Shows | Evidence | Source |
| --- | --- | --- |
| Scope | Example host resolves and matches (pihole-FTL). Example hosts tested with DNS and pihole-FTL (full record): {"orderprocessor-public-service-ecomprod01.ol.epicgames.com": {"dns": "NOERROR", "cname": ["weighted-orderprocessor-public-service-prod.ol.epicgames.com.", "orderprocessor-public-service-prod.cdce.live.use1a.on.epicgames.com."], "ftl_match": true}, "orderprocessor-public-service-prod.ol.epicgames.com": {"dns": "NOERROR", "cname": ["weighted-orderprocessor-public-service-prod.ol.epicgames.com.", "orderprocessor-public-service-prod.cdce.live.use1a.on.epicgames.com."], "ftl_match": true}} | pihole-FTL test |
| Context | Maintainer's earlier note: added the line `^orderprocessor.*\.ol\.epicgames\.com$ -- Epic Games - Required to buy games on Windows` | [commit 0a7a3ac](https://github.com/slyfox1186/pihole-regex/commit/0a7a3ac) |

Status: The note repeats the maintainer's earlier report. Open-ended (orderprocessor.*).

### `^otnprd[0-9]+\.samsungcloudsolution\.net$`

Samsung TV otnprd* hosts - Perflyst: required for software update

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Perflyst: required for software update: "#otnprd10.samsungcloudsolution.net # required for software update" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

Note: Open-ended (otnprd[0-9]+).

### `^outlook\.(live|office(|365))\.com$`

Outlook web mail (outlook.live.com, outlook.office.com, outlook.office365.com)

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Microsoft 365 lists outlook.office365.com: "outlook.office365.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) |

<details>
<summary>Hosts this rule covers, checked one by one (3)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `outlook.live.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) | 0 |

- outlook.office.com: DNS NOERROR; named in https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges; 0 lookups on the maintainer's network
- outlook.office365.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, https://learn.microsoft.com/en-us/microsoft-365/enterprise/network-requests-in-office-2016-for-mac, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

</details>

### `^payment.*\.ol\.epicgames\.com$`

Epic Games payment* hosts - Maintainer reported they are needed for payments

| Shows | Evidence | Source |
| --- | --- | --- |
| Scope | Example host resolves and matches (pihole-FTL). Example hosts tested with DNS and pihole-FTL (full record): {"payment-website-pci.ol.epicgames.com": {"dns": "NOERROR", "cname": ["weighted-payment-website-pci.ol.epicgames.com.", "payment-website-fargate-1306000376.us-east-1.elb.amazonaws.com."], "ftl_match": true}, "payment-public-service-prod.ol.epicgames.com": {"dns": "NOERROR", "cname": ["payment-service-fargate-1560071709.us-east-1.elb.amazonaws.com."], "ftl_match": true}} | pihole-FTL test |
| Context | Maintainer's earlier note: added the line `^payment.*\.ol\.epicgames\.com$ -- Epic Games - Required for payments to process` | [commit f3f9cbb](https://github.com/slyfox1186/pihole-regex/commit/f3f9cbb) |

Status: The note repeats the maintainer's earlier report. Open-ended (payment.*).

### `(\.|^)redd\.it$`

redd.it and its subdomains

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `redd.it` | NOERROR | no | 0 |

</details>

Status: Purpose unverified. No fetched source; the old note said Reddit images, video and short links.

### `^((www|old|new|oauth|gql|gql-fed|gateway)\.)?reddit\.com$`

Reddit - reddit.com and its www, old, new, oauth, gql, gql-fed and gateway hosts

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `www.reddit.com` | Pi-hole query log |

<details>
<summary>Hosts this rule covers, checked one by one (8)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `gateway.reddit.com` | NOERROR | no | 0 |
| `gql-fed.reddit.com` | NOERROR | no | 0 |
| `gql.reddit.com` | NOERROR | no | 0 |
| `new.reddit.com` | NOERROR | no | 0 |
| `oauth.reddit.com` | NOERROR | no | 0 |
| `old.reddit.com` | NOERROR | no | 0 |
| `reddit.com` | NOERROR | no | 0 |

- www.reddit.com: DNS NOERROR; named in https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt, https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV-AGH.txt, https://discourse.pi-hole.net/raw/212; 7 lookups on the maintainer's network

</details>

### `(\.|^)robvanderwoude\.com$`

Rob van der Woude's website (robvanderwoude.com)

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `robvanderwoude.com` | NOERROR | no | 0 |

</details>

### `(\.|^)samsungcloudcdn\.com$`

samsungcloudcdn.com - Perflyst: blocking otn.samsungcloudcdn.com prevents Samsung TV updates

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | Perflyst: blocking otn.samsungcloudcdn.com prevents updates: "#otn.samsungcloudcdn.com # Prevents updates on UE49KS7000 and QE55Q9FNA" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `samsungcloudcdn.com` | NOERROR | no | 0 |

</details>

### `(\.|^)samsungotn\.net$`

Samsung TV - System update check (samsungotn.net)

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Perflyst: system update check: "#samsungotn.net # system update check on Samsung UE65RU7455" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

- samsungotn.net: DNS NOERROR; named in https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt, https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV-AGH.txt; 0 lookups on the maintainer's network

</details>

### `^scontent-(atl3|mia3)-1\.xx\.fbcdn\.net$`

Facebook hosts scontent-atl3-1 and scontent-mia3-1.xx.fbcdn.net - Pi-hole users list both for Facebook

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum: Facebook: the page lists `scontent-atl3-1.xx.fbcdn.net` under the heading "Facebook, Facebook Messenger" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (2)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `scontent-atl3-1.xx.fbcdn.net` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 12 |
| `scontent-mia3-1.xx.fbcdn.net` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 1 |

</details>

### `(\.|^)symcb\.com$`

symcb.com and its subdomains - Microsoft 365 lists *.symcb.com as a required endpoint

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Microsoft 365 required endpoints: "*.public-trust.com, *.symcb.com, *.symcd.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) |

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `symcb.com` | NOERROR | no | 0 |

</details>

### `^[a-z]\.thumbs\.redditmedia\.com$`

Reddit single-letter thumbs hosts (a-z.thumbs.redditmedia.com)

| Shows | Evidence | Source |
| --- | --- | --- |
| Scope | Example host resolves via Reddit's Fastly CDN and matches. Example hosts tested with DNS and pihole-FTL (full record): {"a.thumbs.redditmedia.com": {"dns": "NOERROR", "cname": ["dualstack.reddit.map.fastly.net."], "ftl_match": true}, "b.thumbs.redditmedia.com": {"dns": "NOERROR", "cname": ["dualstack.reddit.map.fastly.net."], "ftl_match": true}} | pihole-FTL test |

Note: Open-ended single-letter subdomain.

### `(\.|^)twimg\.com$`

twimg.com and its subdomains - Listed in anudeep's allowlist

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | anudeep's allowlist: "twimg.com" | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) |

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `twimg.com` | NOERROR | [anudeepND/whitelist (GitHub)](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt) | 0 |

</details>

### `(\.|^)unraid\.net$`

Unraid - unraid.net and its subdomains

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Site title: "The Homelab OS for Storage, Docker &amp; VMs" | [www.unraid.net](https://www.unraid.net/) |

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `unraid.net` | NOERROR | no | 0 |

</details>

Note: The old note said Unraid needs it to update; not verified.

### `(\.|^)wa\.me$`

wa.me and its subdomains - Pi-hole users list wa.me for WhatsApp

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Pi-hole forum: WhatsApp: the page lists `wa.me` under the heading "WhatsApp" | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) |

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `wa.me` | NOERROR | [discourse.pi-hole.net](https://discourse.pi-hole.net/raw/212) | 0 |

</details>

### `^whatsapp-cdn-shv-[0-9]{2}-[a-z]{3}[0-9]\.fbcdn\.net$`

fbcdn.net hosts named whatsapp-cdn-shv-*

| Shows | Evidence | Source |
| --- | --- | --- |
| Scope | Example host resolves and matches (pihole-FTL). Example hosts tested with DNS and pihole-FTL (full record): {"whatsapp-cdn-shv-01-atl3.fbcdn.net": {"dns": "NOERROR", "cname": [], "ftl_match": true}, "whatsapp-cdn-shv-02-mia3.fbcdn.net": {"dns": "NOERROR", "cname": [], "ftl_match": true}, "whatsapp-cdn-shv-01-iad3.fbcdn.net": {"dns": "NOERROR", "cname": [], "ftl_match": true}} | pihole-FTL test |

Note: Open-ended.

### `(\.|^)windowsupdate\.com$`

Windows Update (windowsupdate.com and its subdomains)

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | Microsoft documents *.windowsupdate.com: "HTTP *.windowsupdate.com" | [learn.microsoft.com](https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting) |

<details>
<summary>Hosts this rule covers, checked one by one (1)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `windowsupdate.com` | NOERROR | no | 0 |

</details>

### `^(www\.|go\.)?microsoft\.com$|^(www\.)?windows\.com$`

Microsoft and Windows main sites and go.microsoft.com links

<details>
<summary>Hosts this rule covers, checked one by one (5)</summary>

| Host | DNS | Named in a source | Lookups on the maintainer's network |
| --- | --- | --- | --- |
| `windows.com` | NOERROR | no | 0 |
| `www.windows.com` | NOERROR | no | 0 |

- go.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/azure/devops/organizations/security/allow-list-ip-url, https://learn.microsoft.com/en-us/defender-endpoint/configure-network-connections-microsoft-defender-antivirus, https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, https://learn.microsoft.com/en-us/microsoft-365/enterprise/network-requests-in-office-2016-for-mac; 0 lookups on the maintainer's network
- microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/azure/devops/organizations/security/allow-list-ip-url, https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services, https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- www.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services, https://learn.microsoft.com/en-us/defender-endpoint/configure-network-connections-microsoft-defender-antivirus, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions; 1 lookups on the maintainer's network

</details>

### `^((www|(w[0-9]\.)?web|media((-[a-z]{3}|\.[a-z]{4})[0-9]{1,2}-[0-9](\.|-)(cdn|fna))?)\.)?whatsapp\.(com|net)$`

WhatsApp - whatsapp.com and whatsapp.net with www, web and media hosts

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `whatsapp.com` | Pi-hole query log |

### `^(aic|eic|kic)\.(cdplauncher|lgchhomeapp)\.lgtvcommon\.com$`

LG Channels app launch hosts (aic reported to HaGeZi) and their eic/kic regional names - Exceptions to the lgtvcommon.com block rule

| Shows | Evidence | Source |
| --- | --- | --- |
| If blocked | HaGeZi #11544 report: "Blocking "lgtvcommon.com" domain requests is preventing LG Channels app to be launched on the smart TV" | [hagezi/dns-blocklists #11544](https://github.com/hagezi/dns-blocklists/issues/11544) |
| Context | Hosts named in that report: "aic.cdplauncher.lgtvcommon.com aic.cdpbeacon.lgtvcommon.com aic.lgchhomeapp.lgtvcommon.com" | [hagezi/dns-blocklists #11544](https://github.com/hagezi/dns-blocklists/issues/11544) |
| What it does | HaGeZi kept only these lgtvcommon.com hosts blocked; cdplauncher and lgchhomeapp are not among them: "Remains blocked (Ads/Tracking): ``` ads.lgtvcommon.com adts.lgtvcommon.com cdpbeacon.lgtvcommon.com cdpbeacon2.lgtvcommon.com" | [hagezi/dns-blocklists #11544](https://github.com/hagezi/dns-blocklists/issues/11544) |
| What it does | HaGeZi accepted region variants of LG service hosts as needed for the same function: "I presume any `*.service.lgtvcommon.com` domains are required for the same function, just different regions." | [hagezi/dns-blocklists #1807](https://github.com/hagezi/dns-blocklists/issues/1807) |
| Scope | pihole-FTL: the tracking host cdpbeacon stays blocked. Ftl_tests_2026_11_14: `"aic.cdpbeacon.lgtvcommon.com": "no match"` | Direct check |
| Scope | pihole-FTL: eic.recommend stays blocked. Ftl_tests_2026_11_14: `"eic.recommend.lgtvcommon.com": "no match"` | Direct check |

<details>
<summary>Hosts this rule covers, checked one by one (6)</summary>

- aic.cdplauncher.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
- aic.lgchhomeapp.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
- eic.cdplauncher.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
- eic.lgchhomeapp.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
- kic.cdplauncher.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
- kic.lgchhomeapp.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex

</details>

Note: Decision 2026-11-14: added. Only the aic hosts were reported; the eic and kic names are the same hosts for other regions. No list classifies any of them as tracking, so allowing them costs no privacy.

## RegEx blocklist: `regex-blacklist.sql` (27 entries)

### `^aax(-[a-z0-9]+)*(\.[a-z0-9-]+)?\.amazon\.com$`

Amazon aax hosts (aax-*.amazon.com) - Most of its 20 matches come from ad blocklists

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Matches 20 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |
| Observed | Seen on the maintainer's network: `aax-us-east-retail-direct.amazon.com` | Pi-hole query log |

### `^ads?\.[a-z0-9-]+\.com\.edgesuite\.net$`

Ad hosts on Akamai edgesuite.net (ad. and ads. only, so Windows Update's adl.windows.com is not blocked)

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Matches 3 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |
| Observed | Seen on the maintainer's network: `ads.hulu.com.edgesuite.net` | Pi-hole query log |
| Context | Narrowed in the second audit: commit message: "stop blocking Windows Update via an Akamai ad rule" | [commit 652f298](https://github.com/slyfox1186/pihole-regex/commit/652f298) |

### `^adim(age|g)s?[0-9]*[_.-]`

Generic rule - Blocks names that start with adimage or adimg

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Same rule as mmotti's regex list: "^adim(age\|g)s?[0-9]*[_.-]" | [mmotti/pihole-regex (GitHub)](https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list) |
| Observed | Matches 37 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |

### `^(.+[_.-])?adse?rv(er?|ice)?s?[0-9]*[_.-]`

Generic rule - Matches adserver-style name segments (adserv, adsrv, adservice, with plural and numbered forms) between dots, dashes or underscores

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Same rule as mmotti's regex list: "^(.+[_.-])?adse?rv(er?\|ice)?s?[0-9]*[_.-]" | [mmotti/pihole-regex (GitHub)](https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list) |
| Observed | Matches 827 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |
| Observed | Seen on the maintainer's network: `adservice.google.com` | Pi-hole query log |
| Scope | pihole-FTL: inside a hyphenated name. Pihole-FTL regex-test results (full record): {"foo-adserver.example.com": "match", "adserver2.example.com": "match", "adservice.google.com": "match", "adsrv.example.com": "match"} | pihole-FTL test |
| Scope | pihole-FTL: numbered form. Pihole-FTL regex-test results (full record): {"foo-adserver.example.com": "match", "adserver2.example.com": "match", "adservice.google.com": "match", "adsrv.example.com": "match"} | pihole-FTL test |

### `(^|\.)ad([sx][0-9]*|[0-9]+|system)[_.-]|(^|\.)adv[0-9]*([_-]|\.[^.]+\.[^.]+)`

Generic ad rule - ads/adx (+digits), ad+digits or adsystem before . - or _; adv (+digits) needs - or _ or two more labels

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Matches 4500 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |
| Observed | Seen on the maintainer's network: `ads.celtra.com` | Pi-hole query log |
| Context | Narrowed from mmotti's ad rule in the 2026-11-13 audit: commit message: "narrow the ad rule so .adv.br sites resolve" | [commit d93c6dd](https://github.com/slyfox1186/pihole-regex/commit/d93c6dd) |
| Scope | pihole-FTL: plain ad. does not match. Pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"} | pihole-FTL test |
| Scope | pihole-FTL: ads. matches. Pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"} | pihole-FTL test |
| Scope | pihole-FTL: adx. matches. Pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"} | pihole-FTL test |
| Scope | pihole-FTL: ad3. matches. Pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"} | pihole-FTL test |
| Scope | pihole-FTL: adsystem. matches. Pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"} | pihole-FTL test |
| Scope | pihole-FTL: adv. with two more labels matches. Pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"} | pihole-FTL test |
| Scope | pihole-FTL: .adv.br does not match. Pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"} | pihole-FTL test |
| Scope | pihole-FTL: ads3. matches. Pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"} | pihole-FTL test |
| Scope | pihole-FTL: adx7. matches. Pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"} | pihole-FTL test |
| Scope | pihole-FTL: adv- matches. Pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"} | pihole-FTL test |
| Scope | pihole-FTL: adv_ matches. Pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"} | pihole-FTL test |
| Scope | pihole-FTL: adv2. matches. Pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"} | pihole-FTL test |
| Scope | pihole-FTL: adv2- matches. Pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"} | pihole-FTL test |

Note: Real services it catches have exceptions (Ayla, the Jamaica tax portal, OAB webmail).

### `^adtrack(er|ing)?[0-9]*[_.-]`

Generic rule - Blocks names that start with adtrack/adtracker/adtracking

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Same rule as mmotti's regex list: "^adtrack(er\|ing)?[0-9]*[_.-]" | [mmotti/pihole-regex (GitHub)](https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list) |
| Observed | Matches 27 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |

### `^advert(s|is(ing|ements?))?[0-9]*[_.-]`

Generic rule - Blocks names that start with advert, adverts or advertising

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Same rule as mmotti's regex list: "^advert(s\|is(ing\|ements?))?[0-9]*[_.-]" | [mmotti/pihole-regex (GitHub)](https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list) |
| Observed | Matches 66 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |

### `(^|\.)(ahoravideo-(blog|cdn)\.com|bideo-(cdn|schnellvpn)\.com|fairu-(chat|endpoint|schnellvpn)\.com|fairu-schnellvpn\.xyz|privatproxy-(chat|schnellvpn)\.com|wmail-blog\.com)$`

ViperSoftX malware command servers - The 11 of its 50 generated names whose subdomains no adlist blocks

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | The malware's PowerShell builds these names: "@("wmail", "fairu", "bideo", "privatproxy", "ahoravideo")" | [chris.partridge.tech](https://chris.partridge.tech/2022/evolution-of-vipersoftx-dga/) |
| Scope | Expands to 50 names | Test corpus |
| Observed | Narrowed on 2026-11-22. `pihole -q` on a subdomain of each name showed HaGeZi Threat Intelligence Feeds (and HaGeZi Multi PRO) block 39 of the 50 with all subdomains; the rule keeps the other 11 | Direct check |

### `^analytics?[_.-]`

Generic rule - Blocks names that start with analytic or analytics

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Same rule as mmotti's regex list: "^analytics?[_.-]" | [mmotti/pihole-regex (GitHub)](https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list) |
| Observed | Matches 2070 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |
| Observed | Seen on the maintainer's network: `analytics.google.com` | Pi-hole query log |

Note: Real services under analytics. need exact allows.

### `(\.|^)antivirushub\.com$`

antivirushub.com - Maintainer added it as a 1337x.to redirect domain; it resolved on 2026-11-13

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | antivirushub.com DNS status on 2026-11-13. DNS status `antivirushub.com`: `NOERROR` | DNS lookup |
| Context | Maintainer's earlier note: added the line `(\.\|^)antivirushub\.com$ -- 1337x.to - Sneaky redirect domains that probably log your IP and any other information it gets from your browser sending a GET or POST request.` | [commit 2c047d2](https://github.com/slyfox1186/pihole-regex/commit/2c047d2) |

Status: The note repeats the maintainer's earlier report; purpose unverified. No source for the 1337x redirect claim; no blocklist in the maintainer's Pi-hole contains it.

### `^api\..*\.hismarttv\.com$`

api.*.hismarttv.com hosts - Perflyst's Smart TV rules block them

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Perflyst's Smart TV regex list has the same rule: "^api\..*\.hismarttv\.com$" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/regex.list) |
| Observed | Matches 3 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |

### `^(collect|usage)-(eu|us)-fy[0-9]+\.myhomescreen\.tv$`

Panasonic Viera TV hosts collect-/usage-*.myhomescreen.tv - Perflyst blocks them

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Perflyst blocks these hosts under Panasonic: the page lists `collect-us-fy2022.myhomescreen.tv` under the heading "Panasonic Viera &amp; panny tv" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |
| Observed | Matches 36 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |

### `(\.|^)filesupdating\.com$`

filesupdating.com - Maintainer labeled it iTop VPN; it resolved on 2026-11-13

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | filesupdating.com DNS status on 2026-11-13. DNS status `filesupdating.com`: `NOERROR` | DNS lookup |
| Context | Maintainer's earlier note: added the line `(\.\|^)filesupdating\.com$ -- iTop VPN` | [commit 2c047d2](https://github.com/slyfox1186/pihole-regex/commit/2c047d2) |

Status: The note repeats the maintainer's earlier report; purpose unverified. No source describes it.

### `(\.|^)internetat\.tv$`

internetat.tv - Perflyst's Smart TV rules block it

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Perflyst's Smart TV regex list has the same rule: "(^\|\.)internetat\.tv$" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/regex.list) |
| Observed | Matches 3 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |

### `(^|\.)lgtvcommon\.com$`

lgtvcommon.com - Perflyst's Smart TV rules block it; guide-data and LG Channels app launch hosts are allowed in regex-whitelist

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Perflyst's Smart TV regex list has the same rule: "(^\|\.)lgtvcommon\.com" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/regex.list) |
| Observed | Seen on the maintainer's network: `eic.recommend.lgtvcommon.com` | Pi-hole query log |

Note: Decision 2026-11-14: kept. HaGeZi #11544 (2026-09-23) keeps recommend, cdpbeacon and other lgtvcommon.com tracking hosts blocked; the guide-data and LG Channels hosts are allowed by regex-whitelist.

### `(\.|^)log[0-9]*\.spotify\.com$`

Matches log.spotify.com, log plus any digits under spotify.com, and subdomains of those hosts

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Matches 2 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |
| Scope | pihole-FTL: log123 matches. Pihole-FTL regex-test results (full record): {"log.spotify.com": "match", "log2.spotify.com": "match", "log123.spotify.com": "match", "x.log2.spotify.com": "match", "logger.spotify.com": "no match"} | pihole-FTL test |
| Scope | pihole-FTL: subdomain matches. Pihole-FTL regex-test results (full record): {"log.spotify.com": "match", "log2.spotify.com": "match", "log123.spotify.com": "match", "x.log2.spotify.com": "match", "logger.spotify.com": "no match"} | pihole-FTL test |
| Scope | pihole-FTL: logger does not match. Pihole-FTL regex-test results (full record): {"log.spotify.com": "match", "log2.spotify.com": "match", "log123.spotify.com": "match", "x.log2.spotify.com": "match", "logger.spotify.com": "no match"} | pihole-FTL test |

### `(\.|^)pavv\.co\.kr$`

pavv.co.kr (Samsung) - infolink.pavv.co.kr is allowed for the app store and sign-in

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Perflyst's Smart TV regex list has the same rule: "(^\|\.)pavv\.co\.kr$" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/regex.list) |
| Observed | Matches 2 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |

### `(^|\.)samsungcloudsolution\.net$`

samsungcloudsolution.net (Samsung) - Exact allows exempt configprd and lcprd1.samsungcloudsolution.net

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Perflyst's Smart TV regex list has the same rule: "(^\|\.)samsungcloudsolution\.net$" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/regex.list) |
| Observed | Seen on the maintainer's network: `lcprd1.samsungcloudsolution.net` | Pi-hole query log |

### `(\.|^)samsungelectronics\.com$`

samsungelectronics.com - Perflyst's Samsung TV rules block it

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Perflyst's Smart TV regex list has the same rule: "(^\|\.)samsungelectronics\.com$" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/regex.list) |
| Observed | Matches 10 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |

Status: Purpose unverified. Perflyst gives no description.

### `(\.|^)samsungqbe\.com$`

samsungqbe.com and its subdomains - Blocks Samsung service hosts; TV Plus and one service host are allowed

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Seen on the maintainer's network: `osb-krsvc-v2.samsungqbe.com` | Pi-hole query log |
| Observed | Seen on the maintainer's network: `1070` | Pi-hole query log |

Note: Decision 2026-11-14: kept. The maintainer chose to keep it. It blocks the Samsung device's osb-*-v2 lookups (about 1,900 since 2026-11-12); if TV Plus or sign-in misbehaves, check this rule first.

### `(\.|^)samsungrm\.net$`

samsungrm.net - Perflyst's Samsung TV rules block it

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Perflyst's Smart TV regex list has the same rule: "(^\|\.)samsungrm\.net$" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/regex.list) |
| Observed | Matches 2 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |

Status: Purpose unverified. Perflyst gives no description.

### `(\.|^)smartshare\.lgtvsdp\.com$`

smartshare.lgtvsdp.com - Perflyst's Smart TV rules block it

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Perflyst's Smart TV regex list has the same rule: "(^\|\.)smartshare\.lgtvsdp\.com" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/regex.list) |
| Observed | smartshare.lgtvsdp.com DNS status on 2026-11-13. DNS status `smartshare.lgtvsdp.com`: `NOERROR` | DNS lookup |

### `^[a-z0-9]+\.ssm[1-2]?\.internet\.sony\.tv$`

Sony TV hosts under ssm*.internet.sony.tv (the ssm hosts themselves stay reachable)

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Matches 2 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |
| Context | Perflyst leaves ssm1.internet.sony.tv unblocked: "#ssm1.internet.sony.tv # https://github.com/notracking/hosts-blocklists/issues/384" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

Status: Purpose unverified. What the per-device subdomains do is unverified; Perflyst deliberately does not block the ssm hosts.

### `^stat(s|istics)?[0-9]*[-_]`

Generic rule - Blocks names starting stat-, stats- or statistics-

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Matches 85 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |
| Context | mmotti's original stats rule: "^stat(s\|istics)?[0-9]*[_.-]" | [mmotti/pihole-regex (GitHub)](https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list) |
| Context | Maintainer's narrowed rule: added the line `^stat(s\|istics)?[0-9]*[-_] -- stats/metrics (narrowed to avoid false positives)` | [commit 1677a89](https://github.com/slyfox1186/pihole-regex/commit/1677a89) |

### `(^|\.)telemetry[-_][a-z0-9]`

Generic rule - Blocks telemetry- and telemetry_ names

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Matches 7 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |
| Context | mmotti's original telemetry rule: "^(.+[_.-])?telemetry[_.-]" | [mmotti/pihole-regex (GitHub)](https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list) |
| Context | Maintainer's narrowed rule: added the line `(^\|\.)telemetry[-_][a-z0-9] -- telemetry (narrowed to avoid false positives)` | [commit 1677a89](https://github.com/slyfox1186/pihole-regex/commit/1677a89) |

### `(\.|^)tvinteractive\.tv$`

tvinteractive.tv - Perflyst's Smart TV rules block it

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Perflyst's Smart TV regex list has the same rule: "(\.\|^)tvinteractive\.tv$" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/regex.list) |
| Observed | Matches 5 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |

Status: Purpose unverified. Perflyst gives no description; the old note said Vizio Inscape viewing data.

### `^[a-z]{2}-[a-z]{2}-[a-z]{2}\.ybp\.gysm\.yahoodns\.net$`

Yahoo DNS name pattern xx-xx-xx.ybp.gysm.yahoodns.net - No matches in the 2.17M-name test corpus on 2026-11-13

| Shows | Evidence | Source |
| --- | --- | --- |
| Observed | Matches 0 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 | Test corpus |
| Context | Maintainer's earlier note: added the line `^[a-z]{2}-[a-z]{2}-[a-z]{2}\.ybp\.gysm\.yahoodns\.net$ -- Yahoo` | [commit 2c047d2](https://github.com/slyfox1186/pihole-regex/commit/2c047d2) |

Status: The note repeats the maintainer's earlier report. Decision 2026-11-14: kept. No current matches, so it neither blocks nor breaks anything today.

## Adlists: `adlists.txt` (32 lists)

### `https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Spam/hosts`

FadeMind add.Spam (StevenBlack extras) - Spam websites

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Fademind's Spammers: https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Spam/hosts" | [firebog.net](https://firebog.net/) |
| What it does | FadeMind's README: "\| add.Spam   	 	 \| Spam websites. **MIRROR**" | [FadeMind/hosts.extras (GitHub)](https://raw.githubusercontent.com/FadeMind/hosts.extras/master/README.md) |

### `https://raw.githubusercontent.com/PolishFiltersTeam/KADhosts/master/KADhosts.txt`

KADhosts by PolishFiltersTeam - Scam and fraud sites (SMS subscription traps, viruses, fake shops)

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "PolishFiltersTeam KADhosts: https://raw.githubusercontent.com/PolishFiltersTeam/KADhosts/master/KADhosts.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "Filtry chroniace przed roznego rodzaju przekretami i oszustwami, takimi jak np. subskrypcje SMS, wirusy i falszywe sklepy internetowe." | [PolishFiltersTeam/KADhosts (GitHub)](https://raw.githubusercontent.com/PolishFiltersTeam/KADhosts/master/KADhosts.txt) |

### `https://v.firebog.net/hosts/static/w3kbl.txt`

WaLLy3K's personal blocklist (Firebog maintainer) - Manually verified suspicious domains

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "WaLLy3K's Blacklist: https://v.firebog.net/hosts/static/w3kbl.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "Content added to this list has been manually verified" | [v.firebog.net](https://v.firebog.net/hosts/static/w3kbl.txt) |

### `https://adaway.org/hosts.txt`

AdAway default list - Mobile ad providers and some analytics

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "AdAway: https://adaway.org/hosts.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "Blocking mobile ad providers and some analytics providers" | [adaway.org](https://adaway.org/hosts.txt) |

### `https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext`

Peter Lowe's ad server list - Ads, trackers and other unwanted hosts

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Peter Lowe's Adservers: https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&amp;showintro=0&amp;mimetype=plaintext" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "Blocklist for use with hosts files to block ads, trackers, and other nasty things" | [pgl.yoyo.org](https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext) |

### `https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt`

Anudeep's Blacklist - Ad servers and tracking hosts

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Anudeep ND's Blacklist: https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "Host file to block ads, tracking and more!" | [anudeepND/blacklist (GitHub)](https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt) |

### `https://raw.githubusercontent.com/bigdargon/hostsVN/master/hosts`

hostsVN by bigdargon - Firebog Advertising list

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "hostsVN: https://raw.githubusercontent.com/bigdargon/hostsVN/master/hosts" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "Title: hostsVN" | [bigdargon/hostsVN (GitHub)](https://raw.githubusercontent.com/bigdargon/hostsVN/master/hosts) |

### `https://v.firebog.net/hosts/AdguardDNS.txt`

AdGuard DNS filter (parsed by Firebog) - Domain version of AdGuard's DNS filter

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Adguard DNS: https://v.firebog.net/hosts/AdguardDNS.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "AdguardDNS, parsed and mirrored by https://firebog.net" | [v.firebog.net](https://v.firebog.net/hosts/AdguardDNS.txt) |

### `https://v.firebog.net/hosts/Admiral.txt`

Admiral anti-adblock domains (LanikSJ, parsed by Firebog)

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "LanikSJ's Admiral Anti-Adblock: https://v.firebog.net/hosts/Admiral.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "Admiral, parsed and mirrored by https://firebog.net" | [v.firebog.net](https://v.firebog.net/hosts/Admiral.txt) |

### `https://v.firebog.net/hosts/Easylist.txt`

EasyList (parsed by Firebog) - Domain version of easylist.txt

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Easylist: https://v.firebog.net/hosts/Easylist.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "from https://easylist.to/easylist/easylist.txt" | [v.firebog.net](https://v.firebog.net/hosts/Easylist.txt) |

### `https://hostfiles.frogeye.fr/firstparty-trackers-hosts.txt`

Frogeye first-party trackers host list

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Geoffrey Frogeye's First-Party Trackers: https://hostfiles.frogeye.fr/firstparty-trackers-hosts.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "First-party trackers host list" | [hostfiles.frogeye.fr](https://hostfiles.frogeye.fr/firstparty-trackers-hosts.txt) |

### `https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt`

WindowsSpyBlocker spy rules by crazy-max - Windows telemetry hosts

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Crazy Max's Microsoft Telemetry: https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "WindowsSpyBlocker - Hosts spy rules" | [crazy-max/WindowsSpyBlocker (GitHub)](https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt) |

### `https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.2o7Net/hosts`

FadeMind add.2o7Net - Adobe 2o7 network tracking hosts

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Fademind's 2o7 Network Trackers: https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.2o7Net/hosts" | [firebog.net](https://firebog.net/) |
| What it does | FadeMind's README: "2o7 Network tracking **MIRROR**" | [FadeMind/hosts.extras (GitHub)](https://raw.githubusercontent.com/FadeMind/hosts.extras/master/README.md) |

### `https://v.firebog.net/hosts/Easyprivacy.txt`

EasyPrivacy (parsed by Firebog) - Domain version of easyprivacy.txt

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Easyprivacy: https://v.firebog.net/hosts/Easyprivacy.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "from https://easylist.to/easylist/easyprivacy.txt" | [v.firebog.net](https://v.firebog.net/hosts/Easyprivacy.txt) |

### `https://v.firebog.net/hosts/Prigent-Ads.txt`

Fabrice Prigent's ad list (Toulouse Capitole University, parsed by Firebog) - Ad domains

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Fabrice Prigent's Ads: https://v.firebog.net/hosts/Prigent-Ads.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "dsi.ut-capitole.fr/blacklists/download/publicite.tar.gz" | [v.firebog.net](https://v.firebog.net/hosts/Prigent-Ads.txt) |

### `https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-malware.txt`

NoTrack malware list by QuidsUp - Malware, phishing and adware domains

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Quidsup Malicious: https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-malware.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "Domains classified as malware, phishing or adware" | [gitlab.com](https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-malware.txt) |

### `https://lists.cyberhost.uk/malware.txt`

CyberHost.uk malware and phishing list

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "CyberHost.uk Malware Domains: https://lists.cyberhost.uk/malware.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "CyberHost.uk Malware and Phishing Blocklist" | [lists.cyberhost.uk](https://lists.cyberhost.uk/malware.txt) |

### `https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-hosts-online.txt`

Online malicious hosts from abuse.ch URLhaus (malware-filter mirror)

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | The list's own header: "Title: Online Malicious Hosts Blocklist" | [malware-filter.gitlab.io](https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-hosts-online.txt) |
| What it does | The list's own header: "Source: https://urlhaus.abuse.ch/api/" | [malware-filter.gitlab.io](https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-hosts-online.txt) |

### `https://phishing.army/download/phishing_army_blocklist_extended.txt`

Phishing Army extended list - Phishing domains from PhishTank, OpenPhish, CERT.PL and others

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Phishing Army's Extended Blocklist: https://phishing.army/download/phishing_army_blocklist_extended.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "Community phishing domain blocklist" | [phishing.army](https://phishing.army/download/phishing_army_blocklist_extended.txt) |

### `https://raw.githubusercontent.com/AssoEchap/stalkerware-indicators/master/generated/hosts`

Echap stalkerware indicators - Domains used by stalkerware apps that secretly spy on phones

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Echap's Stalkerware Indicators: https://raw.githubusercontent.com/AssoEchap/stalkerware-indicators/master/generated/hosts" | [firebog.net](https://firebog.net/) |
| What it does | Echap's README: "Indicators of compromise (IOC) for Stalkerware and Watchware applications for Android and iOS" | [AssoEchap/stalkerware-indicators (GitHub)](https://raw.githubusercontent.com/AssoEchap/stalkerware-indicators/master/README.md) |

### `https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt`

Dandelion Sprout's Anti-Malware List

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "DandelionSprout's Anti Malware Filter: https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "This list goes the extra kilometer to prevent more malware than other mainstream anti-malware lists." | [DandelionSprout/adfilt (GitHub)](https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt) |

### `https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Risk/hosts`

FadeMind add.Risk - Risky sites (malware and similar)

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Fademind's Risky Hosts: https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Risk/hosts" | [firebog.net](https://firebog.net/) |
| What it does | FadeMind's README: "Websites with risk content, malwares etc. **MIRROR**" | [FadeMind/hosts.extras (GitHub)](https://raw.githubusercontent.com/FadeMind/hosts.extras/master/README.md) |

### `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/tif.txt`

HaGeZi Threat Intelligence Feeds - Malware, cryptojacking, scams, spam and phishing

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | The list's own header: "Title: HaGeZi's Threat Intelligence Feeds" | [hagezi/dns-blocklists (GitHub)](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/tif.txt) |
| What it does | The list's own header: "This blocklist targets malware, cryptojacking, scams, spam, and phishing." | [hagezi/dns-blocklists (GitHub)](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/tif.txt) |

### `https://raw.githubusercontent.com/Spam404/lists/master/main-blacklist.txt`

Spam404 main blacklist - Firebog Malicious list

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Spam404: https://raw.githubusercontent.com/Spam404/lists/master/main-blacklist.txt" | [firebog.net](https://firebog.net/) |

### `https://v.firebog.net/hosts/Prigent-Crypto.txt`

Fabrice Prigent's cryptojacking list (parsed by Firebog)

| Shows | Evidence | Source |
| --- | --- | --- |
| Context | Firebog lists it under this name: "Fabrice Prigent's Cryptojacking: https://v.firebog.net/hosts/Prigent-Crypto.txt" | [firebog.net](https://firebog.net/) |
| What it does | The list's own header: "dsi.ut-capitole.fr/blacklists/download/cryptojacking.tar.gz" | [v.firebog.net](https://v.firebog.net/hosts/Prigent-Crypto.txt) |

### `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.txt`

HaGeZi Multi PRO - Ads, trackers, telemetry, phishing, malware and scams

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | The list's own header: "Title: HaGeZi's Multi PRO - extended protection (recommended)" | [hagezi/dns-blocklists (GitHub)](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.txt) |
| What it does | The list's own header: "Blocks ads, trackers, metrics, telemetry, phishing, malware, scams" | [hagezi/dns-blocklists (GitHub)](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.txt) |

### `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.amazon.txt`

HaGeZi Amazon native tracker list - Trackers built into Amazon devices, apps and operating systems

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | The list's own header: "Title: HaGeZi's Amazon Tracker - blocks built-in trackers from devices, apps, and OSes!" | [hagezi/dns-blocklists (GitHub)](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.amazon.txt) |

### `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.samsung.txt`

HaGeZi Samsung native tracker list - Trackers built into Samsung devices, apps and operating systems

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | The list's own header: "Title: HaGeZi's Samsung Tracker - blocks built-in trackers from devices, apps, and OSes!" | [hagezi/dns-blocklists (GitHub)](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.samsung.txt) |

### `https://hagezi-mirror.dnsbunker.org/adblock/dyndns.txt`

HaGeZi Dynamic DNS - Dynamic DNS providers often abused to host malware and phishing

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | The list's own header: "Title: HaGeZi's DynDNS - guards against dynamic DNS abuse!" | [hagezi-mirror.dnsbunker.org](https://hagezi-mirror.dnsbunker.org/adblock/dyndns.txt) |
| What it does | The list's own header: "Blocks dynamic DNS services that get abused for phishing campaigns and other shady activity." | [hagezi-mirror.dnsbunker.org](https://hagezi-mirror.dnsbunker.org/adblock/dyndns.txt) |
| Source | Official mirror: the page lists hagezi-mirror.dnsbunker.org as its build mirror, published with every build. | [hagezi/dns-blocklists (GitHub)](https://github.com/hagezi/dns-blocklists) |

### `https://hagezi-mirror.dnsbunker.org/adblock/doh.txt`

HaGeZi Encrypted DNS Bypass (DoH only) - Encrypted DNS servers that devices can use to bypass Pi-hole

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | The list's own header: "Title: HaGeZi's Encrypted DNS Bypass - stop people from sneaking around your DNS!" | [hagezi-mirror.dnsbunker.org](https://hagezi-mirror.dnsbunker.org/adblock/doh.txt) |
| What it does | The list's own header: "Prevent methods to bypass your DNS, blocks encrypted DNS only" | [hagezi-mirror.dnsbunker.org](https://hagezi-mirror.dnsbunker.org/adblock/doh.txt) |
| Source | Official mirror: the page lists hagezi-mirror.dnsbunker.org as its build mirror, published with every build. | [hagezi/dns-blocklists (GitHub)](https://github.com/hagezi/dns-blocklists) |

### `https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt`

Perflyst Smart TV list - Stops smart TVs sending data back home and blocks some TV interface ads

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | The list's own header: "This is a blocklist to block smart-TVs sending metadata back home, sometimes with the added benefit of blocking interface ads" | [perflyst.github.io](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) |

### `https://raw.githubusercontent.com/johang/cookie-consent-hosts/master/hosts.txt`

Cookie consent hosts by johang - Hides cookie and privacy consent banners on websites

| Shows | Evidence | Source |
| --- | --- | --- |
| What it does | The project's README: "A list of hosts that are used to display cookie and privacy consent banners on websites." | [johang/cookie-consent-hosts (GitHub)](https://raw.githubusercontent.com/johang/cookie-consent-hosts/master/README.md) |
