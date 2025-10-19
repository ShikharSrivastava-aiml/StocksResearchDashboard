"""
Authentication Package
User authentication and session management
"""

from .authentication import (
    hash_password,
    load_users,
    save_users,
    create_user,
    authenticate_user,
    check_authentication,
    logout,
    show_login_page
)

__all__ = [
    'hash_password',
    'load_users',
    'save_users',
    'create_user',
    'authenticate_user',
    'check_authentication',
    'logout',
    'show_login_page'
]