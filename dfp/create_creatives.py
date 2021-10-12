
import logging
import os
import pprint

from googleads import ad_manager

from dfp.client import get_client


logger = logging.getLogger(__name__)

def create_creatives(creatives):
  """
  Creates creatives in DFP.

  Args:
    creatives (arr): an array of objects, each a creative configuration
  Returns:
    an array: an array of created creative IDs
  """
  dfp_client = get_client()
  creative_service = dfp_client.GetService('CreativeService',
    version='v202102')
  creatives = creative_service.createCreatives(creatives)

  # Return IDs of created line items.
  created_creative_ids = []
  for creative in creatives:
    created_creative_ids.append(creative['id'])
    logger.info(u'Created creative with name "{name}".'.format(name=creative['name']))
  return created_creative_ids

def create_creative_config(name, advertiser_id, size=None, creative_file=None, safe_frame=False):
  """
  Creates a creative config object.

  Args:
    name (str): the name of the creative
    advertiser_id (int): the ID of the advertiser in DFP
    sizes (string array): size for the creative
    creative_file (string): the name of the file containing creative
    safe_frame (bool): Flag to indicate Whether the Creative is compatible for SafeFrame rendering.


  Returns:
    an object: the line item config
  """

  if creative_file == None:
      creative_file = 'creative_snippet.html'

  snippet_file_path = os.path.join(os.path.dirname(__file__),
    creative_file)
  with open(snippet_file_path, 'r') as snippet_file:
      snippet = snippet_file.read()

  # https://developers.google.com/doubleclick-publishers/docs/reference/v201802/CreativeService.Creative
  
  #if size is not passed, create creative of size 1x1
  if size == None:
    size = {
      'width': 1,
      'height': 1
    }
    
  config = {
    'xsi_type': 'ThirdPartyCreative',
    'name': name,
    'advertiserId': advertiser_id,
    'size': size,
    'snippet': snippet,
    # https://github.com/prebid/Prebid.js/issues/418
    'isSafeFrameCompatible': safe_frame,
  }
  return config

def build_creative_name(bidder_code, order_name, creative_num, size=None, prefix=None):
    """
    Returns a name for a creative.

    Args:
      bidder_code (str): the bidder code for the header bidding partner
      order_name (int): the name of the order in DFP
      creative_num (int): the num_creatives distinguising this creative from any
        duplicates
    Returns:
      a string
    """
    if prefix != None:
      if size==None:
        return '{prefix}_1x1'.format(prefix=prefix)
      return '{prefix}_{width}x{height}'.format(
        prefix=prefix,width=size["width"], height=size["height"] )

    if size == None:
      return '{bidder_code}: HB {order_name}, #{num}'.format(
          bidder_code=bidder_code, order_name=order_name, num=creative_num)
    else:
        return '{bidder_code}: HB {order_name}, {width}x{height} #{num}'.format(
          bidder_code=bidder_code, order_name=order_name, width=size["width"],
          height=size["height"],num=creative_num)

def create_duplicate_creative_configs(bidder_code, order_name, advertiser_id, sizes=None,
  num_creatives=1, creative_file=None, safe_frame=False, prefix=None):
  """
  Returns an array of creative config object.

  Args:
    bidder_code (str): the bidder code for the header bidding partner
    order_name (int): the name of the order in DFP
    advertiser_id (int): the ID of the advertiser in DFP
    sizes(String array): sizes for creative
    num_creatives (int): how many creative configs to generate
    creative_file: (string) file name containing creative content
    safe_frame (bool): to enable safe_frame option
    prefix (string): creative name prefix
  Returns:
    an array: an array of length `num_creatives`, each item a line item config
  """
  creative_configs = []
  #this flow is for prebid where sizes are not passed and for openwrap with 1x1 option set
  if sizes == None:
    for creative_num in range(1, num_creatives + 1):
      config = create_creative_config(
        name=build_creative_name(bidder_code, order_name, creative_num, prefix=prefix),
        advertiser_id=advertiser_id,
        creative_file=creative_file,
        safe_frame=safe_frame
      )
      creative_configs.append(config)
  # this flow is for openwrap, where sizes are considered for creative creation
  else:
    for size in sizes:
      for creative_num in range(1, num_creatives + 1):
        config = create_creative_config(
          name=build_creative_name(bidder_code, order_name, creative_num, size, prefix),
          advertiser_id=advertiser_id,
          size=size,
          creative_file=creative_file,
          safe_frame=safe_frame
        )
        creative_configs.append(config)
  return creative_configs

def create_creative_configs_for_native(advertiser_id,creative_template_ids,
  num_creatives=1, prefix=None):

  creative_configs = []
  for template_id in creative_template_ids:
      for creative_num in range(1, num_creatives + 1):
        config = create_creative_config_native(
          name= "{}_{}_native".format(prefix, template_id),
          advertiser_id=advertiser_id,
          creative_template_id=template_id,
        )
        creative_configs.append(config)
      
  return creative_configs
  

def create_creative_config_native(name, advertiser_id, creative_template_id):
  creative = {
    'xsi_type': 'TemplateCreative',
    'name': name,
    'advertiserId': advertiser_id,
    'size': {
      'width': '1', 
      'height': '1',
      'isAspectRatio': False
    },
    'creativeTemplateId': creative_template_id,
    'destinationUrl': 'http://dummyURL.com',
    'isSafeFrameCompatible': True,
    'isNativeEligible': True
  }
  return creative

# This method creates creative config of type VastRedirectCreative
def create_creative_configs_for_video(advertiser_id, sizes, prefix, vast_url, duration):
  
  creative_configs = []
  
  #if size is not passed, create creative of size 1x1
  if sizes == None:
    sizes = [{
      'width': 1,
      'height': 1
    }]

  for size in sizes:
    name = '{prefix}_{width}x{height}_VASTCREATIVE'.format(
          prefix=prefix,width=size["width"], height=size["height"])
    
    creative = {
      'xsi_type': 'VastRedirectCreative',
      'name': name,
      'advertiserId': advertiser_id,
      'size': size,
      'vastXmlUrl': vast_url,
      'duration' : duration,
      'vastRedirectType' : 'LINEAR'
    }
    creative_configs.append(creative)
    
  return creative_configs


# This method creates creative config of type VastRedirectCreative for adpod
# For every creative duration a new creative will be created.
def create_creative_configs_for_adpod(advertiser_id, sizes, uniquedID, vast_url, creative_durations, slot):
  
  creative_configs = []

  for i in range(len(creative_durations)):
    name = '{slot}_{width}x{height}_{dur}SecondAd_{uniquedID}'.format(slot=slot,
        width=sizes[0]["width"], height=sizes[0]["height"], dur=creative_durations[i],  uniquedID=uniquedID)

    creative = {
      'xsi_type': 'VastRedirectCreative',
      'name': name,
      'advertiserId': advertiser_id,
      'size': sizes[0],
      'vastXmlUrl': str(vast_url).format(slot),
      'duration' : int(creative_durations[i])*1000,
      'vastRedirectType' : 'LINEAR'
    }

    creative_configs.append(creative)
    
  return creative_configs


