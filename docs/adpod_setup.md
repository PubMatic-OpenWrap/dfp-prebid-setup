# Line Item Tool - Adpod Setup
  
Set the following parameters in the settings.py file
 1. Set `OPENWRAP_SETUP_TYPE` to 	`ADPOD` 
 2. Set `ADPOD_SIZE` parameter to number of slots in adpod. Ex `ADPOD_SIZE = 1`
 3. Set `VIDEO_LENGTHS` with adpod video creative durations. Ex `VIDEO_LENGTHS = [5,10,15]`
 4. Set `DFP_PLACEMENT_SIZES` with creative size. Add only one size object. 
	 Ex `DFP_PLACEMENT_SIZES =[{'width': '1','height': '1'}]` 
 6. Set `OPENWRAP_BUCKET_CSV` to one of the csv file mentioned in table below.
 7. Set rest other mandatory parameters in settings.py file.
 
 
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

