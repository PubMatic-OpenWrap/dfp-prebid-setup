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

def create_advertiser(name, advertiser_type="ADVERTISER"):
  """
  Creates a DFP advertiser with name `name` and returns its ID.

  Args:
    name (str): the name of the DFP advertiser
  Returns:
    an integer: the advertiser's DFP ID
  """
  dfp_client = get_client()
  company_service = dfp_client.GetService('CompanyService', version='v202102')

  advertisers_config = [
    {
      'name': name,
      'type': advertiser_type
    }
  ]
  advertisers = company_service.createCompanies(advertisers_config)
  advertiser = advertisers[0]

  # Display results.
  for advertiser in advertisers:
    logger.info(u'Created an advertiser with name "{name}" and '
      'type "{type}".'.format(name=advertiser['name'], type=advertiser['type']))

  return advertiser

def get_advertiser_id_by_name(name, advertiser_type="ADVERTISER"):
  """
  Returns a DFP company ID from company name.

  Args:
    name (str): the name of the DFP advertiser
  Returns:
    an integer: the advertiser's DFP ID
  """
  dfp_client = get_client()
  company_service = dfp_client.GetService('CompanyService', version='v202102')

  # Filter by name.
  query = 'WHERE name = :name AND type = :type'
  values = [
      {'key': 'name',
       'value': {
           'xsi_type': 'TextValue',
           'value': name
       }},
      {'key': 'type',
       'value': {
           'xsi_type': 'TextValue',
           'value': advertiser_type
       }},
  ]
  statement = ad_manager.FilterStatement(query, values)

  response = company_service.getCompaniesByStatement(statement.ToStatement())

  # A company is required.
  no_company_found = False
  try:
    no_company_found = True if len(response['results']) < 1 else False 
  except (AttributeError, KeyError):
    no_company_found = True

  if no_company_found:
    if getattr(settings, 'DFP_CREATE_ADVERTISER_IF_DOES_NOT_EXIST', False):
      advertiser = create_advertiser(name, advertiser_type)
    else:
      raise DFPObjectNotFound('No advertiser found with name {0}'.format(name))
  elif len(response['results']) > 1:
    print(response)
    raise BadSettingException(
      'Multiple advertisers found with name {0}'.format(name))
  else:
    advertiser = response['results'][0]

  logger.info(u'Using existing advertiser with name "{name}" and '
    'type "{type}".'.format(name=advertiser['name'], type=advertiser['type']))

  return advertiser['id']

def main():
  """
  Gets the company name from settings and fetches its ID.

  Returns:
    an integer: the company's DFP ID
  """

  advertiser_name = getattr(settings, 'DFP_ADVERTISER_NAME', None)
  if advertiser_name is None:
    raise MissingSettingException('DFP_ADVERTISER_NAME')

  return get_advertiser_id_by_name(advertiser_name)

if __name__ == '__main__':
  main()
