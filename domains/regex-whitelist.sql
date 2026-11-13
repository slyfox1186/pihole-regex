(\.|^)1drv\.ms$ -- Microsoft OneDrive short links
^(account|accts|catalog|entitlement|eulatracking|lightswitch|priceengine)-public-service-prod[0-9]*\.(ak|ol)\.epicgames\.com$ -- Epic Games - Sign-in, game library, entitlements and store prices
(\.|^)messenger\.com$ -- Facebook Messenger
^(accounts|download|entitlement-public-service-prod\.ak|fg-matchmaking-public-service-live-c\.ol|graphql|launcher-public-service-prod06\.ol)\.epicgames\.com$ -- Epic Games - Sign-in, downloads, launcher and Fortnite matchmaking
^ads-[a-z0-9-]+\.aylanetworks\.com$ -- Ayla Networks IoT device service (Shark, Fujitsu FGLair, Bradford White and other connected appliances) - Caught by the ad regex
^(affiliate|app|id|id-cdn)\.twitch\.tv$ -- Twitch - Sign-in and the creator affiliate dashboard
^(aic|eic|kic|ruc)\.service\.lgtvcommon\.com$|^(aic|eic|kic)\.cdpsvc\.lgtvcommon\.com$ -- LG Smart TV - Broadcast and internet channel guide data in every region (HaGeZi #309 and #1216)
^((www|drivers|download|account|community)\.)?amd\.com$ -- AMD - Main site, driver downloads and support community
^(api\.flightproxy|authsvc|chatsvcagg|config|go\.trouter|presence)\.teams\.microsoft\.com$ -- Microsoft Teams - Sign-in, chat, calls and presence
^(appleid|apps|audiocontentdownload|bpapi|business|captive|certs|configuration|crl|cssubmissions|deviceenrollment|diagassets|fba|gc|gdmf|gg|gs|gsa|gsp1|humb|identity|idmsa|ig|iprofiles|itunes|mdmenrollment|mesu|oscdn|osrecovery|ppq|radarsubmissions|school|serverstatus|skl|suconfig|sw(cdn|dist|download|scan)|sylvan|tbsc|valid|www|axm-app|deviceservices-external|gnf-mdn|gnf-mr|lcdn-(locator|registration)|sq-device|time(-ios|-macos)?|xp)\.apple\.com$ -- Apple - Apple ID, App Store, device enrollment, software updates, captive portal and time servers
(\.|^)apple-(cloudkit|livephotoskit)\.com$ -- Apple - CloudKit app data and Live Photos
^apps\.bdimg\.(com|jomodns\.com)$ -- Baidu static file CDN and its CNAME target
^(apresolve|dealer|embed|global-dealer-ssl|login5|market|mobile-ap|open|play|spclient\.wg)\.spotify\.com$ -- Spotify - Sign-in, playback, the web player and embeds
^(cert\.mgt|device\.auth|eds|help\.ui|licensing|notify|title\.(auth|mgt)|www|xflight|xkms|xsts\.auth)\.xboxlive\.com$ -- Xbox Live - Sign-in, licensing and cloud saves
^(audio4-fa|daily-mix|dailymix-images|download|encore|i|lineup-images|newjams-images|t|upgrade)\.scdn\.co$ -- Spotify - Artwork, audio and web player files
^(aws|det-ta-g7g|todo-ta-g7g)\.amazon\.com$|^cognito-identity\.us-east-1\.amazonaws\.com$ -- Amazon - AWS site, Echo and Fire TV device services, app sign-in
^(axm-adm-[a-z0-9-]+|enroll)\.apple\.com$ -- Apple Business Manager and device enrollment
^(bam-sdk-configs|config-cd-dmgz)\.bamgrid\.com$ -- Disney+ - App configuration (Roku and iPhone)
^(b-api|instagram\.c10r)\.facebook\.com$ -- Facebook and Instagram app APIs
^(benchmarks|commons|empoweringtrust|support\.benchmarks|www)\.ul\.com(\.cdn\.cloudflare\.net)?$ -- UL Benchmarks - 3DMark results and downloads
^(blog|business|careers|contests|dev|email|insights|meta|talent|www\.careers)\.stackoverflow\.com$ -- Stack Overflow
^(blog|community(-cdn|-staging)?|d-cloudflare|docs|downloads(-staging)?|et|guide|help|learn|models(-r2)?)\.topazlabs\.com$ -- Topaz Labs - Downloads, models, docs and community
^(calendar|dns|docs|home|inbox|clients[1-6]?|mail|meet|pay(|ments)|photos|sites|time|wallet|workspace|www)\.google\.com$ -- Google - Search, Gmail, Calendar, Docs, Meet, Photos and Pay (developer domains not included)
^(alt[0-9]-)?mtalk\.google\.com$ -- Android push notifications (Firebase Cloud Messaging)
^cdn\.(datatables\.net|discordapp\.com|embed\.ly|embedly\.com|materialdesignicons\.com|mathjax\.org|plyr\.io|signal\.org)$ -- Public CDNs for site libraries, Discord and Signal
^(cdn\.embed\.ly|cdn\.jsdelivr\.net|cdnjs\.loli\.net)\.cdn\.cloudflare\.net$ -- Cloudflare CNAME targets of the Embedly, jsDelivr and cdnjs mirror CDNs
^cdnjs\.(cloudflare\.com|loli\.net)$ -- cdnjs JavaScript library CDN and its China mirror
^(cdn-mobile\.api|images|players|silo|siloh|stitcher)\.pluto\.tv$ -- Pluto TV streaming
^(winatp-gw-neu|windows)\.microsoft\.com$ -- Microsoft Defender for Endpoint (Europe gateway) and windows.microsoft.com
^(client\.wns|edge\.activity)\.windows\.com$ -- Windows push notifications and activity history
^(cloudsync-prod|reddit-uploaded-media|seedbox-react-infra|ubisoft-uplay-savegames|whispersystems-textsecure-attachments)\.s3(-accelerate)?\.amazonaws\.com$ -- Amazon S3 buckets for Reddit uploads, Ubisoft cloud saves, Signal attachments and others
^code\.(bildstatic\.de|createjs\.com|jquery\.com)$ -- jQuery, CreateJS and Bild.de script CDNs
^((www|m|web|static|graph|b-graph|mqtt-mini|edge-mqtt|upload|connect)\.)?facebook\.com$|^connect\.facebook\.net$ -- Facebook - Site, apps, chat and Facebook Login (connect.facebook.net also serves the Facebook Pixel)
^connectivitycheck\.(android|gstatic)\.com$ -- Android internet connectivity check
^crl[3-4]\.digicert\.com$ -- DigiCert certificate revocation lists
^(csp|devicelistenerprod)\.microsoft\.com$ -- Microsoft - Windows services kept from earlier releases
^d(27xxe7juh1us6|2gatte9o95jao|3a3ewgd1iewwz|3ag4hukkh62yn|83eunklitikj)\.cloudfront\.net$ -- CloudFront hosts for non-ad services kept from earlier releases
^(app|meta|pubsub|status|tvdb2|www)\.plex\.tv$|^pubsub\.plex\.bz$ -- Plex Media Server
(\.|^)dataplicity\.com$ -- Dataplicity - Remote shell for Raspberry Pi
^(devimages|xp|playgrounds(-assets)?)-cdn\.apple\.com$ -- Apple - Developer site images, xp-cdn and Swift Playgrounds downloads
^(oops|www)\.redditmedia\.com$|^www\.redditstatic\.com$|^reddit\.map\.fastly\.net$ -- Reddit - Site assets and its Fastly CDN
^(disney\.(api|connections|content|images|playback)\.edge|playback-certs)\.bamgrid\.com$ -- Disney+ - API, images and playback (Roku and iPhone)
^[a-z0-9]{10}(-dsn)?\.algolia\.net$|^[a-z0-9]{10}-[1-3]\.algolianet\.com$ -- Algolia search API (AdultTime and many site search boxes)
^(download\.developer|ns\.itunes|static\.ips|vpp\.itunes)\.apple\.com$ -- Apple - Developer downloads, iTunes, network diagnostics and Volume Purchase
^[0-6]-edge-chat\.facebook\.com$ -- Facebook Messenger chat servers
^(edge|fs|msedge\.api\.cdp|officecdnmac|officeclient|support|teams|vlscppe|whiteboard|www)\.microsoft\.com$ -- Microsoft - Edge, Office, Teams, Whiteboard, support and main site
^europe\.(cp\.wd|smartscreen(-prod|))\.microsoft\.com$ -- Microsoft Defender SmartScreen and cloud protection (Europe)
(\.|^)gammacdn\.com$ -- Gamma Entertainment (AdultTime) media CDN
^(github\.com|github\.io|github\.githubassets\.com)$ -- GitHub
^gsp-ssl\.ls\.apple\.com$|^gsp-ssl\.ls-apple\.com\.akadns\.net$ -- Apple Maps and location services
^hbbtv\.(prosieben|redbutton|zdf|ard)\.de$ -- HbbTV red-button services for German broadcasters (smart TVs)
(^|\.)itunes(-apple)?\.com(\.akadns\.net)?$ -- Apple iTunes and Apple Music
(\.|^)lencr\.org$ -- Let's Encrypt certificate status and revocation lists
(\.|^)linuxtracker\.org$ -- Linux Tracker - BitTorrent tracker for Linux distributions
(\.|^)mee6\.xyz$ -- MEE6 Discord bot dashboard
^m\.(hotmail\.com|reddit\.com|reuters\.com|twitch\.tv|youtube\.com)$ -- Mobile sites for phones and tablets
^(www\.)?minecraft\.net$ -- Minecraft
^((mobile|www|upload)\.)?twitter\.com$ -- X, formerly Twitter
^(www\.)?(myqnapcloud|qnap)\.com$ -- QNAP NAS - Required for myQNAPcloud to work fully
^(www\.)?no-ip\.com$ -- No-IP dynamic DNS provider site
^ns[12]\.dropbox\.com$ -- Dropbox name servers
^(oauthaccountmanager|www|youtubei)\.googleapis\.com$ -- YouTube app API and Google account sign-in
^ocsp[0-9]*\.(apple|digicert|verisign)\.com$|^ocsp\.entrust\.net$ -- Certificate status checks (OCSP) for Apple, DigiCert, VeriSign and Entrust
^orderprocessor.*\.ol\.epicgames\.com$ -- Epic Games - Required to buy games on Windows
^otnprd[0-9]+\.samsungcloudsolution\.net$ -- Samsung Smart TV - Software updates (Perflyst)
^outlook\.(live|office(|365))\.com$ -- Outlook web mail
^payment.*\.ol\.epicgames\.com$ -- Epic Games - Required for payments to process
(\.|^)redd\.it$ -- Reddit images, video and short links
^((www|old|new|oauth|gql|gql-fed|gateway)\.)?reddit\.com$ -- Reddit (ads., pixel., events. and d. stay blocked as trackers)
(\.|^)robvanderwoude\.com$ -- Rob van der Woude - Scripting tutorials for many languages
(\.|^)samsungcloudcdn\.com$ -- Samsung Smart TV - Updates and app downloads (Perflyst)
(\.|^)samsungotn\.net$ -- Samsung Smart TV - System update check (Perflyst)
^scontent-(atl3|mia3)-1\.xx\.fbcdn\.net$ -- Facebook photo and video CDN
(\.|^)symcb\.com$ -- DigiCert (formerly Symantec) certificate status and revocation lists
^[a-z]\.thumbs\.redditmedia\.com$ -- Reddit thumbnails
(\.|^)twimg\.com$ -- X (Twitter) images and video
(\.|^)unraid\.net$ -- Unraid - Required for the operating system to update
(\.|^)wa\.me$ -- WhatsApp click-to-chat links
^whatsapp-cdn-shv-[0-9]{2}-[a-z]{3}[0-9]\.fbcdn\.net$ -- WhatsApp media CDN
(\.|^)windowsupdate\.com$ -- Windows Update
^(www\.|go\.)?microsoft\.com$|^(www\.)?windows\.com$ -- Microsoft and Windows main sites and go.microsoft.com links
^((www|(w[0-9]\.)?web|media((-[a-z]{3}|\.[a-z]{4})[0-9]{1,2}-[0-9](\.|-)(cdn|fna))?)\.)?whatsapp\.(com|net)$ -- WhatsApp
