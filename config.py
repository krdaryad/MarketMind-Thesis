"""
Global configuration, CSS, and constants.
"""
import streamlit as st
from datetime import datetime
import warnings
import os

warnings.filterwarnings('ignore')

# ============================================================================
# DEBUG SETTINGS
# ============================================================================
DEBUG_MODE = False  # Set to False in production

# ============================================================================
# FILE PATHS
# ============================================================================
CSV_FILE_PATH = "reddit_posts_clean.csv"
MODELS_DIR = "models/"

# Create models directory if it doesn't exist
os.makedirs(MODELS_DIR, exist_ok=True)

# ============================================================================
# NOTE: st.set_page_config() has been REMOVED from here.
# It must be the FIRST command in your main.py file.
# Add this to main.py:
#
# st.set_page_config(
#     page_title="MarketMind - AI Consumer Behavior Analysis",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )
# ============================================================================

# ============================================================================
# BASE CSS (Common to both themes)
# ============================================================================
BASE_CSS = """
<style>
/* ===== 1. GLOBAL STYLES & GRID BACKGROUND ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

.stApp {
    font-family: 'Inter', sans-serif;
    overflow-x: hidden;
    transition: all 0.3s ease;
}

/* ===== 2. SCANNING BAR ANIMATION ===== */
@keyframes global-scan {
    0% { transform: translateY(-100vh); }
    100% { transform: translateY(100vh); }
}

.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 120px;
    background: linear-gradient(to bottom, 
        transparent, 
        rgba(59, 130, 246, 0.1), 
        rgba(59, 130, 246, 0.2), 
        rgba(59, 130, 246, 0.1), 
        transparent);
    z-index: 9999;
    pointer-events: none;
    animation: global-scan 10s linear infinite;
}

/* ===== 3. GLASS‑MORPHISM CARDS ===== */
.card, .metric-card {
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover, .metric-card:hover {
    transform: translateY(-5px);
}

/* ===== 4. PULSING LED NODE ===== */
.led-node {
    height: 10px;
    width: 10px;
    background-color: #3B82F6;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 12px #3B82F6;
    animation: pulse 2s infinite;
    margin-right: 12px;
}

@keyframes pulse {
    0% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.9); }
    100% { opacity: 1; transform: scale(1); }
}

/* ===== 5. TECH METRICS ===== */
.tech-val {
    font-family: 'Courier New', monospace;
    font-size: 2.2rem;
    font-weight: 900;
    margin: 0;
}

.tech-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 0;
}

/* ===== 6. SIDEBAR STYLING ===== */
[data-testid="stSidebar"] {
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(59, 130, 246, 0.2);
    transition: all 0.3s ease;
}

/* ===== 7. TOP MENU BUTTONS ===== */
.top-menu {
    margin-bottom: 1rem;
}
.top-menu button {
    backdrop-filter: blur(10px);
    border-radius: 12px !important;
    transition: all 0.2s ease;
    font-size: 0.8rem !important;
    padding: 0.5rem 0.25rem !important;
}
.top-menu button:hover {
    transform: translateY(-2px);
}
.top-menu button[data-testid="baseButton-primary"] {
    background: transparent !important;
    border-bottom: 2px solid #3B82F6 !important;
    font-weight: 600;
    box-shadow: 0 0 8px rgba(59,130,246,0.6);
}

/* ===== 8. LOADING SPINNER ===== */
.loading-spinner {
    display: inline-block;
    width: 40px;
    height: 40px;
    border: 3px solid rgba(59,130,246,0.3);
    border-radius: 50%;
    border-top-color: #3B82F6;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* ===== 9. TOOLTIPS ===== */
.tooltip {
    position: relative;
    display: inline-block;
    cursor: help;
}
.tooltip .tooltip-text {
    visibility: hidden;
    background-color: #1A1D24;
    text-align: center;
    border-radius: 6px;
    padding: 0.25rem 0.5rem;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    white-space: nowrap;
    font-size: 0.7rem;
}
.tooltip:hover .tooltip-text {
    visibility: visible;
}

/* ===== 10. PROGRESS BAR ===== */
.progress-bar {
    width: 100%;
    height: 6px;
    border-radius: 3px;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #3B82F6, #F59E0B);
    border-radius: 3px;
    transition: width 0.3s ease;
}

/* ===== 11. ANOMALY ALERT ===== */
.anomaly-alert {
    border-left: 4px solid #EF4444;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}

/* ===== 12. PAGINATION ===== */
.pagination {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin: 1rem 0;
}

/* ===== 13. DATA TABLE STYLING ===== */
.dataframe {
    border-radius: 12px;
    overflow: hidden;
}

/* ===== 14. TEXT MUTED ===== */
.text-muted {
    font-size: 0.85rem;
}

/* ===== 15. CARD DESCRIPTION ===== */
.card-description {
    font-size: 0.85rem;
    line-height: 1.5;
    margin-top: 0.5rem;
}

/* Modern Button Styling */
div.stButton > button {
    border-radius: 12px !important;
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
    background: rgba(59, 130, 246, 0.05) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
}

div.stButton > button:hover {
    transform: translateY(-2px) !important;
    background: rgba(59, 130, 246, 0.15) !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2) !important;
    border-color: #3B82F6 !important;
}

/* Primary Button Styling */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
}

div.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
    transform: translateY(-3px) scale(1.02) !important;
}

/* Disabled button styling */
div.stButton > button:disabled {
    opacity: 0.5 !important;
    transform: none !important;
}

/* ===== SMALLER BUTTONS - GLOBAL OVERRIDE ===== */
/* Sidebar buttons specifically */
[data-testid="stSidebar"] .stButton > button {
    font-size: 0.65rem !important;
    padding: 0.2rem 0.4rem !important;
    min-height: 26px !important;
}

/* Refresh button in sidebar */
[data-testid="stSidebar"] .stButton button {
    font-size: 0.6rem !important;
    padding: 0.2rem 0.3rem !important;
    min-height: 24px !important;
}

/* ===== SIDEBAR TEXT-ONLY BUTTONS ===== */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0.25rem 0 !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    color: #8A8F99 !important;
    text-align: left !important;
    border-radius: 0 !important;
    transition: all 0.2s ease !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    color: #3B82F6 !important;
    text-decoration: underline !important;
    background: transparent !important;
    transform: none !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] .stButton > button:active,
[data-testid="stSidebar"] .stButton > button:focus {
    background: transparent !important;
    border: none !important;
    outline: none !important;
}

/* Primary buttons in sidebar (keep subtle) */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: transparent !important;
    color: #3B82F6 !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    color: #2563EB !important;
    text-decoration: underline !important;
}

/* Download buttons in sidebar */
[data-testid="stSidebar"] .stDownloadButton button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #8A8F99 !important;
    text-align: left !important;
    padding: 0.25rem 0 !important;
}

[data-testid="stSidebar"] .stDownloadButton button:hover {
    color: #3B82F6 !important;
    text-decoration: underline !important;
    background: transparent !important;
}

/* ===== EXPANDER STYLING ===== */
.streamlit-expanderHeader {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 0 !important;
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    color: #8A8F99 !important;
    text-transform: uppercase !important;
    box-shadow: none !important;
    border-radius: 0 !important;
}

.streamlit-expanderHeader:hover {
    color: #3B82F6 !important;
    background: transparent !important;
}

.streamlit-expanderHeader svg {
    display: none !important;
}

.streamlit-expanderHeader p {
    margin: 0 !important;
}

/* Content area styling */
.streamlit-expanderContent {
    background: transparent !important;
    border: none !important;
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
}

</style>
"""

