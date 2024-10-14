from googleads import ad_manager
from colorama import init
import os
import logging
import sys
import update_settings
from dfp.client import get_client
from prettytable import PrettyTable
from tasks.update_utils import UpdateUtils

# Colorama for cross-platform support for colored logging.
# https://github.com/kmjennison/dfp-prebid-setup/issues/9
init()

# Configure logging.
if 'DISABLE_LOGGING' in os.environ and os.environ['DISABLE_LOGGING'] == 'true':
  logging.disable(logging.CRITICAL)
  logging.getLogger('googleads').setLevel(logging.CRITICAL)
  logging.getLogger('oauth2client').setLevel(logging.CRITICAL)
else:
  FORMAT = '%(message)s'
  logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)
  logging.getLogger('googleads').setLevel(logging.ERROR)
  logging.getLogger('oauth2client').setLevel(logging.ERROR)
  logging.getLogger(__name__).setLevel(logging.DEBUG)


class Color:
        PURPLE = '\033[95m'
        CYAN = '\033[96m'
        DARKCYAN = '\033[36m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'

class BaseSettingUpdater:
    """
    Base class for updating settings in the DFP/GAM system
    """
    def __init__(self, logger, color, ad_manager_client, setting_class):
        """
        Initializes a BaseSettingUpdater instance.

        Parameters:
            logger: Logger object for handling log messages.
            color: Color object for terminal color formatting.
            ad_manager_client: Google Ad Manager (DFP/GAM) API client.
            setting_class: Class representing the specific settings of the task to update.
        """
        self.logger = logger
        self.color=color
        self.ad_manager_client = ad_manager_client
        self.setting_class = setting_class
        self.API_VERSION = "v202402"

    def confirm_inputs(self):
        """
        Function to print and confirm the user inputs.
        """
        raise NotImplementedError("Subclass must implement this method")

    def update(self):
        """
        Performs the actual update of task based on user inputs.
        """
        raise NotImplementedError("Subclass must implement this method")


