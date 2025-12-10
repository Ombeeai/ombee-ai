import streamlit as st
from pathlib import Path
import base64

def get_base64_image(image_path):
    """Convert image to base64 for embedding in HTML"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

# CSS for hiding sidebar on login page
LOGIN_PAGE_CSS = """
<style>
/* Hide sidebar completely on login page */
section[data-testid="stSidebar"] {
    display: none !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
}
/* Clean up spacing */
.main .block-container {
    padding-top: 2rem !important;
    max-width: 900px !important;
    margin: 0 auto !important;
}
/* Reduce spacing between elements */
.element-container {
    margin-bottom: 0.5rem !important;
}
</style>
"""

# CSS for login page styling
LOGIN_STYLES_CSS = """
<style>
/* Login page logo */
.login-logo-container {
    text-align: center;
    margin: 2rem 0 1.5rem 0;
    animation: fadeInDown 0.6s ease-out;
}

.login-logo {
    width: 120px;
    height: 120px;
    filter: drop-shadow(0 8px 24px rgba(236, 199, 25, 0.5));
    transition: transform 0.3s ease;
}

.login-logo:hover {
    transform: scale(1.05);
}

/* Login title and subtitle */
.login-title {
    text-align: center;
    font-size: 2.8rem;
    font-weight: 800;
    margin: 1.5rem 0 0.5rem 0;
    background: linear-gradient(135deg, #ECC719 0%, #FFD700 50%, #FFF176 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    animation: fadeIn 0.8s ease-out 0.2s both;
}

.login-subtitle {
    text-align: center;
    color: #999999;
    font-size: 1.05rem;
    margin-bottom: 2.5rem;
    font-weight: 400;
    animation: fadeIn 0.8s ease-out 0.3s both;
}

/* Demo info card */
.demo-info-card {
    background: linear-gradient(135deg, rgba(236, 199, 25, 0.1) 0%, rgba(255, 215, 0, 0.05) 100%);
    border: 1px solid rgba(236, 199, 25, 0.3);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    animation: fadeIn 1s ease-out 0.6s both;
}

.demo-info-title {
    color: #ECC719;
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 0.8rem;
}

.demo-credentials {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin-top: 0.8rem;
    flex-wrap: wrap;
}

.demo-credentials span {
    color: #b8b8b8;
    font-size: 0.95rem;
}

/* Animations */
@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* Login page input labels */
.stTextInput > label {
    color: #ECC719 !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    margin-bottom: 0.5rem !important;
}
</style>
"""

# CSS for hiding "Press Enter to apply" message
HIDE_INPUT_INSTRUCTIONS_CSS = """
<style>
/* Hide the "Press Enter to apply" message */
.stTextInput > div > div > input {
    caret-color: auto;
}
.stTextInput [data-testid="InputInstructions"] {
    display: none !important;
}
.stTextInput > label > div[data-testid="InputInstructions"] {
    display: none !important;
}
div[data-testid="InputInstructions"] {
    visibility: hidden !important;
    display: none !important;
}
</style>
"""

# CSS for sidebar styling (user profile, expanders, buttons)
SIDEBAR_CSS = """
<style>
/* Make sidebar expander text more visible - both collapsed and expanded */
section[data-testid="stSidebar"] details[data-testid="stExpander"] summary {
    color: #ECC719 !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    background-color: transparent !important;
}
section[data-testid="stSidebar"] details[data-testid="stExpander"][open] summary {
    color: #ECC719 !important;
    background-color: transparent !important;
}
section[data-testid="stSidebar"] details[data-testid="stExpander"] summary p {
    color: #ECC719 !important;
}
/* Remove ALL white backgrounds from expander */
section[data-testid="stSidebar"] details[data-testid="stExpander"] {
    background-color: transparent !important;
    border: none !important;
}
section[data-testid="stSidebar"] details[data-testid="stExpander"] > div {
    background-color: transparent !important;
}
section[data-testid="stSidebar"] details[data-testid="stExpander"] summary > div {
    background-color: transparent !important;
}
section[data-testid="stSidebar"] .streamlit-expanderHeader {
    background-color: transparent !important;
}
section[data-testid="stSidebar"] .streamlit-expanderContent {
    background-color: transparent !important;
}
/* Make sidebar buttons more visible */
section[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(135deg, rgba(236, 199, 25, 0.2) 0%, rgba(255, 215, 0, 0.15) 100%) !important;
    color: #ECC719 !important;
    border: 1px solid rgba(236, 199, 25, 0.4) !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: linear-gradient(135deg, rgba(236, 199, 25, 0.3) 0%, rgba(255, 215, 0, 0.25) 100%) !important;
    border-color: #ECC719 !important;
}
</style>
"""

THEME_CSS = """
<style>
/* Import Google Fonts - Matching Ombee Website */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

/* Set global font to match Ombee website - excluding icons */
html, body, .stApp {
    font-family: 'Plus Jakarta Sans', 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Apply to text elements but preserve material icons */
p:not([class*="material"]):not([class*="icon"]), 
div:not([class*="material"]):not([class*="icon"]):not([data-baseweb="icon"]), 
li:not([class*="material"]):not([class*="icon"]), 
label:not([class*="material"]):not([class*="icon"]) {
    font-family: 'Plus Jakarta Sans', 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Special handling for spans to avoid breaking icons */
span {
    font-family: inherit;
}

/* Restore Material Icons for Streamlit UI elements */
[data-testid="stExpanderToggleIcon"],
.material-icons,
[class*="material-icons"],
details[data-testid="stExpander"] summary::before,
details[data-testid="stExpander"] summary span {
    font-family: 'Material Icons', 'Material Icons Extended' !important;
}

/* Force icon font for expander toggle specifically */
details summary span[class*="Icon"] {
    font-family: 'Material Icons' !important;
}

/* Streamlit uses specific classes for icons */
span[data-baseweb="icon"],
[class*="StyledIcon"],
[class*="icon"] {
    font-family: 'Material Icons' !important;
}

/* ------ MAIN CONTAINER BACKGROUND ------ */
.main .block-container {
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 25%, #2d2d2d 50%, #1a1a1a 75%, #0a0a0a 100%);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

@keyframes gradientShift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* ------ HEADER SECTION WITH GLOWING EFFECT ------ */
.main-header {
    text-align: center;
    padding: 2.5rem 0 0.8rem 0;
    color: #ECC719;
    font-weight: 800;
    font-size: 3.5rem;
    background: linear-gradient(135deg, #ECC719 0%, #FFD700 50%, #FFF176 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    animation: fadeInDown 0.6s ease-out;
    filter: drop-shadow(0 0 20px rgba(236, 199, 25, 0.4));
}

@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.subtitle {
    text-align: center;
    color: #696969;
    font-size: 1.2rem;
    margin-bottom: 2.5rem;
    font-weight: 500;
    animation: fadeIn 0.8s ease-out 0.2s both;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* ------ DOMAIN CARDS (Vibrant Glass Morphism) ------ */
.domain-card {
    background: linear-gradient(135deg, rgba(30, 30, 30, 0.95) 0%, rgba(45, 45, 45, 0.9) 100%);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(236, 199, 25, 0.2);
    position: relative;
    overflow: hidden;
}

.domain-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #ECC719, #FFD700, #FFF176);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.domain-card:hover::before {
    opacity: 1;
}

.domain-card:hover {
    transform: translateY(-10px) scale(1.03);
    box-shadow: 
        0 20px 60px rgba(236, 199, 25, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
    border-color: rgba(236, 199, 25, 0.5);
}

.domain-card h3 {
    color: #ECC719 !important;
    margin-bottom: 0.8rem;
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    text-shadow: 0 2px 10px rgba(236, 199, 25, 0.3);
}

.domain-card p {
    color: #b8b8b8 !important;
}

/* ------ RESPONSE BOX (Elevated Design) ------ */
.response-box {
    background: linear-gradient(135deg, rgba(30, 30, 30, 0.98) 0%, rgba(40, 40, 40, 0.95) 100%);
    border-left: 6px solid #ECC719;
    padding: 2rem;
    border-radius: 16px;
    margin: 1.5rem 0;
    color: #e0e0e0;
    line-height: 1.8;
    box-shadow: 
        0 12px 40px rgba(0, 0, 0, 0.5),
        0 0 0 1px rgba(236, 199, 25, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
    position: relative;
    overflow: hidden;
    animation: slideInUp 0.5s ease-out;
}

@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.response-box::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 150px;
    height: 150px;
    background: radial-gradient(circle, rgba(236, 199, 25, 0.08) 0%, transparent 70%);
    pointer-events: none;
}

.response-box strong {
    color: #FFD700 !important;
    font-weight: 700;
    text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
}

/* ------ BUTTONS (Glowing Premium Style) ------ */
.stButton>button {
    background: linear-gradient(135deg, #ECC719 0%, #FFD700 100%) !important;
    color: #0a0a0a !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    padding: 0.9rem 1.8rem !important;
    border: none !important;
    box-shadow: 
        0 8px 25px rgba(236, 199, 25, 0.4),
        0 0 30px rgba(236, 199, 25, 0.2) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-size: 1rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #FFD700 0%, #FFF176 100%) !important;
    transform: translateY(-3px) !important;
    box-shadow: 
        0 12px 35px rgba(236, 199, 25, 0.5),
        0 0 50px rgba(236, 199, 25, 0.3) !important;
}

/* Secondary button style */
.stButton>button[kind="secondary"] {
    background: linear-gradient(135deg, rgba(236, 199, 25, 0.15) 0%, rgba(255, 215, 0, 0.1) 100%) !important;
    color: #ECC719 !important;
    border: 2px solid rgba(236, 199, 25, 0.4) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
}

.stButton>button[kind="secondary"]:hover {
    background: linear-gradient(135deg, rgba(236, 199, 25, 0.25) 0%, rgba(255, 215, 0, 0.15) 100%) !important;
    border-color: #ECC719 !important;
    transform: translateY(-2px) !important;
}

/* ------ TEXT INPUT (Glowing Focus) ------ */
.stTextInput>div>div>input {
    background: rgba(30, 30, 30, 0.9) !important;
    border: 2px solid rgba(236, 199, 25, 0.3) !important;
    border-radius: 12px !important;
    padding: 1rem 1.2rem !important;
    color: #e0e0e0 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-size: 1rem !important;
    box-shadow: 
        0 4px 15px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
}

.stTextInput>div>div>input:focus {
    border-color: #ECC719 !important;
    box-shadow: 
        0 6px 25px rgba(236, 199, 25, 0.3),
        0 0 30px rgba(236, 199, 25, 0.2) !important;
    outline: none !important;
    background: rgba(40, 40, 40, 0.95) !important;
}

.stTextInput>div>div>input::placeholder {
    color: #777777 !important;
}

/* ------ INFO / SUCCESS / WARNING BOXES ------ */
div[data-testid="stNotification"] {
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3) !important;
}

div[data-testid="stNotification"][data-baseweb="notification"] > div {
    background: linear-gradient(135deg, rgba(236, 199, 25, 0.15) 0%, rgba(255, 215, 0, 0.1) 100%) !important;
    border-left: 6px solid #ECC719 !important;
    color: #FFD700 !important;
}

/* ------ MARKDOWN TEXT IN MAIN AREA ------ */
.main .block-container h1,
.main .block-container h2,
.main .block-container h3,
.main .block-container h4 {
    color: #ECC719 !important;
}

.main .block-container p,
.main .block-container li,
.main .block-container span {
    color: #c0c0c0 !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
}

/* ------ SIDEBAR (Enhanced Dark Premium) ------ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%) !important;
    border-right: 1px solid rgba(236, 199, 25, 0.2) !important;
}

section[data-testid="stSidebar"] h3 {
    color: #ECC719 !important;
    font-weight: 700 !important;
    text-shadow: 0 2px 10px rgba(236, 199, 25, 0.3);
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li {
    color: #adadad !important;
}

section[data-testid="stSidebar"] hr {
    border-color: rgba(236, 199, 25, 0.3) !important;
    box-shadow: 0 1px 5px rgba(236, 199, 25, 0.2);
}

/* ------ METRICS (Glowing Dashboard) ------ */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(30, 30, 30, 0.9) 0%, rgba(40, 40, 40, 0.85) 100%) !important;
    padding: 1rem !important;
    border-radius: 12px !important;
    border: 1px solid rgba(236, 199, 25, 0.2) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
}

div[data-testid="stMetricValue"] {
    color: #FFD700 !important;
    text-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
}

div[data-testid="stMetricLabel"] {
    color: #999999 !important;
}

/* ------ EXPANDER ------ */
details[data-testid="stExpander"] summary {
    background: linear-gradient(135deg, rgba(30, 30, 30, 0.95) 0%, rgba(40, 40, 40, 0.9) 100%) !important;
    border-radius: 12px !important;
    color: #ECC719 !important;
    border: 1px solid rgba(236, 199, 25, 0.3) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    font-size: 0.95rem !important;
}

details[data-testid="stExpander"] summary:hover {
    border-color: #ECC719 !important;
    box-shadow: 0 6px 20px rgba(236, 199, 25, 0.2) !important;
}

/* Fix expander content text spacing */
details[data-testid="stExpander"] div[data-testid="stExpanderDetails"] p,
details[data-testid="stExpander"] div[data-testid="stExpanderDetails"] li {
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
    margin-bottom: 0.3rem !important;
    color: #c0c0c0 !important;
}

/* Prevent text overlap in expander */
details[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    padding: 0.5rem 0 !important;
    margin-top: 0.5rem !important;
}

/* Ensure expander icon displays correctly */
details[data-testid="stExpander"] summary span[data-testid="stExpanderToggleIcon"],
details[data-testid="stExpander"] summary span[class*="Icon"] {
    font-family: 'Material Icons' !important;
    font-weight: normal !important;
    font-style: normal !important;
}

/* Override font for all icon elements in expander */
details[data-testid="stExpander"] summary > div > span {
    font-family: 'Material Icons' !important;
}

/* ------ HORIZONTAL RULE ------ */
hr {
    border: none !important;
    height: 2px !important;
    background: linear-gradient(90deg, transparent 0%, #ECC719 50%, transparent 100%) !important;
    margin: 2rem 0 !important;
    box-shadow: 0 0 10px rgba(236, 199, 25, 0.3);
}

/* ------ SCROLLBAR ------ */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: #1a1a1a;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #ECC719 0%, #FFD700 100%);
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(236, 199, 25, 0.3);
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #FFD700 0%, #FFF176 100%);
}

/* ------ HIDE STREAMLIT BRANDING ------ */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

def apply_theme(from_file: str | None = None):
    """
    Inject main CSS theme into Streamlit. 
    If from_file is provided it will load CSS from that path.
    """
    if from_file:
        p = Path(from_file)
        if p.exists():
            st.markdown(p.read_text(encoding="utf-8"), unsafe_allow_html=True)
            return
    st.markdown(THEME_CSS, unsafe_allow_html=True)

def apply_login_page_styles():
    """Apply CSS specific to the login page (hides sidebar, adjusts layout)"""
    st.markdown(LOGIN_PAGE_CSS, unsafe_allow_html=True)
    st.markdown(HIDE_INPUT_INSTRUCTIONS_CSS, unsafe_allow_html=True)

def apply_login_styles():
    """Apply login-specific styles (logo, title, demo card)"""
    st.markdown(LOGIN_STYLES_CSS, unsafe_allow_html=True)
    st.markdown(HIDE_INPUT_INSTRUCTIONS_CSS, unsafe_allow_html=True)

def apply_main_page_styles():
    """Apply CSS specific to the main page (input instructions, etc.)"""
    st.markdown(HIDE_INPUT_INSTRUCTIONS_CSS, unsafe_allow_html=True)

def apply_sidebar_styles():
    """Apply CSS for sidebar styling (expanders, buttons)"""
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)