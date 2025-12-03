"""
Unit tests for the services module
"""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from services.stock_analysis.stock_analysis_service import app

class TestStockAnalysisService(unittest.TestCase):
    """
    Test suite for the stock analysis service.
    """

    def setUp(self):
        self.client = TestClient(app)

    @patch('services.stock_analysis.stock_analysis_service.api_client')
    def test_get_analysis_success(self, mock_api_client):
        """
        Test the /analysis/{symbol} endpoint for a successful response.
        """
        mock_api_client.get_company_overview.return_value = {"Symbol": "AAPL"}
        mock_api_client.get_daily_prices.return_value = {"Time Series (Daily)": {}}

        response = self.client.get("/analysis/AAPL")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['symbol'], "AAPL")
        self.assertIn("overview", data)
        self.assertIn("daily", data)

    @patch('services.stock_analysis.stock_analysis_service.api_client')
    def test_get_analysis_not_found(self, mock_api_client):
        """
        Test the /analysis/{symbol} endpoint for a 404 response.
        """
        mock_api_client.get_company_overview.return_value = {}
        mock_api_client.get_daily_prices.return_value = {}

        response = self.client.get("/analysis/UNKNOWN")
        self.assertEqual(response.status_code, 404)

    @patch('services.stock_analysis.stock_analysis_service.api_client')
    def test_get_analysis_api_error(self, mock_api_client):
        """
        Test the /analysis/{symbol} endpoint for a 500 response when the API fails.
        """
        mock_api_client.get_company_overview.side_effect = Exception("API Error")

        response = self.client.get("/analysis/AAPL")
        self.assertEqual(response.status_code, 500)

    @patch('services.stock_analysis.stock_analysis_service.requests.post')
    def test_register_service_with_registry(self, mock_post):
        """
        Test that the service registration is called on startup.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with TestClient(app) as client:
            # The startup event is triggered when the TestClient is created
            pass

        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()
