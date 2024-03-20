#!/usr/bin/env python

import logging

from googleads import ad_manager

import settings
from dfp.client import get_client
from dfp.exceptions import (
  BadSettingException,
  DFPObjectNotFound,
  MissingSettingException
)


logger = logging.getLogger(__name__)

def get_root_ad_unit_id():
  """
  Gets effectiveRootAdUnitIde from DFP.

  Args:
    None
  Returns:
    effectiveRootAdUnitId
  """

  dfp_client = get_client()
  network_service = dfp_client.GetService('NetworkService', version='v202402')
  current_network = network_service.getCurrentNetwork()

  return current_network['effectiveRootAdUnitId']

def main():
  """
  Loads placements from settings and fetches them from DFP.

  Returns:
    None
  """

  id = get_root_ad_unit_id()
  print(id)

if __name__ == '__main__':
  main()
