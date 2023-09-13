#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import logging
import os
import re
import sys
import tasks
from builtins import input
from pprint import pprint

from colorama import init

import constant
import settings

import dfp.associate_line_items_and_creatives
import dfp.create_custom_targeting
import dfp.create_creatives
import dfp.create_creative_sets
import dfp.get_creative_template
import dfp.create_line_items
import dfp.create_orders
import dfp.get_advertisers
import dfp.get_custom_targeting
import dfp.get_placements
import dfp.get_users
import dfp.get_device_categories
import dfp.get_root_ad_unit_id
import dfp.get_network
import dfp.get_device_capabilities
import dfp.get_orders
import dfp.get_line_items
from dfp.exceptions import (
  BadSettingException,
  MissingSettingException,
  DFPException
)
from tasks.price_utils import (
  get_prices_array,
  get_prices_summary_string,
  num_to_micro_amount,
  micro_amount_to_num,
  num_to_str,
)
from tasks.dfp_utils import (
  TargetingKeyGen,
  DFPValueIdGetter,
  get_or_create_dfp_targeting_key
)

from urllib.request import urlopen
import json
import shortuuid
from dfp.client import get_client
from requests.exceptions import ConnectionError
from googleads.errors import GoogleAdsServerFault


order_list = []

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
  logging.getLogger(__name__).setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

creativetype_platform_map = {
    constant.WEB: "display",
    constant.WEB_SAFEFRAME: "display",
    constant.AMP: "amp",
    constant.IN_APP: "inapp",
    constant.IN_APP_VIDEO: "inapp",
    constant.IN_APP_NATIVE: "inapp",
    constant.NATIVE: "native",
    constant.VIDEO : "video",
    constant.ADPOD : "video",
    constant.JW_PLAYER : "jwp"
}

