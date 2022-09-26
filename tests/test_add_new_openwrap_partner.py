
from ast import Constant
from unittest import TestCase

from mock import MagicMock, patch
import json
from unittest.mock import patch

import constant
import settings
import tasks.add_new_openwrap_partner
from tasks.dfp_utils import TargetingKeyGen
from dfp.exceptions import BadSettingException, MissingSettingException
from tasks.price_utils import (
  get_prices_array,
)
obj =tasks.add_new_openwrap_partner.OpenWrapTargetingKeyGen()
email = 'fakeuser@example.com'
advertiser = 'My Advertiser'
advertiser_type = 'ADVERTISER'
order = 'My Cool Order'
adpod_order = 's1_1_My Cool Order'
placements = ['My Site Leaderboard', 'Another Placement']
ad_units = ['Leaderboard Ad Unit', 'Another Ad Unit']
lineitem_type = 'PRICE_PRIORITY'
price_buckets_csv = 'test.csv'
sizes = [
  {
    'width': '300',
    'height': '250'
  },
  {
    'width': '728',
    'height': '90'
  },
]

adpod_creative_size = [
  {
    'width': '1',
    'height': '1'
  }
]

adpod_creative_durations = [5,10]
adpod_slots = [1]

bidder_code = ['mypartner']

@patch.multiple('settings',
  DFP_USER_EMAIL_ADDRESS=email,
  DFP_ADVERTISER_NAME=advertiser,
  DFP_ADVERTISER_TYPE=advertiser_type,
  DFP_ORDER_NAME=order,
  DFP_TARGETED_PLACEMENT_NAMES=placements,
  DFP_LINEITEM_TYPE=lineitem_type,
  DFP_PLACEMENT_SIZES = sizes,
  PREBID_BIDDER_CODE=bidder_code,
  OPENWRAP_BUCKET_CSV=price_buckets_csv,  
  DFP_CREATE_ADVERTISER_IF_DOES_NOT_EXIST=False,
  CURRENCY_EXCHANGE=False,
  ADPOD_SLOTS=adpod_slots,
  VIDEO_LENGTHS =adpod_creative_durations
  )
