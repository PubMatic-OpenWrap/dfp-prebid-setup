#creative type constants
WEB="WEB"
WEB_SAFEFRAME="WEB_SAFEFRAME"
AMP="AMP"
IN_APP="IN_APP"
NATIVE="NATIVE"
VIDEO="VIDEO"
JW_PLAYER="JWPLAYER"
ADPOD="ADPOD"

#video specific creative params
VIDEO_VAST_URL = 'https://ow.pubmatic.com/cache?uuid=%%PATTERN:pwtcid%%'
VIDEO_DURATION = 1000

# adpod specific creative params
ADPOD_VIDEO_VAST_URL = 'https://ow.pubmatic.com/cache?uuid=%%PATTERN:{}_pwtcid%%'

#JW Player specific creative params
JWP_VAST_URL = 'https://vpb-cache.jwplayer.com/cache?uuid=%%PATTERN:vpb_pubmatic_key%%'
JWP_DURATION = 60000

LINE_ITEMS_LIMIT = 450