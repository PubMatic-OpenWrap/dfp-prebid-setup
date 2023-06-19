#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

from googleads import ad_manager

from dfp.client import get_client


logger = logging.getLogger(__name__)


def get_device_capabilities():
  """
  Gets Device capabilities.

  Args:
    None
  Returns:
    map of device capability to its id
  """

  dfp_client = get_client()
  report_downloader = dfp_client.GetDataDownloader(version='v202305')

  device_query = ('SELECT Id, DeviceCapabilityName '
                         'FROM Device_Capability ')

  results = report_downloader.DownloadPqlResultToList(device_query)
  capability_map = {}

  # Build associative array mapping category to id
  for d in results:
      # Skips the header row
      if isinstance(d[0],int):
          capability_map[d[1]] = d[0]

  return capability_map

def main():
  cm = get_device_capabilities()
  print(cm)

if __name__ == '__main__':
  main()
