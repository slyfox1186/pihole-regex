# Regex patterns for domains

# Akamai CDN Ad Server
^.*\.akamai\.net$ -- Akamai CDN Ad Server

# Curseforge (Software program for gaming)
^ads\.stickyadstv\.com$ -- Curseforge Ads

# Twitch Video Ads
^.*\.cf1\.rackcdn\.com$ -- Twitch Video Ads
^.*\.ext-twitch\.tv$ -- Twitch Video Ads
^d[0-9]+.*\.cloudfront\.net$ -- Twitch Video Ads
^video-edge-(55b156.pdx01|6dca22.atl01|833564.atl01|8491b8.pdx01)\.abs\.hls\.ttvnw\.net$ -- Twitch Video Ads
^video-weaver.(atl01|jfk04)\.hls\.ttvnw\.net$ -- Twitch Video Ads

# Samsung Smart TV
(\.|^)internetat\.tv$ -- Samsung Smart TV
(\.|^)pavv\.co\.kr$ -- Samsung Smart TV
(\.|^)samsungelectronics\.com$ -- Samsung Smart TV
(\.|^)samsungqbe\.com$ -- Samsung Smart TV
(\.|^)samsungrm\.net$ -- Samsung Smart TV
^.*\.samsungcloudsolution\.(com|net)$ -- Samsung Smart TV

# Amazon
^ad\.amazon(aws|trust|zones|digicert|marketwatch|mzstatic|wp|yimg|youtube|ytimg|amzn)\.(com|to)$ -- Amazon
^ads\.amzn\.(com|to)$ -- Amazon

# LG Smart TV
(\.|^)ibs\.lgappstv\.com$ -- LG Smart TV
(\.|^)(lgsmartad|lgtvcommon)\.com$ -- LG Smart TV
(\.|^)rdx2\.lgtvsdp\.com$ -- LG Smart TV
(\.|^)smartshare\.lgtvsdp\.com$ -- LG Smart TV
^aic-(gfts|ngfts|op-lss|api|homeprv|nudge|rdl|recommend|sports|wiseconfig)\.(lge|lgthinq|lgtviot|lgtvcommon)\.com$ -- LG Smart TV
^images\.(pluto|redbox)\.(com|tv)$ -- LG Smart TV
^us\..*\.lgeapi\.com$ -- LG Smart TV

# QNAP Computers
^.*\.qnap\.com$ -- QNAP Computers

# Other Smart TVs
(\.|^)tvinteractive\.tv$ -- Other Smart TVs
^(api|auth|msg|unified)\.hismarttv\.com$ -- Other Smart TVs
^.*iad.*\.amazon\.com$ -- Amazon

# iTop VPN Telemetry
^(api|stats)\.itopvpn\.com$ -- iTop VPN Telemetry
^update\.filesupdating\.com$ -- iTop VPN Telemetry

# NordVPN Telemetry
^(applytics|client-api)\.nordvpn\.com$ -- NordVPN Telemetry

# Roblox
^rbx(cdn|trk)\.(com|plus)$ -- Roblox
^roblox\.(com|plus)$ -- Roblox

# Spotify
(\.|^)log[0-9]*\.spotify\.com$ -- Spotify
^pixel(-static)?\.spotify\.com$ -- Spotify

# Tinder App
^go?t?inder(s)?\.com$ -- Tinder App
^gs?p?a?r?k?s?t?inder(s)?\.com$ -- Tinder App
^tinder\.com$ -- Tinder App

# HBBTV
^hbbtv\.(3sat|kabeleins|qvc|rtl2|sat1|sixx|superrtl)\.de$ -- HBBTV

# Google Ads
^ads?\.google(video|\.com)$ -- Google Ads
^adwords\.(google|l\.google)\.com$ -- Google Ads

# Snapchat
^snap(-ads|chat|dev|kit)?\.(c|com|net)$ -- Snapchat
(\.|^)impala-media-production\.s3\.amazonaws\.com$ -- Snapchat
(\.|^)sc-cdn\.net$ -- Snapchat

