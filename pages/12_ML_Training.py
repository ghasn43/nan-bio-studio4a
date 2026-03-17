"""
ML Training Page
Interactive page for building datasets and training ML models.
"""

import streamlit as st

st.set_page_config(
    page_title="ML Training - NanoBio Studio™",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 ML Training")

# Check if user is logged in
if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in first")
    st.stop()

st.info("""
🚀 **ML Training Feature**

Machine learning model training and dataset management is being integrated.

**Current Capabilities:**
- ✅ Manual nanoparticle design in **Design Parameters**
- ✅ Real-time scoring and analysis
- ✅ Property prediction

**Coming Soon:**
- 🧠 ML model training interface
- 📊 Dataset building tools
- 🎯 Model evaluation and ranking
- 📈 Training history tracking
- 🔄 Automated model optimization

**What to do now:**
1. Configure designs in **Design Parameters**
2. View real-time scoring for your designs
3. Check back soon for ML training capabilities!
""")

# Show current design if available
if st.session_state.get("design"):
    st.divider()
    st.subheader("Current Design")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Material", st.session_state.get("design", {}).get("Material", "N/A"))
    with col2:
        st.metric("Size", f"{st.session_state.get('design', {}).get('Size', 'N/A')} nm")
    with col3:
        st.metric("Charge", f"{st.session_state.get('design', {}).get('Charge', 'N/A')} mV")
