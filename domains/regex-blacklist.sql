^aax(-[a-z0-9]+)*(\.[a-z0-9-]+)?\.amazon\.com$ -- Amazon aax hosts (aax-*.amazon.com) - Most of its 20 matches come from ad blocklists
^ads?\.[a-z0-9-]+\.com\.edgesuite\.net$ -- Ad hosts on Akamai edgesuite.net (ad. and ads. only, so Windows Update's adl.windows.com is not blocked)
^adim(age|g)s?[0-9]*[_.-] -- Generic rule - Blocks names that start with adimage or adimg
^(.+[_.-])?adse?rv(er?|ice)?s?[0-9]*[_.-] -- Generic rule - Matches adserver-style name segments (adserv, adsrv, adservice, with plural and numbered forms) between dots, dashes or underscores
(^|\.)ad([sx][0-9]*|[0-9]+|system)[_.-]|(^|\.)adv[0-9]*([_-]|\.[^.]+\.[^.]+) -- Generic ad rule - ads/adx (+digits), ad+digits or adsystem before . - or _; adv (+digits) needs - or _ or two more labels
^adtrack(er|ing)?[0-9]*[_.-] -- Generic rule - Blocks names that start with adtrack/adtracker/adtracking
^advert(s|is(ing|ements?))?[0-9]*[_.-] -- Generic rule - Blocks names that start with advert, adverts or advertising
(^|\.)(ahoravideo-(blog|cdn)\.com|bideo-(cdn|schnellvpn)\.com|fairu-(chat|endpoint|schnellvpn)\.com|fairu-schnellvpn\.xyz|privatproxy-(chat|schnellvpn)\.com|wmail-blog\.com)$ -- ViperSoftX malware command servers - The 11 of its 50 generated names whose subdomains no adlist blocks
^analytics?[_.-] -- Generic rule - Blocks names that start with analytic or analytics
(\.|^)antivirushub\.com$ -- antivirushub.com - Maintainer added it as a 1337x.to redirect domain; it resolved on 2026-11-13
^api\..*\.hismarttv\.com$ -- api.*.hismarttv.com hosts - Perflyst's Smart TV rules block them
^(collect|usage)-(eu|us)-fy[0-9]+\.myhomescreen\.tv$ -- Panasonic Viera TV hosts collect-/usage-*.myhomescreen.tv - Perflyst blocks them
(\.|^)filesupdating\.com$ -- filesupdating.com - Maintainer labeled it iTop VPN; it resolved on 2026-11-13
(\.|^)internetat\.tv$ -- internetat.tv - Perflyst's Smart TV rules block it
(^|\.)lgtvcommon\.com$ -- lgtvcommon.com - Perflyst's Smart TV rules block it; guide-data and LG Channels app launch hosts are allowed in regex-whitelist
(\.|^)log[0-9]*\.spotify\.com$ -- Matches log.spotify.com, log plus any digits under spotify.com, and subdomains of those hosts
(\.|^)pavv\.co\.kr$ -- pavv.co.kr (Samsung) - infolink.pavv.co.kr is allowed for the app store and sign-in
(^|\.)samsungcloudsolution\.net$ -- samsungcloudsolution.net (Samsung) - Exact allows exempt configprd and lcprd1.samsungcloudsolution.net
(\.|^)samsungelectronics\.com$ -- samsungelectronics.com - Perflyst's Samsung TV rules block it
(\.|^)samsungqbe\.com$ -- samsungqbe.com and its subdomains - Blocks Samsung service hosts; TV Plus and one service host are allowed
(\.|^)samsungrm\.net$ -- samsungrm.net - Perflyst's Samsung TV rules block it
(\.|^)smartshare\.lgtvsdp\.com$ -- smartshare.lgtvsdp.com - Perflyst's Smart TV rules block it
^[a-z0-9]+\.ssm[1-2]?\.internet\.sony\.tv$ -- Sony TV hosts under ssm*.internet.sony.tv (the ssm hosts themselves stay reachable)
^stat(s|istics)?[0-9]*[-_] -- Generic rule - Blocks names starting stat-, stats- or statistics-
(^|\.)telemetry[-_][a-z0-9] -- Generic rule - Blocks telemetry- and telemetry_ names
(\.|^)tvinteractive\.tv$ -- tvinteractive.tv - Perflyst's Smart TV rules block it
^[a-z]{2}-[a-z]{2}-[a-z]{2}\.ybp\.gysm\.yahoodns\.net$ -- Yahoo DNS name pattern xx-xx-xx.ybp.gysm.yahoodns.net - No matches in the 2.17M-name test corpus on 2026-11-13
