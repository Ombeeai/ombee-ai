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

THEME_CSS = """
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

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
    color: #b8b8b8;
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
    color: #b8b8b8 !important;
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
}

details[data-testid="stExpander"] summary:hover {
    border-color: #ECC719 !important;
    box-shadow: 0 6px 20px rgba(236, 199, 25, 0.2) !important;
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
    Inject CSS into Streamlit. If from_file is provided it will load CSS from that path.
    """
    if from_file:
        p = Path(from_file)
        if p.exists():
            st.markdown(p.read_text(encoding="utf-8"), unsafe_allow_html=True)
            return
    st.markdown(THEME_CSS, unsafe_allow_html=True)