class VideoPositionUpdater(BaseSettingUpdater):
    """
    Class for updating "Video Position Targeting" of line items.
    """
    def confirm_inputs(self):
        """
        confirm_inputs prints and confirms the user inputs.
        """
        formatted_text = """
Confirm the Input:

{name_start_format}Order{format_end}: {value_start_format}{order_name}{format_end}
{name_start_format}LineItem Name Regex{format_end}: {value_start_format}{lineitem_regex}{format_end}
{name_start_format}LineItem Type{format_end}: {value_start_format}{lineitem_type}{format_end}
{name_start_format}New Video Position{format_end}: {value_start_format}{new_video_position}{format_end}
        """

        self.logger.info(formatted_text.format(
            order_name=self.setting_class.DFP_ORDER_NAME,
            lineitem_regex=self.setting_class.LINE_ITEM_NAME_REGEX,
            lineitem_type=self.setting_class.DFP_LINEITEM_TYPE,
            new_video_position=self.setting_class.NEW_VIDEO_POSITION,
            name_start_format=self.color.BOLD,
            format_end=self.color.END,
            value_start_format=self.color.BLUE,
        ))

        user_confirmation = input("Is this correct? (y/n): ").lower()
        if user_confirmation != 'y':
            self.logger.info('Exiting.')
            return False
        if self.setting_class.NEW_VIDEO_POSITION not in ("PREROLL", "MIDROLL", "POSTROLL"):
            self.logger.info('NEW_VIDEO_POSITION supports only one of the value ("PREROLL", "MIDROLL", "POSTROLL")')
            return False
        return True

    def get_line_items(self):
       return UpdateUtils.get_line_items(self)

    def print_skipped_line_items(self, skip_line_items):
        UpdateUtils.print_skipped_line_items(skip_line_items)

    def print_line_items_with_current_position(self, line_items_to_update):
        """
        Function to print the line items that will be updated by script along with current-video-position and new-video-position
        """
        if len(line_items_to_update) <= 0:
            return

        table = PrettyTable()
        self.logger.info("Following line items will be updated:")
        table.field_names = [
            f"{self.color.BOLD}Line Item Name{self.color.END}",
            f"{self.color.BOLD}Current Video Position{self.color.END}",
            f"{self.color.BOLD}New Video Position{self.color.END}"
        ]
        for line_item,current_position in line_items_to_update.items():
            table.add_row([
                f"{self.color.BLUE}{line_item}{self.color.END}",
                f"{self.color.BLUE}{current_position}{self.color.END}",
                f"{self.color.BLUE}{self.setting_class.NEW_VIDEO_POSITION}{self.color.END}"
            ])
        self.logger.info(table)

    def select_line_items_to_update(self,line_items):
        """
        Selects line items to update based on specified criteria.
        Parameters:
            line_items (list): List of line items to be evaluated for updates.
        Returns:
                1. List of line items to be updated.
                2. Dictionary mapping line item names to their current targeted video positions.
                3. Dictionary containing line item names and reasons for skipping (not updating) each line item.
        """
        # List of line items to be updated
        updated_line_items = []
        # Dictionary mapping line item names to their current targeted video positions.
        line_items_with_current_position = {}
        # Dictionary containing line item names and reasons for skipping (not updating) each line item.
        skip_line_items = {}

        for line_item in line_items:
            # if targeting.videoPositionTargeting is missing then create empty object
            if 'videoPositionTargeting' not in line_item['targeting'] or not line_item['targeting']['videoPositionTargeting']:
                line_item['targeting']['videoPositionTargeting'] = {}

            # if targeting.videoPositionTargeting.targetedPositions is missing then create empty object
            if 'targetedPositions' not in line_item['targeting']['videoPositionTargeting'] or not line_item['targeting']['videoPositionTargeting']['targetedPositions']:
                line_item['targeting']['videoPositionTargeting']['targetedPositions'] = {}

            # current_position holds value of current targeted video positions
            current_position = None
            # flag to check if the current position is same as that of new
            found_same_video_position = False
            # counter to count total number of video-positions targeted for the line-item
            targeted_positions_cnt = 0

            for targeted_position in line_item['targeting']['videoPositionTargeting']['targetedPositions']:
                if 'videoPosition' in targeted_position and targeted_position['videoPosition']:
                    current_position = targeted_position['videoPosition']['positionType']
                    if current_position == self.setting_class.NEW_VIDEO_POSITION:
                        found_same_video_position = True
                        break
                    targeted_position['videoPosition']['positionType'] = self.setting_class.NEW_VIDEO_POSITION
                    targeted_positions_cnt = targeted_positions_cnt + 1

            if found_same_video_position:
                skip_line_items[line_item['name']] = "attempt to target same video position multiple time"
                continue

            if targeted_positions_cnt > 1:
                skip_line_items[line_item['name']] = "multiple video positions found, expecting only one position to update"
                continue

            # if the video position is not found, create a new targeting.videoPositionTargeting
            if targeted_positions_cnt == 0:
                line_item['targeting']['videoPositionTargeting'] = {"targetedPositions":[{"videoPosition":{"positionType": self.setting_class.NEW_VIDEO_POSITION}}]}

            line_items_with_current_position[line_item['name']]=current_position
            updated_line_items.append(line_item)

        return updated_line_items, line_items_with_current_position, skip_line_items

    def update(self):
        """
        Function to update "Video Position Targeting" of line items in GAM.
        It retrieves line items from the response, selects line items to update, and then updates them using the LineItemService.
        The user is prompted for confirmation before proceeding with the update.
        If the update is successful, the names of the updated line items are logged.
        """
        response = self.get_line_items()
        line_items = response['results'] if 'results' in response else []
        if len(line_items) <= 0:
            self.logger.info("No line item found for given input")
            return

        line_items_to_update, line_items_with_current_position, skip_line_items = self.select_line_items_to_update(line_items)
        self.print_skipped_line_items(skip_line_items)
        self.print_line_items_with_current_position(line_items_with_current_position)

        if len(line_items_to_update) > 0:
            user_confirmation = input("Do you want to proceed with the update? (y/n): ").lower()
            if user_confirmation != 'y':
                self.logger.info("Update canceled.")
                return

            line_item_service = self.ad_manager_client.GetService('LineItemService', version=self.API_VERSION)
            returned_line_items=line_item_service.updateLineItems(line_items_to_update)
            if len(returned_line_items) > 0:
                self.logger.info("\nSuccessfully updated following line items")
                for line_item in returned_line_items:
                    self.logger.info(f"{self.color.BLUE}{line_item['name']}{self.color.END}")


