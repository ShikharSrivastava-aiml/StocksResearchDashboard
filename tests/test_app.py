"""
Black-box tests for the main application flow
"""

import unittest
from unittest.mock import patch, MagicMock
import sys

# Define a placeholder for StopException that can be used by mocks
class StopException(Exception):
    pass

class TestAppFlow(unittest.TestCase):
    """
    Test suite for the main application flow.
    """

    def setUp(self):
        """Set up the test environment by mocking the streamlit module."""
        self.mock_st = MagicMock()
        # Mock the StopException as it's imported within the app
        self.mock_st.runtime.scriptrunner.StopException = StopException
        self.patcher = patch.dict('sys.modules', {'streamlit': self.mock_st})
        self.patcher.start()
        # Reset session state for each test
        self.mock_st.session_state = {}
        self.mock_st.columns.return_value = (MagicMock(), MagicMock(), MagicMock())
        self.mock_st.tabs.return_value = (MagicMock(), MagicMock())
        # Mock the config for the logger to prevent a TypeError
        self.mock_st.config.get_option.return_value = "%(message)s"

    def tearDown(self):
        """Clean up the test environment."""
        self.patcher.stop()

    def test_unauthenticated_user_flow(self):
        """
        Test that an unauthenticated user is shown the login page and the script stops.
        """
        # Patch the functions at their source
        with patch('auth.authentication.show_login_page') as mock_show_login_page, \
             patch('data.symbol_loader.load_symbols_database'):
            import app

            # Arrange
            self.mock_st.stop.side_effect = StopException()
            # check_authentication will use the empty session_state and return False

            # Reset mocks to clear state from initial import
            mock_show_login_page.reset_mock()
            self.mock_st.stop.reset_mock()

            # Act & Assert
            with self.assertRaises(StopException):
                import importlib
                importlib.reload(app)

            mock_show_login_page.assert_called_once()
            self.mock_st.stop.assert_called_once()

    def test_authenticated_user_flow_and_navigation(self):
        """
        Test the main application flow for an authenticated user, including page navigation.
        """
        # Patch the functions at their source
        with patch('pages.stock_analysis.render') as mock_render_stock, \
             patch('utils.service_discovery.get_available_services') as mock_get_services, \
             patch('data.symbol_loader.load_symbols_database'):
            import app

            # Arrange
            self.mock_st.session_state = {'logged_in': True, 'username': 'test_user'}
            # check_authentication will use this session_state and return True

            mock_get_services.return_value = {"Stock Analysis Service": {}}
            self.mock_st.sidebar.selectbox.return_value = "Stock Analysis Service"

            # Reset mocks to clear state from initial import
            mock_get_services.reset_mock()
            mock_render_stock.reset_mock()

            # Act
            import importlib
            importlib.reload(app)

            # Assert
            self.mock_st.sidebar.title.assert_called_with("👤 Welcome, test_user")
            mock_get_services.assert_called_once()
            mock_render_stock.assert_called_once()

if __name__ == '__main__':
    unittest.main()
