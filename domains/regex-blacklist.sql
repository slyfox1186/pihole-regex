^a-content-[a-z0-9]+-[0-9]+\.[a-z]{2}-[a-z]+-[0-9]\.elb\.amazonaws\.com$ -- Yahoo
^aax(-[a-z0-9]+)*(\.[a-z0-9-]+)?\.amazon\.com$ -- Amazon ad servers (aax)
^ads?\.[a-z0-9-]+\.com\.edgesuite\.net$ -- Ad hosts on Akamai's edgesuite.net (narrowed to ad. and ads. so Windows Update's adl.windows.com is not blocked)
^adim(age|g)s?[0-9]*[_.-] -- mmotti RegEx
(\.|^)ad-score\.com$ -- Overwolf Desktop App (PC Games)
^adserver-.*\.amazonaws\.com$ -- Ad server load balancers hosted on Amazon AWS
^(.+[_.-])?adse?rv(er?|ice)?s?[0-9]*[_.-] -- mmotti RegEx
(^|\.)ad([sx][0-9]*|[0-9]+|system)[_.-]|(^|\.)adv[0-9]*([_-]|\.[^.]+\.[^.]+) -- ad servers (narrowed; avoids anti-ad/ad.nl false positives, and adv. needs two more labels so Brazil's .adv.br lawyer sites stay reachable)
^adtrack(er|ing)?[0-9]*[_.-] -- mmotti RegEx
^advert(s|is(ing|ements?))?[0-9]*[_.-] -- mmotti RegEx
(^|\.)(ahoravideo|bideo|fairu|privatproxy|wmail)-(blog|cdn|chat|endpoint|schnellvpn)\.(com|xyz)$ -- ViperSoftX remote-access trojan command servers (Emerging Threats)
^analytics?[_.-] -- mmotti RegEx
(\.|^)antivirushub\.com$ -- 1337x.to - Sneaky redirect domains that probably log your IP and any other information it gets from your browser sending a GET or POST request.
^api\..*\.hismarttv\.com$ -- Hisense VIDAA Smart TV (Perflyst)
(\.|^)buybuggle\.com$ -- Hacker website - They install a backdoor trojan on your pc and remote in secretly to record you on webcam and copy a list of all your file paths
^(collect|usage)-(eu|us)-fy[0-9]+\.myhomescreen\.tv$ -- Panasonic Viera Smart TV - Usage data collection
^count(ers?)?[0-9]*(\.|[_-][^.]*\.)[^.]+\.[^.]+ -- mmotti RegEx (needs three or more labels, so sites like counter-strike.net stay reachable)
(\.|^)deimos3\.apple\.com$ -- Apple iTunes U tracking (retired)
^dms-[a-z0-9]+report\.wc\.yahoodns\.net$ -- Yahoo
^dns-[a-z0-9]+\.sombrero\.yahoo\.net$ -- Yahoo
^ds-beap[0-9]\.[a-z]{2}\.[a-z0-9]+\.yahoodns\.net$ -- Yahoo
^ds-global[0-9]\.l[0-9]\.search\.[a-z0-9]+\.yahoo\.com$ -- Yahoo
(\.|^)filesupdating\.com$ -- iTop VPN
(\.|^)gammaentertainment\.com$ -- AdultTime
(\.|^)gardensuny\.com$ -- Hacker website - They install a backdoor trojan on your pc and remote in secretly to record you on webcam and copy a list of all your file paths
(\.|^)getbeamer\.com$ -- Beamer announcement and notification widget (seen on AdultTime)
(^|\.)giraffic\.com$ -- Giraffic video acceleration on Samsung Smart TVs (Perflyst)
(\.|^)hokaclearances\.com$ -- Hacker website - They install a backdoor trojan on your pc and remote in secretly to record you on webcam and copy a list of all your file paths
(\.|^)internetat\.tv$ -- Samsung Smart TV (Perflyst)
(\.|^)lgsmartad\.com$ -- LG Smart TV ads
(^|\.)lgtvcommon\.com$ -- LG Smart TV (Perflyst); guide data hosts are allowed in regex-whitelist
(\.|^)log[0-9]*\.spotify\.com$ -- Spotify logging
(\.|^)lstartanalystconcepts\.org\.uk$ -- BitTorrent - Background Tracking
^mads\. -- mmotti RegEx
^nado-ecs-lb-[a-z]+-[a-z]+-[0-9]-[0-9]+\.[a-z]+-[a-z]+-[0-9]\.elb\.amazonaws\.com$ -- Yahoo
(\.|^)pavv\.co\.kr$ -- Samsung Smart TV (Perflyst)
^pixels?(\.|-[^.]*\.)[^.]+\.[^.]+ -- mmotti RegEx (needs three or more labels, so sites like pixels.com stay reachable)
^prod-elb-ats-[0-9]+\.[a-z]{2}-[a-z]+-[0-9]\.elb\.amazonaws\.com$ -- Yahoo
(^|\.)samsungcloudsolution\.net$ -- Samsung Smart TV (Perflyst)
(\.|^)samsungelectronics\.com$ -- Samsung Smart TV (Perflyst and HaGeZi lists block it too)
(\.|^)samsungqbe\.com$ -- Samsung Smart TV
(\.|^)samsungrm\.net$ -- Samsung Smart TV
(\.|^)shadowadcity\.com$ -- 1337x.to - Sneaky redirect domains that probably log your IP and any other information it gets from your browser sending a GET or POST request.
(\.|^)smartshare\.lgtvsdp\.com$ -- LG Smart TV (Perflyst)
^[a-z0-9]+\.ssm[1-2]?\.internet\.sony\.tv$ -- Sony Smart TV
^ssp-ats-prod-[a-z\-]+-[0-9]\.one-mobile-prod\.aws\.oath\.cloud$ -- Yahoo
^stat(s|istics)?[0-9]*[-_] -- stats/metrics (narrowed to avoid false positives)
(\.|^)steamcommurnily\.com$ -- Confirmed hacker website with malicious intent - DANGER
(\.|^)stickyadstv\.com\.akadns\.net$ -- FreeWheel StickyAds CNAME target (CurseForge app ads)
(^|\.)telemetry[-_][a-z0-9] -- telemetry (narrowed to avoid false positives)
(\.|^)trafyield\.com$ -- 1337x.to - Sneaky redirect domains that probably log your IP and any other information it gets from your browser sending a GET or POST request.
(\.|^)tvinteractive\.tv$ -- Vizio Smart TV - Inscape viewing data (Perflyst)
^uplynk-beacon-newvpc-[0-9]+\.[a-z]{2}-[a-z]+-[0-9]\.elb\.amazonaws\.com$ -- Yahoo
(\.|^)usage\.trackjs\.com$ -- TrackJS usage reporting (seen on AdultTime)
^v-[a-z0-9]+\.wc\.yahoodns\.net$ -- Yahoo
^[a-z]{2}-[a-z]{2}-[a-z]{2}\.ybp\.gysm\.yahoodns\.net$ -- Yahoo
