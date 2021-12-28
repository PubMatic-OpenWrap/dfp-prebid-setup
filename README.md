
# Line Item Tool - Adpod Setup

##### Set the following parameters in the setting.py files

|**Settings**|**Description**|**Type**|**Default**| 
|:----------|:--------------|:-------|:----------|
|`DFP_USER_EMAIL_ADDRESS`| Email of the DFP user who will be the trafficker | string | |  
|`DFP_ADVERTISER_NAME`| The exact name of the DFP advertiser for the order. <br> Set `PubMatic` for openwrap line items | string | |
|`DFP_ADVERTISER_TYPE`| Advertiser type. Can be either `ADVERTISER` or `AD_NETWORK`. |string| |
|`DFP_LINEITEM_TYPE`| Type of LineItem. Set to `PRICE_PRIORITY`| string| |
|`OPENWRAP_SETUP_TYPE`| Setup type. Set to `ADPOD`| string  | |
|`ADPOD_SLOTS`| Represents the position of slot in APOD. <br> Ex: `ADPOD_SLOTS = [1,2,3]`  represents  the 1st, 2nd and 3rd slot position in adpod.| integer array| |
| `DFP_ORDER_NAME` | Name of order that will be created in DFP. <br> Order will be created for lineitems of each slot.<br>Each slot will have multiple orders if lineitems count per slot exceeds 450(order limit).<br>Ex: `DFP_ORDER_NAME = 'test_order_name'` then order name will `s1_1_test_order_name` for `1st` slot and  `s2_1_test_order_name` for `2nd` slot of adpod.<br>`REUSE ADPOD ORDER`:<br> order names are like `['s1_1_test', 's2_1_test']` for 1st and 2nd slot of adpod then set `DFP_ORDER_NAME = 'test'` for using existing orders.| string | |
|`DFP_TARGETED_PLACEMENT_NAMES`| Names of placements the line items should target.| string array| RUN OF NETWORK|
|`DFP_PLACEMENT_SIZES`| Represents creative placement sizes. Add only one size object which will be used for all creatives. <br> Ex `DFP_PLACEMENT_SIZES =[{'width': '1','height': '1'}]` will be used for creatives sizes. | object | | 
|`VIDEO_LENGTHS`| Adpod video creative durations.<br> Ex `VIDEO_LENGTHS = [5,10,15]` will create creatives  with durations 5, 10 and 15 secs for each slot of Adpod. | integer array| |
|`PREBID_BIDDER_CODE`| Bidder codes to target bidders with one line item.Ex PREBID_BIDDER_CODE = ['pubmatic']. This parameter is mandatory for bidder level reporting | strign array| |
|`CURRENCY_EXCHANGE`|  National currency to use in line items.  Ex  `CURRENCY_EXCHANGE = USD`.| string| |
|`DFP_DEVICE_CATEGORIES`| This parameter used to set device category targeting for a Line item. Set to one of `Connected TV`, `Desktop`, `Feature Phone`, `Set Top Box`, `Smartphone`, and `Tablet`. | string | |
|`DFP_ROADBLOCK_TYPE`| Set to one of  `ONE_OR_MORE` or `AS_MANY_AS_POSSIBLE`| string |`ONE OR MORE`|
|`OPENWRAP_CUSTOM_TARGETING`|array of custom targeting for line items. Ex `OPENWRAP_CUSTOM_TARGETING` = `[("a", "IS", ("1", "2", "3")), ("b", "IS_NOT", ("4", "5", "6"))]`.| object array||
 |`OPENWRAP_BUCKET_CSV` | Set to one of the csv file mentioned in the table below.| string | |			

#### Inline Header Bidding  csv
For Adpod setup use one of the following csv files present in `dfp-prebid-setup`  folder for `OPENWRAP_BUCKET_CSV` parameter 
|  Price Granularity | CSV File |
|--|--|
| Auto  | Inline_Header_Bidding_Auto |
| Low | Inline_Header_Bidding_Low |
| Medium  | Inline_Header_Bidding_Med |
| CTV-Medium  |  Inline_Header_Bidding_CTV-Med|
| High  |  Inline_Header_Bidding_High|
| Dense  |Inline_Header_Bidding_Dense|


### Notes:
1. `PREBID_BIDDER_CODE` parameter is mandatory if you need bidder level reporting in DFP.
2. Creat order with new names when adding line items for new price granularity.
3. `60 seconds` is the default maximun duration creative,  line item can serve. 
   If the creative duration exceeds `60 seconds`, ad serving might fail.
4. Tool creates separate order for each adpod slot.
5. In the line item csv files the `rate_id` value should always be `2(minimum)` or `-1` for Adpod setup. 
