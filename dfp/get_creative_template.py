#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

def get_creative_template_by_name(template_name):
    
    dfp_client = get_client()
    # Initialize appropriate service.
    creative_template_service = dfp_client.GetService(
      'CreativeTemplateService', version='v202411')

     # Create a statement to select creative templates.
    statement = (ad_manager.StatementBuilder(version='v202411')
     .Where('name = :name')
     .WithBindVariable('name', template_name))

    response = creative_template_service.getCreativeTemplatesByStatement(
            statement.ToStatement())
   
    no_creative_template_found = False
    try:
        no_creative_template_found = True if len(response['results']) < 1 else False 
    except (AttributeError, KeyError):
        no_creative_template_found = True

    if no_creative_template_found:
        raise DFPObjectNotFound('No DFP creative template found with name {0}'.format(
            template_name))
    else:
        creative_template = response['results'][0]
        #print(creative_template)
        print('Found creative_template with name "{name}" and id {id}.'.format(name=creative_template['name'], id=creative_template['id']))
    return creative_template



def get_creative_template_ids_by_name(creative_template_names):
  """
  Gets creative template IDs from DFP based on their names.

  Args:
    creative_template_names (arr): an array of creative template name strings
  Returns:
    an array: an array of creative template IDs
  """  
  creative_template_ids = []
  for template_name in creative_template_names:
    creative_template_ids.append(get_creative_template_by_name(template_name)['id'])
  return creative_template_ids



def main():
  """
  Gets the creative template name from settings and fetches its ID.

  Returns:
    an integer: the creative template ID
  """

  template_names = getattr(settings, 'OPENWRAP_CREATIVE_TEMPLATE', None)
  if template_names is None:
    raise MissingSettingException('OPENWRAP_CREATIVE_TEMPLATE')

  return get_creative_template_ids_by_name(template_names)

if __name__ == '__main__':
  main()
