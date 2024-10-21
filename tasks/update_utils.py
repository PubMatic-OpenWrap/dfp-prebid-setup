# update_utils.py

from googleads import ad_manager
from prettytable import PrettyTable
from colorama import Fore, Style

class UpdateUtils:
    @staticmethod
    def get_line_items(self):
        """
        Function to build the statement based on filter condition and return all selected line items
        """
        statement = (ad_manager.StatementBuilder()
                 .Where('orderName = :order_name AND name LIKE :line_item_name AND lineItemType = :line_item_type')
                 .WithBindVariable('order_name', self.setting_class.DFP_ORDER_NAME)
                 .WithBindVariable('line_item_name', self.setting_class.LINE_ITEM_NAME_REGEX)
                 .WithBindVariable('line_item_type', self.setting_class.DFP_LINEITEM_TYPE))

        response = self.ad_manager_client.GetService('LineItemService', version=self.API_VERSION).getLineItemsByStatement(statement.ToStatement())
        print(response)
        return response
    
