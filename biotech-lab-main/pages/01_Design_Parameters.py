"""
Design Parameters - Step 2 of NP design workflow
Shows disease-specific optimized parameters and design rationale
Links to clinical trials and educational content
"""

import streamlit as st
import sys
import os
import pandas as pd

# Add modules to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.disease_database import (
    get_disease_design_parameters,
    get_disease_name,
    get_design_rationale,
    get_tissue_barrier_info,
    get_special_notes,
    format_np_params_for_display
)
from modules.clinical_trials_data import get_trials_for_hcc_subtype

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Design Parameters",
    page_icon="⚙️",
    layout="wide"
)

st.markdown("""
<style>
    .param-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .critical-warning {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .design-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 10px 0;
    }
    .rationale-box {
        background: #e7f3ff;
        border-left: 4px solid #0066cc;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CHECK SESSION STATE
# ============================================================

if 'hcc_subtype' not in st.session_state or st.session_state.hcc_subtype is None:
    st.error("⚠️ Please complete Step 1 (Disease Selection) first!")
    st.info("Go to Disease Selection page and choose your cancer subtype.")
    st.stop()

hcc_subtype = st.session_state.hcc_subtype
disease_name = get_disease_name(hcc_subtype)

# ============================================================
# HEADER
# ============================================================

st.markdown(f"""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
    <h1>⚙️ Step 2: Optimized Design Parameters</h1>
    <p>For: <strong>{disease_name}</strong></p>
    <p>These parameters are auto-optimized based on the tumor microenvironment and clinical evidence.</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# GET DESIGN PARAMETERS
# ============================================================

params = get_disease_design_parameters(hcc_subtype)
rationale = get_design_rationale(hcc_subtype)
tissue_barriers = get_tissue_barrier_info(hcc_subtype)
special_notes = get_special_notes(hcc_subtype)

if not params:
    st.error("Could not load design parameters for this subtype")
    st.stop()

# ============================================================
# SECTION 1: CRITICAL PARAMETERS
# ============================================================

st.markdown("## 🎯 Critical NP Design Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="param-card">
        <h3>Size</h3>
        <p>{params.size_nm_min}-{params.size_nm_max} nm</p>
        <p><strong>Optimal: {params.size_nm_optimal} nm</strong></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="param-card">
        <h3>Surface Charge</h3>
        <p>{params.surface_charge.upper()}</p>
        <p><strong>Value: {params.charge_value}</strong></p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="param-card">
        <h3>PEG Coating</h3>
        <p><strong>{params.peg_coating_percent}%</strong></p>
        <p>Immune Evasion</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# SECTION 2: DETAILED PARAMETERS
# ============================================================

st.markdown("## 📋 Complete Parameter Table")

params_dict = format_np_params_for_display(params)
params_df = pd.DataFrame(list(params_dict.items()), columns=["Parameter", "Value"])
st.dataframe(params_df, use_container_width=True)

# ============================================================
# SECTION 3: DESIGN RATIONALE (WHY THESE PARAMETERS)
# ============================================================

st.markdown("## 💡 Design Rationale: WHY These Parameters?")

for i, reason in enumerate(rationale, 1):
    # Highlight critical points for aggressive HCC
    if "CRITICAL" in reason or "MUST" in reason or "⚠️" in reason:
        st.markdown(f"""
        <div class="critical-warning">
            <strong>⚠️ #{i}: {reason}</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="rationale-box">
            <strong>#{i}:</strong> {reason}
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# SECTION 4: TISSUE BARRIER INFORMATION
# ============================================================

st.markdown("## 🏗️ Tissue Barrier Analysis")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    ### Barrier Difficulty: **{tissue_barriers.get('difficulty', 'Unknown').upper()}**
    
    {tissue_barriers.get('description', '')}
    """)

with col2:
    st.markdown("### Key Challenges:")
    challenges = tissue_barriers.get('key_challenges', [])
    for challenge in challenges:
        st.write(f"• {challenge}")

# Additional strategies for difficult barriers
if tissue_barriers.get('advanced_strategies'):
    st.markdown("### Advanced Penetration Strategies:")
    strategies = tissue_barriers.get('advanced_strategies', [])
    for strategy in strategies:
        st.info(f"💡 {strategy}")

# ============================================================
# SECTION 5: SPECIAL NOTES FOR CHALLENGING CASES
# ============================================================

if special_notes:
    st.markdown("---")
    st.markdown("## ⚠️ Special Design Notes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### Challenge Level: {special_notes.get('challenge_level', 'N/A')}")
        st.markdown(f"**why:** {special_notes.get('why_challenging', 'N/A')}")
    
    with col2:
        st.markdown(f"### Clinical Reality")
        st.markdown(f"**{special_notes.get('clinical_reality', 'N/A')}**")
        if special_notes.get('np_design_strategy'):
            st.info(f"🎯 **NP Strategy:** {special_notes.get('np_design_strategy')}")

# ============================================================
# SECTION 6: RELEVANT CLINICAL TRIALS
# ============================================================

st.markdown("---")
st.markdown("## 🏥 Relevant Clinical Trials")

trials = get_trials_for_hcc_subtype(hcc_subtype)

if trials:
    st.warning(f"**{len(trials)} FDA-relevant clinical trials** for this HCC subtype:")
    
    trial_tabs = st.tabs([f"Trial {i+1}: {trial.trial_id}" for i, trial in enumerate(trials[:3])])
    
    for tab, trial in zip(trial_tabs, trials[:3]):
        with tab:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **Trial Name:** {trial.trial_name}
                
                **Phase:** {trial.phase.value}
                
                **Status:** {trial.status.value}
                
                **Primary Endpoint:** {trial.primary_endpoint}
                """)
            
            with col2:
                st.markdown(f"""
                **Mechanism:** {trial.mechanism}
                
                **Sample Size:** {trial.study_population_count}
                
                **Drugs:** {', '.join(trial.drug_names)}
                
                **Year:** {trial.publication_year or 'Ongoing'}
                """)
            
            if trial.median_overall_survival_months:
                st.success(f"✅ Median Overall Survival: {trial.median_overall_survival_months} months")
            
            if trial.landmark_trial:
                st.info("🌟 This is a FDA landmark trial - key decision-making evidence")
            
            st.caption(trial.notes)
else:
    st.info("No specific clinical trials found for this subtype yet.")

# ============================================================
# SECTION 7: PARAMETER COMPARISON
# ============================================================

st.markdown("---")
st.markdown("## 📊 How Your Parameters Compare to Other HCC Subtypes")

# Create comparison table
comparison_df = pd.DataFrame({
    "Parameter": ["Optimal Size (nm)", "Surface Charge", "PEG Coating (%)", "Drug Loading (%)", "Difficulty"],
    "HCC-S": ["120", "Neutral (0)", "5", "20-30", "⭐"],
    "HCC-MS": ["100", "Slight (-5)", "7", "25-35", "⭐⭐⭐"],
    "HCC-L": ["65", "More (-10)", "10", "30-40", "⭐⭐⭐⭐⭐"]
})

# Highlight the selected subtype
st.dataframe(comparison_df, use_container_width=True)

# ============================================================
# SECTION 8: NEXT STEPS
# ============================================================

st.markdown("---")
st.markdown("## ➡️ Next Steps")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### Option 1: AI Co-Designer
    Use these pre-filled parameters to start designing with AI assistance.
    
    **Best for:** Interactive exploration and optimization
    """)

with col2:
    st.markdown("""
    ### Option 2: Manual Design
    Use these parameters as a starting point and create custom designs.
    
    **Best for:** Learning and fine-tuning
    """)

with col3:
    st.markdown("""
    ### Option 3: Review Literature
    Check clinical trials and research papers for this HCC subtype.
    
    **Best for:** Understanding state-of-the-art approaches
    """)

col1, col2 = st.columns(2)

with col1:
    if st.button("🤖 Launch AI Co-Designer", key="launch_codesigner"):
        st.success("Launching AI Co-Designer with your parameters...")
        # In production: st.switch_page("pages/10_AI_Co_Designer.py")
        st.info("Navigate to page: **9_AI_Co_Designer** after clicking")

with col2:
    if st.button("📊 View Data Analytics", key="view_analytics"):
        st.success("Going to Data Analytics page...")
        st.info("Check out page: **17_Data_Analytics** for ML insights")

# ============================================================
# EDUCATIONAL FOOTER
# ============================================================

with st.expander("📚 Educational: How Were These Parameters Determined?"):
    st.markdown("""
    ### Data-Driven Parameter Optimization
    
    These parameters are based on:
    
    1. **Clinical Trial Data**
       - IMbrave150 (Atezolizumab + Bevacizumab)
       - SHARP, REFLECT, RESORCE trials
       - Published response rates and survival data
    
    2. **Tumor Microenvironment Analysis**
       - Vascularization characteristics
       - Hypoxia levels in HCC-L
       - Stromal density and ECM composition
    
    3. **Nanoparticle Engineering Literature**
       - Optimal sizes for EPR effect
       - Surface charge effects on penetration
       - PEG coating impact on circulation
    
    4. **Machine Learning Models**
       - Trained on successful past designs
       - Disease-specific optimization algorithms
       - Predictive efficacy modeling
    
    ### References
    - HCC gene expression signatures (Nature 2015)
    - IMbrave150 clinical trial (Lancet 2020)
    - NP design optimization reviews (Advanced Materials 2023)
    """)

with st.expander("💻 Technical Details: Parameter Calculation"):
    st.markdown(f"""
    ### For {disease_name}
    
    **Size Calculation:**
    - EPR window: 10-200 nm
    - Hypoxic penetration requirement: {params.size_nm_max if params.size_nm_max < 150 else 'not limiting'} nm
    - Renal clearance threshold: {params.renal_clearance_nm_threshold} nm
    - **Selected: {params.size_nm_optimal} nm**
    
    **Charge Selection:**
    - Base charge: {params.charge_value}
    - Penetration enhancement: {params.charge_value <= -5 if params.charge_value <= -5 else 'minimal'}
    - Immune evasion: Optimized
    
    **Drug Loading:**
    - Typical range: {params.drug_loading_percent_min}-{params.drug_loading_percent_max}%
    - Adjusted for: Hypoxia impact on efficacy
    - Degradation timing: {params.biodegradation_hours_min}-{params.biodegradation_hours_max} hours
    """)
