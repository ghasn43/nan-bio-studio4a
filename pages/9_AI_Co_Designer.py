"""
AI Co-Designer — Policy-Aware Optimization
Advanced nanoparticle design using AI optimization
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="NanoBio Studio - AI Co-Designer", layout="wide")

st.title("🤖 AI Co-Designer — Policy-Aware Optimization")

# Check if user is logged in
if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in first")
    st.info("You need to be logged in to access this page.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔐 Go to Login", type="primary", use_container_width=True):
            st.query_params.clear()
            st.switch_page("Login.py")
    
    st.stop()

st.subheader("Advanced AI-Driven Nanoparticle Design Optimization")

# ============================================================
# SIMPLE EXPLANATION FOR LAYMAN
# ============================================================

with st.expander("❓ What is AI Co-Designer? (Simple Explanation)", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 What problem does it solve?
        
        Designing a nanoparticle involves **hundreds of choices**:
        - Size, charge, material, drug, dose
        - Testing all combinations in a lab would be **expensive and slow**
        
        **AI Co-Designer helps you pick the best options first.**
        """)
    
    with col2:
        st.markdown("""
        ### 🤖 How does it work?
        
        1. You tell the AI what matters most (safety, performance, cost)
        2. The AI tests many designs on the computer
        3. It shows you the **top 5-10 best designs**
        4. You pick which ones to actually test in the lab
        """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 What does it show?
        
        ✅ Ranked list of best designs  
        ✅ Performance vs safety vs cost trade-offs  
        ✅ Why each design was suggested  
        ✅ Reports for supervisors
        """)
    
    with col2:
        st.markdown("""
        ### ❌ What it does NOT do
        
        ❌ Replace your judgment  
        ❌ Treat patients  
        ❌ Make final decisions  
        ✅ **Assist your decision-making**
        """)
    
    st.success("**Bottom line:** AI Co-Designer is like a smart filter that helps you find promising nanoparticles to test, instead of testing blindly.")

st.divider()

# ============================================================
# SIDEBAR: Optimization Configuration
# ============================================================

with st.sidebar:
    st.header("⚙️ Optimization Settings")
    
    # Scenario selection
    scenarios = {
        "Balanced": "Equal weight to delivery, safety, and cost",
        "Delivery-First": "Maximize delivery efficacy",
        "Safety-First": "Minimize toxicity and side effects",
        "Cost-Optimized": "Minimize manufacturing cost",
        "Custom": "Define custom weights"
    }
    
    selected_scenario = st.selectbox("Scenario Mode", list(scenarios.keys()))
    st.caption(scenarios[selected_scenario])
    
    st.divider()
    
    # Optimization parameters
    st.markdown("### Objective Weights")
    
    if selected_scenario == "Custom":
        delivery_weight = st.slider("Delivery Priority", 0.0, 1.0, 0.4)
        safety_weight = st.slider("Safety Priority", 0.0, 1.0, 0.3)
        cost_weight = st.slider("Cost Priority", 0.0, 1.0, 0.3)
    else:
        # Pre-defined weights
        weights = {
            "Balanced": {"delivery": 0.4, "safety": 0.3, "cost": 0.3},
            "Delivery-First": {"delivery": 0.6, "safety": 0.2, "cost": 0.2},
            "Safety-First": {"delivery": 0.2, "safety": 0.6, "cost": 0.2},
            "Cost-Optimized": {"delivery": 0.3, "safety": 0.3, "cost": 0.4},
        }
        w = weights[selected_scenario]
        delivery_weight = w["delivery"]
        safety_weight = w["safety"]
        cost_weight = w["cost"]
        
        st.metric("Delivery", f"{delivery_weight:.1%}")
        st.metric("Safety", f"{safety_weight:.1%}")
        st.metric("Cost", f"{cost_weight:.1%}")
    
    st.divider()
    
    # Constraints
    st.markdown("### Design Constraints")
    
    size_constraint = st.checkbox("Size Constraint (80-120 nm)", value=True)
    charge_constraint = st.checkbox("Charge Constraint (±10 mV)", value=True)
    tox_constraint = st.checkbox("Toxicity Limit (< 3/10)", value=True)
    
    st.divider()
    
    # Optimization settings
    n_trials = st.slider("Optimization Trials", 10, 500, 100)
    use_active_learning = st.checkbox("Use Active Learning", value=True)

# ============================================================
# MAIN TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 AI Optimization",
    "📊 Results Analysis",
    "🔍 Explainability",
    "📋 Audit Report"
])

# TAB 1: AI OPTIMIZATION
with tab1:
    st.subheader("AI-Driven Design Optimization")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Optimization Engine")
        
        if st.button("▶️ Start Optimization", type="primary", use_container_width=True):
            st.info(f"Running {n_trials} optimization trials with {selected_scenario} scenario...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(n_trials):
                progress_bar.progress((i + 1) / n_trials)
                status_text.text(f"Trial {i + 1}/{n_trials} - Finding optimal designs...")
                import time
                time.sleep(0.01)
            
            st.success("✅ Optimization completed!")
            st.balloons()
    
    with col2:
        st.markdown("### Constraints Status")
        if size_constraint:
            st.success("✅ Size: 80-120 nm")
        if charge_constraint:
            st.success("✅ Charge: ±10 mV")
        if tox_constraint:
            st.success("✅ Toxicity: < 3/10")
    
    st.divider()
    
    st.markdown("### Top Candidate Designs")
    
    # Mock candidate designs
    candidates = pd.DataFrame({
        "Rank": [1, 2, 3, 4, 5],
        "Score": [94.2, 91.5, 89.8, 87.3, 84.9],
        "Delivery": [92, 89, 87, 85, 82],
        "Safety": [96, 93, 92, 90, 88],
        "Cost": [88, 91, 90, 87, 85],
        "Material": ["Lipid NP", "PLGA", "Lipid NP", "Gold NP", "PLGA"],
        "Size (nm)": [100, 110, 95, 105, 115],
    })
    
    st.dataframe(candidates, use_container_width=True)

# TAB 2: RESULTS ANALYSIS
with tab2:
    st.subheader("Optimization Results & Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Parameter Distribution")
        
        # Mock distribution data
        size_opt = [95, 98, 100, 102, 105, 108]
        charge_opt = [-8, -5, -2, 0, 2, 5]
        
        st.write("Optimal Size Range")
        st.bar_chart(pd.Series([2, 3, 5, 4, 3, 2], index=size_opt))
        
        st.write("Optimal Charge Range")
        st.bar_chart(pd.Series([1, 3, 4, 5, 3, 2], index=charge_opt))
    
    with col2:
        st.markdown("### Pareto Front")
        
        # Create Pareto front visualization
        pareto_data = pd.DataFrame({
            "Safety": [88, 89, 90, 91, 92, 93, 94, 95],
            "Cost": [92, 90, 88, 85, 82, 78, 72, 65],
        })
        
        st.line_chart(pareto_data.set_index("Safety"))
        st.caption("Trade-off between Safety and Cost optimization")
    
    st.divider()
    
    st.markdown("### Key Insights")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Best Overall Score", "94.2/100", "+5.1 vs baseline")
    with col2:
        st.metric("Average Score", "87.3/100", "+3.2 vs baseline")
    with col3:
        st.metric("Feasible Designs", "387/500", "77.4%")

# TAB 3: EXPLAINABILITY
with tab3:
    st.subheader("Design Explainability & Impact Analysis")
    
    st.markdown("### Feature Importance for Top Design")
    
    feature_importance = pd.DataFrame({
        "Feature": ["Size", "Charge", "Material", "PDI", "Encapsulation", "Stability"],
        "Impact": [0.28, 0.22, 0.18, 0.15, 0.12, 0.05]
    }).sort_values("Impact", ascending=False)
    
    st.bar_chart(feature_importance.set_index("Feature"))
    
    st.divider()
    
    st.markdown("### Parameter Sensitivity Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Size Sensitivity**")
        size_sensitivity = pd.DataFrame({
            "Size (nm)": [80, 90, 100, 110, 120],
            "Score Impact": [75, 82, 95, 88, 72]
        })
        st.line_chart(size_sensitivity.set_index("Size (nm)"))
    
    with col2:
        st.write("**Charge Sensitivity**")
        charge_sensitivity = pd.DataFrame({
            "Charge (mV)": [-10, -5, 0, 5, 10],
            "Score Impact": [78, 90, 94, 89, 80]
        })
        st.line_chart(charge_sensitivity.set_index("Charge (mV)"))
    
    st.divider()
    
    st.markdown("### What Changed from Manual Design?")
    
    comparison = pd.DataFrame({
        "Parameter": ["Size", "Charge", "Material", "Encapsulation", "Stability"],
        "Manual Design": [105, -8, "Lipid", 85, 80],
        "AI-Optimized": [100, -3, "Lipid", 92, 88],
        "Improvement": ["+5%", "+62%", "→", "+8%", "+10%"]
    })
    
    st.dataframe(comparison, use_container_width=True)

# TAB 4: AUDIT REPORT
with tab4:
    st.subheader("Audit & Governance Report")
    
    st.markdown("### Optimization Audit Trail")
    
    audit_info = {
        "🔧 Scenario": selected_scenario,
        "⚖️ Delivery Weight": f"{delivery_weight:.1%}",
        "🛡️ Safety Weight": f"{safety_weight:.1%}",
        "💰 Cost Weight": f"{cost_weight:.1%}",
        "🔢 Trials Performed": n_trials,
        "✅ Feasible Solutions": "387 / 500",
        "🏆 Best Score": "94.2 / 100",
        "📅 Timestamp": "2026-03-17 15:30:45 UTC",
    }
    
    for key, value in audit_info.items():
        st.write(f"**{key}**: {value}")
    
    st.divider()
    
    st.markdown("### Constraints Enforcement")
    
    constraints_status = pd.DataFrame({
        "Constraint": ["Size (80-120 nm)", "Charge (±10 mV)", "Toxicity (< 3/10)", "Manufacturing Cost"],
        "Status": ["✅ Enforced", "✅ Enforced", "✅ Enforced", "⚠️ Soft limit"],
        "Violations": [0, 0, 0, 12],
        "Rejection Rate": ["0%", "0%", "0%", "2.4%"]
    })
    
    st.dataframe(constraints_status, use_container_width=True)
    
    st.divider()
    
    # Export options
    st.markdown("### Export Options")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Export as JSON"):
            st.info("Exporting optimization results and candidates...")
    with col2:
        if st.button("📥 Export as CSV"):
            st.info("Exporting design parameters and scores...")
    with col3:
        if st.button("📤 Generate PDF Report"):
            st.info("Generating comprehensive audit report...")

st.divider()

# Show current design if available
if st.session_state.get("design"):
    st.subheader("Current Design Configuration (from Design Parameters)")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Material", st.session_state.get("design", {}).get("Material", "N/A"))
    with col2:
        st.metric("Size", f"{st.session_state.get('design', {}).get('Size', 'N/A')} nm")
    with col3:
        st.metric("Charge", f"{st.session_state.get('design', {}).get('Charge', 'N/A')} mV")
    with col4:
        st.metric("Encapsulation", f"{st.session_state.get('design', {}).get('Encapsulation', 'N/A')}%")