# Yahoo
(\.|^)cs[0-9]+\.wpc\.thetacdn\.net$ -- Yahoo
^.*\.search\.yahoo\.com$ -- Yahoo
^.*\.yahoodns\.net$ -- Yahoo

# Pi-Hole Queries
^doh\.dns\.apple\.com$ -- Apple DoH Blocks Pi-Hole Queries Entirely

# IObit - Desktop Popup Advertisements
^(stats|store)\.iobit\.com$ -- IObit - Desktop Pop up Ads
^purchase(-iobit-com)?\.us-east-1\.elasticbeanstalk\.com$ -- IObit - Desktop Pop-up Ads

# CCleaner Telemetry Desktop App Spyware
^ccleaner\.tools\.avcdn\.net$ -- CCleaner Telemetry Desktop App Spyware

# AdultTime - Ads
^d1[86]rixkn5ruba\.cloudfront\.net$ -- AdultTime - Ads

# Topaz Labs Telemetry
^api\.topaz(-?(|labs))?\.com$

# Miscellaneous
^manifest\.googlevideo\.com$ -- Possibly the number one domain that serves YouTube Ads. We must block it.

# Bittorrent
(\.|^)lstartanalystconcepts\.org\.uk$ -- BitTorrent - Background Tracking

# Additional Patterns
(\.|^)((www|(w[0-9]\.)?web|media((-[a-z]{3}|\.[a-z]{4})[0-9]{1,2}-[0-9](\.|-)(cdn|fna))?)\.)?whatsapp\.(com|net)$ -- WhatsApp
(\.|^)[a-z0-9]+\.execute-api\.us-[a-z]+-[0-9]?\.amazonaws\.com$ -- AWS Apps
(\.|^)ad-score\.com$ -- Overwolf Desktop App (PC Games)
(\.|^)ahoravideo.*$ -- Suspected Virus Harboring Websites
(\.|^)antivirushub\.com$ -- Suspected Virus Harboring Websites
(\.|^)appsync-api\.us-[a-z]+-[0-9]?\.amazonaws\.com$ -- AWS Apps
(\.|^)bideo.*$ -- Suspected Virus Harboring Websites
(\.|^)buybuggle\.com$ -- Hacker website
(\.|^)client\.mchsi\.com$ -- BitTorrent - Background Tracking
(\.|^)deimos3\.apple\.com$ -- Apple
(\.|^)fairu.*$ -- Suspected Virus Harboring Websites
(\.|^)fake\.video\.url\.webm$ -- Overwolf Desktop App (PC Games)
(\.|^)filesupdating\.com$ -- iTop VPN
(\.|^)gammaentertainment\.com$ -- AdultTime
(\.|^)gardensuny\.com$ -- Hacker website
(\.|^)getbeamer\.com$ -- AdultTime
(\.|^)hokaclearances\.com$ -- Hacker website
(\.|^)lambda-url\.us-east-1\.on\.aws$ -- AdultTime
(\.|^)ok\.ru$ -- OK.ru
(\.|^)privatproxy.*$ -- Suspected Virus Harboring Websites
(\.|^)shadowadcity\.com$ -- Suspected Virus Harboring Websites
(\.|^)stickyadstv\.com\.akadns\.net$ -- Curseforge App Ads
(\.|^)trafyield\.com$ -- Suspected Virus Harboring Websites
(\.|^)usage\.trackjs\.com$ -- AdultTime
(\.|^)whatsapp-cdn-shv-[0-9]{2}-[a-z]{3}[0-9]\.fbcdn\.net$ -- WhatsApp
(\.|^)wmail.*$ -- Suspected Virus Harboring Websites
(\.|^)xyz$ -- BitTorrent
(\.|^)youtube-nocookie\.com$ -- YouTube
(^|\.)giraffic\.com$ -- Samsung TV
^[a-rt-z][a-z]{10,14}$ -- LG TV
^[a-z0-9]+\.ssm[1-2]?\.internet\.sony\.tv$ -- Sony Smart TV
^[a-z]+ad\.[a-z]+\.com\.edgesuite\.net$ -- Take out all ad servers in one go for master domain com.edgesuite.net
