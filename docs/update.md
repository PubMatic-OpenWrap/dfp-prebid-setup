# Update line item setup


## Overview


The **tasks/update.py** utility script is designed to automate the process of modifying settings in Google Ad Manager. <br>
This script takes the user inputs from the **update_settings.py** which is orgnized as per specific task, making it easier to manage and execute updates.

#### Note
This script is designed specifically for modifying line items that have been created using our **tasks/add_new_openwrap_partner.py** script.


## configuration settings - update_settings.py
`update_settings.py` should be present in the root directory of project. <br>
It contains configuration settings of following tasks.
<details>
  <summary>1. Video Position</summary><br/>

The `VideoPosition` class in the `update_settings.py` file contains configuration parameters that are required to update the Video Position targeting of line items.

**Parameters:**


|**Parameter**|**Description**|**Type**|**Example** |
|:----------|:--------------|:-------|:---------------|
|`DFP_ORDER_NAME`| The name of your GAM order. Line items will be updated from this order. | string |'test_order' |
| `LINE_ITEM_NAME_REGEX`      |A string representing a regular expression pattern to match line item names. <br/> 1. To select all line items from order, set this to '%'  <br/> 2. To select line items having prefix as 'prefix\_',  set this to 'prefix\_%'  <br/>3.  To select line items having suffix as '\_suffix',  set this to '%\_suffix'| string| '%' |
| `DFP_LINEITEM_TYPE`         | Line item type. <br>Can be "NETWORK", "HOUSE", "PRICE_PRIORITY", or "SPONSORSHIP".      | string               | 'PRICE_PRIORITY'                |
| `NEW_VIDEO_POSITION`        | The value of new video position to target.<br>Valid values: "PREROLL", "MIDROLL", "POSTROLL".              | string        | 'MIDROLL'                       |


**How to Run:**

To execute the Video Position Update Task, use the following command:

```
python -m tasks.update VideoPosition
```

**Limitations**
1. Line item to be updated should be of type "Video" because only "video" line item supports video position targeting.
2. If the selected line item has multiple video-position targeted then it will not update the line item.
3. If the selected line item is already targeted for 'NEW_VIDEO_POSITION' then it will not update the line item.
4. Line item to be updated should have been created using tasks/add_new_openwrap_partner.py

</details>
