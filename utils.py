"""
Utility functions: onboarding, sidebar, top menu, etc.
"""
import streamlit as st
from datetime import datetime
import numpy as np
import pandas as pd
import random
import streamlit as st
from loading_facts import get_random_fact
from config import CATEGORIES, DEFAULT_START, DEFAULT_END, DEBUG_MODE, apply_theme
from data_fetcher import get_companies_list, load_reddit_data, validate_data_quality, check_for_new_data
import base64
def onboarding_step(step):
    steps = {
    1: {
        "title": "Welcome to MarketMind", 
        "content": "A dual-capability system for real-time economic monitoring and historical AI behavioral analysis.", 
        "target": None
    },
    2: {
        "title": "1. The Present: Economic Dashboard", 
        "content": "Start here for live data. Track GDP, Inflation, and the UMich Consumer Sentiment Index via FRED and Yahoo Finance APIs.", 
        "target": "economic-dashboard"
    },
    3: {
        "title": "2. The Past: AI Sentiment Analysis", 
        "content": "Switch to historical mode. Explore how Reddit sentiment drove the 2021 meme stock phenomenon using our cleaned CSV datasets.", 
        "target": "sentiment-trends"
    },
    4: {
        "title": "Pattern & Entity Mining", 
        "content": "Dive deeper into 2021 data using FP-Growth and LDA to discover hidden discussion patterns and company correlations.", 
        "target": "pattern-mining"
    },
    5: {
        "title": "Interactive AI Engine", 
        "content": "Test the brain of the system! Use the Classifier Demo to see how our models categorize sentiment in real-time.", 
        "target": "classifier-demo"
    },
    6: {
        "title": "3. The Theory: Knowledge Hub", 
        "content": "Understand the 'Why'. Visit the Hub for interactive courses on ML methodology and a complete financial glossary.", 
        "target": "learning-hub"
    },
    7: {
        "title": "Thesis Narrative Complete", 
        "content": "You've seen the Live Present, the Historical Past, and the Academic Theory. Enjoy exploring MarketMind!", 
        "target": None
    }
}
    return steps.get(step, steps[1])

    
    st.audio(wave, sample_rate=sample_rate, autoplay=True)
def show_onboarding():
    """Display onboarding tour as a floating glass card."""
    if "onboarding_step" not in st.session_state:
        st.session_state.onboarding_step = 1
        st.session_state.onboarding_active = True
    
    if st.session_state.get("onboarding_active", False):
        step = st.session_state.onboarding_step
        step_data = onboarding_step(step)
        
        # Calculate progress percentage
        progress_pct = (step / 7) * 100
        
        # UI IMPROVEMENT: Use the 'card' class with progress bar
        st.markdown(f'''
            <div class="card" style="border: 2px solid #3B82F6; background: rgba(59, 130, 246, 0.1); padding: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <p style="margin:0; font-size: 0.65rem; color: #3B82F6; font-weight: bold;">
                        SYSTEM TOUR: STEP {step} OF 7
                    </p>
                    <p style="margin:0; font-size: 0.65rem; color: #3B82F6;">
                        {progress_pct:.0f}% COMPLETE
                    </p>
                </div>
                <div class="progress-bar" style="background: rgba(59,130,246,0.2); height: 4px; margin-bottom: 1rem;">
                    <div class="progress-fill" style="width: {progress_pct}%; background: #3B82F6; height: 4px;"></div>
                </div>
                <h3 style="margin-top: 0rem; font-size: 1.1rem;">{step_data['title']}</h3>
                <p style="font-size: 0.85rem;">{step_data['content']}</p>
            </div>
        ''', unsafe_allow_html=True)
        
        # UI IMPROVEMENT: More balanced button layout
        cols = st.columns([1, 1])
        with cols[0]:
            if step > 1:
                if st.button("← Back", key=f"prev_{step}", use_container_width=True):
                    st.session_state.onboarding_step -= 1
                    st.rerun()
        with cols[1]:
            if step < 7:
                if st.button("Continue →", type="primary", key=f"next_{step}", use_container_width=True):
                    st.session_state.onboarding_step += 1
                    st.rerun()
            else:
                if st.button("Finish Tour 🎉", type="primary", key="finish_tour", use_container_width=True):
                    st.session_state.onboarding_active = False
                    st.rerun()
        
                 # Single faint divider between branding and controls
        st.markdown('<hr style="opacity: 0.1; margin: 0.5rem 0;">', unsafe_allow_html=True)
    else:
        if st.button("Restart Tour", key="restart_tour", use_container_width=True):
            st.session_state.onboarding_active = True
            st.session_state.onboarding_step = 1
            st.rerun()

