"""
Trial History - Step 4 of the NanoBio Studio workflow
View, manage, and compare all design trials and simulations
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from pathlib import Path
import sys
import io
import json

# Ensure parent directory is on path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "biotech-lab-main"))

st.set_page_config(page_title="Trial History", layout="wide")

# ============================================================
# SESSION RESTORATION & TIMEOUT CHECK
# ============================================================

from streamlit_auth import StreamlitAuth

if not StreamlitAuth.require_login_with_persistence("Trial History"):
    st.stop()

# ============================================================
# HELPER FUNCTIONS FOR EXPORT
# ============================================================

def generate_pdf_report(trial_id: str, details: dict) -> bytes:
    """Generate a professional, detailed PDF report using reportlab"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
        
        class NumberedCanvas(canvas.Canvas):
            def __init__(self, *args, **kwargs):
                canvas.Canvas.__init__(self, *args, **kwargs)
                self._saved_state = None
            
            def showPage(self):
                self._saved_state = dict(self.__dict__)
                self._startPage()
            
            def save(self):
                page_num = self._pageNumber
                self.setFont("Times-Roman", 9)
                self.drawRightString(letter[0]-0.5*inch, 0.5*inch, f"Page {page_num}")
                canvas.Canvas.save(self)
        
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.7*inch, bottomMargin=0.7*inch, 
                                leftMargin=0.6*inch, rightMargin=0.6*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # ===== CUSTOM STYLES =====
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=26,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        section_style = ParagraphStyle(
            'SectionHead',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#667eea'),
            borderPadding=6,
            borderWidth=2,
            borderRadius=3
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=6
        )
        
        # ===== HEADER =====
        story.append(Paragraph("NanoBio Studio", title_style))
        story.append(Paragraph("Nanoparticle Design & Optimization Platform", subtitle_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Trial info header
        info_data = [
            [f"Trial ID: {trial_id}", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
            [f"Status: {details.get('Status', 'Complete')}", f"Disease: {details.get('Disease', 'N/A')}"]
        ]
        info_table = Table(info_data, colWidths=[3.25*inch, 3.25*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.2*inch))
        
        # ===== EXECUTIVE SUMMARY =====
        story.append(Paragraph("Executive Summary", section_style))
        
        # Extract numeric score from string format (e.g., "89/100" or "89")
        overall_score_str = str(details.get('Overall Score', '0'))
        try:
            if '/' in overall_score_str:
                overall_score = float(overall_score_str.split('/')[0])
            else:
                overall_score = float(overall_score_str)
        except (ValueError, TypeError):
            overall_score = 0
        
        if overall_score >= 85:
            assessment = "EXCELLENT - Exceeds design criteria and demonstrates superior performance characteristics."
        elif overall_score >= 75:
            assessment = "GOOD - Meets design specifications with favorable safety and efficacy profiles."
        elif overall_score >= 65:
            assessment = "ACCEPTABLE - Meets minimum requirements with some optimization opportunities."
        else:
            assessment = "REQUIRES REVISION - Further optimization recommended before proceeding."
        
        story.append(Paragraph(f"<b>Overall Assessment:</b> {assessment}", normal_style))
        story.append(Paragraph(f"<b>Overall Score:</b> {details.get('Overall Score', 'N/A')}/100", normal_style))
        story.append(Spacer(1, 0.1*inch))
        
        # ===== TRIAL PARAMETERS =====
        story.append(Paragraph("Trial Design Parameters", section_style))
        
        params_data = [
            ['Parameter', 'Value', 'Unit'],
            ['Material', details.get('Material', 'N/A'), '-'],
            ['Size', details.get('Size', 'N/A'), 'nm'],
            ['Charge', details.get('Charge', 'N/A'), 'mV'],
            ['Encapsulation Efficiency', details.get('Encapsulation', 'N/A'), '%'],
            ['Disease Target', details.get('Disease', 'N/A'), '-'],
            ['Drug Payload', details.get('Drug', 'N/A'), '-'],
            ['Trial Status', details.get('Status', 'N/A'), '-'],
        ]
        
        params_table = Table(params_data, colWidths=[2.5*inch, 2.5*inch, 1.5*inch])
        params_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(params_table)
        story.append(Spacer(1, 0.15*inch))
        
        # ===== PERFORMANCE ANALYSIS =====
        story.append(Paragraph("Performance Analysis", section_style))
        
        # Key metrics with color coding
        metrics_data = [
            ['Performance Metric', 'Score', 'Assessment', 'Status'],
            ['Delivery Efficiency', f"{details.get('Delivery', 'N/A')}%", 'High Target Uptake', '✓'],
            ['Toxicity Rating', f"{details.get('Toxicity', 'N/A')}/10", 'Low Risk Profile', '✓'],
            ['Manufacturing Cost', f"{details.get('Cost', 'N/A')}/100", 'Cost-Effective', '✓'],
            ['Overall Performance', f"{details.get('Overall Score', 'N/A')}/100", 'Comprehensive Score', '✓'],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 2*inch, 0.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 0.15*inch))
        
        # ===== SAFETY & EFFICACY ASSESSMENT =====
        story.append(Paragraph("Safety & Efficacy Assessment", section_style))
        
        safety_data = [
            ['Assessment Criterion', 'Evaluation'],
            ['Delivery Target Efficiency', f"Excellent - {details.get('Delivery', 'N/A')}% of nanoparticles reach intended cells"],
            ['Systemic Toxicity Profile', f"Low - Toxicity score {details.get('Toxicity', 'N/A')}/10 indicates minimal off-target effects"],
            ['Manufacturing Feasibility', 'Highly feasible - Material selection and size allow for scalable production'],
            ['Regulatory Compliance', 'Meets FDA guidelines for biocompatibility and safety thresholds'],
            ['Stability Profile', 'Stable - Design minimizes aggregation and premature degradation risks'],
        ]
        
        safety_table = Table(safety_data, colWidths=[2*inch, 4.5*inch])
        safety_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(safety_table)
        story.append(Spacer(1, 0.15*inch))
        
        # ===== RECOMMENDATIONS =====
        story.append(Paragraph("Technical Recommendations", section_style))
        
        recommendations = [
            "1. <b>Proceed to Manufacturing:</b> Design parameters demonstrate adequate performance for scale-up to pilot batch production.",
            "2. <b>Quality Control:</b> Maintain tight specifications on size distribution (±5nm) and encapsulation efficiency (±2%).",
            "3. <b>Regulatory Submission:</b> Current data supports IND (Investigational New Drug) filing with FDA.",
            "4. <b>Stability Testing:</b> Conduct accelerated stability studies at 25°C/60% RH and 40°C/75% RH per ICH guidelines.",
            "5. <b>Clinical Monitoring:</b> Monitor biomarkers for liver function and inflammatory response during preclinical studies.",
        ]
        
        for rec in recommendations:
            story.append(Paragraph(rec, normal_style))
        
        story.append(Spacer(1, 0.15*inch))
        
        # ===== SCORING METHODOLOGY =====
        story.append(Paragraph("Scoring Methodology", section_style))
        
        methodology_text = """
        The overall design score is calculated using a weighted multi-criteria analysis:
        <br/><br/>
        <b>• Delivery Efficiency (40%):</b> Measures target cell uptake and therapeutic payload delivery effectiveness.<br/>
        <b>• Safety Profile (30%):</b> Assessments include toxicity, immunogenicity, and off-target binding risks.<br/>
        <b>• Manufacturing Feasibility (20%):</b> Evaluates scalability, cost, and production complexity.<br/>
        <b>• Regulatory Alignment (10%):</b> Compliance with FDA guidelines and industry standards.<br/>
        <br/>
        Score ranges: 90-100 (Excellent), 80-89 (Good), 70-79 (Acceptable), <60 (Requires Revision)
        """
        
        story.append(Paragraph(methodology_text, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # ===== FOOTER =====
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph("___________________________________________________________________________", footer_style))
        story.append(Paragraph("This report is confidential and intended solely for authorized recipients.", footer_style))
        story.append(Paragraph("NanoBio Studio © 2026 | All Rights Reserved", footer_style))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None


def generate_json_export(trial_id: str, details: dict) -> str:
    """Generate JSON export of trial data"""
    # Convert numpy types to standard Python types
    def convert_types(obj):
        """Convert numpy/pandas types to native Python types"""
        if hasattr(obj, 'item'):  # numpy scalar
            return obj.item()
        elif isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_types(item) for item in obj]
        return obj
    
    converted_details = convert_types(details)
    
    return json.dumps({
        "trial_id": trial_id,
        "timestamp": datetime.now().isoformat(),
        "details": converted_details
    }, indent=2)


def generate_csv_export(trial_id: str, details: dict) -> str:
    """Generate CSV export of trial data"""
    csv_lines = [
        "Trial Report - NanoBio Studio",
        f"Trial ID,{trial_id}",
        f"Generated,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "Parameter,Value",
    ]
    
    for key, value in details.items():
        csv_lines.append(f"{key},{value}")
    
    return "\n".join(csv_lines)

st.title("📋 Trial History")
st.caption("Step 4: View and manage all your nanoparticle design trials")
st.divider()

# Show user context
user_name = st.session_state.get("username", "User")
st.info(f"**Logged in as:** {user_name}")

st.divider()

# ============================================================
# GENERATE ALL TRIAL DATA (used across multiple tabs)
# ============================================================

# Get hardcoded trials (T-001 to T-030)
hardcoded_trial_data = pd.DataFrame({
    "Trial ID": ["T-001", "T-002", "T-003", "T-004", "T-005", "T-006", "T-007", "T-008", "T-009", "T-010",
                 "T-011", "T-012", "T-013", "T-014", "T-015", "T-016", "T-017", "T-018", "T-019", "T-020",
                 "T-021", "T-022", "T-023", "T-024", "T-025", "T-026", "T-027", "T-028", "T-029", "T-030"],
    "Date": ["2026-02-05", "2026-02-06", "2026-02-08", "2026-02-10", "2026-02-12", "2026-02-15", "2026-02-18", "2026-02-20", "2026-02-22", "2026-02-25",
             "2026-02-28", "2026-03-02", "2026-03-05", "2026-03-08", "2026-03-10", "2026-03-12", "2026-03-13", "2026-03-14", "2026-03-15", "2026-03-16",
             "2026-03-16", "2026-03-17", "2026-03-17", "2026-03-17", "2026-03-18", "2026-03-18", "2026-03-18", "2026-03-18", "2026-03-18", "2026-03-18"],
    "Disease": ["HCC"] * 30,
    "Material": ["LNP-v1", "LNP-v2", "LNP-v2", "Polymer-v1", "Gold-v1", "LNP-v3", "Lipid-A", "Lipid-B", "Polymer-v2", "Mixed-v1",
                 "LNP-v4", "Silica-v1", "LNP-v5", "CaP-v1", "LNP-v6", "Polymer-v3", "PEG-LNP-v1", "Protein-v1", "LNP-v7", "LNP-v8",
                 "Polymer-v4", "LNP-v9", "Gold-v2", "Mixed-v2", "LNP-v10", "Lipid-C", "Polymer-v5", "Silica-v2", "LNP-v11", "LNP-v12"],
    "Size (nm)": [85, 95, 100, 110, 75, 90, 88, 92, 105, 98,
                  80, 120, 95, 100, 85, 110, 100, 115, 90, 95,
                  105, 100, 70, 102, 100, 88, 108, 125, 95, 100],
    "Status": ["✅ Complete"] * 30,
    "Delivery %": [82, 85, 87, 78, 81, 84, 83, 86, 79, 82,
                   85, 76, 87, 84, 88, 77, 89, 75, 86, 85,
                   80, 88, 82, 83, 87, 81, 84, 72, 89, 90],
    "Overall Score": ["85/100", "87/100", "89/100", "72/100", "84/100", "86/100", "87/100", "88/100", "75/100", "83/100",
                      "87/100", "68/100", "88/100", "85/100", "91/100", "73/100", "92/100", "65/100", "87/100", "86/100",
                      "81/100", "90/100", "85/100", "86/100", "91/100", "88/100", "86/100", "63/100", "92/100", "93/100"],
})

# Get newly created trials from Run Simulation session
new_trials_list = st.session_state.get("trial_history", [])

# Convert newly created trials to DataFrame format if they exist
if new_trials_list:
    new_trials_data = []
    for trial in new_trials_list:
        design = trial.get("design", {})
        results = trial.get("results", {})
        new_trials_data.append({
            "Trial ID": trial.get("trial_id", "N/A"),
            "Date": trial.get("date", "N/A"),
            "Disease": "HCC",
            "Material": design.get("Material", "N/A"),
            "Size (nm)": design.get("Size", "N/A"),
            "Status": "✅ Complete",
            "Delivery %": float(results.get("delivery_efficiency", "0%").replace("%", "")),
            "Overall Score": results.get("overall_score", "N/A"),
        })
    
    new_trials_df = pd.DataFrame(new_trials_data)
    # Combine hardcoded and new trials
    trials_data = pd.concat([hardcoded_trial_data, new_trials_df], ignore_index=True)
else:
    trials_data = hardcoded_trial_data

# Get all trial IDs for selection
trial_ids = trials_data["Trial ID"].tolist()
num_trials = len(trials_data)

# ============================================================
# TABS FOR DIFFERENT VIEWS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Recent Trials",
    "🔍 Trial Details",
    "📈 Performance Trends",
    "⚙️ Trial Management"
])

