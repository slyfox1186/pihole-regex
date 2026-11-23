# Domain list notes: sources and evidence

Every entry in `domains/` carries a short note. For the four `.sql` lists, `pi.py` stores the note as the entry's
comment in Pi-hole. The adlist descriptions in `adlists.txt` appear only in the repository and on this page,
because `adlist.py` gives every adlist the same fixed comment. This page lists the evidence behind each note, so
anyone can check what a domain is and why it is allowed or blocked.

Collected and checked on 2026-11-13, 2026-11-14, 2026-11-21 and 2026-11-22. Web sources were fetched without JavaScript and every quote
below was confirmed to appear on the live page. Pages change; a quote that no longer appears means the source changed
after that date.

## Filter changes on 2026-11-22

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

## Filter changes on 2026-11-21

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

## Filter changes on 2026-11-14

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
Flags:

- `wrong_list`: evidence suggests it may be on the wrong list
- `review`: needs the maintainer's decision (details given)
- `unverified_purpose`: purpose unverified
- `nxdomain`: DNS returned NXDOMAIN on 2026-11-13
- `other`: note repeats the maintainer's earlier report, cited by commit

Flag counts: `other` 37, `review` 1, `unverified_purpose` 51.

## Open questions

Entries that are still open: their purpose is unverified, or their DNS name did not resolve.

### Needs the maintainer's decision (details given) (1)

- exact-blacklist.sql: `qt2-ngfts.lge.com` - LG host sharing ngfts.lge.com's Akamai name - Proposed for blocking in HaGeZi #309; role unverified. It shares ngfts.lge.com's CNAME and 'SDP 2.0' page; blocking may affect LG Content Store images. The old 'file transfer' note had no source.

### Purpose unverified (42)

- exact-whitelist.sql: `clients.config.office.net` - Microsoft 365 host under the documented *.office.net endpoint - Exact role unverified. Microsoft documents only the *.office.net wildcard.
- exact-whitelist.sql: `continuum.dds.microsoft.com` - Microsoft-run host - Purpose unverified (old note said Your Phone notification mirroring, no source found). No Microsoft document names this host; the Your Phone claim in the old note has no source.
- exact-whitelist.sql: `emea.ng.msg.teams.microsoft.com` - Microsoft Teams host under the documented *.teams.microsoft.com endpoint - Exact role unverified. Its CNAME name mentions messaging; that is not a documented role.
- exact-whitelist.sql: `emea.pptservicescast.officeapps.live.com` - Microsoft 365 / Office Online host under the documented *.officeapps.live.com endpoint - Exact role unverified. Microsoft documents only the wildcard.
- exact-whitelist.sql: `mamservice.manage.microsoft.com` - Microsoft Intune host under the documented *.manage.microsoft.com - Exact role unverified. Microsoft documents only the *.manage.microsoft.com wildcard for Intune.
- exact-whitelist.sql: `mrs-efz.ms-acdc.office.com` - Microsoft 365 (office.com) service host - Exact role unverified. Only the *.office.com wildcard is documented.
- exact-whitelist.sql: `mscomajax.vo.msecnd.net` - Microsoft-run host (msecnd.net, required by Microsoft 365) - Exact role unverified. Microsoft documents only the *.msecnd.net wildcard; its root redirects to Microsoft's ASP.NET site.
- exact-whitelist.sql: `win1710.ipv6.microsoft.com` - Microsoft IPv6 host - Purpose unverified. No source names win1710.ipv6.microsoft.com; win10 and win1910 variants are documented as Teredo server names in Microsoft Q&amp;A, so this is an inference.
- exact-blacklist.sql: `aic.api.lgtviot.com` - LG webOS TV host (lgtviot.com) - Proposed for blocking in HaGeZi issue #309; role unverified. The old note said 'IoT telemetry'; no source states what the host does.
- exact-blacklist.sql: `aic.lgtviot.com` - LG webOS TV host (lgtviot.com) - Proposed for blocking in HaGeZi issue #309; role unverified. The old note said 'IoT telemetry'; no source states what the host does.
- exact-blacklist.sql: `aic.sports.lgtviot.com` - LG webOS TV host (lgtviot.com) - Listed in HaGeZi issue #309; role unverified. Only listed, no function stated.
- exact-blacklist.sql: `lgtvonline.lge.com` - LG webOS TV online service host - Role unverified. No source describes it.
- exact-whitelist.sql: `nine.plugins.plexapp.com` - Plex host - Pi-hole users list it for Plex. The source lists it among Plex domains without a role.
- exact-whitelist.sql: `o1.email.plex.tv` - Plex host - Pi-hole users list it for Plex. The source lists it among Plex domains without a role.
- exact-whitelist.sql: `o2.sg0.plex.tv` - Plex host - Pi-hole users list it for Plex. The source lists it among Plex domains without a role.
- exact-whitelist.sql: `tvthemes.plexapp.com.cdn.cloudflare.net` - Plex host - Pi-hole users list it for Plex. The source lists it among Plex domains without a role.
- exact-whitelist.sql: `api.gitkraken.com` - GitKraken host (gitkraken.com). The original line called it 'GitHub - Advanced Git CLI Program'; its role is unverified.
- exact-whitelist.sql: `api.termius.com` - Termius SSH client host (redirects to termius.com). The old note said it is required to sign in; not verified.
- exact-whitelist.sql: `gateway.cname.ustclug.org` - gateway.cname.ustclug.org - Role unverified. Kept from the 2022 'crucial CDN' set; nothing documents what points here.
- exact-whitelist.sql: `dualstack.osff.map.fastly.net` - Fastly host (map.fastly.net) - Which site uses it is unverified. No current CNAME in the lists points here; kept from the 2022 'crucial CDN' set.
- exact-whitelist.sql: `objects.githubusercontent.com` - GitHub content host. Exact role unverified.
- exact-whitelist.sql: `googlehosted.l.googleusercontent.com` - Google hosting CNAME target (googleusercontent.com) - Role unverified. No source describes it.
- exact-whitelist.sql: `edge.gycpi.b.yahoodns.net` - Yahoo-run edge host (yahoodns.net). The old note said Yahoo breaks without it; not verified.
- exact-whitelist.sql: `rover.ebay.com` - eBay-run host (rover.ebay.com). The old note said eBay links pass through it; not verified.
- exact-whitelist.sql: `static.opensubtitles.org` - OpenSubtitles host. Exact role unverified.
- exact-whitelist.sql: `yastatic.net` - Yandex-run host (redirects to yandex.ru). Exact role unverified.
- exact-blacklist.sql: `events-test.redditmedia.com` - Reddit-run host - Maintainer labeled it an event collector; exact role unverified.
- exact-blacklist.sql: `events-test-v2.redditmedia.com` - Reddit-run host - Maintainer labeled it an event collector; exact role unverified.
- exact-blacklist.sql: `nevoai-iothub-54-prod.azure-devices.net` - Microsoft Azure IoT Hub instance named 'nevoai' - Customer unverified (old note: LG Smart TV). Azure IoT Hub names do not show the customer.
- regex-whitelist.sql: `(\.|^)1drv\.ms$` - 1drv.ms and its subdomains. No fetched source names 1drv.ms; the old note said OneDrive short links.
- regex-whitelist.sql: `^apps\.bdimg\.(com|jomodns\.com)$` - apps.bdimg.com and apps.bdimg.jomodns.com. No fetched source; the old note said Baidu static file CDN.
- regex-whitelist.sql: `^(winatp-gw-neu|windows)\.microsoft\.com$` - Microsoft hosts winatp-gw-neu and windows.microsoft.com. Neither is in the cached Microsoft pages; the old note said Defender for Endpoint (Europe).
- regex-whitelist.sql: `^(csp|devicelistenerprod)\.microsoft\.com$` - Microsoft hosts csp and devicelistenerprod.microsoft.com - Purpose unverified. Neither host is in the cached Microsoft endpoint pages.
- regex-whitelist.sql: `^d(27xxe7juh1us6|2gatte9o95jao|3a3ewgd1iewwz|3ag4hukkh62yn|83eunklitikj)\.cloudfront\.net$` - Five CloudFront hosts - The Pi-hole forum lists one for Signal; the rest are unverified. CloudFront certificates do not show customers; only d83eunklitikj (Signal) and d2gatte9o95jao (anudeep whitelist) are sourced.
- regex-whitelist.sql: `^europe\.(cp\.wd|smartscreen(-prod|))\.microsoft\.com$` - Microsoft hosts europe.cp.wd, europe.smartscreen and europe.smartscreen-prod.microsoft.com. Microsoft documents SmartScreen hosts, but these Europe names are not in the cached pages.
- regex-whitelist.sql: `(\.|^)redd\.it$` - redd.it and its subdomains. No fetched source; the old note said Reddit images, video and short links.
- regex-blacklist.sql: `(\.|^)antivirushub\.com$` - antivirushub.com - Maintainer added it as a 1337x.to redirect domain; it resolved on 2026-11-13. No source for the 1337x redirect claim; no blocklist in the maintainer's Pi-hole contains it.
- regex-blacklist.sql: `(\.|^)filesupdating\.com$` - filesupdating.com - Maintainer labeled it iTop VPN; it resolved on 2026-11-13. No source describes it.
- regex-blacklist.sql: `(\.|^)samsungelectronics\.com$` - samsungelectronics.com - Perflyst's Samsung TV rules block it. Perflyst gives no description.
- regex-blacklist.sql: `(\.|^)samsungrm\.net$` - samsungrm.net - Perflyst's Samsung TV rules block it. Perflyst gives no description.
- regex-blacklist.sql: `^[a-z0-9]+\.ssm[1-2]?\.internet\.sony\.tv$` - Sony TV hosts under ssm*.internet.sony.tv (the ssm hosts themselves stay reachable). What the per-device subdomains do is unverified; Perflyst deliberately does not block the ssm hosts.
- regex-blacklist.sql: `(\.|^)tvinteractive\.tv$` - tvinteractive.tv - Perflyst's Smart TV rules block it. Perflyst gives no description; the old note said Vizio Inscape viewing data.


## Exact allowlist (exact-whitelist.sql)

### `arc.msn.com`

