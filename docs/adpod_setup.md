
# Line Item Tool - Adpod Setup

##### Set the following parameters in the setting.py files

|**Settings**|**Description**|**Type**|
|:----------|:--------------|:-------|
|`DFP_USER_EMAIL_ADDRESS`| Email of the DFP user who will be the trafficker | string |
|`DFP_ADVERTISER_NAME`| The exact name of the DFP advertiser for the order. <br> Set `PubMatic` for openwrap line items | string |
|`DFP_ADVERTISER_TYPE`| Advertiser type. Can be either `ADVERTISER` or `AD_NETWORK`. |string|
|`DFP_LINEITEM_TYPE`| Type of LineItem. Set to `PRICE_PRIORITY`| string|
|`OPENWRAP_SETUP_TYPE`| Setup type. Set to `ADPOD`| string  |
|`ADPOD_SLOTS`| Represents the position of slot in APOD. <br> Ex: `ADPOD_SLOTS = [1,2,3]`  represents  the 1st, 2nd and 3rd slot position in adpod.| integer array|
| `DFP_ORDER_NAME` | Name of order that will be created in DFP. <br> Order will be created for lineitems of each slot.<br>Each slot will have multiple orders if lineitems count per slot exceeds 450(order limit).<br><br>Ex: `DFP_ORDER_NAME = 'test_order_name'` then order name will `s1_1_test_order_name` for `1st` slot and  `s2_1_test_order_name` for `2nd` slot of adpod.<br><br>REUSE ADPOD ORDER:<br> order names are like `['s1_1_test', 's2_1_test']` for 1st and 2nd slot of adpod then set `DFP_ORDER_NAME = 'test'` for using existing orders.| string |
|`DFP_TARGETED_PLACEMENT_NAMES`| The names of GAM placements targeted by the line items. Use empty array for, `Run of Network.`| string array| 
|`DFP_PLACEMENT_SIZES`| Represents creative placement sizes. Add only one size object which will be used for all creatives. <br> Ex `DFP_PLACEMENT_SIZES =[{'width': '1','height': '1'}]` will be used for creatives sizes. | object |
|`VIDEO_LENGTHS`| Adpod video creative durations.<br> Ex `VIDEO_LENGTHS = [5,10,15]` will create creatives  with durations 5, 10 and 15 secs for each slot of Adpod. | integer array|
|`PREBID_BIDDER_CODE` | Bidder codes to target bidders with one line item. <br>Ex `PREBID_BIDDER_CODE = ['pubmatic']`. This parameter is mandatory for bidder level reporting. Set to `None` to generate line items for all partners.   | string array|
|`OPENWRAP_BUCKET_CSV` | Set this to one of the cvs file mentioned in ` Inline Header Bidding  csv` table  below. This CSV lists buckets and price granularity; it sets `pwtpb` targeting for each line item..| string |



#### Inline Header Bidding csv
For Adpod setup use/edit one of the following csv files present in `dfp-prebid-setup`  folder for `OPENWRAP_BUCKET_CSV` parameter 

 ***Note: Ignore the Order Name and Advertiser columns are in the CSV file. Specify those settings in, settings.py ***
 ***In the line item csv files the `rate_id` value should always be `2 (minimum)` for Adpod setup***
 
|  Price Granularity | CSV File |
|--|--|
| Auto  | Inline_Header_Bidding_Auto |
| Low | Inline_Header_Bidding_Low |
| Medium  | Inline_Header_Bidding_Med |
| CTV-Medium  |  Inline_Header_Bidding_CTV-Med|
| High  |  Inline_Header_Bidding_High|
| Dense  |Inline_Header_Bidding_Dense|



#### More Optional Settings for Adpod Setup

|**Setting**|**Description**|**Type**|**Default**|
|:----------|:--------------|:-------|:----------|
|`DFP_CREATE_ADVERTISER_IF_DOES_NOT_EXIST`|Determines whether the tool creates an advertiser with `DFP_ADVERTISER_NAME` in GAM if it does not already exist.|bool|`False`
|`DFP_USE_EXISTING_ORDER_IF_EXISTS`|Determines whether to reuse an existing order if it matches `DFP_ORDER_NAME.`|bool|`False`|
|`DFP_CURRENCY_CODE`|National currency to use in line items.|string|`'USD'`|
|`DFP_SAME_ADV_EXCEPTION`|Determines whether to set the "Same Advertiser Exception" on line items. |bool|`False`|
|`DFP_DEVICE_CATEGORIES`|Sets device category targetting for a Line item. Valid values: `Connected TV`, `Desktop`, `Feature Phone`, `Set Top Box`, `Smartphone`, and `Tablet`.|string or array of strings|None|
|`DFP_ROADBLOCK_TYPE`| Roadblock Type. Set to  `ONE_OR_MORE` or `AS_MANY_AS_POSSIBLE`.|string|None|
|`OPENWRAP_CUSTOM_TARGETING`|Array of extra targeting rules per line item. <br>  Ex:  `[("a", "IS", ("1", "2", "3")), ("b", "IS_NOT", ("4", "5", "6"))]` |array of arrays .)|None|

### Notes:
1. `PREBID_BIDDER_CODE` parameter is mandatory if you need bidder level reporting in DFP.
2. Creat order with new names when adding line items for new price granularity.
3. `60 seconds` is the default maximun duration creative,  line item can serve. 
   If the creative duration exceeds `60 seconds`, ad serving might fail.
4. Tool creates separate order for each adpod slot.
5. In the line item csv files the `rate_id` value should always be `2 (minimum)` for Adpod setup. 



