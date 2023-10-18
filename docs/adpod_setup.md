
# Line Item Tool - Adpod Setup

##### Set the following parameters in the setting.py files

|**Settings**|**Description**|**Type**|
|:----------|:--------------|:-------|
|`DFP_USER_EMAIL_ADDRESS`| Email of the DFP user who will be the trafficker | string |
|`DFP_ADVERTISER_NAME`| The exact name of the DFP advertiser for the order. <br> Set `PubMatic` for openwrap line items | string |
|`DFP_ADVERTISER_TYPE`| Advertiser type. Can be either `ADVERTISER` or `AD_NETWORK`. |string|
|`DFP_LINEITEM_TYPE`| Type of LineItem. Set to `PRICE_PRIORITY` or `SPONSORSHIP`| string|
|`OPENWRAP_SETUP_TYPE`| Setup type. Set to `ADPOD`| string  |
|`ADPOD_SLOTS`| Represents the position of slot in APOD. <br> Ex: `ADPOD_SLOTS = [1,2,3]`  represents  the 1st, 2nd and 3rd slot position in adpod.| integer array|
| `DFP_ORDER_NAME` | Name of order that will be created in DFP. <br> Order will be created for lineitems of each slot.<br>Each slot will have multiple orders if lineitems count per slot exceeds 450(order limit).<br><br>Ex: `DFP_ORDER_NAME = 'test_order_name'` then order name will `s1_1_test_order_name` for `1st` slot and  `s2_1_test_order_name` for `2nd` slot of adpod.<br><br>REUSE ADPOD ORDER:<br> order names are like `['s1_1_test', 's2_1_test']` for 1st and 2nd slot of adpod then set `DFP_ORDER_NAME = 'test'` for using existing orders.| string |
|`DFP_TARGETED_PLACEMENT_NAMES`| The names of GAM placements targeted by the line items. Use empty array for, `Run of Network.`| string array| 
|`DFP_PLACEMENT_SIZES`| Represents creative placement sizes. Add only one size object which will be used for all creatives. <br> Ex `DFP_PLACEMENT_SIZES =[{'width': '1','height': '1'}]` will be used for creatives sizes. | object |
|`VIDEO_LENGTHS`| Adpod video creative durations.<br> Ex `VIDEO_LENGTHS = [5,10,15]` will create creatives  with durations 5, 10 and 15 secs for each slot of Adpod. | integer array|
|`PREBID_BIDDER_CODE` | Bidder codes to target bidders with one line item. <br>Ex `PREBID_BIDDER_CODE = ['pubmatic']`. This parameter is mandatory for bidder level reporting. Set to `None` to generate line items for all partners.   | string array|
|`OPENWRAP_BUCKET_CSV` | This option is only for creating price based lineitems. Set this to one of the csv file mentioned in ` Inline Header Bidding  csv` table  below. This CSV lists buckets and price granularity; it sets `pwtpb` targeting for each line item..| string |
|`ENABLE_DEAL_LINEITEM` | Set this value to `TRUE` for creating deal line items| boolean |
|`DEAL_CONFIG_TYPE` | Set this value to `DEALID` or `DEALTIER` for creating deal line items with dealtier or dealid targeting| boolean |
|`DEAL_CONFIG` | Configuration for creating dealtier or dealid lineitem. Set this if `ENABLE_DEAL_LINEITEM` is set to `TRUE`. `DFP_CURRENCY_CODE` will determine the currency with which lineitem is created. | object |


#### More Optional Settings for Adpod Setup

|**Setting**|**Description**|**Type**|**Default**|
|:----------|:--------------|:-------|:----------|
|`DFP_CREATE_ADVERTISER_IF_DOES_NOT_EXIST`|Determines whether the tool creates an advertiser with `DFP_ADVERTISER_NAME` in GAM if it does not already exist.|bool|`False`
|`DFP_USE_EXISTING_ORDER_IF_EXISTS`|Determines whether to reuse an existing order if it matches `DFP_ORDER_NAME.`|bool|`False`|
|`DFP_CURRENCY_CODE`|National currency to use in line items.|string|`'USD'`|
|`DFP_SAME_ADV_EXCEPTION`|Determines whether to set the "Same Advertiser Exception" on line items. |bool|`False`|
|`DFP_DEVICE_CATEGORIES`|Sets device category targetting for a Line item. Valid values: `Connected TV`, `Desktop`, `Feature Phone`, `Set Top Box`, `Smartphone`, and `Tablet`.|string or array of strings|None|
|`DFP_ROADBLOCK_TYPE`| Roadblock Type. Set to  `ONE_OR_MORE` or `AS_MANY_AS_POSSIBLE`.|string|None|
|`OPENWRAP_CUSTOM_TARGETING`|Array of extra targeting rules per line item. <br>  Ex:  `[("a", "IS", ("1", "2", "3")), ("b", "IS_NOT", ("4", "5", "6"))]` |array of arrays|None|
|`VIDEO_POSITION_TYPE`| determines which video position lineitem will target. Valid values -  `PREROLL`, `MIDROLL`, `POSTROLL`, `ALL`.This is a optional setting and is applicable for video and adpod setup. For adpod setup each slot lineitem will have same video position targeting |string|None|


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

