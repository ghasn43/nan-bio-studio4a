"""
Disease Selection - Step 1 of NP design workflow
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.disease_database import (
    get_liver_cancer_subtypes, 
    get_disease_name,
    get_disease_clinical_context,
    get_recommended_drugs,
    format_clinical_context_for_display
)
from modules.clinical_trials_data import get_trials_for_hcc_subtype, format_trial_for_display

st.set_page_config(page_title="Disease & Drug Selection", layout="wide")

st.markdown("""
<style>
.disease-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="disease-header">
    <h1>Step 1: Disease and Drug Selection</h1>
    <p>Select cancer type, subtype, and therapeutic drug to auto-populate design parameters.</p>
</div>
""", unsafe_allow_html=True)

if 'cancer_type' not in st.session_state:
    st.session_state.cancer_type = None
if 'hcc_subtype' not in st.session_state:
    st.session_state.hcc_subtype = None
if 'selected_drug' not in st.session_state:
    st.session_state.selected_drug = None

st.markdown("## Cancer Type Selection")

cancer_types = {
    "liver": "Liver Cancer (Hepatocellular Carcinoma)",
    "lung": "Lung Cancer",
    "breast": "Breast Cancer",
    "pancreatic": "Pancreatic Cancer",
    "brain": "Brain Tumor",
    "colorectal": "Colorectal Cancer",
    "ovarian": "Ovarian Cancer",
}

col1, col2 = st.columns([2, 3])

with col1:
    selected_cancer = st.radio(
        "Choose cancer type:",
        options=list(cancer_types.keys()),
        format_func=lambda x: cancer_types[x],
        key="cancer_selection"
    )
    st.session_state.cancer_type = selected_cancer

with col2:
    st.write("### Why This Cancer Type?")
    if selected_cancer == "liver":
        st.info("Hepatocellular Carcinoma - Explore HCC subtypes with different design strategies")

if selected_cancer == "liver":
    st.markdown("## HCC Subtype Selection")
    
    subtypes = get_liver_cancer_subtypes()
    tab1, tab2, tab3, tab4 = st.tabs(["HCC-S", "HCC-MS", "HCC-L", "Compare"])
    
    with tab1:
        st.markdown("### HCC-S (Well-differentiated)")
        st.write("30% 5-year survival, slower growth, good vasculature")
        st.write("NP Design: 120nm, neutral charge, 5% PEG, 20-30% drug loading")
        context = get_disease_clinical_context("hcc_s")
        if context:
            st.dataframe(format_clinical_context_for_display(context))
        if st.button("Select HCC-S", key="select_hcc_s"):
            st.session_state.hcc_subtype = "hcc_s"
            st.success("HCC-S selected")
            st.rerun()
    
    with tab2:
        st.markdown("### HCC-MS (Intermediate)")
        st.write("15% 5-year survival, moderate growth, variable vasculature")
        st.write("NP Design: 100nm, -5 charge, 7% PEG, 25-35% drug loading")
        context = get_disease_clinical_context("hcc_ms")
        if context:
            st.dataframe(format_clinical_context_for_display(context))
        if st.button("Select HCC-MS", key="select_hcc_ms"):
            st.session_state.hcc_subtype = "hcc_ms"
            st.success("HCC-MS selected")
            st.rerun()
    
    with tab3:
        st.markdown("### HCC-L (Aggressive)")
        st.write("10% 5-year survival, rapid growth, hypoxic")
        st.warning("DESIGN DIFFICULTY: HIGHEST - Requires small particles (50-80nm)")
        st.write("NP Design: 65nm, -10 charge, 10% PEG, 30-40% drug loading")
        context = get_disease_clinical_context("hcc_l")
        if context:
            st.dataframe(format_clinical_context_for_display(context))
        if st.button("Select HCC-L", key="select_hcc_l"):
            st.session_state.hcc_subtype = "hcc_l"
            st.success("HCC-L selected")
            st.rerun()
    
    with tab4:
        st.markdown("### HCC Subtype Comparison")
        comparison_data = {
            "Parameter": ["5-Year Survival", "Growth Rate", "Size (nm)", "Charge", "PEG (%)", "Difficulty"],
            "HCC-S": ["30%", "Slow", "120", "0", "5", "Easy"],
            "HCC-MS": ["15%", "Moderate", "100", "-5", "7", "Medium"],
            "HCC-L": ["10%", "Aggressive", "65", "-10", "10", "Hard"]
        }
        st.dataframe(comparison_data, use_container_width=True)

if st.session_state.hcc_subtype:
    st.markdown(f"## Drug Selection for {get_disease_name(st.session_state.hcc_subtype)}")
    
    drugs = get_recommended_drugs(st.session_state.hcc_subtype)
    
    if drugs:
        drug_choices = {i: drug.drug_name for i, drug in enumerate(drugs)}
        
        selected_drug_idx = st.selectbox(
            "Recommended Drugs",
            options=list(drug_choices.keys()),
            format_func=lambda x: drug_choices[x]
        )
        
        selected_drug = drugs[selected_drug_idx]
        st.session_state.selected_drug = selected_drug
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"### {selected_drug.drug_name}")
            st.write(f"Type: {selected_drug.drug_type}")
            st.write(f"Mechanism: {selected_drug.mechanism}")
        
        with col2:
            st.markdown("### Rationale")
            st.write(selected_drug.reason_for_subtype)
            st.write(f"Dose: {selected_drug.typical_dose}")
        
        with col3:
            st.markdown("### Clinical Trials")
            if selected_drug.clinical_trials:
                for trial in selected_drug.clinical_trials:
                    st.write(f"- {trial}")
    
    st.markdown("---")
    
    if st.button("Continue to Design Parameters", key="continue_to_design"):
        st.info("Navigate to page: 01_Design_Parameters")
