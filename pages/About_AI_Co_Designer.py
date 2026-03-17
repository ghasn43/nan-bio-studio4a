"""About AI Co-Designer - Placeholder"""
import streamlit as st

st.set_page_config(page_title="About AI Co-Designer", layout="wide")
st.title("ℹ️ About AI Co-Designer")

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in first")
    st.stop()

st.info("""
🚀 **Feature Documentation Coming Soon**

The AI Co-Designer feature documentation is being prepared.

For now, refer to:
- **Design Parameters** page for configuring nanoparticles
- **Real-time Scoring** for evaluating your designs
- Contact support for more information
""")
