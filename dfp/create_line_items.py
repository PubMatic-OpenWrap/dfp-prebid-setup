import logging
from googleads import ad_manager

from dfp.client import get_client


logger = logging.getLogger(__name__)

def create_line_items(line_items):
  """
  Creates line items in DFP.

  Args:
    line_items (arr): an array of objects, each a line item configuration
  Returns:
    an array: an array of created line item IDs
  """
  dfp_client = get_client()
  line_item_service = dfp_client.GetService('LineItemService', version='v202102')
  line_items = line_item_service.createLineItems(line_items)

  # Return IDs of created line items.
  created_line_item_ids = []
  for line_item in line_items:
    created_line_item_ids.append(line_item['id'])
    logger.info(u'Created line item with name "{name}".'.format(name=line_item['name']))
  return created_line_item_ids


def create_line_item_config(name, order_id, placement_ids, ad_unit_ids, cpm_micro_amount, sizes, key_gen_obj,
                            lineitem_type='PRICE_PRIORITY',currency_code='USD', setup_type = None, creative_template_ids = None, 
                            same_adv_exception=False, device_categories=None,
                            device_capabilities = None,roadblock_type = 'ONE_OR_MORE', durations = None, slot=None):
  """
  Creates a line item config object.

  Args:
    name (str): the name of the line item
    order_id (int): the ID of the order in DFP
    ad_unit_ids (arr): an array of DFP ad unit IDs to target
    cpm_micro_amount (int): the currency value (in micro amounts) of the
      line item
    sizes (arr): an array of objects, each containing 'width' and 'height'
      keys, to set the creative sizes this line item will serve
    key_gen_obj (obj): targeting key gen object
    lineitem_type (str): the type of line item('PRICE_PRIORTY', 'SPONSORSHIP', 'HOUSE' or 'NETWORK')
    currency_code (str): the currency code (e.g. 'USD' or 'EUR')
    setup_type (str): type of creative, for differentiating native
    creative_template_ids (arr): an array of creative template IDs required for Native
    same_adv_exception (bool) : https://developers.google.com/ad-manager/api/reference/v202102/LineItemService.LineItem.html#disablesameadvertisercompetitiveexclusion
    device_categories
    device_capabilities
    roadblock_type (str) : https://developers.google.com/ad-manager/api/reference/v202102/LineItemService.LineItem.html#roadblockingtype
    durations: video creative durations in case of setup_type = 'ADPOD'
    slot: Represent the slot number of the ADPOD.
  Returns:
    an object: the line item config
  """

  # Set up sizes.
  creative_placeholders = []

 # creative placeholder for native
  if setup_type == 'NATIVE':
    for id in creative_template_ids:
      creative_placeholders.append(
        {
          'size': {
            'width': 1,
            'height': 1
          },
          'creativeTemplateId': id,
          'creativeSizeType': 'NATIVE'
        }
      )
  elif setup_type == 'ADPOD':
    for i in range(len(durations)):
      creative_placeholders.append({
        'size': sizes[0],
        'targetingName': "{}_{}second_ad".format(slot,durations[i])
      })      
  else:
    for size in sizes:
      creative_placeholders.append({
        'size': size
      })

  top_set = key_gen_obj.get_dfp_targeting()

  crv_targeting = None
  if setup_type == 'ADPOD':
    crv_targeting = []
    for dur in durations:
      crv_targeting.append({
          'name': "{}_{}second_ad".format(slot,dur),
          'targeting': {
            'customTargeting': key_gen_obj.set_creative_targeting(dur,slot),
          }
      })

  # https://developers.google.com/doubleclick-publishers/docs/reference/v201802/LineItemService.LineItem
  line_item_config = {
    'name': name,
    'orderId': order_id,
    # https://developers.google.com/doubleclick-publishers/docs/reference/v201802/LineItemService.Targeting
    'targeting': {
      'inventoryTargeting': {},
      'customTargeting': top_set,
    },
    'startDateTimeType': 'IMMEDIATELY',
    'unlimitedEndDateTime': True,
    'lineItemType': lineitem_type,
    'costType': 'CPM',
    'costPerUnit': {
      'currencyCode': currency_code,
      'microAmount': cpm_micro_amount
    },
     'valueCostPerUnit':{
      'currencyCode': currency_code,
      'microAmount': cpm_micro_amount
    },
    'roadblockingType': roadblock_type,
    'creativeRotationType': 'EVEN',
    'primaryGoal': {
      'goalType': 'NONE'
    },
    'creativePlaceholders': creative_placeholders,
    'disableSameAdvertiserCompetitiveExclusion': same_adv_exception,
    'creativeTargetings': crv_targeting
  }

  #for network and house line-items, set goal type and units
  if lineitem_type in ('NETWORK','HOUSE'):
    line_item_config['primaryGoal']['goalType'] = 'DAILY'
    line_item_config['primaryGoal']['units'] = 100

  if lineitem_type in ('SPONSORSHIP'):
    line_item_config['primaryGoal']['unitType'] = 'IMPRESSIONS'
    line_item_config['primaryGoal']['goalType'] = 'DAILY'
    line_item_config['primaryGoal']['units'] = 100
    line_item_config['skipInventoryCheck'] = True
    line_item_config['allowOverbook'] = True

  if device_categories != None and len(device_categories) > 0:
      dev_cat_targeting = []
      for dc in device_categories:
          dev_cat_targeting.append({'id': str(dc)})

      line_item_config['targeting']['technologyTargeting'] = {'deviceCategoryTargeting': {'targetedDeviceCategories': dev_cat_targeting}}

  #device capability targetring
  if device_capabilities != None and len(device_capabilities) > 0:
      dev_cap_targeting = []
      for dc in device_capabilities:
          dev_cap_targeting.append({'id': str(dc)})

      line_item_config['targeting']['technologyTargeting'] = {'deviceCapabilityTargeting': {'targetedDeviceCapabilities': dev_cap_targeting}}

  if placement_ids is not None:
    line_item_config['targeting']['inventoryTargeting']['targetedPlacementIds'] = placement_ids

  if ad_unit_ids is not None:
    line_item_config['targeting']['inventoryTargeting']['targetedAdUnits'] = [{'adUnitId': id} for id in ad_unit_ids]

  if setup_type in ('VIDEO', 'JWPLAYER','ADPOD'):
    line_item_config['environmentType'] = 'VIDEO_PLAYER'
    line_item_config['videoMaxDuration'] = 60000
    line_item_config['targeting']['requestPlatformTargeting'] = {'targetedRequestPlatforms': ['VIDEO_PLAYER']}
    
  return line_item_config
