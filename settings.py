import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
GOOGLEADS_YAML_FILE = os.path.join(ROOT_DIR, 'googleads.yaml')


#########################################################################
# DFP SETTINGS
#########################################################################

# A string describing the order
DFP_ORDER_NAME = None

# The email of the DFP user who will be the trafficker for
# the created order
DFP_USER_EMAIL_ADDRESS = None

# The exact name of the DFP advertiser for the created order
DFP_ADVERTISER_NAME = None

# Advertiser type.  Can be either "ADVERTISER" or "AD_NETWORK".  Controls
#   what type advertisers are looked up and created with.
#   Defaults to "AD_NETWORK"
DFP_ADVERTISER_TYPE = "AD_NETWORK"

# Names of placements the line items should target.
#  Leave empty for Run of Network (requires Network permission)
DFP_TARGETED_PLACEMENT_NAMES = []

# Names of ad units the line items should target.
DFP_TARGETED_AD_UNIT_NAMES = []

# Sizes of placements. These are used to set line item and creative sizes.
DFP_PLACEMENT_SIZES = [
  {
    'width': '300',
    'height': '250'
  },
  {
    'width': '728',
    'height': '90'
  },
]

# Whether we should create the advertiser in DFP if it does not exist.
# If False, the program will exit rather than create an advertiser.
DFP_CREATE_ADVERTISER_IF_DOES_NOT_EXIST = False

# If settings.DFP_ORDER_NAME is the same as an existing order, add the created 
# line items to that order. If False, the program will exit rather than
# modify an existing order.
DFP_USE_EXISTING_ORDER_IF_EXISTS = False

# Optional
# Each line item should have at least as many creatives as the number of 
# ad units you serve on a single page because DFP specifies:
#   "Each of a line item's assigned creatives can only serve once per page,
#    so if you want the same creative to appear more than once per page,
#    copy the creative to associate multiple instances of the same creative."
# https://support.google.com/dfp_sb/answer/82245?hl=en
#
# This will default to the number of placements specified in
# `DFP_TARGETED_PLACEMENT_NAMES`.
# DFP_NUM_CREATIVES_PER_LINE_ITEM = 2

# Optional
# The currency to use in DFP when setting line item CPMs. Defaults to 'USD'.
# DFP_CURRENCY_CODE = 'USD'

# Optional
# Whether to set the "Same Advertiser Exception" on line items.  Defaults to false
#   Currently only works for OpenWrap
#DFP_SAME_ADV_EXCEPTION = True

# Optional
# Device Category Targeting
#    Valid Values: 'Connected TV', 'Desktop', 'Feature Phone', 'Set Top Box', 'Smartphone', 'Tablet'}
#    Defaults to no device category targeting
#    Currently supported for OpenWrap Only
DFP_DEVICE_CATEGORIES = ['Desktop']

# Optional
# DFP Roadblock Type
#    Valid Values: 'ONE_OR_MORE', 'AS_MANY_AS_POSSIBLE'
#    Defaults to 'ONE_OR_MORE'
#    Currently supported for OpenWrap Only
#DFP_ROADBLOCK_TYPE = 'AS_MANY_AS_POSSIBLE'

#########################################################################
# PREBID SETTINGS
#########################################################################

# OpenWrap: you can specify an array to target multiple bidders
#  with one line item
PREBID_BIDDER_CODE = ["pubmatic"]
#
# Prebid line item generator only accepts a single value
#PREBID_BIDDER_CODE = None

# Price buckets. This should match your Prebid settings for the partner. See:
# http://prebid.org/dev-docs/publisher-api-reference.html#module_pbjs.setPriceGranularity
# FIXME: this should be an array of buckets. See:
# https://github.com/prebid/Prebid.js/blob/8fed3d7aaa814e67ca3efc103d7d306cab8c692c/src/cpmBucketManager.js
PREBID_PRICE_BUCKETS = {
  'precision': 2,
  'min' : 0,
  'max' : 20,
  'increment': 0.10,
}

# OpenWrap: Buckets are specified in a CSV fileself
#   Same file format as the PubMatic Line Item tool
OPENWRAP_BUCKET_CSV = 'TestLineItems.csv'

# OpenWrap: Set custom line item targeting values
#OPENWRAP_CUSTOM_TARGETING = [
#    ("a", "IS", ("1", "2", "3")),
#    ("b", "IS_NOT", ("4", "5", "6")),
#]

# OpenWrap Creative Type
#  One of "WEB", "WEB_SAFEFRAME", "AMP", "IN_APP", "UNIVERSAL"
#  Defaults to WEB
#OPENWRAP_CREATIVE_TYPE = "WEB"

#currency conversion
CURRENCY_EXCHANGE = False

#########################################################################

# Try importing local settings, which will take precedence.
try:
    from local_settings import *
except ImportError:
    pass