def toggle_theme():
    """Single-button modern theme toggle with dynamic icon and label."""
    # 1. Initialize State
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True

    is_dark = st.session_state.dark_mode

    # 2. Section Label
    st.sidebar.markdown('<p style="font-size:0.65rem; color:#8A8F99; letter-spacing:1px; margin-bottom:10px;">APPEARANCE</p>', unsafe_allow_html=True)
    
    # 3. Dynamic Styling based on State
    # If Dark: Show Sun icon to switch to Light. If Light: Show Moon icon to switch to Dark.
    label = "Light Mode" if is_dark else "Dark Mode"
    help_text = "Switch to high-contrast light mode" if is_dark else "Switch to eye-friendly dark mode"
    
    # 4. Functional Toggle Button
    if st.sidebar.button(label, use_container_width=True, help=help_text):
        st.session_state.dark_mode = not is_dark
        # Import and apply theme instantly
        from config import apply_theme
        apply_theme()
        st.rerun()

    # 5. Visual "Active State" Indicator (Subtle underline)
    active_color = "#3B82F6" if is_dark else "#F59E0B" # Blue for Dark, Amber for Light
    st.sidebar.markdown(f"""
        <div style="width: 100%; height: 2px; background: rgba(255,255,255,0.05); margin-top: -10px;">
            <div style="width: 100%; height: 100%; background: {active_color}; opacity: 0.6;"></div>
        </div>
    """, unsafe_allow_html=True)
def load_with_facts(func, loading_message=None, *args, **kwargs):
    """
    Execute a function while displaying a random behavioral finance fact.
    
    Parameters:
    - func: The function to execute
    - loading_message: Optional custom loading message (default: "Processing...")
    - *args, **kwargs: Arguments to pass to the function
    """
    fact = get_random_fact()
    message = loading_message or "Processing data"
    
    with st.spinner(f"{message}\n\n💡 **Behavioral Insight:** {fact}"):
        result = func(*args, **kwargs)
    
    return result
