#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧬 NanoBio Studio — Main Entry Point
Connecting Nanotechnology & Biotechnology
Developed by Experts Group FZE

This file serves as the main Streamlit entry point for Streamlit Cloud deployment.
"""

import streamlit as st
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "biotech-lab-main"))

# ============================================================
# PAGE CONFIG - MUST BE FIRST
# ============================================================
st.set_page_config(
    page_title="NanoBio Studio Login",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# IMPORT AND RUN LOGIN PAGE
# ============================================================

import logging
import time
from datetime import datetime
from streamlit_auth import StreamlitAuth, show_user_info, restore_session_from_persistent, check_session_timeout

logger = logging.getLogger(__name__)


def main():
    """Main login page"""

    st.title("🔐 NanoBio Studio Login")

    # Initialize session state
    StreamlitAuth.init_session_state()
    
    # ============================================================
    # TRY TO RESTORE SESSION FROM PERSISTENT STORAGE
    # ============================================================
    
    # Check URL query parameters for session token
    query_params = st.query_params
    if "session_token" in query_params:
        token = query_params.get("session_token", "")
        if token and restore_session_from_persistent(token):
            st.success("✅ Session restored! You are logged in.")
            st.info("Redirecting to Disease Selection...")
            time.sleep(0.5)
            st.switch_page("pages/0_Disease_Selection.py")
            return
    
    # Check if session token is in memory and still valid
    if st.session_state.get("session_token"):
        token = st.session_state.session_token
        if check_session_timeout(token):
            st.success("✅ You are already logged in!")
            show_user_info()
            st.divider()
            if st.button("→ Go to Disease Selection", type="primary", use_container_width=True):
                st.switch_page("pages/0_Disease_Selection.py")
            st.info("Or use the browser back button to continue")
            return
        else:
            # Session timed out
            st.warning("⏰ Your session has expired due to inactivity (15 minutes). Please log in again.")
            StreamlitAuth.logout()
            st.query_params.clear()

    # If already authenticated in memory, redirect to main app
    if StreamlitAuth.is_authenticated() or (st.session_state.get("logged_in") and st.session_state.get("username")):
        st.success("✅ You are already logged in!")
        
        show_user_info()
        
        st.divider()
        
        if st.button("→ Go to Disease Selection", type="primary", use_container_width=True):
            st.switch_page("pages/0_Disease_Selection.py")
        
        st.info("Or use the browser back button to continue")

        return

    # Login form
    st.subheader("Sign In")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Demo Credentials")
        st.info("""
        **Username:** admin  
        **Password:** Admin@2024  
        
        Or sign up below →
        """)

    with col2:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Sign In", type="primary", use_container_width=True):
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                # Authenticate using the auth module
                from auth import authenticate
                
                # authenticate returns (success: bool, role: Optional[str])
                success, role = authenticate(username, password)
                
                if success:
                    # Set session state for both old and new systems
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = role or "viewer"
                    
                    # Also set StreamlitAuth session (creates persistent session)
                    token = StreamlitAuth.login(
                        user_id=username,
                        username=username,
                        email="",
                        roles=[role or "viewer"]
                    )
                    
                    st.session_state.session_token = token
                    
                    st.success(f"✅ Welcome {username}!")
                    
                    # Show user info
                    show_user_info()
                    
                    time.sleep(0.5)
                    
                    # Redirect with session token in URL for persistence across page refreshes
                    st.query_params["session_token"] = token
                    st.switch_page("pages/0_Disease_Selection.py")
                else:
                    st.error("❌ Invalid username or password")


if __name__ == "__main__":
    main()

