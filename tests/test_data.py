"""
Unit tests for the data module
"""

import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from data.symbol_loader import load_symbols_database, get_stock_suggestions

class TestSymbolLoader(unittest.TestCase):
    """
    Test suite for the symbol loader functions.
    """

    def test_load_symbols_database_success(self):
        """
        Test that the symbols database is loaded successfully.
        """
        # Call the function
        with patch('streamlit.warning') as mock_warning:
            df = load_symbols_database(csv_path='tests/data/dummy_symbols.csv')
            self.assertIsInstance(df, pd.DataFrame)
            self.assertFalse(df.empty)
            self.assertIn('SearchText', df.columns)
            self.assertEqual(df['SearchText'][0], 'AAPL - Apple Inc.')
            mock_warning.assert_not_called()

    def test_load_symbols_database_file_not_found(self):
        """
        Test that a warning is issued if the CSV file is not found.
        """
        with patch('streamlit.warning') as mock_warning:
            df = load_symbols_database(csv_path='non_existent.csv')
            self.assertTrue(df.empty)
            mock_warning.assert_called_once()

    def test_load_symbols_database_no_symbol_column(self):
        """
        Test that an error is raised if the 'Symbol' column is missing.
        """
        with patch('streamlit.error') as mock_error:
            df = load_symbols_database(csv_path='tests/data/no_symbol_column.csv')
            self.assertTrue(df.empty)
            mock_error.assert_called_once()

    def test_get_stock_suggestions_empty_input(self):
        """
        Test that an empty list is returned for empty input.
        """
        dummy_df = pd.DataFrame({'Symbol': ['AAPL'], 'SearchText': ['AAPL - Apple Inc.']})
        suggestions = get_stock_suggestions(dummy_df, '')
        self.assertEqual(suggestions, [])

    def test_get_stock_suggestions_valid_input(self):
        """
        Test that correct suggestions are returned for valid input.
        """
        dummy_df = pd.DataFrame({
            'Symbol': ['AAPL', 'GOOG', 'MSFT'],
            'SearchText': ['AAPL - Apple Inc.', 'GOOG - Alphabet Inc.', 'MSFT - Microsoft Corp.']
        })
        suggestions = get_stock_suggestions(dummy_df, 'AAP')
        self.assertEqual(suggestions, ['AAPL - Apple Inc.'])

    def test_get_stock_suggestions_limit(self):
        """
        Test that the number of suggestions is limited.
        """
        dummy_df = pd.DataFrame({
            'Symbol': [f'A{i}' for i in range(20)],
            'SearchText': [f'A{i} - Company {i}' for i in range(20)]
        })
        suggestions = get_stock_suggestions(dummy_df, 'A', limit=5)
        self.assertEqual(len(suggestions), 5)

if __name__ == '__main__':
    unittest.main()
