"""
Design Parameters - Step 2 of the NanoBio Studio workflow
Configure nanoparticle design parameters with real-time scoring
"""
import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go

# Ensure parent directory is on path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "biotech-lab-main"))

from core.scoring import compute_impact, get_recommendations, overall_score_from_impact

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

# Initialize design dictionary in session state
if "design" not in st.session_state:
    st.session_state.design = {
        "Material": "Lipid NP",
        "Target": "Liver Cells",
        "Size": 100,
        "PDI": 0.15,
        "HydrodynamicSize": 120,
        "Encapsulation": 85,
        "Charge": -5,
        "SurfaceArea": 250,
        "Stability": 85,
        "DegradationTime": 30,
        "CrystallinityIndex": 65,
        "PorosityLevel": "Mesoporous (2-50nm)",
        "PoreSize": 5.0,
        "SurfaceCoating": ["PEG (Stealth)"],
        "CoatingThickness": 2.5,
        "FunctionalGroups": ["-COOH (Carboxyl)"],
        "Hydrophobicity": 1.5,
        "Ligand": "GalNAc",
        "LigandDensity": 60,
        "Receptor": "ASGPR",
        "ReceptorBinding": 10.0,
        "ReleaseProfile": "Sustained (1 week)",
        "ReleasePredictability": 85,
    }

d = st.session_state.design

st.title("🎨 Design Parameters")
st.caption("Step 2: Configure nanoparticle design parameters")
st.divider()

# Show disease selection context
context_col1, context_col2 = st.columns(2)
with context_col1:
    st.info(f"""
    **Disease:** {st.session_state.get('selected_disease', 'Not selected')}
    
    **Drug:** {st.session_state.get('selected_drug', 'Not selected')}
    """)

with context_col2:
    st.info(f"""
    **HCC Subtype:** {st.session_state.get('hcc_subtype', 'N/A')}
    """)

st.divider()

# ============================================================
# TABS FOR DIFFERENT PARAMETER GROUPS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(["🧬 Core Properties", "🎨 Surface & Chemistry", "🎯 Targeting", "📊 Scoring"])