class OpenWrapTargetingKeyGen(TargetingKeyGen):
    def __init__(self):

        super().__init__()

        self.bidder_criteria = None
        self.platform_criteria = None
        self.price_els = None
        self.jwPriceValueGetter = None
        self.jw_price_key_id = None
        self.setup_type = None
        self.get_custom_targeting = []
        self.bid_price = None
        self.price_set = None
        self.pwtpid_key_id = None
        self.pwtbst_key_id  = None  
        self.pwtecp_key_id = None
        self.pwtplt_key_id = None
        self.BidderValueGetter = None
        self.BidderValueGetter = None
        self.BstValueGetter = None
        self.PriceValueGetter = None
        self.PltValueGetter = None
        self.creativeTargeting = None
        self.pwtbst_value_id = None
        self.deal_tier = None
    def init_keys(self):  
        # Get DFP key IDs for line item targeting.
        self.pwtpid_key_id = get_or_create_dfp_targeting_key('pwtpid', key_type='PREDEFINED')  # bidder
        self.pwtbst_key_id = get_or_create_dfp_targeting_key('pwtbst', key_type='PREDEFINED')  # is pwt
        self.pwtecp_key_id = get_or_create_dfp_targeting_key('pwtecp', key_type='FREEFORM') # price
        self.pwtplt_key_id = get_or_create_dfp_targeting_key('pwtplt', key_type='PREDEFINED') # platform

        # Instantiate DFP targeting value ID getters for the targeting keys.
        self.BidderValueGetter = DFPValueIdGetter('pwtpid')
        self.BstValueGetter = DFPValueIdGetter('pwtbst')
        self.PriceValueGetter = DFPValueIdGetter('pwtecp', match_type='PREFIX')
        self.PltValueGetter = DFPValueIdGetter('pwtplt')

        self.pwtbst_value_id = self.BstValueGetter.get_value_id("1")    

    # Add creative level targeting for each creative duration for each adpod slot
    # ex: s1_pwtdur = 10
    def set_creative_targeting(self, durations, slot):
        self.creativeTargeting = {}
        key = '{}_pwtdur'.format(slot)   
        key_id = get_or_create_dfp_targeting_key(key, key_type='FREEFORM')
        value_getter = DFPValueIdGetter(key) 
        for dur in durations:         
            value_id = value_getter.get_value_id(str(dur))
            custom_criteria = {
                'xsi_type': 'CustomCriteria',
                'keyId': key_id,
                'valueIds': [value_id],
                'operator': 'IS'
            }     
            self.creativeTargeting[dur]  = {
                'xsi_type': 'CustomCriteriaSet',
                'logicalOperator': 'OR',
                'children': [custom_criteria]
            }
            
    def get_creative_targeting(self, duration):    
        return self.creativeTargeting[duration]
    
    def set_deal_tier(self, slot, deal_tier):
        key = '{}_pwtdt'.format(slot)   
        key_id = get_or_create_dfp_targeting_key(key, key_type='FREEFORM')
        value_getter = DFPValueIdGetter(key)  
        value_id = value_getter.get_value_id(deal_tier)
        self.deal_tier = {
            'xsi_type': 'CustomCriteria',
            'keyId': key_id,
            'valueIds': [value_id],
            'operator': 'IS'
        }

    # Set pwtpb custom targeting key
    def set_bid_price(self, slot,price):
        key = '{}_pwtpb'.format(slot)   
        key_id = get_or_create_dfp_targeting_key(key, key_type='FREEFORM')
        value_getter = DFPValueIdGetter(key)  
        value_id = value_getter.get_value_id(price)
        self.bid_price = {
            'xsi_type': 'CustomCriteria',
            'keyId': key_id,
            'valueIds': [value_id],
            'operator': 'IS'
        }

    def set_bidder_value(self, bidder_code, slot):
        logger.info("Setting bidder value to {0}".format(bidder_code))

        if bidder_code == None:
            self.bidder_criteria = None
            return
        
        if self.setup_type is constant.ADPOD:
            bidderKey = '{}_pwtpid'.format(slot)   
            self.pwtpid_key_id  =  get_or_create_dfp_targeting_key( bidderKey , key_type='PREDEFINED') 
            self.BidderValueGetter = DFPValueIdGetter(bidderKey)

        if isinstance(bidder_code, (list, tuple)):
            # Multiple biders for us to OR to other
            bidder_criteria = []
            for bc in bidder_code:
                value_id = self.BidderValueGetter.get_value_id(bc)
                custom_criteria = {
                    'xsi_type': 'CustomCriteria',
                    'keyId': self.pwtpid_key_id,
                    'valueIds': [value_id],
                    'operator': 'IS'
                }
                bidder_criteria.append(custom_criteria)

            self.bidder_criteria = {
                'xsi_type': 'CustomCriteriaSet',
                'logicalOperator': 'OR',
                'children': bidder_criteria
            }
        else:
            self.bidder_criteria  = {
                'xsi_type': 'CustomCriteria',
                'keyId': self.pwtpid_key_id,
                'valueIds': [self.BidderValueGetter.get_value_id(bidder_code) ],
                'operator': 'IS'
            }

    def set_setup_type(self, ct):
        self.setup_type = ct

    def set_jwplayer_key(self):
        self.jw_price_key_id = get_or_create_dfp_targeting_key('vpb_pubmatic_bid', key_type='FREEFORM')
        self.jwPriceValueGetter = DFPValueIdGetter('vpb_pubmatic_bid', match_type='PREFIX')

    def set_custom_targeting(self, custom_targeting):
        self.custom_targeting = []

        if custom_targeting == None:
            return

        for cc in custom_targeting:
            key_id = get_or_create_dfp_targeting_key(cc[0], key_type='FREEFORM')
            value_getter = DFPValueIdGetter(cc[0])
            one_custom_criteria = None

            if isinstance(cc[2], (list, tuple)):
                value_criterias = []
                for val in cc[2]:
                    value_id = value_getter.get_value_id(val)
                    criteria = {
                        'xsi_type': 'CustomCriteria',
                        'keyId': key_id,
                        'valueIds': [value_id],
                        'operator': cc[1]
                    }
                    value_criterias.append(criteria)

                operator = 'OR'
                if cc[1] == 'IS_NOT':
                    operator = 'AND'

                one_custom_criteria = {
                    'xsi_type': 'CustomCriteriaSet',
                    'logicalOperator': operator,
                    'children': value_criterias
                }
            else:
                one_custom_criteria  = {
                    'xsi_type': 'CustomCriteria',
                    'keyId': key_id,
                    'valueIds': [value_getter.get_value_id(cc[2]) ],
                    'operator': cc[1]
                }

            self.custom_targeting.append(one_custom_criteria)

    def set_price_value(self, price_obj):
        self.price_els = self.process_price_bucket(price_obj['start'], price_obj['end'], price_obj['granularity'])

    def set_platform_targetting(self):

        #get platform value from the creative type
        platform = creativetype_platform_map[self.setup_type]
        platform_value_id = self.PltValueGetter.get_value_id(platform)
        self.platform_criteria = {
            'xsi_type': 'CustomCriteria',
            'keyId': self.pwtplt_key_id,
            'valueIds': [platform_value_id],
            'operator': 'IS'
        }


    def get_dfp_targeting(self):

        top_set = {
            'xsi_type': 'CustomCriteriaSet',
            'logicalOperator': 'AND',
            'children': []
        }

        # is PWT
        pwt_bst_criteria = {
            'xsi_type': 'CustomCriteria',
            'keyId': self.pwtbst_key_id,
            'valueIds': [self.pwtbst_value_id ],
            'operator': 'IS'
        }

        # Generate Ids for all the price elements
        price_value_ids = []
        price_key_id = self.pwtecp_key_id
        price_value_getter = self.PriceValueGetter

        #for JW player set key to 'vpb_pubmatic_bid' for price targetting
        if self.setup_type == constant.JW_PLAYER:
            price_key_id = self.jw_price_key_id
            price_value_getter = self.jwPriceValueGetter

        if self.setup_type != constant.ADPOD:
            for p in self.price_els:
                value_id = price_value_getter.get_value_id(p)
                custom_criteria = {
                    'xsi_type': 'CustomCriteria',
                    'keyId': price_key_id ,
                    'valueIds': [value_id],
                    'operator': 'IS'
                }
                price_value_ids.append(custom_criteria)

            self.price_set = {
                'xsi_type': 'CustomCriteriaSet',
                'logicalOperator': 'OR',
                'children': price_value_ids
            }

        #pwtpid
        if self.bidder_criteria:
            top_set['children'].append(self.bidder_criteria)

        #pwtecp
        if self.price_set:
            top_set['children'].append(self.price_set)

        if  self.deal_tier:
            top_set['children'].append(self.deal_tier)
        # dont set other targetting for JW Player
        if self.setup_type is not constant.JW_PLAYER:

            if self.setup_type not in (constant.ADPOD, constant.IN_APP, constant.IN_APP_VIDEO, constant.IN_APP_NATIVE):
                #pwtbst
                top_set['children'].append(pwt_bst_criteria)

            #pwtplt
            if self.platform_criteria:
                top_set['children'].append(self.platform_criteria)

            #custom targetting
            if len(self.custom_targeting) > 0:
                top_set['children'].extend(self.custom_targeting)

            if self.bid_price: 
                top_set['children'].append(self.bid_price)

        return top_set

    def process_price_bucket(self, start_index, end_index, granu):

        subCustomValueArray = []
        sub_granu = None

        if granu < 0.10:
            sub_granu = 0.01
        elif granu < 1:
            sub_granu = 0.10
        else:
            sub_granu = 1.00

        # if granu is .20 then $r=0 if .25 then $r=5
        r = (granu * 100) % 10
        k = start_index

        while round(k,2) < round(end_index,2):

            #logger.debug("k: {}  end_index: {}".format(k, end_index))
            # if k=1.25 then reminder is 5>0 and for .20 its 0
            if round(k*100) % 10 > 0 or sub_granu == 0.01:
                if r >= 0:
                    #suppose start_index=0.33 and $end=0.40
                    end = None
                    if sub_granu < 0.10:
                        end = k+(granu*100)%10/100
                    else:
                        end = k+(10-(round(k*100)%10))/100

                    if end >= end_index:
                        end = end_index

                    #TODO
                    if k == 0 and sub_granu == 0.01:
                        k = 0.01

                    v = k
                    while round(v,2) < round(end,2):
                        v_str = "{0:.2f}".format(v)
                        #logger.debug("----First---- Custom criteria for Line Item is =  %s", v_str)
                        subCustomValueArray.append(v_str)
                        v = v + 0.01

                    if end + 0.10 <= end_index:
                        k = k + (10-(round(k*100)%10))/100
                    else:
                        k = end

                else: # if r >= 0:
                    #logger.debug("----Second---- Custom criteria for Line Item is =  %f", k)
                    subCustomValueArray.append(k)
                    k = k + sub_granu
            else: # if round(k*100)%10) > 0 or sub_granu == 0.01
                if r > 0 and round(k+sub_granu,2) > round(end_index,2):
                    # To create the custom value from 10 to granularity which can .5, so 10-14
                    g = None
                    if granu > 1:
                        g = 0.10
                    else:
                        g = 0.01

                    v = k
                    while round(v,2) < round(end_index,2):
                        temp = v
                        if granu > 1:
                            temp = round(temp, 1)
                        else:
                            temp = round(temp, 2)

                        if v+g > end_index and round(v+g,2) != round(end_index,2):
                            subCustomValueArray.append("{0:.2f}".format(temp))
                            #logger.debug("----Third---- Custom criteria for Line Item is =  %.2f", subCustomValueArray[-1])
                            g = 0.01
                            v = v + g
                            continue

                        if g == 0.10:
                            subCustomValueArray.append("{0:.1f}".format(v))
                        else:
                            subCustomValueArray.append("{0:.2f}".format(v))

                        #logger.debug("----Third---- Custom criteria for Line Item is =  %s", subCustomValueArray[-1])
                        v = v + g

                    k = k + sub_granu
                elif k == 0: # if r > 0 and round(k+sub_granu,2) > round(end_index,2)
                    vEnd = None
                    if sub_granu < 0.10:
                        vEnd = granu
                    else:
                        vEnd = 0.10

                    v = 0.01
                    while v <= vEnd-0.01:
                        subCustomValueArray.append(str(round(v,2)))
                        #logger.debug("----Fourth---- Custom criteria for Line Item is =  %s", subCustomValueArray[-1])
                        v = v + 0.01

                    k = k + vEnd
                else:
                    if sub_granu != 1:
                        k = round(k,1)

                    if ((round(k*10)) % 10 != 0 or sub_granu ==0.10) and (round(k+sub_granu,2) <= round(end_index,2)):
                        subCustomValueArray.append(str(round(k,2)))
                        #logger.debug("----fifth----1 Custom criteria for Line Item is =  %s", subCustomValueArray[-1])
                    elif (k+sub_granu > end_index and granu == 1) or (granu> 1 and k + sub_granu >end_index):
                        subCustomValueArray.append("{0:.1f}".format(k))
                        #logger.debug("----fifth----2 Custom criteria for Line Item is =  %s", subCustomValueArray[-1])
                    elif sub_granu == 0.10 and round(k+sub_granu,2) > round(end_index,2) and end_index*100%10 >0:
                        subCustomValueArray.append("{0:.2f}".format(k))
                        #logger.debug("----fifth----2.5 Custom criteria for Line Item is =  %s", subCustomValueArray[-1])
                    else:
                        subCustomValueArray.append("{0}.".format(int(k)))
                        #logger.debug("----fifth----3 Custom criteria for Line Item is =  %s", subCustomValueArray[-1])

                    if k >= 1 and round(k*10)%10==0 and k+sub_granu <= end_index: #if $k=2 and end range is 2.57 then it should not increment to 3 while granu is 1
                        k = k+sub_granu
                    elif sub_granu == 0.10 and (round(k+sub_granu,2) > round(end_index,2) and end_index*100%10 > 0): #$end_index*100%10>0 and $sub_granu==0.10 and $k+$sub_granu>$end_index)
                        k = k + 0.01
                    else:
                        k = round(k,2) + 0.10

                    if (round(k,2) != round(end_index,2)) and (round(k+0.10,2) != round (end_index,2)) and ((k+0.10 > end_index and granu == 1) or (k + 0.10 > end_index and granu>1)):
                        subCustomValueArray.append("{0:.2f}".format(k))
                        #logger.debug("----fifth----4 Custom criteria for Line Item is =  %s", subCustomValueArray[-1])
                        k = k + 0.01
        logger.debug("Custom price targetting for each lineitem: {}".format( subCustomValueArray))
        return subCustomValueArray

