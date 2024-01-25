

import argparse
from googleads import ad_manager
from colorama import init
import os
import logging
import sys
import update_settings 

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

def build_statement(order_name, line_item_name_regex, line_item_type):
    # Create a statement to select line items by name and order name using regex
    statement = (ad_manager.StatementBuilder()
                 .Where('orderName = :order_name AND name LIKE :line_item_name AND lineItemType = :line_item_type')
                 .WithBindVariable('order_name', order_name)
                 .WithBindVariable('line_item_name', line_item_name_regex)
                 .WithBindVariable('line_item_type', line_item_type))
                 
    return statement


def update_line_items(ad_manager_client, response, new_position_type):

    
        line_items = response['results'] if 'results' in response else []

        if line_items:
            skip_line_items = {}
            updated_line_items = []
            for line_item in line_items:
                
                # do not update line-item if targeting information is missing
                if 'targeting' not in line_item or not line_item['targeting']:
                    print(f"Warning: targeting information is missing hence will not update Line Item: {line_item['name']}")
                    skip_line_items[line_item['name']] = "targeting information is missing"
                    continue

                # do not update line-item if targeting.requestPlatformTargeting information is missing
                if 'requestPlatformTargeting' not in line_item['targeting'] or not line_item['targeting']['requestPlatformTargeting']:
                    print(f"Warning: targeting.requestPlatformTargeting information is missing hence will not update Line Item: {line_item['name']}")
                    skip_line_items[line_item['name']] = "targeting.requestPlatformTargeting (Inventory type) information is missing"
                    continue

                # if targeting.videoPositionTargeting is missing then create empty object
                if 'videoPositionTargeting' not in line_item['targeting'] or not line_item['targeting']['videoPositionTargeting']:
                    line_item['targeting']['videoPositionTargeting'] = {}
                
                # if targeting.videoPositionTargeting.targetedPositions is missing then create empty object
                if 'targetedPositions' not in line_item['targeting']['videoPositionTargeting'] or not line_item['targeting']['videoPositionTargeting']['targetedPositions']:
                    line_item['targeting']['videoPositionTargeting']['targetedPositions'] = {}

                
                current_position = None
                # Flag to check if the current position is same as that of new
                found_same_video_position = False
                # Counter to check number of video-positions targeted for the line-item
                targeted_positions_cnt = 0

                for targeted_position in line_item['targeting']['videoPositionTargeting']['targetedPositions']:
                    if 'videoPosition' in targeted_position and targeted_position['videoPosition']:
                        current_position = targeted_position['videoPosition']['positionType']
                        if current_position == new_position_type:
                            found_same_video_position = True
                            break
                        targeted_position['videoPosition']['positionType'] = new_position_type
                        targeted_positions_cnt = targeted_positions_cnt + 1
                        

                if found_same_video_position:
                    print(f"Warning: Line Item {line_item['name']} is already targeted for {new_position_type}, will not update it.")
                    skip_line_items[line_item['name']] = "attempt to target same video position multiple time"
                    continue

                if targeted_positions_cnt > 1:
                    print(f"Warning: Line Item {line_item['name']} is targeted for multiple video positions, will not update it.")
                    skip_line_items[line_item['name']] = "multiple video positions found expecting only one position to update"
                    continue

                # If the video position is not updated, create a new targeting.videoPositionTargeting
                if targeted_positions_cnt == 0:
                    line_item['targeting']['videoPositionTargeting'] = {"targetedPositions":[{"videoPosition":{"positionType": new_position_type}}]}

                # Create an update statement
                # update_statement = ad_manager.StatementBuilder().Where('id = :line_item_id').WithBindVariable('line_item_id', line_item['id'])
                # update_statements.append(update_statement)
                # updated_line_items[line_item['name']] ={"current_position":current_position, "new_position":new_position_type}
                updated_line_items.append(line_item)
            
            if len(skip_line_items) > 0:
                print(f"Following line items will not be updated")
                print(f"Line-Item: Reason")
                for key,value in skip_line_items.items():
                    print(f"{key}: {value}")
                print("----------------------------------------------")
            
            # Update the line items in single API call
            if len(updated_line_items) > 0:
                
                # for key,value in updated_line_items.items():
                #     print(f"Line_Item:{key} Current_Position:{value['current_position']} New_Position:{value['new_position']}")
                
                
                #print(f"Line Item Name: {line_item['name']}, Current Video Position: {current_position}, New Video Position: {new_position_type}")
                user_confirmation = input("Do you want to proceed with the update? (yes/no): ").lower()
                if user_confirmation != 'yes':
                    print("Update canceled.")
                    return
                
                line_item_service = ad_manager_client.GetService('LineItemService', version='v202305')  # Use the appropriate API version

                # single DFP/GAM API call to update all selected line items
                rval=line_item_service.updateLineItems(updated_line_items)
                # rval=line_item_service.updateLineItems(update_statements)
                print(rval)
    

def simple_update_line_items(ad_manager_client, response):

        line_item_service = ad_manager_client.GetService('LineItemService', version='v202305')  # Use the appropriate API version

        line_items = response['results'] if 'results' in response else []
        updated_line_items = []
        if line_items:
            for line_item in response['results']:
                if not line_item['isArchived']:
                    line_item['deliveryRateType'] = 'AS_FAST_AS_POSSIBLE'
                    updated_line_items.append(line_item)

            # Update line items remotely.
            line_items = line_item_service.updateLineItems(updated_line_items)

            # Display results.
            if line_items:
                for line_item in line_items:
                    print('Line item with id "%s", belonging to order id "%s", named '
                        '"%s", and delivery rate "%s" was updated.'
                        % (line_item['id'], line_item['orderId'], line_item['name'],
                            line_item['deliveryRateType']))
                else:
                    print('No line items were updated.')
        else:
            print('No line items found to update.')
    
             
   

def main():
    parser = argparse.ArgumentParser(description="Update specific settings.")
    parser.add_argument("setting_class", choices=["VideoPosition", "UpdatePrice"], help="Specify which settings to use.")
    args = parser.parse_args()

    # Set up your credentials and network code
    ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage('/home/test/go/src/Ashish/dfp-prebid-setup/googleads.yaml')

    # Use settings based on the provided command-line argument
    if args.setting_class == "VideoPosition":
        settings_class = update_settings.VideoPosition
    elif args.setting_class == "UpdatePrice":
        settings_class = update_settings.UpdatePrice
    else:
        print("Invalid setting class.")
        return

    # Use settings from the specified class
    order_name = settings_class.DFP_ORDER_NAME
    line_item_name_regex = settings_class.LINE_ITEM_NAME_REGEX
    line_item_type = settings_class.DFP_LINEITEM_TYPE
    new_position_type = settings_class.NEW_VIDEO_POSITION

    # Build the statement
    statement = build_statement(order_name, line_item_name_regex, line_item_type)

    # Get the line items
    response = ad_manager_client.GetService('LineItemService', version='v202305').getLineItemsByStatement(statement.ToStatement())

    # Update line items and list before/after with user confirmation
    update_line_items(ad_manager_client, response, new_position_type)
    # simple_update_line_items(ad_manager_client,response)

if __name__ == "__main__":
    main()
