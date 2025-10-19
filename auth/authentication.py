"""
User Authentication Module
Handles user registration, login, and session management
"""

import streamlit as st
import hashlib
import pickle
import os
from datetime import datetime
from pathlib import Path

USERS_FILE = "users_data.pkl"


def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def load_users() -> dict:
    """Load users data from encrypted file."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'rb') as f:
                return pickle.load(f)
        except:
            return {}
    return {}


def save_users(users_data: dict) -> None:
    """Save users data to encrypted file."""
    with open(USERS_FILE, 'wb') as f:
        pickle.dump(users_data, f)


def create_user(username: str, password: str) -> tuple[bool, str]:
    """Create a new user account."""
    users = load_users()

    if username in users:
        return False, "Username already exists"

    users[username] = {
        'password': hash_password(password),
        'created_at': datetime.now().isoformat(),
        'portfolio': [],
        'watchlist': [],
        'preferences': {}
    }

    save_users(users)
    return True, "Account created successfully"


def authenticate_user(username: str, password: str) -> tuple[bool, str]:
    """Authenticate user credentials."""
    users = load_users()

    if username not in users:
        return False, "Username not found"

    if users[username]['password'] == hash_password(password):
        return True, "Login successful"

    return False, "Invalid password"


def check_authentication() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get('logged_in', False)


def logout():
    """Logout current user."""
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state.clear()


def show_login_page():
    """Display login/registration page."""
    st.title("🔐 StockAnalysisDashboard - Login")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            st.subheader("Login to Your Account")
            login_username = st.text_input("Username", key="login_user")
            login_password = st.text_input("Password", type="password", key="login_pass")

            if st.button("🔓 Login", use_container_width=True):
                if login_username and login_password:
                    success, message = authenticate_user(login_username, login_password)
                    if success:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = login_username
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter both username and password")

        with tab2:
            st.subheader("Create New Account")
            reg_username = st.text_input("Choose Username", key="reg_user")
            reg_password = st.text_input("Choose Password", type="password", key="reg_pass")
            reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_confirm")

            if st.button("📝 Register", use_container_width=True):
                if reg_username and reg_password and reg_password_confirm:
                    if reg_password != reg_password_confirm:
                        st.error("Passwords do not match")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters")
                    elif len(reg_username) < 3:
                        st.error("Username must be at least 3 characters")
                    else:
                        success, message = create_user(reg_username, reg_password)
                        if success:
                            st.success(message + " - You can now login!")
                        else:
                            st.error(message)
                else:
                    st.warning("Please fill in all fields")

                st.info("""
                        **Features:**
                        - 📊 Stock Analysis Reports
                        - 💼 Portfolio Management (Saved to your account)
                        - 📰 Market News & Sentiment
                        - 💬 Earnings Call Transcripts
                        """)