def setup_partner(user_email, advertiser_name, advertiser_type, order_name, placements,
     sizes, lineitem_type, lineitem_prefix, bidder_code, prices, setup_type, creative_template, num_creatives, use_1x1,
     currency_code, custom_targeting, same_adv_exception, device_categories, device_capabilities, roadblock_type, slot , adpod_creative_durations, creative_user_def_var, deal_config, deal_lineitem_enabled):
  """
  Call all necessary DFP tasks for a new Prebid partner setup.
  """

  order_count = 1
  total_lineitem_count = 0
  slot_order_name = ''
  order_id = 0

  # Get the user.
  user_id = dfp.get_users.get_user_id_by_email(user_email)

  # Get the placement IDs.
  placement_ids = None
  ad_unit_ids = None
  if len(placements) > 0:
      placement_ids = dfp.get_placements.get_placement_ids_by_name(placements)
  else:
      # Run of network
      root_id = dfp.get_root_ad_unit_id.get_root_ad_unit_id()
      ad_unit_ids = [ root_id ]

  # Get the device category IDs
  # Dont get device categories for in-app and jwplayer platform
  device_category_ids = None
  if device_categories != None and setup_type not in (constant.IN_APP, constant.IN_APP_VIDEO, constant.IN_APP_NATIVE, constant.JW_PLAYER):
      device_category_ids = []
      if isinstance(device_categories, str):
          device_categories = (device_categories)

      dc_map = dfp.get_device_categories.get_device_categories()

      for dc in device_categories:
          if dc in dc_map:
              device_category_ids.append(dc_map[dc])
          else:
              raise BadSettingException("Invalid Device Cagetory: {} ".format(dc))


  #get device capabilty ids for in-APP platform
  device_capability_ids = None
  if device_capabilities != None and setup_type in (constant.IN_APP, constant.IN_APP_VIDEO, constant.IN_APP_NATIVE):
    device_capability_ids = []
    if isinstance(device_capabilities, str):
        device_capabilities = (device_capabilities)

    dc_map = dfp.get_device_capabilities.get_device_capabilities()

    for dc in device_capabilities:
        if dc in dc_map:
            device_capability_ids.append(dc_map[dc])
        else:
            raise BadSettingException("Invalid Device Capability: {} ".format(dc))


  # Get (or potentially create) the advertiser.
  advertiser_id = dfp.get_advertisers.get_advertiser_id_by_name(
    advertiser_name, advertiser_type)
 
  if setup_type  == constant.ADPOD and deal_lineitem_enabled == False:
    order = get_existing_order_details(slot, order_name)
    order_id = order['id']
    total_lineitem_count  = order['lic'] 
    order_count = order['order_count'] 
    
    if order_id != 0 and total_lineitem_count > 0:
        logger.info(
        'Using existing order with name "{name}".'.format(name=order['name']))
        order_list.append(order['name'])
    
    for p in prices:
        if total_lineitem_count % constant.LINE_ITEMS_LIMIT == 0:
            slot_order_name  = str(slot) + "_" + str(order_count) + "_" + order_name  
            order_count = order_count + 1
            order_id = dfp.create_orders.create_order(slot_order_name, advertiser_id, user_id)
            order_list.append(slot_order_name)
        p['order_id'] = order_id
        total_lineitem_count = total_lineitem_count + 1 
  else:
    order_id = dfp.create_orders.create_order(order_name, advertiser_id, user_id)

  # Create creatives.
  #Get creative template for native platform
  creative_template_ids = None
  if setup_type == constant.NATIVE or setup_type == constant.IN_APP_NATIVE:
      creative_template_ids = dfp.get_creative_template.get_creative_template_ids_by_name(creative_template)

  #if bidder is None, then bidder will be 'All'
  bidder_str = bidder_code
  if bidder_str == None:
      bidder_str = "All"
  elif isinstance(bidder_str, (list, tuple)):
      bidder_str = "_".join(bidder_str)

  #generate unique id that will be used for creative and line item naming
  unique_id = get_unique_id(setup_type)

  #create creatives
  if setup_type == 'ADPOD':
      logger.info('\nCreating creatives for slot {}...'.format(slot)) 
  else:
      logger.info("\ncreating creatives...")

  size_arg = sizes
  if use_1x1:
      size_arg = None

  creative_configs = get_creative_config(setup_type, bidder_str, order_name, advertiser_id, size_arg, num_creatives, creative_template_ids,  prefix=unique_id, adpod_creative_durations=adpod_creative_durations, slot=slot, creative_user_def_var=creative_user_def_var)
  creative_ids = dfp.create_creatives.create_creatives(creative_configs)
  
  # if platform is video, create creative sets
  if setup_type in (constant.VIDEO, constant.IN_APP_VIDEO, constant.JW_PLAYER):
      creative_set_configs = dfp.create_creative_sets.create_creative_set_config(creative_ids, sizes, unique_id)
      creative_ids = dfp.create_creative_sets.create_creative_sets(creative_set_configs)
  if setup_type == constant.ADPOD:
      creative_set_configs = dfp.create_creative_sets.create_creative_set_config_adpod(creative_ids, sizes, unique_id, adpod_creative_durations, slot)
      creative_ids = dfp.create_creative_sets.create_creative_sets(creative_set_configs)

  # Create line items.
  # if line item prefix is not passed, set unique id as lineitem prefix
  if lineitem_prefix is None:
      lineitem_prefix = unique_id

  if setup_type == 'ADPOD':
      logger.info('\nCreating line_itmes for slot {}...'.format(slot))
  else:
      logger.info("\ncreating line_items...")

  if setup_type == constant.ADPOD and deal_lineitem_enabled == True:
      line_items_config = create_deal_line_item_configs(deal_config, order_id,
      placement_ids, bidder_code, sizes, OpenWrapTargetingKeyGen(), lineitem_type, lineitem_prefix,
      currency_code, custom_targeting, setup_type, ad_unit_ids=ad_unit_ids, same_adv_exception=same_adv_exception,
      device_category_ids=None, device_capability_ids=None, roadblock_type=roadblock_type,durations=adpod_creative_durations,slot=slot)
       
  else:    
      line_items_config = create_line_item_configs(prices, order_id,
      placement_ids, bidder_code, sizes, OpenWrapTargetingKeyGen(), lineitem_type, lineitem_prefix,
      currency_code, custom_targeting, setup_type, creative_template_ids, same_adv_exception=same_adv_exception,ad_unit_ids=ad_unit_ids,
      device_category_ids=device_category_ids, device_capability_ids=device_capability_ids, roadblock_type=roadblock_type,durations=adpod_creative_durations,slot=slot)
  
  line_item_ids = dfp.create_line_items.create_line_items(line_items_config)

  # Associate creatives with line items.
  size_overrides = []
  if use_1x1 and setup_type is not (constant.NATIVE or constant.IN_APP_NATIVE):
      size_overrides = sizes

  if setup_type == 'ADPOD':
      logger.info("\nCreating lineitem creative associations for slot {}...".format(slot))
  else:
      logger.info("\nCreating lineitem creative associations...")

  dfp.associate_line_items_and_creatives.make_licas(line_item_ids,
      creative_ids, size_overrides=size_overrides, setup_type=setup_type,slot=slot,durations=adpod_creative_durations)
    

