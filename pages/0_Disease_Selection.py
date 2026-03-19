"""
Disease & Drug Selection - Step 1 of the NanoBio Studio workflow
"""
import streamlit as st
import sys
from pathlib import Path

# Ensure parent directory is on path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.disease_drug_mapping import (
    get_diseases, 
    get_subtypes_for_disease, 
    get_drugs_for_disease,
    get_drugs_for_subtype,
    get_drug_details,
    get_disease_info
)

st.set_page_config(page_title="Disease & Drug Selection", layout="wide")

# ============================================================
# SESSION RESTORATION & TIMEOUT CHECK
# ============================================================

from streamlit_auth import restore_session_from_persistent, check_session_timeout, StreamlitAuth

# Initialize session state
StreamlitAuth.init_session_state()

# Try to restore session from URL query parameters
query_params = st.query_params
if "session_token" in query_params:
    token = query_params.get("session_token", "")
    if token:
        restore_session_from_persistent(token)

# Check if user is logged in or session is valid
logged_in = st.session_state.get("logged_in") or st.session_state.get("authenticated")

if not logged_in:
    st.warning("⚠️ Please log in first")
    st.info("You need to be logged in to access this page.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔐 Go to Login", type="primary", use_container_width=True):
            st.query_params.clear()
            st.switch_page("Login.py")
    
    st.stop()

# Check for session timeout
if st.session_state.get("session_token"):
    token = st.session_state.session_token
    if not check_session_timeout(token):
        st.warning("⏰ Your session has expired due to inactivity (15 minutes). Please log in again.")
        StreamlitAuth.logout()
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
    
    diseases = get_diseases()
    
    disease = st.selectbox(
        "Choose a disease type",
        options=diseases,
        key="disease_select",
        index=0
    )
    
    # Get subtypes and display if applicable
    subtypes = get_subtypes_for_disease(disease)
    
    if subtypes and len(subtypes) > 1:
        subtype = st.selectbox(
            "Select disease subtype",
            options=subtypes,
            index=0
        )
        st.session_state.hcc_subtype = subtype
    elif subtypes and len(subtypes) == 1:
        st.info(f"Subtype: {subtypes[0]}")
        st.session_state.hcc_subtype = subtypes[0]
    
    st.session_state.selected_disease = disease
    
    # Display disease epidemiology
    with st.expander("📊 Disease Statistics", expanded=False):
        disease_info = get_disease_info(disease)
        if disease_info:
            epi = disease_info.get("epidemiology", {})
            if epi:
                col_epi1, col_epi2, col_epi3 = st.columns(3)
                with col_epi1:
                    st.metric("Annual Incidence", epi.get("incidence", "N/A"))
                with col_epi2:
                    st.metric("Annual Mortality", epi.get("mortality", "N/A"))
                with col_epi3:
                    st.metric("5-Year Survival", epi.get("5yr_survival", "N/A"))
            
            unmet = disease_info.get("unmet_needs", "")
            if unmet:
                st.markdown(f"**Unmet Clinical Needs:** {unmet}")

with col2:
    st.subheader("💊 Select Therapeutic Drug")
    
    # Get drugs appropriate for selected disease (and subtype if applicable)
    if "hcc_subtype" in st.session_state and disease == "Hepatocellular Carcinoma (HCC)":
        available_drugs = get_drugs_for_subtype(disease, st.session_state.hcc_subtype)
    else:
        available_drugs = get_drugs_for_disease(disease)
    
    if not available_drugs:
        st.error("No drugs available for selected disease")
        drug = None
    else:
        drug = st.selectbox(
            "Choose a therapeutic drug",
            options=available_drugs,
            index=0
        )
        st.session_state.selected_drug = drug
        
        # Display drug details
        with st.expander("ℹ️ Drug Information", expanded=False):
            drug_details = get_drug_details(disease, drug)
            if drug_details:
                st.markdown(f"**Drug Type:** {drug_details.get('type', 'N/A')}")
                st.markdown(f"**Mechanism:** {drug_details.get('mechanism', 'N/A')}")
                st.markdown(f"**Description:** {drug_details.get('description', 'N/A')}")
                st.markdown(f"**Approved:** {'✅ Yes' if drug_details.get('approved') else '❌ No'}")
                
                suitable = drug_details.get('suitable_for', [])
                if suitable:
                    st.markdown(f"**Suitable for subtypes:** {', '.join(suitable)}")

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
        from streamlit_auth import switch_page_with_token
        switch_page_with_token("pages/2_Home.py")

with col2:
    if st.session_state.get("selected_disease") and st.session_state.get("selected_drug"):
        if st.button("Next: Design Parameters →", type="primary", use_container_width=True):
            st.session_state.disease_selected = True
            from streamlit_auth import switch_page_with_token
            switch_page_with_token("pages/3_Design_Parameters.py")
    else:
        st.button("Next: Design Parameters →", disabled=True, use_container_width=True)

with col3:
    pass
