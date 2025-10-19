"""
User Data Model
Handles user data operations
"""

from auth.authentication import load_users, save_users
from typing import Optional, Dict, List, Any


class User:
    """User data model and operations."""

    def __init__(self, username: str):
        self.username = username
        self._data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Load user data from storage."""
        users = load_users()
        return users.get(self.username, {})

    def save(self) -> bool:
        """Save user data to storage."""
        users = load_users()
        if self.username in users:
            users[self.username].update(self._data)
            save_users(users)
            return True
        return False

    def get_data(self) -> Dict[str, Any]:
        """Get all user data."""
        return self._data

    def update_data(self, data: Dict[str, Any]) -> bool:
        """Update user data."""
        self._data.update(data)
        return self.save()

    def get_created_at(self) -> str:
        """Get account creation date."""
        return self._data.get('created_at', 'Unknown')

    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences."""
        return self._data.get('preferences', {})

    def update_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Update user preferences."""
        self._data['preferences'] = preferences
        return self.save()

    def change_password(self, new_password_hash: str) -> bool:
        """Change user password."""
        self._data['password'] = new_password_hash
        return self.save()

    @staticmethod
    def delete_user(username: str) -> bool:
        """Delete a user account."""
        users = load_users()
        if username in users:
            del users[username]
            save_users(users)
            return True
        return False