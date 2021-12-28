# Line Item Tool - Adpod Setup

##### Set the following parameters in the setting.py files

 |**Settings**|**Description**|**Type**|**Default**| **Optional**|
|:----------|:--------------|:-------|:----------|:----------|
|`DFP_USER_EMAIL_ADDRESS`| Email of the DFP user who will be the trafficker  | string |  | No |
|`DFP_ADVERTISER_NAME`| The exact name of the DFP advertiser for the order. Set `PubMatic` for openwrap Line items | string |   | No | 
|`DFP_ADVERTISER_TYPE`| Advertiser type. Can be either `ADVERTISER` or `AD_NETWORK`. |string||No|
|`DFP_LINEITEM_TYPE`| Type of LineItem. Set to `PRICE_PRIORITY`| string| | No | 
|`OPENWRAP_SETUP_TYPE`| Setup type. Set to `ADPOD`| string  | | No |
|`ADPOD_SLOTS`| Represents the position of slot in APOD.<br>  Ex: `ADPOD_SLOTS = [1,2,3]`  represents  the 1st, 2nd and 3rd slot position in adpod.| integer array| | No|
| `DFP_ORDER_NAME` | Name of order that will be created in DFP.<br>  Separate order wil be created for lineitems of each slot.  Each slot will have multiple orders if linitems count per slot exceeds 450(order limit).<br>  Ex:  `DFP_ORDER_NAME = 'test_order_name'` then order name will `s1_1_test_order_name` for `1st` slot and  `s2_1_test_order_name` for `2nd` slot of adpod.  <br> `REUSE ADPOD ORDER`:<br> Existing order names are like `['s1_1_test', 's2_1_test']` for 1st and 2nd slot of adpod then set `DFP_ORDER_NAME = 'test'` for using existing orders.| string | | No|