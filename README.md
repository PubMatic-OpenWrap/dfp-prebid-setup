# Line Item Tool for Prebid, OpenWrap, and GAM

This Python-based line item generator for [Prebid.js](http://prebid.org/), [OpenWrap](https://community.pubmatic.com/display/OP/OpenWrap), and [Google Ad Manager](https://admanager.google.com/home/), automates setup for new header bidding partners.

> **Note:** Doubleclick for Publishers (DFP) is now called, Google Ad Manager (GAM). If this repository refers to DFP, consider it equal to, GAM.

When your ad ops team sets up Prebid/OpenWrap, they often must create hundreds of line items in GAM. Using this tool, your team can now define the settings for:

* Advertiser.
* Placements or ad units.
* Prebid/OpenWrap.

The Line Item Tool then uses those definitions to:

* Create an order with one line item per price level.
* Attach creatives.
* Set placement and/or ad units.
* Set Prebid/OpenWrap key-value targeting.

> **Note:** While this tool covers typical use cases, it may not fit your needs. Review the [Limitations](#limitations) before you begin.

## Get started

You'll need the following to use the Line Item Tool:

* Python version >= 3.6 and a basic knowledge of Python.
* Access to create a service account in the Google Developers Console.
* Admin access to your Google Ad Manager account.

### Create Google Ad Manager credentials

The Line Item Tool requires valid GAM credentials to access your  account. The steps below summarize the steps from the [GAM docs](https://developers.google.com/ad-manager/docs/authentication) and the Google Ads Python libary [auth guide](https://github.com/googleads/googleads-python-lib).

1.  If you haven't done so already, sign up for a [GAM account](https://admanager.google.com/).
2.  Create Google developer credentials:
    *   Go to the [Google Developers Console Credentials page](https://console.developers.google.com/apis/credentials).
    *   On the **Credentials** page, select **Create credentials**, then select **Service account key**.
    *   Select **New service account**, then select _JSON_ key type. You can leave the _role_ blank.
    *   Use **Create** to download a file containing a `.json` private key.
3.  Turn on API access to GAM:
    *   Sign into your [GAM account](https://admanager.google.com/)—_you must have admin rights_.
    *   In the **Admin** section, select **Global settings.**
    *   Turn on **API access** if it isn't already enabled.
    *   Press the **Add a service account user** button.
        *   Use the service account email for the Google developer credentials you created in step 2.
        *   Set the role to, _Administrator_.
        *   Select **Save**.

### Set up the tool

#### Line Item Tool Prerequisites:

*   Python version 3.6 or higher.
*   Python command line package installer, `pip`.

#### Use the following steps to set up the tool:

1.  Clone this repository.
2.  Install Python dependencies by running:
    > `pip install -r requirements.txt`
3.  Rename key:
    *   Rename the Google credentials key you downloaded in step 2 above (`[something].json`), to `key.json`.
    *   Now move it to the root of this repository.
4.  Make a copy of `googleads.example.yaml` and rename it, `googleads.yaml`.
5.  In `googleads.yaml`, set these required fields:
    *   `application_name` - the Google project you named while creating GAM credentials above. It should appear in the top-left of the [credentials page](https://console.developers.google.com/apis/credentials).
    *   `network_code` - your GAM network number. For example, in `https://admanager.google.com/12398712#delivery`, the network code is `12398712`.

#### Verifying set up

To test your set up, from the top-level directory run:

> `python -m dfp.get_orders`

If successful, it returns all the orders in your GAM account.

## Create Line Items for OpenWrap

1. Change the following mandatory settings in `settings.py`:

|**Setting**|**Description**|**Type**|
|:----------|:--------------|:-------|
|`DFP_ORDER_NAME`|The name of your new GAM order.|string|
|`DFP_USER_EMAIL_ADDRESS`|The email of the GAM user acting as trafficker for the new order.|string|
|`DFP_ADVERTISER_NAME`|The name of the GAM advertiser for the new order.|string|
|`DFP_LINEITEM_TYPE`|The type of Lineitem. Can be either `PRICE_PRIORITY`,`SPONSORSHIP`,`NETWORK` or `HOUSE`.|string|
|`DFP_TARGETED_PLACEMENT_NAMES`|The names of GAM placements targeted by the line items. Use empty array for, **Run of Network**.|array of strings|
|`DFP_PLACEMENT_SIZES`|The creative sizes for the targeted placements.|array of objects (for example, `[{'width': '728', 'height': '90'}]`)|
|`PREBID_BIDDER_CODE`|The value of [`pwtpid`](https://github.com/PubMatic/OpenWrap#wrapper-keys-sent-to-dfp) for this partner. Set to `None` to generate line items for all partners. Use array of strings if the line should match multiple partners.|string or array of strings|
|`OPENWRAP_SETUP_TYPE`|Which type of creative to use.  Options are `WEB`, `WEB_SAFEFRAME`, `AMP`, `IN_APP`, `NATIVE`, `VIDEO`, `JWPLAYER`,`ADPOD`.|string|
|`OPENWRAP_BUCKET_CSV`|This CSV lists buckets and price granularity; it sets `pwtecp` targeting for each line item.| string|
|`OPENWRAP_CREATIVE_TEMPLATE` |The creative template name for Native Lineitems. This is only required when `OPENWRAP_SETUP_TYPE`=`NATIVE`. | string |

2. Then, from the root of the repository, run:
    > `python -m tasks.add_new_openwrap_partner`
3. Review your order, line items, and creatives for correctness.
4. Finally, approve the order in GAM.

> **Note:** GAM may warn, "Needs creatives," on the order for ~15 minutes after order creation. This warning is usually incorrect and disappears on its own.

### More optional settings

|**Setting**|**Description**|**Type**|**Default**|
|:----------|:--------------|:-------|:----------|
|`DFP_CREATE_ADVERTISER_IF_DOES_NOT_EXIST`|Determines whether the tool creates an advertiser with `DFP_ADVERTISER_NAME` in GAM if it does not already exist.|bool|`False`
|`DFP_USE_EXISTING_ORDER_IF_EXISTS`|Determines whether to rename an existing order if it matches `DFP_ORDER_NAME.`|bool|`False`|
|`DFP_NUM_CREATIVES_PER_LINE_ITEM`|The number of duplicate creatives to attach to each line item. Due to GAM limitations, this should be equal to or greater than the number of ad units you serve on a given page. |int|Length of setting, `DFP_TARGETED_PLACEMENT_NAMES`|
|`DFP_CURRENCY_CODE`|National currency to use in line items.|string|`'USD'`|
|`DFP_SAME_ADV_EXCEPTION`|Determines whether to set the "Same Advertiser Exception" on line items. Currently works only for OpenWrap.|bool|`False`|
|`DFP_DEVICE_CATEGORIES`|Sets device category targetting for a Line item. Valid values: `Connected TV`, `Desktop`, `Feature Phone`, `Set Top Box`, `Smartphone`, and `Tablet`. Not applicable for 'IN_APP' and 'JWPLAYER'|string or array of strings|None|
|`DFP_ROADBLOCK_TYPE`|Same as **Display Creatives** in previous Line Item Tool version. Valid values: `ONE_OR_MORE` and `AS_MANY_AS_POSSIBLE`.|string|None|
|`LINE_ITEM_PREFIX`|The prefix to insert before a line-item name.|string|None|
|`OPENWRAP_CUSTOM_TARGETING`|Array of extra targeting rules per line item. Not applicable for 'IN_APP' and 'JWPLAYER'|array of arrays (For example, `[("a", "IS", ("1", "2", "3")), ("b", "IS_NOT", ("4", "5", "6"))]`.)|None|
|`CURRENCY_EXCHANGE`|Same as **Currency Module** in the previous Line Item Tool. When used, this option converts the _rate_ calculated from CSV to the network's currency setting. This is applicable for `WEB`, `WEB_SAFEFRAME` and `NATIVE` only. |bool|True|
|`OPENWRAP_USE_1x1_CREATIVE`| When this option is set, the tool creates a single creative with size 1x1 and all lineitems with size overrides. |bool|False|

## Create Line Items for Prebid

1.  Change the following mandatory settings in `settings.py`:

|**Setting**|**Description**|**Type**|
|:----------|:--------------|:-------|
|`DFP_ORDER_NAME`|The name of your new GAM order.|string|
|`DFP_USER_EMAIL_ADDRESS`|Email of the GAM user who will be the trafficker for the new order.|string|
|`DFP_ADVERTISER_NAME`|Name of the GAM advertiser for the new order.|string|
|`DFP_TARGETED_AD_UNIT_NAMES`|Names of GAM ad units the line items should target.|array of strings|
|`DFP_TARGETED_PLACEMENT_NAMES`|Names of GAM placements the line items should target.|array of strings|
|`DFP_PLACEMENT_SIZES`|Creative sizes for the targeted placements.|array of objects (e.g., `[{'width': '728', 'height': '90'}]`)|
|`PREBID_BIDDER_CODE`|The value of [`hb_bidder`](http://prebid.org/dev-docs/publisher-api-reference.html#module_pbjs.bidderSettings) for this partner.|string|
|`PREBID_PRICE_BUCKETS`|[Price granularity](http://prebid.org/dev-docs/publisher-api-reference.html#module_pbjs.setPriceGranularity); used to set `hb_pb` for each line item|object|

2.  Next, from the root of the repository, run:
    > `python -m tasks.add_new_prebid_partner`
3.  Finally, review your order, line items, and creatives to make sure they are correct. Then, approve the order in GAM.

> **Note:** GAM may warn, "Needs creatives" on the order for ~15 minutes after order creation. The warning is usually incorrect and disappears on its own.

### Extra Settings
<a name="extra"></a>
In most cases, you won't need to change these settings.

|**Setting**|**Description**|**Type**|**Default**|
|:----------|:--------------|:-------|:----------|
|`DFP_CREATE_ADVERTISER_IF_DOES_NOT_EXIST`|Determines whether to create an advertiser with `DFP_ADVERTISER_NAME` in GAM if one does not exist.|bool|`False`|
|`DFP_USE_EXISTING_ORDER_IF_EXISTS`|Determines whether to rename an existing order if another matches `DFP_ORDER_NAME.`|bool|`False`|
|`DFP_NUM_CREATIVES_PER_LINE_ITEM`|The number of duplicate creatives to attach to each line item. Due to GAM limitations, this should be equal to or greater than the number of ad units you serve on a given page. |int|Length of setting, `DFP_TARGETED_PLACEMENT_NAMES`|
|`DFP_CURRENCY_CODE`|National currency to use in line items.|string|`'USD'`|
|`DFP_LINE_ITEM_FORMAT`|The format for the line item names.|string|`u'{bidder_code}: HB ${price}'`|

## Limitations

*   Line Item Tool does not change existing orders or line items, it only creates them. If you need to make a change to an order, it's easiest to archive the existing order and recreate it. But you can add new line items in the existing order using the setting DFP_USE_EXISTING_ORDER_IF_EXISTS. See [Extra Settings](#extra) above.