def print_summary(order_name,advertiser_name,advertiser_type,adpod_size, adpod_creative_durations, deal_config, adpod_slots, lineitem_type,  lineitem_prefix,
        setup_type, user_email, placements_print, sizes, custom_targeting, same_adv_exception, bidder_code, roadblock_type):

    dealtiers=[]
    li_count = 0
    for bidder, cfg in deal_config.items():
      li_count = li_count + len(cfg[constant.PREFIX]) * len(cfg[constant.MIN_DEAL_TIER])
      for prefix in cfg[constant.PREFIX]:
        for mdt in cfg[constant.MIN_DEAL_TIER]:
            dealtiers.append(prefix + str(mdt))  

    logger.info(
      u"""
      ADPOD Details :
      
      {name_start_format}Order{format_end}: {value_start_format}{order_name}{format_end}
      {name_start_format}Advertiser{format_end}: {value_start_format}{advertiser}{format_end}
      {name_start_format}Advertiser Type{format_end}: {value_start_format}{advertiser_type}{format_end}
      {name_start_format}LineItem Type{format_end}: {value_start_format}{lineitem_type}{format_end}
      {name_start_format}LineItem Prefix{format_end}: {value_start_format}{lineitem_prefix}{format_end}
      {name_start_format}Setup Type{format_end} = {value_start_format}{setup_type}{format_end}
      {name_start_format}Adpod Size{format_end}: {value_start_format}{adpod_size}{format_end}
      {name_start_format}Adpod slot positions{format_end}: {value_start_format}{adpod_slot}{format_end}
      {name_start_format}Adpod creative Durations{format_end}: {adpod_creative_durations}{format_end}
      {name_start_format}Line Item per each slot{format_end}: {value_start_format}{lineitem_per_slot}{format_end}
      {name_start_format}Creatives per each slot{format_end}: {value_start_format}{creatives_per_slot}{format_end}
      {name_start_format}Total number of Line Items{format_end}: {value_start_format}{lineitem_total}{format_end}
      {name_start_format}Total number of Creatives{format_end}: {value_start_format}{creatives_total}{format_end}      
      {name_start_format}LineItem Type{format_end}: {value_start_format}{lineitem_type}{format_end}      
      {name_start_format}Deal Config{format_end}: {value_start_format}{deal_config}{format_end}            
      
      Line items will have targeting:
      {name_start_format}Dealtiers{format_end} = {value_start_format}{dealtiers}{format_end}
      {name_start_format}Bidders{format_end} = {value_start_format}{bidder_code}{format_end}
      {name_start_format}Placements{format_end} = {value_start_format}{placements}{format_end}
      {name_start_format}Custom targeting{format_end} = {value_start_format}{custom_targeting}{format_end}
      {name_start_format}Same advertiser exception{format_end} = {value_start_format}{same_adv_exception}{format_end}
      {name_start_format}Roadblock type{format_end} = {value_start_format}{roadblock_type}{format_end}
  
      """.format(
        order_name=order_name,
        advertiser=advertiser_name,
        advertiser_type=advertiser_type,
        lineitem_type=lineitem_type,
        lineitem_prefix=lineitem_prefix,
        setup_type=setup_type,
        user_email=user_email,
        adpod_size = adpod_size,
        adpod_slot = adpod_slots,
        lineitem_per_slot = li_count,
        lineitem_total = li_count*adpod_size,
        adpod_creative_durations = adpod_creative_durations,
        creatives_per_slot= len(adpod_creative_durations),
        creatives_total= adpod_size * len(adpod_creative_durations),
        deal_config = deal_config,
        dealtiers = dealtiers,
        bidder_code = bidder_code,
        placements=placements_print,
        sizes=sizes,
        custom_targeting=custom_targeting,
        same_adv_exception=same_adv_exception,
        roadblock_type=roadblock_type,
        name_start_format=color.BOLD,
        format_end=color.END,
        value_start_format=color.BLUE,
    ))  


def get_creative_file(setup_type):
    creative_file = "creative_snippet_openwrap.html"
    if setup_type == constant.WEB:
        creative_file = "creative_snippet_openwrap.html"
    elif setup_type == constant.WEB_SAFEFRAME:
        creative_file = "creative_snippet_openwrap_sf.html"
    elif setup_type == constant.AMP:
        creative_file = "creative_snippet_openwrap_amp.html"
    elif setup_type == constant.IN_APP:
        creative_file = "creative_snippet_openwrap_in_app.html"

    return creative_file

