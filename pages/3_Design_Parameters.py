"""
Design Parameters - Step 2 of the NanoBio Studio workflow
Configure nanoparticle design parameters with real-time scoring
"""
import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
import importlib

# Ensure parent directory is on path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "biotech-lab-main"))

from core.scoring import compute_impact, get_recommendations, overall_score_from_impact

# Force reload to ensure latest version is used
import core.scoring
importlib.reload(core.scoring)
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

# ============================================================
# SIMPLE EXPLANATION FOR LAYMAN
# ============================================================

with st.expander("❓ What are Design Parameters? (Simple Explanation)", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🛠️ What are you designing?
        
        A **nanoparticle** is a tiny drug carrier. You need to decide:
        - How big should it be? (Size in nm)
        - What charge should it have? (Charge in mV)
        - What material? (Lipid, gold, polymer)
        - How much drug inside? (Encapsulation %)
        
        **Think of it like building a tiny medicine package.**
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Why does each parameter matter?
        
        ✅ **Size** → Affects how it travels in the body  
        ✅ **Charge** → Controls where it sticks and how safe it is  
        ✅ **Material** → Determines cost and biocompatibility  
        ✅ **Drug Loading** → How much medicine gets delivered
        """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 What are the 4 tabs?
        
        **Tab 1: Core Properties**  
        Size, charge, encapsulation basics
        
        **Tab 2: Surface Chemistry**  
        Coating, hydrophobicity, crystal structure
        """)
    
    with col2:
        st.markdown("""
        **Tab 3: Targeting**  
        How to make it find the right cells
        
        **Tab 4: Scoring**  
        See real-time score & adjust weights
        """)
    
    st.success("**Your goal:** Find a design that's safe, effective, affordable, and works well for your target disease.")

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

