"""
NanoBio Studio™ Branding Components
Reusable Streamlit components for consistent branding across the application
"""

import streamlit as st
from components.branding_config import (
    APP_NAME, TAGLINE, COMPANY_NAME, COPYRIGHT, PROPRIETARY_NOTICE,
    FOUNDER_NAME, FOUNDER_TITLE, EMAIL, PHONE, WEBSITE, LOCATION,
    IP_OWNERSHIP_STATEMENT, RESEARCH_DISCLAIMER, LICENSING_CONTACT,
    POWERED_BY, BRAND_COLORS, get_footer_text, get_contact_info
)


def render_brand_header():
    """
    Render professional branded header at the top of pages
    """
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(
            f"""
            <div style="padding: 15px; background-color: {BRAND_COLORS['primary']}; 
                        border-radius: 5px; color: white; text-align: center;">
                <h2 style="margin: 0; color: white;">🧬 {APP_NAME}</h2>
                <p style="margin: 5px 0; font-size: 14px; color: #E6F0F7;"><i>{TAGLINE}</i></p>
                <p style="margin: 8px 0; font-size: 12px; color: #B3D9FF;">{POWERED_BY}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="padding: 15px; text-align: right; font-size: 11px; color: {BRAND_COLORS['gray']};">
                <strong>{COMPANY_NAME}</strong><br>
                {LOCATION}<br>
                <small>{PROPRIETARY_NOTICE}</small>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("---")


def render_brand_footer():
    """
    Render professional branded footer at the bottom of pages
    """
    st.markdown("---")
    st.markdown(
        f"""
        <div style="padding: 15px; background-color: {BRAND_COLORS['light']}; 
                    border-radius: 5px; text-align: center; font-size: 12px; color: {BRAND_COLORS['gray']};">
            <strong>{get_footer_text()}</strong><br>
            <small>Founder & IP Owner: <strong>{FOUNDER_NAME}</strong> | {COMPANY_NAME}</small>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_ip_notice():
    """
    Render IP Ownership Notice with legal language
    """
    st.markdown("---")
    st.markdown("### 🔐 Intellectual Property Notice")
    st.info(IP_OWNERSHIP_STATEMENT)


def render_research_disclaimer():
    """
    Render Research Disclaimer
    """
    st.markdown("### ⚠️ Research Disclaimer")
    st.warning(RESEARCH_DISCLAIMER)


def render_licensing_contact():
    """
    Render Licensing & Partnerships Contact Block
    """
    st.markdown("---")
    st.markdown("### 🤝 Licensing, Partnerships & Collaboration")
    st.markdown(LICENSING_CONTACT)


def render_contact_box():
    """
    Render compact contact information box
    """
    st.markdown(
        f"""
        <div style="padding: 12px; background-color: {BRAND_COLORS['light']}; 
                    border-left: 4px solid {BRAND_COLORS['primary']}; 
                    border-radius: 4px; margin: 10px 0;">
            <strong>{APP_NAME}</strong><br>
            <small>{COMPANY_NAME} | {LOCATION}</small><br>
            <small><strong>Contact:</strong> {EMAIL} | {PHONE}</small><br>
            <small><strong>Web:</strong> {WEBSITE}</small>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_sidebar_branding():
    """
    Render compact branding panel in the sidebar
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            f"""
            <div style="padding: 10px; text-align: center; font-size: 11px;">
                <h4 style="margin: 0; color: {BRAND_COLORS['primary']};">{APP_NAME}</h4>
                <small><strong>{COMPANY_NAME}</strong></small><br>
                <small>🔒 Proprietary IP</small><br>
                <small><strong>Founder:</strong> {FOUNDER_NAME}</small>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if st.button("📧 Send Feedback", key="sidebar_contact"):
            st.markdown(f"📧 **Email:** {EMAIL}\n📱 **Phone:** {PHONE}")
        
        st.markdown("---")


def render_page_title_with_branding(title, subtitle=None):
    """
    Render page title with consistent branding styling
    """
    gray_color = BRAND_COLORS['gray']
    subtitle_html = f'<p style="margin: 5px 0; color: {gray_color}; font-size: 14px;"><em>{subtitle}</em></p>' if subtitle else ''
    
    st.markdown(
        f"""
        <div style="padding: 15px; background-color: {BRAND_COLORS['light']}; 
                    border-radius: 5px; margin: 10px 0;">
            <h1 style="margin: 0; color: {BRAND_COLORS['primary']};">{title}</h1>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_section_divider(label=None):
    """
    Render branded section divider
    """
    if label:
        st.markdown(f"### {label}")
    st.markdown("---")


def add_branding_to_exported_report(report_content):
    """
    Add branding footer to exported report content (for PDF/Word exports)
    Returns formatted report with branding
    """
    branding_footer = f"""
    
    ================================================================================
    {APP_NAME}
    {TAGLINE}
    ================================================================================
    {COPYRIGHT}
    {PROPRIETARY_NOTICE}
    
    Founder & IP Owner: {FOUNDER_NAME} ({FOUNDER_TITLE})
    Company: {COMPANY_NAME}
    Location: {LOCATION}
    
    Contact:
    Email: {EMAIL}
    Phone: {PHONE}
    Website: {WEBSITE}
    
    DISCLAIMER:
    {RESEARCH_DISCLAIMER}
    
    ================================================================================
    """
    
    return f"{report_content}\n{branding_footer}"


def render_about_page_branding():
    """
    Full About page with comprehensive branding information
    """
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"## About {APP_NAME}")
        st.markdown(f"""
        **{APP_NAME}** is an advanced computational platform for nanoparticle design, simulation, 
        and translational research. Developed by **{COMPANY_NAME}**, it combines machine learning, 
        molecular simulation, and regulatory frameworks to accelerate nanomedicine development.
        """)
    
    with col2:
        st.markdown(f"""
        <div style="padding: 15px; background-color: {BRAND_COLORS['light']}; 
                    border-radius: 5px; text-align: center;">
            <strong>{COMPANY_NAME}</strong><br>
            {LOCATION}<br><br>
            <strong>Founder & IP Owner</strong><br>
            {FOUNDER_NAME}
        </div>
        """,
        unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    st.subheader("🔐 Intellectual Property")
    st.info(IP_OWNERSHIP_STATEMENT)
    
    st.subheader("⚠️ Research & Clinical Disclaimer")
    st.warning(RESEARCH_DISCLAIMER)
    
    st.subheader("🤝 Partnership & Licensing")
    st.markdown(LICENSING_CONTACT)
    
    st.subheader("📞 Contact Information")
    st.markdown(f"""
    - **Email:** {EMAIL}
    - **Phone:** {PHONE}
    - **Website:** {WEBSITE}
    - **Location:** {LOCATION}
    """)


# ============================================================
# HELPER FUNCTION FOR QUICK INTEGRATION
# ============================================================
def setup_page_with_branding(page_title, page_subtitle=None, show_ip_notice=False, 
                            show_disclaimer=False, show_footer=True):
    """
    Quick setup function to add complete branding to any page
    
    Usage in your page:
    ```
    from components.branding import setup_page_with_branding
    setup_page_with_branding(
        page_title="Your Page Title",
        page_subtitle="Optional subtitle",
        show_ip_notice=True,
        show_disclaimer=True
    )
    ```
    """
    render_sidebar_branding()
    render_brand_header()
    render_page_title_with_branding(page_title, page_subtitle)
    
    if show_ip_notice:
        render_ip_notice()
    
    if show_disclaimer:
        render_research_disclaimer()
    
    if show_footer:
        render_brand_footer()
