"""
Portfolio Data Model
Handles portfolio operations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from models.user import User


class Portfolio:
    """Portfolio data model and operations."""

    def __init__(self, username: str):
        self.username = username
        self.user = User(username)
        self._portfolio = self._load_portfolio()

    def _load_portfolio(self) -> List[Dict[str, Any]]:
        """Load portfolio from user data."""
        user_data = self.user.get_data()
        return user_data.get('portfolio', [])

    def save(self) -> bool:
        """Save portfolio to user data."""
        user_data = self.user.get_data()
        user_data['portfolio'] = self._portfolio
        return self.user.update_data(user_data)

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all portfolio positions."""
        return self._portfolio

    def add_position(self, symbol: str, shares: int, purchase_price: float,
                     purchase_date: Optional[str] = None) -> bool:
        """Add a new position to portfolio."""
        if purchase_date is None:
            purchase_date = datetime.now().strftime('%Y-%m-%d')

        position = {
            'symbol': symbol.upper(),
            'shares': shares,
            'purchase_price': purchase_price,
            'date_added': purchase_date
        }

        self._portfolio.append(position)
        return self.save()

    def remove_position(self, symbol: str) -> bool:
        """Remove a position from portfolio."""
        self._portfolio = [p for p in self._portfolio if p['symbol'] != symbol.upper()]
        return self.save()

    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get a specific position."""
        for position in self._portfolio:
            if position['symbol'] == symbol.upper():
                return position
        return None

    def update_position(self, symbol: str, **kwargs) -> bool:
        """Update a position."""
        for position in self._portfolio:
            if position['symbol'] == symbol.upper():
                position.update(kwargs)
                return self.save()
        return False

    def clear(self) -> bool:
        """Clear all positions."""
        self._portfolio = []
        return self.save()

    def get_symbols(self) -> List[str]:
        """Get list of all symbols in portfolio."""
        return [p['symbol'] for p in self._portfolio]

    def get_total_positions(self) -> int:
        """Get total number of positions."""
        return len(self._portfolio)

    def get_total_shares(self) -> int:
        """Get total number of shares across all positions."""
        return sum(p['shares'] for p in self._portfolio)