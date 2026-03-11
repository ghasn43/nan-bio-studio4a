"""ML Module Package"""
from .config import get_settings
from .db.database import get_db

# FastAPI app only imported when explicitly needed (not on Streamlit)
def get_app():
    """Lazy load FastAPI app to avoid import errors in Streamlit Cloud"""
    from .main import app
    return app

__all__ = ["get_settings", "get_db", "get_app"]