# ============================================================================
# DARK MODE CSS (with Streamlit native element overrides)
# ============================================================================
DARK_CSS = """
<style>
/* Dark mode overrides */
.stApp {
    background-color: #05070A;
    background-image: 
        linear-gradient(rgba(59, 130, 246, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59, 130, 246, 0.05) 1px, transparent 1px);
    background-size: 45px 45px;
    color: #E2E8F0;
}

/* Custom Cards */
.card, .metric-card {
    background: rgba(10, 15, 25, 0.7);
    border: 1px solid rgba(59, 130, 246, 0.1);
}

.card:hover, .metric-card:hover {
    border-color: #3B82F6;
    box-shadow: 0 0 40px rgba(59, 130, 246, 0.15);
}

/* Text colors */
.text-muted {
    color: #8A8F99 !important;
}

.card-description {
    color: #94A3B8;
}

.tech-val {
    color: #FFFFFF;
    text-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
}

.tech-label {
    color: #64748B;
}

/* Streamlit Sidebar */
[data-testid="stSidebar"] {
    background-color: rgba(10, 15, 25, 0.95) !important;
    border-right: 1px solid rgba(59, 130, 246, 0.2);
}

/* Streamlit Top Menu/Hamburger */
[data-testid="stToolbar"] {
    background-color: rgba(10, 15, 25, 0.9) !important;
}

[data-testid="stDecoration"] {
    background: linear-gradient(90deg, #3B82F6, #F59E0B) !important;
}

/* Streamlit Status Widgets */
[data-testid="stStatusWidget"] {
    background-color: rgba(10, 15, 25, 0.9) !important;
    color: #E2E8F0 !important;
}

/* Streamlit Markdown */
.stMarkdown, .stText, .stDataFrame, .stAlert {
    color: #E2E8F0;
}

/* Streamlit Buttons */
.stButton > button {
    background: rgba(59, 130, 246, 0.2);
    border: 1px solid rgba(59, 130, 246, 0.3);
    color: #E2E8F0;
}

.stButton > button:hover {
    background: rgba(59, 130, 246, 0.4);
    border-color: #3B82F6;
}

/* Streamlit Selectboxes, Inputs */
.stSelectbox > div, .stTextInput > div, .stNumberInput > div {
    background: rgba(10, 15, 25, 0.8);
    border-color: rgba(59, 130, 246, 0.3);
    color: #E2E8F0;
}

/* Streamlit Metrics */
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}

[data-testid="stMetricLabel"] p {
    color: #8A8F99 !important;
}

/* Streamlit Tabs */
button[data-baseweb="tab"] p {
    color: #8A8F99 !important;
}

button[aria-selected="true"] p {
    color: #3B82F6 !important;
}

/* Streamlit Expanders */
.streamlit-expanderHeader {
    background: rgba(10, 15, 25, 0.8);
    color: #E2E8F0;
    border-radius: 8px;
}

/* Streamlit DataFrames */
[data-testid="stDataFrameResizable"], [data-testid="stTable"] {
    background-color: rgba(10, 15, 25, 0.8) !important;
    color: #E2E8F0 !important;
}

/* Streamlit Dropdown Menus */
div[data-baseweb="select"] > div {
    background-color: rgba(10, 15, 25, 0.9) !important;
    color: #E2E8F0 !important;
}

div[data-baseweb="popover"] ul {
    background-color: #0A0F19 !important;
}

div[data-baseweb="popover"] li {
    background-color: #0A0F19 !important;
    color: #E2E8F0 !important;
}

div[data-baseweb="popover"] li:hover {
    background-color: #1A1D24 !important;
    color: #3B82F6 !important;
}

/* Streamlit Info/Warning/Success */
.stAlert {
    background: rgba(10, 15, 25, 0.9) !important;
}

/* Streamlit Spinner */
.stSpinner > div {
    border-color: #3B82F6 !important;
}

/* Top Menu Buttons */
.top-menu button {
    background: rgba(10, 15, 25, 0.7) !important;
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
    color: #8A8F99 !important;
}

.top-menu button:hover {
    background: linear-gradient(135deg, rgba(59,130,246,0.3), rgba(59,130,246,0.1)) !important;
    border-color: #3B82F6 !important;
    color: #FFFFFF !important;
}

.top-menu button[data-testid="baseButton-primary"] {
    border-bottom: 2px solid #3B82F6 !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 8px rgba(59,130,246,0.6);
}

.tooltip .tooltip-text {
    background-color: #1A1D24;
    color: #8A8F99;
}

.progress-bar {
    background: #1A1D24;
}

.anomaly-alert {
    background: linear-gradient(135deg, rgba(239,68,68,0.2), rgba(239,68,68,0.05));
}

.dataframe {
    background: #111317;
    color: #E2E8F0;
}

/* ===== THEME-AWARE TEXT CLASSES ===== */
.theme-text-primary {
    color: #E2E8F0 !important;
}
.theme-text-secondary {
    color: #8A8F99 !important;
}
.theme-text-accent {
    color: #3B82F6 !important;
}
.theme-text-positive {
    color: #10B981 !important;
}
.theme-text-negative {
    color: #EF4444 !important;
}
.theme-text-warning {
    color: #F59E0B !important;
}

/* ===== THEME-AWARE BACKGROUNDS ===== */
.theme-bg-card {
    background: rgba(10, 15, 25, 0.7) !important;
    border: 1px solid rgba(59, 130, 246, 0.2) !important;
}
.theme-bg-positive-light {
    background: rgba(16, 185, 129, 0.1) !important;
}
.theme-bg-negative-light {
    background: rgba(239, 68, 68, 0.1) !important;
}
.theme-bg-warning-light {
    background: rgba(245, 158, 11, 0.1) !important;
}
.theme-bg-info-light {
    background: rgba(59, 130, 246, 0.05) !important;
}

/* ===== THEME-AWARE BORDERS ===== */
.theme-border-positive {
    border-left: 3px solid #10B981 !important;
}
.theme-border-negative {
    border-left: 3px solid #EF4444 !important;
}
.theme-border-warning {
    border-left: 3px solid #F59E0B !important;
}
.theme-border-info {
    border-left: 3px solid #3B82F6 !important;
}

/* ===== METRIC CARD STYLES ===== */
.metric-value {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 0;
}
.metric-label {
    font-size: 0.7rem;
    color: #8A8F99;
    margin: 0;
}
.duration-badge, .info-badge {
    background: #1A1D24;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.75rem;
    display: inline-block;
}
.info-badge {
    background: #1A1D24;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.75rem;
    display: inline-block;
    color: #8A8F99;
}
</style>
"""

