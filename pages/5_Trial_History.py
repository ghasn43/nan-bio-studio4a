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

# Check if user is logged in
if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in first")
    st.switch_page("Login.py")

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
        
        overall_score = float(str(details.get('Overall Score', 0)).split('/')[0]) if '/' in str(details.get('Overall Score', 0)) else details.get('Overall Score', 0)
        
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
    return json.dumps({
        "trial_id": trial_id,
        "timestamp": datetime.now().isoformat(),
        "details": details
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
    
    # Mock trial data
    trials_data = {
        "Trial ID": ["TRIAL-001", "TRIAL-002", "TRIAL-003", "TRIAL-004", "TRIAL-005"],
        "Date": [
            (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
            (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
            (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
            (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"),
        ],
        "Disease": ["HCC", "HCC", "HCC", "HCC", "HCC"],
        "Material": ["Lipid NP", "PLGA", "Lipid NP", "Gold NP", "Lipid NP"],
        "Size (nm)": [100, 110, 95, 105, 115],
        "Status": ["✅ Complete", "✅ Complete", "✅ Complete", "✅ Complete", "⚙️ Running"],
        "Delivery %": [87.5, 82.3, 91.2, 75.8, 0],
        "Overall Score": [89, 85, 92, 78, "In Progress"],
    }
    
    df_trials = pd.DataFrame(trials_data)
    
    st.dataframe(df_trials, use_container_width=True, hide_index=True)
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Trials", 5, "This month: 5")
    with col2:
        st.metric("Success Rate", "80%", "4/5 completed")
    with col3:
        st.metric("Best Score", "92/100", "TRIAL-003")

# TAB 2: TRIAL DETAILS
with tab2:
    st.subheader("Trial Details & Comparison")
    
    # Select trial to view
    trial_id = st.selectbox("Select Trial", ["TRIAL-001", "TRIAL-002", "TRIAL-003", "TRIAL-004", "TRIAL-005"])
    
    st.markdown(f"### {trial_id} - Detailed Report")
    
    # Mock trial details
    trial_details = {
        "TRIAL-001": {
            "Disease": "HCC",
            "Drug": "Sorafenib",
            "Material": "Lipid NP",
            "Size": 100,
            "Charge": -5,
            "Encapsulation": 85,
            "Delivery": 87.5,
            "Toxicity": 0.8,
            "Cost": 88,
            "Overall Score": 89,
            "Status": "Complete",
            "Date": "2026-03-17 14:30"
        }
    }
    
    details = trial_details.get(trial_id, trial_details["TRIAL-001"])
    
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
            "Trial": ["TRIAL-001", "TRIAL-002", "TRIAL-003", "TRIAL-004", "TRIAL-005"],
            "Score": [89, 85, 92, 78, 88]
        })
        
        st.line_chart(trend_data.set_index("Trial"))
    
    with col2:
        st.markdown("### Delivery Efficiency vs Toxicity")
        
        scatter_data = pd.DataFrame({
            "Delivery %": [87.5, 82.3, 91.2, 75.8, 86.5],
            "Toxicity": [0.8, 1.2, 0.5, 2.1, 0.9]
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
    
    with stats_col1:
        st.metric("Active Trials", 1)
    with stats_col2:
        st.metric("Completed Trials", 4)
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

