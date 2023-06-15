
import logging
import os
import pprint

from googleads import ad_manager

from dfp.client import get_client


logger = logging.getLogger(__name__)

  
def create_creative_sets(creative_sets):

    """
    Creates creative sets in DFP.

    Args:
        creative sets (arr): an array of objects, each having creative set configuration
    Returns:
        an array: an array of created creative set IDs
    """

    dfp_client = get_client()
    creative_set_service = dfp_client.GetService('CreativeSetService',
                                           version='v202305')
    creative_set_ids = []
    for creative_set in creative_sets:
        creative_set = creative_set_service.createCreativeSet(creative_set)
        creative_set_ids.append(creative_set['id'])
    return creative_set_ids


def create_creative_set_config(creative_ids, sizes, prefix):
    """
    Returns an array of creative  set config object.

    Args:
        creative ids (int array): the IDs of the creatives
        sizes(String array): sizes for creative
        prefix (string): creative name prefix
    Returns:
        an array: an array of creative set config
    """
    creative_sets = []
    size = len(creative_ids)
    for i in range(size):
        creative_set = {
            'name': '{}_{}x{}'.format(prefix, sizes[i]["width"], sizes[i]["height"]),
            'masterCreativeId': creative_ids[i]
        }
        creative_sets.append(creative_set)
    return creative_sets


def create_creative_set_config_adpod(creative_ids, sizes,  uniqueID, durations,slot):
    """
    Returns an array of creative  set config object.

    Args:
        creative ids (int array): the IDs of the creatives
        sizes(String array): sizes for creative
        uniqueID (string): creative name suffix for unique identification
        durations(string array): Creative durations
        slot(string): slot name
    Returns:
        an array: an array of creative set config
    """
    
    creative_sets = []
    size = len(creative_ids)
    for i in range(size):
        creative_set = {
            'name': '{}_{}X{}_{}SecondsAdSet_{}'.format(slot,  sizes[0]["height"], sizes[0]["width"], durations[i], uniqueID ),
            'masterCreativeId': creative_ids[i]
        }
        creative_sets.append(creative_set)
    return creative_sets    