# ============================================================================
# LIGHT MODE CSS (with Streamlit native element overrides)
# ============================================================================
LIGHT_CSS = """
<style>
/* 1. Global Background & Text */
.stApp {
    background-color: #F1F5F9;
    background-image: 
        linear-gradient(rgba(59, 130, 246, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59, 130, 246, 0.05) 1px, transparent 1px);
    background-size: 40px 40px;
    color: #0F172A;
}

/* Text colors */
.text-muted {
    color: #64748B !important;
}

.card-description {
    color: #475569;
}

/* 2. Enhanced Card Visibility */
.card, .metric-card {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
}

.card:hover, .metric-card:hover {
    border-color: #3B82F6 !important;
    box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1);
    transform: translateY(-4px);
}

/* 3. Tech Metrics Contrast */
.tech-val {
    color: #1E40AF !important;
    text-shadow: none !important;
}

.tech-label {
    color: #64748B !important;
    font-weight: 600;
}

/* 4. Sidebar Light Mode */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}

/* 5. Streamlit Toolbar */
[data-testid="stToolbar"] {
    background-color: #FFFFFF !important;
}

[data-testid="stDecoration"] {
    background: linear-gradient(90deg, #3B82F6, #F59E0B) !important;
}

/* 6. Inputs & Buttons */
.stButton > button {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
    border: 1px solid #CBD5E1 !important;
    transition: all 0.2s;
}

.stButton > button:hover {
    border-color: #3B82F6 !important;
    color: #3B82F6 !important;
    background-color: #F8FAFC !important;
}

/* Primary buttons */
.stButton button[data-testid="baseButton-primary"] {
    background-color: #3B82F6 !important;
    color: white !important;
    border: none !important;
}

/* 7. Form Inputs */
.stSelectbox > div, .stTextInput > div, .stNumberInput > div {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
}

/* 8. Markdown Visibility */
h1, h2, h3 {
    color: #0F172A !important;
}

.stMarkdown p {
    color: #334155 !important;
    line-height: 1.6;
}

/* 9. Scanline Adjustment for Light Mode */
.stApp::before {
    background: linear-gradient(to bottom, 
        transparent, 
        rgba(59, 130, 246, 0.03), 
        rgba(59, 130, 246, 0.07), 
        rgba(59, 130, 246, 0.03), 
        transparent) !important;
}

/* 10. Streamlit Widgets Light Mode */
[data-testid="stWidgetLabel"] p {
    color: #1E293B !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: #1E40AF !important;
}

[data-testid="stMetricLabel"] p {
    color: #64748B !important;
}

/* 11. Tabs */
button[data-baseweb="tab"] p {
    color: #64748B !important;
}

button[aria-selected="true"] p {
    color: #3B82F6 !important;
    font-weight: 700 !important;
}

/* 12. DataFrames */
[data-testid="stTable"], [data-testid="stDataFrame"], [data-testid="stDataFrameResizable"] {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
    border: 1px solid #E2E8F0 !important;
}

.stDataFrame thead tr th {
    background-color: #F8FAFC !important;
    color: #475569 !important;
    font-weight: 600 !important;
}

[data-testid="stDataFrameResizable"] div:hover {
    background-color: #F1F5F9 !important;
}

/* 13. Expanders */
.streamlit-expanderHeader {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
    border-bottom: 1px solid #F1F5F9 !important;
}

/* 14. Dropdown Pickers */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
    border-color: #E2E8F0 !important;
}

div[data-baseweb="popover"] ul {
    background-color: #FFFFFF !important;
}

div[data-baseweb="popover"] li {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
}

div[data-baseweb="popover"] li:hover {
    background-color: #F1F5F9 !important;
    color: #3B82F6 !important;
}

div[data-baseweb="popover"] li [aria-selected="true"] {
    background-color: #EFF6FF !important;
    color: #3B82F6 !important;
}

div[data-baseweb="select"] div[aria-hidden="true"] {
    color: #94A3B8 !important;
}

/* 15. Status Widgets */
[data-testid="stStatusWidget"] {
    background-color: #FFFFFF !important;
}

/* 16. Alerts */
.stAlert {
    background-color: #FFFFFF !important;
}

/* ===== THEME-AWARE TEXT CLASSES ===== */
.theme-text-primary {
    color: #0F172A !important;
}
.theme-text-secondary {
    color: #64748B !important;
}
.theme-text-accent {
    color: #2563EB !important;
}
.theme-text-positive {
    color: #059669 !important;
}
.theme-text-negative {
    color: #DC2626 !important;
}
.theme-text-warning {
    color: #D97706 !important;
}

/* ===== THEME-AWARE BACKGROUNDS ===== */
.theme-bg-card {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
}
.theme-bg-positive-light {
    background: rgba(5, 150, 105, 0.08) !important;
}
.theme-bg-negative-light {
    background: rgba(220, 38, 38, 0.08) !important;
}
.theme-bg-warning-light {
    background: rgba(217, 119, 6, 0.08) !important;
}
.theme-bg-info-light {
    background: rgba(37, 99, 235, 0.05) !important;
}

/* ===== THEME-AWARE BORDERS ===== */
.theme-border-positive {
    border-left: 3px solid #059669 !important;
}
.theme-border-negative {
    border-left: 3px solid #DC2626 !important;
}
.theme-border-warning {
    border-left: 3px solid #D97706 !important;
}
.theme-border-info {
    border-left: 3px solid #2563EB !important;
}

/* ===== METRIC CARD STYLES ===== */
.metric-value {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 0;
    color: #0F172A;
}
.metric-label {
    font-size: 0.7rem;
    color: #64748B;
    margin: 0;
}
.duration-badge, .info-badge {
    background: #F1F5F9;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.75rem;
    display: inline-block;
    color: #475569;
}
.info-badge {
    background: #F1F5F9;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.75rem;
    display: inline-block;
    color: #475569;
}
</style>
"""

