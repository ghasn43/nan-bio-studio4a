"""
Disease & Drug Selection - First step in NP design workflow
Students select cancer type, subtype, and therapeutic drug
Auto-populates design constraints based on selections
"""

import streamlit as st
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.disease_database import (
    get_liver_cancer_subtypes, 
    get_disease_name,
    get_disease_clinical_context,
    get_recommended_drugs,
    format_clinical_context_for_display
)
from modules.clinical_trials_data import get_trials_for_hcc_subtype, format_trial_for_display

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Disease & Drug Selection",
    page_icon="🧬",
    layout="wide"
)

# Custom branding
st.markdown("""
<style>
    .disease-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .cascade-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .disease-card {
        background: white;
        border: 2px solid #667eea;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 2px solid #28a745;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="disease-header">
    <h1>🧬 Step 1: Disease & Drug Selection</h1>
    <p>Select the cancer type and subtype, then choose a therapeutic drug.</p>
    <p><strong>Your selections will auto-populate optimized nanoparticle design parameters.</strong></p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if 'cancer_type' not in st.session_state:
    st.session_state.cancer_type = None
if 'hcc_subtype' not in st.session_state:
    st.session_state.hcc_subtype = None
if 'selected_drug' not in st.session_state:
    st.session_state.selected_drug = None

# ============================================================
# STEP 1: CANCER TYPE SELECTION
# ============================================================

st.markdown("## Step 1️⃣: Select Cancer Type")

cancer_types = {
    "liver": "🦠 Liver Cancer (Hepatocellular Carcinoma)",
    "lung": "🫁 Lung Cancer",
    "breast": "🤍 Breast Cancer",
    "pancreatic": "🧆 Pancreatic Cancer",
    "brain": "🧠 Brain Tumor (Glioblastoma)",
    "colorectal": "🔴 Colorectal Cancer",
    "ovarian": "🌸 Ovarian Cancer",
}

col1, col2 = st.columns([2, 3])

with col1:
    st.write("### Available Cancer Types")
    selected_cancer = st.radio(
        "Choose cancer type:",
        options=list(cancer_types.keys()),
        format_func=lambda x: cancer_types[x],
        key="cancer_selection"
    )
    st.session_state.cancer_type = selected_cancer

# Display cancer info
with col2:
    st.write("### Why This Cancer Type?")
    if selected_cancer == "liver":
        st.info("""
        **Hepatocellular Carcinoma (HCC)** - Most common primary liver cancer
        
        **Why interesting for NP design:**
        - Hepatocyte-specific targeting possible
        - Multiple HCC subtypes → different design strategies
        - Clinical trial evidence for multiple approaches
        - Hypoxic environment in aggressive subtypes poses challenges
        """)
    elif selected_cancer == "lung":
        st.info("Lung cancer NP designs currently under development - Coming soon!")
    else:
        st.info(f"Other cancer types - Stay tuned for {selected_cancer} options!")

# ============================================================
# STEP 2: HCC SUBTYPE SELECTION (Conditional)
# ============================================================

if selected_cancer == "liver":
    st.markdown("## Step 2️⃣: Select HCC Subtype")
    st.markdown("""
    Different HCC subtypes have dramatically different vascularization, 
    growth rates, and treatment responses. **This determines your NP design parameters.**
    """)
    
    # Get available subtypes
    subtypes = get_liver_cancer_subtypes()
    
    tab1, tab2, tab3, tab4 = st.tabs(
        ["HCC-S (Well-differentiated)", "HCC-MS (Intermediate)", "HCC-L (Aggressive)", "Compare All"]
    )
    
    # TAB 1: HCC-S
    with tab1:
        st.markdown("### 🟢 HCC-S (Well-differentiated, Slow Growth)")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Clinical Characteristics:**
            - Better prognosis (30% 5-year survival)
            - Slower growth rate
            - Good vascularization
            - Lower aggressiveness
            
            **NP Design Result:**
            - Larger particles (100-150 nm)
            - Neutral surface charge
            - Moderate PEG (5%)
            - 20-30% drug loading
            """)
        
        with col2:
            # Show clinical context
            context = get_disease_clinical_context("hcc_s")
            if context:
                st.markdown("**Statistical Summary:**")
                st.dataframe(format_clinical_context_for_display(context))
        
        if st.button("🎯 Select HCC-S", key="select_hcc_s"):
            st.session_state.hcc_subtype = "hcc_s"
            st.success("✅ HCC-S selected! Moving to Step 3...")
            st.rerun()
    
    # TAB 2: HCC-MS
    with tab2:
        st.markdown("### 🟡 HCC-MS (Intermediate Aggressiveness)")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Clinical Characteristics:**
            - Intermediate prognosis (15% 5-year survival)
            - Moderate growth rate
            - Variable vascularization
            - Mixed differentiation
            
            **NP Design Result:**
            - Medium particles (80-120 nm)
            - Slightly negative charge (-5)
            - Moderate PEG (7%)
            - 25-35% drug loading
            """)
        
        with col2:
            context = get_disease_clinical_context("hcc_ms")
            if context:
                st.markdown("**Statistical Summary:**")
                st.dataframe(format_clinical_context_for_display(context))
        
        if st.button("🎯 Select HCC-MS", key="select_hcc_ms"):
            st.session_state.hcc_subtype = "hcc_ms"
            st.success("✅ HCC-MS selected! Moving to Step 3...")
            st.rerun()
    
    # TAB 3: HCC-L (AGGRESSIVE)
    with tab3:
        st.markdown("### 🔴 HCC-L (Poorly Differentiated, AGGRESSIVE)")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Clinical Characteristics:**
            - Poor prognosis (10% 5-year survival)
            - Rapid growth
            - **HYPOXIC core** (poor vascularization)
            - Highly aggressive
            
            **NP Design Challenge:** ⚠️ ⚠️ ⚠️
            - **MUST use small particles (50-80 nm)**
            - More negative charge (-10)
            - Maximum PEG (10%)
            - High drug loading (30-40%)
            """)
        
        with col2:
            st.warning("""
            **⚠️ DESIGN DIFFICULTY: HIGHEST**
            
            Hypoxic core creates massive barriers:
            - Poor blood supply
            - Dense stromal barriers
            - High interstitial pressure
            - Necrotic regions
            
            **Strategy:** Smaller particles penetrate better through barriers
            """)
            
            context = get_disease_clinical_context("hcc_l")
            if context:
                st.markdown("**Statistical Summary:**")
                st.dataframe(format_clinical_context_for_display(context))
        
        if st.button("🎯 Select HCC-L", key="select_hcc_l"):
            st.session_state.hcc_subtype = "hcc_l"
            st.success("✅ HCC-L selected! Moving to Step 3...")
            st.rerun()
    
    # TAB 4: COMPARISON
    with tab4:
        st.markdown("### 📊 Comparison of All HCC Subtypes")
        
        comparison_data = {
            "Characteristic": [
                "5-Year Survival (%)",
                "Growth Rate",
                "Vascularization",
                "Optimal NP Size (nm)",
                "Surface Charge",
                "PEG Coating (%)",
                "Drug Loading (%)",
                "Difficulty Level"
            ],
            "HCC-S": ["30", "Slow", "Good", "120", "Neutral (0)", "5", "20-30", "⭐"],
            "HCC-MS": ["15", "Moderate", "Moderate", "100", "Slight (-5)", "7", "25-35", "⭐⭐⭐"],
            "HCC-L": ["10", "Aggressive", "Hypoxic", "65", "More (-10)", "10", "30-40", "⭐⭐⭐⭐⭐"]
        }
        
        comparison_df = st.dataframe(comparison_data, use_container_width=True)

