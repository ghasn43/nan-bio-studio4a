"""
NanoBio Studio™ Branding Configuration
Central configuration for consistent branding across the entire application
"""

# ============================================================
# APP BRANDING
# ============================================================
APP_NAME = "NanoBio Studio™"
TAGLINE = "AI-Assisted Nanoparticle Design, Simulation, and Translational Insight"

# ============================================================
# COMPANY & IP OWNERSHIP
# ============================================================
COMPANY_NAME = "Experts Group FZE"
LOCATION = "Abu Dhabi / UAE"

# ============================================================
# COPYRIGHT & IP NOTICE
# ============================================================
YEAR = 2026
COPYRIGHT = f"© {YEAR} Experts Group FZE. All rights reserved."
PROPRIETARY_NOTICE = "Proprietary & Confidential"

# ============================================================
# FOUNDER / IP OWNER
# ============================================================
FOUNDER_NAME = "Ghassan Muammar"
FOUNDER_TITLE = "Founder & IP Owner"

# ============================================================
# CONTACT INFORMATION
# ============================================================
EMAIL = "[INSERT YOUR EMAIL]"
PHONE = "[INSERT YOUR PHONE]"
WEBSITE = "[INSERT YOUR WEBSITE]"

# ============================================================
# IP OWNERSHIP STATEMENT
# ============================================================
IP_OWNERSHIP_STATEMENT = f"""{APP_NAME} is proprietary intellectual property owned exclusively by {COMPANY_NAME}.

Unauthorized copying, modification, distribution, reverse engineering, sublicensing, publication, or commercial use of this software, its design, workflows, models, simulations, branding, content, and associated materials is strictly prohibited without prior written permission from {COMPANY_NAME}.

Founder & IP Owner: {FOUNDER_NAME}
{COMPANY_NAME} | {LOCATION}
"""

# ============================================================
# DISCLAIMER
# ============================================================
RESEARCH_DISCLAIMER = f"""{APP_NAME} is a research, design, and simulation platform intended for computational, scientific, and translational support purposes only. 

It does not replace:
• Laboratory validation
• Regulatory review
• Clinical judgment
• Formal medical advice
• In vitro/in vivo experimental confirmation

Users are responsible for validating simulations and predictions in legitimate laboratory and clinical settings."""

# ============================================================
# LICENSING & PARTNERSHIPS
# ============================================================
LICENSING_CONTACT = f"""For licensing, partnerships, research collaboration, investment, or authorized commercial use, please contact:

{COMPANY_NAME}
Founder & IP Owner: {FOUNDER_NAME}
Email: {EMAIL}
Phone: {PHONE}
Website: {WEBSITE}
Location: {LOCATION}
"""

# ============================================================
# POWERED BY STATEMENT
# ============================================================
POWERED_BY = f"Powered by {COMPANY_NAME}"

# ============================================================
# BRANDING COLORS (Optional for custom CSS/styling)
# ============================================================
BRAND_COLORS = {
    "primary": "#003366",      # Deep Navy Blue
    "accent": "#0066CC",       # Bright Blue
    "light": "#E6F0F7",        # Light Blue
    "white": "#FFFFFF",
    "dark": "#1A1A1A",
    "gray": "#666666",
    "silver": "#C0C0C0",
}

# ============================================================
# FORMATTING HELPERS
# ============================================================
def get_footer_text():
    """Get formatted footer text"""
    return f"{COPYRIGHT} | {PROPRIETARY_NOTICE} | Founder & IP Owner: {FOUNDER_NAME}"

def get_header_text():
    """Get formatted header text"""
    return f"{APP_NAME}\n{TAGLINE}"

def get_contact_info():
    """Get formatted contact information"""
    contact_lines = [
        f"📧 Email: {EMAIL}",
        f"📱 Phone: {PHONE}",
        f"🌐 Website: {WEBSITE}",
        f"📍 Location: {LOCATION}",
    ]
    return " | ".join(contact_lines)

def get_company_info():
    """Get formatted company information"""
    return f"{COMPANY_NAME} | {LOCATION}"
