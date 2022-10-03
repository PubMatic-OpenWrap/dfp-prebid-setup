#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
from builtins import input
from pprint import pprint

from colorama import init

import settings
import dfp.associate_line_items_and_creatives
import dfp.create_custom_targeting
import dfp.create_creatives
import dfp.create_line_items
import dfp.create_orders
import dfp.get_ad_units
import dfp.get_advertisers
import dfp.get_custom_targeting
import dfp.get_placements
import dfp.get_users
import dfp.get_root_ad_unit_id
from dfp.exceptions import (
  BadSettingException,
  MissingSettingException
)
from tasks.price_utils import (
  get_prices_array,
  get_prices_summary_string,
  micro_amount_to_num,
  num_to_str,
)
from tasks.dfp_utils import (
  TargetingKeyGen,
  DFPValueIdGetter,
  get_or_create_dfp_targeting_key
)

# Colorama for cross-platform support for colored logging.
# https://github.com/kmjennison/dfp-prebid-setup/issues/9
init()

# Configure logging.
if 'DISABLE_LOGGING' in os.environ and os.environ['DISABLE_LOGGING'] == 'true':
  logging.disable(logging.CRITICAL)
  logging.getLogger('googleads').setLevel(logging.CRITICAL)
  logging.getLogger('oauth2client').setLevel(logging.CRITICAL)
else:
  FORMAT = '%(message)s'
  logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)
  logging.getLogger('googleads').setLevel(logging.ERROR)
  logging.getLogger('oauth2client').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

class PrebidTargetingKeyGen(TargetingKeyGen):
    def __init__(self):

        super().__init__()

        # Get DFP key IDs for line item targeting.
        
        self.hb_pb_key_id = get_or_create_dfp_targeting_key('hb_pb')

        # Instantiate DFP targeting value ID getters for the targeting keys.
        
        self.HBPBValueGetter = DFPValueIdGetter('hb_pb')

        self.hb_bidder_value_id = None
        self.hb_pb_value_id = None

    def set_bidder_value(self, bidder_code):
        print("Setting bidder value to {0}".format(bidder_code))

        if bidder_code is None:
          self.bidder_criteria=None
          return

        #get hb_bidder_key only when bidder code is not None
        self.hb_bidder_key_id = get_or_create_dfp_targeting_key('hb_bidder')
        self.HBBidderValueGetter = DFPValueIdGetter('hb_bidder')

        self.hb_bidder_value_id = self.HBBidderValueGetter.get_value_id(bidder_code)
        return self.hb_bidder_value_id

    def set_price_value(self, price_str):
        self.hb_pb_value_id = self.HBPBValueGetter.get_value_id(price_str)
        return self.hb_pb_value_id

    def get_dfp_targeting(self):
      # Create key/value targeting for Prebid.
      # https://github.com/googleads/googleads-python-lib/blob/master/examples/dfp/v201802/line_item_service/target_custom_criteria.py
      # create custom criterias

      top_set = {
        'xsi_type': 'CustomCriteriaSet',
        'logicalOperator': 'AND',
        'children': []
      }
        

      if self.hb_bidder_value_id is not None:
        hb_bidder_criteria = {
        'xsi_type': 'CustomCriteria',
        'keyId': self.hb_bidder_key_id,
        'valueIds': [self.hb_bidder_value_id],
        'operator': 'IS'
        }
        top_set['children'].append(hb_bidder_criteria)


      hb_pb_criteria = {
        'xsi_type': 'CustomCriteria',
        'keyId': self.hb_pb_key_id,
        'valueIds': [self.hb_pb_value_id],
        'operator': 'IS'
      }

      top_set['children'].append(hb_pb_criteria)
      # The custom criteria will resemble:
      # (hb_bidder_criteria.key == hb_bidder_criteria.value AND
      #    hb_pb_criteria.key == hb_pb_criteria.value)
      return top_set