##### Using Custom Price Granularity 
1. Create a csv file using the file template shown [here](https://github.com/PubMatic-OpenWrap/dfp-prebid-setup/blob/master/LineItem.csv)
2. Add start_range, end_range, granularity and rate_id  in csv file for each price granularity range.
3. Set rate_id = 2 for all the price ranges.   
4. In settings.py file set `OPENWRAP_BUCKET_CSV` parameter to csv filename.


##### Example (CSV):
1. The smallest granularity level accepted is $0.01 (0 is not a valid option)
2. Enter a granularity level of -1 for the final line item. This covers all targeting within the range to the endpoint. 
(the last line with granularity “-1” covers all bids between $20-$30): 

| order_name | advertiser | start_range | end_range | granularity | rate_id |
|--|--|--|--|--| --|
|"Pubmatic HB" | "Pubmatic" | 0 | 10 | 1 | 2 |
|"Pubmatic HB" | "Pubmatic" | 10 | 20 | 2 | 2 
|"Pubmatic HB" | "Pubmatic" | 20 | 30 | -1 | 2 

*****Rates (pwtpb) created with above granularity: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16 ,18, 20]***** 

### Notes:
1. `PREBID_BIDDER_CODE` parameter is mandatory if you need bidder level reporting in DFP.
2. Creat order with new names when adding line items for new price granularity.
3. `60 seconds` is the default maximun duration creative,  line item can serve. 
   If the creative duration exceeds `60 seconds`, ad serving might fail.
4. Tool creates separate order for each adpod slot.
5. In the line item csv files the `rate_id` value should always be `2 (minimum)` for Adpod setup. 
6. Creative vast_xml is cached at 'https://ow.pubmatic.com/cache?uuid=%%PATTERN:{slotName}_pwtcid%%'.   
Ex: https://ow.pubmatic.com/cache?uuid=123456789.


## Deal LineItem Setup:
1. Set `ENABLE_DEAL_LINEITEM` to `TRUE`
2. Set `DEAL_CONFIG` with correct dealtier or dealid config. 
   Ex: DealTier Config: `{"pubmatic":{"price":10,"prefix":["abc"],"dealpriority":[5]}}`
   Ex: DealId Config: `{"pubmatic":{"price":10,"dealids":["PubDeal1]}}`
3. Set `DEAL_CONFIG_TYPE` to `DEALID` or `DEALTIER`
4. Set `DFP_LINEITEM_TYPE` to `SPONSORSHIP`
5. Set `OPENWRAP_SETUP_TYPE` to 'ADPOD'
6. Set `ADPOD_SLOTS` to required correct adpod slot position. Ex: [1,2,3] for 1st, 2nd and 3rd position.
7. Set `VIDEO_LENGTHS` to required creative durations.
8. Set `DFP_PLACEMENT_SIZES` to required creative size.
9. Set `PREBID_BIDDER_CODE` with required biddercodes. This parameter is optional, use only for creating lineitem with bidder targeting.
10. Set `DFP_ORDER_NAME` to order name. Lineitem of all the slots will be part of a single order.
11. Set `DFP_USER_EMAIL_ADDRESS`, `DFP_ADVERTISER_NAME`, `DFP_ADVERTISER_TYPE` settings
12. Set all other optional setting as required.

#### Notes (Deal LineItem Setup):
1. Single order will have lineitems for all the slots.
2. Line items will be created with `pwtdt` targeting for dealtier lineitems and `pwtdid` targeting for dealid lineitems . Optional `pwtpid` (bidder targeting) is added if bidder codes are set.
3. Deal config should be similar to what is expected in openwrap bid request and response.
4. For dealtier lineitems:
   <br> No of lineitems created = len(dealpriority)*len(prefix) * no of bidders
   <br>Ex: For config `{"appnexus":{"price":20,"prefix":["apnx"],"dealpriority":[8,10]},"pubmatic":{"price":10,"prefix":["pubm"],"dealpriority":[5]}}`
   <br><br>No of lineitems for pubmatic:  `1` --> `["pubm5"]` -->  `price:10`
   <br>No of lineitems for appnexus:  `2`  --> `["apnx8","apnx10"]` --> `price:20`
   <br><br> Targeting keys(`pwtdt`): `["pubm5", "apnx8", "apnx10"]` 
5. For dealid lineitems:
   <br> No of lineitems created = len(dealids) * no of bidders
   <br>Ex: For config `{"appnexus":{"price":20,"dealids":["ApnxDeal1"]},"pubmatic":{"price":10,"dealids":["PubmDeal1"]}}`
   <br><br>No of lineitems for pubmatic:  `1` --> `["PubmDeal1"]` -->  `price:10`
   <br>No of lineitems for appnexus:  `1`  --> `["ApnxDeal1"]` --> `price:20`