def create_deal_line_item_configs(deal_config, order_id, placement_ids, bidder_code, sizes, key_gen_obj,
  lineitem_type, lineitem_prefix, currency_code, custom_targeting, setup_type, ad_unit_ids=None, same_adv_exception=False, 
  device_category_ids=None,device_capability_ids=None, roadblock_type='ONE_OR_MORE', durations = None, slot = None):
  """
  Create a line item config for each dealtier.

  Args:
    prices (array)
    order_id (int)
    placement_ids (arr)
    bidder_code (str or arr)
    sizes (arr)
    key_gen_obj (obj)
    lineitem_type (str)
    lineitem_prefix (str)
    currency_code (str)
    custom_targeting (arr)
    setup_type (str)
    creative_template_ids (arr)
    ad_unit_ids (arr)
    same_adv_exception(bool)
    device_category_ids (int)
    device_capability_ids (int)
    roadblock_type (str)
    durations(array)
    slot(string) 
  Returns:
    an array of objects: the array of DFP line item configurations
  """

 
  key_gen_obj.set_setup_type(setup_type)

  # Set DFP targeting for custom targetting passed in settings.py
  key_gen_obj.set_custom_targeting(custom_targeting)
  key_gen_obj.set_creative_targeting(durations,slot)  

  line_items_config = []
     
  #create line item config for each price
  for bidder, cfg in deal_config.items():
    if bidder_code is not None:
        found = False
        for bc in bidder_code:
            if bidder == bc:
                found = True
                break
        if found == True:
            key_gen_obj.set_bidder_value(bidder_code, slot)
        else:
            key_gen_obj.set_bidder_value(None, slot)
 
    for prefix in cfg[constant.PREFIX]:
        for mdt in cfg[constant.MIN_DEAL_TIER]:
            dealtier = prefix + str(mdt)
            key_gen_obj.set_deal_tier(slot, dealtier)
            # Autogenerate the line item name. (prefix_rate)
            line_item_name = '{}_{}_{}_{}'.format(slot, lineitem_prefix, bidder, dealtier)

            config = dfp.create_line_items.create_line_item_config(
              name=line_item_name,
              order_id=order_id,
              placement_ids=placement_ids,
              cpm_micro_amount=num_to_micro_amount(round(cfg['price'],2)),
              sizes=sizes,
              key_gen_obj=key_gen_obj,
              lineitem_type=lineitem_type,
              currency_code=currency_code,
              setup_type=setup_type,
              creative_template_ids=None,
              ad_unit_ids=ad_unit_ids,
              same_adv_exception=same_adv_exception,
              device_categories=device_category_ids,
              device_capabilities=device_capability_ids,
              roadblock_type=roadblock_type,
              durations=durations,
              slot=slot
            )

            line_items_config.append(config)

  return line_items_config


def create_line_item_configs(prices, order_id, placement_ids, bidder_code, sizes, key_gen_obj,
  lineitem_type, lineitem_prefix, currency_code, custom_targeting, setup_type, creative_template_ids,
  ad_unit_ids=None, same_adv_exception=False, device_category_ids=None,device_capability_ids=None,
  roadblock_type='ONE_OR_MORE', durations = None, slot = None):
  """
  Create a line item config for each price bucket.

  Args:
    prices (array)
    order_id (int)
    placement_ids (arr)
    bidder_code (str or arr)
    sizes (arr)
    key_gen_obj (obj)
    lineitem_type (str)
    lineitem_prefix (str)
    currency_code (str)
    custom_targeting (arr)
    setup_type (str)
    creative_template_ids (arr)
    ad_unit_ids (arr)
    same_adv_exception(bool)
    device_category_ids (int)
    device_capability_ids (int)
    roadblock_type (str)
    durations(array)
    slot(string) 
  Returns:
    an array of objects: the array of DFP line item configurations
  """

  if setup_type is not constant.ADPOD:
      key_gen_obj.init_keys()

  key_gen_obj.set_setup_type(setup_type)

  # Set DFP custom targeting for key `pwtpid` based on bidder code
  key_gen_obj.set_bidder_value(bidder_code, slot)

  # Set DFP targeting for custom targetting passed in settings.py
  key_gen_obj.set_custom_targeting(custom_targeting)

  #do not set platform targeting for jwplayer, adpod
  if setup_type not in (constant.JW_PLAYER, constant.ADPOD):
      key_gen_obj.set_platform_targetting()

  if setup_type is constant.JW_PLAYER:
      key_gen_obj.set_jwplayer_key()

  if setup_type is constant.ADPOD:  
     key_gen_obj.set_creative_targeting(durations,slot)  

  line_items_config = []

  #create line item config for each price
  for price in prices:
    if setup_type ==constant.ADPOD:
        price_str = num_to_str(price['rate'], precision=2)
        order_id = price['order_id']
    else:    
        price_str = num_to_str(price['rate'], precision=3)

    # Remove trailing zero if exists
    if re.match("\d+\.\d{2}0",price_str):
        price_str = price_str[0:-1]

    bidder_str = bidder_code
    if bidder_str == None:
        bidder_str = "All"
    elif isinstance(bidder_str, (list, tuple)):
        bidder_str = "_".join(bidder_str)

    # Autogenerate the line item name. (prefix_rate)
    if setup_type == 'ADPOD':
        line_item_name = '{}_{}_{}'.format(slot, lineitem_prefix, price_str)
    else:
        line_item_name = '{}_{}'.format(lineitem_prefix, price_str)
    
    # Set DFP custom targeting for key `pwtecp`
    if setup_type is not constant.ADPOD:
        key_gen_obj.set_price_value(price)

     # Set DFP custom targeting for key `pwtpb`
    if setup_type  == constant.ADPOD:
        key_gen_obj.set_bid_price(slot, num_to_str(price['start'], precision=2))
  
    config = dfp.create_line_items.create_line_item_config(
      name=line_item_name,
      order_id=order_id,
      placement_ids=placement_ids,
      cpm_micro_amount=num_to_micro_amount(round(price['rate'],2)),
      sizes=sizes,
      key_gen_obj=key_gen_obj,
      lineitem_type=lineitem_type,
      currency_code=currency_code,
      setup_type=setup_type,
      creative_template_ids=creative_template_ids,
      ad_unit_ids=ad_unit_ids,
      same_adv_exception=same_adv_exception,
      device_categories=device_category_ids,
      device_capabilities=device_capability_ids,
      roadblock_type=roadblock_type,
      durations=durations,
      slot=slot
    )

    line_items_config.append(config)

  return line_items_config

#This method returns creative config based on the creative type
def get_creative_config(setup_type, bidder_str, order_name, advertiser_id, sizes, num_creatives,
    creative_template_ids, prefix, adpod_creative_durations=None, slot= None, creative_user_def_var=None):

    creative_configs= []
    if setup_type == constant.NATIVE or setup_type == constant.IN_APP_NATIVE:
        creative_configs = dfp.create_creatives.create_creative_configs_for_native(advertiser_id, creative_template_ids, num_creatives, prefix, creative_user_def_var)
    elif setup_type == constant.VIDEO:
        creative_configs = dfp.create_creatives.create_creative_configs_for_video(advertiser_id, sizes, prefix, constant.VIDEO_VAST_URL, constant.VIDEO_DURATION)
    elif setup_type == constant.IN_APP_VIDEO:
        creative_configs = dfp.create_creatives.create_creative_configs_for_video(advertiser_id, sizes, prefix, constant.SDK_VIDEO_VAST_URL, constant.SDK_VIDEO_DURATION)
    elif setup_type == constant.JW_PLAYER:
        creative_configs = dfp.create_creatives.create_creative_configs_for_video(advertiser_id, sizes, prefix, constant.JWP_VAST_URL, constant.JWP_DURATION)
    elif setup_type == constant.ADPOD:
        creative_configs = dfp.create_creatives.create_creative_configs_for_adpod(advertiser_id, sizes, prefix,constant.ADPOD_VIDEO_VAST_URL, adpod_creative_durations, slot)
    else:
        use_safe_frame = False
        if setup_type in (constant.WEB_SAFEFRAME, constant.AMP):
          use_safe_frame = True
        creative_file = get_creative_file(setup_type)
        creative_configs = dfp.create_creatives.create_duplicate_creative_configs(
          bidder_str, order_name, advertiser_id, sizes, num_creatives, creative_file=creative_file, safe_frame=use_safe_frame, prefix=prefix)

    return creative_configs

