
import constant
import re
import dfp
import logging
import tasks.add_new_openwrap_partner as lib
from tasks.price_utils import (
  get_prices_array,
  get_prices_summary_string,
  num_to_micro_amount,
  micro_amount_to_num,
  num_to_str,
)

logger = logging.getLogger(__name__)

def create_deal_line_item_configs(deal_config, order_id, placement_ids, bidder_code, sizes, key_gen_obj,
  lineitem_type, lineitem_prefix, currency_code, custom_targeting, setup_type, ad_unit_ids=None, same_adv_exception=False, 
  device_category_ids=None,device_capability_ids=None, roadblock_type='ONE_OR_MORE', durations = None, slot = None):
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
        if found:
            key_gen_obj.set_bidder_value(bidder_code, slot)

    for prefix in cfg['prefix']:
        for mdt in cfg['mindealtier']:
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

def setup_deal_lineitems(user_id, advertiser_id, order_id, placements,
     sizes, lineitem_type, lineitem_prefix, bidder_code, deal_config, setup_type, num_creatives, use_1x1,
     currency_code, custom_targeting, same_adv_exception, device_categories, device_capabilities, roadblock_type, slot , adpod_creative_durations, creative_user_def_var):
  """
  Call all necessary DFP tasks for a new Prebid partner setup.
  """


  # Get the placement IDs.
  placement_ids = None
  ad_unit_ids = None
  if len(placements) > 0:
      placement_ids = dfp.get_placements.get_placement_ids_by_name(placements)
  else:
      # Run of network
      root_id = dfp.get_root_ad_unit_id.get_root_ad_unit_id()
      ad_unit_ids = [ root_id ]

  #if bidder is None, then bidder will be 'All'
  bidder_str = bidder_code
  if bidder_str == None:
      bidder_str = "All"
  elif isinstance(bidder_str, (list, tuple)):
      bidder_str = "_".join(bidder_str)

  #generate unique id that will be used for creative and line item naming
  unique_id = lib.get_unique_id(setup_type)

  #create creatives
  logger.info('\nCreating creatives for slot {}...'.format(slot)) 


  size_arg = sizes
  if use_1x1:
      size_arg = None

  creative_configs = lib.get_creative_config(setup_type, bidder_str, None, advertiser_id, size_arg, num_creatives, None,  prefix=unique_id, adpod_creative_durations=adpod_creative_durations, slot=slot, creative_user_def_var=creative_user_def_var)
  creative_ids = dfp.create_creatives.create_creatives(creative_configs)
  
  creative_set_configs = dfp.create_creative_sets.create_creative_set_config_adpod(creative_ids, sizes, unique_id, adpod_creative_durations, slot)
  creative_ids = dfp.create_creative_sets.create_creative_sets(creative_set_configs)

  # Create line items.
  # if line item prefix is not passed, set unique id as lineitem prefix
  if lineitem_prefix is None:
      lineitem_prefix = unique_id

  logger.info('\nCreating line_itmes for slot {}...'.format(slot))

  line_items_config = create_deal_line_item_configs(deal_config, order_id,
      placement_ids, bidder_code, sizes, lib.OpenWrapTargetingKeyGen(), lineitem_type, lineitem_prefix,
      currency_code, custom_targeting, setup_type, ad_unit_ids=ad_unit_ids, same_adv_exception=same_adv_exception,
      device_category_ids=None, device_capability_ids=None, roadblock_type=roadblock_type,durations=adpod_creative_durations,slot=slot)
  
  line_item_ids = dfp.create_line_items.create_line_items(line_items_config)

  # Associate creatives with line items.
  size_overrides = []
  if use_1x1 and setup_type is not (constant.NATIVE or constant.IN_APP_NATIVE):
      size_overrides = sizes

  logger.info("\nCreating lineitem creative associations for slot {}...".format(slot))

  dfp.associate_line_items_and_creatives.make_licas(line_item_ids,
      creative_ids, size_overrides=size_overrides, setup_type=setup_type,slot=slot,durations=adpod_creative_durations)
  
def print_summary(adpod_size, adpod_creative_durations, deal_config, adpod_slots,lineitem_type):

    li_count = 0
    for bidder, cfg in deal_config.items():
      li_count = li_count + len(cfg['prefix']) * len(cfg['mindealtier'])
               

    logger.info(
      u"""
      ADPOD Details :
      
      {name_start_format}Adpod Size{format_end}: {value_start_format}{adpod_size}{format_end}
      {name_start_format}Adpod slot positions{format_end}: {value_start_format}{adpod_slot}{format_end}
      {name_start_format}Adpod creative Durations{format_end}: {adpod_creative_durations}{format_end}
      {name_start_format}Line Item per each slot{format_end}: {value_start_format}{lineitem_per_slot}{format_end}
      {name_start_format}Creatives per each slot{format_end}: {value_start_format}{creatives_per_slot}{format_end}
      {name_start_format}Total number of Line Items{format_end}: {value_start_format}{lineitem_total}{format_end}
      {name_start_format}Total number of Creatives{format_end}: {value_start_format}{creatives_total}{format_end}      
      {name_start_format}LineItem Type{format_end}: {value_start_format}{lineitem_type}{format_end}      
      {name_start_format}Deal Config{format_end}: {value_start_format}{deal_config}{format_end}            
        """.format(
        adpod_size = adpod_size,
        adpod_slot = adpod_slots,
        lineitem_per_slot = li_count,
        adpod_creative_durations = adpod_creative_durations,
        creatives_per_slot= len(adpod_creative_durations),
        lineitem_total = li_count*adpod_size,
        creatives_total= adpod_size * len(adpod_creative_durations),
        lineitem_type = lineitem_type,
        deal_config = deal_config,
        name_start_format=lib.color.BOLD,
        format_end=lib.color.END,
        value_start_format=lib.color.BLUE,
    ))  