# TAB 1: CORE PROPERTIES
with tab1:
    st.subheader("🧬 Core Material Properties")
    
    material_properties = {
        "Lipid NP": {"biodegradation": 7, "cost_base": 50, "density": 0.95},
        "PLGA": {"biodegradation": 30, "cost_base": 40, "density": 1.22},
        "Gold NP": {"biodegradation": 180, "cost_base": 80, "density": 19.3},
        "Silica NP": {"biodegradation": 365, "cost_base": 30, "density": 2.2},
        "DNA Origami": {"biodegradation": 1, "cost_base": 120, "density": 1.65},
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        d["Material"] = st.selectbox(
            "Select Material",
            list(material_properties.keys()),
            index=list(material_properties.keys()).index(d.get("Material", "Lipid NP"))
        )
        material_info = material_properties.get(d["Material"], {})
        st.caption(f"🔄 **Biodegradation**: {material_info.get('biodegradation', 'N/A')} days")
        st.caption(f"💰 **Cost Base**: ${material_info.get('cost_base', 'N/A')}")
    
    with col2:
        d["Target"] = st.selectbox(
            "Target Organ/Tissue",
            ["Liver Cells", "Tumor", "Brain", "Lung", "Kidney", "Spleen", "Bone"],
            index=["Liver Cells", "Tumor", "Brain", "Lung", "Kidney", "Spleen", "Bone"].index(d.get("Target", "Liver Cells"))
        )
        st.caption(f"⚡ **Density**: {material_info.get('density', 'N/A')} g/cm³")
    
    st.markdown("### 📏 Physical Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        d["Size"] = st.slider(
            "Core Particle Size (nm)",
            min_value=10,
            max_value=500,
            value=int(d.get("Size", 100)),
            step=5,
            help="Optimal range: 80-120 nm"
        )
    
    with col2:
        d["PDI"] = st.slider(
            "Polydispersity Index",
            min_value=0.05,
            max_value=0.5,
            value=float(d.get("PDI", 0.15)),
            step=0.02,
            help="<0.1 = very uniform"
        )
    
    with col3:
        d["HydrodynamicSize"] = st.slider(
            "Hydrodynamic Size (nm)",
            min_value=20,
            max_value=600,
            value=int(d.get("HydrodynamicSize", 120)),
            step=5,
        )
    
    st.markdown("### ⚛️ Encapsulation & Stability")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        d["Encapsulation"] = st.slider(
            "Drug Encapsulation (%)",
            min_value=10,
            max_value=100,
            value=int(d.get("Encapsulation", 85)),
            step=5,
        )
    
    with col2:
        d["Stability"] = st.slider(
            "Stability (%)",
            min_value=20,
            max_value=100,
            value=int(d.get("Stability", 85)),
            step=5,
        )
    
    with col3:
        d["DegradationTime"] = st.slider(
            "Degradation Time (days)",
            min_value=1,
            max_value=365,
            value=int(d.get("DegradationTime", 30)),
            step=5,
        )

# TAB 2: SURFACE & CHEMISTRY
with tab2:
    st.subheader("🎨 Surface Modification & Chemistry")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Surface Charge**")
        d["Charge"] = st.slider(
            "Surface Charge (mV)",
            min_value=-50,
            max_value=50,
            value=int(d.get("Charge", -5)),
            step=2,
            help="Optimal: ±10 mV"
        )
        
        st.write("**Surface Area**")
        d["SurfaceArea"] = st.slider(
            "Surface Area (nm²)",
            min_value=50,
            max_value=2000,
            value=int(d.get("SurfaceArea", 250)),
            step=50,
        )
    
    with col2:
        st.write("**Hydrophobicity**")
        d["Hydrophobicity"] = st.slider(
            "Surface Hydrophobicity (LogP)",
            min_value=-5.0,
            max_value=5.0,
            value=float(d.get("Hydrophobicity", 1.5)),
            step=0.2,
        )
        
        st.write("**Crystallinity**")
        d["CrystallinityIndex"] = st.slider(
            "Crystallinity Index (%)",
            min_value=0,
            max_value=100,
            value=int(d.get("CrystallinityIndex", 65)),
            step=5,
        )
    
    st.markdown("### 🧪 Coating & Functional Groups")
    
    col1, col2 = st.columns(2)
    
    with col1:
        d["SurfaceCoating"] = st.multiselect(
            "Surface Coating Layers",
            ["PEG (Stealth)", "Chitosan", "Hyaluronic Acid", "Albumin"],
            default=d.get("SurfaceCoating", ["PEG (Stealth)"])
        )
        
        if d["SurfaceCoating"]:
            d["CoatingThickness"] = st.slider(
                "Coating Thickness (nm)",
                min_value=0.5,
                max_value=20.0,
                value=float(d.get("CoatingThickness", 2.5)),
                step=0.5,
            )
    
    with col2:
        d["FunctionalGroups"] = st.multiselect(
            "Functional Groups",
            ["-OH (Hydroxyl)", "-COOH (Carboxyl)", "-NH2 (Amino)", "-SH (Thiol)"],
            default=d.get("FunctionalGroups", ["-COOH (Carboxyl)"])
        )

# TAB 3: TARGETING
with tab3:
    st.subheader("🎯 Targeting & Ligands")
    
    col1, col2 = st.columns(2)
    
    with col1:
        d["Ligand"] = st.selectbox(
            "Primary Targeting Ligand",
            ["GalNAc", "Folate", "Transferrin", "RGD Peptide", "Anti-HER2", "None"],
            index=["GalNAc", "Folate", "Transferrin", "RGD Peptide", "Anti-HER2", "None"].index(d.get("Ligand", "GalNAc"))
        )
        
        if d["Ligand"] != "None":
            d["LigandDensity"] = st.slider(
                "Ligand Surface Density (%)",
                min_value=5,
                max_value=100,
                value=int(d.get("LigandDensity", 60)),
                step=5,
            )
    
    with col2:
        d["Receptor"] = st.selectbox(
            "Target Receptor",
            ["ASGPR", "Folate Receptor", "Transferrin Receptor", "Integrin", "EGFR", "None"],
            index=["ASGPR", "Folate Receptor", "Transferrin Receptor", "Integrin", "EGFR", "None"].index(d.get("Receptor", "ASGPR"))
        )
        
        if d["Receptor"] != "None":
            d["ReceptorBinding"] = st.slider(
                "Receptor Binding Affinity (Kd, nM)",
                min_value=0.1,
                max_value=1000.0,
                value=float(d.get("ReceptorBinding", 10.0)),
                step=1.0,
            )
    
    st.markdown("### 💊 Release Profile")
    
    d["ReleaseProfile"] = st.selectbox(
        "Release Profile",
        ["Immediate", "Sustained (1 week)", "Sustained (2 weeks)", "Sustained (1 month)"],
        index=["Immediate", "Sustained (1 week)", "Sustained (2 weeks)", "Sustained (1 month)"].index(d.get("ReleaseProfile", "Sustained (1 week)"))
    )
    
    d["ReleasePredictability"] = st.slider(
        "Release Predictability (%)",
        min_value=50,
        max_value=100,
        value=int(d.get("ReleasePredictability", 85)),
        step=5,
    )

# TAB 4: SCORING & ANALYSIS
with tab4:
    st.subheader("📊 Real-Time Design Scoring")
    
    # Compute scores
    impact = compute_impact(d)
    overall = overall_score_from_impact(impact)
    
    # Create gauge chart
    fig = go.Figure(data=[go.Indicator(
        mode="gauge+number+delta",
        value=overall,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Design Success Score"},
        delta={"reference": 80, "suffix": " vs target"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "darkblue"},
            "steps": [
                {"range": [0, 30], "color": "rgba(255, 100, 100, 0.3)"},
                {"range": [30, 60], "color": "rgba(255, 200, 0, 0.3)"},
                {"range": [60, 85], "color": "rgba(150, 255, 100, 0.3)"},
                {"range": [85, 100], "color": "rgba(100, 255, 100, 0.3)"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 85
            }
        }
    )])
    
    fig.update_layout(
        height=350,
        font={"size": 14},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Scoring breakdown
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Delivery Score", f"{impact['Delivery']:.1f}/100", delta=None)
    with col2:
        st.metric("Toxicity Score", f"{impact['Toxicity']:.1f}/10", delta=None)
    with col3:
        st.metric("Cost Index", f"{impact['Cost']:.1f}/100", delta=None)
    
    st.divider()
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    recommendations = get_recommendations(d)
    
    for rec in recommendations:
        if "✅" in rec:
            st.success(rec)
        elif "🔴" in rec:
            st.error(rec)
        elif "🟡" in rec:
            st.warning(rec)
        else:
            st.info(rec)

st.divider()

# Navigation buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("← Back to Disease Selection", use_container_width=True):
        st.switch_page("pages/0_Disease_Selection.py")

with col2:
    if st.button("Next: Run Simulation →", type="primary", use_container_width=True):
        st.session_state.parameters_configured = True
        st.success("✅ Parameters saved! Ready for simulation...")

with col3:
    if st.button("Save Design", use_container_width=True):
        st.session_state.design_saved = True
        st.success("✅ Design saved to your profile")

