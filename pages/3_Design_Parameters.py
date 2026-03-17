"""
Design Parameters - Step 2 of the NanoBio Studio workflow
Configure nanoparticle design parameters
"""
import streamlit as st
import sys
from pathlib import Path

# Ensure parent directory is on path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "biotech-lab-main"))

st.set_page_config(page_title="Design Parameters", layout="wide")

# Check if user is logged in
if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in first")
    st.switch_page("Login.py")

# Check if disease was selected
if not st.session_state.get("disease_selected"):
    st.warning("⚠️ Please select a disease first")
    st.info("Redirecting to disease selection...")
    st.switch_page("pages/0_Disease_Selection.py")

# Initialize design parameters in session state
if "np_size_nm" not in st.session_state:
    st.session_state.np_size_nm = 50
if "np_composition" not in st.session_state:
    st.session_state.np_composition = "Lipid Nanoparticle (LNP)"
if "surface_coating" not in st.session_state:
    st.session_state.np_surface_coating = "PEG"
if "target_efficiency" not in st.session_state:
    st.session_state.target_efficiency = 60

st.title("🎨 Design Parameters")
st.caption("Step 2: Configure nanoparticle design parameters")
st.divider()

# Show disease selection context
col1, col2 = st.columns(2)
with col1:
    st.info(f"""
    **Disease:** {st.session_state.get('selected_disease', 'Not selected')}
    
    **Drug:** {st.session_state.get('selected_drug', 'Not selected')}
    """)

with col2:
    st.info(f"""
    **HCC Subtype:** {st.session_state.get('hcc_subtype', 'N/A')}
    """)

st.divider()

# Design parameters
st.subheader("🔬 Nanoparticle Specifications")

col1, col2 = st.columns(2)

with col1:
    st.write("**Particle Size**")
    size = st.slider(
        "Nanoparticle size (nm)",
        min_value=10,
        max_value=200,
        value=st.session_state.np_size_nm,
        step=5
    )
    st.session_state.np_size_nm = size

    st.write("**Composition**")
    composition = st.selectbox(
        "Select nanoparticle material",
        options=[
            "Lipid Nanoparticle (LNP)",
            "Polymeric Nanoparticle (PNP)",
            "Gold Nanoparticle (AuNP)",
            "Silica Nanoparticle (SiNP)",
            "Iron Oxide Nanoparticle (IONP)"
        ],
        index=0
    )
    st.session_state.np_composition = composition

with col2:
    st.write("**Surface Coating**")
    coating = st.selectbox(
        "Select surface coating",
        options=[
            "PEG (Polyethylene Glycol)",
            "Apolipoprotein",
            "Transferrin",
            "RGD Peptide",
            "No coating"
        ],
        index=0
    )
    st.session_state.np_surface_coating = coating

    st.write("**Target Delivery Efficiency**")
    efficiency = st.slider(
        "Desired delivery efficiency (%)",
        min_value=20,
        max_value=95,
        value=st.session_state.target_efficiency,
        step=5
    )
    st.session_state.target_efficiency = efficiency

st.divider()

# Display summary
st.subheader("📋 Design Summary")
summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    st.markdown(f"""
    **Current Configuration:**
    - Size: **{st.session_state.np_size_nm} nm**
    - Material: **{st.session_state.np_composition}**
    - Coating: **{st.session_state.np_surface_coating}**
    - Target Efficiency: **{st.session_state.target_efficiency}%**
    """)

with summary_col2:
    st.success("✅ Configuration is valid and ready for simulation")

st.divider()

# Navigation buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("← Back to Disease Selection", use_container_width=True):
        st.switch_page("pages/0_Disease_Selection.py")

with col2:
    if st.button("Next: Run Simulation →", type="primary", use_container_width=True):
        st.session_state.parameters_configured = True
        st.success("✅ Parameters saved! Proceeding to simulation...")
        st.info("🧬 Simulation page coming next")

with col3:
    if st.button("Save Design", use_container_width=True):
        st.session_state.design_saved = True
        st.success("✅ Design saved to your profile")
