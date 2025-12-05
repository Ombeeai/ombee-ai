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

/* ------ GLOBAL APP BACKGROUND ------ */
.stApp {
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%) !important;
    color: #1a1a1a !important;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* ------ HEADER SECTION WITH GRADIENT ------ */
.main-header {
    text-align: center;
    padding: 2.5rem 0 0.8rem 0;
    color: #1a1a1a;
    font-weight: 800;
    font-size: 3rem;
    background: linear-gradient(135deg, #ECC719 0%, #FFD700 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    animation: fadeInDown 0.6s ease-out;
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
    color: #666666;
    font-size: 1.2rem;
    margin-bottom: 2.5rem;
    font-weight: 500;
    animation: fadeIn 0.8s ease-out 0.2s both;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

/* ------ DOMAIN CARDS (Modern Glass Morphism) ------ */
.domain-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(236, 199, 25, 0.1);
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
    background: linear-gradient(90deg, #ECC719, #FFD700);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.domain-card:hover::before {
    opacity: 1;
}

.domain-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 16px 48px rgba(236, 199, 25, 0.15);
    border-color: rgba(236, 199, 25, 0.3);
}

.domain-card h3 {
    color: #1a1a1a;
    margin-bottom: 0.8rem;
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: -0.01em;
}

/* ------ RESPONSE BOX (Premium Design) ------ */
.response-box {
    background: linear-gradient(135deg, #ffffff 0%, #fafafa 100%);
    border-left: 6px solid #ECC719;
    padding: 2rem;
    border-radius: 16px;
    margin: 1.5rem 0;
    color: #1a1a1a;
    line-height: 1.8;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
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
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(236, 199, 25, 0.03) 0%, transparent 70%);
    pointer-events: none;
}

.response-box p {
    color: #2a2a2a !important;
    font-size: 1.05rem;
    margin-bottom: 0.8rem;
}

.response-box strong {
    color: #D0A310;
    font-weight: 700;
}

/* ------ BUTTONS (Premium Ombee Style) ------ */
.stButton>button {
    background: linear-gradient(135deg, #ECC719 0%, #FFD700 100%);
    color: #1a1a1a;
    font-weight: 600;
    border-radius: 12px;
    padding: 0.9rem 1.8rem;
    border: none;
    box-shadow: 0 6px 20px rgba(236, 199, 25, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-size: 1rem;
    position: relative;
    overflow: hidden;
}

.stButton>button::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}

.stButton>button:hover::before {
    width: 300px;
    height: 300px;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #D0A310 0%, #ECC719 100%);
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(236, 199, 25, 0.4);
}

.stButton>button:active {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(236, 199, 25, 0.3);
}

/* ------ TEXT INPUT (Modern Focus State) ------ */
.stTextInput>div>div>input {
    background: #ffffff;
    border: 2px solid #e8e8e8;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    color: #1a1a1a;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-size: 1rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stTextInput>div>div>input:focus {
    border-color: #ECC719;
    box-shadow: 0 4px 20px rgba(236, 199, 25, 0.2);
    outline: none;
    transform: translateY(-2px);
}

.stTextInput>div>div>input::placeholder {
    color: #999999;
}

/* ------ INFO / SUCCESS / WARNING BOXES (Enhanced) ------ */
.stInfo, .stSuccess, .stWarning {
    border-radius: 12px !important;
    color: #333333 !important;
    padding: 1rem 1.2rem !important;
    font-weight: 500 !important;
    animation: slideInRight 0.4s ease-out;
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.stInfo {
    background: linear-gradient(135deg, #FFF8E1 0%, #FFFBF0 100%) !important;
    border-left: 6px solid #ECC719 !important;
    box-shadow: 0 4px 12px rgba(236, 199, 25, 0.1);
}

.stSuccess {
    background: linear-gradient(135deg, #E8F5E9 0%, #F1F8F2 100%) !important;
    border-left: 6px solid #4CAF50 !important;
    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.1);
}

.stWarning {
    background: linear-gradient(135deg, #FFF3E0 0%, #FFF9F0 100%) !important;
    border-left: 6px solid #FF9800 !important;
    box-shadow: 0 4px 12px rgba(255, 152, 0, 0.1);
}

/* ------ SIDEBAR (Premium Dark Mode) ------ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%) !important;
    border-right: none;
    box-shadow: 2px 0 20px rgba(0, 0, 0, 0.1);
}

section[data-testid="stSidebar"] .stMarkdown {
    color: #e0e0e0 !important;
}

section[data-testid="stSidebar"] h3 {
    color: #ECC719 !important;
    font-weight: 700;
    margin-bottom: 1rem;
}

section[data-testid="stSidebar"] p {
    color: #b8b8b8 !important;
    line-height: 1.6;
}

section[data-testid="stSidebar"] hr {
    border-color: rgba(236, 199, 25, 0.2) !important;
    margin: 1.5rem 0;
}

/* ------ EXPANDER (Modern Accordion) ------ */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #ffffff 0%, #f8f8f8 100%) !important;
    border-radius: 12px;
    padding: 0.8rem 1.2rem;
    color: #1a1a1a !important;
    border: 1px solid #e8e8e8;
    transition: all 0.3s ease;
    font-weight: 600;
}

.streamlit-expanderHeader:hover {
    background: linear-gradient(135deg, #FFF8E1 0%, #ffffff 100%) !important;
    border-color: #ECC719;
    transform: translateX(4px);
}

/* ------ METRICS (Dashboard Style) ------ */
[data-testid="stMetricValue"] {
    color: #ECC719 !important;
    font-weight: 800 !important;
    font-size: 2rem !important;
}

[data-testid="stMetricLabel"] {
    color: #999999 !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
}

[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.5);
    padding: 1rem;
    border-radius: 12px;
    border: 1px solid rgba(236, 199, 25, 0.1);
}

/* ------ GENERAL TEXT ENHANCEMENTS ------ */
h1, h2, h3, h4, h5, h6 {
    color: #1a1a1a !important;
    font-weight: 700;
    letter-spacing: -0.01em;
}

p, li, span {
    color: #444444 !important;
    line-height: 1.7;
}

/* ------ HORIZONTAL RULE ------ */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, #ECC719 50%, transparent 100%);
    margin: 2rem 0;
}

/* ------ SPINNER (Loading Animation) ------ */
.stSpinner > div {
    border-top-color: #ECC719 !important;
}

/* ------ SCROLLBAR STYLING ------ */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #ECC719 0%, #FFD700 100%);
    border-radius: 10px;
    transition: background 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #D0A310 0%, #ECC719 100%);
}

/* ------ EXAMPLE QUERY BUTTONS ------ */
.stButton>button[key^="example_"] {
    background: #ffffff;
    color: #1a1a1a;
    border: 2px solid #e8e8e8;
    font-weight: 500;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    padding: 0.7rem 1.2rem;
}

.stButton>button[key^="example_"]:hover {
    background: #FFF8E1;
    border-color: #ECC719;
    color: #1a1a1a;
    box-shadow: 0 4px 16px rgba(236, 199, 25, 0.2);
}

/* ------ RESPONSIVE DESIGN ------ */
@media (max-width: 768px) {
    .main-header {
        font-size: 2rem;
        padding: 1.5rem 0 0.5rem 0;
    }
    
    .subtitle {
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .domain-card {
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .response-box {
        padding: 1.5rem;
    }
}

/* ------ PULSE ANIMATION FOR ACTIVE STATUS ------ */
@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.7;
    }
}

.domain-card p[style*="color: #4CAF50"] {
    animation: pulse 2s ease-in-out infinite;
}
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