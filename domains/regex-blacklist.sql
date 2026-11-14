^a-content-[a-z0-9]+-[0-9]+\.[a-z]{2}-[a-z]+-[0-9]\.elb\.amazonaws\.com$ -- a-content AWS load balancer pattern - No matches in the 2.17M-name test corpus on 2026-11-13
^aax(-[a-z0-9]+)*(\.[a-z0-9-]+)?\.amazon\.com$ -- Amazon aax hosts (aax-*.amazon.com) - Most of its 20 matches come from ad blocklists
^ads?\.[a-z0-9-]+\.com\.edgesuite\.net$ -- Ad hosts on Akamai edgesuite.net (ad. and ads. only, so Windows Update's adl.windows.com is not blocked)
^adim(age|g)s?[0-9]*[_.-] -- Generic rule - Blocks names that start with adimage or adimg
(\.|^)ad-score\.com$ -- ad-score.com - Seven lists block it, including HaGeZi Pro, EasyList, AdGuard DNS and Peter Lowe's
^adserver-.*\.amazonaws\.com$ -- Matches amazonaws.com names starting adserver- (the 14 corpus matches are load balancers)
^(.+[_.-])?adse?rv(er?|ice)?s?[0-9]*[_.-] -- Generic rule - Matches adserver-style name segments (adserv, adsrv, adservice, with plural and numbered forms) between dots, dashes or underscores
(^|\.)ad([sx][0-9]*|[0-9]+|system)[_.-]|(^|\.)adv[0-9]*([_-]|\.[^.]+\.[^.]+) -- Generic ad rule - ads/adx (+digits), ad+digits or adsystem before . - or _; adv (+digits) needs - or _ or two more labels
^adtrack(er|ing)?[0-9]*[_.-] -- Generic rule - Blocks names that start with adtrack/adtracker/adtracking
^advert(s|is(ing|ements?))?[0-9]*[_.-] -- Generic rule - Blocks names that start with advert, adverts or advertising
(^|\.)(ahoravideo|bideo|fairu|privatproxy|wmail)-(blog|cdn|chat|endpoint|schnellvpn)\.(com|xyz)$ -- ViperSoftX malware command servers - All 50 names its domain generator builds
^analytics?[_.-] -- Generic rule - Blocks names that start with analytic or analytics
(\.|^)antivirushub\.com$ -- antivirushub.com - Maintainer added it as a 1337x.to redirect domain; it resolved on 2026-11-13
^api\..*\.hismarttv\.com$ -- api.*.hismarttv.com hosts - Perflyst's Smart TV rules block them
(\.|^)buybuggle\.com$ -- buybuggle.com - Maintainer reported it as a malware site; DNS gave no answer on 2026-11-13
^(collect|usage)-(eu|us)-fy[0-9]+\.myhomescreen\.tv$ -- Panasonic Viera TV hosts collect-/usage-*.myhomescreen.tv - Perflyst blocks them
^count(ers?)?[0-9]*(\.|[_-][^.]*\.)[^.]+\.[^.]+ -- Generic rule - Blocks count/counter names with three or more labels (counter-strike.net still works)
(\.|^)deimos3\.apple\.com$ -- deimos3.apple.com - Apple host; a Pi-hole forum post lists it among Apple hosts to allow
^dms-[a-z0-9]+report\.wc\.yahoodns\.net$ -- Yahoo DNS name pattern dms-*report.wc.yahoodns.net - No matches in the 2.17M-name test corpus on 2026-11-13
^dns-[a-z0-9]+\.sombrero\.yahoo\.net$ -- Yahoo DNS name pattern dns-*.sombrero.yahoo.net - No matches in the 2.17M-name test corpus on 2026-11-13
^ds-beap[0-9]\.[a-z]{2}\.[a-z0-9]+\.yahoodns\.net$ -- Yahoo DNS name pattern ds-beap*.yahoodns.net - No matches in the 2.17M-name test corpus on 2026-11-13
^ds-global[0-9]\.l[0-9]\.search\.[a-z0-9]+\.yahoo\.com$ -- Yahoo search host pattern ds-global*.search.*.yahoo.com - No matches in the 2.17M-name test corpus on 2026-11-13
(\.|^)filesupdating\.com$ -- filesupdating.com - Maintainer labeled it iTop VPN; it resolved on 2026-11-13
(\.|^)gammaentertainment\.com$ -- gammaentertainment.com - Maintainer labeled it AdultTime
(\.|^)gardensuny\.com$ -- gardensuny.com - Maintainer reported it as malicious; DNS returned NXDOMAIN on 2026-11-13
(\.|^)getbeamer\.com$ -- getbeamer.com and its subdomains - Maintainer reported it on AdultTime; its gmetrics host is in a blocklist
(^|\.)giraffic\.com$ -- giraffic.com - Perflyst's Smart TV rules block it
(\.|^)hokaclearances\.com$ -- hokaclearances.com - Maintainer reported it as malicious; DNS returned NXDOMAIN on 2026-11-13
(\.|^)internetat\.tv$ -- internetat.tv - Perflyst's Smart TV rules block it
(\.|^)lgsmartad\.com$ -- lgsmartad.com - Perflyst's Smart TV rules and nine lists, including HaGeZi's LG list, block it
(^|\.)lgtvcommon\.com$ -- lgtvcommon.com - Perflyst's Smart TV rules block it; guide-data and LG Channels app launch hosts are allowed in regex-whitelist
(\.|^)log[0-9]*\.spotify\.com$ -- Matches log.spotify.com, log plus any digits under spotify.com, and subdomains of those hosts
(\.|^)lstartanalystconcepts\.org\.uk$ -- lstartanalystconcepts.org.uk - Maintainer labeled it BitTorrent background tracking; DNS returned NXDOMAIN on 2026-11-13
^mads\. -- Generic rule - Blocks names that start with mads.
^nado-ecs-lb-[a-z]+-[a-z]+-[0-9]-[0-9]+\.[a-z]+-[a-z]+-[0-9]\.elb\.amazonaws\.com$ -- nado-ecs-lb AWS load balancer pattern - No matches in the 2.17M-name test corpus on 2026-11-13
(\.|^)pavv\.co\.kr$ -- pavv.co.kr (Samsung) - infolink.pavv.co.kr is allowed for the app store and sign-in
^pixels?(\.|-[^.]*\.)[^.]+\.[^.]+ -- Generic rule - Blocks pixel/pixels names with three or more labels (pixels.com still works)
^prod-elb-ats-[0-9]+\.[a-z]{2}-[a-z]+-[0-9]\.elb\.amazonaws\.com$ -- prod-elb-ats AWS load balancer pattern - No matches in the 2.17M-name test corpus on 2026-11-13
(^|\.)samsungcloudsolution\.net$ -- samsungcloudsolution.net (Samsung) - Exact allows exempt configprd and lcprd1.samsungcloudsolution.net
(\.|^)samsungelectronics\.com$ -- samsungelectronics.com - Perflyst's Samsung TV rules block it
(\.|^)samsungqbe\.com$ -- samsungqbe.com and its subdomains - Blocks Samsung service hosts; TV Plus and one service host are allowed
(\.|^)samsungrm\.net$ -- samsungrm.net - Perflyst's Samsung TV rules block it
(\.|^)shadowadcity\.com$ -- shadowadcity.com - Maintainer labeled it a 1337x.to redirect; DNS returned NXDOMAIN on 2026-11-13
(\.|^)smartshare\.lgtvsdp\.com$ -- smartshare.lgtvsdp.com - Perflyst's Smart TV rules block it
^[a-z0-9]+\.ssm[1-2]?\.internet\.sony\.tv$ -- Sony TV hosts under ssm*.internet.sony.tv (the ssm hosts themselves stay reachable)
^ssp-ats-prod-[a-z\-]+-[0-9]\.one-mobile-prod\.aws\.oath\.cloud$ -- oath.cloud ssp-ats-prod pattern - No matches in the 2.17M-name test corpus on 2026-11-13
^stat(s|istics)?[0-9]*[-_] -- Generic rule - Blocks names starting stat-, stats- or statistics-
(\.|^)steamcommurnily\.com$ -- steamcommurnily.com - Maintainer reported it as malicious; DNS returned NXDOMAIN on 2026-11-13
(\.|^)stickyadstv\.com\.akadns\.net$ -- FreeWheel StickyAds Akamai name (stickyadstv.com.akadns.net)
(^|\.)telemetry[-_][a-z0-9] -- Generic rule - Blocks telemetry- and telemetry_ names
(\.|^)trafyield\.com$ -- trafyield.com - Five lists block it, including HaGeZi Pro and HaGeZi TIF
(\.|^)tvinteractive\.tv$ -- tvinteractive.tv - Perflyst's Smart TV rules block it
^uplynk-beacon-newvpc-[0-9]+\.[a-z]{2}-[a-z]+-[0-9]\.elb\.amazonaws\.com$ -- uplynk-beacon AWS load balancer pattern - No matches in the 2.17M-name test corpus on 2026-11-13
(\.|^)usage\.trackjs\.com$ -- TrackJS usage beacon
^v-[a-z0-9]+\.wc\.yahoodns\.net$ -- Yahoo DNS name pattern v-*.wc.yahoodns.net - No matches in the 2.17M-name test corpus on 2026-11-13
^[a-z]{2}-[a-z]{2}-[a-z]{2}\.ybp\.gysm\.yahoodns\.net$ -- Yahoo DNS name pattern xx-xx-xx.ybp.gysm.yahoodns.net - No matches in the 2.17M-name test corpus on 2026-11-13
