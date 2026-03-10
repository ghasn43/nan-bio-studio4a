"""
Phase 3 Configuration

Additional configuration for authentication, RBAC, and Streamlit integration.
"""

import os
from enum import Enum


class JWTSettings:
    """JWT configuration"""

    # Secret key (CHANGE THIS IN PRODUCTION)
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")

    # Algorithm
    ALGORITHM = "HS256"

    # Expiration in hours
    EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    # Refresh token expiration in days
    REFRESH_EXPIRATION_DAYS = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", "7"))


class StreamlitSessionConfig:
    """Streamlit session configuration"""

    # Session timeout in seconds
    SESSION_TIMEOUT = int(os.getenv("STREAMLIT_SESSION_TIMEOUT", "3600"))

    # Cache settings
    ENABLE_CACHE = os.getenv("STREAMLIT_ENABLE_CACHE", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("STREAMLIT_CACHE_TTL", "300"))

    # UI settings
    SHOW_SIDEBAR = os.getenv("STREAMLIT_SHOW_SIDEBAR", "true").lower() == "true"
    SHOW_MENU = os.getenv("STREAMLIT_SHOW_MENU", "true").lower() == "true"
    SHOW_FOOTER = os.getenv("STREAMLIT_SHOW_FOOTER", "true").lower() == "true"


class RBACConfig:
    """RBAC configuration"""

    # Enable/disable RBAC
    ENABLE_RBAC = os.getenv("ENABLE_RBAC", "true").lower() == "true"

    # Require login
    REQUIRE_LOGIN = os.getenv("REQUIRE_LOGIN", "true").lower() == "true"

    # Default role for new users
    DEFAULT_ROLE = os.getenv("DEFAULT_ROLE", "viewer")


class DebugConfig:
    """Debug configuration"""

    # Enable debug logging
    DEBUG_LOGGING = os.getenv("DEBUG_LOGGING", "false").lower() == "true"

    # Show user info in sidebar
    SHOW_USER_DEBUG_INFO = os.getenv("SHOW_USER_DEBUG_INFO", "false").lower() == "true"

    # Show permissions matrix
    SHOW_PERMISSIONS_MATRIX = os.getenv("SHOW_PERMISSIONS_MATRIX", "false").lower() == "true"


# Environment names
class Environment(str, Enum):
    """Environment types"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


# Current environment
ENVIRONMENT = Environment(os.getenv("APP_ENV", "development").lower())


def get_jwt_settings():
    """Get JWT settings"""
    return JWTSettings()


def get_streamlit_config():
    """Get Streamlit configuration"""
    return StreamlitSessionConfig()


def get_rbac_config():
    """Get RBAC configuration"""
    return RBACConfig()


def get_debug_config():
    """Get debug configuration"""
    return DebugConfig()
