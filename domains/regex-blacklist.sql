^a-content-[a-z0-9]+-[0-9]+\.[a-z]{2}-[a-z]+-[0-9]\.elb\.amazonaws\.com$ -- Yahoo
^aax(-[a-z0-9]+)*(\.[a-z0-9-]+)?\.amazon\.com$ -- Amazon ad servers (aax)
^ad[a-z0-9-]*\.[a-z0-9-]+\.com\.edgesuite\.net$ -- Take out common ad subdomains for master domain com.edgesuite.net
^adim(age|g)s?[0-9]*[_.-] -- mmotti RegEx
(\.|^)ad-score\.com$ -- Overwolf Desktop App (PC Games)
^adserver-.*\.amazonaws\.com$ -- Yahoo
^(.+[_.-])?adse?rv(er?|ice)?s?[0-9]*[_.-] -- mmotti RegEx
(^|\.)ad([sxv][0-9]*|[0-9]+|system)[_.-] -- ad servers (narrowed; avoids anti-ad/ad.nl false positives)
^adtrack(er|ing)?[0-9]*[_.-] -- mmotti RegEx
^advert(s|is(ing|ements?))?[0-9]*[_.-] -- mmotti RegEx
^aff(iliat(es?|ion))?[_.-] -- mmotti RegEx
(^|\.)(ahoravideo|bideo|fairu|privatproxy|wmail)-(blog|cdn|chat|endpoint|schnellvpn)\.(com|xyz)$ -- ViperSoftX remote-access trojan command servers (Emerging Threats)
^analytics?[_.-] -- mmotti RegEx
(\.|^)antivirushub\.com$ -- 1337x.to - Sneaky redirect domains that probably log your IP and any other information it gets from your browser sending a GET or POST request.
^api\..*\.hismarttv\.com$ -- Smart TV (Vizio/Other)
^banners?[_.-] -- mmotti RegEx
^beacons?[0-9]*(\.|[_-][^.]*\.)[^.]+\.[^.]+ -- mmotti RegEx (needs three or more labels, so sites like beacons.ai stay reachable)
(\.|^)buybuggle\.com$ -- Hacker website - They install a backdoor trojan on your pc and remote in secretly to record you on webcam and copy a list of all your file paths
^(collect|usage)-(eu|us)-fy[0-9]+\.myhomescreen\.tv$ -- Other Smart TVs
^count(ers?)?[0-9]*(\.|[_-][^.]*\.)[^.]+\.[^.]+ -- mmotti RegEx (needs three or more labels, so sites like counter-strike.net stay reachable)
^cs[0-9]+\.wpc\.thetacdn\.net$ -- Yahoo
(\.|^)deimos3\.apple\.com$ -- Apple
^dms-[a-z0-9]+report\.wc\.yahoodns\.net$ -- Yahoo
^dns-[a-z0-9]+\.sombrero\.yahoo\.net$ -- Yahoo
^ds-beap[0-9]\.[a-z]{2}\.[a-z0-9]+\.yahoodns\.net$ -- Yahoo
^ds-global[0-9]\.l[0-9]\.search\.[a-z0-9]+\.yahoo\.com$ -- Yahoo
(\.|^)filesupdating\.com$ -- iTop VPN
(\.|^)gammaentertainment\.com$ -- AdultTime
(\.|^)gardensuny\.com$ -- Hacker website - They install a backdoor trojan on your pc and remote in secretly to record you on webcam and copy a list of all your file paths
(\.|^)getbeamer\.com$ -- AdultTime
(^|\.)giraffic\.com$ -- Smart TV (Samsung/Other)
(\.|^)hokaclearances\.com$ -- Hacker website - They install a backdoor trojan on your pc and remote in secretly to record you on webcam and copy a list of all your file paths
(\.|^)internetat\.tv$ -- Smart TV (Samsung/Other)
(\.|^)lgsmartad\.com$ -- LG Smart TVs
(^|\.)lgtvcommon\.com$ -- LG Smart TV / LG TV
(\.|^)log[0-9]*\.spotify\.com$ -- Spotify
(\.|^)lstartanalystconcepts\.org\.uk$ -- BitTorrent - Background Tracking
^mads\. -- mmotti RegEx
^nado-ecs-lb-[a-z]+-[a-z]+-[0-9]-[0-9]+\.[a-z]+-[a-z]+-[0-9]\.elb\.amazonaws\.com$ -- Yahoo
(\.|^)pavv\.co\.kr$ -- Smart TV (Samsung/Other)
^pixels?(\.|-[^.]*\.)[^.]+\.[^.]+ -- mmotti RegEx (needs three or more labels, so sites like pixels.com stay reachable)
^prod-elb-ats-[0-9]+\.[a-z]{2}-[a-z]+-[0-9]\.elb\.amazonaws\.com$ -- Yahoo
(^|\.)samsungcloudsolution\.net$ -- Smart TV (Samsung/Other)
(\.|^)samsungelectronics\.com$ -- Samsung Smart TV (Perflyst and HaGeZi lists block it too)
(\.|^)samsungqbe\.com$ -- Samsung Smart TV
(\.|^)samsungrm\.net$ -- Samsung Smart TV
(\.|^)shadowadcity\.com$ -- 1337x.to - Sneaky redirect domains that probably log your IP and any other information it gets from your browser sending a GET or POST request.
(\.|^)smartshare\.lgtvsdp\.com$ -- LG Smart TVs
^[a-z0-9]+\.ssm[1-2]?\.internet\.sony\.tv$ -- Sony Smart TV
^ssp-ats-prod-[a-z\-]+-[0-9]\.one-mobile-prod\.aws\.oath\.cloud$ -- Yahoo
^stat(s|istics)?[0-9]*[-_] -- stats/metrics (narrowed to avoid false positives)
(\.|^)steamcommurnily\.com$ -- Confirmed hacker website with malicious intent - DANGER
(\.|^)stickyadstv\.com\.akadns\.net$ -- Curseforge App Ads
(^|\.)telemetry[-_][a-z0-9] -- telemetry (narrowed to avoid false positives)
(\.|^)trafyield\.com$ -- 1337x.to - Sneaky redirect domains that probably log your IP and any other information it gets from your browser sending a GET or POST request.
(\.|^)tvinteractive\.tv$ -- Vizio Smart TV
^uplynk-beacon-newvpc-[0-9]+\.[a-z]{2}-[a-z]+-[0-9]\.elb\.amazonaws\.com$ -- Yahoo
(\.|^)usage\.trackjs\.com$ -- AdultTime
^v-[a-z0-9]+\.wc\.yahoodns\.net$ -- Yahoo
^[a-z]{2}-[a-z]{2}-[a-z]{2}\.ybp\.gysm\.yahoodns\.net$ -- Yahoo