# ============================================================================
# MOBILE CSS
# ============================================================================
MOBILE_CSS = """
<style>
/* Mobile Responsive Styles */
@media (max-width: 768px) {
    .metric-card {
        padding: 0.75rem !important;
        margin-bottom: 0.5rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    
    .metric-card:active {
        transform: scale(0.98) !important;
        background: rgba(59,130,246,0.15) !important;
    }
    
    button, .stButton button, .stDownloadButton button {
        min-height: 48px !important;
        min-width: 48px !important;
        border-radius: 12px !important;
        margin: 4px 0 !important;
    }
    
    .stSelectbox div[data-baseweb="select"] > div {
        min-height: 48px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto !important;
        overflow-y: hidden !important;
        flex-wrap: nowrap !important;
        -webkit-overflow-scrolling: touch !important;
    }
    
    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.25rem !important; }
    h3 { font-size: 1.1rem !important; }
    
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* Force sidebar to be collapsible and narrower */
    [data-testid="stSidebar"] {
        width: 280px !important;
        min-width: 280px !important;
        max-width: 280px !important;
        position: fixed !important;
        z-index: 1000 !important;
        height: 100% !important;
        transform: translateX(-100%);
        transition: transform 0.3s ease !important;
    }
    
    /* Show sidebar when expanded */
    [data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0) !important;
    }
    
    /* Main content takes full width */
    [data-testid="stMain"] {
        width: 100% !important;
        margin-left: 0 !important;
    }
    
    /* Chart containers - prevent overflow */
    .stPlotlyChart {
        overflow-x: auto !important;
    }
    
    .js-plotly-plot {
        min-width: 300px !important;
    }
    
    /* Plotly legend - make horizontal on mobile */
    .legend {
        display: flex !important;
        flex-wrap: wrap !important;
        justify-content: center !important;
        gap: 0.5rem !important;
    }
    
    .legend .traces {
        display: inline-block !important;
        width: auto !important;
    }
    
    /* Data tables - horizontal scroll */
    .stDataFrame {
        overflow-x: auto !important;
        display: block !important;
        white-space: nowrap !important;
    }
    
    /* Metric cards grid - apply to actual metrics */
    div[data-testid="stMetric"] {
        width: 48% !important;
        display: inline-block !important;
        margin: 1% !important;
    }
    
    /* Stack columns on mobile */
    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    
    /* Reduce spacing between elements */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* Hide less important elements on mobile (optional) */
    .system-kernel-footer {
        display: none !important;
    }
    
    /* Make buttons full width on mobile */
    .stButton button {
        width: 100% !important;
    }
    
    /* Adjust expander for touch */
    .streamlit-expanderHeader {
        padding: 0.75rem 0 !important;
    }
    
    /* Better spacing for selectboxes */
    .stSelectbox label {
        font-size: 0.8rem !important;
    }
    
    /* Make tabs scrollable horizontally */
    .stTabs [data-baseweb="tab-list"] {
        display: flex !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        white-space: nowrap !important;
        gap: 0.25rem !important;
        padding-bottom: 0.5rem !important;
        scrollbar-width: thin !important;
        -webkit-overflow-scrolling: touch !important;
    }
    
    /* Individual tab buttons */
    .stTabs [data-baseweb="tab"] {
        flex: 0 0 auto !important;
        white-space: nowrap !important;
        padding: 0.5rem 0.75rem !important;
        font-size: 0.75rem !important;
        min-width: auto !important;
    }
    
    /* Tab content area */
    .stTabs [data-testid="stTabPanel"] {
        padding-top: 0.75rem !important;
    }
    
    /* Hide scrollbar on Webkit browsers (optional - cleaner look) */
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        height: 3px !important;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
        background: #1A1D24 !important;
        border-radius: 3px !important;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
        background: #3B82F6 !important;
        border-radius: 3px !important;
    }
}

/* Small phones (max-width: 480px) */
@media (max-width: 480px) {
    /* Even smaller fonts */
    h1 {
        font-size: 1.2rem !important;
    }
    
    .tech-val {
        font-size: 1rem !important;
    }
    
    /* Single column for metrics */
    div[data-testid="stMetric"] {
        width: 100% !important;
        margin: 0.25rem 0 !important;
    }
    
    /* Hide secondary metrics row on very small screens */
    .secondary-metrics {
        display: none !important;
    }
    
    /* Reduce chart height further */
    .js-plotly-plot {
        height: 250px !important;
    }
}

@media (min-width: 769px) and (max-width: 1024px) {
    .metric-card {
        padding: 1rem !important;
    }
}
</style>
"""

