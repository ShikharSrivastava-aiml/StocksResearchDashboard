"""
Subsystem tests for the pages
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from pages import stock_analysis

class TestStockAnalysisPage(unittest.TestCase):
    """
    Test suite for the stock analysis page.
    """

    @patch('pages.stock_analysis.display_company_header')
    @patch('pages.stock_analysis.display_key_metrics')
    @patch('pages.stock_analysis.st')
    @patch('pages.stock_analysis.requests.get')
    @patch('pages.stock_analysis.get_service_url')
    @patch('pages.stock_analysis.stock_input_with_suggestions')
    def test_render_successful_analysis(self, mock_stock_input, mock_get_service_url, mock_requests_get, mock_st, mock_display_key_metrics, mock_display_company_header):
        """
        Test the render function for a successful stock analysis.
        """
        # Arrange
        mock_st.columns.side_effect = [
            (MagicMock(), MagicMock()),
            (MagicMock(), MagicMock(), MagicMock())
        ]
        mock_st.button.return_value = True

        session_state = {}

        def get_item(key, default=None):
            return session_state.get(key, default)

        def set_item(key, value):
            session_state[key] = value

        mock_st.session_state.get.side_effect = get_item
        mock_st.session_state.__setitem__.side_effect = set_item
        mock_st.session_state.__contains__.side_effect = session_state.__contains__


        mock_stock_input.return_value = "AAPL"
        mock_get_service_url.return_value = "http://test_service"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "AAPL",
            "overview": {"Symbol": "AAPL", "52WeekHigh": "200", "52WeekLow": "100"},
            "daily": {
                "Time Series (Daily)": {
                    "2023-01-01": {"4. close": "150.00"},
                    "2023-01-02": {"4. close": "152.00"}
                }
            }
        }
        mock_requests_get.return_value = mock_response

        # Act
        stock_analysis.render(pd.DataFrame())

        # Assert
        mock_st.spinner.assert_called_with("Analyzing AAPL...")
        mock_requests_get.assert_called_with("http://test_service/analysis/AAPL")
        self.assertIn('analysis_data', session_state)
        self.assertEqual(session_state['analysis_data']['symbol'], "AAPL")
        mock_st.success.assert_called_with("✅ Analysis complete for AAPL")

    @patch('pages.stock_analysis.st')
    @patch('pages.stock_analysis.requests.get')
    @patch('pages.stock_analysis.get_service_url')
    @patch('pages.stock_analysis.stock_input_with_suggestions')
    def test_render_failed_analysis(self, mock_stock_input, mock_get_service_url, mock_requests_get, mock_st):
        """
        Test the render function for a failed stock analysis.
        """
        # Arrange
        mock_st.columns.return_value = (MagicMock(), MagicMock())
        mock_st.button.return_value = True
        mock_st.session_state = {}
        mock_stock_input.return_value = "FAIL"
        mock_get_service_url.return_value = "http://test_service"

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Service Error"
        mock_requests_get.return_value = mock_response

        # Act
        stock_analysis.render(pd.DataFrame())

        # Assert
        mock_st.spinner.assert_called_with("Analyzing FAIL...")
        mock_st.error.assert_called_with("Failed to analyze FAIL: Service Error")

    @patch('pages.stock_analysis.st')
    @patch('pages.stock_analysis.stock_input_with_suggestions')
    def test_render_no_symbol(self, mock_stock_input, mock_st):
        """
        Test the render function when no symbol is entered.
        """
        # Arrange
        mock_st.columns.return_value = (MagicMock(), MagicMock())
        mock_st.button.return_value = True
        mock_st.session_state = {}
        mock_stock_input.return_value = ""

        # Act
        stock_analysis.render(pd.DataFrame())

        # Assert
        mock_st.warning.assert_called_with("Please enter a stock symbol.")

if __name__ == '__main__':
    unittest.main()
