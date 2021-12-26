# Line Item Tool - Adpod Setup

---
##### Set the following parameters in the setting.py files
 1.  Set values for`DFP_USER_EMAIL_ADDRESS`.
 2.  Set value for `DFP_ADVERTISER_NAME`.
 3.  Set `DFP_ADVERTISER_TYPE` parameter to `ADVERTISER` or `AD_NETWORK`.         
 4.  Set `DFP_LINEITEM_TYPE` to `PRICE_PRIORITY`.  
 5.  Set `OPENWRAP_SETUP_TYPE` to `ADPOD`              
 6.  Set `DFP_TARGETED_PLACEMENT_NAMES` to  arrary of Names of placements the line items should target.
 	 `DFP_TARGETED_PLACEMENT_NAMES = []` represents `RUN OF NETWORK`.
 7.  Set `ADPOD_SLOTS` parameter to slots position in adpod. 
 	 Ex: `ADPOD_SLOTS = [1,2,3]`  represents  the 1st, 2nd and 3rd slot position in adpod.
 8. Set `DFP_ORDER_NAME` parameter with order name.
 	Separate order wil be created for lineitems of each slot. 
    Each slot will have multiple orders if linitems count per slot exceeds 450(order limit). 
    Ex:  `DFP_ORDER_NAME = 'test_order_name'` then order name will `s1_1_test_order_name` for `1st` slot and  `s2_1_test_order_name` for `2nd` slot of adpod
   
    `REUSE ADPOD ORDER`:
    Existing order names are like `['s1_1_test', 's2_1_test']` for 1st and 2nd slot of adpod then set `DFP_ORDER_NAME = 'test'` for using existing orders.

 9. Set `DFP_PLACEMENT_SIZES` with creative size. Add only one size object which will be used for all creatives. 
	Ex `DFP_PLACEMENT_SIZES =[{'width': '1','height': '1'}]` will be used for creatives sizes. 
 10. Set `VIDEO_LENGTHS` with adpod video creative durations. 
 	 Ex `VIDEO_LENGTHS = [5,10,15]` will create creatives with durations 5, 10 and 15 secs for each slot of Adpod.
 11. Set `PREBID_BIDDER_CODE` to array of bidier codes to target multiple bidders with one line item.
	 Ex PREBID_BIDDER_CODE = ['pubmatic']
 	 This parameter is `optional`.
 	 Set this parameter to get bidder level reporting for adpod.
 12. Set `CURRENCY_EXCHANGE` to national currency to use in line items.
 	This parameter is `Optional`. 
    Ex  `CURRENCY_EXCHANGE = USD`.
 13. Set `DFP_DEVICE_CATEGORIES` to one of `Connected TV`, `Desktop`, `Feature Phone`, `Set Top Box`, `Smartphone`, and `Tablet`.
    `Optional Parameter`
 	This parameter used to set device category targetting for a Line item. 
 14. Set `DFP_ROADBLOCK_TYPE` to one of  `ONE_OR_MORE` or `AS_MANY_AS_POSSIBLE`
 	Defaults to `ONE OR MORE`
 15. Set `OPENWRAP_CUSTOM_TARGETING` to array of custom targeting for line items.
 	Ex `OPENWRAP_CUSTOM_TARGETING` = `[("a", "IS", ("1", "2", "3")), ("b", "IS_NOT", ("4", "5", "6"))]`.
 	`This parameter is optional`.
 16. Set `OPENWRAP_BUCKET_CSV` to one of the csv file mentioned in the table below.			


 
 
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
