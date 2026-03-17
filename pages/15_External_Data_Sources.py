"""
15 External Data Sources - Placeholder Page
"""

import streamlit as st

st.set_page_config(page_title="15 External Data Sources", page_icon="📊", layout="wide")

st.title("📊 15 External Data Sources")

# Check if user is logged in
if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in first")
    st.stop()

st.info("""
🚀 **Feature Coming Soon**

15 External Data Sources is being integrated with your nanoparticle design workflow.

**Current Capabilities:**
- ✅ Manual nanoparticle design in **Design Parameters**
- ✅ Real-time scoring and analysis
- ✅ Property optimization

**What to do now:**
1. Go to **Design Parameters** to configure nanoparticles
2. View real-time scoring for your designs
3. Check back soon for this feature!
""")

# Show current design if available
if st.session_state.get("design"):
    st.divider()
    st.subheader("Current Design Configuration")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Material", st.session_state.get("design", {}).get("Material", "N/A"))
    with col2:
        st.metric("Size", f"{st.session_state.get('design', {}).get('Size', 'N/A')} nm")
    with col3:
        st.metric("Charge", f"{st.session_state.get('design', {}).get('Charge', 'N/A')} mV")