Note: Microsoft Windows Spotlight - Lock screen images, tips and suggested apps; also listed for the Xbox Series X/S Store app

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Windows Spotlight content endpoint (function): [https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints): "Windows Spotlight still tries to deliver new lock screen images and updated content but it fails; suggested apps, Microsoft account notifications, and Windows tips aren't downloaded. TLSv1.2/HTTPS/HTTP arc.msn.com"
- Pi-hole users list it for the Xbox Series X/S Store app (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `arc.msn.com` under the heading "Store App on Series X/S"

### `clientconfig.passport.net`

Note: Microsoft (passport.net) host - Microsoft lists it as a Windows Autopilot dependency; Pi-hole users list it for Xbox Live

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Listed by Microsoft as a Windows Autopilot dependency (function): [https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints): "Windows Autopilot - WNS Dependencies Default Required False clientconfig.passport.net"
- Pi-hole users list it for Xbox Live (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `clientconfig.passport.net` under the heading "Xbox Live"

### `clients.config.office.net`

Note: Microsoft 365 host under the documented *.office.net endpoint - Exact role unverified

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Covered by Microsoft 365's required *.office.net endpoint (product): [https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges): "47 Default Required No *.office.net"
- Flags: `unverified_purpose`. Microsoft documents only the *.office.net wildcard.

### `continuum.dds.microsoft.com`

Note: Microsoft-run host - Purpose unverified (old note said Your Phone notification mirroring, no source found)

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- anudeep's whitelist lists it, without a description (observation): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "continuum.dds.microsoft.com"
- Flags: `unverified_purpose`. No Microsoft document names this host; the Your Phone claim in the old note has no source.

### `cp801.prod.do.dsp.mp.microsoft.com`

Note: Microsoft Delivery Optimization host - Microsoft lists *.prod.do.dsp.mp.microsoft.com for Windows Update

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Matches Microsoft's documented Delivery Optimization endpoint *.prod.do.dsp.mp.microsoft.com (function): [https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting](https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting): "Protocol Endpoint URL TLS 1.2 *.prod.do.dsp.mp.microsoft.com"
- Delivery Optimization service wildcard (function): [https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints](https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints): "Delivery Optimization Service *.do.dsp.mp.microsoft.com"

### `geover.prod.do.dsp.mp.microsoft.com`

Note: Microsoft Delivery Optimization host - Microsoft lists *.prod.do.dsp.mp.microsoft.com for Windows Update

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Matches Microsoft's documented Delivery Optimization endpoint *.prod.do.dsp.mp.microsoft.com (function): [https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting](https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting): "Protocol Endpoint URL TLS 1.2 *.prod.do.dsp.mp.microsoft.com"
- Delivery Optimization service wildcard (function): [https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints](https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints): "Delivery Optimization Service *.do.dsp.mp.microsoft.com"

### `geo-prod.do.dsp.mp.microsoft.com`

Note: Microsoft Delivery Optimization host - Pi-hole users list it for the Microsoft Store

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft`
- Matches Microsoft's documented Delivery Optimization endpoint (function): [https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints](https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints): "Delivery Optimization Service *.do.dsp.mp.microsoft.com"
- Pi-hole users list it for the Microsoft Store (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `geo-prod.do.dsp.mp.microsoft.com` under the heading "Microsoft Store (Windows Store)"

### `dev.virtualearth.net`

Note: Microsoft Bing Maps host - Windows uses it to check for updates to offline maps

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Windows Maps endpoint (function): [https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions): "The following endpoints are used to check for updates to maps that have been downloaded for offline use."
- Named in that Maps list (function): [https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions): "HTTPS/HTTP dev.virtualearth.net"
- Pi-hole users list it for the Bing Maps Platform (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `dev.virtualearth.net` under the heading "Bing Maps Platform"

### `ecn.dev.virtualearth.net`

Note: Microsoft Bing Maps host - In Windows' Maps endpoint list and required by Microsoft 365

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Windows Maps endpoint (function): [https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions): "HTTPS/HTTP ecn.dev.virtualearth.net"
- Required Microsoft 365 endpoint (product): [https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges): "*.informationprotection.azure.com, ecn.dev.virtualearth.net"
- Pi-hole users list it for the Bing Maps Platform (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `ecn.dev.virtualearth.net` under the heading "Bing Maps Platform"

### `t0.ssl.ak.dynamic.tiles.virtualearth.net`

Note: Microsoft Bing Maps host - Covered by Windows' Maps endpoint list

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Matches the Maps wildcard in Microsoft's Windows endpoint list (function): [https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions): "HTTPS/HTTP *.ssl.ak.dynamic.tiles.virtualearth.net"
- Pi-hole users list it for the Bing Maps Platform (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `t0.ssl.ak.dynamic.tiles.virtualearth.net` under the heading "Bing Maps Platform"

### `t0.ssl.ak.tiles.virtualearth.net`

Note: Microsoft Bing Maps host - Covered by Windows' Maps endpoint list

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Matches the Maps wildcard in Microsoft's Windows endpoint list (function): [https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions): "HTTPS/HTTP *.ssl.ak.tiles.virtualearth.net"
- Pi-hole users list it for the Bing Maps Platform (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `t0.ssl.ak.tiles.virtualearth.net` under the heading "Bing Maps Platform"

### `displaycatalog.mp.microsoft.com`

Note: Microsoft Store catalog - Without it apps cannot be installed or updated from the Store

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft: blocking it stops Store installs and updates (consequence): [https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints): "If you turn off traffic for these endpoints, apps can't be installed or updated from the Microsoft Store. TLSv1.2/HTTPS/HTTP *displaycatalog.mp.microsoft.com"

### `dl.delivery.mp.microsoft.com`

Note: Microsoft download delivery - Windows Update, Microsoft Store and Edge downloads

- Microsoft runs it (CNAME to Akamai; certificate is domain-validated only) (owner): DNS CNAME chain: `a1683.dscd.akamai.net.`
- Matches Microsoft's documented *.dl.delivery.mp.microsoft.com (function): [https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting](https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting): "HTTP *.dl.delivery.mp.microsoft.com"
- Edge downloads (function): [https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints](https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints): "Edge Browser *.dl.delivery.mp.microsoft.com"
- Pi-hole users list it for the Microsoft Store (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `dl.delivery.mp.microsoft.com` under the heading "Microsoft Store (Windows Store)"

### `tlu.dl.delivery.mp.microsoft.com`

Note: Microsoft download delivery host - Microsoft lists *.dl.delivery.mp.microsoft.com for Windows Update

- Matches Microsoft's documented *.dl.delivery.mp.microsoft.com (function): [https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting](https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting): "HTTP *.dl.delivery.mp.microsoft.com"
- Pi-hole users list it for Windows 10 Update (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `tlu.dl.delivery.mp.microsoft.com` under the heading "Windows 10 Update"

### `dns.msftncsi.com`

Note: Windows network connectivity check (NCSI) - If this lookup fails, Windows shows the network alert in the taskbar

- Microsoft: NCSI resolves this name (function): [https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/internet-explorer-edge-open-connect-corporate-public-network](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/internet-explorer-edge-open-connect-corporate-public-network): "NCSI sends another DNS request to resolve the address of the dns.msftncsi.com FQDN. If any of these requests fails, the network alert appears in the Task Bar"

### `ipv6.msftncsi.com`

Note: Windows network connectivity check (NCSI) domain - Microsoft documents *.msftncsi.com for NCSI

- Microsoft documents *.msftncsi.com for NCSI (function): [https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/internet-explorer-edge-open-connect-corporate-public-network](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/internet-explorer-edge-open-connect-corporate-public-network): "*.msftncsi.com *.msftconnecttest.com"
- Pi-hole users list it under Windows/Microsoft (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `ipv6.msftncsi.com` under the heading "Windows/Microsoft"

### `www.msftncsi.com`

Note: Windows network connectivity check (NCSI) - Used by Windows 8.1 and earlier

- Microsoft: NCSI probe for Windows 8.1 and earlier (function): [https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/internet-explorer-edge-open-connect-corporate-public-network](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/internet-explorer-edge-open-connect-corporate-public-network): "Windows 8.1 or earlier versions: NCSI sends a DNS request to resolve the address of the www.msftncsi.com FQDN."

### `www.msftconnecttest.com`

Note: Windows network connectivity check (NCSI) - Used by Windows 10 and later

- Microsoft: NCSI probe for Windows 10 and later (function): [https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/internet-explorer-edge-open-connect-corporate-public-network](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/internet-explorer-edge-open-connect-corporate-public-network): "Windows 10 or later versions: NCSI sends a DNS request to resolve the address of the www.msftconnecttest.com FQDN."

### `ecs.office.com`

Note: Microsoft feature deployment service - Microsoft lists it as an Intune feature-deployment dependency

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft lists it as a feature deployment dependency (function): [https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints): "Dependency - Feature Deployment Default Required False config.edge.skype.com ecs.office.com"

### `emea.ng.msg.teams.microsoft.com`

Note: Microsoft Teams host under the documented *.teams.microsoft.com endpoint - Exact role unverified

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Covered by Microsoft Teams' required *.teams.microsoft.com (product): [https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges): "*.lync.com, *.teams.cloud.microsoft, *.teams.microsoft.com"
- Flags: `unverified_purpose`. Its CNAME name mentions messaging; that is not a documented role.

### `emea.pptservicescast.officeapps.live.com`

Note: Microsoft 365 / Office Online host under the documented *.officeapps.live.com endpoint - Exact role unverified

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Covered by Microsoft 365's required *.officeapps.live.com (product): [https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges): "*.officeapps.live.com, *.online.office.com, office.live.com"
- Flags: `unverified_purpose`. Microsoft documents only the wildcard.

### `fe3cr.delivery.mp.microsoft.com`

Note: Microsoft update service - Microsoft lists it for Defender security updates

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft`
- Microsoft lists this Windows Update client URL for Defender updates (function): [https://learn.microsoft.com/en-us/defender-endpoint/configure-network-connections-microsoft-defender-antivirus](https://learn.microsoft.com/en-us/defender-endpoint/configure-network-connections-microsoft-defender-antivirus): "https://fe3cr.delivery.mp.microsoft.com/ClientWebService/client.asmx"

### `sls.update.microsoft.com`

Note: Microsoft Windows Update - Update service

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft`
- Matches Microsoft's documented *.update.microsoft.com (function): [https://learn.microsoft.com/en-us/defender-endpoint/configure-network-connections-microsoft-defender-antivirus](https://learn.microsoft.com/en-us/defender-endpoint/configure-network-connections-microsoft-defender-antivirus): "*.update.microsoft.com *.delivery.mp.microsoft.com *.windowsupdate.com"
- Pi-hole users list it for Windows 10 Update (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `sls.update.microsoft.com` under the heading "Windows 10 Update"

### `forms.office.com`

Note: Microsoft Forms - Surveys and quizzes

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- The site serves Microsoft Forms (function): Title of the page the host serves: `Microsoft Forms`

### `g.live.com`

Note: Microsoft OneDrive host - Pi-hole users also list it for backing up BitLocker keys to a Microsoft account

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- OneDrive endpoint (function): [https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints): "anything that relies on g.live.com to get updated URL information no longer works"
- Required for SharePoint Online and OneDrive (product): [https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges): "36 Default Required No g.live.com, oneclient.sfx.ms"
- Pi-hole users list it for BitLocker key backup (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `g.live.com` under the heading "Backup bitlocker recovery key to Microsoft account"

### `has.spserv.microsoft.com`

Note: Microsoft Device Health Attestation - Intune device health reporting

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft: Device Health Attestation endpoint (function): [https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints): "continue to use the existing Device Health Attestation DHA endpoint 'has.spserv.microsoft.com' for device health attestation reporting"

### `i.s-microsoft.com`

Note: Microsoft-run host (s-microsoft.com) - Microsoft lists *.s-microsoft.com for Windows Autopilot; Pi-hole users list it for Microsoft web pages

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft lists *.s-microsoft.com as a Windows Autopilot dependency (product): [https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints): "windowsphone.com *.s-microsoft.com c.s-microsoft.com"
- Pi-hole users list it for Microsoft web pages (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `i.s-microsoft.com` under the heading "Microsoft Web Pages (Outlook, Office365, Live, Microsoft.com...)"

### `licensing.mp.microsoft.com`

Note: Microsoft licensing - Windows online activation and app licensing

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft: used for activation and app licensing (function): [https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints): "The following endpoint is used for online activation and some app licensing."
- Blocking breaks activation (consequence): [https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints): "This action also blocks online activation and app licensing might not work. TLSv1.2/HTTPS/HTTP licensing.mp.microsoft.com"

### `storeedgefd.dsx.mp.microsoft.com`

Note: Microsoft Store - Loads the Store app's content

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft: needed to load Store content (function): [https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints): "The following endpoints are needed to load the content in the Microsoft Store app. HTTPS livetileedge.dsx.mp.microsoft.com HTTP storeedgefd.dsx.mp.microsoft.com"

### `login.live.com`

Note: Microsoft account sign-in (Outlook.com, OneDrive and Microsoft account)

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft lists it for consumer Outlook.com, OneDrive and Microsoft account (function): [https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints): "Consumer Outlook.com, OneDrive, Device authentication, and Microsoft account Default Required False account.live.com login.live.com"
- The site is the Microsoft account sign-in page (function): Title of the page the host serves: `Sign in to your Microsoft account`

### `login.microsoftonline.com`

Note: Microsoft Entra ID sign-in - Required by Microsoft 365

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft: authentication and identity (function): [https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints): "Authentication and Identity, includes Microsoft Entra ID and Entra ID related services. Allow Required True login.microsoftonline.com"

### `logincdn.msauth.net`

Note: Microsoft sign-in host (msauth.net) - Listed among Microsoft's OneDrive endpoints and required by Microsoft 365

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Listed among Microsoft's OneDrive endpoints (product): [https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints): "TLSv1.2/HTTPS/HTTP oneclient.sfx.ms HTTPS logincdn.msauth.net"
- Microsoft 365 lists *.msauth.net as required for sign-in (product): [https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges): "*.microsoftonline.com, *.msauth.net"

### `onedrive.live.com`

Note: Microsoft OneDrive - Listed among Microsoft's OneDrive endpoints

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Listed among Microsoft's OneDrive endpoints (product): [https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints): "TLSv1.2/HTTPS/HTTP g.live.com HTTP onedrive.live.com"

### `storage.live.com`

Note: Microsoft OneDrive host - Microsoft 365 lists it for OneDrive supportability, telemetry and APIs

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft: OneDrive supportability, telemetry and APIs (function): [https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges): "OneDrive for Business: supportability, telemetry, APIs, and embedded email links No storage.live.com"

### `mamservice.manage.microsoft.com`

Note: Microsoft Intune host under the documented *.manage.microsoft.com - Exact role unverified

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Under Intune's documented *.manage.microsoft.com (product): [https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints): "Note SSL traffic inspection isn't supported for '*.manage.microsoft.com'"
- Flags: `unverified_purpose`. Microsoft documents only the *.manage.microsoft.com wildcard for Intune.

### `r.manage.microsoft.com`

Note: Microsoft Intune host under the documented *.manage.microsoft.com - Redirects to the Intune admin center

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Under Intune's documented *.manage.microsoft.com (product): [https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints): "Note SSL traffic inspection isn't supported for '*.manage.microsoft.com'"
- Its web page redirects to the Intune admin center (observation): Title of the page the host serves: `Microsoft Intune admin center`

### `mrs-efz.ms-acdc.office.com`

Note: Microsoft 365 (office.com) service host - Exact role unverified

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Covered by Microsoft 365's required *.office.com (product): [https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges): "147 Default Required No *.office.com, www.microsoft365.com"
- Flags: `unverified_purpose`. Only the *.office.com wildcard is documented.

### `mscomajax.vo.msecnd.net`

Note: Microsoft-run host (msecnd.net, required by Microsoft 365) - Exact role unverified

- Microsoft 365 lists *.msecnd.net as a required Microsoft domain (owner): [https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges): "*.msauthimages.net, *.msecnd.net"
- Its root redirects to Microsoft's ASP.NET site (observation): Address the host's web page ends at: `https://dotnet.microsoft.com/en-us/apps/aspnet`
- Flags: `unverified_purpose`. Microsoft documents only the *.msecnd.net wildcard; its root redirects to Microsoft's ASP.NET site.

### `officeci-mauservice.azurewebsites.net`

Note: Microsoft AutoUpdate for Mac - Management control endpoint

- Microsoft runs it (Azure web app with Microsoft certificate) (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft: Management Control endpoint for Microsoft AutoUpdate (function): [https://learn.microsoft.com/en-us/microsoft-365/enterprise/network-requests-in-office-2016-for-mac](https://learn.microsoft.com/en-us/microsoft-365/enterprise/network-requests-in-office-2016-for-mac): "https://officeci-mauservice.azurewebsites.net/ ST Management Control endpoint for Microsoft AutoUpdate"

### `presence.teams.live.com`

Note: Microsoft Teams host (teams.live.com)

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- teams.live.com is a Microsoft Teams endpoint (product): [https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions): "TLSv1.2/HTTP teams.events.data.microsoft.com HTTP teams.live.com"

### `products.office.com`

Note: Microsoft 365 product pages (now redirect to microsoft.com)

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Redirects to the Microsoft 365 site (observation): Address the host's web page ends at: `https://www.microsoft.com/en-us/microsoft-365`
- Pi-hole users list it for Microsoft web pages (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `products.office.com` under the heading "Microsoft Web Pages (Outlook, Office365, Live, Microsoft.com...)"

### `res-1.cdn.office.net`

Note: Microsoft 365 CDN host - Microsoft lists *.cdn.office.net for Microsoft 365 app updates

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft lists *.cdn.office.net for Microsoft 365 app updates (product): [https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints](https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints): "M365 app updates *.officecdn.microsoft.com *.cdn.office.net"

### `statics.teams.cdn.office.net`

Note: Microsoft Teams host - Microsoft lists it for the Teams app

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft: endpoint of the Teams application (product): [https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions): "HTTP statics.teams.cdn.live.net HTTP statics.teams.cdn.office.net"

### `settings-win.data.microsoft.com`

Note: Microsoft Windows settings service - Lets apps such as the Xbox app update their configuration

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft`
- Microsoft: dynamic app configuration endpoint (function): [https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints): "The following endpoints are used as a way for apps to dynamically update their configuration. Apps such as System Initiated User Feedback and the Xbox app use it."
- Blocking may stop apps (consequence): [https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints): "If you turn off traffic for this endpoint, an app that uses this endpoint might stop working."

### `sharepoint.com`

Note: Microsoft SharePoint Online and OneDrive for Business

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft 365 required *.sharepoint.com (product): [https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges): "31 Optimize Required Yes *.sharepoint.com"

### `spynet2.microsoft.com`

Note: Microsoft Defender SpyNet host - A 2011 article names spynet2 as a server Defender and Security Essentials contact; both share one CNAME

- Defender and Security Essentials use spynet2 to talk to Microsoft (function): [https://www.ghacks.net/2011/06/02/disabling-microsoft-spynet-in-windows7/](https://www.ghacks.net/2011/06/02/disabling-microsoft-spynet-in-windows7/): "Spynet2.microsoft.com"
- Both names CNAME to the same Defender cloud-protection front end (observation): DNS CNAME chain: `wd-prod-cp-us-east-1-fe.eastus.cloudapp.azure.com.`
- Note on the evidence: Neither host appears in Microsoft's current Defender connection page (fetched 2026-11-13).

### `spynetalt.microsoft.com`

Note: Microsoft Defender SpyNet host - A 2011 article names spynet2 as a server Defender and Security Essentials contact; both share one CNAME

- Defender and Security Essentials use spynet2 to talk to Microsoft (function): [https://www.ghacks.net/2011/06/02/disabling-microsoft-spynet-in-windows7/](https://www.ghacks.net/2011/06/02/disabling-microsoft-spynet-in-windows7/): "Spynet2.microsoft.com"
- Both names CNAME to the same Defender cloud-protection front end (observation): DNS CNAME chain: `wd-prod-cp-us-east-1-fe.eastus.cloudapp.azure.com.`
- Note on the evidence: Neither host appears in Microsoft's current Defender connection page (fetched 2026-11-13).

### `substrate.office.com`

Note: Microsoft 365 host - Microsoft lists it among Office endpoints in Windows

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Listed among Microsoft's Office endpoints in Windows (product): [https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions): "HTTP roaming.officeapps.live.com HTTPS/HTTP substrate.office.com"
- Its web path /mail/ and Outlook CNAME (observation): DNS CNAME chain: `atm.outlook.mira.tm.svc.cloud.microsoft.`

### `teams.office.com`

Note: Microsoft Teams (redirects to teams.microsoft.com)

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Redirects to Teams (observation): Address the host's web page ends at: `https://teams.microsoft.com/v2/`

### `win10.ipv6.microsoft.com`

Note: Microsoft Teredo IPv6 server - Xbox networking on Windows uses Teredo

- Xbox troubleshooting guides treat it as the Teredo server Xbox networking needs (function): [https://www.drivereasy.com/knowledge/teredo-is-unable-to-qualify-xbox-window-10-solved/](https://www.drivereasy.com/knowledge/teredo-is-unable-to-qualify-xbox-window-10-solved/): "Then type win10.ipv6.microsoft.com"
- Microsoft Xbox networking: Xbox on Windows 10 uses Teredo for peer-to-peer traffic (function): [https://diswww.mit.edu/charon/nanog/179964](https://diswww.mit.edu/charon/nanog/179964): "New Xbox experiences launching on Windows 10 will use Teredo for P2P"

### `win1710.ipv6.microsoft.com`

Note: Microsoft IPv6 host - Purpose unverified

- Resolves in DNS from unbound (observation): DNS status: `NOERROR`
- Flags: `unverified_purpose`. No source names win1710.ipv6.microsoft.com; win10 and win1910 variants are documented as Teredo server names in Microsoft Q&amp;A, so this is an inference.

### `windows.msn.com`

Note: Microsoft Edge - Endpoint Microsoft lists for the Edge browser

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft lists it under Microsoft Edge (product): [https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints): "Learn how to turn off traffic to all of the following endpoints for Microsoft Edge. TLSv1.2/HTTP edge.microsoft.com TLSv1.2/HTTP windows.msn.com"

### `xbox.ipv6.microsoft.com`

Note: Microsoft Xbox Live - Listed as required for full Xbox Live functionality

- Pi-hole's Xbox Live list (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `xbox.ipv6.microsoft.com` under the heading "Full Functionality"
- Pi-hole forum: confirmed by Microsoft as required (function): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212): "which were also confirmed by Microsoft as being required by Xbox Live for full functionality"

### `analytics.dev.azure.com`

Note: Microsoft Azure DevOps Analytics OData endpoint - Caught by the analytics regex

- Microsoft runs it (owner): TLS certificate subject: `O = Microsoft Corporation`
- Microsoft: Analytics OData endpoint (function): [https://learn.microsoft.com/en-us/azure/devops/report/analytics/analytics-query-parts](https://learn.microsoft.com/en-us/azure/devops/report/analytics/analytics-query-parts): "https://analytics.dev.azure.com/&lt;OrganizationName&gt;/&lt;ProjectName&gt;/_odata/version/$metadata"
- Matches this repo's analytics block regex (allow_reason): This repo's block regexes that match it (tested with pihole-FTL): `^analytics?[_.-]`

### `aic-ngfts.lge.com`

Note: LG webOS TV - LG Content Store cover art; HaGeZi issue #309 reports cover art breaks when blocked

- LG Electronics runs it (owner): TLS certificate subject: `O = LG Electronics Inc.`
- Reported in HaGeZi #309 (consequence): [https://github.com/hagezi/dns-blocklists/issues/309](https://github.com/hagezi/dns-blocklists/issues/309): "aic-ngfts.lge.com - _Breaks LG Content App Cover Art_"
- Looked up by the maintainer's LG webOS TV (observation): Lookups on the maintainer's network, by device type (LG webOS TV): `10`

### `ngfts.lge.com`

Note: LG webOS TV - LG Content Store thumbnails and cover art

- LG Electronics runs it (owner): TLS certificate subject: `O = LG Electronics Inc.`
- Perflyst: blocking it stops thumbnails in the LG Content Store (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#ngfts.lge.com # blocks thumbnails from loading in the LG Content Store"
- HaGeZi #309 report (consequence): [https://github.com/hagezi/dns-blocklists/issues/309](https://github.com/hagezi/dns-blocklists/issues/309): "ngfts.lge.com - _Breaks LG Content App Cover Art_"

### `us.rdx2.lgtvsdp.com`

Note: LG webOS TV (US) - LG Content Store cover art

- LG Electronics runs it (owner): TLS certificate subject: `O = LG Electronics Inc.`
- HaGeZi #309 report (consequence): [https://github.com/hagezi/dns-blocklists/issues/309](https://github.com/hagezi/dns-blocklists/issues/309): "us.rdx2.lgtvsdp.com - _Breaks LG Content App Cover Art_"

### `us.ibs.lgappstv.com`

Note: LG webOS TV (US) - TV service location setting

- LG Electronics runs it (owner): TLS certificate subject: `O = LG Electronics Inc.`
- HaGeZi #309 report (consequence): [https://github.com/hagezi/dns-blocklists/issues/309](https://github.com/hagezi/dns-blocklists/issues/309): "us.ibs.lgappstv.com - _Needed for Service Location Area (Settings)_"

### `api-tv.spotify.com`

Note: Spotify - API for the Spotify app on TVs and PlayStation 4

- Spotify runs it (owner): TLS certificate subject: `O = Spotify AB`
- Perflyst: required for the TV and PS4 Spotify app (function): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#api-tv.spotify.com # required for TV and PS4 spotify app"

### `applicast.ga.sony.net`

Note: Sony Bravia TV - AppliCast app widget service; Perflyst says apps need it

- The site identifies itself (function): Title of the page the host serves: `AppliCast Widgets Distribution Service`
- Perflyst: needed for applications on Sony Bravia (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) lists `applicast.ga.sony.net` under the heading "needed for applications, if blocked error "no internet connection""

### `portal.store.sonyentertainmentnetwork.com`

Note: Sony (Sony Interactive Entertainment) host - Perflyst says Bravia TV apps need it

- Sony Interactive Entertainment runs it (owner): TLS certificate subject: `O = Sony Interactive Entertainment LLC`
- Perflyst: needed for applications on Sony Bravia (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) lists `portal.store.sonyentertainmentnetwork.com` under the heading "needed for applications, if blocked error "no internet connection""

### `update.biv.sony.tv`

Note: Sony Bravia TV - Software updates

- Perflyst: required for updates (function): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#update.biv.sony.tv # required for updates"

### `auth.samsungosp.com`

Note: Samsung TV - Samsung account sign-in

- Samsung runs it (owner): TLS certificate subject: `Samsung Electronics`
- Perflyst: Samsung accounts fail when blocked (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#auth.samsungosp.com # if blocked, samsung accounts will fail to authenticate"

### `cdn.samsungcloudsolution.com`

Note: Samsung TV - System update check

- Perflyst: system update check (function): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#cdn.samsungcloudsolution.com # System update check on Samsung UE40F5500"
- Looked up by the maintainer's Samsung device (observation): Lookups on the maintainer's network, by device type (Samsung device): `22`

### `configprd.samsungcloudsolution.net`

Note: Samsung TV host - Perflyst keeps it unblocked - Caught by the samsungcloudsolution.net regex

- Samsung runs it (owner): TLS certificate subject: `Samsung Electronics`
- Perflyst keeps it unblocked under Samsung (product): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) lists `configprd.samsungcloudsolution.net` under the heading "Samsung"
- Matches this repo's samsungcloudsolution.net block regex (allow_reason): This repo's block regexes that match it (tested with pihole-FTL): `samsungcloudsolution`

### `lcprd1.samsungcloudsolution.net`

Note: Samsung TV - Network connection test (no tracking per Perflyst) - Caught by the samsungcloudsolution.net regex

- Samsung runs it (owner): TLS certificate subject: `Samsung Electronics`
- Perflyst: ping test, no beaconing (function): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#lcprd1.samsungcloudsolution.net # ping test, no beaconing"
- Matches this repo's samsungcloudsolution.net block regex (allow_reason): This repo's block regexes that match it (tested with pihole-FTL): `samsungcloudsolution`
- Looked up 776 times by the maintainer's Samsung device (observation): Lookups on the maintainer's network, by device type (Samsung device): `776`

### `time.samsungcloudsolution.com`

Note: Samsung TV host - Plex, YouTube and Prime Video fail on some Samsung TVs without it (Perflyst)

- Samsung runs it (owner): TLS certificate subject: `Samsung Electronics`
- Perflyst report (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#time.samsungcloudsolution.com # if blocked, services like Plex, YouTube and Amazon Video not working anymore on some Samsung TV's"

### `gpm.samsungqbe.com`

Note: Samsung TV host - Perflyst reports connection problems when blocked - Caught by the samsungqbe.com regex

- Samsung runs it (owner): TLS certificate subject: `Samsung Electronics`
- Perflyst report (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#gpm.samsungqbe.com # Numerous connection problems, e.g. #82"
- Matches this repo's samsungqbe.com block regex (allow_reason): This repo's block regexes that match it (tested with pihole-FTL): `samsungqbe`

### `osb-ussvc.samsungqbe.com`

Note: Samsung TV host - Required for Samsung TV Plus (Perflyst) - Caught by the samsungqbe.com regex

- Samsung runs it (owner): TLS certificate subject: `Samsung Electronics`
- Perflyst: required for TV Plus (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#osb-ussvc.samsungqbe.com # required for TV Plus"
- Matches this repo's samsungqbe.com block regex (allow_reason): This repo's block regexes that match it (tested with pihole-FTL): `samsungqbe`

### `infolink.pavv.co.kr`

Note: Samsung TV - App store and sign-in - Caught by the pavv.co.kr regex

- Samsung runs it (owner): TLS certificate subject: `Samsung Electronics`
- Perflyst report (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#infolink.pavv.co.kr # Needed for appstore and login on Samsung UE40F5500"
- Matches this repo's pavv.co.kr block regex (allow_reason): This repo's block regexes that match it (tested with pihole-FTL): `pavv`

### `avpro.global.yamaha.com`

Note: Yamaha AV receivers - Firmware updates (blocking it stops updates on the RX-V685)

- Perflyst report (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#avpro.global.yamaha.com # Blocks system updates on RX-V685"

### `deviceportal.nettvservices.com`

Note: Philips TV (TP Vision) host - Perflyst says apps need it

- TP Vision (Philips TV maker) runs it (owner): TLS certificate subject: `O = TP Vision Europe B.V.`
- Perflyst: needed for apps (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#deviceportal.nettvservices.com # needed for apps"

### `epg.corio.com`

Note: Philips TV host - Perflyst says apps need it

- Perflyst: needed for apps (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#epg.corio.com # needed for apps"
- DNS timed out on 2026-11-13 from the local resolver (observation): DNS status: `no-answer`
- Note on the evidence: DNS gave no answer once on 2026-11-13; recheck.

### `www.ecdinterface.philips.com`

Note: Philips-run host - Perflyst ties it to the Philips Hue Bridge

- Philips runs it (owner): TLS certificate subject: `O = Philips International B.V.`
- Perflyst: Philips Hue Bridge (product): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#www.ecdinterface.philips.com # Philips Hue Bridge"

### `images.vizio.com`

Note: Vizio TV host - Perflyst says Vizio smart TV features need it

- Perflyst: required for Vizio smart TV features (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) lists `images.vizio.com` under the heading "Required for Vizio smart tv features"

### `vcs.vdspf.com`

Note: Panasonic Viera TV - Firmware downloads (TV is told of new firmware but cannot install it when blocked)

- Panasonic runs it (owner): TLS certificate subject: `O = Panasonic`
- Perflyst report (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#vcs.vdspf.com // if blocked, notified of new firmware but unable to download/install"

### `itv.ard.de`

Note: ARD (German public TV) - HbbTV red-button media library on smart TVs

- Suedwestrundfunk (an ARD broadcaster) holds its certificate (owner): TLS certificate subject: `dwestrundfunk`
- Perflyst: ARD media library, HbbTV (function): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#itv.ard.de # ARD media lib - HBBTV"

### `location-api.hdhomerun.com`

Note: SiliconDust HDHomeRun TV tuner - Firmware updates

- Perflyst: required for firmware updates (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#location-api.hdhomerun.com # required for firmware update"

### `tuner-api.hdhomerun.com`

Note: SiliconDust HDHomeRun TV tuner - Firmware updates

- Perflyst: required for firmware updates (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#tuner-api.hdhomerun.com # required for firmware update"

### `time-a.timefreq.bldrdoc.gov`

Note: NIST host (CNAME time-a-b.nist.gov) - Perflyst lists it for Sharp smart TVs (Opera OS) and advises not blocking it

- CNAME to NIST's time server (owner): DNS CNAME chain: `time-a-b.nist.gov.`
- Perflyst: used by Sharp Smart TV, not a good idea to block (product): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "# time-a.timefreq.bldrdoc.gov # probably not a good idea to block this one"
- Listed under Sharp Smart TV (product): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) lists `time-a.timefreq.bldrdoc.gov` under the heading "Sharp Smart TV using Opera OS (thanks to sml156)"

### `appboot.netflix.com`

Note: Netflix host - Netflix breaks when it is blocked (Perflyst, anudeep)

- Netflix runs it (owner): TLS certificate subject: `Netflix`
- Perflyst: secure, api-global and appboot break Netflix (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) lists `appboot.netflix.com` under the heading "secure, api-global, and appboot break Netflix"
- anudeep: domains needed for Netflix (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `appboot.netflix.com` under the heading "Netflix - Domains needed for netlix to work correctly"

### `secure.netflix.com`

Note: Netflix host - Netflix breaks when it is blocked (Perflyst)

- Netflix runs it (owner): TLS certificate subject: `Netflix`
- Perflyst: secure, api-global and appboot break Netflix (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) lists `secure.netflix.com` under the heading "secure, api-global, and appboot break Netflix"
- Looked up by the maintainer's Samsung device and LG TV (observation): Lookups on the maintainer's network, by device type (Samsung device): `12`

### `netflix.com`

Note: Netflix - Main site

- Netflix runs it (owner): TLS certificate subject: `Netflix`
- Site title (function): Title of the page the host serves: `Netflix`

### `nrdp.prod.cloud.netflix.com`

Note: Netflix host - Maintainer added it to sign in on Nvidia Shield TV

- Netflix runs it (owner): TLS certificate subject: `Netflix`
- Maintainer's original reason (consequence): commit [6420fa3](https://github.com/slyfox1186/pihole-regex/commit/6420fa3) added the line `nrdp.prod.cloud.netflix.com`
- Looked up by the maintainer's Samsung device and LG TV (observation): Lookups on the maintainer's network, by device type (LG webOS TV): `26`
- Flags: `other`.

### `uiboot.netflix.com`

Note: Netflix host - Maintainer added it to sign in on Nvidia Shield TV

- Netflix runs it (owner): TLS certificate subject: `Netflix`
- Maintainer's original reason (consequence): commit [a913bbc](https://github.com/slyfox1186/pihole-regex/commit/a913bbc) added the line `uiboot.netflix.com -- Required to login to NetFlix on Nvidia Shield`
- Looked up by the maintainer's Samsung device and LG TV (observation): Lookups on the maintainer's network, by device type (Samsung device): `46`
- Flags: `other`.

### `win10.prod.http1.netflix.com`

Note: Netflix host - Maintainer reported it is required for signing in

- Netflix runs it (owner): TLS certificate subject: `Netflix`
- Maintainer's original reason (consequence): commit [34a8b8d](https://github.com/slyfox1186/pihole-regex/commit/34a8b8d) added the line `win10.prod.http1.netflix.com`
- Flags: `other`.

### `api.roku.com`

Note: Roku host - Maintainer added it for Disney+ and other Roku apps

- Roku runs it (owner): TLS certificate subject: `Roku`
- Maintainer's original reason (consequence): commit [52189ee](https://github.com/slyfox1186/pihole-regex/commit/52189ee) added the line `api.roku.com -- Streaming on some Roku apps like Disney Plus`
- Flags: `other`.

### `x-default-stgec.uplynk.com`

Note: Uplynk host - Maintainer added it for Discovery+ playback on Nvidia Shield TV

- Maintainer's original reason (consequence): commit [28ee6d6](https://github.com/slyfox1186/pihole-regex/commit/28ee6d6) added the line `x-default-stgec.uplynk.com`
- Flags: `other`.

### `assets.adobedtm.com`

Note: Adobe-run host - Pi-hole users report Lowe's online checkout fails when it is blocked

- Adobe runs it (owner): TLS certificate subject: `Adobe Inc.`
- Pi-hole forum report (consequence): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212): "Clicking "Start Secure Checkout" from the Shopping Cart on Lowe's website does not load anything."
- Looked up by the maintainer's desktop PC and iPhone (observation): Lookups on the maintainer's network, by device type (Linux desktop PC): `6`
- Block List Project's ads list blocks it (allow_reason): Block List Project lists that contain it: `ads`

### `auth.split.io`

Note: Split.io host - The MyFitnessPal app cannot log in without it

- Pi-hole forum: these fix MyFitnessPal login (consequence): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212): "## MyFitnessPal Mobile App These fixes login issue."
- Listed under MyFitnessPal (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `auth.split.io` under the heading "MyFitnessPal Mobile App"
- Note on the evidence: The old note said Spotify; the source names MyFitnessPal.

### `sdk.split.io`

Note: Split.io host - The MyFitnessPal app cannot log in without it

- Pi-hole forum: these fix MyFitnessPal login (consequence): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212): "## MyFitnessPal Mobile App These fixes login issue."
- Listed under MyFitnessPal (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `sdk.split.io` under the heading "MyFitnessPal Mobile App"
- Note on the evidence: The old note said EA Games; the source names MyFitnessPal.

### `viewer.content.glympse.com`

Note: Glympse host - Papa John's 'Where's my pizza' order tracker needs it

- Pi-hole forum report (consequence): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212): "The papa john's where's my pizza requires: viewer.content.glympse.com"

### `gravatar.com`

Note: Gravatar avatar site - Plex uses it for login pictures

- Pi-hole forum: Plex custom login pictures (function): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212): "pihole allow gravatar.com # custom login pictures"
- Site title (function): Title of the page the host serves: `Avatar`

### `thetvdb.com`

Note: TheTVDB - TV series metadata used by Plex

- Pi-hole forum: Plex TV series metadata (function): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212): "pihole allow thetvdb.com # metadata for tv series"
- Site title (function): Title of the page the host serves: `TheTVDB.com`

### `apt.sonarr.tv`

Note: Sonarr TV download manager host - Pi-hole users list it for Sonarr

- Pi-hole forum lists it under Sonarr (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `apt.sonarr.tv` under the heading "Sonarr"

### `download.sonarr.tv`

Note: Sonarr TV download manager host - Pi-hole users list it for Sonarr

- Pi-hole forum lists it under Sonarr (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `download.sonarr.tv` under the heading "Sonarr"

### `forums.sonarr.tv`

Note: Sonarr TV download manager - Forums

- Pi-hole forum lists it under Sonarr (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `forums.sonarr.tv` under the heading "Sonarr"

### `services.sonarr.tv`

Note: Sonarr TV download manager host - Pi-hole users list it for Sonarr

- Pi-hole forum lists it under Sonarr (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `services.sonarr.tv` under the heading "Sonarr"

### `skyhook.sonarr.tv`

Note: Sonarr TV download manager host - Pi-hole users list it for Sonarr

- Pi-hole forum lists it under Sonarr (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `skyhook.sonarr.tv` under the heading "Sonarr"

### `chat.signal.org`

Note: Signal messenger host - Pi-hole users list it for Signal

- Signal runs it (owner): TLS certificate subject: `Signal Messenger`
- Listed under Signal (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `chat.signal.org` under the heading "Signal"

### `contentproxy.signal.org`

Note: Signal messenger host - Pi-hole users list it for Signal

- Listed under Signal (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `contentproxy.signal.org` under the heading "Signal"

### `storage.signal.org`

Note: Signal messenger host - Pi-hole users list it for Signal

- Signal runs it (owner): TLS certificate subject: `Signal Messenger`
- Listed under Signal (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `storage.signal.org` under the heading "Signal"

### `updates2.signal.org`

Note: Signal messenger host - Pi-hole users list it for Signal

- Signal runs it (owner): TLS certificate subject: `Signal Messenger`
- Listed under Signal (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `updates2.signal.org` under the heading "Signal"

### `check2.tsb.co.uk`

Note: TSB Bank (UK) host - Pi-hole users list it for the TSB Mobile app; it CNAMEs to ThreatMetrix (online-metrix.net)

- TSB runs it (owner): TLS certificate subject: `TSB Bank Plc`
- Listed under TSB Mobile (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `check2.tsb.co.uk` under the heading "TSB Mobile"
- CNAME to ThreatMetrix (online-metrix.net) fraud-prevention service (observation): DNS CNAME chain: `h-tsb.online-metrix.net.`
- Block List Project's tracking list blocks it (allow_reason): Block List Project lists that contain it: `tracking`

### `chevrolet.com`

Note: Chevrolet car maker's website

- General Motors runs it (owner): TLS certificate subject: `General Motors LLC`
- Site title (function): Title of the page the host serves: `Chevrolet`
- Listed on the Pi-hole forum (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `chevrolet.com` under the heading "Chevrolet"

### `directvnow.com`

Note: DirecTV Stream (formerly DirecTV Now) website

- DirecTV runs it (owner): TLS certificate subject: `DIRECTV`
- Pi-hole forum lists it under DirectTV (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `directvnow.com` under the heading "DirectTV"

### `dl.dropboxusercontent.com`

Note: Dropbox file host - Pi-hole users list it for Dropbox

- Dropbox runs it (owner): TLS certificate subject: `Dropbox`
- Listed under Dropbox (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `dl.dropboxusercontent.com` under the heading "Dropbox"

### `dl.dropbox.com`

Note: Dropbox host - Listed in anudeep's allowlist

- Dropbox runs it (owner): TLS certificate subject: `Dropbox`
- anudeep's whitelist lists it (observation): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "dl.dropbox.com"

### `dl.google.com`

Note: Google downloads - Pi-hole users list it for Chrome updates on Ubuntu

- Pi-hole forum: Google Chrome updates on Ubuntu (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `dl.google.com` under the heading "Google Chrome (to update on ubuntu)"
- Looked up by the maintainer's desktop PC (observation): Lookups on the maintainer's network, by device type (Linux desktop PC): `4`

### `android.clients.google.com`

Note: Google host - Pi-hole users list it for the Google Play Store

- Pi-hole forum lists it under Google Play (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `android.clients.google.com` under the heading "Google Play"

### `redirector.gvt1.com`

Note: Google host - Pi-hole users list it for Android TV

- Pi-hole forum lists it under Android TV (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `redirector.gvt1.com` under the heading "Android TV"

### `entitlement.auth.adobe.com`

Note: Adobe host - WatchESPN needs it (Pi-hole forum, anudeep)

- Adobe runs it (owner): TLS certificate subject: `Adobe Inc`
- Pi-hole forum and anudeep list it under WatchESPN (consequence): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `entitlement.auth.adobe.com` under the heading "WatchESPN"

### `fpdownload.adobe.com`

Note: Adobe host - WatchESPN needs it (Pi-hole forum, anudeep)

- Adobe runs it (owner): TLS certificate subject: `Adobe Inc`
- Pi-hole forum and anudeep list it under WatchESPN (consequence): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `fpdownload.adobe.com` under the heading "WatchESPN"

### `gdlp01.c-wss.com`

Note: Canon host - Pi-hole users list it for Canon printers

- Canon runs it (owner): TLS certificate subject: `Canon Inc.`
- Pi-hole forum lists it under Canon printers (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `gdlp01.c-wss.com` under the heading "Cannon Printers"

### `gfwsl.geforce.com`

Note: Nvidia host - Pi-hole users list it for GeForce Experience

- Nvidia runs it (owner): TLS certificate subject: `NVIDIA Corporation`
- Listed under NVIDIA GeForce Experience (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `gfwsl.geforce.com` under the heading "NVIDIA GeForce Experience"

### `imagesak.secureserver.net`

Note: GoDaddy - Webmail button images

- GoDaddy runs it (owner): TLS certificate subject: `GoDaddy Inc.`
- Listed under GoDaddy webmail buttons (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `imagesak.secureserver.net` under the heading "GoDaddy webmail buttons"

### `json.bild.de`

Note: Bild.de (German news, Axel Springer) host - Pi-hole users list it for Bild.de

- Axel Springer runs it (owner): TLS certificate subject: `Axel Springer SE`
- Listed under Bild DE (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `json.bild.de` under the heading "Bild DE"
- Block List Project's ads list blocks it (allow_reason): Block List Project lists that contain it: `ads`

### `mobileandroidapi.punchh.com`

Note: Punchh (PAR) host - Pi-hole users list it for Punchh loyalty apps (Farmer Boys, El Pollo Loco and others)

- Punchh runs it (owner): TLS certificate subject: `PUNCHH INC`
- Listed under Punchh (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `mobileandroidapi.punchh.com` under the heading "Punchh (Farmer Boys, El Pollo Loco, Capriotti's, etc.)"
- Block List Project's ads list blocks it (allow_reason): Block List Project lists that contain it: `ads`

### `nine.plugins.plexapp.com`

Note: Plex host - Pi-hole users list it for Plex

- Pi-hole forum lists it under Plex (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `nine.plugins.plexapp.com` under the heading "Plex Domains"
- Flags: `unverified_purpose`. The source lists it among Plex domains without a role.

### `o1.email.plex.tv`

Note: Plex host - Pi-hole users list it for Plex

- Pi-hole forum lists it under Plex (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `o1.email.plex.tv` under the heading "Plex Domains"
- Flags: `unverified_purpose`. The source lists it among Plex domains without a role.

### `o2.sg0.plex.tv`

Note: Plex host - Pi-hole users list it for Plex

- Pi-hole forum lists it under Plex (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `o2.sg0.plex.tv` under the heading "Plex Domains"
- Flags: `unverified_purpose`. The source lists it among Plex domains without a role.

### `tvthemes.plexapp.com.cdn.cloudflare.net`

Note: Plex host - Pi-hole users list it for Plex

- Pi-hole forum lists it under Plex (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `tvthemes.plexapp.com.cdn.cloudflare.net` under the heading "Plex Domains"
- Flags: `unverified_purpose`. The source lists it among Plex domains without a role.

### `plex.tv`

Note: Plex main site

- Plex runs it (owner): TLS certificate subject: `Plex GmbH`
- Listed under Plex (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `plex.tv` under the heading "Plex Domains"

### `portal.fb.com`

Note: Meta-run host - Pi-hole users list it for Facebook

- Meta runs it (owner): TLS certificate subject: `Meta Platforms`
- Pi-hole forum lists it under Facebook (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `portal.fb.com` under the heading "Facebook, Facebook Messenger"
- Block List Project's facebook list blocks it (allow_reason): Block List Project lists that contain it: `facebook`

### `scontent.fgdl5-1.fna.fbcdn.net`

Note: Facebook (Meta) host - Pi-hole users list it for Facebook

- Meta runs it (owner): TLS certificate subject: `Meta Platforms`
- Listed under Facebook, Facebook Messenger (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `scontent.fgdl5-1.fna.fbcdn.net` under the heading "Facebook, Facebook Messenger"
- Block List Project's facebook list blocks it (allow_reason): Block List Project lists that contain it: `facebook`

### `s.mzstatic.com`

Note: Apple static content host - Apple Music tracks fail without it; Apple lists it for Classroom

- Apple runs it (owner): TLS certificate subject: `Apple Inc.`
- Apple network requirements list it (product): [https://support.apple.com/en-us/101555](https://support.apple.com/en-us/101555): "s.mzstatic.com 443 TCP iPadOS and macOS Classroom and Schoolwork device verification"
- Pi-hole forum: Apple Music tracks fail when blocked (consequence): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212): "Apple Music streaming tracks not playing with (s.mzstatic.com) blocked."

### `styles.redditmedia.com`

Note: Reddit host - Pi-hole users list it for Reddit

- Reddit runs it (owner): TLS certificate subject: `Reddit`
- Listed under Reddit (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `styles.redditmedia.com` under the heading "Reddit"

### `tracking-protection.cdn.mozilla.net`

Note: Mozilla host - Pi-hole users list it for Firefox Tracking Protection

- Listed under Mozilla Firefox Tracking Protection (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `tracking-protection.cdn.mozilla.net` under the heading "Mozilla Firefox Tracking Protection"

### `tracking.dpd.de`

Note: DPD (Germany) - Parcel tracking

- Site title (function): Title of the page the host serves: `Sendungsverfolgung`
- Listed under DPD package tracking (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `tracking.dpd.de` under the heading "Tracking Packages sent with DPD"

### `v.w-x.co`

Note: w-x.co host - Pi-hole users report weather.com videos do not play without it

- Pi-hole forum report (consequence): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `v.w-x.co` under the heading "Videos not playing on weather.com"
- Block List Project's ads list blocks it (allow_reason): Block List Project lists that contain it: `ads`

### `www.appleiphonecell.com`

Note: Apple-related host - Pi-hole users list it with captive.apple.com for iOS

- Pi-hole forum lists it under iOS/Apple (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `www.appleiphonecell.com` under the heading "iOS/Apple"

### `weeklyad.target.com.edgesuite.net`

Note: Target - Weekly ad pages (Akamai host)

- Listed under Target's Weekly Ads (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `weeklyad.target.com.edgesuite.net` under the heading "Target's Weekly Ads"

### `crl.entrust.net`

Note: Entrust certificate revocation host - Maintainer added it for certificate validation

- Maintainer's original line (function): commit [9cbe2dd](https://github.com/slyfox1186/pihole-regex/commit/9cbe2dd) added the line `crl.entrust.net # Security certificate validation.`
- Flags: `other`.

### `i.cdn.turner.com`

Note: Turner CDN host - anudeep lists it for Adult Swim videos on Amazon Fire TV

- anudeep: Adult Swim videos on Amazon Firestick (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `i.cdn.turner.com` under the heading "Adult Swim Videos on Amazon Firestick"
- CNAME to Akamai (observation): DNS CNAME chain: `akamaiedge`

### `pmd.cdn.turner.com`

Note: Turner CDN host - anudeep lists it for Adult Swim videos on Amazon Fire TV

- anudeep: Adult Swim videos on Amazon Firestick (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `pmd.cdn.turner.com` under the heading "Adult Swim Videos on Amazon Firestick"
- Certificate (observation): TLS certificate subject: `Warner Bros. Discovery`

### `z.cdn.turner.com`

Note: Turner CDN host - anudeep lists it for Adult Swim on Fire TV and the Roku TNT app

- anudeep: Adult Swim videos on Amazon Firestick (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `z.cdn.turner.com` under the heading "Adult Swim Videos on Amazon Firestick"
- Certificate (observation): TLS certificate subject: `Warner Bros. Discovery`

### `bit.ly`

Note: Bitly - URL shortener

- anudeep lists it under URL shorteners (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `bit.ly` under the heading "URL shorteners"
- Site title (function): Title of the page the host serves: `Bitly`

### `goo.gl`

Note: Google URL shortener domain - Listed by anudeep as a URL shortener

- anudeep lists it under URL shorteners (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `goo.gl` under the heading "URL shorteners"
- The root now answers 'Invalid Dynamic Link' (observation): Title of the page the host serves: `Invalid Dynamic Link`

### `graph.instagram.com`

Note: Instagram (Meta) host - Listed by anudeep under Facebook

- Meta runs it (owner): TLS certificate subject: `Meta Platforms`
- anudeep lists it under Facebook (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `graph.instagram.com` under the heading "Facebook"
- Block List Project's facebook list blocks it (allow_reason): Block List Project lists that contain it: `facebook`

### `lm.licenses.adobe.com`

Note: Adobe - Software licence verification

- Adobe runs it (owner): TLS certificate subject: `Adobe Inc.`
- anudeep: Adobe licence verification endpoints (function): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `lm.licenses.adobe.com` under the heading "Adobe licence verification endpoints"

### `ota-downloads.nvidia.com`

Note: Nvidia updates host (anudeep)

- Nvidia runs it (owner): TLS certificate subject: `NVIDIA Corporation`
- anudeep: Nvidia updates (function): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `ota-downloads.nvidia.com` under the heading "Nvidia updates"

### `pgl.yoyo.org`

Note: Peter Lowe's ad server list - Blocklist source site

- anudeep lists it under hosts files (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `pgl.yoyo.org` under the heading "Host files"

### `someonewhocares.org`

Note: Dan Pollock's hosts file - Blocklist source site

- anudeep lists it under hosts files (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `someonewhocares.org` under the heading "Host files"

### `sysctl.org`

Note: Cameleon hosts file (sysctl.org) - Blocklist source site

- anudeep lists it under hosts files (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `sysctl.org` under the heading "Host files"

### `winhelp2002.mvps.org`

Note: MVPS hosts file - Blocklist source site

- anudeep lists it under hosts files (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `winhelp2002.mvps.org` under the heading "Host files"

### `v.firebog.net`

Note: Firebog - Curated blocklist collection - Blocklist source site

- anudeep lists it under hosts files (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `v.firebog.net` under the heading "Host files"

### `stats.streamelements.com`

Note: StreamElements chat statistics site - Caught by mmotti's original stats regex

- Site title (function): Title of the page the host serves: `StreamElements Chat Stats`
- mmotti's original regex list blocks it (tested with pihole-FTL) (allow_reason): mmotti's regexes that match it (tested with pihole-FTL): `^stat(s|istics)?[0-9]*[_.-]`

### `adverts.ie`

Note: Adverts.ie website - Caught by mmotti's original advert regex

- Site title (function): Title of the page the host serves: `Adverts`
- mmotti's original regex list blocks it (tested with pihole-FTL) (allow_reason): mmotti's regexes that match it (tested with pihole-FTL): `^advert`
- Block List Project's ads list blocks it (allow_reason): Block List Project lists that contain it: `ads`

### `anti-ad.net`

Note: anti-AD - Chinese ad-filter list project site - Caught by mmotti's original ad regex

- Site title (function): Title of the page the host serves: `anti-AD`
- mmotti's original regex list blocks it (tested with pihole-FTL) (allow_reason): mmotti's regexes that match it (tested with pihole-FTL): `^ad([sxv]?[0-9]*|system)`

### `www.ad.nl`

Note: AD.nl (DPG Media) website - Caught by mmotti's original ad regex

- DPG Media runs it (owner): TLS certificate subject: `DPG Media Group NV`
- mmotti's original regex list blocks it (tested with pihole-FTL) (allow_reason): mmotti's regexes that match it (tested with pihole-FTL): `^ad([sxv]?[0-9]*|system)`

### `beacons-npa.gov.uk`

Note: Bannau Brycheiniog National Park Authority website - HaGeZi Pro blocks it

- Site title (function): Title of the page the host serves: `Bannau Brycheiniog National Park Authority`
- mmotti's original regex list blocks it (tested with pihole-FTL) (allow_reason): mmotti's regexes that match it (tested with pihole-FTL): `^beacons?`
- HaGeZi Pro blocks it (allow_reason): checked 2026-11-21: `pro.txt` contains `||beacons-npa.gov.uk^`

### `mytaxes.ads.taj.gov.jm`

Note: Jamaica government host - Maintainer described it as the Tax Administration Jamaica taxpayer portal - Caught by the ad regex

- Matches this repo's ad block regex (allow_reason): This repo's block regexes that match it (tested with pihole-FTL): `adv[0-9]*`
- Maintainer's original line (function): commit [d93c6dd](https://github.com/slyfox1186/pihole-regex/commit/d93c6dd) added the line `mytaxes.ads.taj.gov.jm -- Tax Administration Jamaica taxpayer portal - Caught by the ad regex`

### `webmail.adv.oabsp.org.br`

Note: OAB Sao Paulo webmail - Caught by the ad regex

- Matches this repo's ad block regex (allow_reason): This repo's block regexes that match it (tested with pihole-FTL): `adv[0-9]*`
- Site title (function): Title of the page the host serves: `Webmail`

### `pixel-by-labcorp.zendesk.com`

Note: Pixel by Labcorp help center (Zendesk) - Caught by mmotti's original pixel regex

- Redirects to Labcorp's support site (observation): Address the host's web page ends at: `support.ondemand.labcorp.com`
- mmotti's original regex list blocks it (tested with pihole-FTL) (allow_reason): mmotti's regexes that match it (tested with pihole-FTL): `^pixels?`

### `stats-api.mlssoccer.com`

Note: Major League Soccer - Match statistics on mlssoccer.com - Caught by the stats regex

- Matches this repo's stats block regex (allow_reason): This repo's block regexes that match it (tested with pihole-FTL): `^stat`
- Maintainer's original line (function): commit [652f298](https://github.com/slyfox1186/pihole-regex/commit/652f298) added the line `stats-api.mlssoccer.com -- MLS match statistics on mlssoccer.com - Caught by the stats regex`

### `stats-widgets.mlsdigital.net`

Note: Major League Soccer - Match statistics on mlssoccer.com - Caught by the stats regex

- Matches this repo's stats block regex (allow_reason): This repo's block regexes that match it (tested with pihole-FTL): `^stat`
- Maintainer's original line (function): commit [652f298](https://github.com/slyfox1186/pihole-regex/commit/652f298) added the line `stats-widgets.mlsdigital.net -- MLS match statistics widgets on mlssoccer.com - Caught by the stats regex`

### `stats-prod.sidearmsports.com`

Note: SIDEARM live stats site - Caught by the stats regex

- Matches this repo's stats block regex (allow_reason): This repo's block regexes that match it (tested with pihole-FTL): `^stat`
- Site title (function): Title of the page the host serves: `SIDEARMLiveStats`

### `stats.foldingathome.org`

Note: Folding@home - Project statistics site - Caught by mmotti's original stats regex

- Site title (function): Title of the page the host serves: `Folding@home Statistics`
- mmotti's original regex list blocks it (tested with pihole-FTL) (allow_reason): mmotti's regexes that match it (tested with pihole-FTL): `^stat`

### `stats.stackexchange.com`

Note: Cross Validated (stats.stackexchange.com) - Caught by mmotti's original stats regex

- Site title (function): Title of the page the host serves: `Cross Validated`
- mmotti's original regex list blocks it (tested with pihole-FTL) (allow_reason): mmotti's regexes that match it (tested with pihole-FTL): `^stat`

### `ddns.net`

Note: ddns.net dynamic DNS domain - HaGeZi's DynDNS list blocks it; only the bare domain is allowed

- Block List Project's malware list blocks it (allow_reason): Block List Project lists that contain it: `malware`
- No HTTPS site; DNS answers (observation): DNS status: `NOERROR`
- Note on the evidence: Decision 2026-11-14: kept. Only the bare domain is allowed; customer hostnames under it stay blockable.
- HaGeZi's DynDNS list blocks it (allow_reason): checked 2026-11-21: `dyndns.txt` contains `||ddns.net^`

### `dyndns.org`

Note: Dyn dynamic DNS domain (Oracle certificate) - HaGeZi's DynDNS list blocks it; only the bare domain is allowed

- Oracle certificate (owner): TLS certificate subject: `Oracle Corporation`
- Block List Project's malware list blocks it (allow_reason): Block List Project lists that contain it: `malware`
- Site (function): Title of the page the host serves: `My Dyn Account`
- Note on the evidence: Decision 2026-11-14: kept. Only the bare domain is allowed; customer hostnames under it stay blockable.
- HaGeZi's DynDNS list blocks it (allow_reason): checked 2026-11-21: `dyndns.txt` contains `||dyndns.org^`

### `fairuse.org`

Note: fairuse.org - HaGeZi's DynDNS list blocks it as a dynamic DNS domain; only the bare domain is allowed

- Block List Project's malware list blocks it (allow_reason): Block List Project lists that contain it: `malware`
- Maintainer's original line (function): commit [f3f9cbb](https://github.com/slyfox1186/pihole-regex/commit/f3f9cbb) added the line `fairuse.org -- Fair use information site - Blocked by the Block List Project malware list`
- HaGeZi's DynDNS list blocks it (allow_reason): checked 2026-11-21: `dyndns.txt` contains `||fairuse.org^`. The earlier 'fair use information site' label had no source and was dropped.

### `g2a.com`

Note: G2A.COM website - No list in this collection blocks it now; Block List Project's fraud list did until 11.13.2026

- Block List Project's fraud list blocks it (allow_reason): Block List Project lists that contain it: `fraud`
- Not blocked by this collection (observation): checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13.

### `www.g2a.com`

Note: G2A.COM website - No list in this collection blocks it now; Block List Project's fraud list did until 11.13.2026

- G2A runs it (owner): TLS certificate subject: `G2A.COM Limited`
- Block List Project's fraud list blocks it (allow_reason): Block List Project lists that contain it: `fraud`
- Not blocked by this collection (observation): checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13.

### `name.com`

Note: Name.com domain registrar - No list in this collection blocks it now; Block List Project's redirect list did until 11.13.2026

- Site title (function): Title of the page the host serves: `Domain Names`
- Block List Project's redirect list blocks it (allow_reason): Block List Project lists that contain it: `redirect`
- Not blocked by this collection (observation): checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13.

### `wallpapers.com`

Note: Wallpapers.com - Free wallpaper site - No list in this collection blocks it now; Block List Project's fraud list did until 11.13.2026

- Site title (function): Title of the page the host serves: `Wallpapers.com`
- Block List Project's fraud list blocks it (allow_reason): Block List Project lists that contain it: `fraud`
- Not blocked by this collection (observation): checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13.

### `www.wallpapers.com`

Note: Wallpapers.com - Free wallpaper site - No list in this collection blocks it now; Block List Project's fraud list did until 11.13.2026

- Site title (function): Title of the page the host serves: `Wallpapers.com`
- Block List Project's fraud list blocks it (allow_reason): Block List Project lists that contain it: `fraud`
- Not blocked by this collection (observation): checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13.

### `www.trustpilot.com`

Note: Trustpilot website - No list in this collection blocks it now; Block List Project's scam and phishing lists did until 11.13.2026

- Block List Project's scam list blocks it (allow_reason): Block List Project lists that contain it: `scam`
- Block List Project's phishing list blocks it (allow_reason): Block List Project lists that contain it: `phishing`
- Not blocked by this collection (observation): checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13.

### `bitcoin.org`

Note: Bitcoin project website - Prigent's cryptojacking list (Firebog) blocks it

- Site title (function): Title of the page the host serves: `Bitcoin`
- Block List Project's crypto list blocks it (allow_reason): Block List Project lists that contain it: `crypto`
- Prigent's cryptojacking list blocks it (allow_reason): checked 2026-11-21: `https://v.firebog.net/hosts/Prigent-Crypto.txt` contains `bitcoin.org`

### `surveymonkey.com`

Note: SurveyMonkey - Online surveys - No list in this collection blocks it now; Block List Project's malware list did until 11.13.2026

- Site title (function): Title of the page the host serves: `SurveyMonkey`
- Block List Project's malware list blocks it (allow_reason): Block List Project lists that contain it: `malware`
- Not blocked by this collection (observation): checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13.

### `secure.surveymonkey.com`

Note: SurveyMonkey host - Listed in anudeep's allowlist

- anudeep's whitelist lists it (observation): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "secure.surveymonkey.com"
- Block List Project's ads list blocks it (allow_reason): Block List Project lists that contain it: `ads`

### `bufferapp.com`

Note: Buffer - Social media management (redirects to buffer.com)

- Site title (function): Title of the page the host serves: `Buffer`
- Block List Project's tracking list blocks it (allow_reason): Block List Project lists that contain it: `tracking`

### `intercom.io`

Note: Intercom website (redirects to intercom.com) - No list in this collection blocks it now; Block List Project's tracking list did until 11.13.2026

- Redirects to Intercom's site (observation): Address the host's web page ends at: `intercom.com`
- Block List Project's tracking list blocks it (allow_reason): Block List Project lists that contain it: `tracking`
- Not blocked by this collection (observation): checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13.

### `insights-collector.gog.com`

Note: GOG-run host - Maintainer reported GOG Galaxy updates need it

- GOG runs it (owner): TLS certificate subject: `GOG`
- Block List Project's tracking list blocks it (allow_reason): Block List Project lists that contain it: `tracking`
- Maintainer's first-hand report when it was added (consequence): commit [b7c12d6](https://github.com/slyfox1186/pihole-regex/commit/b7c12d6) added the line `insights-collector.gog.com -- GOG.com Galaxy updates`
- Flags: `other`. Decision 2026-11-14: kept. The only evidence is the maintainer's own first-hand breakage report; tracking lists block this one host, and allowing it is narrow.

### `t.paydaythegame.com`

Note: PAYDAY 3 host - Maintainer reported the game needs it to load saved profiles

- Maintainer's original line (consequence): commit [6df2dbb](https://github.com/slyfox1186/pihole-regex/commit/6df2dbb) added the line `t.paydaythegame.com`
- Block List Project's tracking list blocks it (allow_reason): Block List Project lists that contain it: `tracking`
- Maintainer's first-hand report when it was added (consequence): commit [997f633](https://github.com/slyfox1186/pihole-regex/commit/997f633) added the line `(0, 't.paydaythegame.com', 1, 'PayDay 3 is a video game and this domain is required to load into your saved profile - SlyEWL')`
- Flags: `other`. Decision 2026-11-14: kept. The only evidence is the maintainer's own first-hand breakage report; tracking lists block this one host, and allowing it is narrow.

### `nvidia.tt.omtrdc.net`

Note: Adobe-run host (omtrdc.net) for nvidia.com - Maintainer reported the Nvidia CUDA Toolkit site needs it

- Adobe runs omtrdc.net (owner): TLS certificate subject: `Adobe Inc.`
- Maintainer's earlier note (product): commit [652f298](https://github.com/slyfox1186/pihole-regex/commit/652f298) added the line `nvidia.tt.omtrdc.net -- Adobe Target for nvidia.com - Allowed for the Nvidia CUDA Toolkit website`
- Maintainer's first-hand report when it was added (consequence): commit [b871acb](https://github.com/slyfox1186/pihole-regex/commit/b871acb) added the line `nvidia.tt.omtrdc.net -- Nvidia CUDA SDK Toolkit Website`
- Flags: `other`. Decision 2026-11-14: kept. The only evidence is the maintainer's own first-hand breakage report; tracking lists block this one host, and allowing it is narrow.

### `7ba3f64df98de730df38846b54ecfbdf7f61f80f.cws.conviva.com`

Note: Conviva host - Maintainer reported Disney+ watch history needs it

- Conviva runs it (owner): TLS certificate subject: `Conviva Inc.`
- Block List Project's basic list blocks it (allow_reason): Block List Project lists that contain it: `basic`
- Maintainer's earlier note (product): commit [0a7a3ac](https://github.com/slyfox1186/pihole-regex/commit/0a7a3ac) added the line `7ba3f64df98de730df38846b54ecfbdf7f61f80f.cws.conviva.com -- Conviva video analytics host - Disney+ saves The Simpsons watch history through it`
- Maintainer's first-hand report when it was added (consequence): commit [52189ee](https://github.com/slyfox1186/pihole-regex/commit/52189ee) added the line `7ba3f64df98de730df38846b54ecfbdf7f61f80f.cws.conviva.com -- Saves your watch history for The Simpons on Disney Plus`
- Flags: `other`. Decision 2026-11-14: kept. The only evidence is the maintainer's own first-hand breakage report; tracking lists block this one host, and allowing it is narrow.

### `privacyportal-de.onetrust.com`

Note: OneTrust privacy portal host - Maintainer added it for Nvidia Shield TV

- Maintainer's original line (consequence): commit [873a89b](https://github.com/slyfox1186/pihole-regex/commit/873a89b) added the line `(0, 'privacyportal-de.onetrust.com', 1, 'Nvidia Shield TV - SlyEWL')`
- Page title (function): Title of the page the host serves: `DS Portal`

### `js.stripe.com`

Note: Stripe host - Maintainer added it for Indiegogo payments

- Stripe runs it (owner): TLS certificate subject: `Stripe`
- Maintainer's original line (consequence): commit [873a89b](https://github.com/slyfox1186/pihole-regex/commit/873a89b) added the line `(0, 'js.stripe.com', 1, 'Indiegogo - SlyEWL')`
- Looked up 51 times by the maintainer's desktop PC (observation): Lookups on the maintainer's network, by device type (Linux desktop PC): `51`
- Flags: `other`.

### `images.ctfassets.net`

Note: ctfassets.net image host - Maintainer added it for AdultTime icons

- Maintainer's original line (consequence): commit [c49ceeb](https://github.com/slyfox1186/pihole-regex/commit/c49ceeb) added the line `(0, 'images.ctfassets.net', 1, 'AdultTime.com - Icons - SlyEWL')`
- Flags: `other`.

### `connect.ubisoft.com`

Note: Ubisoft Connect - Maintainer reported it is needed to buy items in the Ubisoft desktop app

- Redirects to Ubisoft Connect (function): Title of the page the host serves: `Ubisoft Connect`
- Maintainer's original line (consequence): commit [c49ceeb](https://github.com/slyfox1186/pihole-regex/commit/c49ceeb) added the line `(0, 'connect.ubisoft.com', 1, 'Required to buy items from the Ubisoft Desktop App - SlyEWL')`

### `connectivity.pod1.avatar.ext.hp.com`

Note: HP host - Maintainer reported it is required to activate a new printer from the Windows app

- HP runs it (owner): TLS certificate subject: `HP Inc`
- Maintainer's original line (consequence): commit [a913bbc](https://github.com/slyfox1186/pihole-regex/commit/a913bbc) added the line `connectivity.pod1.avatar.ext.hp.com -- HP Printers - Required to activate a new printer using the software app on Windows.`

### `bbuseruploads.s3.amazonaws.com`

Note: Amazon S3 bucket - Maintainer added it to download x264 source code

- Maintainer's original line (consequence): commit [ac2658d](https://github.com/slyfox1186/pihole-regex/commit/ac2658d) added the line `bbuseruploads.s3.amazonaws.com -- Required to build the Linux package x264 from source code.`
- Flags: `other`.

### `d29g4g2dyqv443.cloudfront.net`

Note: CloudFront host - Maintainer added it for the Nvidia CUDA Toolkit website

- Maintainer's original line (consequence): commit [b871acb](https://github.com/slyfox1186/pihole-regex/commit/b871acb) added the line `d29g4g2dyqv443.cloudfront.net -- Nvidia CUDA SDK Toolkit Website`
- Flags: `other`. CloudFront does not show the customer.

### `dirms4qsy6412.cloudfront.net`

Note: CloudFront host - Maintainer added it for the Nvidia CUDA Toolkit website

- Maintainer's original line (consequence): commit [b871acb](https://github.com/slyfox1186/pihole-regex/commit/b871acb) added the line `dirms4qsy6412.cloudfront.net -- Nvidia CUDA SDK Toolkit Website`
- Flags: `other`. CloudFront does not show the customer.

### `dcape-na.amazon.com`

Note: Amazon host - Maintainer added it to sign in to Amazon apps on Windows Subsystem for Android

- Maintainer's original line (consequence): commit [b7c12d6](https://github.com/slyfox1186/pihole-regex/commit/b7c12d6) added the line `dcape-na.amazon.com -- Required to login to Amazon using Windows Android Subsystem for Linux`
- Perflyst lists it under Fire TV 'others (unknown usage)' (product): [https://perflyst.github.io/PiHoleBlocklist/AmazonFireTV.txt](https://perflyst.github.io/PiHoleBlocklist/AmazonFireTV.txt) lists `dcape-na.amazon.com` under the heading "others (unknown usage)"

### `api.themoviedb.org`

Note: The Movie Database (TMDB) API - Maintainer added it for Plex metadata

- Redirects to TMDB developer docs (function): Address the host's web page ends at: `developer.themoviedb.org`
- Maintainer's original line (product): commit [f3f9cbb](https://github.com/slyfox1186/pihole-regex/commit/f3f9cbb) added the line `api.themoviedb.org -- Plex Media Server - The Movie Database metadata`
- Flags: `other`.

### `signin.nexon.com`

Note: Nexon sign-in host - Maintainer added it for The First Descendant

- Nexon runs it (owner): TLS certificate subject: `NEXON Korea Corporation`
- Maintainer's original line (consequence): commit [b871acb](https://github.com/slyfox1186/pihole-regex/commit/b871acb) added the line `signin.nexon.com -- The First Decendant`

### `static-assets-prod.unrealengine.com`

Note: Epic Games (unrealengine.com) host - Maintainer added it to load the Epic Games desktop app

- Maintainer's original line (consequence): commit [52189ee](https://github.com/slyfox1186/pihole-regex/commit/52189ee) added the line `static-assets-prod.unrealengine.com -- Load the Epic Games desktop app`
- Flags: `other`.

### `static-cdn.jtvnw.net`

Note: jtvnw.net host - Maintainer added it to load Twitch icons

- Maintainer's original line (consequence): commit [5c124ab](https://github.com/slyfox1186/pihole-regex/commit/5c124ab) added the line `static-cdn.jtvnw.net -- Required to load icons`
- Flags: `other`.

### `sh.rustup.rs`

Note: Rust - rustup installer script

- Maintainer's original line (consequence): commit [b871acb](https://github.com/slyfox1186/pihole-regex/commit/b871acb) added the line `sh.rustup.rs -- RustUp Linux Install Script`

### `static.rust-lang.org`

Note: Rust host - Maintainer added it for the rustup install script

- Maintainer's original line (consequence): commit [b871acb](https://github.com/slyfox1186/pihole-regex/commit/b871acb) added the line `static.rust-lang.org -- RustUp Linux Install Script`

### `index.crates.io`

Note: crates.io package index

- Site title (function): Title of the page the host serves: `The crates.io package index`

### `www.duplicatephotocleaner.com`

Note: Duplicate Photo Cleaner - Duplicate photo finder app site

- Site title (function): Title of the page the host serves: `Duplicate Photo`

### `www.vbsedit.com`

Note: VbsEdit - VBScript editor

- Site title (function): Title of the page the host serves: `VbsEdit`

### `tcr9i.chat.openai.com`

Note: OpenAI ChatGPT - Service host the maintainer added for the ChatGPT desktop app

- Maintainer's original line (consequence): commit [52189ee](https://github.com/slyfox1186/pihole-regex/commit/52189ee) added the line `tcr9i.chat.openai.com -- Allows you to send queries to the ChatGPT AI using their desktop app`
- CNAME to openai.com (observation): DNS CNAME chain: `openai.com.`

### `api.gitkraken.com`

Note: GitKraken host (gitkraken.com)

- Responds over HTTPS (observation): Address the host's web page ends at: `api.gitkraken.com`
- Flags: `unverified_purpose`. The original line called it 'GitHub - Advanced Git CLI Program'; its role is unverified.

### `api.termius.com`

Note: Termius SSH client host (redirects to termius.com)

- Redirects to Termius (observation): Title of the page the host serves: `Termius`
- Flags: `unverified_purpose`. The old note said it is required to sign in; not verified.

### `maxcdn.bootstrapcdn.com`

Note: BootstrapCDN - A tested Bootstrap file matched Bootstrap's published integrity hash

- Integrity check (function): Library integrity check (full record): 2026-11-13: https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css has sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u, the integrity hash getbootstrap.com publishes for Bootstrap 3.3.7

### `stackpath.bootstrapcdn.com`

Note: BootstrapCDN - Serves Bootstrap files

- Integrity check (function): Library integrity check (full record): 2026-11-13: https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js returned 60,044 bytes of JavaScript whose header reads Bootstrap v4.5.2 (header checked, not hash-compared)

### `netdna.bootstrapcdn.com`

Note: BootstrapCDN - Serves Font Awesome files

- Integrity check (function): Library integrity check (full record): 2026-11-13: https://netdna.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css returned 31,000 bytes of CSS whose header reads Font Awesome 4.7.0 (header checked, not hash-compared)

### `unpkg.com`

Note: unpkg - npm package CDN; a tested jQuery file matched the official copy

- Site title (function): Title of the page the host serves: `UNPKG`
- Integrity check (function): Library integrity check (full record): 2026-11-13: https://unpkg.com/jquery@3.6.0/dist/jquery.min.js compared byte-for-byte with https://code.jquery.com/jquery-3.6.0.min.js: identical (SHA-256 tested ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e, reference ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e)

### `lib.baomitu.com`

Note: baomitu.com public JavaScript library CDN (China) - A tested jQuery file matched the official copy

- Integrity check (function): Library integrity check (full record): 2026-11-13: https://lib.baomitu.com/jquery/3.6.0/jquery.min.js compared byte-for-byte with https://code.jquery.com/jquery-3.6.0.min.js: identical (SHA-256 tested ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e, reference ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e)

### `lib.baomitu.com.qh-cdn.com`

Note: CNAME target of lib.baomitu.com - Kept so CNAME-inspecting blockers do not block that library CDN

- lib.baomitu.com points here (function): DNS CNAME chain of `lib.baomitu.com`: `lib.baomitu.com.qh-cdn.com.`

### `libs.baidu.com`

Note: Baidu public JavaScript library CDN (China) - A tested jQuery file matched the official copy

- Baidu runs it (owner): TLS certificate subject: `Beijing Baidu Netcom`
- Integrity check (function): Library integrity check (full record): 2026-11-13: https://libs.baidu.com/jquery/2.0.0/jquery.min.js compared byte-for-byte with https://code.jquery.com/jquery-2.0.0.min.js after converting CRLF line endings: identical (SHA-256 tested 91e8044a4b1bfce3c131d5579965a9808b42cdb9a350a53928d54cd35d6c1451, reference d482871a5e948cb4884fa0972ea98a81abca057b6bd3f8c995a18c12487e761c)

### `developer.n.shifen.com`

Note: Baidu host - CNAME target of libs.baidu.com

- Baidu certificate (owner): TLS certificate subject: `Beijing Baidu Netcom`
- libs.baidu.com points here (function): DNS CNAME chain of `libs.baidu.com`: `developer.n.shifen.com.`

### `upcdn.b0.upaiyun.com`

Note: Upyun (China) JavaScript library CDN - A tested jQuery file matched the official copy

- Page title is Upyun's JS library service (function): Title of the page the host serves: `JS`
- Integrity check (function): Library integrity check (full record): 2026-11-13: https://upcdn.b0.upaiyun.com/libs/jquery/jquery-2.0.2.min.js compared byte-for-byte with https://code.jquery.com/jquery-2.0.2.min.js: identical (SHA-256 tested 4d9586a075f082a04fd40178499c472012b351db4c1a4d210907a0891f7d8ad9, reference 4d9586a075f082a04fd40178499c472012b351db4c1a4d210907a0891f7d8ad9)

### `vo.aicdn.com`

Note: CNAME target of upcdn.b0.upaiyun.com

- upcdn.b0.upaiyun.com points here (function): DNS CNAME chain of `upcdn.b0.upaiyun.com`: `vo.aicdn.com.`

### `sdn.geekzu.org`

Note: Geekzu public library CDN (China) - A tested jQuery file matched the official copy

- Integrity check (function): Library integrity check (full record): 2026-11-13: https://sdn.geekzu.org/ajax/ajax/libs/jquery/3.6.0/jquery.min.js compared byte-for-byte with https://code.jquery.com/jquery-3.6.0.min.js: identical (SHA-256 tested ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e, reference ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e)

### `sdn.inbond.gslb.geekzu.org`

Note: geekzu.org host - Former CNAME target of sdn.geekzu.org

- Resolves via another Geekzu host (observation): DNS CNAME chain: `outbond.gslb.geekzu.org.`
- sdn.geekzu.org no longer CNAMEs here (observation): DNS status of `sdn.geekzu.org`: `NOERROR`
- Note on the evidence: Decision 2026-11-14: kept. No longer a current CNAME target, but no list in this repo's adlists blocks it, so the allow changes nothing.

### `fonts.loli.net`

Note: loli.net Google Fonts mirror (China) - Served Google Fonts CSS when tested

- Integrity check (function): Library integrity check (full record): 2026-11-13: https://fonts.loli.net/css?family=Roboto returned Google Fonts CSS (@font-face rules for Roboto)

### `fonts.loli.net.cdn.cloudflare.net`

Note: Cloudflare CNAME target of fonts.loli.net (Google Fonts mirror)

- fonts.loli.net points here (function): DNS CNAME chain of `fonts.loli.net`: `fonts.loli.net.cdn.cloudflare.net.`

### `use.fontawesome.com`

Note: Font Awesome - Icon font CDN (served Font Awesome 5.15.4 CSS when tested)

- Integrity check (function): Library integrity check (full record): 2026-11-13: https://use.fontawesome.com/releases/v5.15.4/css/all.css returned CSS whose header reads Font Awesome Free 5.15.4 (header checked, not hash-compared)

### `use.fontawesome.com.cdn.cloudflare.net`

Note: Cloudflare CNAME target of use.fontawesome.com (Font Awesome)

- use.fontawesome.com points here (function): DNS CNAME chain of `use.fontawesome.com`: `use.fontawesome.com.cdn.cloudflare.net.`

### `mathjax.rstudio.com`

Note: MathJax library CDN on rstudio.com - Served MathJax 2.7.9 when tested

- Integrity check (function): Library integrity check (full record): 2026-11-13: https://mathjax.rstudio.com/latest/MathJax.js redirected to /2.7.9/MathJax.js, a file with the MathJax Consortium header: serves MathJax 2.7.9

### `materialdesignicons.b-cdn.net`

Note: Material Design Icons host - Redirects to jsDelivr

- Integrity check (function): Library integrity check (full record): 2026-11-13: https://materialdesignicons.b-cdn.net/ redirects to cdn.jsdelivr.net/mdi/

### `mat1.gtimg.com`

Note: Tencent static file host (China) - No list in this collection blocks it now; Block List Project's malware and abuse lists did until 11.13.2026

- Tencent certificate (Chinese company name) (owner): TLS certificate subject: `E8`
- Block List Project malware list (allow_reason): Block List Project lists that contain it: `malware`
- Note on the evidence: Decision 2026-11-14: kept. Kept from the 2022 'crucial CDN' set; no list currently in this repo's adlists blocks it.
- Not blocked by this collection (observation): checked 2026-11-21 against every adlist in `adlists.txt`; none contains it. Block List Project was dropped on 2026-11-13.

### `mat1.gtimg.com.tegsea.tc.qq.com`

Note: Tencent host - Former CNAME target of mat1.gtimg.com

- Tencent certificate (owner): TLS certificate subject: `Shenzhen Tencent Computer Systems`
- mat1.gtimg.com now resolves through a different chain (observation): DNS CNAME chain of `mat1.gtimg.com`: `ovscdns`
- Note on the evidence: Decision 2026-11-14: kept. No longer a current CNAME target, but no list in this repo's adlists blocks it, so the allow changes nothing.

### `gateway.cname.ustclug.org`

Note: gateway.cname.ustclug.org - Role unverified

- Resolves (observation): DNS status: `NOERROR`
- Flags: `unverified_purpose`. Kept from the 2022 'crucial CDN' set; nothing documents what points here.

### `dualstack.osff.map.fastly.net`

Note: Fastly host (map.fastly.net) - Which site uses it is unverified

- Looked up once by the maintainer's iPhone (observation): Lookups on the maintainer's network, by device type (iPhone): `1`
- Flags: `unverified_purpose`. No current CNAME in the lists points here; kept from the 2022 'crucial CDN' set.

### `jquery.com`

Note: jQuery project website

- Site title (function): Title of the page the host serves: `jQuery`

### `players.brightcove.net`

Note: Brightcove video player host - Listed in anudeep's allowlist

- Fastly CNAME for Brightcove (observation): DNS CNAME chain: `dualstack.brightcove.map.fastly.net.`
- anudeep's whitelist lists it (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "players.brightcove.net"

### `ssl.p.jwpcdn.com`

Note: JW Player host - Listed in anudeep's allowlist

- Fastly CNAME for JW Player (observation): DNS CNAME chain: `jwplayer-dualstack.map.fastly.net.`
- anudeep's whitelist lists it (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "ssl.p.jwpcdn.com"

### `res.cloudinary.com`

Note: Cloudinary host - Listed in anudeep's allowlist

- Cloudinary runs it (owner): TLS certificate subject: `Cloudinary Ltd`
- anudeep's whitelist lists it (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "res.cloudinary.com"

### `imgix.net`

Note: imgix.net - Listed in anudeep's allowlist

- anudeep's whitelist lists it (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "imgix.net"
- Note on the evidence: Only the bare domain; it has no HTTPS site.

### `lastfm-img2.akamaized.net`

Note: Akamai host lastfm-img2 - Listed in anudeep's allowlist

- anudeep's whitelist lists it (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "lastfm-img2.akamaized.net"

### `hls.ted.com`

Note: TED (ted.com) host - Listed in anudeep's allowlist

- anudeep's whitelist lists it (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "hls.ted.com"

### `vidtech.cbsinteractive.com`

Note: CBS Interactive host - Redirects to avia.cbsivideo.com

- Redirects to avia.cbsivideo.com (observation): Address the host's web page ends at: `avia.cbsivideo.com`
- anudeep's whitelist lists it (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "vidtech.cbsinteractive.com"

### `traffic.libsyn.com`

Note: Libsyn (podcast hosting platform) host - Listed in anudeep's allowlist

- Libsyn runs it (owner): TLS certificate subject: `LIBERATED SYNDICATION`
- anudeep's whitelist lists it (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "traffic.libsyn.com"

### `secure.avangate.com`

Note: 2Checkout (Verifone) host - Redirects to 2checkout.com

- Verifone runs it (owner): TLS certificate subject: `Verifone`
- Redirects to 2Checkout (observation): Address the host's web page ends at: `2checkout.com`

### `keystone.mwbsys.com`

Note: Malwarebytes host - Virus definition updates fail when it is blocked (yhosts issue #163)

- yhosts issue #163 (consequence): [https://github.com/vokins/yhosts/issues/163](https://github.com/vokins/yhosts/issues/163): "makes malwarebytes unable to install updated virus definitions"
- anudeep's whitelist lists it (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "keystone.mwbsys.com"

### `keyserver.ubuntu.com`

Note: Ubuntu OpenPGP key server

- Site title (function): Title of the page the host serves: `OpenPGP Keyserver`

### `codeload.github.com`

Note: GitHub host - Used by the maintainer's desktop PC

- Used by the maintainer's desktop PC (observation): Lookups on the maintainer's network, by device type (Linux desktop PC): `4`

### `objects.githubusercontent.com`

Note: GitHub content host

- Resolves (observation): DNS status: `NOERROR`
- Flags: `unverified_purpose`. Exact role unverified.

### `raw.githubusercontent.com`

Note: GitHub raw file host - This repo's scripts download their lists from it

- pi.py downloads the lists from raw.githubusercontent.com (function): [https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/pi.py](https://raw.githubusercontent.com/slyfox1186/pihole-regex/main/scripts/pi.py): "raw.githubusercontent.com/slyfox1186/pihole-regex/main/domains"
- Used by the maintainer's desktop PC (observation): Lookups on the maintainer's network, by device type (Linux desktop PC): `69`

### `mirror.clarkson.edu`

Note: Clarkson University mirror site

- Site title (function): Title of the page the host serves: `mirror.clarkson.edu`

### `mirror.umd.edu`

Note: University of Maryland free software mirror

- Site title (function): Title of the page the host serves: `University of Maryland Free Software Mirror`

### `mirror.msys2.org`

Note: MSYS2 package mirror - Redirects to repo.msys2.org

- Redirects to repo.msys2.org (observation): Address the host's web page ends at: `repo.msys2.org`
- Maintainer's original line (product): commit [f6af928](https://github.com/slyfox1186/pihole-regex/commit/f6af928) added the line `(0, 'mirror.msys2.org', 1, 'MSys2 - Required CDN for sourcing and build packages - SlyEWL')`

### `gs-loc.ls-apple.com.akadns.net`

Note: Apple Location Services (Wi-Fi and cell positioning) - Target of gs-loc.apple.com

- Apple certificate (owner): TLS certificate subject: `Apple Inc.`
- gs-loc.apple.com resolves to it (function): Related DNS lookup (full record): gs-loc.apple.com CNAME gs-loc-new.ls-apple.com.akadns.net CNAME gs-loc.ls-apple.com.akadns.net (unbound, 2026-11-13)
- Research paper on iOS location services (function): [https://arxiv.org/html/2610.21597v1](https://arxiv.org/html/2610.21597v1): "to Apple server gs-loc.apple.com/clls/wloc , which responds with the locations of nearby Wi-Fi networks and cell towers"
- Looked up by the maintainer's iPhone (observation): Lookups on the maintainer's network, by device type (iPhone): `5`

### `icloud.com`

Note: Apple iCloud website

- Apple runs it (owner): TLS certificate subject: `Apple Inc.`
- Site title (function): Title of the page the host serves: `iCloud`
- Apple lists *.icloud.com for iCloud services (product): [https://support.apple.com/en-us/101555](https://support.apple.com/en-us/101555): "*.icloud.com 443 TCP iOS, iPadOS, tvOS, macOS, and visionOS iCloud services"

### `upload.appleschoolcontent.com`

Note: Apple host - Apple lists it for SFTP uploads

- Apple's network requirements (function): [https://support.apple.com/en-us/101555](https://support.apple.com/en-us/101555): "upload.appleschoolcontent.com 22 SSH - SFTP uploads"

### `play.google.com`

Note: Google Play Store

- Redirects into the Play Store (observation): Address the host's web page ends at: `play.google.com/store`
- Used by the maintainer's desktop PC (observation): Lookups on the maintainer's network, by device type (Linux desktop PC): `67`

### `play-lh.googleusercontent.com`

Note: Google host - Maintainer added it for the Google Play Store

- Maintainer's original line (consequence): commit [b7c12d6](https://github.com/slyfox1186/pihole-regex/commit/b7c12d6) added the line `play-lh.googleusercontent.com -- Google play Store`
- Flags: `other`.

### `lh3.googleusercontent.com`

Note: Google user content host - Used heavily by the maintainer's desktop and iPhone

- Used heavily by the maintainer's desktop and iPhone (observation): Lookups on the maintainer's network, by device type (Linux desktop PC): `152`
- Note on the evidence: The old note said Nvidia Shield TV apps break without it; no source found.

### `googlehosted.l.googleusercontent.com`

Note: Google hosting CNAME target (googleusercontent.com) - Role unverified

- Resolves (observation): DNS status: `NOERROR`
- Flags: `unverified_purpose`. No source describes it.

### `graph.oculus.com`

Note: Oculus (Meta) host

- Meta runs it (owner): TLS certificate subject: `Meta Platforms`
- CNAME into Facebook (observation): DNS CNAME chain: `oculus.c10r.facebook.com.`
- Block List Project's Facebook list blocks it (allow_reason): Block List Project lists that contain it: `facebook`

### `edge.gycpi.b.yahoodns.net`

Note: Yahoo-run edge host (yahoodns.net)

- Yahoo runs it (owner): TLS certificate subject: `Yahoo Holdings`
- Flags: `unverified_purpose`. The old note said Yahoo breaks without it; not verified.

### `my.plexapp.com`

Note: Plex host - Redirects to watch.plex.tv

- Redirect (observation): Address the host's web page ends at: `watch.plex.tv`
- Block List Project's ads list blocks it (allow_reason): Block List Project lists that contain it: `ads`

### `ws.audioscrobbler.com`

Note: Last.fm API - Listed in anudeep's allowlist

- Site title (function): Title of the page the host serves: `Last.fm API`
- anudeep's whitelist lists it (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "ws.audioscrobbler.com"

### `client-rapi.recombee.us`

Note: Recombee host - Maintainer labeled it for AdultTime

- Responds 401 without a token (observation): Address the host's web page ends at: `client-rapi.recombee.us`
- Maintainer's earlier note (product): commit [652f298](https://github.com/slyfox1186/pihole-regex/commit/652f298) added the line `client-rapi.recombee.us -- Recombee recommendations API (AdultTime)`
- Flags: `other`. Recombee documents client-rapi.recombee.com; the .us host is not documented.

### `members.adulttime.com`

Note: AdultTime - Member sign-in site

- Redirects to AdultTime login (observation): Address the host's web page ends at: `adulttime.com/en/login`

### `rover.ebay.com`

Note: eBay-run host (rover.ebay.com)

- eBay runs it (owner): TLS certificate subject: `eBay Inc.`
- Flags: `unverified_purpose`. The old note said eBay links pass through it; not verified.

### `best.aliexpress.com`

Note: AliExpress shopping site

- Alibaba certificate (owner): TLS certificate subject: `Alibaba`
- Site title (function): Title of the page the host serves: `AliExpress`

### `login.aliexpress.com`

Note: AliExpress - Sign-in

- Alibaba certificate (owner): TLS certificate subject: `Alibaba`
- Redirects to the login page (observation): Address the host's web page ends at: `login`

### `www.aliexpress.com`

Note: AliExpress shopping site

- Alibaba certificate (owner): TLS certificate subject: `Alibaba`

### `play.kayosports.com.au`

Note: Kayo Sports (Hubbl) host

- Hubbl (Kayo's owner) certificate (owner): TLS certificate subject: `Hubbl Pty Ltd`

### `t.co`

Note: t.co - X (Twitter) domain

- Site title (function): Title of the page the host serves: `t.co`

### `j.mp`

Note: Bitly short link domain

- Bitly page (function): Title of the page the host serves: `Bitly`

### `tinyurl.com`

Note: TinyURL - URL shortener

- Site title (function): Title of the page the host serves: `URL Shortener`

### `linkedin.com`

Note: LinkedIn website

- LinkedIn runs it (owner): TLS certificate subject: `Linkedin Corporation`

### `pinterest.com`

Note: Pinterest

- Pinterest runs it (owner): TLS certificate subject: `Pinterest`
- Site title (function): Title of the page the host serves: `Pinterest`

### `color.adobe.com`

Note: Adobe Color - Color palette tool

- Adobe runs it (owner): TLS certificate subject: `Adobe Inc`
- Site title (function): Title of the page the host serves: `Color Palettes`

### `bugmenot.com`

Note: BugMeNot - Shared logins for sites that force sign-up

- Site title (function): Title of the page the host serves: `BugMeNot`

### `giphy.com`

Note: GIPHY website

- Site title (function): Title of the page the host serves: `GIPHY`

### `wikipedia.org`

Note: Wikipedia

- Site title (function): Title of the page the host serves: `Wikipedia`

### `wordpress.com`

Note: WordPress.com website

- Site title (function): Title of the page the host serves: `WordPress.com`

### `wp.com`

Note: wp.com - Redirects to wordpress.com

- Redirect (observation): Address the host's web page ends at: `wordpress.com`

### `vimeo.com`

Note: Vimeo - Video platform

- Site title (function): Title of the page the host serves: `Vimeo`

### `society6.com`

Note: Society6 - Artist-designed prints and home decor shop

- Site title (function): Title of the page the host serves: `Society6`

### `www.howtogeek.com`

Note: How-To Geek - Technology help site

- Site title (function): Title of the page the host serves: `How-To Geek`

### `www.propublica.org`

Note: ProPublica - Investigative journalism site

- Site title (function): Title of the page the host serves: `ProPublica`

### `www.shellcheck.net`

Note: ShellCheck - Shell script checker

- Site title (function): Title of the page the host serves: `ShellCheck`

### `www.squaretrade.com`

Note: SquareTrade (Allstate) - Product protection plans

- SquareTrade runs it (owner): TLS certificate subject: `SquareTrade`
- Site title (function): Title of the page the host serves: `Allstate Protection Plans`

### `www.solaredge.com`

Note: SolarEdge website

- SolarEdge runs it (owner): TLS certificate subject: `SolarEdge Technologies`

### `dynupdate.no-ip.com`

Note: No-IP host - Listed in anudeep's allowlist

- Root redirects to No-IP (observation): Address the host's web page ends at: `noip.com`
- anudeep's whitelist lists it (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "dynupdate.no-ip.com"

### `medium.com`

Note: Medium website

- Cloudflare challenge page (observation): Title of the page the host serves: `Just a moment`

### `unsplash.com`

Note: Unsplash website

- Bot-check page (observation): Title of the page the host serves: `unsplash`

### `static.opensubtitles.org`

Note: OpenSubtitles host

- Redirects into opensubtitles.org (observation): Address the host's web page ends at: `opensubtitles.org`
- Flags: `unverified_purpose`. Exact role unverified.

### `www.opensubtitles.org`

Note: OpenSubtitles website

- Bot-check page on opensubtitles.org (observation): Address the host's web page ends at: `opensubtitles.org`

### `yastatic.net`

Note: Yandex-run host (redirects to yandex.ru)

- Redirects to Yandex (observation): Address the host's web page ends at: `yandex.ru`
- Flags: `unverified_purpose`. Exact role unverified.

### `imgs.xkcd.com`

Note: xkcd host - Listed in anudeep's allowlist

- anudeep's whitelist lists it (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "imgs.xkcd.com"
- Fastly CNAME (observation): DNS CNAME chain: `dualstack.i.ssl.global.fastly.net.`

### `d.adguard-dns.com`

Note: AdGuard DNS server - HaGeZi's DoH list blocks it; iPhones with an AdGuard DNS profile cannot load Messages photos without it

- HaGeZi's DoH/VPN/Proxy list blocks it (allow_reason): the list contains `||adguard-dns.com^` (checked with `pihole -q` on 2026-11-15)
- Name and address (observation): DNS answer `94.140.14.49`; the TLS certificate is domain-validated (`CN=*.d.adguard-dns.com`), so it does not name the owner
- Maintainer's iPhone (observation): the phone uses an AdGuard DNS profile and asks the network only for this name. From 2026-11-14 20:56, when the DoH list was added, Pi-hole blocked it 1,010 times and photos in Messages stayed on "loading" on home Wi-Fi while they loaded on cellular. Allowing it on 2026-11-15 fixed the photos.

## Exact blocklist (exact-blacklist.sql)

### `aic.api.lgtviot.com`

Note: LG webOS TV host (lgtviot.com) - Proposed for blocking in HaGeZi issue #309; role unverified

- Reported from LG webOS TVs (product): [https://github.com/hagezi/dns-blocklists/issues/309](https://github.com/hagezi/dns-blocklists/issues/309): "LG WebOS domains found on reddit and personally tested"
- Listed in that report (product): [https://github.com/hagezi/dns-blocklists/issues/309](https://github.com/hagezi/dns-blocklists/issues/309): "aic.api.lgtviot.com aic.lgtviot.com ngfts.lge.com"
- Flags: `unverified_purpose`. The old note said 'IoT telemetry'; no source states what the host does.

### `aic.lgtviot.com`

Note: LG webOS TV host (lgtviot.com) - Proposed for blocking in HaGeZi issue #309; role unverified

- Reported from LG webOS TVs (product): [https://github.com/hagezi/dns-blocklists/issues/309](https://github.com/hagezi/dns-blocklists/issues/309): "LG WebOS domains found on reddit and personally tested"
- Listed in that report (product): [https://github.com/hagezi/dns-blocklists/issues/309](https://github.com/hagezi/dns-blocklists/issues/309): "aic.api.lgtviot.com aic.lgtviot.com ngfts.lge.com"
- Flags: `unverified_purpose`. The old note said 'IoT telemetry'; no source states what the host does.

### `aic.sports.lgtviot.com`

Note: LG webOS TV host (lgtviot.com) - Listed in HaGeZi issue #309; role unverified

- HaGeZi #309 notes the name resolves (product): [https://github.com/hagezi/dns-blocklists/issues/309](https://github.com/hagezi/dns-blocklists/issues/309): "aic.sports.lgtviot.com resolves"
- Flags: `unverified_purpose`. Only listed, no function stated.

### `qt2-ngfts.lge.com`

Note: LG host sharing ngfts.lge.com's Akamai name - Proposed for blocking in HaGeZi #309; role unverified

- LG Electronics runs it (owner): TLS certificate subject: `O = LG Electronics Inc.`
- Proposed in that LG webOS report (product): [https://github.com/hagezi/dns-blocklists/issues/309](https://github.com/hagezi/dns-blocklists/issues/309): "canvas.tubitv.com qt2-ngfts.lge.com"
- Same Akamai host as the allowed ngfts.lge.com (observation): DNS CNAME chain: `e6114.e21.akamaiedge.net.`
- Flags: `unverified_purpose`, `review`. It shares ngfts.lge.com's CNAME and 'SDP 2.0' page; blocking may affect LG Content Store images. The old 'file transfer' note had no source.

### `www.ueiwsp.com`

Note: Universal Electronics QuickSet Cloud API - LG TVs use it to detect HDMI devices; reports conflict on whether blocking breaks LG Universal Control

- Technical write-up of LG TV traffic (function): [https://vdaluz.com/blog/lg-tv-telemetry-pihole-adblock-lists](https://vdaluz.com/blog/lg-tv-telemetry-pihole-adblock-lists): "www.ueiwsp.com is the QuickSet Cloud API from Universal Electronics, the company behind LG's device discovery and control feature that recognizes the soundbar or console plugged into an HDMI port"
- Proposed for blocking in the LG webOS report (HaGeZi #309) (product): [https://github.com/hagezi/dns-blocklists/issues/309](https://github.com/hagezi/dns-blocklists/issues/309): "us.lgtvsdp.com www.ueiwsp.com"
- Looked up by the maintainer's Samsung device and LG TV (observation): Lookups on the maintainer's network, by device type (Samsung device): `6`
- A report that blocking it stops QuickSet remote-code lookup (consequence): [https://github.com/lewisdoesstuff/lifesgoodwithoutspying/issues/3](https://github.com/lewisdoesstuff/lifesgoodwithoutspying/issues/3): "That is the UEI QuickSet code lookup, roughly every 5 to 10 minutes."
- A tested report that Universal Control still worked with it blocked (consequence): [https://github.com/furkan-bayrak/lg-tv-blocklist/issues/24](https://github.com/furkan-bayrak/lg-tv-blocklist/issues/24): "Universal Control all work, the last one with `ueiwsp.com` blocked"
- Note on the evidence: Decision 2026-11-14: kept. A HaGeZi #309 reporter blocked it with no breakage after testing; one later user also reported LG Universal Control still worked.

### `lgtvonline.lge.com`

Note: LG webOS TV online service host - Role unverified

- Looked up by the maintainer's LG webOS TV (observation): Lookups on the maintainer's network, by device type (LG webOS TV): `1`
- Flags: `unverified_purpose`. No source describes it.

### `datarouter.ol.epicgames.com`

Note: Epic Games data collection (hardware, operating system and app performance data) - Data Router

- HaGeZi issue #5301 (function): [https://github.com/hagezi/dns-blocklists/issues/5301](https://github.com/hagezi/dns-blocklists/issues/5301): "The domain is used by Epic Games for data collection, including hardware, operating system details, and application performance data."
- Blocked by this repo as Epic telemetry (product): commit [10a4010](https://github.com/slyfox1186/pihole-regex/commit/10a4010) message: "Block Reddit event collectors and Epic Games telemetry"
- Block List Project's tracking list also blocks it (observation): Block List Project lists that contain it: `tracking`

### `metric-public-service-prod.ol.epicgames.com`

Note: Epic Games telemetry - Resolves to the same Data Router service

- CNAME to Epic's datarouter service (function): DNS CNAME chain: `datarouter.cfef.live.use1a.on.epicgames.com.`
- Blocked by this repo as Epic telemetry (product): commit [10a4010](https://github.com/slyfox1186/pihole-regex/commit/10a4010) message: "Epic Games telemetry"
- Block List Project's tracking list also blocks it (observation): Block List Project lists that contain it: `tracking`

### `events-test.redditmedia.com`

Note: Reddit-run host - Maintainer labeled it an event collector; exact role unverified

- Reddit runs it (owner): TLS certificate subject: `Reddit`
- Blocked by this repo as a Reddit event collector (product): commit [10a4010](https://github.com/slyfox1186/pihole-regex/commit/10a4010) message: "Block Reddit event collectors"
- Maintainer's earlier note (product): commit [10a4010](https://github.com/slyfox1186/pihole-regex/commit/10a4010) added the line `events-test.redditmedia.com -- Reddit event collector (same service as events.redditmedia.com)`
- Flags: `other`, `unverified_purpose`.

### `events-test-v2.redditmedia.com`

Note: Reddit-run host - Maintainer labeled it an event collector; exact role unverified

- Reddit runs it (owner): TLS certificate subject: `Reddit`
- Blocked by this repo as a Reddit event collector (product): commit [10a4010](https://github.com/slyfox1186/pihole-regex/commit/10a4010) message: "Block Reddit event collectors"
- Maintainer's earlier note (product): commit [10a4010](https://github.com/slyfox1186/pihole-regex/commit/10a4010) added the line `events-test-v2.redditmedia.com -- Reddit event collector (same service as events.redditmedia.com)`
- Flags: `other`, `unverified_purpose`.

### `usage.truenas.com`

Note: TrueNAS analytics data collection host

- TrueNAS security docs (function): [https://www.truenas.com/docs/solutions/optimizations/security/](https://www.truenas.com/docs/solutions/optimizations/security/): "Analytics data collection to https://usage.truenas.com/submit"

### `banners.hangmyads.com`

Note: HangMyAds ad network (Portugal) - Maintainer labeled this host as serving banner ads

- HangMyAds is an ad network (owner): [https://hangmyads.com/](https://hangmyads.com/): "We are an Ad Network based in Portugal"
- Blocked by this repo (product): commit [2c53c1f](https://github.com/slyfox1186/pihole-regex/commit/2c53c1f) message: "Block the HangMyAds ad network's banner host"
- mmotti's original banner regex also blocks it (observation): mmotti's regexes that match it (tested with pihole-FTL): `banners`
- Maintainer's earlier note (product): commit [2c53c1f](https://github.com/slyfox1186/pihole-regex/commit/2c53c1f) added the line `banners.hangmyads.com -- HangMyAds ad network banners`
- Flags: `other`.

### `codes.iobit.com`

Note: IObit host - Maintainer reported it serves in-app pop-up ads

- Akamai CNAME (observation): DNS CNAME chain: `a117.dscd.akamai.net.`
- Maintainer's earlier note (product): commit [0a7a3ac](https://github.com/slyfox1186/pihole-regex/commit/0a7a3ac) added the line `codes.iobit.com -- IObit desktop app pop-up ads`
- Flags: `other`.

### `giveaway.iobit.com`

Note: IObit host - Maintainer labeled it IObit promotions

- Resolves (observation): DNS status: `NOERROR`
- Maintainer's earlier note (product): commit [f3f9cbb](https://github.com/slyfox1186/pihole-regex/commit/f3f9cbb) added the line `giveaway.iobit.com -- IObit promotions`
- Flags: `other`.

### `survey.iobit.com`

Note: IObit host - Maintainer labeled it IObit surveys

- Resolves (observation): DNS status: `NOERROR`
- Maintainer's earlier note (product): commit [f3f9cbb](https://github.com/slyfox1186/pihole-regex/commit/f3f9cbb) added the line `survey.iobit.com -- IObit surveys`
- Flags: `other`.

### `api.itopvpn.com`

Note: iTop VPN host - Maintainer reported it as telemetry

- Maintainer's original line (product): commit [c377502](https://github.com/slyfox1186/pihole-regex/commit/c377502) added the line `(1, 'api.itopvpn.com', 1, 'iTop VPN Telemetry - SlyEBL')`
- Its root page redirects to google.com (observation): Address the host's web page ends at: `www.google.com`
- Flags: `other`.

### `bench.utorrent.com`

Note: uTorrent host - Maintainer reported it serves ads in the desktop app

- Older ad hostnames under it were in blocklists (observation): commit [d56660b](https://github.com/slyfox1186/pihole-regex/commit/d56660b) added the line `i-1006.b-0.ad.bench.utorrent.com`
- Maintainer's earlier note (product): commit [f3f9cbb](https://github.com/slyfox1186/pihole-regex/commit/f3f9cbb) added the line `bench.utorrent.com -- uTorrent desktop app ads`
- Flags: `other`.

### `prod.ups-ats.us-east-1.aolp-ds-prd.aws.oath.cloud`

Note: oath.cloud host whose CNAME names an online-targeting service

- CNAME to Oath's online targeting service (function): DNS CNAME chain: `dcs-online-targeting-prd.aws.oath.cloud.`

### `mindfieldonline.com`

Note: MindField website - Maintainer reported it on an LG Smart TV

- Site title (function): Title of the page the host serves: `MindField`
- Maintainer's earlier note (product): commit [f3f9cbb](https://github.com/slyfox1186/pihole-regex/commit/f3f9cbb) added the line `mindfieldonline.com -- Online survey panel (seen on LG Smart TV)`
- Flags: `other`. The query log since 2026-11-12 has no lookups.

### `nevoai-iothub-54-prod.azure-devices.net`

Note: Microsoft Azure IoT Hub instance named 'nevoai' - Customer unverified (old note: LG Smart TV)

- Azure certificate (owner): TLS certificate subject: `Microsoft Corporation`
- Flags: `unverified_purpose`. Azure IoT Hub names do not show the customer.

## Regex allowlist (regex-whitelist.sql)

### `(\.|^)1drv\.ms$`

Note: 1drv.ms and its subdomains

- Hosts this rule allows or blocks, checked one by one (1):
  - 1drv.ms: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
- Flags: `unverified_purpose`. No fetched source names 1drv.ms; the old note said OneDrive short links.

### `^(account|accts|catalog|entitlement|eulatracking|lightswitch|priceengine)-public-service-prod[0-9]*\.(ak|ol)\.epicgames\.com$`

Note: Epic Games hosts *-public-service-prod.ak/ol.epicgames.com for account, accts, catalog, entitlement, eulatracking, lightswitch and priceengine

- Matched host on the maintainer's network (observation): Matching lookups on the maintainer's network: `eulatracking-public-service-prod06.ol.epicgames.com`
- Note on the evidence: Open-ended (prod[0-9]*).

### `(\.|^)messenger\.com$`

Note: messenger.com and its subdomains - Pi-hole users list Messenger hosts for Facebook Messenger

- Pi-hole forum Facebook and Messenger section (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212): "## Facebook, Facebook Messenger"
- Hosts this rule allows or blocks, checked one by one (2):
  - Domain allowed
  - messenger.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^(accounts|download|entitlement-public-service-prod\.ak|fg-matchmaking-public-service-live-c\.ol|graphql|launcher-public-service-prod06\.ol)\.epicgames\.com$`

Note: Epic Games hosts accounts, download, entitlement-public-service-prod.ak, fg-matchmaking, graphql and launcher

- Pi-hole forum lists graphql.epicgames.com (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212): "graphql.epicgames.com"
- Hosts this rule allows or blocks, checked one by one (6):
  - accounts.epicgames.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - download.epicgames.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - entitlement-public-service-prod.ak.epicgames.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - fg-matchmaking-public-service-live-c.ol.epicgames.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - graphql.epicgames.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - launcher-public-service-prod06.ol.epicgames.com: DNS NOERROR; not named in the sources fetched; 1 lookups on the maintainer's network

### `^ads-[a-z0-9-]+\.aylanetworks\.com$`

Note: Ayla Networks smart-home IoT cloud - ads-* device hosts - Caught by the ad regex

- Ayla describes its business (owner): [https://www.aylanetworks.com/](https://www.aylanetworks.com/): "Simplifying Smart Home IoT | Ayla Networks"
- Matched host on the maintainer's network (observation): Matching lookups on the maintainer's network: `ads-field.aylanetworks.com`
- Note on the evidence: The 652f298 audit traced these hosts to Shark, Fujitsu FGLair and Bradford White appliances.

### `^(affiliate|app|id|id-cdn)\.twitch\.tv$`

Note: Twitch hosts affiliate, app, id and id-cdn.twitch.tv

- Hosts this rule allows or blocks, checked one by one (4):
  - affiliate.twitch.tv: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - app.twitch.tv: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - id-cdn.twitch.tv: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - id.twitch.tv: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^(aic|eic|kic|ruc)\.service\.lgtvcommon\.com$|^(aic|eic|kic)\.cdpsvc\.lgtvcommon\.com$`

Note: LG TV hosts aic/eic/kic/ruc.service and aic/eic/kic.cdpsvc.lgtvcommon.com - HaGeZi #309: aic hosts carry channel guide data

- HaGeZi #309: guide data breaks without these (consequence): [https://github.com/hagezi/dns-blocklists/issues/309](https://github.com/hagezi/dns-blocklists/issues/309): "aic.cdpsvc.lgtvcommon.com - _Prevents Internet Channel guide data from downloading_"
- HaGeZi #309: OTA guide data (consequence): [https://github.com/hagezi/dns-blocklists/issues/309](https://github.com/hagezi/dns-blocklists/issues/309): "aic.service.lgtvcommon.com - _Prevents local OTA Channel guide data from downloading_"
- Looked up by the maintainer's network (observation): Matching lookups on the maintainer's network: `eic.service.lgtvcommon.com`
- HaGeZi accepted region variants of LG service hosts (function): [https://github.com/hagezi/dns-blocklists/issues/1807](https://github.com/hagezi/dns-blocklists/issues/1807): "I presume any `*.service.lgtvcommon.com` domains are required for the same function, just different regions."
- Hosts this rule allows or blocks, checked one by one (7):
  - aic.cdpsvc.lgtvcommon.com: DNS NOERROR; named in https://github.com/hagezi/dns-blocklists/issues/309, https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
  - aic.service.lgtvcommon.com: DNS NOERROR; named in https://github.com/hagezi/dns-blocklists/issues/309; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
  - eic.cdpsvc.lgtvcommon.com: DNS NOERROR; named in https://github.com/hagezi/dns-blocklists/issues/309; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
  - eic.service.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 1 lookups on the maintainer's network; would be blocked by this repo's deny regex
  - kic.cdpsvc.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
  - kic.service.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
  - ruc.service.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex

### `^((www|drivers|download|account|community)\.)?amd\.com$`

Note: AMD - amd.com and its www, drivers, download, account and community hosts

- Hosts this rule allows or blocks, checked one by one (6):
  - account.amd.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - amd.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - community.amd.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - download.amd.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - drivers.amd.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - www.amd.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^(api\.flightproxy|authsvc|chatsvcagg|config|go\.trouter|presence)\.teams\.microsoft\.com$`

Note: Microsoft Teams hosts (*.teams.microsoft.com, required by Microsoft 365): flightproxy, authsvc, chatsvcagg, config, trouter, presence

- Microsoft lists Teams' config host (product): [https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions): "TLSv1.2/HTTPS/HTTP config.teams.microsoft.com"
- Microsoft 365 required *.teams.microsoft.com (product): [https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges): "*.lync.com, *.teams.cloud.microsoft, *.teams.microsoft.com"
- Hosts this rule allows or blocks, checked one by one (6):
  - api.flightproxy.teams.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - authsvc.teams.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - chatsvcagg.teams.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - config.teams.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions; 0 lookups on the maintainer's network
  - go.trouter.teams.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - presence.teams.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^(appleid|apps|audiocontentdownload|bpapi|business|captive|certs|configuration|crl|cssubmissions|deviceenrollment|diagassets|fba|gc|gdmf|gg|gs|gsa|gsp1|humb|identity|idmsa|ig|iprofiles|itunes|mdmenrollment|mesu|oscdn|osrecovery|ppq|radarsubmissions|school|serverstatus|skl|suconfig|sw(cdn|dist|download|scan)|sylvan|tbsc|valid|www|axm-app|deviceservices-external|gnf-mdn|gnf-mr|lcdn-(locator|registration)|sq-device|time(-ios|-macos)?|xp)\.apple\.com$`

Note: Apple - 54 apple.com hosts, most in Apple's network requirements (software updates, captive portal check, time, enrollment)

- Apple: software update catalogs (function): [https://support.apple.com/en-us/101555](https://support.apple.com/en-us/101555): "mesu.apple.com 443, 80 TCP iOS, iPadOS, tvOS, watchOS, macOS, and visionOS Hosts software update catalogs"
- Apple: captive portal check (function): [https://support.apple.com/en-us/101555](https://support.apple.com/en-us/101555): "captive.apple.com 443, 80 TCP iOS, iPadOS, tvOS, macOS, and visionOS Internet connectivity validation for networks that use captive portals"
- Apple: time servers (function): [https://support.apple.com/en-us/101555](https://support.apple.com/en-us/101555): "time.apple.com 123 UDP iOS, iPadOS, tvOS, macOS, and visionOS Used by devices to set their date and time"
- Hosts this rule allows or blocks, checked one by one (54):
  - appleid.apple.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - apps.apple.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - audiocontentdownload.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - axm-app.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - bpapi.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - business.apple.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - captive.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 2 lookups on the maintainer's network
  - certs.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - configuration.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 28 lookups on the maintainer's network
  - crl.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - cssubmissions.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - deviceenrollment.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - deviceservices-external.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - diagassets.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - fba.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - gc.apple.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - gdmf.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 48 lookups on the maintainer's network
  - gg.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - gnf-mdn.apple.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - gnf-mr.apple.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - gs.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - gsa.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 10 lookups on the maintainer's network
  - gsp1.apple.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 1 lookups on the maintainer's network
  - humb.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 2 lookups on the maintainer's network
  - identity.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - idmsa.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - ig.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - iprofiles.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - itunes.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 2 lookups on the maintainer's network
  - lcdn-locator.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 4 lookups on the maintainer's network
  - lcdn-registration.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - mdmenrollment.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - mesu.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 28 lookups on the maintainer's network
  - oscdn.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - osrecovery.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - ppq.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - radarsubmissions.apple.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - school.apple.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - serverstatus.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - skl.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - sq-device.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - suconfig.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - swcdn.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - swdist.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - swdownload.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - swscan.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - sylvan.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - tbsc.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - time-ios.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - time-macos.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - time.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 11 lookups on the maintainer's network
  - valid.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 2 lookups on the maintainer's network
  - www.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - xp.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 40 lookups on the maintainer's network
- Note on the evidence: gc, apps, business, radarsubmissions and school are not in Apple's network page; each host's sources are listed per branch.

### `(\.|^)apple-(cloudkit|livephotoskit)\.com$`

Note: Apple CloudKit and Live Photos kit domains (apple-cloudkit.com, apple-livephotoskit.com)

- Apple lists api.apple-cloudkit.com (product): [https://support.apple.com/en-us/101555](https://support.apple.com/en-us/101555): "api.apple-cloudkit.com 443 TCP macOS App notarization"
- Hosts this rule allows or blocks, checked one by one (2):
  - apple-cloudkit.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - apple-livephotoskit.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^apps\.bdimg\.(com|jomodns\.com)$`

Note: apps.bdimg.com and apps.bdimg.jomodns.com

- Hosts this rule allows or blocks, checked one by one (2):
  - apps.bdimg.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - apps.bdimg.jomodns.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
- Flags: `unverified_purpose`. No fetched source; the old note said Baidu static file CDN.

### `^(apresolve|dealer|embed|global-dealer-ssl|login5|market|mobile-ap|open|play|spclient\.wg)\.spotify\.com$`

Note: Spotify hosts apresolve, dealer, embed, global-dealer-ssl, login5, market, mobile-ap, open, play and spclient.wg.spotify.com

- Pi-hole forum lists spclient.wg.spotify.com and apresolve under Spotify (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `spclient.wg.spotify.com` under the heading "Spotify"
- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `dealer.spotify.com`
- Hosts this rule allows or blocks, checked one by one (10):
  - apresolve.spotify.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt, https://discourse.pi-hole.net/raw/212; 8 lookups on the maintainer's network
  - dealer.spotify.com: DNS NOERROR; not named in the sources fetched; 12 lookups on the maintainer's network
  - embed.spotify.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - global-dealer-ssl.spotify.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - login5.spotify.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - market.spotify.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - mobile-ap.spotify.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - open.spotify.com: DNS NOERROR; not named in the sources fetched; 6 lookups on the maintainer's network
  - play.spotify.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - spclient.wg.spotify.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt, https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

### `^(cert\.mgt|device\.auth|eds|help\.ui|licensing|notify|title\.(auth|mgt)|www|xflight|xkms|xsts\.auth)\.xboxlive\.com$`

Note: Twelve xboxlive.com hosts - The Pi-hole forum lists them as required for full Xbox Live functionality

- Pi-hole's Xbox Live list (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `xsts.auth.xboxlive.com` under the heading "Full Functionality"
- Confirmed by Microsoft as required, per the forum (function): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212): "which were also confirmed by Microsoft as being required by Xbox Live for full functionality"
- Hosts this rule allows or blocks, checked one by one (12):
  - cert.mgt.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - device.auth.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - eds.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - help.ui.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - licensing.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - notify.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - title.auth.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - title.mgt.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - www.xboxlive.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - xflight.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - xkms.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - xsts.auth.xboxlive.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

### `^(audio4-fa|daily-mix|dailymix-images|download|encore|i|lineup-images|newjams-images|t|upgrade)\.scdn\.co$`

Note: Spotify scdn.co hosts (audio4-fa, daily-mix, dailymix-images, download, encore, i, lineup-images, newjams-images, t, upgrade)

- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `i.scdn.co`
- Hosts this rule allows or blocks, checked one by one (10):
  - audio4-fa.scdn.co: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - daily-mix.scdn.co: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - dailymix-images.scdn.co: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - download.scdn.co: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - encore.scdn.co: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - i.scdn.co: DNS NOERROR; not named in the sources fetched; 10 lookups on the maintainer's network
  - lineup-images.scdn.co: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - newjams-images.scdn.co: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - t.scdn.co: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - upgrade.scdn.co: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^(aws|det-ta-g7g|todo-ta-g7g)\.amazon\.com$|^cognito-identity\.us-east-1\.amazonaws\.com$`

Note: Amazon hosts aws, det-ta-g7g and todo-ta-g7g.amazon.com (anudeep lists the last two for Kindle) and cognito-identity (AWS authentication)

- anudeep lists these under Amazon Kindle (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `todo-ta-g7g.amazon.com` under the heading "Amazon Kindle"
- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `todo-ta-g7g.amazon.com`
- AWS lists cognito-identity under authentication (function): [https://docs.aws.amazon.com/workspaces-web/latest/adminguide/allowed.html](https://docs.aws.amazon.com/workspaces-web/latest/adminguide/allowed.html): "WorkSpaces Secure Browser authentication *.auth. { region} .amazoncognito.com cognito-identity."
- Hosts this rule allows or blocks, checked one by one (4):
  - aws.amazon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - cognito-identity.us-east-1.amazonaws.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - det-ta-g7g.amazon.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - todo-ta-g7g.amazon.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt, https://perflyst.github.io/PiHoleBlocklist/AmazonFireTV.txt; 111 lookups on the maintainer's network

### `^(axm-adm-[a-z0-9-]+|enroll)\.apple\.com$`

Note: Apple hosts axm-adm-*.apple.com and enroll.apple.com

- Apple's network page covers Apple Business device management (function): [https://support.apple.com/en-us/101555](https://support.apple.com/en-us/101555): "Device management services to upload enrollment profiles"
- Note on the evidence: Open-ended (axm-adm-[a-z0-9-]+).

### `^(bam-sdk-configs|config-cd-dmgz)\.bamgrid\.com$`

Note: bamgrid.com hosts bam-sdk-configs and config-cd-dmgz - Used on the maintainer's network

- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `config-cd-dmgz.bamgrid.com`
- Hosts this rule allows or blocks, checked one by one (2):
  - bam-sdk-configs.bamgrid.com: DNS NOERROR; not named in the sources fetched; 1 lookups on the maintainer's network
  - config-cd-dmgz.bamgrid.com: DNS NOERROR; not named in the sources fetched; 14 lookups on the maintainer's network
- Note on the evidence: The old note said Disney+ app configuration; not documented here.

### `^(b-api|instagram\.c10r)\.facebook\.com$`

Note: Facebook hosts b-api.facebook.com and instagram.c10r.facebook.com - Listed in community allowlists

- Pi-hole forum lists b-api under Facebook (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `b-api.facebook.com` under the heading "Facebook, Facebook Messenger"
- Hosts this rule allows or blocks, checked one by one (2):
  - b-api.facebook.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - instagram.c10r.facebook.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network

### `^(benchmarks|commons|empoweringtrust|support\.benchmarks|www)\.ul\.com(\.cdn\.cloudflare\.net)?$`

Note: Five ul.com hosts (benchmarks, support.benchmarks, www and two more) plus their Cloudflare CNAMEs

- Hosts this rule allows or blocks, checked one by one (10):
  - benchmarks.ul.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - benchmarks.ul.com.cdn.cloudflare.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - commons.ul.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - commons.ul.com.cdn.cloudflare.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - empoweringtrust.ul.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - empoweringtrust.ul.com.cdn.cloudflare.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - support.benchmarks.ul.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - support.benchmarks.ul.com.cdn.cloudflare.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - www.ul.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - www.ul.com.cdn.cloudflare.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^(blog|business|careers|contests|dev|email|insights|meta|talent|www\.careers)\.stackoverflow\.com$`

Note: Stack Overflow hosts blog, business, careers, contests, dev, email, insights, meta, talent and www.careers

- Hosts this rule allows or blocks, checked one by one (10):
  - blog.stackoverflow.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - business.stackoverflow.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - careers.stackoverflow.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - contests.stackoverflow.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - dev.stackoverflow.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - email.stackoverflow.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - insights.stackoverflow.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - meta.stackoverflow.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - talent.stackoverflow.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - www.careers.stackoverflow.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^(blog|community(-cdn|-staging)?|d-cloudflare|docs|downloads(-staging)?|et|guide|help|learn|models(-r2)?)\.topazlabs\.com$`

Note: Topaz Labs hosts (blog, community, docs, downloads, guide, help, learn, models and others)

- Hosts this rule allows or blocks, checked one by one (14):
  - blog.topazlabs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - community-cdn.topazlabs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - community-staging.topazlabs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - community.topazlabs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - d-cloudflare.topazlabs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - docs.topazlabs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - downloads-staging.topazlabs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - downloads.topazlabs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - et.topazlabs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - guide.topazlabs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - help.topazlabs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - learn.topazlabs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - models-r2.topazlabs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - models.topazlabs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^(calendar|docs|home|inbox|clients[1-6]?|mail|meet|pay(|ments)|photos|sites|time|wallet|workspace|www)\.google\.com$`

Note: Google hosts calendar, docs, home, inbox, clients, mail, meet, pay, photos, sites, time, wallet, workspace and www.google.com

- Pi-hole forum: Google Maps and other Google services (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `clients4.google.com` under the heading "Google Maps and other Google services"
- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `mail.google.com`
- Hosts this rule allows or blocks, checked one by one (22):
  - calendar.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - clients.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - clients1.google.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt; 1 lookups on the maintainer's network
  - clients2.google.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 12 lookups on the maintainer's network
  - clients3.google.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 24 lookups on the maintainer's network
  - clients4.google.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 14 lookups on the maintainer's network
  - clients5.google.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt; 0 lookups on the maintainer's network
  - clients6.google.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt; 60 lookups on the maintainer's network
  - dns.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - docs.google.com: DNS NOERROR; not named in the sources fetched; 2 lookups on the maintainer's network
  - home.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - inbox.google.com: DNS NOERROR; not named in the sources fetched; 65 lookups on the maintainer's network
  - mail.google.com: DNS NOERROR; not named in the sources fetched; 1245 lookups on the maintainer's network
  - meet.google.com: DNS NOERROR; not named in the sources fetched; 30 lookups on the maintainer's network
  - pay.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - payments.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - photos.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - sites.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - time.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - wallet.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - workspace.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - www.google.com: DNS NOERROR; not named in the sources fetched; 564 lookups on the maintainer's network

### `^(alt[0-9]-)?mtalk\.google\.com$`

Note: Google push notifications (mtalk.google.com and alt0-9-mtalk) - Pi-hole users list mtalk for Android app push

- Pi-hole forum: push notifications (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `mtalk.google.com` under the heading "Push Notification"
- Hosts this rule allows or blocks, checked one by one (11):
  - alt0-mtalk.google.com: DNS NXDOMAIN; not named in the sources fetched; 0 lookups on the maintainer's network
  - alt1-mtalk.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - alt2-mtalk.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - alt3-mtalk.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - alt4-mtalk.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - alt5-mtalk.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - alt6-mtalk.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - alt7-mtalk.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - alt8-mtalk.google.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - alt9-mtalk.google.com: DNS NXDOMAIN; not named in the sources fetched; 0 lookups on the maintainer's network
  - mtalk.google.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 10 lookups on the maintainer's network
- Note on the evidence: alt0-mtalk and alt9-mtalk returned NXDOMAIN on 2026-11-13; allowing them is harmless.

### `^cdn\.(datatables\.net|discordapp\.com|embed\.ly|embedly\.com|materialdesignicons\.com|mathjax\.org|plyr\.io|signal\.org)$`

Note: cdn. hosts of datatables.net, discordapp.com, embed.ly, embedly.com, materialdesignicons.com, mathjax.org, plyr.io and signal.org

- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `cdn.discordapp.com`
- Hosts this rule allows or blocks, checked one by one (8):
  - cdn.datatables.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - cdn.discordapp.com: DNS NOERROR; not named in the sources fetched; 993 lookups on the maintainer's network
  - cdn.embed.ly: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - cdn.embedly.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt; 0 lookups on the maintainer's network
  - cdn.materialdesignicons.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - cdn.mathjax.org: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - cdn.plyr.io: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - cdn.signal.org: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

### `^(cdn\.embed\.ly|cdn\.jsdelivr\.net|cdnjs\.loli\.net)\.cdn\.cloudflare\.net$`

Note: Cloudflare CNAME names of cdn.embed.ly, cdn.jsdelivr.net and cdnjs.loli.net

- Hosts this rule allows or blocks, checked one by one (3):
  - cdn.embed.ly.cdn.cloudflare.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - cdn.jsdelivr.net.cdn.cloudflare.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - cdnjs.loli.net.cdn.cloudflare.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^cdnjs\.(cloudflare\.com|loli\.net)$`

Note: cdnjs.cloudflare.com and its China mirror cdnjs.loli.net - A tested jQuery file from the mirror matched the official copy

- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `cdnjs.cloudflare.com`
- Integrity check of the loli.net mirror (function): Library integrity check (full record): 2026-11-13: https://cdnjs.loli.net/ajax/libs/jquery/3.6.0/jquery.min.js compared byte-for-byte with https://code.jquery.com/jquery-3.6.0.min.js: identical (SHA-256 tested ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e, reference ff1523fb7389539c84c65aba19260648793bb4f5e29329d2ee8804bc37a3fe6e)
- Hosts this rule allows or blocks, checked one by one (2):
  - cdnjs.cloudflare.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://learn.microsoft.com/en-us/microsoft-365/enterprise/network-requests-in-office-2016-for-mac; 8 lookups on the maintainer's network
  - cdnjs.loli.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^(cdn-mobile\.api|images|players|silo|siloh|stitcher)\.pluto\.tv$`

Note: Pluto TV hosts cdn-mobile.api, images, players, silo, siloh and stitcher.pluto.tv

- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `players.pluto.tv`
- Hosts this rule allows or blocks, checked one by one (6):
  - cdn-mobile.api.pluto.tv: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - images.pluto.tv: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - players.pluto.tv: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 1 lookups on the maintainer's network
  - silo.pluto.tv: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - siloh.pluto.tv: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - stitcher.pluto.tv: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network

### `^(winatp-gw-neu|windows)\.microsoft\.com$`

Note: Microsoft hosts winatp-gw-neu and windows.microsoft.com

- Hosts this rule allows or blocks, checked one by one (2):
  - winatp-gw-neu.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - windows.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
- Flags: `unverified_purpose`. Neither is in the cached Microsoft pages; the old note said Defender for Endpoint (Europe).

### `^(client\.wns|edge\.activity)\.windows\.com$`

Note: Windows hosts client.wns and edge.activity.windows.com (Microsoft lists edge.activity)

- Microsoft lists edge.activity.windows.com (product): [https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions](https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions): "edge.activity.windows.com"
- Hosts this rule allows or blocks, checked one by one (2):
  - client.wns.windows.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - edge.activity.windows.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions; 0 lookups on the maintainer's network

### `^(cloudsync-prod|reddit-uploaded-media|seedbox-react-infra|ubisoft-uplay-savegames|whispersystems-textsecure-attachments)\.s3(-accelerate)?\.amazonaws\.com$`

Note: Five Amazon S3 buckets incl. cloudsync-prod (Origin save sync) and whispersystems-textsecure-attachments (listed under Signal)

- Pi-hole forum: Signal attachments bucket (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `whispersystems-textsecure-attachments.s3-accelerate.amazonaws.com` under the heading "Signal"
- Pi-hole forum: Origin save sync (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `cloudsync-prod.s3.amazonaws.com` under the heading "Origin (Savegame-Sync)"
- Hosts this rule allows or blocks, checked one by one (10):
  - cloudsync-prod.s3-accelerate.amazonaws.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - cloudsync-prod.s3.amazonaws.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - reddit-uploaded-media.s3-accelerate.amazonaws.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - reddit-uploaded-media.s3.amazonaws.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - seedbox-react-infra.s3-accelerate.amazonaws.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - seedbox-react-infra.s3.amazonaws.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - ubisoft-uplay-savegames.s3-accelerate.amazonaws.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - ubisoft-uplay-savegames.s3.amazonaws.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - whispersystems-textsecure-attachments.s3-accelerate.amazonaws.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - whispersystems-textsecure-attachments.s3.amazonaws.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^code\.(bildstatic\.de|createjs\.com|jquery\.com)$`

Note: code.bildstatic.de, code.createjs.com and code.jquery.com

- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `code.jquery.com`
- Hosts this rule allows or blocks, checked one by one (3):
  - code.bildstatic.de: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - code.createjs.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - code.jquery.com: DNS NOERROR; not named in the sources fetched; 5 lookups on the maintainer's network

### `^((www|m|web|static|graph|b-graph|mqtt-mini|edge-mqtt|upload|connect)\.)?facebook\.com$|^connect\.facebook\.net$`

Note: Facebook - facebook.com, its www, m, web, static, graph, b-graph, mqtt, upload and connect hosts, and connect.facebook.net

- Pi-hole forum: Facebook and Messenger (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `www.facebook.com` under the heading "Facebook, Facebook Messenger"
- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `www.facebook.com`
- Hosts this rule allows or blocks, checked one by one (12):
  - b-graph.facebook.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - connect.facebook.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - connect.facebook.net: DNS NOERROR; not named in the sources fetched; 6 lookups on the maintainer's network
  - edge-mqtt.facebook.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt, https://discourse.pi-hole.net/raw/212; 9 lookups on the maintainer's network
  - facebook.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - graph.facebook.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt, https://discourse.pi-hole.net/raw/212; 24 lookups on the maintainer's network
  - m.facebook.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - mqtt-mini.facebook.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - static.facebook.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - upload.facebook.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - web.facebook.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 16 lookups on the maintainer's network
  - www.facebook.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 22 lookups on the maintainer's network
- Note on the evidence: Decision 2026-11-14: kept. Facebook Login on other sites loads from connect.facebook.net; the old note says the Facebook Pixel tracker also loads from it.

### `^connectivitycheck\.(android|gstatic)\.com$`

Note: Android internet connectivity check

- Pi-hole forum: Android/Chrome (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `connectivitycheck.gstatic.com` under the heading "Android/Chrome"
- Hosts this rule allows or blocks, checked one by one (2):
  - connectivitycheck.android.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - connectivitycheck.gstatic.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 2 lookups on the maintainer's network

### `^crl[3-4]\.digicert\.com$`

Note: DigiCert certificate revocation lists (CRL) - Apple lists them for certificate validation

- Apple: certificate validation (function): [https://support.apple.com/en-us/101555](https://support.apple.com/en-us/101555): "crl3.digicert.com 80 TCP iOS, iPadOS, tvOS, macOS, and visionOS Certificate validation"
- Hosts this rule allows or blocks, checked one by one (2):
  - crl3.digicert.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - crl4.digicert.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

### `^(csp|devicelistenerprod)\.microsoft\.com$`

Note: Microsoft hosts csp and devicelistenerprod.microsoft.com - Purpose unverified

- Hosts this rule allows or blocks, checked one by one (2):
  - csp.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - devicelistenerprod.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
- Flags: `unverified_purpose`. Neither host is in the cached Microsoft endpoint pages.

### `^d(27xxe7juh1us6|2gatte9o95jao|3a3ewgd1iewwz|3ag4hukkh62yn|83eunklitikj)\.cloudfront\.net$`

Note: Five CloudFront hosts - The Pi-hole forum lists one for Signal; the rest are unverified

- Pi-hole forum lists d83eunklitikj under Signal (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `d83eunklitikj.cloudfront.net` under the heading "Signal"
- Hosts this rule allows or blocks, checked one by one (5):
  - d27xxe7juh1us6.cloudfront.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - d2gatte9o95jao.cloudfront.net: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt; 0 lookups on the maintainer's network
  - d3a3ewgd1iewwz.cloudfront.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - d3ag4hukkh62yn.cloudfront.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - d83eunklitikj.cloudfront.net: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
- Flags: `unverified_purpose`. CloudFront certificates do not show customers; only d83eunklitikj (Signal) and d2gatte9o95jao (anudeep whitelist) are sourced.

### `^(app|meta|pubsub|status|tvdb2|www)\.plex\.tv$|^pubsub\.plex\.bz$`

Note: Plex hosts app, meta, pubsub, status, tvdb2 and www.plex.tv, and pubsub.plex.bz

- Pi-hole forum: Plex domains (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `pubsub.plex.tv` under the heading "Plex Domains"
- Hosts this rule allows or blocks, checked one by one (7):
  - app.plex.tv: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - meta.plex.tv: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - pubsub.plex.bz: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - pubsub.plex.tv: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - status.plex.tv: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - tvdb2.plex.tv: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - www.plex.tv: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

### `(\.|^)dataplicity\.com$`

Note: Dataplicity - Remote access to Raspberry Pi and other devices (dataplicity.com and subdomains)

- Dataplicity's site (function): [https://www.dataplicity.com/](https://www.dataplicity.com/): "Diagnose and resolve field-device problems remotely."
- Hosts this rule allows or blocks, checked one by one (1):
  - dataplicity.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt; 0 lookups on the maintainer's network

### `^(devimages|xp|playgrounds?(-assets)?)-cdn\.apple\.com$`

Note: Apple hosts devimages-cdn (Xcode components), xp-cdn (content caching reporting) and Swift Playground hosts (playground- and playgrounds- spellings)

- Apple: Xcode downloadable components (function): [https://support.apple.com/en-us/101555](https://support.apple.com/en-us/101555): "devimages-cdn.apple.com 80, 443 TCP macOS Xcode downloadable components"
- Apple: xp-cdn is content caching reporting (function): [https://support.apple.com/en-us/101555](https://support.apple.com/en-us/101555): "xp-cdn.apple.com 443 TCP macOS Reporting"
- Apple's documented Swift Playground hosts are singular (function): [https://support.apple.com/en-us/101555](https://support.apple.com/en-us/101555): "playground-assets-cdn.apple.com 443 TCP iPadOS and macOS Swift Playground"
- Hosts this rule allows or blocks, checked one by one (6):
  - devimages-cdn.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - playground-assets-cdn.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - playground-cdn.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - playgrounds-assets-cdn.apple.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - playgrounds-cdn.apple.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - xp-cdn.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
- Note on the evidence: Decision 2026-11-14: rule corrected to allow Apple's documented playground-cdn and playground-assets-cdn.

### `^(oops|www)\.redditmedia\.com$|^www\.redditstatic\.com$|^reddit\.map\.fastly\.net$`

Note: Reddit hosts oops and www.redditmedia.com, www.redditstatic.com and reddit.map.fastly.net

- Pi-hole forum: Reddit (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `www.redditstatic.com` under the heading "Reddit"
- Hosts this rule allows or blocks, checked one by one (4):
  - oops.redditmedia.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - reddit.map.fastly.net: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - www.redditmedia.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - www.redditstatic.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 9 lookups on the maintainer's network

### `^(disney\.(api|connections|content|images|playback)\.edge|playback-certs)\.bamgrid\.com$`

Note: bamgrid.com hosts disney.api, connections, content, images and playback edge, and playback-certs - Used heavily on the maintainer's network

- Used heavily on the maintainer's network (observation): Matching lookups on the maintainer's network: `disney.api.edge.bamgrid.com`
- Hosts this rule allows or blocks, checked one by one (6):
  - disney.api.edge.bamgrid.com: DNS NOERROR; not named in the sources fetched; 273 lookups on the maintainer's network
  - disney.connections.edge.bamgrid.com: DNS NOERROR; not named in the sources fetched; 37 lookups on the maintainer's network
  - disney.content.edge.bamgrid.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - disney.images.edge.bamgrid.com: DNS NOERROR; not named in the sources fetched; 31 lookups on the maintainer's network
  - disney.playback.edge.bamgrid.com: DNS NOERROR; not named in the sources fetched; 34 lookups on the maintainer's network
  - playback-certs.bamgrid.com: DNS NOERROR; not named in the sources fetched; 20 lookups on the maintainer's network

### `^[a-z0-9]{10}(-dsn)?\.algolia\.net$|^[a-z0-9]{10}-[1-3]\.algolianet\.com$`

Note: Algolia hostnames: 10 alphanumeric characters with .algolia.net or -dsn.algolia.net, or -1 to -3.algolianet.com

- Example app host resolves and matches (pihole-FTL) (scope): Example hosts tested with DNS and pihole-FTL (full record): {"latency-dsn.algolia.net": {"dns": "NOERROR", "cname": ["dsn.latency.api.algolia.net.", "s10-use-1.algolia.net."], "ftl_match": false}, "bh4d9od16a-dsn.algolia.net": {"dns": "NOERROR", "cname": ["dsn.bh4d9od16a.api.algolia.net.", "s8-usc-1.algolia.net."], "ftl_match": true}, "bh4d9od16a-1.algolianet.com": {"dns": "NOERROR", "cname": ["c6-eu-1.algolianet.com."], "ftl_match": true}}
- Note on the evidence: Open-ended. The maintainer's earlier note tied it to AdultTime search.

### `^(download\.developer|ns\.itunes|static\.ips|vpp\.itunes)\.apple\.com$`

Note: Apple hosts download.developer (Xcode components), ns.itunes, static.ips and vpp.itunes.apple.com

- Apple: Xcode components (function): [https://support.apple.com/en-us/101555](https://support.apple.com/en-us/101555): "download.developer.apple.com 80, 443 TCP macOS Xcode downloadable components"
- Hosts this rule allows or blocks, checked one by one (4):
  - download.developer.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - ns.itunes.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - static.ips.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - vpp.itunes.apple.com: DNS NOERROR; named in https://support.apple.com/en-us/101555, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

### `^[0-6]-edge-chat\.facebook\.com$`

Note: Facebook hosts 0- to 6-edge-chat.facebook.com - Listed in anudeep's optional allowlist

- anudeep lists them under Facebook (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt) lists `0-edge-chat.facebook.com` under the heading "Facebook"
- Hosts this rule allows or blocks, checked one by one (7):
  - 0-edge-chat.facebook.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - 1-edge-chat.facebook.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - 2-edge-chat.facebook.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - 3-edge-chat.facebook.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - 4-edge-chat.facebook.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - 5-edge-chat.facebook.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network
  - 6-edge-chat.facebook.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt; 0 lookups on the maintainer's network

### `^(edge|fs|msedge\.api\.cdp|officecdnmac|officeclient|support|teams|vlscppe|whiteboard|www)\.microsoft\.com$`

Note: Microsoft hosts edge, fs, msedge.api.cdp, officecdnmac, officeclient, support, teams, vlscppe, whiteboard and www.microsoft.com

- Microsoft Edge endpoint (function): [https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints): "TLSv1.2/HTTP edge.microsoft.com"
- Hosts this rule allows or blocks, checked one by one (10):
  - edge.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints, https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions; 0 lookups on the maintainer's network
  - fs.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions; 0 lookups on the maintainer's network
  - msedge.api.cdp.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - officecdnmac.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - officeclient.microsoft.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, https://learn.microsoft.com/en-us/microsoft-365/enterprise/network-requests-in-office-2016-for-mac, https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - support.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/archive/blogs/clientsecurity/microsoft-spynet, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7; 0 lookups on the maintainer's network
  - teams.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges; 0 lookups on the maintainer's network
  - vlscppe.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - whiteboard.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - www.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services, https://learn.microsoft.com/en-us/defender-endpoint/configure-network-connections-microsoft-defender-antivirus, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions; 1 lookups on the maintainer's network

### `^europe\.(cp\.wd|smartscreen(-prod|))\.microsoft\.com$`

Note: Microsoft hosts europe.cp.wd, europe.smartscreen and europe.smartscreen-prod.microsoft.com

- Microsoft documents SmartScreen hosts (function): [https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints](https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints): "If you turn off traffic for these endpoints, SmartScreen notifications won't appear."
- Hosts this rule allows or blocks, checked one by one (3):
  - europe.cp.wd.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - europe.smartscreen-prod.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - europe.smartscreen.microsoft.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
- Flags: `unverified_purpose`. Microsoft documents SmartScreen hosts, but these Europe names are not in the cached pages.

### `(\.|^)gammacdn\.com$`

Note: gammacdn.com and its subdomains - Maintainer labeled it Gamma Entertainment (AdultTime) media

- Maintainer's earlier note (product): commit [0a7a3ac](https://github.com/slyfox1186/pihole-regex/commit/0a7a3ac) added the line `(\.|^)gammacdn\.com$ -- Gamma Entertainment (AdultTime) media CDN`
- Hosts this rule allows or blocks, checked one by one (1):
  - gammacdn.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
- Flags: `other`.

### `^(github\.com|github\.io|github\.githubassets\.com)$`

Note: GitHub - github.com, github.io and github.githubassets.com

- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `github.com`
- Hosts this rule allows or blocks, checked one by one (3):
  - github.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt, https://raw.githubusercontent.com/anudeepND/whitelist/master/README.md, https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://github.com/hagezi/dns-blocklists/issues/1216, https://github.com/hagezi/dns-blocklists/issues/995, https://github.com/hagezi/dns-blocklists/issues/309, https://github.com/hagezi/dns-blocklists/issues/309, https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt, https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV-AGH.txt, https://discourse.pi-hole.net/raw/212; 1506 lookups on the maintainer's network
  - github.githubassets.com: DNS NOERROR; not named in the sources fetched; 60 lookups on the maintainer's network
  - github.io: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt; 0 lookups on the maintainer's network

### `^gsp-ssl\.ls\.apple\.com$|^gsp-ssl\.ls-apple\.com\.akadns\.net$`

Note: Apple gsp-ssl.ls.apple.com and its Akamai name - Pi-hole users list it for the iOS Weather app

- Pi-hole forum: iOS Weather app (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `gsp-ssl.ls.apple.com` under the heading "iOS Weather app"
- Hosts this rule allows or blocks, checked one by one (2):
  - gsp-ssl.ls-apple.com.akadns.net: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - gsp-ssl.ls.apple.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 50 lookups on the maintainer's network

### `^hbbtv\.(prosieben|redbutton|zdf|ard)\.de$`

Note: HbbTV hosts of ProSieben, redbutton.de, ZDF and ARD (Perflyst lists three of them)

- Perflyst lists them (product): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) lists `hbbtv.zdf.de` under the heading "HBBTV"
- Hosts this rule allows or blocks, checked one by one (4):
  - hbbtv.ard.de: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - hbbtv.prosieben.de: DNS NOERROR; named in https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt, https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV-AGH.txt; 0 lookups on the maintainer's network
  - hbbtv.redbutton.de: DNS NOERROR; named in https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt, https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV-AGH.txt; 0 lookups on the maintainer's network
  - hbbtv.zdf.de: DNS NOERROR; named in https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt, https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV-AGH.txt; 0 lookups on the maintainer's network
- Note on the evidence: hbbtv.ard.de is not in Perflyst's list.

### `(^|\.)itunes(-apple)?\.com(\.akadns\.net)?$`

Note: itunes.com, itunes-apple.com and their Akamai names (Apple)

- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `bag-cdn.itunes-apple.com.akadns.net`
- Hosts this rule allows or blocks, checked one by one (4):
  - itunes-apple.com: DNS NXDOMAIN; not named in the sources fetched; 0 lookups on the maintainer's network
  - itunes-apple.com.akadns.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - itunes.com: DNS NOERROR; named in https://support.apple.com/en-us/101555; 0 lookups on the maintainer's network
  - itunes.com.akadns.net: DNS NXDOMAIN; not named in the sources fetched; 0 lookups on the maintainer's network

### `(\.|^)lencr\.org$`

Note: Let's Encrypt (lencr.org) - Data referenced inside its certificates

- Let's Encrypt docs (function): [https://letsencrypt.org/docs/lencr.org/](https://letsencrypt.org/docs/lencr.org/): "We use it to host data that is referenced inside the certificates we issue."
- Hosts this rule allows or blocks, checked one by one (1):
  - lencr.org: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `(\.|^)linuxtracker\.org$`

Note: Linux Tracker - Torrent site for Linux distributions

- Site text (function): [https://linuxtracker.org/](https://linuxtracker.org/): "LINUX DISTRIBUTIONS. TOGETHER."
- Hosts this rule allows or blocks, checked one by one (1):
  - linuxtracker.org: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `(\.|^)mee6\.xyz$`

Note: MEE6 Discord bot site (mee6.xyz)

- Site title (function): [https://mee6.xyz/](https://mee6.xyz/): "Discord Bot | MEE6"
- Hosts this rule allows or blocks, checked one by one (1):
  - mee6.xyz: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^m\.(hotmail\.com|reddit\.com|reuters\.com|twitch\.tv|youtube\.com)$`

Note: Mobile sites m.hotmail.com, m.reddit.com, m.reuters.com, m.twitch.tv and m.youtube.com

- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `m.youtube.com`
- Hosts this rule allows or blocks, checked one by one (5):
  - m.hotmail.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - m.reddit.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - m.reuters.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - m.twitch.tv: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - m.youtube.com: DNS NOERROR; not named in the sources fetched; 5 lookups on the maintainer's network

### `^(www\.)?minecraft\.net$`

Note: Minecraft website

- Hosts this rule allows or blocks, checked one by one (2):
  - minecraft.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - www.minecraft.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^((mobile|www|upload)\.)?twitter\.com$`

Note: twitter.com and its mobile, www and upload hosts - Pi-hole users list them for Twitter

- Pi-hole forum: Twitter (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `upload.twitter.com` under the heading "Twitter"
- Hosts this rule allows or blocks, checked one by one (4):
  - mobile.twitter.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - twitter.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/README.md, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - upload.twitter.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - www.twitter.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^(www\.)?(myqnapcloud|qnap)\.com$`

Note: qnap.com and myqnapcloud.com with their www hosts

- Hosts this rule allows or blocks, checked one by one (4):
  - myqnapcloud.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - qnap.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - www.myqnapcloud.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - www.qnap.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^(www\.)?no-ip\.com$`

Note: No-IP website (no-ip.com and www)

- Hosts this rule allows or blocks, checked one by one (2):
  - no-ip.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt; 0 lookups on the maintainer's network
  - www.no-ip.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt; 0 lookups on the maintainer's network

### `^ns[12]\.dropbox\.com$`

Note: Dropbox hosts ns1.dropbox.com and ns2.dropbox.com - Listed in community allowlists

- Pi-hole forum: Dropbox (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `ns1.dropbox.com` under the heading "Dropbox"
- Hosts this rule allows or blocks, checked one by one (2):
  - ns1.dropbox.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - ns2.dropbox.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

### `^(oauthaccountmanager|www|youtubei)\.googleapis\.com$`

Note: Google hosts www, youtubei and oauthaccountmanager.googleapis.com - Pi-hole users list them for YouTube on iOS

- Pi-hole forum: YouTube app for iOS (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `youtubei.googleapis.com` under the heading "YouTube App for iOS"
- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `oauthaccountmanager.googleapis.com`
- Hosts this rule allows or blocks, checked one by one (3):
  - oauthaccountmanager.googleapis.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 177 lookups on the maintainer's network
  - www.googleapis.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://discourse.pi-hole.net/raw/212; 33 lookups on the maintainer's network
  - youtubei.googleapis.com: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 71 lookups on the maintainer's network

### `^ocsp[0-9]*\.(apple|digicert|verisign)\.com$|^ocsp\.entrust\.net$`

Note: Certificate status (OCSP) hosts of Apple, DigiCert, VeriSign and Entrust

- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `ocsp2.apple.com`
- Note on the evidence: Open-ended (ocsp[0-9]*).

### `^orderprocessor.*\.ol\.epicgames\.com$`

Note: Epic Games orderprocessor* hosts - Maintainer reported they are needed to buy games

- Example host resolves and matches (pihole-FTL) (scope): Example hosts tested with DNS and pihole-FTL (full record): {"orderprocessor-public-service-ecomprod01.ol.epicgames.com": {"dns": "NOERROR", "cname": ["weighted-orderprocessor-public-service-prod.ol.epicgames.com.", "orderprocessor-public-service-prod.cdce.live.use1a.on.epicgames.com."], "ftl_match": true}, "orderprocessor-public-service-prod.ol.epicgames.com": {"dns": "NOERROR", "cname": ["weighted-orderprocessor-public-service-prod.ol.epicgames.com.", "orderprocessor-public-service-prod.cdce.live.use1a.on.epicgames.com."], "ftl_match": true}}
- Maintainer's earlier note (product): commit [0a7a3ac](https://github.com/slyfox1186/pihole-regex/commit/0a7a3ac) added the line `^orderprocessor.*\.ol\.epicgames\.com$ -- Epic Games - Required to buy games on Windows`
- Flags: `other`. Open-ended (orderprocessor.*).

### `^otnprd[0-9]+\.samsungcloudsolution\.net$`

Note: Samsung TV otnprd* hosts - Perflyst: required for software update

- Perflyst: required for software update (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#otnprd10.samsungcloudsolution.net # required for software update"
- Note on the evidence: Open-ended (otnprd[0-9]+).

### `^outlook\.(live|office(|365))\.com$`

Note: Outlook web mail (outlook.live.com, outlook.office.com, outlook.office365.com)

- Microsoft 365 lists outlook.office365.com (product): [https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges): "outlook.office365.com"
- Hosts this rule allows or blocks, checked one by one (3):
  - outlook.live.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt; 0 lookups on the maintainer's network
  - outlook.office.com: DNS NOERROR; named in https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges; 0 lookups on the maintainer's network
  - outlook.office365.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, https://learn.microsoft.com/en-us/microsoft-365/enterprise/network-requests-in-office-2016-for-mac, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

### `^payment.*\.ol\.epicgames\.com$`

Note: Epic Games payment* hosts - Maintainer reported they are needed for payments

- Example host resolves and matches (pihole-FTL) (scope): Example hosts tested with DNS and pihole-FTL (full record): {"payment-website-pci.ol.epicgames.com": {"dns": "NOERROR", "cname": ["weighted-payment-website-pci.ol.epicgames.com.", "payment-website-fargate-1306000376.us-east-1.elb.amazonaws.com."], "ftl_match": true}, "payment-public-service-prod.ol.epicgames.com": {"dns": "NOERROR", "cname": ["payment-service-fargate-1560071709.us-east-1.elb.amazonaws.com."], "ftl_match": true}}
- Maintainer's earlier note (product): commit [f3f9cbb](https://github.com/slyfox1186/pihole-regex/commit/f3f9cbb) added the line `^payment.*\.ol\.epicgames\.com$ -- Epic Games - Required for payments to process`
- Flags: `other`. Open-ended (payment.*).

### `(\.|^)redd\.it$`

Note: redd.it and its subdomains

- Hosts this rule allows or blocks, checked one by one (1):
  - redd.it: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
- Flags: `unverified_purpose`. No fetched source; the old note said Reddit images, video and short links.

### `^((www|old|new|oauth|gql|gql-fed|gateway)\.)?reddit\.com$`

Note: Reddit - reddit.com and its www, old, new, oauth, gql, gql-fed and gateway hosts

- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `www.reddit.com`
- Hosts this rule allows or blocks, checked one by one (8):
  - gateway.reddit.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - gql-fed.reddit.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - gql.reddit.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - new.reddit.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - oauth.reddit.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - old.reddit.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - reddit.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - www.reddit.com: DNS NOERROR; named in https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt, https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV-AGH.txt, https://discourse.pi-hole.net/raw/212; 7 lookups on the maintainer's network

### `(\.|^)robvanderwoude\.com$`

Note: Rob van der Woude's website (robvanderwoude.com)

- Hosts this rule allows or blocks, checked one by one (1):
  - robvanderwoude.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `(\.|^)samsungcloudcdn\.com$`

Note: samsungcloudcdn.com - Perflyst: blocking otn.samsungcloudcdn.com prevents Samsung TV updates

- Perflyst: blocking otn.samsungcloudcdn.com prevents updates (consequence): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#otn.samsungcloudcdn.com # Prevents updates on UE49KS7000 and QE55Q9FNA"
- Hosts this rule allows or blocks, checked one by one (1):
  - samsungcloudcdn.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `(\.|^)samsungotn\.net$`

Note: Samsung TV - System update check (samsungotn.net)

- Perflyst: system update check (function): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#samsungotn.net # system update check on Samsung UE65RU7455"
- Hosts this rule allows or blocks, checked one by one (1):
  - samsungotn.net: DNS NOERROR; named in https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt, https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV-AGH.txt; 0 lookups on the maintainer's network

### `^scontent-(atl3|mia3)-1\.xx\.fbcdn\.net$`

Note: Facebook hosts scontent-atl3-1 and scontent-mia3-1.xx.fbcdn.net - Pi-hole users list both for Facebook

- Pi-hole forum: Facebook (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `scontent-atl3-1.xx.fbcdn.net` under the heading "Facebook, Facebook Messenger"
- Hosts this rule allows or blocks, checked one by one (2):
  - scontent-atl3-1.xx.fbcdn.net: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 12 lookups on the maintainer's network
  - scontent-mia3-1.xx.fbcdn.net: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 1 lookups on the maintainer's network

### `(\.|^)symcb\.com$`

Note: symcb.com and its subdomains - Microsoft 365 lists *.symcb.com as a required endpoint

- Microsoft 365 required endpoints (product): [https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges): "*.public-trust.com, *.symcb.com, *.symcd.com"
- Hosts this rule allows or blocks, checked one by one (1):
  - symcb.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^[a-z]\.thumbs\.redditmedia\.com$`

Note: Reddit single-letter thumbs hosts (a-z.thumbs.redditmedia.com)

- Example host resolves via Reddit's Fastly CDN and matches (scope): Example hosts tested with DNS and pihole-FTL (full record): {"a.thumbs.redditmedia.com": {"dns": "NOERROR", "cname": ["dualstack.reddit.map.fastly.net."], "ftl_match": true}, "b.thumbs.redditmedia.com": {"dns": "NOERROR", "cname": ["dualstack.reddit.map.fastly.net."], "ftl_match": true}}
- Note on the evidence: Open-ended single-letter subdomain.

### `(\.|^)twimg\.com$`

Note: twimg.com and its subdomains - Listed in anudeep's allowlist

- anudeep's allowlist (product): [https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt](https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt): "twimg.com"
- Hosts this rule allows or blocks, checked one by one (1):
  - twimg.com: DNS NOERROR; named in https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt; 0 lookups on the maintainer's network

### `(\.|^)unraid\.net$`

Note: Unraid - unraid.net and its subdomains

- Site title (function): [https://www.unraid.net/](https://www.unraid.net/): "The Homelab OS for Storage, Docker &amp; VMs"
- Hosts this rule allows or blocks, checked one by one (1):
  - unraid.net: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
- Note on the evidence: The old note said Unraid needs it to update; not verified.

### `(\.|^)wa\.me$`

Note: wa.me and its subdomains - Pi-hole users list wa.me for WhatsApp

- Pi-hole forum: WhatsApp (product): [https://discourse.pi-hole.net/raw/212](https://discourse.pi-hole.net/raw/212) lists `wa.me` under the heading "WhatsApp"
- Hosts this rule allows or blocks, checked one by one (1):
  - wa.me: DNS NOERROR; named in https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network

### `^whatsapp-cdn-shv-[0-9]{2}-[a-z]{3}[0-9]\.fbcdn\.net$`

Note: fbcdn.net hosts named whatsapp-cdn-shv-*

- Example host resolves and matches (pihole-FTL) (scope): Example hosts tested with DNS and pihole-FTL (full record): {"whatsapp-cdn-shv-01-atl3.fbcdn.net": {"dns": "NOERROR", "cname": [], "ftl_match": true}, "whatsapp-cdn-shv-02-mia3.fbcdn.net": {"dns": "NOERROR", "cname": [], "ftl_match": true}, "whatsapp-cdn-shv-01-iad3.fbcdn.net": {"dns": "NOERROR", "cname": [], "ftl_match": true}}
- Note on the evidence: Open-ended.

### `(\.|^)windowsupdate\.com$`

Note: Windows Update (windowsupdate.com and its subdomains)

- Microsoft documents *.windowsupdate.com (function): [https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting](https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/windows-update-issues-troubleshooting): "HTTP *.windowsupdate.com"
- Hosts this rule allows or blocks, checked one by one (1):
  - windowsupdate.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^(www\.|go\.)?microsoft\.com$|^(www\.)?windows\.com$`

Note: Microsoft and Windows main sites and go.microsoft.com links

- Hosts this rule allows or blocks, checked one by one (5):
  - go.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/azure/devops/organizations/security/allow-list-ip-url, https://learn.microsoft.com/en-us/defender-endpoint/configure-network-connections-microsoft-defender-antivirus, https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, https://learn.microsoft.com/en-us/microsoft-365/enterprise/network-requests-in-office-2016-for-mac; 0 lookups on the maintainer's network
  - microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/azure/devops/organizations/security/allow-list-ip-url, https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services, https://learn.microsoft.com/en-us/windows/deployment/do/delivery-optimization-endpoints, https://discourse.pi-hole.net/raw/212; 0 lookups on the maintainer's network
  - windows.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network
  - www.microsoft.com: DNS NOERROR; named in https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services, https://learn.microsoft.com/en-us/defender-endpoint/configure-network-connections-microsoft-defender-antivirus, https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7, https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints, https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions; 1 lookups on the maintainer's network
  - www.windows.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network

### `^((www|(w[0-9]\.)?web|media((-[a-z]{3}|\.[a-z]{4})[0-9]{1,2}-[0-9](\.|-)(cdn|fna))?)\.)?whatsapp\.(com|net)$`

Note: WhatsApp - whatsapp.com and whatsapp.net with www, web and media hosts

- Used on the maintainer's network (observation): Matching lookups on the maintainer's network: `whatsapp.com`

### `^(aic|eic|kic)\.(cdplauncher|lgchhomeapp)\.lgtvcommon\.com$`

Note: LG Channels app launch hosts (aic reported to HaGeZi) and their eic/kic regional names - Exceptions to the lgtvcommon.com block rule

- HaGeZi #11544 report (consequence): [https://github.com/hagezi/dns-blocklists/issues/11544](https://github.com/hagezi/dns-blocklists/issues/11544): "Blocking "lgtvcommon.com" domain requests is preventing LG Channels app to be launched on the smart TV"
- Hosts named in that report (product): [https://github.com/hagezi/dns-blocklists/issues/11544](https://github.com/hagezi/dns-blocklists/issues/11544): "aic.cdplauncher.lgtvcommon.com aic.cdpbeacon.lgtvcommon.com aic.lgchhomeapp.lgtvcommon.com"
- HaGeZi kept only these lgtvcommon.com hosts blocked; cdplauncher and lgchhomeapp are not among them (function): [https://github.com/hagezi/dns-blocklists/issues/11544](https://github.com/hagezi/dns-blocklists/issues/11544): "Remains blocked (Ads/Tracking): ``` ads.lgtvcommon.com adts.lgtvcommon.com cdpbeacon.lgtvcommon.com cdpbeacon2.lgtvcommon.com"
- HaGeZi accepted region variants of LG service hosts as needed for the same function (function): [https://github.com/hagezi/dns-blocklists/issues/1807](https://github.com/hagezi/dns-blocklists/issues/1807): "I presume any `*.service.lgtvcommon.com` domains are required for the same function, just different regions."
- pihole-FTL: the tracking host cdpbeacon stays blocked (scope): ftl_tests_2026_11_14: `"aic.cdpbeacon.lgtvcommon.com": "no match"`
- pihole-FTL: eic.recommend stays blocked (scope): ftl_tests_2026_11_14: `"eic.recommend.lgtvcommon.com": "no match"`
- Hosts this rule allows or blocks, checked one by one (6):
  - aic.cdplauncher.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
  - aic.lgchhomeapp.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
  - eic.cdplauncher.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
  - eic.lgchhomeapp.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
  - kic.cdplauncher.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
  - kic.lgchhomeapp.lgtvcommon.com: DNS NOERROR; not named in the sources fetched; 0 lookups on the maintainer's network; would be blocked by this repo's deny regex
- Note on the evidence: Decision 2026-11-14: added. Only the aic hosts were reported; the eic and kic names are the same hosts for other regions. No list classifies any of them as tracking, so allowing them costs no privacy.

## Regex blocklist (regex-blacklist.sql)

### `^aax(-[a-z0-9]+)*(\.[a-z0-9-]+)?\.amazon\.com$`

Note: Amazon aax hosts (aax-*.amazon.com) - Most of its 20 matches come from ad blocklists

- Matches 20 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `20`
- Matched a lookup on the maintainer's network (observation): Matching lookups on the maintainer's network: `aax-us-east-retail-direct.amazon.com`

### `^ads?\.[a-z0-9-]+\.com\.edgesuite\.net$`

Note: Ad hosts on Akamai edgesuite.net (ad. and ads. only, so Windows Update's adl.windows.com is not blocked)

- Matches 3 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `3`
- Matched a lookup on the maintainer's network (observation): Matching lookups on the maintainer's network: `ads.hulu.com.edgesuite.net`
- Narrowed in the second audit (product): commit [652f298](https://github.com/slyfox1186/pihole-regex/commit/652f298) message: "stop blocking Windows Update via an Akamai ad rule"

### `^adim(age|g)s?[0-9]*[_.-]`

Note: Generic rule - Blocks names that start with adimage or adimg

- Same rule as mmotti's regex list (product): [https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list](https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list): "^adim(age|g)s?[0-9]*[_.-]"
- Matches 37 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `37`

### `^(.+[_.-])?adse?rv(er?|ice)?s?[0-9]*[_.-]`

Note: Generic rule - Matches adserver-style name segments (adserv, adsrv, adservice, with plural and numbered forms) between dots, dashes or underscores

- Same rule as mmotti's regex list (product): [https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list](https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list): "^(.+[_.-])?adse?rv(er?|ice)?s?[0-9]*[_.-]"
- Matches 827 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `827`
- Matched a lookup on the maintainer's network (observation): Matching lookups on the maintainer's network: `adservice.google.com`
- pihole-FTL: inside a hyphenated name (scope): pihole-FTL regex-test results (full record): {"foo-adserver.example.com": "match", "adserver2.example.com": "match", "adservice.google.com": "match", "adsrv.example.com": "match"}
- pihole-FTL: numbered form (scope): pihole-FTL regex-test results (full record): {"foo-adserver.example.com": "match", "adserver2.example.com": "match", "adservice.google.com": "match", "adsrv.example.com": "match"}

### `(^|\.)ad([sx][0-9]*|[0-9]+|system)[_.-]|(^|\.)adv[0-9]*([_-]|\.[^.]+\.[^.]+)`

Note: Generic ad rule - ads/adx (+digits), ad+digits or adsystem before . - or _; adv (+digits) needs - or _ or two more labels

- Matches 4500 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `4500`
- Matched a lookup on the maintainer's network (observation): Matching lookups on the maintainer's network: `ads.celtra.com`
- Narrowed from mmotti's ad rule in the 2026-11-13 audit (product): commit [d93c6dd](https://github.com/slyfox1186/pihole-regex/commit/d93c6dd) message: "narrow the ad rule so .adv.br sites resolve"
- pihole-FTL: plain ad. does not match (scope): pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"}
- pihole-FTL: ads. matches (scope): pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"}
- pihole-FTL: adx. matches (scope): pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"}
- pihole-FTL: ad3. matches (scope): pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"}
- pihole-FTL: adsystem. matches (scope): pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"}
- pihole-FTL: adv. with two more labels matches (scope): pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"}
- pihole-FTL: .adv.br does not match (scope): pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"}
- pihole-FTL: ads3. matches (scope): pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"}
- pihole-FTL: adx7. matches (scope): pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"}
- pihole-FTL: adv- matches (scope): pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"}
- pihole-FTL: adv_ matches (scope): pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"}
- pihole-FTL: adv2. matches (scope): pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"}
- pihole-FTL: adv2- matches (scope): pihole-FTL regex-test results (full record): {"ad.example.com": "no match", "ads.example.com": "match", "adx.example.com": "match", "ad3.example.com": "match", "adsystem.example.com": "match", "ads-field.aylanetworks.com": "match", "adv.example.com": "match", "firm.adv.br": "no match", "anti-ad.net": "no match", "www.ad.nl": "no match", "ads3.example.com": "match", "adx7.example.com": "match", "adv-example.com": "match", "adv_example.com": "match", "adv.example.net": "match", "adv2.example.com": "match", "adv2-example.com": "match"}
- Note on the evidence: Real services it catches have exceptions (Ayla, the Jamaica tax portal, OAB webmail).

### `^adtrack(er|ing)?[0-9]*[_.-]`

Note: Generic rule - Blocks names that start with adtrack/adtracker/adtracking

- Same rule as mmotti's regex list (product): [https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list](https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list): "^adtrack(er|ing)?[0-9]*[_.-]"
- Matches 27 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `27`

### `^advert(s|is(ing|ements?))?[0-9]*[_.-]`

Note: Generic rule - Blocks names that start with advert, adverts or advertising

- Same rule as mmotti's regex list (product): [https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list](https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list): "^advert(s|is(ing|ements?))?[0-9]*[_.-]"
- Matches 66 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `66`

### `(^|\.)(ahoravideo-(blog|cdn)\.com|bideo-(cdn|schnellvpn)\.com|fairu-(chat|endpoint|schnellvpn)\.com|fairu-schnellvpn\.xyz|privatproxy-(chat|schnellvpn)\.com|wmail-blog\.com)$`

Note: ViperSoftX malware command servers - The 11 of its 50 generated names whose subdomains no adlist blocks

- The malware's PowerShell builds these names (function): [https://chris.partridge.tech/2022/evolution-of-vipersoftx-dga/](https://chris.partridge.tech/2022/evolution-of-vipersoftx-dga/): "@("wmail", "fairu", "bideo", "privatproxy", "ahoravideo")"
- Expands to 50 names (scope): Names it matches in a 2.17M-name test corpus: `50`
- Narrowed on 2026-11-22 (observation): `pihole -q` on a subdomain of each name showed HaGeZi Threat Intelligence Feeds (and HaGeZi Multi PRO) block 39 of the 50 with all subdomains; the rule keeps the other 11

### `^analytics?[_.-]`

Note: Generic rule - Blocks names that start with analytic or analytics

- Same rule as mmotti's regex list (product): [https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list](https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list): "^analytics?[_.-]"
- Matches 2070 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `2070`
- Matched a lookup on the maintainer's network (observation): Matching lookups on the maintainer's network: `analytics.google.com`
- Note on the evidence: Real services under analytics. need exact allows.

### `(\.|^)antivirushub\.com$`

Note: antivirushub.com - Maintainer added it as a 1337x.to redirect domain; it resolved on 2026-11-13

- antivirushub.com DNS status on 2026-11-13 (observation): DNS status `antivirushub.com`: `NOERROR`
- Maintainer's earlier note (product): commit [2c047d2](https://github.com/slyfox1186/pihole-regex/commit/2c047d2) added the line `(\.|^)antivirushub\.com$ -- 1337x.to - Sneaky redirect domains that probably log your IP and any other information it gets from your browser sending a GET or POST request.`
- Flags: `other`, `unverified_purpose`. No source for the 1337x redirect claim; no blocklist in the maintainer's Pi-hole contains it.

### `^api\..*\.hismarttv\.com$`

Note: api.*.hismarttv.com hosts - Perflyst's Smart TV rules block them

- Perflyst's Smart TV regex list has the same rule (product): [https://perflyst.github.io/PiHoleBlocklist/regex.list](https://perflyst.github.io/PiHoleBlocklist/regex.list): "^api\..*\.hismarttv\.com$"
- Matches 3 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `3`

### `^(collect|usage)-(eu|us)-fy[0-9]+\.myhomescreen\.tv$`

Note: Panasonic Viera TV hosts collect-/usage-*.myhomescreen.tv - Perflyst blocks them

- Perflyst blocks these hosts under Panasonic (product): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt) lists `collect-us-fy2022.myhomescreen.tv` under the heading "Panasonic Viera &amp; panny tv"
- Matches 36 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `36`

### `(\.|^)filesupdating\.com$`

Note: filesupdating.com - Maintainer labeled it iTop VPN; it resolved on 2026-11-13

- filesupdating.com DNS status on 2026-11-13 (observation): DNS status `filesupdating.com`: `NOERROR`
- Maintainer's earlier note (product): commit [2c047d2](https://github.com/slyfox1186/pihole-regex/commit/2c047d2) added the line `(\.|^)filesupdating\.com$ -- iTop VPN`
- Flags: `other`, `unverified_purpose`. No source describes it.

### `(\.|^)internetat\.tv$`

Note: internetat.tv - Perflyst's Smart TV rules block it

- Perflyst's Smart TV regex list has the same rule (product): [https://perflyst.github.io/PiHoleBlocklist/regex.list](https://perflyst.github.io/PiHoleBlocklist/regex.list): "(^|\.)internetat\.tv$"
- Matches 3 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `3`

### `(^|\.)lgtvcommon\.com$`

Note: lgtvcommon.com - Perflyst's Smart TV rules block it; guide-data and LG Channels app launch hosts are allowed in regex-whitelist

- Perflyst's Smart TV regex list has the same rule (product): [https://perflyst.github.io/PiHoleBlocklist/regex.list](https://perflyst.github.io/PiHoleBlocklist/regex.list): "(^|\.)lgtvcommon\.com"
- Matched a lookup on the maintainer's network (observation): Matching lookups on the maintainer's network: `eic.recommend.lgtvcommon.com`
- Note on the evidence: Decision 2026-11-14: kept. HaGeZi #11544 (2026-09-23) keeps recommend, cdpbeacon and other lgtvcommon.com tracking hosts blocked; the guide-data and LG Channels hosts are allowed by regex-whitelist.

### `(\.|^)log[0-9]*\.spotify\.com$`

Note: Matches log.spotify.com, log plus any digits under spotify.com, and subdomains of those hosts

- Matches 2 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `2`
- pihole-FTL: log123 matches (scope): pihole-FTL regex-test results (full record): {"log.spotify.com": "match", "log2.spotify.com": "match", "log123.spotify.com": "match", "x.log2.spotify.com": "match", "logger.spotify.com": "no match"}
- pihole-FTL: subdomain matches (scope): pihole-FTL regex-test results (full record): {"log.spotify.com": "match", "log2.spotify.com": "match", "log123.spotify.com": "match", "x.log2.spotify.com": "match", "logger.spotify.com": "no match"}
- pihole-FTL: logger does not match (scope): pihole-FTL regex-test results (full record): {"log.spotify.com": "match", "log2.spotify.com": "match", "log123.spotify.com": "match", "x.log2.spotify.com": "match", "logger.spotify.com": "no match"}

### `(\.|^)pavv\.co\.kr$`

Note: pavv.co.kr (Samsung) - infolink.pavv.co.kr is allowed for the app store and sign-in

- Perflyst's Smart TV regex list has the same rule (product): [https://perflyst.github.io/PiHoleBlocklist/regex.list](https://perflyst.github.io/PiHoleBlocklist/regex.list): "(^|\.)pavv\.co\.kr$"
- Matches 2 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `2`

### `(^|\.)samsungcloudsolution\.net$`

Note: samsungcloudsolution.net (Samsung) - Exact allows exempt configprd and lcprd1.samsungcloudsolution.net

- Perflyst's Smart TV regex list has the same rule (product): [https://perflyst.github.io/PiHoleBlocklist/regex.list](https://perflyst.github.io/PiHoleBlocklist/regex.list): "(^|\.)samsungcloudsolution\.net$"
- Matched a lookup on the maintainer's network (observation): Matching lookups on the maintainer's network: `lcprd1.samsungcloudsolution.net`

### `(\.|^)samsungelectronics\.com$`

Note: samsungelectronics.com - Perflyst's Samsung TV rules block it

- Perflyst's Smart TV regex list has the same rule (product): [https://perflyst.github.io/PiHoleBlocklist/regex.list](https://perflyst.github.io/PiHoleBlocklist/regex.list): "(^|\.)samsungelectronics\.com$"
- Matches 10 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `10`
- Flags: `unverified_purpose`. Perflyst gives no description.

### `(\.|^)samsungqbe\.com$`

Note: samsungqbe.com and its subdomains - Blocks Samsung service hosts; TV Plus and one service host are allowed

- Matched a lookup on the maintainer's network (observation): Matching lookups on the maintainer's network: `osb-krsvc-v2.samsungqbe.com`
- Samsung device looked up osb-krsvc-v2 1,070 times (observation): Matching lookups on the maintainer's network: `1070`
- Note on the evidence: Decision 2026-11-14: kept. The maintainer chose to keep it. It blocks the Samsung device's osb-*-v2 lookups (about 1,900 since 2026-11-12); if TV Plus or sign-in misbehaves, check this rule first.

### `(\.|^)samsungrm\.net$`

Note: samsungrm.net - Perflyst's Samsung TV rules block it

- Perflyst's Smart TV regex list has the same rule (product): [https://perflyst.github.io/PiHoleBlocklist/regex.list](https://perflyst.github.io/PiHoleBlocklist/regex.list): "(^|\.)samsungrm\.net$"
- Matches 2 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `2`
- Flags: `unverified_purpose`. Perflyst gives no description.

### `(\.|^)smartshare\.lgtvsdp\.com$`

Note: smartshare.lgtvsdp.com - Perflyst's Smart TV rules block it

- Perflyst's Smart TV regex list has the same rule (product): [https://perflyst.github.io/PiHoleBlocklist/regex.list](https://perflyst.github.io/PiHoleBlocklist/regex.list): "(^|\.)smartshare\.lgtvsdp\.com"
- smartshare.lgtvsdp.com DNS status on 2026-11-13 (observation): DNS status `smartshare.lgtvsdp.com`: `NOERROR`

### `^[a-z0-9]+\.ssm[1-2]?\.internet\.sony\.tv$`

Note: Sony TV hosts under ssm*.internet.sony.tv (the ssm hosts themselves stay reachable)

- Matches 2 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `2`
- Perflyst leaves ssm1.internet.sony.tv unblocked (product): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "#ssm1.internet.sony.tv # https://github.com/notracking/hosts-blocklists/issues/384"
- Flags: `unverified_purpose`. What the per-device subdomains do is unverified; Perflyst deliberately does not block the ssm hosts.

### `^stat(s|istics)?[0-9]*[-_]`

Note: Generic rule - Blocks names starting stat-, stats- or statistics-

- Matches 85 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `85`
- mmotti's original stats rule (product): [https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list](https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list): "^stat(s|istics)?[0-9]*[_.-]"
- Maintainer's narrowed rule (product): commit [1677a89](https://github.com/slyfox1186/pihole-regex/commit/1677a89) added the line `^stat(s|istics)?[0-9]*[-_] -- stats/metrics (narrowed to avoid false positives)`

### `(^|\.)telemetry[-_][a-z0-9]`

Note: Generic rule - Blocks telemetry- and telemetry_ names

- Matches 7 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `7`
- mmotti's original telemetry rule (product): [https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list](https://raw.githubusercontent.com/mmotti/pihole-regex/master/regex.list): "^(.+[_.-])?telemetry[_.-]"
- Maintainer's narrowed rule (product): commit [1677a89](https://github.com/slyfox1186/pihole-regex/commit/1677a89) added the line `(^|\.)telemetry[-_][a-z0-9] -- telemetry (narrowed to avoid false positives)`

### `(\.|^)tvinteractive\.tv$`

Note: tvinteractive.tv - Perflyst's Smart TV rules block it

- Perflyst's Smart TV regex list has the same rule (product): [https://perflyst.github.io/PiHoleBlocklist/regex.list](https://perflyst.github.io/PiHoleBlocklist/regex.list): "(\.|^)tvinteractive\.tv$"
- Matches 5 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `5`
- Flags: `unverified_purpose`. Perflyst gives no description; the old note said Vizio Inscape viewing data.

### `^[a-z]{2}-[a-z]{2}-[a-z]{2}\.ybp\.gysm\.yahoodns\.net$`

Note: Yahoo DNS name pattern xx-xx-xx.ybp.gysm.yahoodns.net - No matches in the 2.17M-name test corpus on 2026-11-13

- Matches 0 names in the 2.17M-name test corpus (blocklists, query log, repo lists) on 2026-11-13 (observation): Names it matches in a 2.17M-name test corpus: `0`
- Maintainer's earlier note (product): commit [2c047d2](https://github.com/slyfox1186/pihole-regex/commit/2c047d2) added the line `^[a-z]{2}-[a-z]{2}-[a-z]{2}\.ybp\.gysm\.yahoodns\.net$ -- Yahoo`
- Flags: `other`. Decision 2026-11-14: kept. No current matches, so it neither blocks nor breaks anything today.

## Adlists (adlists.txt)

### `https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Spam/hosts`

Note: FadeMind add.Spam (StevenBlack extras) - Spam websites

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Fademind's Spammers: https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Spam/hosts"
- FadeMind's README (function): [https://raw.githubusercontent.com/FadeMind/hosts.extras/master/README.md](https://raw.githubusercontent.com/FadeMind/hosts.extras/master/README.md): "| add.Spam   	 	 | Spam websites. **MIRROR**"

### `https://raw.githubusercontent.com/PolishFiltersTeam/KADhosts/master/KADhosts.txt`

Note: KADhosts by PolishFiltersTeam - Scam and fraud sites (SMS subscription traps, viruses, fake shops)

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "PolishFiltersTeam KADhosts: https://raw.githubusercontent.com/PolishFiltersTeam/KADhosts/master/KADhosts.txt"
- The list's own header (function): [https://raw.githubusercontent.com/PolishFiltersTeam/KADhosts/master/KADhosts.txt](https://raw.githubusercontent.com/PolishFiltersTeam/KADhosts/master/KADhosts.txt): "Filtry chroniace przed roznego rodzaju przekretami i oszustwami, takimi jak np. subskrypcje SMS, wirusy i falszywe sklepy internetowe."

### `https://v.firebog.net/hosts/static/w3kbl.txt`

Note: WaLLy3K's personal blocklist (Firebog maintainer) - Manually verified suspicious domains

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "WaLLy3K's Blacklist: https://v.firebog.net/hosts/static/w3kbl.txt"
- The list's own header (function): [https://v.firebog.net/hosts/static/w3kbl.txt](https://v.firebog.net/hosts/static/w3kbl.txt): "Content added to this list has been manually verified"

### `https://adaway.org/hosts.txt`

Note: AdAway default list - Mobile ad providers and some analytics

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "AdAway: https://adaway.org/hosts.txt"
- The list's own header (function): [https://adaway.org/hosts.txt](https://adaway.org/hosts.txt): "Blocking mobile ad providers and some analytics providers"

### `https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext`

Note: Peter Lowe's ad server list - Ads, trackers and other unwanted hosts

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Peter Lowe's Adservers: https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&amp;showintro=0&amp;mimetype=plaintext"
- The list's own header (function): [https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext](https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext): "Blocklist for use with hosts files to block ads, trackers, and other nasty things"

### `https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt`

Note: Anudeep's Blacklist - Ad servers and tracking hosts

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Anudeep ND's Blacklist: https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt"
- The list's own header (function): [https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt](https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt): "Host file to block ads, tracking and more!"

### `https://raw.githubusercontent.com/bigdargon/hostsVN/master/hosts`

Note: hostsVN by bigdargon - Firebog Advertising list

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "hostsVN: https://raw.githubusercontent.com/bigdargon/hostsVN/master/hosts"
- The list's own header (function): [https://raw.githubusercontent.com/bigdargon/hostsVN/master/hosts](https://raw.githubusercontent.com/bigdargon/hostsVN/master/hosts): "Title: hostsVN"

### `https://v.firebog.net/hosts/AdguardDNS.txt`

Note: AdGuard DNS filter (parsed by Firebog) - Domain version of AdGuard's DNS filter

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Adguard DNS: https://v.firebog.net/hosts/AdguardDNS.txt"
- The list's own header (function): [https://v.firebog.net/hosts/AdguardDNS.txt](https://v.firebog.net/hosts/AdguardDNS.txt): "AdguardDNS, parsed and mirrored by https://firebog.net"

### `https://v.firebog.net/hosts/Admiral.txt`

Note: Admiral anti-adblock domains (LanikSJ, parsed by Firebog)

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "LanikSJ's Admiral Anti-Adblock: https://v.firebog.net/hosts/Admiral.txt"
- The list's own header (function): [https://v.firebog.net/hosts/Admiral.txt](https://v.firebog.net/hosts/Admiral.txt): "Admiral, parsed and mirrored by https://firebog.net"

### `https://v.firebog.net/hosts/Easylist.txt`

Note: EasyList (parsed by Firebog) - Domain version of easylist.txt

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Easylist: https://v.firebog.net/hosts/Easylist.txt"
- The list's own header (function): [https://v.firebog.net/hosts/Easylist.txt](https://v.firebog.net/hosts/Easylist.txt): "from https://easylist.to/easylist/easylist.txt"

### `https://hostfiles.frogeye.fr/firstparty-trackers-hosts.txt`

Note: Frogeye first-party trackers host list

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Geoffrey Frogeye's First-Party Trackers: https://hostfiles.frogeye.fr/firstparty-trackers-hosts.txt"
- The list's own header (function): [https://hostfiles.frogeye.fr/firstparty-trackers-hosts.txt](https://hostfiles.frogeye.fr/firstparty-trackers-hosts.txt): "First-party trackers host list"

### `https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt`

Note: WindowsSpyBlocker spy rules by crazy-max - Windows telemetry hosts

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Crazy Max's Microsoft Telemetry: https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt"
- The list's own header (function): [https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt](https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt): "WindowsSpyBlocker - Hosts spy rules"

### `https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.2o7Net/hosts`

Note: FadeMind add.2o7Net - Adobe 2o7 network tracking hosts

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Fademind's 2o7 Network Trackers: https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.2o7Net/hosts"
- FadeMind's README (function): [https://raw.githubusercontent.com/FadeMind/hosts.extras/master/README.md](https://raw.githubusercontent.com/FadeMind/hosts.extras/master/README.md): "2o7 Network tracking **MIRROR**"

### `https://v.firebog.net/hosts/Easyprivacy.txt`

Note: EasyPrivacy (parsed by Firebog) - Domain version of easyprivacy.txt

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Easyprivacy: https://v.firebog.net/hosts/Easyprivacy.txt"
- The list's own header (function): [https://v.firebog.net/hosts/Easyprivacy.txt](https://v.firebog.net/hosts/Easyprivacy.txt): "from https://easylist.to/easylist/easyprivacy.txt"

### `https://v.firebog.net/hosts/Prigent-Ads.txt`

Note: Fabrice Prigent's ad list (Toulouse Capitole University, parsed by Firebog) - Ad domains

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Fabrice Prigent's Ads: https://v.firebog.net/hosts/Prigent-Ads.txt"
- The list's own header (function): [https://v.firebog.net/hosts/Prigent-Ads.txt](https://v.firebog.net/hosts/Prigent-Ads.txt): "dsi.ut-capitole.fr/blacklists/download/publicite.tar.gz"

### `https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-malware.txt`

Note: NoTrack malware list by QuidsUp - Malware, phishing and adware domains

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Quidsup Malicious: https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-malware.txt"
- The list's own header (function): [https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-malware.txt](https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-malware.txt): "Domains classified as malware, phishing or adware"

### `https://lists.cyberhost.uk/malware.txt`

Note: CyberHost.uk malware and phishing list

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "CyberHost.uk Malware Domains: https://lists.cyberhost.uk/malware.txt"
- The list's own header (function): [https://lists.cyberhost.uk/malware.txt](https://lists.cyberhost.uk/malware.txt): "CyberHost.uk Malware and Phishing Blocklist"

### `https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-hosts-online.txt`

Note: Online malicious hosts from abuse.ch URLhaus (malware-filter mirror)

- The list's own header (function): [https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-hosts-online.txt](https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-hosts-online.txt): "Title: Online Malicious Hosts Blocklist"
- The list's own header (function): [https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-hosts-online.txt](https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-hosts-online.txt): "Source: https://urlhaus.abuse.ch/api/"

### `https://phishing.army/download/phishing_army_blocklist_extended.txt`

Note: Phishing Army extended list - Phishing domains from PhishTank, OpenPhish, CERT.PL and others

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Phishing Army's Extended Blocklist: https://phishing.army/download/phishing_army_blocklist_extended.txt"
- The list's own header (function): [https://phishing.army/download/phishing_army_blocklist_extended.txt](https://phishing.army/download/phishing_army_blocklist_extended.txt): "Community phishing domain blocklist"

### `https://raw.githubusercontent.com/AssoEchap/stalkerware-indicators/master/generated/hosts`

Note: Echap stalkerware indicators - Domains used by stalkerware apps that secretly spy on phones

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Echap's Stalkerware Indicators: https://raw.githubusercontent.com/AssoEchap/stalkerware-indicators/master/generated/hosts"
- Echap's README (function): [https://raw.githubusercontent.com/AssoEchap/stalkerware-indicators/master/README.md](https://raw.githubusercontent.com/AssoEchap/stalkerware-indicators/master/README.md): "Indicators of compromise (IOC) for Stalkerware and Watchware applications for Android and iOS"

### `https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt`

Note: Dandelion Sprout's Anti-Malware List

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "DandelionSprout's Anti Malware Filter: https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt"
- The list's own header (function): [https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt](https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt): "This list goes the extra kilometer to prevent more malware than other mainstream anti-malware lists."

### `https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Risk/hosts`

Note: FadeMind add.Risk - Risky sites (malware and similar)

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Fademind's Risky Hosts: https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Risk/hosts"
- FadeMind's README (function): [https://raw.githubusercontent.com/FadeMind/hosts.extras/master/README.md](https://raw.githubusercontent.com/FadeMind/hosts.extras/master/README.md): "Websites with risk content, malwares etc. **MIRROR**"

### `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/tif.txt`

Note: HaGeZi Threat Intelligence Feeds - Malware, cryptojacking, scams, spam and phishing

- The list's own header (function): [https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/tif.txt](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/tif.txt): "Title: HaGeZi's Threat Intelligence Feeds"
- The list's own header (function): [https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/tif.txt](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/tif.txt): "This blocklist targets malware, cryptojacking, scams, spam, and phishing."

### `https://raw.githubusercontent.com/Spam404/lists/master/main-blacklist.txt`

Note: Spam404 main blacklist - Firebog Malicious list

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Spam404: https://raw.githubusercontent.com/Spam404/lists/master/main-blacklist.txt"

### `https://v.firebog.net/hosts/Prigent-Crypto.txt`

Note: Fabrice Prigent's cryptojacking list (parsed by Firebog)

- Firebog lists it under this name (product): [https://firebog.net/](https://firebog.net/): "Fabrice Prigent's Cryptojacking: https://v.firebog.net/hosts/Prigent-Crypto.txt"
- The list's own header (function): [https://v.firebog.net/hosts/Prigent-Crypto.txt](https://v.firebog.net/hosts/Prigent-Crypto.txt): "dsi.ut-capitole.fr/blacklists/download/cryptojacking.tar.gz"

### `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.txt`

Note: HaGeZi Multi PRO - Ads, trackers, telemetry, phishing, malware and scams

- The list's own header (function): [https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.txt](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.txt): "Title: HaGeZi's Multi PRO - extended protection (recommended)"
- The list's own header (function): [https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.txt](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.txt): "Blocks ads, trackers, metrics, telemetry, phishing, malware, scams"

### `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.amazon.txt`

Note: HaGeZi Amazon native tracker list - Trackers built into Amazon devices, apps and operating systems

- The list's own header (function): [https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.amazon.txt](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.amazon.txt): "Title: HaGeZi's Amazon Tracker - blocks built-in trackers from devices, apps, and OSes!"

### `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.samsung.txt`

Note: HaGeZi Samsung native tracker list - Trackers built into Samsung devices, apps and operating systems

- The list's own header (function): [https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.samsung.txt](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.samsung.txt): "Title: HaGeZi's Samsung Tracker - blocks built-in trackers from devices, apps, and OSes!"

### `https://hagezi-mirror.dnsbunker.org/adblock/dyndns.txt`

Note: HaGeZi Dynamic DNS - Dynamic DNS providers often abused to host malware and phishing

- The list's own header (function): [https://hagezi-mirror.dnsbunker.org/adblock/dyndns.txt](https://hagezi-mirror.dnsbunker.org/adblock/dyndns.txt): "Title: HaGeZi's DynDNS - guards against dynamic DNS abuse!"
- The list's own header (function): [https://hagezi-mirror.dnsbunker.org/adblock/dyndns.txt](https://hagezi-mirror.dnsbunker.org/adblock/dyndns.txt): "Blocks dynamic DNS services that get abused for phishing campaigns and other shady activity."
- Official mirror (source): [https://github.com/hagezi/dns-blocklists](https://github.com/hagezi/dns-blocklists) lists hagezi-mirror.dnsbunker.org as its build mirror, published with every build.

### `https://hagezi-mirror.dnsbunker.org/adblock/doh.txt`

Note: HaGeZi Encrypted DNS Bypass (DoH only) - Encrypted DNS servers that devices can use to bypass Pi-hole

- The list's own header (function): [https://hagezi-mirror.dnsbunker.org/adblock/doh.txt](https://hagezi-mirror.dnsbunker.org/adblock/doh.txt): "Title: HaGeZi's Encrypted DNS Bypass - stop people from sneaking around your DNS!"
- The list's own header (function): [https://hagezi-mirror.dnsbunker.org/adblock/doh.txt](https://hagezi-mirror.dnsbunker.org/adblock/doh.txt): "Prevent methods to bypass your DNS, blocks encrypted DNS only"
- Official mirror (source): [https://github.com/hagezi/dns-blocklists](https://github.com/hagezi/dns-blocklists) lists hagezi-mirror.dnsbunker.org as its build mirror, published with every build.

### `https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt`

Note: Perflyst Smart TV list - Stops smart TVs sending data back home and blocks some TV interface ads

- The list's own header (function): [https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt](https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt): "This is a blocklist to block smart-TVs sending metadata back home, sometimes with the added benefit of blocking interface ads"

### `https://raw.githubusercontent.com/johang/cookie-consent-hosts/master/hosts.txt`

Note: Cookie consent hosts by johang - Hides cookie and privacy consent banners on websites

- The project's README (function): [https://raw.githubusercontent.com/johang/cookie-consent-hosts/master/README.md](https://raw.githubusercontent.com/johang/cookie-consent-hosts/master/README.md): "A list of hosts that are used to display cookie and privacy consent banners on websites."
