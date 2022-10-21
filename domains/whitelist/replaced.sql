## This is a backup of all exact whitelists that I have replaced with other filters (mainly using regex).

# ADULTTIME
(0, 'cdn.contentful.com', 1, 'AdultTime - A required CDN of the site to access image, videos, etc - SlyEWL')
(0, 'client-rapi.recombee.us', 1, 'AdultTime - Required for side panels to load - SlyEWL')
(0, 'kosmos-assets-prod.react.gammacdn.com', 1, 'AdultTime - Required for react buttons to work - SlyEWL')
(0, 'kosmos-prod.react.gammacdn.com', 1, 'AdultTime - Required for react buttons to work - SlyEWL')

# FACEBOOK
(0, '0-edge-chat.facebook.com', 1, 'Facebook - SlyEWL')
(0, '1-edge-chat.facebook.com', 1, 'Facebook - SlyEWL')
(0, '2-edge-chat.facebook.com', 1, 'Facebook - SlyEWL')
(0, '3-edge-chat.facebook.com', 1, 'Facebook - SlyEWL')
(0, '4-edge-chat.facebook.com', 1, 'Facebook - SlyEWL')
(0, '5-edge-chat.facebook.com', 1, 'Facebook - SlyEWL')
(0, '6-edge-chat.facebook.com', 1, 'Facebook - SlyEWL')
(0, 'edge-chat.facebook.com', 1, 'Facebook - SlyEWL')

# XBOX
(0, 'device.auth.xboxlive.com', 1, 'Microsoft Xbox - Used for Xbox updates, game downloads, acheivements - SlyEWL')
(0, 'title.auth.xboxlive.com', 1, 'Microsoft Xbox - Used for Xbox updates, game downloads, acheivements - SlyEWL')
(0, 'xsts.auth.xboxlive.com', 1, 'Microsoft Xbox - Used for Xbox updates, game downloads, acheivements - SlyEWL')

# GOOGLE
(0, 'clients1.google.com', 1, 'Google - Required to use Google Maps - SlyEWL')
(0, 'clients2.google.com', 1, 'Google - Required to use Google Maps - SlyEWL') REPLACED
(0, 'clients3.google.com', 1, 'Google - Required to use Google Maps - SlyEWL')    BY
(0, 'clients4.google.com', 1, 'Google - Required to use Google Maps - SlyEWL')   REGEX: ^clients[1-6]*\.google\.com$ 
(0, 'clients5.google.com', 1, 'Google - Required to use Google Maps - SlyEWL')
(0, 'clients6.google.com', 1, 'Google - Required to use Google Maps - SlyEWL')

# QNAP
(0, 'appcenter.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'blog.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'docs.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'download-gcdn.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'download.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'eu.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'eu1.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'europe.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'event.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'files.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'files1.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'forum.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'forum1.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'ftp.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'gcdn-qne-archive.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'help.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'helpdesk.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'install.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'license.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'license2.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'live.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'livebeta.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'reseller.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'security.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'service.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'shop.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'smtp.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'software.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'update.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'us1.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')
(0, 'www.qnap.com', 1, 'QNAP - NAS Storage Computers - SlyEWL')

# RegEx Strings
^kosmos(|-assets)-prod\.react\.gammacdn\.com$