def setup_partner(user_email, advertiser_name, order_name, placements, ad_units, sizes, bidder_code, prices,
                  num_creatives, currency_code):
  """
  Call all necessary DFP tasks for a new Prebid partner setup.
  """

  # Get the user.
  user_id = dfp.get_users.get_user_id_by_email(user_email)

   # Get the placement IDs and ad_unit IDs.
  # Get the placement IDs.
  placement_ids=None
  ad_unit_ids=None
  if len(placements)>0:
    placement_ids = dfp.get_placements.get_placement_ids_by_name(placements)

  # Get the ad unit IDs.
  if len(ad_units)>0:
    ad_unit_ids = dfp.get_ad_units.get_ad_unit_ids_by_name(ad_units)
  # Get (or potentially create) the advertiser.
  else:
    root_id = dfp.get_root_ad_unit_id.get_root_ad_unit_id()
    ad_unit_ids = [ root_id ]

  
  advertiser_id = dfp.get_advertisers.get_advertiser_id_by_name(
    advertiser_name)

  # Create the order.
  order_id = dfp.create_orders.create_order(order_name, advertiser_id, user_id)

  # Create creatives.
  creative_configs = dfp.create_creatives.create_duplicate_creative_configs(
      bidder_code, order_name, advertiser_id, num_creatives=num_creatives)
  creative_ids = dfp.create_creatives.create_creatives(creative_configs)

  # Create line items.
  line_items_config = create_line_item_configs(prices, order_id,
    placement_ids, ad_unit_ids, bidder_code, sizes, PrebidTargetingKeyGen(),
    currency_code)

  logger.info("Creating line items...")
  line_item_ids = dfp.create_line_items.create_line_items(line_items_config)

  # Associate creatives with line items.
  dfp.associate_line_items_and_creatives.make_licas(line_item_ids,
    creative_ids, size_overrides=sizes)

  logger.info("""

    Done! Please review your order, line items, and creatives to
    make sure they are correct. Then, approve the order in DFP.

    Happy bidding!

  """)

def create_line_item_configs(prices, order_id, placement_ids, ad_unit_ids, bidder_code,
  sizes, key_gen_obj, currency_code):
  """
  Create a line item config for each price bucket.

  Args:
    prices (array)
    order_id (int)
    placement_ids (arr)
    ad_unit_ids (arr)
    bidder_code (str)
    sizes (arr)
    key_gen_obj (obj)
    currency_code (str)
  Returns:
    an array of objects: the array of DFP line item configurations
  """

  # The DFP targeting value ID for this `hb_bidder` code.
  key_gen_obj.set_bidder_value(bidder_code)

  line_items_config = []
  for price in prices:

    price_str = num_to_str(micro_amount_to_num(price))

    # Autogenerate the line item name.
    if bidder_code==None:
      line_item_name = u'{bidder_code}: HB ${price}'.format(
      bidder_code='Top Bid',
      price=price_str
    )
    else:
      line_item_name = u'{bidder_code}: HB ${price}'.format(
      bidder_code=bidder_code,
      price=price_str
    )

    # The DFP targeting value ID for this `hb_pb` price value.
    key_gen_obj.set_price_value(price_str)

    config = dfp.create_line_items.create_line_item_config(
      name=line_item_name,
      order_id=order_id,
      placement_ids=placement_ids,
      ad_unit_ids=ad_unit_ids,
      cpm_micro_amount=price,
      sizes=sizes,
      key_gen_obj=key_gen_obj,
      currency_code=currency_code,
    )

    line_items_config.append(config)

  return line_items_config

