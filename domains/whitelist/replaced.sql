// This is a backup of all exact whitelists that I have replaced with other filters (mainly using regex).

(0, '0-edge-chat.facebook.com', 1, 'Facebook - SlyEWL')
(0, '1-edge-chat.facebook.com', 1, 'Facebook - SlyEWL')
(0, '2-edge-chat.facebook.com', 1, 'Facebook - SlyEWL')
(0, '3-edge-chat.facebook.com', 1, 'Facebook - SlyEWL')
(0, '4-edge-chat.facebook.com', 1, 'Facebook - SlyEWL')
(0, '5-edge-chat.facebook.com', 1, 'Facebook - SlyEWL')
(0, '6-edge-chat.facebook.com', 1, 'Facebook - SlyEWL')
(0, 'edge-chat.facebook.com', 1, 'Facebook - SlyEWL')

(0, 'device.auth.xboxlive.com', 1, 'Microsoft Xbox - Used for Xbox updates, game downloads, acheivements - SlyEWL')
(0, 'title.auth.xboxlive.com', 1, 'Microsoft Xbox - Used for Xbox updates, game downloads, acheivements - SlyEWL')
(0, 'xsts.auth.xboxlive.com', 1, 'Microsoft Xbox - Used for Xbox updates, game downloads, acheivements - SlyEWL')

(0, 'kosmos-assets-prod.react.gammacdn.com', 1, 'AdultTime - Required for react buttons to work - SlyEWL')
(0, 'kosmos-prod.react.gammacdn.com', 1, 'AdultTime - Required for react buttons to work - SlyEWL')

(0, 'clients1.google.com', 1, 'Google - Required to use Google Maps - SlyEWL')
(0, 'clients2.google.com', 1, 'Google - Required to use Google Maps - SlyEWL') REPLACED
(0, 'clients3.google.com', 1, 'Google - Required to use Google Maps - SlyEWL')    BY
(0, 'clients4.google.com', 1, 'Google - Required to use Google Maps - SlyEWL')   REGEX: ^clients[1-6]*\.google\.com$ 
(0, 'clients5.google.com', 1, 'Google - Required to use Google Maps - SlyEWL')
(0, 'clients6.google.com', 1, 'Google - Required to use Google Maps - SlyEWL')

// RegEx Strings replaced
^kosmos(|-assets)-prod\.react\.gammacdn\.com$
