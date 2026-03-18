"""
Disease & Drug Selection - Step 1 of the NanoBio Studio workflow
"""
import streamlit as st
import sys
from pathlib import Path

# Ensure parent directory is on path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "biotech-lab-main"))

st.set_page_config(page_title="Disease & Drug Selection", layout="wide")

# Check if user is logged in
if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in first")
    st.info("Redirecting to login...")
    st.stop()

# Render sidebar navigation
try:
    from components.sidebar_navigation import render_sidebar_navigation
    render_sidebar_navigation()
except Exception as e:
    st.sidebar.error(f"Navigation error: {e}")

# Initialize session state for disease selection
if "hcc_subtype" not in st.session_state:
    st.session_state.hcc_subtype = "AFP-high HCC"
if "selected_drug" not in st.session_state:
    st.session_state.selected_drug = "Sorafenib"
if "disease_selected" not in st.session_state:
    st.session_state.disease_selected = False

st.title("🏥 Disease & Drug Selection")
st.caption("Step 1: Choose disease type and therapeutic drug")

# Main workflow
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🦠 Select Disease")
    
    disease = st.selectbox(
        "Choose a disease type",
        options=[
            "Hepatocellular Carcinoma (HCC)",
            "Pancreatic Cancer",
            "Breast Cancer",
            "Lung Cancer",
            "Colorectal Cancer"
        ],
        key="disease_select",
        index=0
    )

    if disease == "Hepatocellular Carcinoma (HCC)":
        subtype = st.selectbox(
            "Select HCC Subtype",
            options=[
                "AFP-high HCC",
                "Immune-active HCC",
                "Immune-excluded HCC",
                "Immune-desert HCC"
            ],
            index=0
        )
        st.session_state.hcc_subtype = subtype
    
    st.session_state.selected_disease = disease

with col2:
    st.subheader("💊 Select Therapeutic Drug")
    
    drug = st.selectbox(
        "Choose a therapeutic drug",
        options=[
            "Sorafenib",
            "Lenvatinib",
            "Atezolizumab + Bevacizumab",
            "Durvalumab",
            "Nivolumab"
        ],
        index=0
    )
    
    st.session_state.selected_drug = drug

st.markdown("---")

# Display selections
if st.session_state.get("selected_disease") and st.session_state.get("selected_drug"):
    st.success(f"✅ Selected: **{st.session_state.selected_disease}** with **{st.session_state.selected_drug}**")
else:
    st.info("👆 Please select a disease and drug above")

# Action buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("← Back to Home", use_container_width=True):
        st.session_state.current_tab = "🏠 Home"
        st.switch_page("pages/2_Home.py")

with col2:
    if st.session_state.get("selected_disease") and st.session_state.get("selected_drug"):
        if st.button("Next: Design Parameters →", type="primary", use_container_width=True):
            st.session_state.disease_selected = True
            st.switch_page("pages/3_Design_Parameters.py")
    else:
        st.button("Next: Design Parameters →", disabled=True, use_container_width=True)

with col3:
    pass
