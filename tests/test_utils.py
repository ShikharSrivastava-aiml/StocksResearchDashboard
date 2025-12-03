"""
Unit tests for the utils module
"""

import unittest
from unittest.mock import patch
from utils.helpers import (
    format_currency, format_percentage, format_large_number,
    infer_quarter, format_date, get_sentiment_color,
    get_sentiment_emoji, get_sentiment_label
)
from utils.service_discovery import get_available_services, get_service_url, deregister_service

class TestHelpers(unittest.TestCase):
    """
    Test suite for the helper functions.
    """

    def test_format_currency(self):
        self.assertEqual(format_currency(1234.56), "$1,234.56")
        self.assertEqual(format_currency(1234.567, decimals=3), "$1,234.567")

    def test_format_percentage(self):
        self.assertEqual(format_percentage(85.25), "85.25%")
        self.assertEqual(format_percentage(85.257, decimals=3), "85.257%")

    def test_format_large_number(self):
        self.assertEqual(format_large_number(1234567890), "$1.23B")
        self.assertEqual(format_large_number(1234567), "$1.23M")
        self.assertEqual(format_large_number(1234), "$1.23K")
        self.assertEqual(format_large_number(123), "$123.00")

    def test_infer_quarter(self):
        self.assertEqual(infer_quarter("2023-03-31"), "Q1")
        self.assertEqual(infer_quarter("2023-06-30"), "Q2")
        self.assertEqual(infer_quarter("2023-09-30"), "Q3")
        self.assertEqual(infer_quarter("2023-12-31"), "Q4")
        self.assertEqual(infer_quarter(""), "Q?")

    def test_format_date(self):
        self.assertEqual(format_date("2023-10-26T10:00:00"), "2023-10-26")
        self.assertEqual(format_date("invalid-date"), "invalid-date")

    def test_get_sentiment_color(self):
        self.assertEqual(get_sentiment_color(0.5), "green")
        self.assertEqual(get_sentiment_color(-0.5), "red")
        self.assertEqual(get_sentiment_color(0), "gray")

    def test_get_sentiment_emoji(self):
        self.assertEqual(get_sentiment_emoji(0.5), "😊")
        self.assertEqual(get_sentiment_emoji(-0.5), "😟")
        self.assertEqual(get_sentiment_emoji(0), "😐")

    def test_get_sentiment_label(self):
        self.assertEqual(get_sentiment_label(0.5), "Positive 📈")
        self.assertEqual(get_sentiment_label(-0.5), "Negative 📉")
        self.assertEqual(get_sentiment_label(0), "Neutral ➡️")

class TestServiceDiscovery(unittest.TestCase):
    """
    Test suite for the service discovery functions.
    """

    @patch('utils.service_discovery.requests.get')
    def test_get_available_services_success(self, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "service_one": {},
            "service_two": {}
        }
        mock_get.return_value = mock_response

        services = get_available_services()
        self.assertEqual(len(services), 2)
        self.assertIn("Service One", services)

    @patch('utils.service_discovery.requests.get')
    def test_get_available_services_failure(self, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        services = get_available_services()
        self.assertEqual(services, {})

    @patch('utils.service_discovery.requests.get')
    def test_get_service_url_success(self, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"service_url": "http://test.com"}
        mock_get.return_value = mock_response

        url = get_service_url("test_service")
        self.assertEqual(url, "http://test.com")

    @patch('utils.service_discovery.requests.get')
    def test_get_service_url_failure(self, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(Exception):
            get_service_url("unknown_service")

    @patch('utils.service_discovery.requests.delete')
    def test_deregister_service_success(self, mock_delete):
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response

        try:
            deregister_service("Test Service")
        except Exception as e:
            self.fail(f"deregister_service raised an exception unexpectedly: {e}")

    @patch('utils.service_discovery.requests.delete')
    def test_deregister_service_failure(self, mock_delete):
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 500
        mock_delete.return_value = mock_response

        with self.assertRaises(Exception):
            deregister_service("failing_service")

if __name__ == '__main__':
    unittest.main()
