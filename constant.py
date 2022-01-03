#creative type constants
WEB="WEB"
WEB_SAFEFRAME="WEB_SAFEFRAME"
AMP="AMP"
IN_APP="IN_APP"
IN_APP_VIDEO="IN_APP_VIDEO"
NATIVE="NATIVE"
VIDEO="VIDEO"
JW_PLAYER="JWPLAYER"
ADPOD="ADPOD"

#video specific creative params
VIDEO_VAST_URL = 'https://ow.pubmatic.com/cache?uuid=%%PATTERN:pwtcid%%'
VIDEO_DURATION = 1000

# adpod specific creative params
ADPOD_VIDEO_VAST_URL = 'https://ow.pubmatic.com/cache?uuid=%%PATTERN:{}_pwtcid%%'

#video specific creative params
SDK_VIDEO_VAST_URL = 'https://trinity.pubmatic.com/openwrapsdk/assets/gam/signallingvast?ad_id=%%PATTERN:pwtsid_pubmatic%%'
SDK_VIDEO_DURATION = 15000

#JW Player specific creative params
JWP_VAST_URL = 'https://vpb-cache.jwplayer.com/cache?uuid=%%PATTERN:vpb_pubmatic_key%%'
JWP_DURATION = 60000

LINE_ITEMS_LIMIT = 450