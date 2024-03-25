#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

from googleads import ad_manager

from dfp.client import get_client


logger = logging.getLogger(__name__)


def get_device_categories():
  """
  Gets Device Categories.

  Args:
	None
  Returns:
    map of Device Category to its Id
  """

  dfp_client = get_client()
  report_downloader = dfp_client.GetDataDownloader(version='v202402')

  device_query = ('SELECT Id, DeviceCategoryName '
                         'FROM Device_Category ')

  results = report_downloader.DownloadPqlResultToList(device_query)
  category_map = {}

  # Build associative array mapping category to id
  for d in results:
      # Skips the header row
      if isinstance(d[0],int):
          category_map[d[1]] = d[0]

  return category_map

def main():
  cm = get_device_categories()
  print(cm)

if __name__ == '__main__':
  main()