# ============================================================================
# THEME MANAGEMENT
# ============================================================================
def get_theme_css(is_dark=True):
    """Return the appropriate CSS based on theme."""
    base = BASE_CSS
    if is_dark:
        return base + DARK_CSS + MOBILE_CSS
    else:
        return base + LIGHT_CSS + MOBILE_CSS

def apply_theme():
    """Apply the current theme CSS to the app."""
    is_dark = st.session_state.get('dark_mode', True)
    css = get_theme_css(is_dark)
    st.markdown(css, unsafe_allow_html=True)

def get_plotly_template():
    """Return the appropriate Plotly template based on current theme."""
    if st.session_state.get('dark_mode', True):
        return "plotly_dark"
    else:
        return "plotly_white"

# ============================================================================
# CATEGORY MAPPING
# ============================================================================
CATEGORIES = {
    "GLOBAL MACRO": [
        "Economic Dashboard",
        "Causality Analysis"
    ],
    "2021 STOCK CASE STUDY": [
        "Dashboard",
        "Sentiment Trends",
        "Entity Analysis",
        "Company Comparison",
        "Volatility Analysis",
        "Event Impact"
    ],
    "AI ENGINE & PATTERN MINING": [
        "AI Analysis",
        "Correlation Analysis",
        "Pattern Mining",
        "Classifier Demo",
        "Model Accuracy"
    ],
    "KNOWLEDGE & THEORY": [
        "Market History",
        "Learning Hub",
        "Methodology",
        "Glossary"
    ]
}

# ============================================================================
# DEFAULTS
# ============================================================================
DEFAULT_START = datetime(2021, 2, 1)
DEFAULT_END = datetime(2021, 2, 28)

# ============================================================================
# COMPANY MAPPINGS
# ============================================================================
COMPANY_TICKERS = {
    'Apple': 'AAPL',
    'Tesla': 'TSLA',
    'Amazon': 'AMZN',
    'Google': 'GOOGL',
    'Microsoft': 'MSFT',
    'GOOG': 'GOOGL',
    'AMZN': 'AMZN',
    'TSLA': 'TSLA',
    'AAPL': 'AAPL',
    'MSFT': 'MSFT'
}

# ============================================================================
# COLOR SCHEME
# ============================================================================
COLORS = {
    'positive': '#10B981',
    'neutral': '#8A8F99',
    'negative': '#EF4444',
    'primary': '#3B82F6',
    'secondary': '#F59E0B'
}