"""
Alpha Vantage API Client
Wrapper for all API calls
"""

import requests
import json
import streamlit as st
from typing import Optional, Dict, Any
from pathlib import Path


class APIClient:
    """Alpha Vantage API client."""

    def __init__(self, config_file: str = "config.json"):
        self.base_url = "https://www.alphavantage.co/query"
        self.api_key = self._load_api_key(config_file)

    def _load_api_key(self, config_file: str) -> str:
        """Load API key from config file."""
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            api_key = config.get("api_key", "").strip()
            if not api_key:
                raise ValueError("API key is empty")
            return api_key
        except FileNotFoundError:
            raise FileNotFoundError(f"{config_file} not found")
        except Exception as e:
            raise Exception(f"Error loading API key: {e}")

    def _make_request(self, params: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Make API request with error handling."""
        params['apikey'] = self.api_key

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if "Note" in data:
                st.warning("⚠️ API rate limit reached. Try again in a minute.")
                return None

            if "Error Message" in data:
                st.error(f"❌ API error: {data['Error Message']}")
                return None

            return data

        except requests.exceptions.RequestException as e:
            st.error(f"🌐 Network error: {e}")
            return None
        except json.JSONDecodeError:
            st.error("⚠️ Failed to parse API response (invalid JSON).")
            return None

    def get_company_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company overview data."""
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }
        return self._make_request(params)

    def get_daily_prices(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get daily price data."""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol
        }
        return self._make_request(params)

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote."""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol
        }
        return self._make_request(params)

    def get_earnings(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get earnings data."""
        params = {
            'function': 'EARNINGS',
            'symbol': symbol
        }
        return self._make_request(params)

    def get_earnings_transcript(self, symbol: str, quarter: str) -> Optional[Dict[str, Any]]:
        """Get earnings call transcript."""
        params = {
            'function': 'EARNINGS_CALL_TRANSCRIPT',
            'symbol': symbol,
            'quarter': quarter
        }
        return self._make_request(params)

    def get_news_sentiment(self, topics: Optional[str] = None,
                           tickers: Optional[str] = None,
                           sort: str = 'LATEST',
                           limit: int = 20) -> Optional[Dict[str, Any]]:
        """Get news sentiment data."""
        params = {
            'function': 'NEWS_SENTIMENT',
            'sort': sort,
            'limit': str(limit)
        }

        if topics:
            params['topics'] = topics
        if tickers:
            params['tickers'] = tickers

        return self._make_request(params)