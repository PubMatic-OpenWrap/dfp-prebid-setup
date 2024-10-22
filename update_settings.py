# update_settings.py

import os

# Add common setting
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
GOOGLEADS_YAML_FILE = os.path.join(ROOT_DIR, 'googleads.yaml')


# This utility class encapsulates configuration settings for updating the video positions of line items within a designated order.
# To execute the update, use the command: `python3 -m tasks.update VideoPosition`.
# The task requires input parameters such as DFP_ORDER_NAME, LINE_ITEM_NAME_REGEX, and DFP_LINEITEM_TYPE,
# and it performs the update by setting the video position of all selected line items to the specified NEW_POSITION_TYPE.
class VideoPosition:

    # DFP_ORDER_NAME: A string describing the order. Line items will be updated from this order.
    DFP_ORDER_NAME = 'test_order'

    # LINE_ITEM_NAME_REGEX: A string represents a regular expression pattern that can be used to match line item names.
    # It supports '%' as a wildcard character, representing zero or more characters.
    # To update all line items present in 'DFP_ORDER_NAME', set LINE_ITEM_NAME_REGEX = '%'
    # To update line items having prefix as 'prefix_', set LINE_ITEM_NAME_REGEX = 'prefix_%'
    # To update line items having suffix as '_suffix', set LINE_ITEM_NAME_REGEX = '%_suffix'
    LINE_ITEM_NAME_REGEX = '%'

    # DFP_LINEITEM_TYPE: Lineitem type. Can be either "NETWORK", "HOUSE", "PRICE_PRIORITY" or "SPONSORSHIP"
    DFP_LINEITEM_TYPE= 'PRICE_PRIORITY'

    # NEW_VIDEO_POSITION: video position to target
    # Valid values -  "PREROLL", "MIDROLL", "POSTROLL"
    NEW_VIDEO_POSITION = 'POSTROLL'


# This utility class encapsulates configuration settings for updating the line item type of line items within a designated order.
# To execute the update, use the command: `python3 -m tasks.update LineItemType`.
# The task requires input parameters such as DFP_ORDER_NAME, LINE_ITEM_NAME_REGEX, and DFP_LINEITEM_TYPE,
# and it performs the update by setting the line item type of all selected line items to the specified NEW_LINEITEM_TYPE.
# Don't use this utility for updating Lineitems for the ADPOD setup as it could interfere with the existing deal setup for sponsorship line items and cause unexpected behavior.
class LineItemType:

    # DFP_ORDER_NAME: A string describing the order. Line items will be updated from this order.
    DFP_ORDER_NAME = 'test_order'

    # LINE_ITEM_NAME_REGEX: A string represents a regular expression pattern that can be used to match line item names.
    # It supports '%' as a wildcard character, representing zero or more characters.
    # To update all line items present in 'DFP_ORDER_NAME', set LINE_ITEM_NAME_REGEX = '%'
    # To update line items having prefix as 'prefix_', set LINE_ITEM_NAME_REGEX = 'prefix_%'
    # To update line items having suffix as '_suffix', set LINE_ITEM_NAME_REGEX = '%_suffix'
    LINE_ITEM_NAME_REGEX = '%'

    # DFP_LINEITEM_TYPE: Lineitem type. Can be either "NETWORK", "HOUSE", "PRICE_PRIORITY" or "SPONSORSHIP"
    DFP_LINEITEM_TYPE ='PRICE_PRIORITY'

    # NEW_LINEITEM_TYPE: New line item type to target
    # Valid values -  "NETWORK", "HOUSE", "PRICE_PRIORITY" or "SPONSORSHIP"
    NEW_LINEITEM_TYPE = 'NETWORK'
