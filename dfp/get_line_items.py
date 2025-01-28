#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from googleads import ad_manager

from dfp.client import get_client


logger = logging.getLogger(__name__)

def get_line_item_count_by_order(order_id):
  """
  Get  line item count for a order

  Args:
    orderId (long): orderid
  Returns:
    int : count of line itms in order
  """
  dfp_client = get_client()
  line_item_service = dfp_client.GetService('LineItemService', version='v202411')

   # Filter by order.
  query = 'WHERE orderId = :orderId'
  values = [{
    'key': 'orderId',
    'value': {
      'xsi_type': 'TextValue',
      'value': order_id
    }
  }]
  
  statement = ad_manager.FilterStatement(query, values)
  response = line_item_service.getLineItemsByStatement(statement.ToStatement())
  if 'totalResultSetSize' in response :
    return response['totalResultSetSize']
  return 0     


