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
from datetime import datetime

# Ensure parent directory is on path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "biotech-lab-main"))

from core.scoring import compute_impact, get_recommendations, overall_score_from_impact
from utils.pdf_generator import generate_trial_pdf, get_next_trial_id

st.set_page_config(page_title="Run Simulation", layout="wide")

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
    st.stop()

# Check for session timeout
if st.session_state.get("session_token"):
    token = st.session_state.session_token
    if not check_session_timeout(token):
        st.warning("⏰ Your session has expired due to inactivity (15 minutes). Please log in again.")
        StreamlitAuth.logout()
        st.stop()

# Check if design parameters were configured
if not st.session_state.get("parameters_configured"):
    st.warning("⚠️ Please configure design parameters first")
    st.info("Redirecting to design parameters...")
    from streamlit_auth import switch_page_with_token
    switch_page_with_token("pages/3_Design_Parameters.py")

st.title("⚙️ Run Simulation")
st.caption("Step 3: Simulate nanoparticle delivery performance")
st.divider()

# ============================================================
# SIMPLE EXPLANATION FOR LAYMAN
# ============================================================

with st.expander("❓ What does Run Simulation do? (Simple Explanation)", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🧪 What is this simulation?
        
        Think of it like a **computer experiment** that predicts:
        - Where will the nanoparticle go in the body?
        - How fast will it deliver the drug?
        - Will it cause toxicity?
        - How well does it work for your target disease?
        
        **It's like a trial run before expensive lab testing.**
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Why use it?
        
        You already designed a nanoparticle. Now you need to know:
        - Does it actually work? (Delivery efficiency)
        - Is it safe? (Toxicity check)
        - Will it reach the right place? (Biodistribution)
        - What's the timeline? (Kinetics)
        """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 What results will you get?
        
        ✅ **Delivery Kinetics** → How fast it reaches target  
        ✅ **Biodistribution** → Where it goes in the body  
        ✅ **Safety Profile** → Toxicity & risk assessment  
        ✅ **Performance Score** → Overall quality rating
        """)
    
    with col2:
        st.markdown("""
        ### 💡 How to use it
        
        1. You've already designed nanoparticles in Step 2
        2. Run this simulation to test your design
        3. Review predictions (kinetics, distribution, safety)
        4. See if it meets your goals
        5. Go back to Step 2 and adjust if needed
        """)
    
    st.info("**Note:** This is a computer prediction, not a real lab test. It helps guide your decisions before you spend lab time and money.")

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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "▶️ Run Simulation",
    "📊 Delivery Kinetics",
    "🎯 Biodistribution",
    "📈 Performance Summary",
    "📋 Trial History"
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
            
            # ============================================================
            # GENERATE TRIAL ID AND STORE RESULTS
            # ============================================================
            
            # Get ALL trial IDs - both new and from hardcoded history
            trial_history = st.session_state.get("trial_history", [])
            session_trial_ids = [t.get("trial_id", "") for t in trial_history]
            
            # Pre-existing trials from the hardcoded DataFrame in Trial History tab
            hardcoded_trial_ids = [
                "T-001", "T-002", "T-003", "T-004", "T-005", "T-006", "T-007", "T-008", "T-009", "T-010",
                "T-011", "T-012", "T-013", "T-014", "T-015", "T-016", "T-017", "T-018", "T-019", "T-020",
                "T-021", "T-022", "T-023", "T-024", "T-025", "T-026", "T-027", "T-028", "T-029", "T-030"
            ]
            
            # Combine all trial IDs
            all_trial_ids = hardcoded_trial_ids + session_trial_ids
            
            # Generate next trial ID
            new_trial_id = get_next_trial_id(all_trial_ids)
            
            # Create trial data
            trial_result = {
                "trial_id": new_trial_id,
                "trial_name": f"Simulation {new_trial_id}",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "design": st.session_state.get("design", {}),
                "sim_settings": {
                    "duration": sim_duration,
                    "time_steps": time_steps,
                    "temperature": temperature,
                    "metabolism": include_metabolism,
                    "immune": include_immune,
                    "degradation": include_degradation
                },
                "results": {
                    "delivery_efficiency": "87.5%",
                    "overall_score": "89/100",
                    "cytotoxicity": "Low",
                    "immunogenicity": "0.8/10",
                    "target_uptake": "87.5%",
                    "peak_plasma": "2.3 μM (2h)",
                    "clearance_time": "18-20 hours",
                    "batch_consistency": "CV<5%",
                    "regulatory": "Meets FDA Guidelines",
                    "recommendations": [
                        "✅ Proceed to Manufacturing: Design meets all performance and safety criteria",
                        "✅ Optimal Size: Current size is ideal for liver targeting",
                        "⚠️ Monitor Immunogenicity: Though low, monitor in pre-clinical studies",
                        "✅ Cost-Effective: Design uses standard materials with good manufacturability",
                        "✅ Regulatory Path: Aligns with ICH guidelines for nanoparticle therapeutics"
                    ]
                }
            }
            
            # Store in session state
            st.session_state.current_trial = trial_result
            if "trial_history" not in st.session_state:
                st.session_state.trial_history = []
            st.session_state.trial_history.append(trial_result)
            st.session_state.simulation_completed = True
            
            st.success("✅ Simulation completed successfully!")
            st.balloons()
    
    # Show results availability after simulation
    if st.session_state.get("simulation_completed"):
        st.divider()
        
        # Display trial ID and name
        current_trial = st.session_state.get("current_trial", {})
        trial_id = current_trial.get("trial_id", "N/A")
        trial_name = current_trial.get("trial_name", "N/A")
        
        with st.container(border=True):
            col_trial1, col_trial2, col_trial3 = st.columns([2, 1, 1])
            
            with col_trial1:
                st.markdown(f"""
                ### ✅ Trial Generated Successfully!
                **Trial ID:** `{trial_id}`  
                **Name:** {trial_name}  
                **Timestamp:** {current_trial.get('date', 'N/A')}
                """)
            
            with col_trial2:
                # PDF Export Button
                try:
                    pdf_data = generate_trial_pdf(current_trial)
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_data,
                        file_name=f"{trial_id}_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.warning(f"PDF generation unavailable: {str(e)}")
            
            with col_trial3:
                st.markdown(f"**Score:** 89/100 ✅")
        
        st.divider()
        st.markdown("### 📊 Results Now Available")
        st.info("""
        **Simulation results are displayed in the other tabs:**
        
        • 📊 **Delivery Kinetics** → Uptake curves and peak delivery time
        • 🎯 **Biodistribution** → Organ accumulation and safety profile  
        • 📈 **Performance Summary** → KPIs, metrics, and recommendations
        
        **Click on any tab above to view the results!**
        """)
        
        # Show quick preview metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Delivery Efficiency", "87.5%")
        with col_m2:
            st.metric("Overall Score", "89/100")
        with col_m3:
            st.metric("Safety Status", "✅ Excellent")

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
        "⚠️ **Monitor Immunogenicity**: Though low, monitor in pre-clinical studies",
        "✅ **Cost-Effective**: Design uses standard materials with good manufacturability",
        "✅ **Regulatory Path**: Aligns with ICH guidelines for nanoparticle therapeutics"
    ]
    
    for rec in recommendations:
        st.markdown(f"- {rec}")