def get_existing_order_details(slot, order_name):

    count = 1
    while True:
        orderName =  str(slot) + "_" + str(count) + "_" + order_name  
        order = dfp.get_orders.get_order_by_name(orderName)
        if order is None:
            return {
                    'id': 0,
                    'order_count': count,
                    'lic': 0,
                    'name': orderName 
                }  
        
        orderId = order['id']
        lic = dfp.get_line_items.get_line_item_count_by_order(orderId)
        if lic < constant.LINE_ITEMS_LIMIT:
           return {
               'id': orderId,
               'order_count': count,
               'lic': lic,
               'name': orderName
           } 
        count = count+1
     
def get_unique_id(setup_type):

    uid = shortuuid.uuid()
    if setup_type in (constant.WEB, constant.WEB_SAFEFRAME):
        uid = u'DISPLAY_{}'.format(uid)
    if setup_type is constant.AMP:
        uid = u'AMP_{}'.format(uid)
    if setup_type is constant.IN_APP:
        uid = u'INAPP_{}'.format(uid)
    if setup_type is constant.IN_APP_VIDEO:
        uid = u'INAPP_VIDEO_{}'.format(uid)
    if setup_type is constant.IN_APP_NATIVE:
        uid = u'INAPP_NATIVE_{}'.format(uid)
    if setup_type is constant.NATIVE:
        uid = u'NATIVE_{}'.format(uid)
    if setup_type is constant.VIDEO:
        uid = u'VIDEO_{}'.format(uid)
    if setup_type is constant.JW_PLAYER:
        uid = u'JWP_{}'.format(uid)
    if setup_type is constant.ADPOD:
        uid = u'VIDEO_{}'.format(uid)
    return uid

def get_calculated_rate(start_rate_range, end_rate_range, rate_id, exchange_rate, precision):

    if(start_rate_range == 0 and rate_id == 2):
        rate_id = 1

    if rate_id == 2:
        return round(start_rate_range * exchange_rate, precision)
    else:
        return round(((start_rate_range + end_rate_range) / 2.0) * exchange_rate, precision)


def get_dfp_network():
    current_network = dfp.get_network.get_dfp_network()
    return current_network

def get_exchange_rate(currency_code):
    if currency_code.upper() == "USD":
        return float(1)
    #currency_code = 'GBP'
    url = "http://api.currencylayer.com/live?access_key=55586212cb183ad61a879b07d76e1d47&source=USD&currencies=" + currency_code +"&format=1"

    response = urlopen(url)
    string = response.read().decode('utf-8')
    json_obj = json.loads(string)
    return float(json_obj['quotes']['USD' + currency_code])


def load_price_csv(filename, setup_type):
    buckets = []
    exchange_rate = 1

    #read currency conversion flag
    currency_exchange = True

    precision = 3 
    if setup_type == constant.ADPOD:
        currency_exchange = False
        precision = 2

    # Currency module/CURRENCY_EXCHANGE is applicable for web and native platform
    if setup_type in (constant.WEB, constant.WEB_SAFEFRAME, constant.NATIVE, constant.IN_APP, constant.IN_APP_VIDEO):
        currency_exchange = getattr(settings, 'CURRENCY_EXCHANGE', True)

    if currency_exchange:
        network = get_dfp_network()
        logger.info("Network currency : %s", network.currencyCode)
        exchange_rate = get_exchange_rate(network.currencyCode)

    logger.info("Currency exchange rate: {}".format(exchange_rate))
    #currency rate handling till here
    with open(filename, 'r') as csvfile:
        preader = csv.reader(csvfile)
        next(preader)  # skip header row
        for row in preader:
                # ignore extra lines or spaces
                if row == [] or row[0].strip() == "":
                    continue
                print(row)

                try:
                    start_range = float(row[2])
                    end_range = float(row[3])
                    granularity = float(row[4])
                    rate_id = int(row[5])
                    if setup_type == constant.ADPOD:
                        rate_id = 2
                except ValueError:
                    raise BadSettingException('Start range, end range, granularity and rate id should be number. Please correct the csv and try again.')

                validateCSVValues(start_range, end_range, granularity, rate_id)

                if granularity != -1:
                    i = start_range
                    while i < end_range:
                        a = round(i + granularity,2)
                        if a > end_range:
                            a = end_range

                        if round(i,2) != (a,2):
                             buckets.append({
                                'start': i,
                                'end': a,
                                'granularity': granularity,
                                'rate': get_calculated_rate(i, a, rate_id, exchange_rate, precision)
                             })
                        i = a
                else:
                     buckets.append({
                        'start': start_range,
                        'end': end_range,
                        'granularity': 1.0,
                        'rate': get_calculated_rate(start_range, end_range, rate_id, exchange_rate, precision)
                     })

    return buckets