def check_price_buckets_validity(price_buckets):
  """
  Validate that the price_buckets object contains all required keys and the
  values are the expected types.

  Args:
    price_buckets (object)
  Returns:
    None
  """

  try:
    pb_precision = price_buckets['precision']
    pb_min = price_buckets['min']
    pb_max = price_buckets['max']
    pb_increment = price_buckets['increment']
  except KeyError:
    raise BadSettingException('The setting "PREBID_PRICE_BUCKETS" '
      'must contain keys "precision", "min", "max", and "increment".')

  if not (isinstance(pb_precision, int) or isinstance(pb_precision, float)):
    raise BadSettingException('The "precision" key in "PREBID_PRICE_BUCKETS" '
      'must be a number.')

  if not (isinstance(pb_min, int) or isinstance(pb_min, float)):
    raise BadSettingException('The "min" key in "PREBID_PRICE_BUCKETS" '
      'must be a number.')

  if not (isinstance(pb_max, int) or isinstance(pb_max, float)):
    raise BadSettingException('The "max" key in "PREBID_PRICE_BUCKETS" '
      'must be a number.')

  if not (isinstance(pb_increment, int) or isinstance(pb_increment, float)):
    raise BadSettingException('The "increment" key in "PREBID_PRICE_BUCKETS" '
      'must be a number.')

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def main():
  """
  Validate the settings and ask for confirmation from the user. Then,
  start all necessary DFP tasks.
  """

  user_email = getattr(settings, 'DFP_USER_EMAIL_ADDRESS', None)
  if user_email is None:
    raise MissingSettingException('DFP_USER_EMAIL_ADDRESS')

  advertiser_name = getattr(settings, 'DFP_ADVERTISER_NAME', None)
  if advertiser_name is None:
    raise MissingSettingException('DFP_ADVERTISER_NAME')

  order_name = getattr(settings, 'DFP_ORDER_NAME', None)
  if order_name is None:
    raise MissingSettingException('DFP_ORDER_NAME')

  placements = getattr(settings, 'DFP_TARGETED_PLACEMENT_NAMES', [])
  ad_units = getattr(settings, 'DFP_TARGETED_AD_UNIT_NAMES', [])


  sizes = getattr(settings, 'DFP_PLACEMENT_SIZES', None)
  if sizes is None:
    raise MissingSettingException('DFP_PLACEMENT_SIZES')
  elif len(sizes) < 1:
    raise BadSettingException('The setting "DFP_PLACEMENT_SIZES" '
      'must contain at least one size object.')

  currency_code = getattr(settings, 'DFP_CURRENCY_CODE', 'USD')

  # How many creatives to attach to each line item. We need at least one
  # creative per ad unit on a page. See:
  # https://github.com/kmjennison/dfp-prebid-setup/issues/13
  num_creatives = (
    getattr(settings, 'DFP_NUM_CREATIVES_PER_LINE_ITEM', None) or
    len(placements)
  )

  bidder_code = getattr(settings, 'PREBID_BIDDER_CODE', None)
  if bidder_code is not None and not isinstance(bidder_code,(str)):
    raise BadSettingException('PREBID_BIDDER_CODE')

  price_buckets = getattr(settings, 'PREBID_PRICE_BUCKETS', None)
  if price_buckets is None:
    raise MissingSettingException('PREBID_PRICE_BUCKETS')

  check_price_buckets_validity(price_buckets)

  prices = get_prices_array(price_buckets)
  prices_summary = get_prices_summary_string(prices,
    price_buckets['precision'])

  logger.info(
    u"""

    Going to create {name_start_format}{num_line_items}{format_end} new line items.
      {name_start_format}Order{format_end}: {value_start_format}{order_name}{format_end}
      {name_start_format}Advertiser{format_end}: {value_start_format}{advertiser}{format_end}

    Line items will have targeting:
      {name_start_format}hb_pb{format_end} = {value_start_format}{prices_summary}{format_end}
      {name_start_format}hb_bidder{format_end} = {value_start_format}{bidder_code}{format_end}
      {name_start_format}placements{format_end} = {value_start_format}{placements}{format_end}
      {name_start_format}ad units{format_end} = {value_start_format}{ad_units}{format_end}

    """.format(
      num_line_items = len(prices),
      order_name=order_name,
      advertiser=advertiser_name,
      user_email=user_email,
      prices_summary=prices_summary,
      bidder_code=bidder_code,
      placements=placements,
      ad_units=ad_units,
      sizes=sizes,
      name_start_format=color.BOLD,
      format_end=color.END,
      value_start_format=color.BLUE,
    ))

  ok = input('Is this correct? (y/n)\n')

  if ok != 'y':
    logger.info('Exiting.')
    return

  setup_partner(user_email, advertiser_name, order_name, placements, ad_units, sizes, bidder_code, prices, num_creatives, currency_code)

if __name__ == '__main__':
  main()