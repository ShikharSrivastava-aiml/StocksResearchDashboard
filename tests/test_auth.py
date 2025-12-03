"""
Unit tests for the auth module
"""

import unittest
from unittest.mock import patch, MagicMock
from auth.authentication import (
    hash_password, load_users, save_users,
    create_user, authenticate_user, check_authentication, logout
)

class TestAuthentication(unittest.TestCase):
    """
    Test suite for the authentication functions.
    """

    def test_hash_password(self):
        """
        Test that the password hashing function works correctly.
        """
        self.assertIsNotNone(hash_password("password123"))
        self.assertIsInstance(hash_password("password123"), str)

    @patch('auth.authentication.os.path.exists')
    @patch('builtins.open')
    @patch('auth.authentication.pickle.load')
    def test_load_users(self, mock_pickle_load, mock_open, mock_exists):
        """
        Test loading users from the pickle file.
        """
        mock_exists.return_value = True
        mock_pickle_load.return_value = {"user1": {"password": "hashed_password"}}
        users = load_users()
        self.assertEqual(users, {"user1": {"password": "hashed_password"}})

    @patch('builtins.open')
    @patch('auth.authentication.pickle.dump')
    def test_save_users(self, mock_pickle_dump, mock_open):
        """
        Test saving users to the pickle file.
        """
        users_data = {"user1": {"password": "hashed_password"}}
        save_users(users_data)
        mock_pickle_dump.assert_called_once_with(users_data, unittest.mock.ANY)

    @patch('auth.authentication.load_users')
    @patch('auth.authentication.save_users')
    def test_create_user(self, mock_save_users, mock_load_users):
        """
        Test creating a new user.
        """
        mock_load_users.return_value = {}
        success, message = create_user("new_user", "password123")
        self.assertTrue(success)
        self.assertEqual(message, "Account created successfully")
        mock_save_users.assert_called_once()

    @patch('auth.authentication.load_users')
    def test_create_user_already_exists(self, mock_load_users):
        """
        Test creating a user that already exists.
        """
        mock_load_users.return_value = {"existing_user": {"password": "hashed_password"}}
        success, message = create_user("existing_user", "password123")
        self.assertFalse(success)
        self.assertEqual(message, "Username already exists")

    @patch('auth.authentication.load_users')
    def test_authenticate_user_success(self, mock_load_users):
        """
        Test successful user authentication.
        """
        hashed_pw = hash_password("password123")
        mock_load_users.return_value = {"user1": {"password": hashed_pw}}
        success, message = authenticate_user("user1", "password123")
        self.assertTrue(success)
        self.assertEqual(message, "Login successful")

    @patch('auth.authentication.load_users')
    def test_authenticate_user_not_found(self, mock_load_users):
        """
        Test authentication for a user that does not exist.
        """
        mock_load_users.return_value = {}
        success, message = authenticate_user("unknown_user", "password123")
        self.assertFalse(success)
        self.assertEqual(message, "Username not found")

    @patch('auth.authentication.load_users')
    def test_authenticate_user_invalid_password(self, mock_load_users):
        """
        Test authentication with an invalid password.
        """
        hashed_pw = hash_password("password123")
        mock_load_users.return_value = {"user1": {"password": hashed_pw}}
        success, message = authenticate_user("user1", "wrong_password")
        self.assertFalse(success)
        self.assertEqual(message, "Invalid password")

    @patch('auth.authentication.st')
    def test_check_authentication(self, mock_st):
        """
        Test the authentication check.
        """
        mock_st.session_state.get.return_value = True
        self.assertTrue(check_authentication())

        mock_st.session_state.get.return_value = False
        self.assertFalse(check_authentication())

    @patch('auth.authentication.st')
    def test_logout(self, mock_st):
        """
        Test the logout function.
        """
        logout()
        self.assertEqual(mock_st.session_state.__setitem__.call_count, 2)
        mock_st.session_state.clear.assert_called_once()


if __name__ == '__main__':
    unittest.main()
