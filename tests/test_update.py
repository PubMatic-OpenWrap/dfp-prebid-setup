import unittest
from unittest.mock import MagicMock
from unittest.mock import patch, call
from tasks.update import *
from io import StringIO

class TestBaseSettingUpdater(unittest.TestCase):
    """
    Unit tests for the BaseSettingUpdater class.
    This test suite covers the functionality of the BaseSettingUpdater class,
    """
    def setUp(self):
        self.logger = MagicMock()
        self.color = MagicMock()
        self.ad_manager_client = MagicMock()
        self.setting_class = MagicMock()

    def test_confirm_inputs_raises_not_implemented_error(self):
        updater = BaseSettingUpdater(self.logger, self.color, self.ad_manager_client, self.setting_class)
        with self.assertRaises(NotImplementedError):
            updater.confirm_inputs()

    def test_update_raises_not_implemented_error(self):
        updater = BaseSettingUpdater(self.logger, self.color, self.ad_manager_client, self.setting_class)
        with self.assertRaises(NotImplementedError):
            updater.update()

class TestVideoPositionUpdater(unittest.TestCase):
    """
    Unit tests for the VideoPositionUpdater class.
    This test suite covers the functionality of the VideoPositionUpdater class,
    ensuring that it correctly updates the "Video Position Targeting" of line items.
    """
    @patch('builtins.input', return_value='n')
    def test_confirm_inputs_user_selects_n(self, _):
        # setup and create class object
        updater = VideoPositionUpdater(logger=MagicMock(), color=Color(), ad_manager_client=MagicMock(), setting_class=MagicMock())
        updater.setting_class.DFP_ORDER_NAME = 'test_order'
        updater.setting_class.LINE_ITEM_NAME_REGEX = '%'
        updater.setting_class.DFP_LINEITEM_TYPE = 'PRICE_PRIORITY'
        updater.setting_class.NEW_VIDEO_POSITION = 'INVALID'

        result = updater.confirm_inputs()

        self.assertFalse(result)
        updater.logger.info.assert_called()
        assert updater.logger.info.call_count == 2

    @patch('builtins.input', return_value='y')
    def test_confirm_inputs_user_selects_y(self, _):
        # setup and create class object
        updater = VideoPositionUpdater(logger=MagicMock(), color=Color(), ad_manager_client=MagicMock(), setting_class=MagicMock())
        updater.setting_class.DFP_ORDER_NAME = 'test_order'
        updater.setting_class.LINE_ITEM_NAME_REGEX = '%'
        updater.setting_class.DFP_LINEITEM_TYPE = 'PRICE_PRIORITY'
        updater.setting_class.NEW_VIDEO_POSITION = 'MIDROLL'

        result = updater.confirm_inputs()

        self.assertTrue(result)
        updater.logger.info.assert_called()
        assert updater.logger.info.call_count == 1

    @patch('builtins.input', return_value='y')
    def test_confirm_inputs_incorrect_video_position(self, _):
        # setup and create class object
        updater = VideoPositionUpdater(logger=MagicMock(), color=Color(), ad_manager_client=MagicMock(), setting_class=MagicMock())
        updater.setting_class.DFP_ORDER_NAME = 'test_order'
        updater.setting_class.LINE_ITEM_NAME_REGEX = '%'
        updater.setting_class.DFP_LINEITEM_TYPE = 'PRICE_PRIORITY'
        updater.setting_class.NEW_VIDEO_POSITION = 'INVALID'

        result = updater.confirm_inputs()

        self.assertFalse(result)
        updater.logger.info.assert_called()
        assert updater.logger.info.call_count == 2

    @patch('tasks.update.ad_manager.AdManagerClient')
    @patch('tasks.update.ad_manager.StatementBuilder')
    def test_get_line_items(self, mock_ad_manager_client, mock_statement_builder):
        # setup and create class object
        expected_result = {'results': [{'name': 'line_item_1'}, {'name': 'line_item_2'}]}
        mock_line_item_service = MagicMock()
        mock_line_item_service = mock_ad_manager_client.GetService.return_value
        mock_line_item_service.getLineItemsByStatement.return_value = expected_result

        updater = VideoPositionUpdater(logger=MagicMock(), color=MagicMock(), ad_manager_client=mock_ad_manager_client, setting_class=MagicMock())

        result = updater.get_line_items()
        self.assertEqual(result, expected_result)

    def test_print_skipped_line_items(self):
        # setup and create class object
        mock_logger = MagicMock()
        updater = VideoPositionUpdater(logger=mock_logger, color=MagicMock(), ad_manager_client=MagicMock(), setting_class=MagicMock())

        updater.print_skipped_line_items({})
        updater.logger.info.assert_not_called()

        updater.print_skipped_line_items({'line_item_1': 'reason_1', 'line_item_2': 'reason_2'})
        updater.logger.info.assert_called()
        assert updater.logger.info.call_count == 2

    def test_print_line_items_with_current_position(self):
        # setup and create class object
        mock_logger = MagicMock()
        updater = VideoPositionUpdater(logger=mock_logger, color=MagicMock(), ad_manager_client=MagicMock(), setting_class=MagicMock())

        updater.print_line_items_with_current_position({})
        updater.logger.info.assert_not_called()

        updater.print_line_items_with_current_position({'line_item_1': 'PREROLL', 'line_item_2': 'POSTROLL'})
        updater.logger.info.assert_called()
        assert updater.logger.info.call_count == 2

    def test_select_line_items_to_update_found_empty_list(self):
        line_items = []
        updater = VideoPositionUpdater(logger=MagicMock(), color=MagicMock(), ad_manager_client=MagicMock(), setting_class=MagicMock())
        updater.setting_class.NEW_VIDEO_POSITION = 'POSTROLL'

        updated_line_items, line_items_with_current_position, skip_line_items = updater.select_line_items_to_update(line_items)

        self.assertEqual(len(updated_line_items), 0)
        self.assertEqual(len(line_items_with_current_position), 0)
        self.assertEqual(len(skip_line_items), 0)

    def test_select_line_items_to_update_when_videoPositionTargeting_is_absent(self):
        line_items = [
            {
                'name': 'line_item_1',
                'targeting': {}
            }
        ]
        expected_updated_line_items = [
            {
                'name': 'line_item_1',
                'targeting': {'videoPositionTargeting': {'targetedPositions': [{'videoPosition': {'positionType': 'POSTROLL'}}]}}
            }
        ]
        expected_line_item_with_curr_pos = { 'line_item_1': None }
        expected_skip_line_items = {}

        updater = VideoPositionUpdater(logger=MagicMock(), color=MagicMock(), ad_manager_client=MagicMock(), setting_class=MagicMock())
        updater.setting_class.NEW_VIDEO_POSITION = 'POSTROLL'

        updated_line_items, line_items_with_current_position, skip_line_items = updater.select_line_items_to_update(line_items)

        self.assertEqual(updated_line_items, expected_updated_line_items)
        self.assertEqual(line_items_with_current_position, expected_line_item_with_curr_pos)
        self.assertEqual(skip_line_items, expected_skip_line_items)

    def test_select_line_items_to_update_when_targetedPositions_is_absent(self):
        line_items = [
            {
                'name': 'line_item_1',
                'targeting': {'videoPositionTargeting': {}}
            }
        ]
        expected_updated_line_items = [
            {
                'name': 'line_item_1',
                'targeting': {'videoPositionTargeting': {'targetedPositions': [{'videoPosition': {'positionType': 'POSTROLL'}}]}}
            }
        ]
        expected_line_item_with_curr_pos = { 'line_item_1': None }
        expected_skip_line_items = {}

        updater = VideoPositionUpdater(logger=MagicMock(), color=MagicMock(), ad_manager_client=MagicMock(), setting_class=MagicMock())
        updater.setting_class.NEW_VIDEO_POSITION = 'POSTROLL'

        updated_line_items, line_items_with_current_position, skip_line_items = updater.select_line_items_to_update(line_items)

        self.assertEqual(updated_line_items, expected_updated_line_items)
        self.assertEqual(line_items_with_current_position, expected_line_item_with_curr_pos)
        self.assertEqual(skip_line_items, expected_skip_line_items)

    def test_select_line_items_to_update_when_videoPosition_is_absent(self):
        line_items = [
            {
                'name': 'line_item_1',
                'targeting': {'videoPositionTargeting': {'targetedPositions': []}}
            }
        ]
        expected_updated_line_items = [
            {
                'name': 'line_item_1',
                'targeting': {'videoPositionTargeting': {'targetedPositions': [{'videoPosition': {'positionType': 'POSTROLL'}}]}}
            }
        ]
        expected_line_item_with_curr_pos = { 'line_item_1': None }
        expected_skip_line_items = {}

        updater = VideoPositionUpdater(logger=MagicMock(), color=MagicMock(), ad_manager_client=MagicMock(), setting_class=MagicMock())
        updater.setting_class.NEW_VIDEO_POSITION = 'POSTROLL'

        updated_line_items, line_items_with_current_position, skip_line_items = updater.select_line_items_to_update(line_items)

        self.assertEqual(updated_line_items, expected_updated_line_items)
        self.assertEqual(line_items_with_current_position, expected_line_item_with_curr_pos)
        self.assertEqual(skip_line_items, expected_skip_line_items)

    def test_select_line_items_to_update_when_videoPosition_is_already_targeted(self):
        line_items = [
            {
                'name': 'line_item_1',
                'targeting': {'videoPositionTargeting': {'targetedPositions': [{'videoPosition': {'positionType': 'POSTROLL'}}]}}
            }
        ]
        expected_updated_line_items = []
        expected_line_item_with_curr_pos = {}
        expected_skip_line_items = {
            'line_item_1': 'attempt to target same video position multiple time',
        }

        updater = VideoPositionUpdater(logger=MagicMock(), color=MagicMock(), ad_manager_client=MagicMock(), setting_class=MagicMock())
        updater.setting_class.NEW_VIDEO_POSITION = 'POSTROLL'

        updated_line_items, line_items_with_current_position, skip_line_items = updater.select_line_items_to_update(line_items)

        self.assertEqual(updated_line_items, expected_updated_line_items)
        self.assertEqual(line_items_with_current_position, expected_line_item_with_curr_pos)
        self.assertEqual(skip_line_items, expected_skip_line_items)

    def test_select_line_items_to_update_when_multiple_videoPosition_are_targeted(self):
        line_items = [
            {
                'name': 'line_item_1',
                'targeting': {'videoPositionTargeting': {'targetedPositions': [{'videoPosition': {'positionType': 'POSTROLL'}},{'videoPosition': {'positionType': 'PREROLL'}}]}}
            }
        ]
        expected_updated_line_items = []
        expected_line_item_with_curr_pos = {}
        expected_skip_line_items = {
            'line_item_1': "multiple video positions found, expecting only one position to update",
        }

        updater = VideoPositionUpdater(logger=MagicMock(), color=MagicMock(), ad_manager_client=MagicMock(), setting_class=MagicMock())
        updater.setting_class.NEW_VIDEO_POSITION = 'MIDROLL'

        updated_line_items, line_items_with_current_position, skip_line_items = updater.select_line_items_to_update(line_items)

        self.assertEqual(updated_line_items, expected_updated_line_items)
        self.assertEqual(line_items_with_current_position, expected_line_item_with_curr_pos)
        self.assertEqual(skip_line_items, expected_skip_line_items)

    def test_select_line_items_to_update_for_multiple_line_items_passed_as_input(self):
        line_items = [
            {
                'name': 'line_item_1',
                'targeting': {'videoPositionTargeting': {'targetedPositions': []}}
            },
            {
                'name': 'line_item_2',
                'targeting': {'videoPositionTargeting': {'targetedPositions': [{'videoPosition': {'positionType': 'MIDROLL'}}]}}
            },
            {
                'name': 'line_item_3',
                'targeting': {'videoPositionTargeting': {'targetedPositions': [{'videoPosition': {'positionType': 'POSTROLL'}}]}}
            }
        ]
        expected_updated_line_items = [
            {
                'name': 'line_item_1',
                'targeting': {'videoPositionTargeting': {'targetedPositions': [{'videoPosition': {'positionType': 'POSTROLL'}}]}}
            },
            {
                'name': 'line_item_2',
                'targeting': {'videoPositionTargeting': {'targetedPositions': [{'videoPosition': {'positionType': 'POSTROLL'}}]}}
            },
        ]
        expected_line_item_with_curr_pos = {
            'line_item_1': None,
            'line_item_2': "MIDROLL"
        }
        expected_skip_line_items = {
            'line_item_3': "attempt to target same video position multiple time"
        }

        updater = VideoPositionUpdater(logger=MagicMock(), color=MagicMock(), ad_manager_client=MagicMock(), setting_class=MagicMock())
        updater.setting_class.NEW_VIDEO_POSITION = 'POSTROLL'

        updated_line_items, line_items_with_current_position, skip_line_items = updater.select_line_items_to_update(line_items)

        self.assertEqual(updated_line_items, expected_updated_line_items)
        self.assertEqual(line_items_with_current_position, expected_line_item_with_curr_pos)
        self.assertEqual(skip_line_items, expected_skip_line_items)

    @patch('tasks.update.ad_manager.AdManagerClient')
    def test_update_when_no_line_items_returned_by_GAM(self, mock_ad_manager_client):
        mock_logger = MagicMock()
        updater = VideoPositionUpdater(logger=mock_logger, color=MagicMock(), ad_manager_client=mock_ad_manager_client, setting_class=MagicMock())

        # Mock the get_line_items method to return a response with line items
        with patch.object(updater, 'get_line_items', return_value={}):
            updater.update()

        mock_logger.info.assert_called_once_with("No line item found for given input")

    @patch('tasks.update.ad_manager.AdManagerClient')
    def test_update_when_no_line_items_found_to_update(self, mock_ad_manager_client):
        mock_logger = MagicMock()
        updater = VideoPositionUpdater(logger=mock_logger, color=MagicMock(), ad_manager_client=mock_ad_manager_client, setting_class=MagicMock())

        # Mock the get_line_items method to return a response with line items
        with patch.object(updater, 'get_line_items', return_value={'results': [{'name': 'line_item_1'}]}):
            with patch.object(updater, 'select_line_items_to_update', return_value=([], {}, {})):
                updater.update()

        mock_logger.info.assert_not_called()
        mock_ad_manager_client.GetService.assert_not_called()


    @patch('builtins.input', return_value='n')
    @patch('tasks.update.ad_manager.AdManagerClient')
    def test_update_when_user_dont_want_to_proceed(self, mock_ad_manager_client,mock_input):
        mock_logger = MagicMock()
        updater = VideoPositionUpdater(logger=mock_logger, color=MagicMock(), ad_manager_client=mock_ad_manager_client, setting_class=MagicMock())

        # Mock the get_line_items method to return a response with line items
        with patch.object(updater, 'get_line_items', return_value={'results': [{'name': 'line_item_1'}]}):
            with patch.object(updater, 'select_line_items_to_update', return_value=([{'name': 'line_item_1'}], {}, {})):
                updater.update()

        mock_logger.info.assert_called_once_with("Update canceled.")
        mock_ad_manager_client.GetService.assert_not_called()

    @patch('builtins.input', return_value='y')
    @patch('tasks.update.ad_manager.AdManagerClient')
    def test_update_after_user_confirmation(self, mock_ad_manager_client,mock_input):
        mock_logger = MagicMock()
        expected_result = [{'name': 'line_item_1'}]
        mock_line_item_service = MagicMock()
        mock_line_item_service = mock_ad_manager_client.GetService.return_value
        mock_line_item_service.updateLineItems.return_value = expected_result

        updater = VideoPositionUpdater(logger=mock_logger(), color=MagicMock(), ad_manager_client=mock_ad_manager_client, setting_class=MagicMock())

        # Mock the get_line_items method to return a response with line items
        with patch.object(updater, 'get_line_items', return_value={'results': [{'name': 'line_item_1'}]}):
            with patch.object(updater, 'select_line_items_to_update', return_value=([{'name': 'line_item_1'}], {}, {})):
                updater.update()

        mock_ad_manager_client.GetService.assert_called()
        updater.logger.info.assert_called()
        assert updater.logger.info.call_count == 2