@patch('googleads.ad_manager.AdManagerClient.LoadFromStorage')
class AddNewOpenwrapPartnerTests(TestCase):

  def test_missing_email_setting(self, mock_dfp_client):
    """
    It throws an exception with a missing setting.
    """
    settings.DFP_USER_EMAIL_ADDRESS = None
    with self.assertRaises(MissingSettingException):
      tasks.add_new_openwrap_partner.main()

  def test_missing_advertiser_setting(self, mock_dfp_client):
    """
    It throws an exception with a missing setting.
    """
    settings.DFP_ADVERTISER_NAME = None
    with self.assertRaises(MissingSettingException):
      tasks.add_new_openwrap_partner.main()

  def test_missing_advertiser_type(self,mock_dfp_client):
    """
    It throws an exception with a Bad setting.
    """
    settings.DFP_ADVERTISER_TYPE = ['ADVERTISER','AD_NETWORK']  
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main()
    
  def test_missing_order_setting(self, mock_dfp_client):
    """
    It throws an exception with a missing setting.
    """
    settings.DFP_ORDER_NAME = None
    with self.assertRaises(MissingSettingException):
      tasks.add_new_openwrap_partner.main()

  def test_missing_lineitem_type_setting(self, mock_dfp_client):
    """
    It throws an exception with a missing setting.
    """
    settings.DFP_LINEITEM_TYPE = None
    with self.assertRaises(MissingSettingException):
      tasks.add_new_openwrap_partner.main()

  @patch('settings.OPENWRAP_SETUP_TYPE', 'abcd', create=True)
  def test_wrong_setup_type(self,mock_dfp_client):
    """
    It throws an exception with a Bad setting.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main()

  @patch('settings.OPENWRAP_SETUP_TYPE', None, create=True)
  def test_missing_price_bucket_csv(self, mock_dfp_client):
    """
    It throws an exception with a missing setting.
    """
    settings.OPENWRAP_BUCKET_CSV = None
    with self.assertRaises(MissingSettingException):
      tasks.add_new_openwrap_partner.main()

  @patch('settings.OPENWRAP_SETUP_TYPE', constant.ADPOD, create=True)
  def test_missing_adpod_contains_atleast_one_slot(self, mock_dfp_client):
    """
    It throws an exception with a missing setting.
    """
    settings.ADPOD_SLOTS=[]
    with self.assertRaises(MissingSettingException):
      tasks.add_new_openwrap_partner.main()     

  @patch('settings.OPENWRAP_SETUP_TYPE', constant.ADPOD, create=True)
  def test_missing_adpod_creative_duration(self, mock_dfp_client):
    """
    It throws an exception with a missing setting.
    """
    settings.VIDEO_LENGTHS = None
    with self.assertRaises(MissingSettingException):
      tasks.add_new_openwrap_partner.main()      
 
  @patch('settings.OPENWRAP_SETUP_TYPE', constant.ADPOD, create=True)
  def test_missing_adpod_creative_contain_atleast_one_duration(self, mock_dfp_client):
    """
    It throws an exception with a missing setting.
    """
    settings.VIDEO_LENGTHS=[]
    with self.assertRaises(MissingSettingException):
      tasks.add_new_openwrap_partner.main()      
  

  @patch('settings.OPENWRAP_SETUP_TYPE', constant.WEB, create=True)
  def test_missing_placement_size_in_other_than_native(self,mock_dfp_client):
    """
    It throws an exception with a missing setting.
    """
    settings.DFP_PLACEMENT_SIZES= None
    with self.assertRaises(MissingSettingException):
      tasks.add_new_openwrap_partner.main()      
 
  @patch('settings.OPENWRAP_SETUP_TYPE', constant.ADPOD, create=True)
  def test_missing_adpod_placement_size_1(self, mock_dfp_client):
    """
    It throws an exception with a missing setting.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main()    

  @patch('settings.OPENWRAP_SETUP_TYPE', constant.WEB, create=True)
  def test_wrong_placement_size_in_other_than_native(self,mock_dfp_client):
    """
    It throws an exception with a Bad setting.
    """
    settings.DFP_PLACEMENT_SIZES= []
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main() 

  @patch('settings.OPENWRAP_SETUP_TYPE', constant.NATIVE, create=True)
  def test_missing_creative_template(self,mock_dfp_client):
    """
    It throws an exception with a missing setting.
    """
    settings.OPENWRAP_CREATIVE_TEMPLATE= None
    with self.assertRaises(MissingSettingException):
      tasks.add_new_openwrap_partner.main() 

  @patch('settings.OPENWRAP_SETUP_TYPE', constant.NATIVE, create=True)
  def test_wrong_creative_template(self,mock_dfp_client):
    """
    It throws an exception with a Bad setting.
    """
    settings.OPENWRAP_CREATIVE_TEMPLATE= int(1)
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main() 

  
  def test_wrong_bidder_code_setting(self,mock_dfp_client):
    """
    It throws an exception with a Bad setting.
    """
    settings.PREBID_BIDDER_CODE= int(1)
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main() 

  @patch('settings.DFP_SAME_ADV_EXCEPTION',1,create=True)
  def test_wrong_same_adv_exception_setting(self,mock_dfp_client):
    """
    It throws an exception with a Bad setting.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main() 

  @patch('settings.DFP_DEVICE_CATEGORIES',1,create=True)
  def test_wrong_device_catagories_setting(self,mock_dfp_client):
    """
    It throws an exception with a Bad setting.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main() 

  @patch('settings.DFP_ROADBLOCK_TYPE','test',create=True)
  def test_wrong_roadbloack_type_setting(self,mock_dfp_client):
    """
    It throws an exception with a Bad setting.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main()  
  
  @patch('settings.LINE_ITEM_PREFIX',1,create=True)
  def test_wrong_lineitem_prefix_setting(self,mock_dfp_client):
    """
    It throws an exception with a Bad setting.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main() 

  @patch('settings.OPENWRAP_USE_1x1_CREATIVE',1,create=True)
  def test_wrong_use_1x1_creative_setting(self,mock_dfp_client):
    """
    It throws an exception with a Bad setting.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main() 

  @patch('settings.OPENWRAP_CUSTOM_TARGETING',1,create=True)
  def test_wrong_custom_targeting_setting(self,mock_dfp_client):
    """
    It throws an exception with a Bad setting.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main()

  @patch('settings.OPENWRAP_CUSTOM_TARGETING',[("a", "IS", (1,2,3),1), ("b", "IS_NOT", ("4", "5", "6"))],create=True)
  def test_wrong_custom_targeting_length_setting(self,mock_dfp_client):
    """
    It throws an exception with a Bad setting.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main()

  @patch('settings.OPENWRAP_CUSTOM_TARGETING',[("a", "TEST", ("1","2","3")), ("b", "TEST1", ("4", "5", "6"))],create=True)
  def test_wrong_custom_targeting_IS_and_IS_NOT(self,mock_dfp_client):
    """
    It throws an exception with a Bad setting.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main() 


  @patch('settings.OPENWRAP_CUSTOM_TARGETING',[("a", "IS", (1)), ("b", "IS_NOT", (4))],create=True)
  def test_wrong_custom_targeting_instance(self,mock_dfp_client):
    """
    It throws an exception with a Bad setting.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.main()
  

  def test_validate_CSVValues_can_not_negative(self,mock_dfp_client):
    """
    It throws an exception with start range and end range can not be negative.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.validateCSVValues(-1,-2,1,1)

  def test_validate_CSVValues_start_range_more_than_end_range(self,mock_dfp_client):
    """
    It throws an exception with Start range can not be more than end range.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.validateCSVValues(4,1,1,1)

  def test_validate_CSVValues_rate_id_can_1_or_2(self,mock_dfp_client):
    """
    It throws an exception with Rate id can only be 1 or 2.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.validateCSVValues(1,5,1,3)
  
  def test_validate_CSVValues_Start_range_can_not_be_less_than_0_point_01_for_granularity_0_point_01(self,mock_dfp_client):
    """
    It throws an exception with Start range can not be less than 0.01 for granularity 0.01.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.validateCSVValues(0.001,5,0.01,2)

  def test_validate_CSVValues_End_range_can_not_be_more_than_999(self,mock_dfp_client):
    """
    It throws an exception with End range can not be more than 999.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.validateCSVValues(1,1000,1,1)
  
  def test_validate_CSVValues_0_is_not_accepted_as_granularity(self,mock_dfp_client):
    """
    It throws an exception with Zero is not accepted as granularity.
    """
    with self.assertRaises(BadSettingException):
      tasks.add_new_openwrap_partner.validateCSVValues(1,5,0,1)

 
  @patch('dfp.get_orders.get_order_by_name',return_value={
               'id': 1234567,
               'order_count': 1,
               'lic': 10,
               'name': 'test_order_name'
           } )
  @patch('dfp.get_line_items.get_line_item_count_by_order',return_value=10)
  def test_get_exixting_order_details(self,mock_dfp_client,mock_order_name,mock_lic):
   
    actual=tasks.add_new_openwrap_partner.get_existing_order_details('test','order_name')
    self.assertGreater(constant.LINE_ITEMS_LIMIT,actual['lic'])

  
  @patch('shortuuid.uuid',return_value=1234)
  def test_get_unique_id_WEB(self,mock_dfp_client,mock_uuid):
    actual_uid=tasks.add_new_openwrap_partner.get_unique_id(constant.WEB)
    expected_uid=u'DISPLAY_{}'.format('1234')
    self.assertEqual(actual_uid,expected_uid)
  
  @patch('shortuuid.uuid',return_value=1234)
  def test_get_unique_id_AMP(self,mock_dfp_client,mock_uuid):
    actual_uid=tasks.add_new_openwrap_partner.get_unique_id(constant.AMP)
    expected_uid=u'AMP_{}'.format('1234')
    self.assertEqual(actual_uid,expected_uid)
  
  @patch('shortuuid.uuid',return_value=1234)
  def test_get_unique_id_IN_APP(self,mock_dfp_client,mock_uuid):
    actual_uid=tasks.add_new_openwrap_partner.get_unique_id(constant.IN_APP)
    expected_uid=u'INAPP_{}'.format('1234')
    self.assertEqual(actual_uid,expected_uid)
  
  @patch('shortuuid.uuid',return_value=1234)
  def test_get_unique_id_IN_APP_VIDEO(self,mock_dfp_client,mock_uuid):
    actual_uid=tasks.add_new_openwrap_partner.get_unique_id(constant.IN_APP_VIDEO)
    expected_uid=u'INAPP_VIDEO_{}'.format('1234')
    self.assertEqual(actual_uid,expected_uid)
  
  @patch('shortuuid.uuid',return_value=1234)
  def test_get_unique_id_NATIVE(self,mock_dfp_client,mock_uuid):
    actual_uid=tasks.add_new_openwrap_partner.get_unique_id(constant.NATIVE)
    expected_uid=u'NATIVE_{}'.format('1234')
    self.assertEqual(actual_uid,expected_uid)

  @patch('shortuuid.uuid',return_value=1234)
  def test_get_unique_id_VIDEO(self,mock_dfp_client,mock_uuid):
    actual_uid=tasks.add_new_openwrap_partner.get_unique_id(constant.VIDEO)
    expected_uid=u'VIDEO_{}'.format('1234')
    self.assertEqual(actual_uid,expected_uid)
  
  @patch('shortuuid.uuid',return_value=1234)
  def test_get_unique_id_JWP(self,mock_dfp_client,mock_uuid):
    actual_uid=tasks.add_new_openwrap_partner.get_unique_id(constant.JW_PLAYER)
    expected_uid=u'JWP_{}'.format('1234')
    self.assertEqual(actual_uid,expected_uid)

  @patch('shortuuid.uuid',return_value=1234)
  def test_get_unique_id_ADPOD(self,mock_dfp_client,mock_uuid):
    actual_uid=tasks.add_new_openwrap_partner.get_unique_id(constant.ADPOD)
    expected_uid=u'VIDEO_{}'.format('1234')
    self.assertEqual(actual_uid,expected_uid)
  
  @patch('settings.DFP_CURRENCY_CODE', 'EUR', create=True)
  @patch('tasks.add_new_openwrap_partner.setup_partner')
  @patch('tasks.add_new_openwrap_partner.input', return_value='y')
  @patch('settings.OPENWRAP_SETUP_TYPE', None, create=True)
  def test_custom_currency_code(self, mock_input, mock_setup_partners,
    mock_dfp_client):
    """
    Ensure we use the currency code setting if it exists.
    """
    tasks.add_new_openwrap_partner.main()
    args, _ = mock_setup_partners.call_args
    self.assertEqual(args[14], 'EUR')

  @patch('tasks.add_new_openwrap_partner.setup_partner')
  @patch('tasks.add_new_openwrap_partner.input', return_value='n')
  @patch('settings.OPENWRAP_SETUP_TYPE', None, create=True)
  def test_user_confirmation_rejected(self, mock_input, 
    mock_setup_partners, mock_dfp_client):
    """
    Make sure we exit when the user rejects the confirmation.
    """
    tasks.add_new_openwrap_partner.main()
    mock_setup_partners.assert_not_called()

  @patch('tasks.add_new_openwrap_partner.setup_partner')
  @patch('tasks.add_new_openwrap_partner.input', return_value='asdf')
  @patch('settings.OPENWRAP_SETUP_TYPE', None, create=True) 
  def test_user_confirmation_not_accepted(self, mock_input, 
    mock_setup_partners, mock_dfp_client):
    """
    Make sure we exit when the user types something other than 'y'.
    """
    tasks.add_new_openwrap_partner.main()
    mock_setup_partners.assert_not_called()

  @patch('tasks.add_new_openwrap_partner.setup_partner')
  @patch('tasks.add_new_openwrap_partner.input', return_value='y')
  @patch('settings.OPENWRAP_SETUP_TYPE', None, create=True) 
  def test_user_confirmation_accepted(self, mock_input, 
    mock_setup_partners, mock_dfp_client):
    """
    Make sure we start the process when the user confirms we should proceed.
    """
    tasks.add_new_openwrap_partner.main()
    mock_setup_partners.assert_called_once()

  @patch('settings.DFP_NUM_CREATIVES_PER_LINE_ITEM', 5, create=True)
  @patch('tasks.add_new_openwrap_partner.setup_partner')
  @patch('tasks.add_new_openwrap_partner.input', return_value='y')
  @patch('settings.OPENWRAP_SETUP_TYPE', None, create=True) 
  def test_num_duplicate_creatives_from_settings(self, mock_input, 
    mock_setup_partners, mock_dfp_client):
    """
    Make sure we use the settings for the number of creatives per line item
    if the setting exists.
    """
    tasks.add_new_openwrap_partner.main()
    args, _ = mock_setup_partners.call_args
    num_creatives = args[12]
    self.assertEqual(num_creatives, 5)

  @patch('settings.DFP_NUM_CREATIVES_PER_LINE_ITEM', None, create=True)
  @patch('tasks.add_new_openwrap_partner.setup_partner')
  @patch('tasks.add_new_openwrap_partner.input', return_value='y')
  @patch('settings.OPENWRAP_SETUP_TYPE', None, create=True) 
  def test_num_duplicate_creatives_no_settings(self, mock_input, 
    mock_setup_partners, mock_dfp_client):
    """
    Make sure we use the default number of creatives per line item if the
    setting does not exist.
    """
    tasks.add_new_openwrap_partner.main()
    args, _ = mock_setup_partners.call_args
    num_creatives = args[12]
    self.assertEqual(num_creatives, len(placements))


  @patch('settings.DFP_NUM_CREATIVES_PER_LINE_ITEM', None, create=True)
  @patch('tasks.add_new_openwrap_partner.setup_partner')
  @patch('tasks.add_new_openwrap_partner.input', return_value='y')
  @patch('settings.OPENWRAP_SETUP_TYPE', None, create=True) 
  def test_num_duplicate_creatives_no_placements(self, mock_input, 
    mock_setup_partners, mock_dfp_client):
    """
    Make sure we use the default number of creatives per line item if the
    setting does not exist.
    """
    settings.DFP_TARGETED_PLACEMENT_NAMES = None
    tasks.add_new_openwrap_partner.main()
    args, _ = mock_setup_partners.call_args
    num_creatives = args[12]
    self.assertEqual(num_creatives, 1)

  @patch('settings.OPENWRAP_SETUP_TYPE', constant.IN_APP, create=True)
  @patch('tasks.add_new_openwrap_partner.setup_partner')
  @patch('tasks.add_new_openwrap_partner.load_price_csv')
  @patch('tasks.add_new_openwrap_partner.input', return_value='y')
  def test_OPENWRAP_SETUP_TYPE_inapp(self, mock_input, mock_load_price_csv,
    mock_setup_partners, mock_dfp_client):
    """
    Make sure we use the default number of creatives per line item if the
    setting does not exist.
    """
    tasks.add_new_openwrap_partner.main()
    args, _ = mock_setup_partners.call_args
    
    self.assertEqual(args[10], constant.IN_APP)
    #check roadblock type
    self.assertEqual(args[19], 'AS_MANY_AS_POSSIBLE')
    #check bidder code
    self.assertEqual(args[8], None)
    #check device targetting
    self.assertEqual(args[17], None)
    #check custom targetting
    self.assertEqual(args[15], None)

  @patch('settings.OPENWRAP_SETUP_TYPE', constant.IN_APP_VIDEO, create=True)
  @patch('tasks.add_new_openwrap_partner.setup_partner')
  @patch('tasks.add_new_openwrap_partner.load_price_csv')
  @patch('tasks.add_new_openwrap_partner.input', return_value='y')
  def test_openwrap_creative_type_inapp_video(self, mock_input, mock_load_price_csv,
    mock_setup_partners, mock_dfp_client):
    """
    Make sure we use the default number of creatives per line item if the
    setting does not exist.
    """
    tasks.add_new_openwrap_partner.main()
    args, _ = mock_setup_partners.call_args
    
    self.assertEqual(args[10], constant.IN_APP_VIDEO)
    #check roadblock type
    self.assertEqual(args[19], 'ONE_OR_MORE')
    #check bidder code
    self.assertEqual(args[8], None)
    #check device targetting
    self.assertEqual(args[17], None)
    #check custom targetting
    self.assertEqual(args[15], None)
    
  @patch('settings.OPENWRAP_SETUP_TYPE', constant.JW_PLAYER, create=True)
  @patch('tasks.add_new_openwrap_partner.setup_partner')
  @patch('tasks.add_new_openwrap_partner.load_price_csv')
  @patch('tasks.add_new_openwrap_partner.input', return_value='y')
  def test_OPENWRAP_SETUP_TYPE_jwplayer(self, mock_input, mock_load_price_csv,
    mock_setup_partners, mock_dfp_client):
    """
    Make sure we use the default number of creatives per line item if the
    setting does not exist.
    """
    tasks.add_new_openwrap_partner.main()
    args, _ = mock_setup_partners.call_args
    
    self.assertEqual(args[10], constant.JW_PLAYER)
    #check roadblock type
    self.assertEqual(args[19], 'ONE_OR_MORE')
    #check bidder code
    self.assertEqual(args[8], ['pubmatic'])
    #check device targetting
    self.assertEqual(args[17], None)
    #check custom targetting
    self.assertEqual(args[15], None)

  @patch('settings.OPENWRAP_SETUP_TYPE', constant.VIDEO, create=True)
  @patch('tasks.add_new_openwrap_partner.setup_partner')
  @patch('tasks.add_new_openwrap_partner.load_price_csv')
  @patch('tasks.add_new_openwrap_partner.input', return_value='y')
  def test_OPENWRAP_SETUP_TYPE_video(self, mock_input, mock_load_price_csv,
    mock_setup_partners, mock_dfp_client):
    """
    Make sure we use the default number of creatives per line item if the
    setting does not exist.
    """
    tasks.add_new_openwrap_partner.main()
    args, _ = mock_setup_partners.call_args
    
    #check platform
    self.assertEqual(args[10], constant.VIDEO)
    #check roadblock type
    self.assertEqual(args[19], 'ONE_OR_MORE')

  @patch('settings.OPENWRAP_SETUP_TYPE', constant.ADPOD, create=True)
  @patch('tasks.add_new_openwrap_partner.setup_partner')
  @patch('tasks.add_new_openwrap_partner.load_price_csv')
  @patch('tasks.add_new_openwrap_partner.input', return_value='y')
  def test_OPENWRAP_SETUP_TYPE_adpod(self, mock_input, mock_load_price_csv,
    mock_setup_partners, mock_dfp_client):
    """
    Make sure we use the default number of creatives per line item if the
    setting does not exist.
    """
    settings.DFP_PLACEMENT_SIZES = adpod_creative_size
    tasks.add_new_openwrap_partner.main()
    args, _ = mock_setup_partners.call_args
    
    #check platform
    self.assertEqual(args[10], constant.ADPOD)
    #check roadblock type
    self.assertEqual(args[19], 'ONE_OR_MORE')  

  @patch('tasks.add_new_openwrap_partner.create_line_item_configs')
  @patch('tasks.add_new_openwrap_partner.DFPValueIdGetter')
  @patch('tasks.add_new_openwrap_partner.get_or_create_dfp_targeting_key')
  @patch('dfp.associate_line_items_and_creatives')
  @patch('dfp.create_creatives')
  @patch('dfp.create_line_items')
  @patch('tasks.add_new_openwrap_partner.get_unique_id', return_value = 'DISPLAY_xyz')
  @patch('dfp.create_orders')
  @patch('dfp.get_advertisers')
  @patch('dfp.get_device_categories')
  @patch('dfp.get_placements')
  @patch('dfp.get_users')
  def test_setup_partner(self, mock_get_users, mock_get_placements, mock_get_device_categories,
    mock_get_advertisers, mock_create_orders, mock_get_unique_id,
    mock_create_line_items, mock_create_creatives, mock_licas, mock_dfp_client,
    mock_get_or_create_dfp_targeting_key, mock_dfp_value_id_getter, mock_create_line_item_configs):
    """
    It calls all expected DFP functions.
    """

    mock_get_users.get_user_id_by_email = MagicMock(return_value=14523)
    mock_get_placements.get_placement_ids_by_name = MagicMock(
      return_value=[1234567, 9876543])
    mock_get_device_categories.get_device_categories = MagicMock(
       return_value={
        'Connected TV': 30004,
        'Desktop': 30000,
        'Feature Phone': 30003,
        'Set Top Box': 30006,
        'Smartphone': 30001, 
        'Tablet': 30002
      }
    )
    mock_get_advertisers.get_advertiser_id_by_name = MagicMock(
      return_value=246810)
    mock_create_orders.create_order = MagicMock(return_value=1357913)
    mock_create_creatives.create_creatives = MagicMock(return_value = [54321,98765])
    mock_create_line_items.create_line_items = MagicMock(
      return_value =[543210, 987650])

    prices = [{
       'start': 1,
       'end': 2,
       'granularity': 1,
       'rate': 1.5
    }]

    tasks.add_new_openwrap_partner.setup_partner(user_email=email, advertiser_name=advertiser, 
                                               advertiser_type = advertiser_type, order_name=order,
                                               placements=placements, sizes=sizes, lineitem_type = lineitem_type,
                                               lineitem_prefix = 'LI_123', bidder_code=bidder_code, prices=prices,
                                               setup_type = constant.WEB, creative_template = None, num_creatives=2,
                                               use_1x1=False, currency_code='USD', custom_targeting= None,
                                               same_adv_exception= False, device_categories=['Desktop'], device_capabilities=None, 
                                               roadblock_type= 'ONE_OR_MORE',slot = None,adpod_creative_durations=None)

    mock_get_users.get_user_id_by_email.assert_called_once_with(email)
    mock_get_placements.get_placement_ids_by_name.assert_called_once_with(
      placements)
    mock_get_advertisers.get_advertiser_id_by_name.assert_called_once_with(
      advertiser, advertiser_type)
    mock_create_orders.create_order.assert_called_once_with(order, 246810,
      14523)
    (mock_create_creatives.create_duplicate_creative_configs
      .assert_called_once_with(bidder_code[0], order, 246810,  [{'width': '300', 'height': '250'}, {'width': '728', 'height': '90'}], 2, creative_file='creative_snippet_openwrap.html', prefix='DISPLAY_xyz', safe_frame=False))
    mock_create_creatives.create_creatives.assert_called_once()
    mock_create_line_items.create_line_items.assert_called_once()
    mock_licas.make_licas.assert_called_once_with([543210, 987650], [54321, 98765], durations=None, setup_type='WEB', size_overrides=[], slot=None)



  @patch('tasks.add_new_openwrap_partner.create_line_item_configs')
  @patch('tasks.add_new_openwrap_partner.DFPValueIdGetter')
  @patch('tasks.add_new_openwrap_partner.get_or_create_dfp_targeting_key')
  @patch('dfp.associate_line_items_and_creatives')
  @patch('dfp.create_creative_sets')
  @patch('dfp.create_creatives')
  @patch('dfp.create_line_items')
  @patch('tasks.add_new_openwrap_partner.get_unique_id', return_value = 'VIDEO_xyz')
  @patch('dfp.create_orders')
  @patch('dfp.get_advertisers')
  @patch('dfp.get_placements')
  @patch('dfp.get_users')
  def test_setup_partner_for_video(self, mock_get_users, mock_get_placements,
    mock_get_advertisers, mock_create_orders, mock_get_unique_id,
    mock_create_line_items, mock_create_creatives, mock_create_creative_sets, mock_licas, mock_dfp_client,
    mock_get_or_create_dfp_targeting_key, mock_dfp_value_id_getter, mock_create_line_item_configs):
    """
    It calls all expected DFP functions.
    """

    mock_get_users.get_user_id_by_email = MagicMock(return_value=14523)
    mock_get_placements.get_placement_ids_by_name = MagicMock(
      return_value=[1234567, 9876543])
    mock_get_advertisers.get_advertiser_id_by_name = MagicMock(
      return_value=246810)
    mock_create_orders.create_order = MagicMock(return_value=1357913)
    mock_create_creatives.create_creatives = MagicMock(return_value = [54321,98765])
    mock_create_creative_sets.create_creative_sets = MagicMock(return_value = [54321,98765])
    mock_create_line_items.create_line_items = MagicMock(
      return_value =[543210, 987650])

    prices = [{
       'start': 1,
       'end': 2,
       'granularity': 1,
       'rate': 1.5
    }]

    tasks.add_new_openwrap_partner.setup_partner(user_email=email, advertiser_name=advertiser, 
                                               advertiser_type = advertiser_type, order_name=order,
                                               placements=placements, sizes=sizes, lineitem_type = lineitem_type,
                                               lineitem_prefix = 'LI_123', bidder_code=bidder_code, prices=prices,
                                               setup_type = constant.VIDEO, creative_template = None, num_creatives=2,
                                               use_1x1=False, currency_code='USD', custom_targeting= None,
                                               same_adv_exception= False, device_categories=None, device_capabilities=None, 
                                               roadblock_type= 'ONE_OR_MORE', slot = None,adpod_creative_durations=None)

    mock_get_users.get_user_id_by_email.assert_called_once_with(email)
    mock_get_placements.get_placement_ids_by_name.assert_called_once_with(
      placements)
    mock_get_advertisers.get_advertiser_id_by_name.assert_called_once_with(
      advertiser, advertiser_type)
    mock_create_orders.create_order.assert_called_once_with(order, 246810,
      14523)
    (mock_create_creatives.create_creative_configs_for_video
      .assert_called_once_with(246810, sizes, 'VIDEO_xyz', constant.VIDEO_VAST_URL, constant.VIDEO_DURATION))
    mock_create_creatives.create_creatives.assert_called_once()
    mock_create_creative_sets.create_creative_set_config.assert_called_once_with([54321,98765], sizes, 'VIDEO_xyz' )
    mock_create_creative_sets.create_creative_sets.assert_called_once()
    mock_create_line_items.create_line_items.assert_called_once()
    mock_licas.make_licas.assert_called_once_with([543210, 987650], [54321, 98765], durations=None, setup_type='VIDEO', size_overrides=[], slot=None)


  @patch('tasks.add_new_openwrap_partner.create_line_item_configs')
  @patch('tasks.add_new_openwrap_partner.DFPValueIdGetter')
  @patch('tasks.add_new_openwrap_partner.get_or_create_dfp_targeting_key')
  @patch('dfp.associate_line_items_and_creatives')
  @patch('dfp.create_creative_sets')
  @patch('dfp.create_creatives')
  @patch('dfp.create_line_items')
  @patch('tasks.add_new_openwrap_partner.get_unique_id', return_value = 'ADPOD_xyz')
  @patch('dfp.create_orders')
  @patch('dfp.get_advertisers')
  @patch('dfp.get_placements')
  @patch('dfp.get_users')
  def test_setup_partner_for_adpod(self, mock_get_users, mock_get_placements,
    mock_get_advertisers, mock_create_orders, mock_get_unique_id,
    mock_create_line_items, mock_create_creatives, mock_create_creative_sets, mock_licas, mock_dfp_client,
    mock_get_or_create_dfp_targeting_key, mock_dfp_value_id_getter, mock_create_line_item_configs):
    """
    It calls all expected DFP functions.
    """

    mock_get_users.get_user_id_by_email = MagicMock(return_value=14523)
    mock_get_placements.get_placement_ids_by_name = MagicMock(
      return_value=[1234567, 9876543])
    mock_get_advertisers.get_advertiser_id_by_name = MagicMock(
      return_value=246810)
    mock_create_orders.create_order = MagicMock(return_value=1357913)
    mock_create_creatives.create_creatives = MagicMock(return_value = [54321,98765])
    mock_create_creative_sets.create_creative_sets = MagicMock(return_value = [54321,98765])
    mock_create_line_items.create_line_items = MagicMock(
      return_value =[543210, 987650])

    prices = [{
       'start': 5,
       'end': 10,
       'granularity': 5,
       'rate': 5
    }]

    tasks.add_new_openwrap_partner.setup_partner(user_email=email, advertiser_name=advertiser, 
                                               advertiser_type = advertiser_type, order_name=order,
                                               placements=placements, sizes=adpod_creative_size, lineitem_type = lineitem_type,
                                               lineitem_prefix = 'LI_123', bidder_code=bidder_code, prices=prices,
                                               setup_type = constant.ADPOD, creative_template = None, num_creatives=2,
                                               use_1x1=False, currency_code='USD', custom_targeting= None,
                                               same_adv_exception= False, device_categories=None, device_capabilities=None, 
                                               roadblock_type= 'ONE_OR_MORE',  slot = 's1',adpod_creative_durations=[5,10])

    mock_get_users.get_user_id_by_email.assert_called_once_with(email)
    mock_get_placements.get_placement_ids_by_name.assert_called_once_with(
      placements)
    mock_get_advertisers.get_advertiser_id_by_name.assert_called_once_with(
      advertiser, advertiser_type)
    mock_create_orders.create_order.assert_called_once_with(adpod_order, 246810,
      14523)
    (mock_create_creatives.create_creative_configs_for_adpod
      .assert_called_once_with(246810, adpod_creative_size, 'ADPOD_xyz', constant.ADPOD_VIDEO_VAST_URL,adpod_creative_durations,'s1'))
    mock_create_creatives.create_creatives.assert_called_once()
    mock_create_creative_sets.create_creative_set_config_adpod.assert_called_once_with([54321,98765], adpod_creative_size, 'ADPOD_xyz' , adpod_creative_durations,'s1')
    mock_create_creative_sets.create_creative_sets.assert_called_once()
    mock_create_line_items.create_line_items.assert_called_once()
    mock_licas.make_licas.assert_called_once_with([543210, 987650], [54321, 98765], durations=[5, 10], setup_type='ADPOD', size_overrides=[], slot='s1')


  @patch('tasks.add_new_openwrap_partner.create_line_item_configs')
  @patch('tasks.add_new_openwrap_partner.DFPValueIdGetter')
  @patch('tasks.add_new_openwrap_partner.get_or_create_dfp_targeting_key')
  @patch('dfp.associate_line_items_and_creatives')
  @patch('dfp.create_creatives')
  @patch('dfp.create_line_items')
  @patch('tasks.add_new_openwrap_partner.get_unique_id', return_value = 'INAPP_xyz')
  @patch('dfp.create_orders')
  @patch('dfp.get_advertisers')
  @patch('dfp.get_device_capabilities')
  @patch('dfp.get_placements')
  @patch('dfp.get_users')
  def test_setup_partner_for_inapp(self, mock_get_users, mock_get_placements, mock_get_device_capabilities,
    mock_get_advertisers, mock_create_orders, mock_get_unique_id,
    mock_create_line_items, mock_create_creatives, mock_licas, mock_dfp_client,
    mock_get_or_create_dfp_targeting_key, mock_dfp_value_id_getter, mock_create_line_item_configs):
    """
    It calls all expected DFP functions.
    """

    mock_get_users.get_user_id_by_email = MagicMock(return_value=14523)
    mock_get_placements.get_placement_ids_by_name = MagicMock(
      return_value=[1234567, 9876543])
    mock_get_device_capabilities.get_device_capabilities = MagicMock(
      return_value= {
        'Mobile Apps': 5005,
        'MRAID v1': 5001,
        'MRAID v2': 5006,
        'Phone calls': 5000
      }
    )
    mock_get_advertisers.get_advertiser_id_by_name = MagicMock(
      return_value=246810)
    mock_create_orders.create_order = MagicMock(return_value=1357913)
    mock_create_creatives.create_creatives = MagicMock(return_value = [54321,98765])
    mock_create_line_items.create_line_items = MagicMock(
      return_value =[543210, 987650])

    prices = [{
       'start': 1,
       'end': 2,
       'granularity': 1,
       'rate': 1.5
    }]

    tasks.add_new_openwrap_partner.setup_partner(user_email=email, advertiser_name=advertiser, 
                                               advertiser_type = advertiser_type, order_name=order,
                                               placements=placements, sizes=sizes, lineitem_type = lineitem_type,
                                               lineitem_prefix = 'LI_123', bidder_code=bidder_code, prices=prices,
                                               setup_type = constant.IN_APP, creative_template = None, num_creatives=2,
                                               use_1x1=False, currency_code='USD', custom_targeting= None,
                                               same_adv_exception= False, device_categories=None, device_capabilities=['Mobile Apps'], 
                                               roadblock_type= 'ONE_OR_MORE', slot = None,adpod_creative_durations=None)

    mock_get_device_capabilities.get_device_capabilities.assert_called_once()   
    (mock_create_creatives.create_duplicate_creative_configs
      .assert_called_once_with(bidder_code[0], order, 246810,  sizes, 2, creative_file='creative_snippet_openwrap_in_app.html', prefix='INAPP_xyz', safe_frame=False))
    mock_licas.make_licas.assert_called_once_with([543210,987650], [54321,98765], durations=None, setup_type='IN_APP', size_overrides=[], slot=None)




  @patch('tasks.add_new_openwrap_partner.create_line_item_configs')
  @patch('tasks.add_new_openwrap_partner.DFPValueIdGetter')
  @patch('tasks.add_new_openwrap_partner.get_or_create_dfp_targeting_key')
  @patch('dfp.associate_line_items_and_creatives')
  @patch('dfp.create_creative_sets')
  @patch('dfp.create_creatives')
  @patch('dfp.create_line_items')
  @patch('tasks.add_new_openwrap_partner.get_unique_id', return_value = 'IN_APP_VIDEO_xyz')
  @patch('dfp.create_orders')
  @patch('dfp.get_advertisers')
  @patch('dfp.get_device_capabilities')
  @patch('dfp.get_placements')
  @patch('dfp.get_users')
  def test_setup_partner_for_in_app_video(self, mock_get_users, mock_get_placements, mock_get_device_capabilities,
    mock_get_advertisers, mock_create_orders, mock_get_unique_id,
    mock_create_line_items, mock_create_creatives, mock_create_creative_sets, mock_licas, mock_dfp_client,
    mock_get_or_create_dfp_targeting_key, mock_dfp_value_id_getter, mock_create_line_item_configs):
    """
    It calls all expected DFP functions.
    """

    mock_get_users.get_user_id_by_email = MagicMock(return_value=14523)
    mock_get_placements.get_placement_ids_by_name = MagicMock(
      return_value=[1234567, 9876543])
    mock_get_device_capabilities.get_device_capabilities = MagicMock(
      return_value= {
        'Mobile Apps': 5005,
        'MRAID v1': 5001,
        'MRAID v2': 5006,
        'Phone calls': 5000
      }
    )
    mock_get_advertisers.get_advertiser_id_by_name = MagicMock(
      return_value=246810)
    mock_create_orders.create_order = MagicMock(return_value=1357913)
    mock_create_creatives.create_creatives = MagicMock(return_value = [54321,98765])
    mock_create_creative_sets.create_creative_sets = MagicMock(return_value = [54321,98765])
    mock_create_line_items.create_line_items = MagicMock(
      return_value =[543210, 987650])

    prices = [{
       'start': 1,
       'end': 2,
       'granularity': 1,
       'rate': 1.5
    }]

    tasks.add_new_openwrap_partner.setup_partner(user_email=email, advertiser_name=advertiser, 
                                               advertiser_type = advertiser_type, order_name=order,
                                               placements=placements, sizes=sizes, lineitem_type = lineitem_type,
                                               lineitem_prefix = 'LI_123', bidder_code=bidder_code, prices=prices,
                                               setup_type = constant.IN_APP_VIDEO, creative_template = None, num_creatives=2,
                                               use_1x1=False, currency_code='USD', custom_targeting= None,
                                               same_adv_exception= False, device_categories=None, device_capabilities=['Mobile Apps'], 
                                               roadblock_type= 'ONE_OR_MORE', slot = None,adpod_creative_durations=None)

    mock_get_device_capabilities.get_device_capabilities.assert_called_once()
    mock_get_users.get_user_id_by_email.assert_called_once_with(email)
    mock_get_placements.get_placement_ids_by_name.assert_called_once_with(
      placements)
    mock_get_advertisers.get_advertiser_id_by_name.assert_called_once_with(
      advertiser, advertiser_type)
    mock_create_orders.create_order.assert_called_once_with(order, 246810,
      14523)
    (mock_create_creatives.create_creative_configs_for_video
      .assert_called_once_with(246810, sizes, 'IN_APP_VIDEO_xyz', constant.SDK_VIDEO_VAST_URL, constant.SDK_VIDEO_DURATION))
    mock_create_creatives.create_creatives.assert_called_once()
    mock_create_creative_sets.create_creative_set_config.assert_called_once_with([54321,98765], sizes, 'IN_APP_VIDEO_xyz' )
    mock_create_creative_sets.create_creative_sets.assert_called_once()
    mock_create_line_items.create_line_items.assert_called_once()
    mock_licas.make_licas.assert_called_once_with([543210, 987650], [54321, 98765], durations=None, setup_type='IN_APP_VIDEO', size_overrides=[], slot=None)



  @patch('tasks.add_new_openwrap_partner.create_line_item_configs')
  @patch('tasks.add_new_openwrap_partner.DFPValueIdGetter')
  @patch('tasks.add_new_openwrap_partner.get_or_create_dfp_targeting_key')
  @patch('dfp.associate_line_items_and_creatives')
  @patch('dfp.create_creatives')
  @patch('dfp.create_line_items')
  @patch('tasks.add_new_openwrap_partner.get_unique_id', return_value = 'NATIVE_xyz')
  @patch('dfp.get_creative_template')
  @patch('dfp.create_orders')
  @patch('dfp.get_advertisers')
  @patch('dfp.get_placements')
  @patch('dfp.get_users')
  def test_setup_partner_for_native(self, mock_get_users, mock_get_placements,
    mock_get_advertisers, mock_create_orders, mock_get_creative_template, mock_get_unique_id,
    mock_create_line_items, mock_create_creatives, mock_licas, mock_dfp_client,
    mock_get_or_create_dfp_targeting_key, mock_dfp_value_id_getter, mock_create_line_item_configs):
    """
    It calls all expected DFP functions.
    """

    mock_get_users.get_user_id_by_email = MagicMock(return_value=14523)
    mock_get_placements.get_placement_ids_by_name = MagicMock(
      return_value=[1234567, 9876543])
    mock_get_advertisers.get_advertiser_id_by_name = MagicMock(
      return_value=246810)
    mock_create_orders.create_order = MagicMock(return_value=1357913)
    mock_get_creative_template.get_creative_template_ids_by_name =  MagicMock(return_value= [123,456])
    mock_create_creatives.create_creatives = MagicMock(return_value = [54321,98765])
    mock_create_line_items.create_line_items = MagicMock(
      return_value =[543210, 987650])

    prices = [{
       'start': 1,
       'end': 2,
       'granularity': 1,
       'rate': 1.5
    }]

    tasks.add_new_openwrap_partner.setup_partner(user_email=email, advertiser_name=advertiser, 
                                               advertiser_type = advertiser_type, order_name=order,
                                               placements=placements, sizes=sizes, lineitem_type = lineitem_type,
                                               lineitem_prefix = 'LI_123', bidder_code=bidder_code, prices=prices,
                                               setup_type = constant.NATIVE, creative_template = None, num_creatives=2,
                                               use_1x1=False, currency_code='USD', custom_targeting= None,
                                               same_adv_exception= False, device_categories=None, device_capabilities=None, 
                                               roadblock_type= 'ONE_OR_MORE', slot = None,adpod_creative_durations=None)

    mock_get_creative_template.get_creative_template_ids_by_name.assert_called_once()
    mock_create_creatives.create_creative_configs_for_native.assert_called_once_with(246810,  [123, 456], 2, 'NATIVE_xyz')
    mock_create_creatives.create_creatives.assert_called_once()
    mock_create_line_items.create_line_items.assert_called_once()
    mock_licas.make_licas.assert_called_once_with([543210, 987650], [54321, 98765], durations=None, setup_type='NATIVE', size_overrides=[], slot=None)


  @patch('tasks.add_new_openwrap_partner.create_line_item_configs')
  @patch('tasks.add_new_openwrap_partner.DFPValueIdGetter')
  @patch('tasks.add_new_openwrap_partner.get_or_create_dfp_targeting_key')
  @patch('dfp.associate_line_items_and_creatives')
  @patch('dfp.create_creatives')
  @patch('dfp.create_line_items')
  @patch('tasks.add_new_openwrap_partner.get_unique_id', return_value = 'NATIVE_xyz')
  @patch('dfp.get_creative_template')
  @patch('dfp.create_orders')
  @patch('dfp.get_advertisers')
  @patch('dfp.get_root_ad_unit_id')
  @patch('dfp.get_users')
  def test_setup_partner_for_RON(self, mock_get_users, mock_get_root_ad_unit_id,
    mock_get_advertisers, mock_create_orders, mock_get_creative_template, mock_get_unique_id,
    mock_create_line_items, mock_create_creatives, mock_licas, mock_dfp_client,
    mock_get_or_create_dfp_targeting_key, mock_dfp_value_id_getter, mock_create_line_item_configs):
    """
    It calls all expected DFP functions.
    """

    mock_get_root_ad_unit_id.get_root_ad_unit_id = MagicMock(return_value=23546)

    prices = [{
       'start': 1,
       'end': 2,
       'granularity': 1,
       'rate': 1.5
    }]


    tasks.add_new_openwrap_partner.setup_partner(user_email=email, advertiser_name=advertiser, 
                                               advertiser_type = advertiser_type, order_name=order,
                                               placements=[], sizes=sizes, lineitem_type = lineitem_type,
                                               lineitem_prefix = 'LI_123', bidder_code=bidder_code, prices=prices,
                                               setup_type = constant.NATIVE, creative_template = None, num_creatives=2,
                                               use_1x1=False, currency_code='USD', custom_targeting= None,
                                               same_adv_exception= False, device_categories=None, device_capabilities=None, 
                                               roadblock_type= 'ONE_OR_MORE', slot = None,adpod_creative_durations=None)
    
    mock_get_root_ad_unit_id.get_root_ad_unit_id.assert_called_once()
    #args, kwargs = mock_create_line_item_configs.call_args
    #self.assertEqual(args[12], None)
   
  
  def test_get_creative_file_for_web_safeframe(self,mock_dfp_client):
    expected_value= tasks.add_new_openwrap_partner.get_creative_file(constant.WEB_SAFEFRAME)
    self.assertEqual(expected_value,"creative_snippet_openwrap_sf.html")

  def test_get_creative_file_for_amp(self,mock_dfp_client):
    expected_value= tasks.add_new_openwrap_partner.get_creative_file(constant.AMP)
    self.assertEqual(expected_value,"creative_snippet_openwrap_amp.html")

  def test_process_price_bucket_sub_granu_0_point_01(self,mock_dfp_client):
    actual=obj.process_price_bucket(1,1.1,0.05)
    self.assertEqual(actual,['1.00', '1.01', '1.02', '1.03', '1.04', '1.05', '1.06', '1.07', '1.08', '1.09'])
  
  def test_process_price_bucket_else_1_case(self,mock_dfp_client):
    actual=obj.process_price_bucket(1,1.05,0.25)
    self.assertEqual(actual,['1.00', '1.01', '1.02', '1.03', '1.04'])
  
  def test_process_price_bucket_else_2_case(self,mock_dfp_client):
    actual=obj.process_price_bucket(0,1.05,0.25)
    self.assertEqual(actual,['0.01', '0.02', '0.03', '0.04', '0.05', '0.06', '0.07', '0.08', '0.09', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.00', '1.01', '1.02', '1.03', '1.04'])

  @patch('dfp.get_custom_targeting')
  def test_create_line_item_configs(self, mock_get_targeting, mock_dfp_client):
    """
    It creates the expected line item configs.
    """
    
    prices = [{
       'start': 1,
       'end': 2,
       'granularity': 1,
       'rate': 1.5
    },
    {
       'start': 2,
       'end': 5,
       'granularity': 1,
       'rate': 3.5
    }]

    configs = tasks.add_new_openwrap_partner.create_line_item_configs(prices= prices, order_id=1234567,
                                                                    placement_ids=[9876543, 1234567], ad_unit_ids=None,
                                                                    bidder_code='iamabiddr', sizes=sizes, key_gen_obj=tasks.add_new_openwrap_partner.OpenWrapTargetingKeyGen(), 
        lineitem_type=lineitem_type, lineitem_prefix = 'abc', 
        currency_code='HUF', custom_targeting = None, setup_type = constant.WEB, creative_template_ids=None)

    self.assertEqual(len(configs), 2)

    self.assertEqual(configs[0]['name'], 'abc_1.50') 
    self.assertEqual(configs[0]['costPerUnit']['microAmount'], 1500000)

    self.assertEqual(configs[1]['name'], 'abc_3.50')
    self.assertEqual(
      configs[1]['targeting']['inventoryTargeting']['targetedPlacementIds'],
      [9876543, 1234567]
    )
    self.assertEqual(configs[1]['orderId'], 1234567)
    self.assertEqual(configs[1]['costPerUnit']['microAmount'], 3500000)
    self.assertEqual(configs[1]['costPerUnit']['currencyCode'], 'HUF')
    self.assertEqual(configs[1]['valueCostPerUnit']['microAmount'], 3500000)
    self.assertEqual(configs[1]['valueCostPerUnit']['currencyCode'], 'HUF')
    self.assertEqual(configs[1]['lineItemType'], lineitem_type)
    self.assertEqual(configs[1]['roadblockingType'], 'ONE_OR_MORE')
    self.assertEqual(configs[1]['disableSameAdvertiserCompetitiveExclusion'], False)

    self.assertEqual(len(configs[1]['creativePlaceholders']), 2)
    self.assertEqual(configs[1]['creativePlaceholders'][0]['size'], sizes[0])
    self.assertEqual(configs[1]['creativePlaceholders'][1]['size'], sizes[1])
  
  @patch('tasks.add_new_openwrap_partner.get_exchange_rate')
  @patch('settings.OPENWRAP_SETUP_TYPE', constant.ADPOD, create=True)
  @patch('dfp.get_network.get_dfp_network')
  def test_Calculate_price_Adpod(self,mock_dfp_client, mock_get_dfp_network,mock_get_exchange_rate):
    input=[{
      'expected': 171,
      'filename': 'Inline_Header_Bidding_Auto.csv'
    },
    {
      'expected': 201,
      'filename': 'Inline_Header_Bidding_CTV-Med.csv'
    },
    {
      'expected': 424,
      'filename': 'Inline_Header_Bidding_Dense.csv'
    },
    {
      'expected': 2000,
      'filename': 'Inline_Header_Bidding_High.csv'
    },
    {
      'expected': 201,
      'filename': 'Inline_Header_Bidding_Med.csv'
    }]

    for inp in input:
      prices = tasks.add_new_openwrap_partner.load_price_csv(inp['filename'],constant.ADPOD)
      self.assertEqual(len(prices),inp['expected'],"Expected and generated line items don't match")
