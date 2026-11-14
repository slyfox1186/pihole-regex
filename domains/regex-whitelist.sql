(\.|^)1drv\.ms$ -- 1drv.ms and its subdomains
^(account|accts|catalog|entitlement|eulatracking|lightswitch|priceengine)-public-service-prod[0-9]*\.(ak|ol)\.epicgames\.com$ -- Epic Games hosts *-public-service-prod.ak/ol.epicgames.com for account, accts, catalog, entitlement, eulatracking, lightswitch and priceengine
(\.|^)messenger\.com$ -- messenger.com and its subdomains - Pi-hole users list Messenger hosts for Facebook Messenger
^(accounts|download|entitlement-public-service-prod\.ak|fg-matchmaking-public-service-live-c\.ol|graphql|launcher-public-service-prod06\.ol)\.epicgames\.com$ -- Epic Games hosts accounts, download, entitlement-public-service-prod.ak, fg-matchmaking, graphql and launcher
^ads-[a-z0-9-]+\.aylanetworks\.com$ -- Ayla Networks smart-home IoT cloud - ads-* device hosts - Caught by the ad regex
^(affiliate|app|id|id-cdn)\.twitch\.tv$ -- Twitch hosts affiliate, app, id and id-cdn.twitch.tv
^(aic|eic|kic|ruc)\.service\.lgtvcommon\.com$|^(aic|eic|kic)\.cdpsvc\.lgtvcommon\.com$ -- LG TV hosts aic/eic/kic/ruc.service and aic/eic/kic.cdpsvc.lgtvcommon.com - HaGeZi #309: aic hosts carry channel guide data
^((www|drivers|download|account|community)\.)?amd\.com$ -- AMD - amd.com and its www, drivers, download, account and community hosts
^(api\.flightproxy|authsvc|chatsvcagg|config|go\.trouter|presence)\.teams\.microsoft\.com$ -- Microsoft Teams hosts (*.teams.microsoft.com, required by Microsoft 365): flightproxy, authsvc, chatsvcagg, config, trouter, presence
^(appleid|apps|audiocontentdownload|bpapi|business|captive|certs|configuration|crl|cssubmissions|deviceenrollment|diagassets|fba|gc|gdmf|gg|gs|gsa|gsp1|humb|identity|idmsa|ig|iprofiles|itunes|mdmenrollment|mesu|oscdn|osrecovery|ppq|radarsubmissions|school|serverstatus|skl|suconfig|sw(cdn|dist|download|scan)|sylvan|tbsc|valid|www|axm-app|deviceservices-external|gnf-mdn|gnf-mr|lcdn-(locator|registration)|sq-device|time(-ios|-macos)?|xp)\.apple\.com$ -- Apple - 54 apple.com hosts, most in Apple's network requirements (software updates, captive portal check, time, enrollment)
(\.|^)apple-(cloudkit|livephotoskit)\.com$ -- Apple CloudKit and Live Photos kit domains (apple-cloudkit.com, apple-livephotoskit.com)
^apps\.bdimg\.(com|jomodns\.com)$ -- apps.bdimg.com and apps.bdimg.jomodns.com
^(apresolve|dealer|embed|global-dealer-ssl|login5|market|mobile-ap|open|play|spclient\.wg)\.spotify\.com$ -- Spotify hosts apresolve, dealer, embed, global-dealer-ssl, login5, market, mobile-ap, open, play and spclient.wg.spotify.com
^(cert\.mgt|device\.auth|eds|help\.ui|licensing|notify|title\.(auth|mgt)|www|xflight|xkms|xsts\.auth)\.xboxlive\.com$ -- Twelve xboxlive.com hosts - The Pi-hole forum lists them as required for full Xbox Live functionality
^(audio4-fa|daily-mix|dailymix-images|download|encore|i|lineup-images|newjams-images|t|upgrade)\.scdn\.co$ -- Spotify scdn.co hosts (audio4-fa, daily-mix, dailymix-images, download, encore, i, lineup-images, newjams-images, t, upgrade)
^(aws|det-ta-g7g|todo-ta-g7g)\.amazon\.com$|^cognito-identity\.us-east-1\.amazonaws\.com$ -- Amazon hosts aws, det-ta-g7g and todo-ta-g7g.amazon.com (anudeep lists the last two for Kindle) and cognito-identity (AWS authentication)
^(axm-adm-[a-z0-9-]+|enroll)\.apple\.com$ -- Apple hosts axm-adm-*.apple.com and enroll.apple.com
^(bam-sdk-configs|config-cd-dmgz)\.bamgrid\.com$ -- bamgrid.com hosts bam-sdk-configs and config-cd-dmgz - Used on the maintainer's network
^(b-api|instagram\.c10r)\.facebook\.com$ -- Facebook hosts b-api.facebook.com and instagram.c10r.facebook.com - Listed in community allowlists
^(benchmarks|commons|empoweringtrust|support\.benchmarks|www)\.ul\.com(\.cdn\.cloudflare\.net)?$ -- Five ul.com hosts (benchmarks, support.benchmarks, www and two more) plus their Cloudflare CNAMEs
^(blog|business|careers|contests|dev|email|insights|meta|talent|www\.careers)\.stackoverflow\.com$ -- Stack Overflow hosts blog, business, careers, contests, dev, email, insights, meta, talent and www.careers
^(blog|community(-cdn|-staging)?|d-cloudflare|docs|downloads(-staging)?|et|guide|help|learn|models(-r2)?)\.topazlabs\.com$ -- Topaz Labs hosts (blog, community, docs, downloads, guide, help, learn, models and others)
^(calendar|dns|docs|home|inbox|clients[1-6]?|mail|meet|pay(|ments)|photos|sites|time|wallet|workspace|www)\.google\.com$ -- Google hosts calendar, dns, docs, home, inbox, clients, mail, meet, pay, photos, sites, time, wallet, workspace and www.google.com
^(alt[0-9]-)?mtalk\.google\.com$ -- Google push notifications (mtalk.google.com and alt0-9-mtalk) - Pi-hole users list mtalk for Android app push
^cdn\.(datatables\.net|discordapp\.com|embed\.ly|embedly\.com|materialdesignicons\.com|mathjax\.org|plyr\.io|signal\.org)$ -- cdn. hosts of datatables.net, discordapp.com, embed.ly, embedly.com, materialdesignicons.com, mathjax.org, plyr.io and signal.org
^(cdn\.embed\.ly|cdn\.jsdelivr\.net|cdnjs\.loli\.net)\.cdn\.cloudflare\.net$ -- Cloudflare CNAME names of cdn.embed.ly, cdn.jsdelivr.net and cdnjs.loli.net
^cdnjs\.(cloudflare\.com|loli\.net)$ -- cdnjs.cloudflare.com and its China mirror cdnjs.loli.net - A tested jQuery file from the mirror matched the official copy
^(cdn-mobile\.api|images|players|silo|siloh|stitcher)\.pluto\.tv$ -- Pluto TV hosts cdn-mobile.api, images, players, silo, siloh and stitcher.pluto.tv
^(winatp-gw-neu|windows)\.microsoft\.com$ -- Microsoft hosts winatp-gw-neu and windows.microsoft.com
^(client\.wns|edge\.activity)\.windows\.com$ -- Windows hosts client.wns and edge.activity.windows.com (Microsoft lists edge.activity)
^(cloudsync-prod|reddit-uploaded-media|seedbox-react-infra|ubisoft-uplay-savegames|whispersystems-textsecure-attachments)\.s3(-accelerate)?\.amazonaws\.com$ -- Five Amazon S3 buckets incl. cloudsync-prod (Origin save sync) and whispersystems-textsecure-attachments (listed under Signal)
^code\.(bildstatic\.de|createjs\.com|jquery\.com)$ -- code.bildstatic.de, code.createjs.com and code.jquery.com
^((www|m|web|static|graph|b-graph|mqtt-mini|edge-mqtt|upload|connect)\.)?facebook\.com$|^connect\.facebook\.net$ -- Facebook - facebook.com, its www, m, web, static, graph, b-graph, mqtt, upload and connect hosts, and connect.facebook.net
^connectivitycheck\.(android|gstatic)\.com$ -- Android internet connectivity check
^crl[3-4]\.digicert\.com$ -- DigiCert certificate revocation lists (CRL) - Apple lists them for certificate validation
^(csp|devicelistenerprod)\.microsoft\.com$ -- Microsoft hosts csp and devicelistenerprod.microsoft.com - Purpose unverified
^d(27xxe7juh1us6|2gatte9o95jao|3a3ewgd1iewwz|3ag4hukkh62yn|83eunklitikj)\.cloudfront\.net$ -- Five CloudFront hosts - The Pi-hole forum lists one for Signal; the rest are unverified
^(app|meta|pubsub|status|tvdb2|www)\.plex\.tv$|^pubsub\.plex\.bz$ -- Plex hosts app, meta, pubsub, status, tvdb2 and www.plex.tv, and pubsub.plex.bz
(\.|^)dataplicity\.com$ -- Dataplicity - Remote access to Raspberry Pi and other devices (dataplicity.com and subdomains)
^(devimages|xp|playgrounds?(-assets)?)-cdn\.apple\.com$ -- Apple hosts devimages-cdn (Xcode components), xp-cdn (content caching reporting) and Swift Playground hosts (playground- and playgrounds- spellings)
^(oops|www)\.redditmedia\.com$|^www\.redditstatic\.com$|^reddit\.map\.fastly\.net$ -- Reddit hosts oops and www.redditmedia.com, www.redditstatic.com and reddit.map.fastly.net
^(disney\.(api|connections|content|images|playback)\.edge|playback-certs)\.bamgrid\.com$ -- bamgrid.com hosts disney.api, connections, content, images and playback edge, and playback-certs - Used heavily on the maintainer's network
^[a-z0-9]{10}(-dsn)?\.algolia\.net$|^[a-z0-9]{10}-[1-3]\.algolianet\.com$ -- Algolia hostnames: 10 alphanumeric characters with .algolia.net or -dsn.algolia.net, or -1 to -3.algolianet.com
^(download\.developer|ns\.itunes|static\.ips|vpp\.itunes)\.apple\.com$ -- Apple hosts download.developer (Xcode components), ns.itunes, static.ips and vpp.itunes.apple.com
^[0-6]-edge-chat\.facebook\.com$ -- Facebook hosts 0- to 6-edge-chat.facebook.com - Listed in anudeep's optional allowlist
^(edge|fs|msedge\.api\.cdp|officecdnmac|officeclient|support|teams|vlscppe|whiteboard|www)\.microsoft\.com$ -- Microsoft hosts edge, fs, msedge.api.cdp, officecdnmac, officeclient, support, teams, vlscppe, whiteboard and www.microsoft.com
^europe\.(cp\.wd|smartscreen(-prod|))\.microsoft\.com$ -- Microsoft hosts europe.cp.wd, europe.smartscreen and europe.smartscreen-prod.microsoft.com
(\.|^)gammacdn\.com$ -- gammacdn.com and its subdomains - Maintainer labeled it Gamma Entertainment (AdultTime) media
^(github\.com|github\.io|github\.githubassets\.com)$ -- GitHub - github.com, github.io and github.githubassets.com
^gsp-ssl\.ls\.apple\.com$|^gsp-ssl\.ls-apple\.com\.akadns\.net$ -- Apple gsp-ssl.ls.apple.com and its Akamai name - Pi-hole users list it for the iOS Weather app
^hbbtv\.(prosieben|redbutton|zdf|ard)\.de$ -- HbbTV hosts of ProSieben, redbutton.de, ZDF and ARD (Perflyst lists three of them)
(^|\.)itunes(-apple)?\.com(\.akadns\.net)?$ -- itunes.com, itunes-apple.com and their Akamai names (Apple)
(\.|^)lencr\.org$ -- Let's Encrypt (lencr.org) - Data referenced inside its certificates
(\.|^)linuxtracker\.org$ -- Linux Tracker - Torrent site for Linux distributions
(\.|^)mee6\.xyz$ -- MEE6 Discord bot site (mee6.xyz)
^m\.(hotmail\.com|reddit\.com|reuters\.com|twitch\.tv|youtube\.com)$ -- Mobile sites m.hotmail.com, m.reddit.com, m.reuters.com, m.twitch.tv and m.youtube.com
^(www\.)?minecraft\.net$ -- Minecraft website
^((mobile|www|upload)\.)?twitter\.com$ -- twitter.com and its mobile, www and upload hosts - Pi-hole users list them for Twitter
^(www\.)?(myqnapcloud|qnap)\.com$ -- qnap.com and myqnapcloud.com with their www hosts
^(www\.)?no-ip\.com$ -- No-IP website (no-ip.com and www)
^ns[12]\.dropbox\.com$ -- Dropbox hosts ns1.dropbox.com and ns2.dropbox.com - Listed in community allowlists
^(oauthaccountmanager|www|youtubei)\.googleapis\.com$ -- Google hosts www, youtubei and oauthaccountmanager.googleapis.com - Pi-hole users list them for YouTube on iOS
^ocsp[0-9]*\.(apple|digicert|verisign)\.com$|^ocsp\.entrust\.net$ -- Certificate status (OCSP) hosts of Apple, DigiCert, VeriSign and Entrust
^orderprocessor.*\.ol\.epicgames\.com$ -- Epic Games orderprocessor* hosts - Maintainer reported they are needed to buy games
^otnprd[0-9]+\.samsungcloudsolution\.net$ -- Samsung TV otnprd* hosts - Perflyst: required for software update
^outlook\.(live|office(|365))\.com$ -- Outlook web mail (outlook.live.com, outlook.office.com, outlook.office365.com)
^payment.*\.ol\.epicgames\.com$ -- Epic Games payment* hosts - Maintainer reported they are needed for payments
(\.|^)redd\.it$ -- redd.it and its subdomains
^((www|old|new|oauth|gql|gql-fed|gateway)\.)?reddit\.com$ -- Reddit - reddit.com and its www, old, new, oauth, gql, gql-fed and gateway hosts
(\.|^)robvanderwoude\.com$ -- Rob van der Woude's website (robvanderwoude.com)
(\.|^)samsungcloudcdn\.com$ -- samsungcloudcdn.com - Perflyst: blocking otn.samsungcloudcdn.com prevents Samsung TV updates
(\.|^)samsungotn\.net$ -- Samsung TV - System update check (samsungotn.net)
^scontent-(atl3|mia3)-1\.xx\.fbcdn\.net$ -- Facebook hosts scontent-atl3-1 and scontent-mia3-1.xx.fbcdn.net - Pi-hole users list both for Facebook
(\.|^)symcb\.com$ -- symcb.com and its subdomains - Microsoft 365 lists *.symcb.com as a required endpoint
^[a-z]\.thumbs\.redditmedia\.com$ -- Reddit single-letter thumbs hosts (a-z.thumbs.redditmedia.com)
(\.|^)twimg\.com$ -- twimg.com and its subdomains - Listed in anudeep's allowlist
(\.|^)unraid\.net$ -- Unraid - unraid.net and its subdomains
(\.|^)wa\.me$ -- wa.me and its subdomains - Pi-hole users list wa.me for WhatsApp
^whatsapp-cdn-shv-[0-9]{2}-[a-z]{3}[0-9]\.fbcdn\.net$ -- fbcdn.net hosts named whatsapp-cdn-shv-*
(\.|^)windowsupdate\.com$ -- Windows Update (windowsupdate.com and its subdomains)
^(www\.|go\.)?microsoft\.com$|^(www\.)?windows\.com$ -- Microsoft and Windows main sites and go.microsoft.com links
^((www|(w[0-9]\.)?web|media((-[a-z]{3}|\.[a-z]{4})[0-9]{1,2}-[0-9](\.|-)(cdn|fna))?)\.)?whatsapp\.(com|net)$ -- WhatsApp - whatsapp.com and whatsapp.net with www, web and media hosts
^(aic|eic|kic)\.(cdplauncher|lgchhomeapp)\.lgtvcommon\.com$ -- LG Channels app launch hosts (aic reported to HaGeZi) and their eic/kic regional names - Exceptions to the lgtvcommon.com block rule