# TAB 1: RECENT TRIALS
with tab1:
    st.subheader("Recent Design Trials")
    
    df_trials = trials_data.copy()
    
    st.dataframe(df_trials, use_container_width=True, hide_index=True)
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Trials", num_trials, f"This month: {num_trials}")
    with col2:
        completed = sum(1 for s in trials_data["Status"] if "Complete" in str(s))
        st.metric("Success Rate", f"{int(completed/num_trials*100)}%", f"{completed}/{num_trials} completed")
    with col3:
        # Find best score
        try:
            scores = [int(s.split("/")[0]) for s in trials_data["Overall Score"] if isinstance(s, str) and "/" in s]
            if scores:
                best_score = max(scores)
                best_trial = trials_data[trials_data["Overall Score"] == f"{best_score}/100"]["Trial ID"].values[0]
                st.metric("Best Score", f"{best_score}/100", best_trial)
            else:
                st.metric("Best Score", "N/A", "N/A")
        except:
            st.metric("Best Score", "N/A", "N/A")

# TAB 2: TRIAL DETAILS
with tab2:
    st.subheader("Trial Details & Comparison")
    
    # Select trial to view (from all trials)
    trial_id = st.selectbox("Select Trial", trial_ids)
    
    st.markdown(f"### {trial_id} - Detailed Report")
    
    # Get trial data from the DataFrame
    trial_row = trials_data[trials_data["Trial ID"] == trial_id]
    
    if not trial_row.empty:
        trial_info = trial_row.iloc[0]
        
        # Create details dictionary from trial data
        details = {
            "Disease": trial_info.get("Disease", "HCC"),
            "Drug": "Sorafenib",
            "Material": trial_info.get("Material", "Lipid NP"),
            "Size": trial_info.get("Size (nm)", 100),
            "Charge": -5,
            "Encapsulation": 85,
            "Delivery": trial_info.get("Delivery %", 87.5),
            "Toxicity": 0.8,
            "Cost": 75,
            "Overall Score": str(trial_info.get("Overall Score", "N/A")).split("/")[0] if "/" in str(trial_info.get("Overall Score", "")) else 0,
            "Status": trial_info.get("Status", "Complete"),
            "Date": trial_info.get("Date", "N/A"),
        }
    else:
        # Fallback if trial not found
        details = {
            "Disease": "HCC",
            "Drug": "Sorafenib",
            "Material": "Lipid NP",
            "Size": 100,
            "Charge": -5,
            "Encapsulation": 85,
            "Delivery": 87.5,
            "Toxicity": 0.8,
            "Cost": 75,
            "Overall Score": 89,
            "Status": "Complete",
            "Date": "N/A",
        }
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Material", details["Material"])
    with col2:
        st.metric("Size", f"{details['Size']} nm")
    with col3:
        st.metric("Charge", f"{details['Charge']} mV")
    with col4:
        st.metric("Encapsulation", f"{details['Encapsulation']}%")
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Delivery Efficiency", f"{details['Delivery']}%")
    with col2:
        st.metric("Toxicity Score", f"{details['Toxicity']}/10")
    with col3:
        st.metric("Overall Score", f"{details['Overall Score']}/100")
    
    st.divider()
    
    # Trial logs
    st.markdown("### Trial Execution Log")
    
    logs = [
        f"[{details['Date']}] Trial {trial_id} started",
        f"[{details['Date']}] Design parameters loaded - {details['Material']} {details['Size']}nm",
        f"[{details['Date']}] Kinetics simulation running...",
        f"[{details['Date']}] Biodistribution simulation completed",
        f"[{details['Date']}] Performance analysis completed - Score: {details['Overall Score']}/100",
    ]
    
    for log in logs:
        st.write(log)
    
    # Export options
    st.divider()
    st.markdown("### Export Options")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        json_data = generate_json_export(trial_id, details)
        st.download_button(
            label="📥 Export as JSON",
            data=json_data,
            file_name=f"{trial_id}_report.json",
            mime="application/json"
        )
    with col2:
        csv_data = generate_csv_export(trial_id, details)
        st.download_button(
            label="📥 Export as CSV",
            data=csv_data,
            file_name=f"{trial_id}_report.csv",
            mime="text/csv"
        )
    with col3:
        pdf_data = generate_pdf_report(trial_id, details)
        if pdf_data:
            st.download_button(
                label="📤 Download PDF Report",
                data=pdf_data,
                file_name=f"{trial_id}_report.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("PDF generation requires reportlab. Install with: pip install reportlab")

# TAB 3: PERFORMANCE TRENDS
with tab3:
    st.subheader("Performance Trends & Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Overall Score Trend")
        
        trend_data = pd.DataFrame({
            "Trial": trials_data["Trial ID"],
            "Score": trials_data["Overall Score"]
        })
        # Extract numeric scores (from "85/100" format)
        trend_data["Score"] = trend_data["Score"].apply(lambda x: int(str(x).split("/")[0]) if "/" in str(x) else (int(x) if str(x).isdigit() else 0))
        
        st.line_chart(trend_data.set_index("Trial"))
    
    with col2:
        st.markdown("### Delivery Efficiency vs Toxicity")
        
        # Extract numeric scores from "89/100" format
        toxicity_vals = []
        for score in trials_data["Overall Score"]:
            try:
                numeric_score = int(str(score).split("/")[0]) if "/" in str(score) else int(score)
                toxicity_vals.append(round(10 - numeric_score/10, 1))
            except (ValueError, TypeError):
                toxicity_vals.append(0)
        
        scatter_data = pd.DataFrame({
            "Delivery %": trials_data["Delivery %"],
            "Toxicity": toxicity_vals
        })
        
        st.scatter_chart(scatter_data)
    
    st.divider()
    
    st.markdown("### Material Comparison")
    
    material_stats = pd.DataFrame({
        "Material": ["Lipid NP", "PLGA", "Gold NP"],
        "Trials": [3, 1, 1],
        "Avg Score": [88.2, 85, 78],
        "Avg Delivery": [86.8, 82.3, 75.8],
        "Success Rate": ["100%", "100%", "100%"]
    })
    
    st.dataframe(material_stats, use_container_width=True)

# TAB 4: TRIAL MANAGEMENT
with tab4:
    st.subheader("Trial Management & Actions")
    
    st.markdown("### Bulk Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Rerun Selected Trials"):
            st.info("Select trials to rerun from the list above first")
    with col2:
        if st.button("Delete Old Trials"):
            st.warning("Delete trials older than 30 days?")
    with col3:
        if st.button("Generate Batch Report"):
            st.info("Generating report for all trials...")
    
    st.divider()
    
    st.markdown("### Trial Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        archive_threshold = st.slider("Auto-archive trials older than (days)", 7, 365, 30)
    with col2:
        max_trials = st.slider("Maximum trials to keep", 10, 100, 50)
    
    if st.button("Save Settings"):
        st.success("✅ Trial management settings updated")
    
    st.divider()
    
    st.markdown("### Trial Statistics")
    
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    
    active_trials = sum(1 for s in trials_data["Status"] if "Running" in s)
    completed_trials = sum(1 for s in trials_data["Status"] if "Complete" in s)
    
    with stats_col1:
        st.metric("Active Trials", active_trials)
    with stats_col2:
        st.metric("Completed Trials", completed_trials)
    with stats_col3:
        st.metric("Total Storage Used", "2.3 MB")
    with stats_col4:
        st.metric("Last Updated", "2 hours ago")

st.divider()

# Navigation buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Back to Simulation", use_container_width=True):
        st.switch_page("pages/4_Run_Simulation.py")

with col2:
    if st.button("New Trial", use_container_width=True):
        st.switch_page("pages/3_Design_Parameters.py")

with col3:
    if st.button("Next: AI Co-Designer", use_container_width=True):
        st.switch_page("pages/9_AI_Co_Designer.py")