class LineItemTypeUpdater(BaseSettingUpdater):
    """
    Class for updating "Line Item Type" of line items.
    """
    def confirm_inputs(self):
        """
        confirm_inputs prints and confirms the user inputs.
        """
        formatted_text = """
Confirm the Input:

{name_start_format}Order{format_end}: {value_start_format}{order_name}{format_end}
{name_start_format}LineItem Name Regex{format_end}: {value_start_format}{lineitem_regex}{format_end}
{name_start_format}LineItem Type{format_end}: {value_start_format}{lineitem_type}{format_end}
{name_start_format}New Line Item Type{format_end}: {value_start_format}{new_lineitem_type}{format_end}
        """

        self.logger.info(formatted_text.format(
            order_name=self.setting_class.DFP_ORDER_NAME,
            lineitem_regex=self.setting_class.LINE_ITEM_NAME_REGEX,
            lineitem_type=self.setting_class.DFP_LINEITEM_TYPE,
            new_lineitem_type=self.setting_class.NEW_LINEITEM_TYPE,
            name_start_format=self.color.BOLD,
            format_end=self.color.END,
            value_start_format=self.color.BLUE,
        ))

        user_confirmation = input("Is this correct? (y/n): ").lower()
        if user_confirmation != 'y':
            self.logger.info('Exiting.')
            return False

        if self.setting_class.NEW_LINEITEM_TYPE == self.setting_class.DFP_LINEITEM_TYPE:
            self.logger.info('NEW_LINEITEM_TYPE is same as DFP_LINEITEM_TYPE')
            return False

        if self.setting_class.NEW_LINEITEM_TYPE not in ("NETWORK", "HOUSE", "PRICE_PRIORITY", "SPONSORSHIP"):
            self.logger.info('NEW_LINEITEM_TYPE supports only one of the value ("NETWORK", "HOUSE", "PRICE_PRIORITY", "SPONSORSHIP")')
            return False
        return True

    def get_line_items(self):
        return UpdateUtils.get_line_items(self)

    def print_skipped_line_items(self, skip_line_items):
        UpdateUtils.print_skipped_line_items(skip_line_items)

    def print_line_items_with_current_type(self, line_items_to_update):
        """
        Function to print the line items that will be updated by script along with current-line-item-type and new-line-item-type
        """
        if len(line_items_to_update) <= 0:
            self.logger.info("No line items to update")
            return

        table = PrettyTable()
        self.logger.info("Following line items will be updated:")
        table.field_names = [
            f"{self.color.BOLD}Line Item Name{self.color.END}",
            f"{self.color.BOLD}Current Line Item Type{self.color.END}",
            f"{self.color.BOLD}New Line Item Type{self.color.END}"
        ]
        for line_item,current_type in line_items_to_update.items():
            table.add_row([
                f"{self.color.BLUE}{line_item}{self.color.END}",
                f"{self.color.BLUE}{current_type}{self.color.END}",
                f"{self.color.BLUE}{self.setting_class.NEW_LINEITEM_TYPE}{self.color.END}"
            ])
        self.logger.info(table)

    def select_line_items_to_update(self,line_items):
        """
        Selects line items to update based on specified criteria.
        Parameters:
            line_items (list): List of line items to be evaluated for updates.
        Returns:
                1. List of line items to be updated.
                2. Dictionary mapping line item names to their current targeted line item types.
                3. Dictionary containing line item names and reasons for skipping (not updating) each line item.
        """
        # List of line items to be updated
        updated_line_items = []
        # Dictionary mapping line item names to their current targeted line item types.
        line_items_with_current_type = {}
        # Dictionary containing line item names and reasons for skipping (not updating) each line item.
        skip_line_items = {}

        for line_item in line_items:
            current_type = line_item['lineItemType']
            if current_type == self.setting_class.NEW_LINEITEM_TYPE:
                skip_line_items[line_item['name']] = "attempt to target same line item type multiple time"
                continue

            line_item['lineItemType'] = self.setting_class.NEW_LINEITEM_TYPE
            if self.setting_class.NEW_LINEITEM_TYPE in ('NETWORK','HOUSE'):
                line_item['primaryGoal']['goalType'] = 'DAILY'
                line_item['primaryGoal']['units'] = 100

            elif self.setting_class.NEW_LINEITEM_TYPE in ('SPONSORSHIP'):
                line_item['primaryGoal']['unitType'] = 'IMPRESSIONS'
                line_item['primaryGoal']['goalType'] = 'DAILY'
                line_item['primaryGoal']['units'] = 100
                line_item['skipInventoryCheck'] = True
                line_item['allowOverbook'] = True
                line_item['priority'] = 4

            elif self.setting_class.NEW_LINEITEM_TYPE == "PRICE_PRIORITY":
                line_item['priority'] = 12

            elif self.setting_class.NEW_LINEITEM_TYPE == "HOUSE":
                line_item['priority'] = 16

            line_items_with_current_type[line_item['name']]=current_type
            updated_line_items.append(line_item)

        return updated_line_items, line_items_with_current_type, skip_line_items

    def update(self):
        """
        Function to update "Line Item Type" of line items in GAM.
        It retrieves line items from the response, selects line items to update, and then updates them using the LineItemService.
        The user is prompted for confirmation before proceeding with the update.
        If the update is successful, the names of the updated line items are logged.
        """
        response = self.get_line_items()
        line_items = response['results'] if 'results' in response else []
        if len(line_items ) <= 0:
            self.logger.info("No line item found for given input")
            return

        line_items_to_update, line_items_with_current_type, skip_line_items = self.select_line_items_to_update(line_items)
        self.print_skipped_line_items(skip_line_items)
        self.print_line_items_with_current_type(line_items_with_current_type)

        if len(line_items_to_update) > 0:
            user_confirmation = input("Do you want to proceed with the update? (y/n): ").lower()
            if user_confirmation != 'y':
                self.logger.info("Update canceled.")
                return

            line_item_service = self.ad_manager_client.GetService('LineItemService', version=self.API_VERSION)
            returned_line_items=line_item_service.updateLineItems(line_items_to_update)
            if len(returned_line_items) > 0:
                self.logger.info("\nSuccessfully updated following line items")
                for line_item in returned_line_items:
                    self.logger.info(f"{self.color.BLUE}{line_item['name']}{self.color.END}")
            else:
                self.logger.info("No line items were updated.")
        else:
            self.logger.info("No line items matched the criteria for update.")

def main():
    try:
        if len(sys.argv) != 2:
            print("Usage: python -m tasks.update [VideoPosition|LineItemType]")
            print("Example: python -m tasks.update VideoPosition")
            return

        update_task = sys.argv[1].lower()
        logger = logging.getLogger(__name__)
        color = Color()

        # Use settings based on the command-line argument
        if update_task == "videoposition":
            updater = VideoPositionUpdater(logger,color, get_client(), update_settings.VideoPosition)
        elif update_task == "lineitemtype":
            updater = LineItemTypeUpdater(logger,color, get_client(), update_settings.LineItemType)
        else:
            print("Invalid setting class.")
            return

        if not updater.confirm_inputs():
            return
        updater.update()

    except Exception as e:
        print(f"Fatal Error: {e}")

if __name__ == "__main__":
    main()
