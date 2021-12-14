# Line Item Tool - Adpod Setup
  
Set the following parameters in the settings.py file
 1. Set `OPENWRAP_SETUP_TYPE` to `ADPOD`
 2. Set values for parameters`DFP_USER_EMAIL_ADDRESS`, `DFP_ADVERTISER_NAME`, `DFP_LINEITEM_TYPE`.  
 3. Set `ADPOD_SLOTS` parameter to slots position in adpod. 
 	Ex `ADPOD_SLOTS = [1,2,3]` , will create 1st, 2nd and 3rd slot of adpod. 
 4. Set `VIDEO_LENGTHS` with adpod video creative durations. 
 	Ex `VIDEO_LENGTHS = [5,10,15]` will create creatives with durations 5, 10 and 15 secs for each slot of Adpod.
 5. Set `DFP_PLACEMENT_SIZES` with creative size. Add only one size object. 
	Ex `DFP_PLACEMENT_SIZES =[{'width': '1','height': '1'}]` will be used for creatives sizes. 
 6. Set `DFP_ORDER_NAME`.
 	Ex:  DFP_ORDER_NAME = 'test_order_name' then order name will s1_1_test_order_name,  s2_1_test_order_name for 1st and 2nd slot of adpod.
	For using existin order, Existing order names are like 's1_1_test', 's2_1_test' then set DFP_ORDER_NAME = 'test' for using existing orders.
 7. Set `OPENWRAP_BUCKET_CSV` to one of the csv file mentioned in table below.
 8. Set values for Optional` parameters`DFP_USER_EMAIL_ADDRESS`, `DFP_ADVERTISER_NAME`, `DFP_LINEITEM_TYPE`, `PREBID_BIDDER_CODE`, `CURRENCY_EXCHANGE`, `DFP_ADVERTISER_TYPE`, `DFP_TARGETED_PLACEMENT_NAMES`, `DFP_CURRENCY_CODE` 
 
 
#### Inline Header Bidding  csv
For Adpod setup use one of the following csv files present in `dfp-prebid-setup` root folder for `OPENWRAP_BUCKET_CSV` parameter 
|  Price Granularity | CSV File |
|--|--|
| Auto  | Inline_Header_Bidding_Auto |
| Low | Inline_Header_Bidding_Low |
| Medium  | Inline_Header_Bidding_Med |
| CTV-Medium  |  Inline_Header_Bidding_CTV-Med|
| High  |  Inline_Header_Bidding_High|
| Dense  |Inline_Header_Bidding_Dense|

