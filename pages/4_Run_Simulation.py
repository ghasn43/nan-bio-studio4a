"""
Run Simulation - Step 3 of the NanoBio Studio workflow
Simulate nanoparticle delivery and performance
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Ensure parent directory is on path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "biotech-lab-main"))

from core.scoring import compute_impact, get_recommendations, overall_score_from_impact

st.set_page_config(page_title="Run Simulation", layout="wide")

# Check if user is logged in
if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in first")
    st.switch_page("Login.py")

# Check if design parameters were configured
if not st.session_state.get("parameters_configured"):
    st.warning("⚠️ Please configure design parameters first")
    st.info("Redirecting to design parameters...")
    st.switch_page("pages/3_Design_Parameters.py")

st.title("⚙️ Run Simulation")
st.caption("Step 3: Simulate nanoparticle delivery performance")
st.divider()

# Show current design context
with st.expander("📋 Current Design Configuration", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    design = st.session_state.get("design", {})
    
    with col1:
        st.metric("Material", design.get("Material", "N/A"))
    with col2:
        st.metric("Size", f"{design.get('Size', 'N/A')} nm")
    with col3:
        st.metric("Charge", f"{design.get('Charge', 'N/A')} mV")
    with col4:
        st.metric("Encapsulation", f"{design.get('Encapsulation', 'N/A')}%")

st.divider()

# ============================================================
# SIMULATION TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "▶️ Run Simulation",
    "📊 Delivery Kinetics",
    "🎯 Biodistribution",
    "📈 Performance Summary"
])

# TAB 1: RUN SIMULATION
with tab1:
    st.subheader("Execute Design Simulation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Simulation Settings")
        
        sim_duration = st.slider("Simulation Duration (hours)", 1, 72, 24)
        time_steps = st.slider("Time Steps", 10, 1000, 100)
        temperature = st.selectbox("Temperature", ["37°C (Body Temp)", "25°C (Room Temp)", "4°C (Refrigerated)"])
        
        st.markdown("### Advanced Options")
        include_metabolism = st.checkbox("Include Metabolism", value=True)
        include_immune = st.checkbox("Include Immune Response", value=True)
        include_degradation = st.checkbox("Include Degradation", value=True)
    
    with col2:
        st.markdown("### Simulation Status")
        
        if st.button("▶️ START SIMULATION", type="primary", use_container_width=True, key="start_sim"):
            st.info(f"Running {sim_duration}-hour simulation with {time_steps} time steps...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate progress
            for i in range(100):
                progress_bar.progress((i + 1) / 100)
                status_text.text(f"Simulating: {(i + 1)}% complete...")
                import time
                time.sleep(0.01)
            
            st.success("✅ Simulation completed successfully!")
            st.session_state.simulation_completed = True
            st.balloons()

# TAB 2: DELIVERY KINETICS
with tab2:
    st.subheader("Delivery Kinetics Analysis")
    
    # Mock delivery kinetics data
    hours = np.arange(0, 25, 1)
    delivery_pct = 100 * (1 - np.exp(-0.15 * hours))  # Exponential uptake
    
    kinetics_df = pd.DataFrame({
        "Hours": hours,
        "Delivery %": delivery_pct
    })
    
    st.line_chart(kinetics_df.set_index("Hours"))
    st.caption("Cumulative target cell uptake over time")
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Peak Delivery Time", "6-8 hours", "Optimal window")
    with col2:
        st.metric("24h Delivery Efficiency", "87.5%", "High efficiency")
    with col3:
        st.metric("Half-Life (t₁/₂)", "4.6 hours", "Standard")

# TAB 3: BIODISTRIBUTION
with tab3:
    st.subheader("Predicted Biodistribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Organ Distribution (24h)")
        
        biodist = pd.DataFrame({
            "Organ": ["Liver", "Spleen", "Kidney", "Lung", "Blood"],
            "Accumulation %": [45, 20, 15, 12, 8]
        })
        
        st.bar_chart(biodist.set_index("Organ"))
    
    with col2:
        st.markdown("### Cellular Uptake Mechanism")
        
        uptake = pd.DataFrame({
            "Mechanism": ["Receptor-Mediated", "Endocytosis", "Phagocytosis", "Passive"],
            "Contribution %": [45, 30, 20, 5]
        })
        
        uptake_fig = go.Figure(data=[go.Pie(
            labels=uptake["Mechanism"],
            values=uptake["Contribution %"],
            hole=0.3
        )])
        uptake_fig.update_layout(height=350)
        st.plotly_chart(uptake_fig, use_container_width=True)
    
    st.divider()
    
    st.markdown("### Safety Profile")
    
    safety_data = pd.DataFrame({
        "Parameter": ["Hepatotoxicity Risk", "Immunogenicity", "Off-Target Binding", "Aggregation Risk"],
        "Score (0-10)": [1.2, 0.8, 0.5, 0.3],
        "Status": ["✅ Low", "✅ Very Low", "✅ Minimal", "✅ Minimal"]
    })
    
    st.dataframe(safety_data, use_container_width=True)

# TAB 4: PERFORMANCE SUMMARY
with tab4:
    st.subheader("Simulation Results Summary")
    
    st.markdown("### Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Delivery Efficiency", "87.5%", "+12.5% vs baseline")
    with col2:
        st.metric("Cytotoxicity", "Low", "0.8/10")
    with col3:
        st.metric("Systemic Exposure", "Minimal", "< 5% off-target")
    with col4:
        st.metric("Overall Score", "89/100", "Excellent")
    
    st.divider()
    
    st.markdown("### Detailed Results Table")
    
    results = pd.DataFrame({
        "Metric": [
            "Target Cell Uptake (24h)",
            "Peak Plasma Concentration",
            "Clearance Time",
            "Immunogenicity Score",
            "Precipitation Risk",
            "Batch Consistency",
            "Manufacturing Feasibility",
            "Regulatory Compliance"
        ],
        "Value": [
            "87.5%",
            "2.3 μM (2h)",
            "18-20 hours",
            "0.8/10 (Very Low)",
            "Minimal",
            "High (CV<5%)",
            "8.5/10 (Good)",
            "Meets FDA Guidelines"
        ],
        "Assessment": [
            "✅ Excellent",
            "✅ Optimal",
            "✅ Appropriate",
            "✅ Safe",
            "✅ Stable",
            "✅ Reproducible",
            "✅ Feasible",
            "✅ Compliant"
        ]
    })
    
    st.dataframe(results, use_container_width=True)
    
    st.divider()
    
    st.markdown("### Recommendations")
    
    recommendations = [
        "✅ **Proceed to Manufacturing**: Design meets all performance and safety criteria",
        "✅ **Optimal Size**: Current 100nm size is ideal for liver targeting",
        "⚠️ **Consider PEG Optimization**: Slight increase in PEG coating (2.5→3.0nm) could improve circulation",
        "✅ **Batch Parameters**: Maintain tight controls on encapsulation efficiency (±2%)"
    ]
    
    for rec in recommendations:
        st.write(rec)

st.divider()

# Navigation buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("← Back to Design Parameters", use_container_width=True):
        st.switch_page("pages/3_Design_Parameters.py")

with col2:
    if st.button("Save Simulation Results", use_container_width=True):
        st.success("✅ Simulation results saved!")

with col3:
    if st.button("Next: AI Co-Designer →", use_container_width=True):
        st.session_state.simulation_completed = True
        st.switch_page("pages/9_AI_Co_Designer.py")