def validateCSVValues(start_range, end_range, granularity, rate_id):
    if start_range < 0 or end_range < 0 :
        raise BadSettingException('Start range and end range can not be negative. Please correct the csv and try again.')

    if start_range > end_range:
        raise BadSettingException('Start range can not be more than end range. Please correct the csv and try again.')

    if rate_id not in (1,2):
        raise BadSettingException('Rate id can only be 1 or 2. Please correct the csv and try again')

    if start_range < 0.01 and granularity == 0.01:
        raise BadSettingException('Start range can not be less than 0.01 for granularity 0.01, either increase granularity or start range in csv.')

    if end_range > 999:
        raise BadSettingException('End range can not be more then 999. Please correct the csv and try again.')

    if granularity == 0:
        raise BadSettingException('Zero is not accepted as granularity. Please correct the csv and try again')

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

  advertiser_type = getattr(settings, 'DFP_ADVERTISER_TYPE', "ADVERTISER")
  if advertiser_type != "ADVERTISER" and advertiser_type != "AD_NETWORK":
    raise BadSettingException('DFP_ADVERTISER_TYPE')

  order_name = getattr(settings, 'DFP_ORDER_NAME', None)
  if order_name is None:
    raise MissingSettingException('DFP_ORDER_NAME')

  lineitem_type = getattr(settings, 'DFP_LINEITEM_TYPE', None)
  if lineitem_type is None:
    raise MissingSettingException('DFP_LINEITEM_TYPE')


  num_placements = 0
  placements = getattr(settings, 'DFP_TARGETED_PLACEMENT_NAMES', None)
  placements_print = str(placements)
  if placements is None:
    placements = []
    placements_print = "RON"

  # if no placements are specified, we wil do run of network which is
  #   effectively one placement
  num_placements = len(placements)
  if num_placements == 0:
      num_placements = 1
      placements_print = "RON"

  setup_type = getattr(settings, 'OPENWRAP_SETUP_TYPE', None)
  if setup_type is None:
    setup_type = constant.WEB
  elif setup_type not in [constant.WEB, constant.WEB_SAFEFRAME, constant.AMP, constant.IN_APP, constant.IN_APP_VIDEO, constant.IN_APP_NATIVE,
    constant.NATIVE, constant.VIDEO, constant.JW_PLAYER, constant.ADPOD]:
    raise BadSettingException('Unknown OPENWRAP_SETUP_TYPE: {0}'.format(setup_type))
  
  deal_config = None
  deal_lineitem_enabled = False
  if setup_type == constant.ADPOD:
    deal_lineitem_enabled = getattr(settings, 'ENABLE_DEAL_LINEITEM', False)
    deal_config = getattr(settings, 'DEAL_CONFIG', None)
    adpod_creative_cache_url = getattr(settings, 'ADPOD_CREATIVE_CACHE_URL', constant.DEFAULT_APDOD_CACHE_URL)  
    constant.ADPOD_VIDEO_VAST_URL =  constant.ADPOD_VIDEO_VAST_URL.replace("{url}",adpod_creative_cache_url)
  
  adpod_slots = getattr(settings, 'ADPOD_SLOTS', None)
  adpod_size = len(adpod_slots)

  if setup_type == constant.ADPOD and (adpod_slots == None or len(adpod_slots) == 0):
    raise MissingSettingException('The setting "ADPOD_SLOTS" must contain alteast one slot.')

  if  (setup_type == constant.ADPOD and deal_lineitem_enabled == True) and lineitem_type != constant.LI_SPONSORSHIP:
     raise  BadSettingException('DFP_LINEITEM_TYPE should be SPONSORSHIP for creating deal lineitems')
 
  if (setup_type == constant.ADPOD and deal_lineitem_enabled == True) and deal_config is None:
     raise  MissingSettingException('Set valid DEAL_CONFIG for creating deal lineitems')
 
  adpod_creative_durations = getattr(settings, 'VIDEO_LENGTHS', None)
  if setup_type == constant.ADPOD and adpod_creative_durations is None:
    raise MissingSettingException('VIDEO_LENGTHS')
  elif setup_type == constant.ADPOD and len(adpod_creative_durations) < 1:
    raise MissingSettingException('The setting "VIDEO_LENGTHS" must contain alteast one durations.')

  sizes = getattr(settings, 'DFP_PLACEMENT_SIZES', None)
  if setup_type not in [constant.NATIVE]:
    if sizes is None:
        raise MissingSettingException('DFP_PLACEMENT_SIZES')
    elif setup_type == constant.ADPOD and len(sizes) != 1:
        raise BadSettingException('The setting "DFP_PLACEMENT_SIZES" '
        'for ADPOD Setup should only have one size object.')   
    elif len(sizes) < 1:
        raise BadSettingException('The setting "DFP_PLACEMENT_SIZES" '
        'must contain at least one size object.')

  currency_code = getattr(settings, 'DFP_CURRENCY_CODE', 'USD')

  # How many creatives to attach to each line item. We need at least one
  # creative per ad unit on a page. See:
  # https://github.com/kmjennison/dfp-prebid-setup/issues/13
  num_creatives = (
    getattr(settings, 'DFP_NUM_CREATIVES_PER_LINE_ITEM', None) or
    num_placements
  )


  # read creative template for native Line-items
  creative_template = None
  creative_user_def_var = None
  if setup_type == constant.NATIVE or setup_type == constant.IN_APP_NATIVE:
      creative_template = getattr(settings, 'OPENWRAP_CREATIVE_TEMPLATE', None)
      if creative_template is None:
        raise MissingSettingException('OPENWRAP_CREATIVE_TEMPLATE')
      elif not isinstance (creative_template, (list, str)):
        raise BadSettingException('OPENWRAP_CREATIVE_TEMPLATE')
      if isinstance (creative_template, str):
          creative_template = [creative_template]

      if setup_type == constant.IN_APP_NATIVE:
        creative_user_def_var = 'pubmatic-ow-signal:%%PATTERN:pwtsid%%'
      else:
        creative_user_def_var = getattr(settings, 'OPENWRAP_NATIVE_CREATIVE_USER_DEFINED_VAR', None)

  bidder_code = getattr(settings, 'PREBID_BIDDER_CODE', None)
  if bidder_code is not None and not isinstance(bidder_code, (list, tuple, str)):
    raise BadSettingException('PREBID_BIDDER_CODE')

  same_adv_exception = getattr(settings, 'DFP_SAME_ADV_EXCEPTION', False)
  if not isinstance(same_adv_exception, bool):
      raise BadSettingException('DFP_SAME_ADV_EXCEPTION')

  device_categories = getattr(settings, 'DFP_DEVICE_CATEGORIES', None)
  if device_categories is not None and not isinstance(device_categories, (list, tuple, str)):
       raise BadSettingException('DFP_DEVICE_CATEGORIES')

  device_capabilities = None
  roadblock_type = getattr(settings, 'DFP_ROADBLOCK_TYPE', 'ONE_OR_MORE')
  if roadblock_type not in ('ONE_OR_MORE', 'AS_MANY_AS_POSSIBLE'):
      raise BadSettingException('DFP_ROADBLOCK_TYPE')

  lineitem_prefix = getattr(settings, 'LINE_ITEM_PREFIX', None)
  if lineitem_prefix != None:
      if not isinstance(lineitem_prefix, (str)):
        raise BadSettingException('LINE_ITEM_PREFIX')

  use_1x1 = getattr(settings, 'OPENWRAP_USE_1x1_CREATIVE', False)
  if not isinstance(use_1x1, bool):
      raise BadSettingException('OPENWRAP_USE_1x1_CREATIVE')

  custom_targeting = getattr(settings, 'OPENWRAP_CUSTOM_TARGETING', None)
  if custom_targeting != None:
      if not isinstance(custom_targeting, (list, tuple)):
          raise BadSettingException('OPENWRAP_CUSTOM_TARGETING')

      for ct in custom_targeting:
         if len(ct) != 3:
             raise BadSettingException('OPENWRAP_CUSTOM_TARGETING')

         if ct[1] != "IS" and ct[1] != "IS_NOT":
             raise BadSettingException('OPENWRAP_CUSTOM_TARGETING')

         if not isinstance(ct[2], (list, tuple, str, bool)):
             raise BadSettingException('OPENWRAP_CUSTOM_TARGETING - {0}'.format(type(ct[2])))

  prices = None  
  # Calculate price only for price based lineitems   
  if deal_lineitem_enabled == False :
    price_buckets_csv = getattr(settings, 'OPENWRAP_BUCKET_CSV', None)
    if price_buckets_csv is None:
        raise MissingSettingException('OPENWRAP_BUCKET_CSV')

    prices = load_price_csv(price_buckets_csv, setup_type)

    prices_summary = []
    for p in prices:
        prices_summary.append(p['rate'])
    
    if len(prices) > constant.LINE_ITEMS_LIMIT and setup_type != constant.ADPOD:
        print('\n Error: {} Lineitems will be created. This is exceeding Line items count per order of {}!\n'
        .format(len(prices),constant.LINE_ITEMS_LIMIT)) 
        return

  # set bidder_code, custom_targetting, device categories to None when setup_type is IN-APP, JW_PLAYER
  # default roadblock_type to ONE_OR_MORE when setup_type is VIDEO, JW_PLAYER
  # default roadblock type to 'AS_MANY_AS_POSSIBLE' when setup_type is in-app

  if setup_type == constant.IN_APP:
      roadblock_type = 'AS_MANY_AS_POSSIBLE'
      device_categories = None
  elif setup_type == constant.IN_APP_VIDEO:
      roadblock_type = 'ONE_OR_MORE'
      device_categories = None
  elif setup_type == constant.JW_PLAYER:
      roadblock_type = 'ONE_OR_MORE'
      bidder_code = ['pubmatic']
      custom_targeting = None
      device_categories = None
  elif setup_type == constant.VIDEO:
      roadblock_type = 'ONE_OR_MORE'
  elif setup_type == constant.ADPOD:
      roadblock_type = 'ONE_OR_MORE'

    
  if deal_lineitem_enabled == False: 
    # Prininting non adpod lineitem summary
    logger.info(
        u"""

        Going to create {name_start_format}{num_line_items}{format_end} new line items.
        {name_start_format}Order{format_end}: {value_start_format}{order_name}{format_end}
        {name_start_format}Advertiser{format_end}: {value_start_format}{advertiser}{format_end}
        {name_start_format}Advertiser Type{format_end}: {value_start_format}{advertiser_type}{format_end}
        {name_start_format}LineItem Type{format_end}: {value_start_format}{lineitem_type}{format_end}
        {name_start_format}LineItem Prefix{format_end}: {value_start_format}{lineitem_prefix}{format_end}
        {name_start_format}Setup Type{format_end} = {value_start_format}{setup_type}{format_end}
        {name_start_format}Use 1x1 Creative{format_end} = {value_start_format}{use_1x1}{format_end}
            
        Line items will have targeting:
        {name_start_format}rates{format_end} = {value_start_format}{prices_summary}{format_end}
        {name_start_format}bidders{format_end} = {value_start_format}{bidder_code}{format_end}
        {name_start_format}placements{format_end} = {value_start_format}{placements}{format_end}
        {name_start_format}custom targeting{format_end} = {value_start_format}{custom_targeting}{format_end}
        {name_start_format}same advertiser exception{format_end} = {value_start_format}{same_adv_exception}{format_end}
        {name_start_format}device categories{format_end} = {value_start_format}{device_categories}{format_end}
        {name_start_format}device capabilities{format_end} = {value_start_format}{device_capabilities}{format_end}
        {name_start_format}roadblock type{format_end} = {value_start_format}{roadblock_type}{format_end}
        """.format(
        num_line_items = len(prices),
        order_name=order_name,
        advertiser=advertiser_name,
        advertiser_type=advertiser_type,
        lineitem_type=lineitem_type,
        lineitem_prefix=lineitem_prefix,
        setup_type=setup_type,
        user_email=user_email,
        prices_summary=prices_summary,
        bidder_code=bidder_code,
        placements=placements_print,
        sizes=sizes,
        custom_targeting=custom_targeting,
        same_adv_exception=same_adv_exception,
        device_categories=device_categories,
        device_capabilities=device_capabilities,
        roadblock_type=roadblock_type,
        use_1x1=use_1x1,
        name_start_format=color.BOLD,
        format_end=color.END,
        value_start_format=color.BLUE,
        ))

    if setup_type == constant.ADPOD:
        # Prininting adpod price based lineitem summary
        logger.info(
        u"""
        ADPOD Details :
        {name_start_format}Adpod Size{format_end}: {value_start_format}{adpod_size}{format_end}
        {name_start_format}Adpod creative Durations{format_end}: {adpod_creative_durations}{format_end}
        {name_start_format}Line Item per each slot{format_end}: {value_start_format}{lineitem_per_slot}{format_end}
        {name_start_format}Creatives per each slot{format_end}: {value_start_format}{creatives_per_slot}{format_end}
        {name_start_format}Total number of Line Items{format_end}: {value_start_format}{lineitem_total}{format_end}
        {name_start_format}Total number of Creatives{format_end}: {value_start_format}{creatives_total}{format_end}      
        """.format(
            adpod_size = adpod_size,
            lineitem_per_slot = len(prices),
            adpod_creative_durations = adpod_creative_durations,
            creatives_per_slot= len(adpod_creative_durations),
            lineitem_total = len(prices)*adpod_size,
            creatives_total= adpod_size * len(adpod_creative_durations),
            name_start_format=color.BOLD,
            format_end=color.END,
            value_start_format=color.BLUE,
        ))
  else:
    # Prininting adpod deal lineitem summary
    print_summary(order_name,advertiser_name,advertiser_type,adpod_size, adpod_creative_durations, deal_config, adpod_slots, lineitem_type,  lineitem_prefix,
        setup_type, user_email, placements_print, sizes, custom_targeting, same_adv_exception, bidder_code, roadblock_type) 
        
  ok = input('Is this correct? (y/n)\n')

  if ok != 'y':
    logger.info('Exiting.')
    return

  try:
    if setup_type == constant.ADPOD: 
        for i in adpod_slots:
            slot = "s{}".format(i) 
            setup_partner(
                    user_email,
                    advertiser_name,
                    advertiser_type,
                    order_name,
                    placements,
                    sizes,
                    lineitem_type,
                    lineitem_prefix,
                    bidder_code,
                    prices,
                    setup_type,
                    creative_template,
                    num_creatives,
                    use_1x1,
                    currency_code,
                    custom_targeting,
                    same_adv_exception,
                    device_categories,
                    device_capabilities,
                    roadblock_type,
                    slot,
                    adpod_creative_durations,
                    None,
                    deal_config,
                    deal_lineitem_enabled,
            )

            if deal_lineitem_enabled == False:
                logger.info(""" 

                Orders Created: """ + str(order_list))    
    else:
        setup_partner(
                    user_email,
                    advertiser_name,
                    advertiser_type,
                    order_name,
                    placements,
                    sizes,
                    lineitem_type,
                    lineitem_prefix,
                    bidder_code,
                    prices,
                    setup_type,
                    creative_template,
                    num_creatives,
                    use_1x1,
                    currency_code,
                    custom_targeting,
                    same_adv_exception,
                    device_categories,
                    device_capabilities,
                    roadblock_type,
                    None,
                    None,
                    creative_user_def_var,
                    deal_config,
                    deal_lineitem_enabled,
            )  
    logger.info("""

    Done! Please review your orders, line items, and creatives to
    make sure they are correct. Then, approve the order in DFP.

    Happy bidding!

    """)    
  except ConnectionError as e:
      logger.error('\nConnection Error. Please try again after some time! Err: \n{}'.format(e))
  except GoogleAdsServerFault as e:
      if "ServerError.SERVER_ERROR" in str(e):
        logger.error('\n\nDFP Server Error. Please try again after some time! Err: \n{}'.format(e))
      else:
        raise DFPException("\n\nError occured while creating Lineitems in DFP: \n {}".format(e))

if __name__ == '__main__':
  main()
  