# Function to display gauge chart
def display_score_gauge(key="gauge"):
    """Display the real-time design scoring gauge"""
    impact = compute_impact(d)
    overall = overall_score_from_impact(impact)
    
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
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig, use_container_width=True, key=key)
    with col2:
        st.markdown("### 📊 Score Metrics")
        st.metric("Overall Score", f"{overall:.1f}/100")
        st.metric("Delivery", f"{impact['Delivery']:.1f}/100")
        st.metric("Toxicity", f"{impact['Toxicity']:.1f}/10")
        st.metric("Cost Index", f"{impact['Cost']:.1f}/100")

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
    st.divider()
    st.markdown("### 🎯 Parameter Impact on Score")
    display_score_gauge("gauge_core")
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
    
    st.divider()
    st.markdown("### 🎯 Parameter Impact on Score")
    display_score_gauge("gauge_surface")

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
        
        # Always render the slider to persist values in session state
        ligand_density_disabled = d["Ligand"] == "None"
        d["LigandDensity"] = st.slider(
            "Ligand Surface Density (%)",
            min_value=5,
            max_value=100,
            value=int(d.get("LigandDensity", 60)),
            step=5,
            disabled=ligand_density_disabled,
            help="Only active when a ligand is selected" if ligand_density_disabled else "Higher density = better targeting"
        )
    
    with col2:
        d["Receptor"] = st.selectbox(
            "Target Receptor",
            ["ASGPR", "Folate Receptor", "Transferrin Receptor", "Integrin", "EGFR", "None"],
            index=["ASGPR", "Folate Receptor", "Transferrin Receptor", "Integrin", "EGFR", "None"].index(d.get("Receptor", "ASGPR"))
        )
        
        # Always render the slider to persist values in session state
        receptor_binding_disabled = d["Receptor"] == "None"
        d["ReceptorBinding"] = st.slider(
            "Receptor Binding Affinity (Kd, nM)",
            min_value=0.1,
            max_value=1000.0,
            value=float(d.get("ReceptorBinding", 10.0)),
            step=1.0,
            disabled=receptor_binding_disabled,
            help="Only active when a receptor is selected" if receptor_binding_disabled else "Lower Kd = stronger binding"
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
    
    # SYNC design changes to session state immediately
    st.session_state.design = d
    
    st.divider()
    
    # Debug: Show current targeting values
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ligand Density", f"{d.get('LigandDensity', 0)}%")
    with col2:
        st.metric("Receptor Kd", f"{d.get('ReceptorBinding', 0):.1f} nM")
    with col3:
        st.metric("Release Predict", f"{d.get('ReleasePredictability', 0)}%")
    with col4:
        st.metric("Selected Ligand", d.get("Ligand", "None"))
    
    st.divider()
    st.markdown("### 🎯 Parameter Impact on Score")
    
    # Recompute impact with current synced values
    current_impact = compute_impact(st.session_state.design)
    current_score = overall_score_from_impact(current_impact)
    
    fig = go.Figure(data=[go.Indicator(
        mode="gauge+number+delta",
        value=current_score,
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
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig, use_container_width=True, key=f"gauge_targeting_{current_score:.1f}")
    with col2:
        st.markdown("### 📊 Score Metrics")
        st.metric("Overall Score", f"{current_score:.1f}/100")
        st.metric("Delivery", f"{current_impact['Delivery']:.1f}/100")
        st.metric("Toxicity", f"{current_impact['Toxicity']:.1f}/10")
        st.metric("Cost Index", f"{current_impact['Cost']:.1f}/100")

# TAB 4: SCORING & ANALYSIS
with tab4:
    st.subheader("📊 Design Performance Analysis")
    
    # Initialize weight settings in session state
    if "weight_presets" not in st.session_state:
        st.session_state.weight_presets = {
            "Balanced": {"size": 0.18, "charge": 0.14, "encap": 0.18, "pdi": 0.10, "hydro": 0.06, "stability": 0.04, "targeting": 0.08, "release": 0.04, "surface_area": 0.04, "hydrophobicity": 0.05, "crystallinity": 0.05, "coating": 0.05},
            "Targeting-Focused": {"size": 0.12, "charge": 0.10, "encap": 0.12, "pdi": 0.08, "hydro": 0.04, "stability": 0.03, "targeting": 0.20, "release": 0.10, "surface_area": 0.03, "hydrophobicity": 0.04, "crystallinity": 0.04, "coating": 0.10},
            "Core-Physics-Focus": {"size": 0.25, "charge": 0.20, "encap": 0.25, "pdi": 0.15, "hydro": 0.08, "stability": 0.06, "targeting": 0.01, "release": 0.00, "surface_area": 0.00, "hydrophobicity": 0.00, "crystallinity": 0.00, "coating": 0.00},
            "Surface-Chemistry-Focus": {"size": 0.10, "charge": 0.10, "encap": 0.10, "pdi": 0.08, "hydro": 0.05, "stability": 0.03, "targeting": 0.06, "release": 0.03, "surface_area": 0.10, "hydrophobicity": 0.15, "crystallinity": 0.10, "coating": 0.10},
        }
    
    if "custom_weights" not in st.session_state:
        st.session_state.custom_weights = st.session_state.weight_presets["Balanced"].copy()
    
    # Preset selector
    st.markdown("### ⚖️ Weight Configuration")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        preset_name = st.selectbox(
            "📋 Weight Preset",
            list(st.session_state.weight_presets.keys()),
            help="Select a preset weight distribution"
        )
        
        if preset_name:
            st.session_state.custom_weights = st.session_state.weight_presets[preset_name].copy()
    
    with col2:
        st.info(f"**Active:** {preset_name}")
    
    st.divider()
    
    # Weight adjustment sliders
    st.markdown("### 🎚️ Fine-Tune Weights")
    st.caption("Drag sliders to adjust importance of each parameter (will auto-normalize)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.session_state.custom_weights["size"] = st.slider("Size", 0, 30, int(st.session_state.custom_weights["size"] * 100), 1) / 100
        st.session_state.custom_weights["charge"] = st.slider("Charge", 0, 30, int(st.session_state.custom_weights["charge"] * 100), 1) / 100
        st.session_state.custom_weights["encap"] = st.slider("Encapsulation", 0, 30, int(st.session_state.custom_weights["encap"] * 100), 1) / 100
        st.session_state.custom_weights["pdi"] = st.slider("PDI", 0, 20, int(st.session_state.custom_weights["pdi"] * 100), 1) / 100
    
    with col2:
        st.session_state.custom_weights["targeting"] = st.slider("Targeting", 0, 30, int(st.session_state.custom_weights["targeting"] * 100), 1) / 100
        st.session_state.custom_weights["release"] = st.slider("Release Predict", 0, 20, int(st.session_state.custom_weights["release"] * 100), 1) / 100
        st.session_state.custom_weights["hydrophobicity"] = st.slider("Hydrophobicity", 0, 20, int(st.session_state.custom_weights["hydrophobicity"] * 100), 1) / 100
        st.session_state.custom_weights["crystallinity"] = st.slider("Crystallinity", 0, 20, int(st.session_state.custom_weights["crystallinity"] * 100), 1) / 100
    
    with col3:
        st.session_state.custom_weights["coating"] = st.slider("Coating", 0, 20, int(st.session_state.custom_weights["coating"] * 100), 1) / 100
        st.session_state.custom_weights["hydro"] = st.slider("Hydrodynamic", 0, 20, int(st.session_state.custom_weights["hydro"] * 100), 1) / 100
        st.session_state.custom_weights["stability"] = st.slider("Stability", 0, 20, int(st.session_state.custom_weights["stability"] * 100), 1) / 100
        st.session_state.custom_weights["surface_area"] = st.slider("Surface Area", 0, 20, int(st.session_state.custom_weights["surface_area"] * 100), 1) / 100
    
    st.divider()
    
    # Display weight distribution
    st.markdown("### 📊 Weight Distribution")
    
    # Create pie chart of weights
    import plotly.graph_objects as go
    weights_dict = st.session_state.custom_weights
    
    # Group small weights
    labels = []
    values = []
    for k, v in weights_dict.items():
        if v > 0.02:  # Only show > 2%
            labels.append(k.replace('_', ' ').title())
            values.append(v)
    
    fig_weights = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hoverinfo="label+percent+value",
        textposition="auto",
        textinfo="label+percent"
    )])
    
    fig_weights.update_layout(
        height=400,
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig_weights, use_container_width=True)
    
    st.divider()
    
    # Calculate score with custom weights
    current_impact_custom = compute_impact(d, st.session_state.custom_weights)
    current_score_custom = overall_score_from_impact(current_impact_custom)
    
    st.markdown("### 🎯 Impact on Score (with Custom Weights)")
    
    fig_gauge = go.Figure(data=[go.Indicator(
        mode="gauge+number+delta",
        value=current_score_custom,
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
    
    fig_gauge.update_layout(
        height=350,
        font={"size": 14},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_custom_{current_score_custom:.1f}")
    with col2:
        st.markdown("### 📊 Score Breakdown")
        st.metric("Overall Score", f"{current_score_custom:.1f}/100")
        st.metric("Delivery", f"{current_impact_custom['Delivery']:.1f}/100")
        st.metric("Toxicity", f"{current_impact_custom['Toxicity']:.1f}/10")
        st.metric("Cost Index", f"{current_impact_custom['Cost']:.1f}/100")
    
    st.divider()
    
    # Recommendations
    st.markdown("### 💡 Smart Recommendations")
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

# Ensure all changes to 'd' are saved back to session state
st.session_state.design = d

st.divider()

# Navigation buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("← Back to Disease Selection", use_container_width=True):
        st.switch_page("pages/0_Disease_Selection.py")

with col2:
    if st.button("Next: Run Simulation →", type="primary", use_container_width=True):
        st.session_state.parameters_configured = True
        st.switch_page("pages/4_Run_Simulation.py")

with col3:
    if st.button("Save Design", use_container_width=True):
        st.session_state.design_saved = True
        st.success("✅ Design saved to your profile")