class TestMainFunction(unittest.TestCase):
    """
    Unit tests for the main function.
    This test suite covers the functionality of the main function.
    """

    @patch('builtins.print')
    @patch('tasks.update.sys.argv', ['program_name'])
    def test_main_when_command_line_arg_is_absent(self,mock_print):
        main()
        expected_print_calls = [
            call("Usage: python -m tasks.update [VideoPosition]"),
            call("Example: python -m tasks.update VideoPosition")
        ]
        mock_print.assert_has_calls(expected_print_calls, any_order=True)

    @patch('tasks.update.VideoPositionUpdater')
    @patch('tasks.update.sys.argv', ['program_name', "videoposition"])
    def test_main_when_command_line_arg_is_correct(self,mock_updater):
        main()

        mock_updater.assert_called_once()
        mock_updater.return_value.confirm_inputs.assert_called_once()
        mock_updater.return_value.update.assert_called_once()

    @patch('builtins.print')
    @patch('tasks.update.sys.argv', ['program_name', "invalid"])
    def test_main_when_command_line_arg_is_incorrect_choice(self,mock_print):
        main()
        expected_print_calls = [
            call("Invalid setting class."),
        ]
        mock_print.assert_has_calls(expected_print_calls, any_order=True)

    @patch('tasks.update.VideoPositionUpdater')
    @patch('tasks.update.sys.argv', ['program_name', "videoposition"])
    def test_main_when_confirm_inputs_returns_false(self,mock_updater):
        mock_updater.return_value.confirm_inputs.return_value = False
        main()
        mock_updater.assert_called_once()
        mock_updater.return_value.update.assert_not_called()

    @patch('tasks.update.VideoPositionUpdater')
    @patch('tasks.update.sys.argv', ['program_name', 'VideoPosition'])
    def test_main_catch_exception(self, mock_updater):
        # Set up the mock to raise an exception
        mock_instance = mock_updater.return_value
        mock_instance.confirm_inputs.side_effect = Exception("Test Exception")

        # Capture the standard output
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            main()
        except Exception as e:
            self.assertEqual(str(e), "Test Exception")

        # Reset the standard output
        sys.stdout = sys.__stdout__

        captured_output_str = captured_output.getvalue()
        self.assertIn("Fatal Error: Test Exception", captured_output_str)

if __name__ == '__main__':
    unittest.main()