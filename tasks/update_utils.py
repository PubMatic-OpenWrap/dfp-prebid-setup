# update_utils.py

from googleads import ad_manager
from prettytable import PrettyTable
from colorama import Fore, Style

class UpdateUtils:
    @staticmethod
    def print_skipped_line_items(skip_line_items):
        """
        Function to print the line items that will not be updated by script along with its reason
        """
        if len(skip_line_items) <= 0:
            return

        table = PrettyTable()
        print("Following line items will not be updated:")
        table.field_names = [
            f"{Fore.BLUE}Line Item Name{Style.RESET_ALL}",
            f"{Fore.BLUE}Reason{Style.RESET_ALL}",
        ]
        for line_item, reason in skip_line_items.items():
            table.add_row([
                f"{Fore.BLUE}{line_item}{Style.RESET_ALL}",
                f"{Fore.BLUE}{reason}{Style.RESET_ALL}",
            ])
        print(table)

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
    