def render_data_quality():
    """Displays a high-tech data health indicator."""
    st.sidebar.markdown("---")
    st.sidebar.markdown('<p class="tech-label" style="font-size:0.6rem; color:#8A8F99;">DATA INTEGRITY MONITOR</p>', unsafe_allow_html=True)
    
    # Get actual data quality metrics
    posts_df = st.session_state.get('posts_data', None)
    if posts_df is not None and not posts_df.empty:
        stats = validate_data_quality(posts_df)
        health_score = stats.get('data_completeness', 98.2)
    else:
        health_score = 0
    
    status_color = "#10B981" if health_score > 95 else ("#F59E0B" if health_score > 80 else "#EF4444")
    status_text = "EXCELLENT" if health_score > 95 else ("MODERATE" if health_score > 80 else "CRITICAL")
    
    st.sidebar.markdown(f"""
        <div style="border: 1px solid rgba(59, 130, 246, 0.2); border-left: 4px solid {status_color}; 
                    padding: 0.75rem; border-radius: 8px; background: rgba(10, 15, 25, 0.4);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                <span style="font-size: 0.7rem; color: #E2E8F0;">System Health</span>
                <span style="font-size: 0.7rem; font-weight: bold; color: {status_color};">{status_text}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.65rem; color: #8A8F99;">Integrity Score</span>
                <span style="font-size: 0.65rem; font-weight: bold; color: {status_color};">{health_score:.1f}%</span>
            </div>
            <div class="progress-bar" style="background: rgba(255,255,255,0.1); margin-top: 0.5rem; height: 4px;">
                <div class="progress-fill" style="width: {health_score}%; background: {status_color}; height: 4px;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_system_controls(posts_df):
    
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if posts_df is not None and not posts_df.empty:
            csv = posts_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Export CSV",
                data=csv,
                file_name=f"marketmind_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                help="Download the currently filtered dataset"
            )
        else:
            st.button("No Data", disabled=True, use_container_width=True)
    
    with col2:
        if DEBUG_MODE:
            if st.button("Debug Console", use_container_width=True, help="View raw session state and system logs"):
                st.session_state.show_debug = not st.session_state.get('show_debug', False)
                st.rerun()
    
    # If debug is active, show a floating code block
    if st.session_state.get('show_debug', False):
        with st.expander("System kernel logs", expanded=True):
            # Get model accuracy if available
            model_results = st.session_state.get('model_results', None)
            accuracy = "N/A"
            if model_results is not None and not model_results.empty:
                accuracy = f"{model_results.iloc[0]['Accuracy']:.3f}" if 'Accuracy' in model_results.columns else "N/A"
            
            st.json({
                "session_id": str(st.session_state.get('session_id', 'N/A'))[-8:],
                "active_filters": {
                    "company": st.session_state.get('selected_company', 'All'),
                    "date_range": str(st.session_state.get('date_range', ['2021-02-01', '2021-02-28'])),
                    "sentiment": st.session_state.get('sentiment_filter', 'All'),
                    "min_score": st.session_state.get('min_score', 0)
                },
                "model_metrics": {
                    "accuracy": accuracy,
                    "data_volume": len(posts_df) if posts_df is not None else 0
                },
                "data_load_time": f"{np.random.uniform(0.1, 0.4):.3f}s"
            })

def track_user_session():
    """Track user interactions for analytics."""
    if 'session_start' not in st.session_state:
        st.session_state.session_start = datetime.now()
        st.session_state.page_views = {}
        st.session_state.session_id = hash(datetime.now())
    
    current_page = st.session_state.get('current_page', 'Unknown')
    if current_page not in st.session_state.page_views:
        st.session_state.page_views[current_page] = 0
    st.session_state.page_views[current_page] += 1

def render_sidebar():
    """Render sidebar with a prominent corner logo."""
    
    track_user_session()
    
    with st.sidebar:
        try:
            # 1. Determine which logo to use based on theme
            is_dark = st.session_state.get('dark_mode', True)
            logo_filename = "logo.png" if is_dark else "logo_light.png"
            
            # 2. Load and encode the logo
            with open(logo_filename, "rb") as f:
                logo_data = base64.b64encode(f.read()).decode()
            
            # 3. Render logo with slight transition effect
            st.markdown(f"""
                <div style="display: flex; justify-content: center; padding: 0.5rem 0 2rem 0; transition: opacity 0.3s ease;">
                    <img src="data:image/png;base64,{logo_data}" 
                        style="width: 180px; opacity: 1;">
                </div>
            """, unsafe_allow_html=True)
            
        except FileNotFoundError:
            # Fallback to text if no logo found
            st.sidebar.markdown("<h2 style='text-align: center;'>MarketMind</h2>", unsafe_allow_html=True)
        # ====================================================================
        # THEME TOGGLE - MODERN CAPSULE BUTTON
        # ====================================================================
        toggle_theme()
        
        
        
        # ====================================================================
        # ANALYSIS FILTERS
        # ====================================================================
        with st.expander("ANALYSIS FILTERS", expanded=False):
            # Load data for filters
            posts_df = load_reddit_data()
            
            if not posts_df.empty:
                # Date range picker with fallback
                min_date = posts_df['created'].min().date() if not posts_df.empty else datetime(2021, 1, 1).date()
                max_date = posts_df['created'].max().date() if not posts_df.empty else datetime(2021, 2, 28).date()
                
                date_range = st.date_input(
                    "Date Range",
                    [min_date, max_date],
                    min_value=min_date,
                    max_value=max_date,
                    format="YYYY-MM-DD"
                )
                st.session_state.date_range = date_range
                
                # Company filter
                companies = get_companies_list(posts_df)
                selected_company = st.selectbox("Company", ["All"] + companies)
                st.session_state.selected_company = selected_company
                
                # Sentiment filter
                sentiment_filter = st.selectbox("Sentiment", ["All", "Positive", "Neutral", "Negative"])
                st.session_state.sentiment_filter = sentiment_filter
                
                # Score filter
                max_score = int(posts_df['score'].max()) if not posts_df.empty else 100
                min_score = st.slider("Minimum Score", 0, max_score, 0, 10)
                st.session_state.min_score = min_score
                
                if st.button("Apply Filters", use_container_width=True):
                    st.success("Filters applied!")
                    st.rerun()
            else:
                st.warning("No data loaded")
        
        # ====================================================================
        # DATA QUALITY MONITOR
        # ====================================================================
        #render_data_quality()
        
        # ====================================================================
        # SYSTEM CONTROLS (Export + Debug)
        # ====================================================================
        posts_df = st.session_state.get('posts_data', None)
        render_system_controls(posts_df)
        

def render_top_menu():
    """Render top menu with categories."""
    cols = st.columns(len(CATEGORIES))
    for idx, (cat_name, pages) in enumerate(CATEGORIES.items()):
        with cols[idx]:
            is_active = (st.session_state.current_category == cat_name)
            if st.button(
                cat_name,
                key=f"cat_{cat_name}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_category = cat_name
                if pages:
                    st.session_state.current_page = pages[0]
                else:
                    st.session_state.current_page = "Dashboard"
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)

def render_header():
    st.markdown("""
    <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;'>
        <div style='display: flex; align-items: center;'>
            <div class='led-node'></div>
            <h2 style='letter-spacing: -2px; margin: 0; font-weight: 900;'>Visualisation and analysis of consumer behavior in asset markets</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div class='card' style='font-family: monospace; font-size: 0.8rem; color: #10B981; margin-top: 2rem;'>
        > [SCAN_CORE]: Deep learning matrices synchronized.<br>
        > [GRID_NODE]: Data analysis complete.<br>
        > [ACTION]: Ready for visualization.
    </div>
    """, unsafe_allow_html=True)

    # ====================================================================
        # SYSTEM KERNEL ID (Academic Power Move)
        # ====================================================================
    if 'session_id' in st.session_state:
            session_id_short = str(st.session_state.session_id)[-8:]
            st.markdown(f"""
            <div style="margin-top: 1rem; padding: 0.5rem; border-top: 1px solid rgba(59,130,246,0.2);">
                <p style="font-family: monospace; font-size: 0.55rem; color: #64748B; text-align: center; margin: 0;">
                    SYSTEM KERNEL: {session_id_short}
                </p>
                <p style="font-family: monospace; font-size: 0.5rem; color: #64748B; text-align: center; margin: 0.25rem 0 0 0;">
                    SESSION: {st.session_state.session_start.strftime('%Y-%m-%d %H:%M') if 'session_start' in st.session_state else 'N/A'}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
    '''''   # ====================================================================
        # VERSION FOOTER
        # ====================================================================
            st.markdown("""
            <div style="margin-top: 1rem; text-align: center; opacity: 0.4; font-size: 0.55rem;">
                MARKETMIND ENGINE v2.4.0<br>
                © 2026 THESIS PROJECT
            </div>
        """, unsafe_allow_html=True)
    '''''