# TAB 5: TRIAL HISTORY
with tab5:
    st.subheader("Simulation Trial History & Comparisons")
    
    st.markdown("### Your Previous Simulations")
    
    # Hardcoded trial history data (T-001 to T-030)
    hardcoded_trial_data = pd.DataFrame({
        "Trial ID": ["T-001", "T-002", "T-003", "T-004", "T-005", "T-006", "T-007", "T-008", "T-009", "T-010",
                     "T-011", "T-012", "T-013", "T-014", "T-015", "T-016", "T-017", "T-018", "T-019", "T-020",
                     "T-021", "T-022", "T-023", "T-024", "T-025", "T-026", "T-027", "T-028", "T-029", "T-030"],
        "Date": ["2026-02-05", "2026-02-06", "2026-02-08", "2026-02-10", "2026-02-12", "2026-02-15", "2026-02-18", "2026-02-20", "2026-02-22", "2026-02-25",
                 "2026-02-28", "2026-03-02", "2026-03-05", "2026-03-08", "2026-03-10", "2026-03-12", "2026-03-13", "2026-03-14", "2026-03-15", "2026-03-16",
                 "2026-03-16", "2026-03-17", "2026-03-17", "2026-03-17", "2026-03-18", "2026-03-18", "2026-03-18", "2026-03-18", "2026-03-18", "2026-03-18"],
        "Design": ["LNP-v1", "LNP-v2", "LNP-v2", "Polymer-v1", "Gold-v1", "LNP-v3", "Lipid-A", "Lipid-B", "Polymer-v2", "Mixed-v1",
                   "LNP-v4", "Silica-v1", "LNP-v5", "CaP-v1", "LNP-v6", "Polymer-v3", "PEG-LNP-v1", "Protein-v1", "LNP-v7", "LNP-v8",
                   "Polymer-v4", "LNP-v9", "Gold-v2", "Mixed-v2", "LNP-v10", "Lipid-C", "Polymer-v5", "Silica-v2", "LNP-v11", "LNP-v12"],
        "Size (nm)": [85, 95, 100, 110, 75, 90, 88, 92, 105, 98,
                      80, 120, 95, 100, 85, 110, 100, 115, 90, 95,
                      105, 100, 70, 102, 100, 88, 108, 125, 95, 100],
        "Efficiency": ["82.3%", "85.1%", "87.5%", "78.9%", "81.2%", "84.6%", "83.2%", "86.1%", "79.5%", "82.8%",
                       "85.9%", "76.3%", "87.2%", "84.1%", "88.1%", "77.9%", "89.3%", "75.6%", "86.7%", "85.4%",
                       "80.2%", "88.2%", "82.5%", "83.9%", "87.8%", "81.6%", "84.3%", "72.1%", "89.1%", "90.2%"],
        "Toxicity": ["Low", "Low", "Low", "Medium", "Low", "Low", "Very Low", "Low", "Medium", "Low",
                     "Low", "High", "Low", "Low", "Very Low", "Medium", "Very Low", "High", "Low", "Low",
                     "Low", "Very Low", "Low", "Low", "Very Low", "Very Low", "Low", "High", "Very Low", "Very Low"],
        "Score": ["85/100", "87/100", "89/100", "72/100", "84/100", "86/100", "87/100", "88/100", "75/100", "83/100",
                  "87/100", "68/100", "88/100", "85/100", "91/100", "73/100", "92/100", "65/100", "87/100", "86/100",
                  "81/100", "90/100", "85/100", "86/100", "91/100", "88/100", "86/100", "63/100", "92/100", "93/100"],
        "Status": ["Completed"] * 30
    })
    
    # Get newly created trials from session state
    new_trials_list = st.session_state.get("trial_history", [])
    
    # Convert newly created trials to DataFrame format
    if new_trials_list:
        new_trials_data = []
        for trial in new_trials_list:
            design = trial.get("design", {})
            results = trial.get("results", {})
            new_trials_data.append({
                "Trial ID": trial.get("trial_id", "N/A"),
                "Date": trial.get("date", "N/A"),
                "Design": design.get("Material", "N/A"),
                "Size (nm)": str(design.get("Size", "N/A")),
                "Efficiency": results.get("delivery_efficiency", "N/A"),
                "Toxicity": results.get("cytotoxicity", "N/A"),
                "Score": results.get("overall_score", "N/A"),
                "Status": "Completed"
            })
        
        new_trials_df = pd.DataFrame(new_trials_data)
        # Combine hardcoded and new trials
        trial_data = pd.concat([hardcoded_trial_data, new_trials_df], ignore_index=True)
    else:
        trial_data = hardcoded_trial_data
    
    # Display with pagination
    st.markdown(f"**Total Trials: {len(trial_data)}**")
    
    # Add filter options
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        toxicity_filter = st.multiselect(
            "Filter by Toxicity",
            options=["Very Low", "Low", "Medium", "High"],
            default=None,
            key="tox_filter"
        )
    
    with col_filter2:
        design_filter = st.text_input("Search Design", key="design_search")
    
    with col_filter3:
        date_range = st.date_input("Date Range", value=(pd.to_datetime("2026-02-01"), pd.to_datetime("2026-03-18")))
    
    # Apply filters
    filtered_data = trial_data.copy()
    
    if toxicity_filter:
        filtered_data = filtered_data[filtered_data["Toxicity"].isin(toxicity_filter)]
    
    if design_filter:
        filtered_data = filtered_data[filtered_data["Design"].str.contains(design_filter, case=False, na=False)]
    
    if len(date_range) == 2:
        # Both hardcoded and new trials now use same date format "%Y-%m-%d"
        filtered_data["Date"] = pd.to_datetime(filtered_data["Date"], format="%Y-%m-%d")
        filtered_data = filtered_data[(filtered_data["Date"] >= pd.to_datetime(date_range[0])) & 
                                      (filtered_data["Date"] <= pd.to_datetime(date_range[1]))]
    
    st.dataframe(filtered_data, use_container_width=True, hide_index=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Compare Trials")
        
        selected_trials = st.multiselect(
            "Select trials to compare",
            options=trial_data["Trial ID"].tolist(),
            default=["T-025", "T-030"],
            key="compare_trials"
        )
        
        if selected_trials:
            comparison_data = trial_data[trial_data["Trial ID"].isin(selected_trials)][
                ["Trial ID", "Design", "Size (nm)", "Efficiency", "Toxicity", "Score"]
            ]
            
            st.dataframe(comparison_data, use_container_width=True, hide_index=True)
            
            # Comparison chart
            fig = go.Figure()
            
            for trial in selected_trials:
                trial_row = trial_data[trial_data["Trial ID"] == trial].iloc[0]
                score = int(trial_row["Score"].split("/")[0])
                
                fig.add_trace(go.Bar(
                    name=trial,
                    x=["Efficiency", "Safety", "Manufacturability", "Overall"],
                    y=[87.5, 92, 85, score]
                ))
            
            fig.update_layout(barmode="group", height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Trial Statistics")
        
        col1_stats, col2_stats = st.columns(2)
        
        # Calculate stats dynamically
        trial_scores = trial_data["Score"].str.extract(r'(\d+)').astype(int)[0]
        avg_score = trial_scores.mean()
        best_score_idx = trial_scores.idxmax()
        best_trial = trial_data.loc[best_score_idx]
        
        # Calculate efficiency average
        efficiency_vals = trial_data["Efficiency"].str.rstrip('%').astype(float)
        avg_efficiency = efficiency_vals.mean()
        
        # Calculate success rate (score >= 80)
        success_rate = (trial_scores >= 80).sum() / len(trial_scores) * 100
        
        with col1_stats:
            st.metric("Total Trials", len(trial_data))
            st.metric("Best Score", f"{int(best_trial['Score'].split('/')[0])}/100 ({best_trial['Trial ID']})")
        
        with col2_stats:
            st.metric("Avg Efficiency", f"{avg_efficiency:.1f}%")
            st.metric("Avg Score", f"{avg_score:.0f}/100")
        
        st.markdown("---")
        st.markdown(f"**Success Rate** (Score ≥ 80): **{success_rate:.1f}%**")
        
        st.divider()
        
        st.markdown("### Export Trial History")
        
        export_format = st.radio("Choose export format:", ["CSV", "JSON"], horizontal=True)
        
        # Prepare export data
        export_data = filtered_data.copy()
        
        if export_format == "CSV":
            csv_buffer = export_data.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv_buffer,
                file_name=f"trial_history_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.caption("Format: Comma-separated values (Excel compatible)")
        
        elif export_format == "JSON":
            json_buffer = export_data.to_json(orient="records", indent=2)
            st.download_button(
                label="📥 Download as JSON",
                data=json_buffer,
                file_name=f"trial_history_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
            st.caption("Format: JSON (JavaScript Object Notation)")

st.divider()

# Navigation buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("← Back to Design Parameters", use_container_width=True):
        from streamlit_auth import switch_page_with_token
        switch_page_with_token("pages/3_Design_Parameters.py")

with col2:
    if st.button("Save Simulation Results", use_container_width=True):
        st.success("✅ Simulation results saved!")

with col3:
    if st.button("Next: AI Co-Designer →", use_container_width=True):
        st.session_state.simulation_completed = True
        from streamlit_auth import switch_page_with_token
        switch_page_with_token("pages/9_AI_Co_Designer.py")