# ============================================================
# STEP 3: DRUG SELECTION (Conditional)
# ============================================================

if st.session_state.hcc_subtype:
    st.markdown(f"""
    ## Step 3️⃣: Select Therapeutic Drug
    
    Based on **{get_disease_name(st.session_state.hcc_subtype)}** selection
    """)
    
    # Get recommended drugs for this subtype
    drugs = get_recommended_drugs(st.session_state.hcc_subtype)
    
    if drugs:
        drug_choices = {i: drug.drug_name for i, drug in enumerate(drugs)}
        
        selected_drug_idx = st.selectbox(
            "Recommended Drugs for This HCC Subtype",
            options=list(drug_choices.keys()),
            format_func=lambda x: drug_choices[x]
        )
        
        selected_drug = drugs[selected_drug_idx]
        st.session_state.selected_drug = selected_drug
        
        # Display drug info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"### 💊 {selected_drug.drug_name}")
            st.write(f"**Type:** {selected_drug.drug_type}")
            st.write(f"**Mechanism:** {selected_drug.mechanism}")
        
        with col2:
            st.markdown("### 📋 Why This Drug?")
            st.write(selected_drug.reason_for_subtype)
            st.write(f"**Typical Dose:** {selected_drug.typical_dose}")
        
        with col3:
            st.markdown("### 🏥 Clinical Trials")
            if selected_drug.clinical_trials:
                for trial in selected_drug.clinical_trials:
                    st.write(f"✓ {trial}")
    
    # ============================================================
    # SUMMARY & NEXT STEPS
    # ============================================================
    
    st.markdown("---")
    st.markdown("## Summary of Your Selections")
    
    summary_col1, summary_col2 = st.columns(2)
    
    with summary_col1:
        st.markdown(f"""
        ### Your Design Profile
        
        **Cancer Type:** Liver Cancer 🦠
        **Subtype:** {get_disease_name(st.session_state.hcc_subtype)} 
        **Drug:** {st.session_state.selected_drug.drug_name if st.session_state.selected_drug else "Not selected"}
        **Mechanism:** {st.session_state.selected_drug.mechanism if st.session_state.selected_drug else "—"}
        """)
    
    with summary_col2:
        # Show related clinical trials
        trials = get_trials_for_hcc_subtype(st.session_state.hcc_subtype)
        if trials:
            st.markdown(f"### Related Clinical Trials ({len(trials)} available)")
            for trial in trials[:3]:  # Show top 3
                trial_info = format_trial_for_display(trial)
                st.markdown(f"""
                **{trial_info['Trial ID']}:** {trial_info['Trial Name']}
                - Phase: {trial_info['Phase']}
                - Drugs: {trial_info['Drugs']}
                """)
    
    # ============================================================
    # PROCEED TO NEXT STEP
    # ============================================================
    
    st.markdown("---")
    
    if st.button("➡️ Continue to Step 2: Design Parameters", key="continue_to_design"):
        st.success("✅ Proceeding to NP Design Parameters Page...")
        st.info("""
        The next page will show you:
        - Optimized nanoparticle parameters for your cancer subtype
        - Design rationale and tissue barrier information
        - ML model suggestions based on similar past designs
        - Start the AI Co-Designer with these pre-filled constraints
        """)
        # Note: In production, use st.switch_page() or navigation

