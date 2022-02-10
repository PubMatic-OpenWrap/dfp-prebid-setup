
import logging
from googleads import ad_manager

from dfp.client import get_client


logger = logging.getLogger(__name__)

def remove_licas(line_item_id):
  """
  Removes all creative associations from a line item in DFP.

  Args:
    line_item_id (int): item ID
  Returns:
    Number of ceratives removed
  """
  dfp_client = get_client()
  lica_service = dfp_client.GetService(
    'LineItemCreativeAssociationService', version='v202111')

 # Create query.
  statement = (dfp.StatementBuilder()
               .Where('lineItemId = :lineItemId AND status = :status')
               .WithBindVariable('status', 'ACTIVE')
               .WithBindVariable('lineItemId', int(line_item_id)))

  num_deactivated_licas = 0

  # Get LICAs by statement.
  while True:
    response = lica_service.getLineItemCreativeAssociationsByStatement(
        statement.ToStatement())

    if 'results' in response and len(response['results']):
      for lica in response['results']:
        print ('LICA with line item id "%s", creative id "%s", and status'
               ' "%s" will be deactivated.' %
               (lica['lineItemId'], lica['creativeId'], lica['status']))

      result = lica_service.performLineItemCreativeAssociationAction(
        {'xsi_type': 'DeactivateLineItemCreativeAssociations'},
        statement.ToStatement())

      if result and int(result['numChanges']) > 0:
        num_deactivated_licas += int(result['numChanges'])
      statement.offset += statement.limit
    else:
      break

  logger.info(
     u'Removed {0} line item <> creative associations.'.format(num_deactivated_licas))

  return num_deactivated_licas