# ============================================================
# FOOTER / ADDITIONAL INFO
# ============================================================

st.markdown("---")

with st.expander("📚 Learn More About HCC Subtypes"):
    st.markdown("""
    ### Why Do HCC Subtypes Matter?
    
    **Gene Expression Profiling** revealed that HCC has distinct molecular subtypes:
    
    - **HCC-S (Subclass S):** 
      - Well-differentiated, better prognosis
      - Proliferative signatures present
      - Better respond to older-generation kinase inhibitors
    
    - **HCC-MS (Mixed Subclass):**
      - Intermediate characteristics
      - Variable gene expression patterns
      - May benefit from combination therapy
    
    - **HCC-L (Proliferative/Poor prognosis):**
      - Poorly differentiated, aggressive
      - TP53 mutations common
      - Worse vascularization (hypoxia)
      - Requires multi-drug approaches
    
    **For NP Design:** Each subtype's unique microenvironment requires different 
    particle sizes, surface modifications, and drug combinations.
    """)

with st.expander("💡 Design Tips"):
    st.markdown("""
    ### Key Considerations for HCC-L (Aggressive):
    
    1. **Particle Size is CRITICAL**
       - Hypoxic tumors have dense stroma
       - Smaller particles (50-80nm) penetrate better
       - But too small → renal clearance
    
    2. **Surface Modifications**
       - More PEG coating needed (10%)
       - Negative surface charge helps ECM penetration
       - Consider peptide targeting in addition to ASGPR
    
    3. **Drug Loading Strategy**
       - Higher loading (30-40%) needed
       - Faster degradation in hostile environment
       - Consider combination therapy (chemo + immunotherapy)
    
    4. **Clinical Evidence**
       - IMbrave150 (Atezolizumab + Bevacizumab) FDA approved
       - Particularly good for advanced HCC including HCC-L
       - NP delivery could enhance synergy
    """)
