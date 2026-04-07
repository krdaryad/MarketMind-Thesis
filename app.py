"""
Main application entry point with loading screen.
"""
import streamlit as st
import pandas as pd
import time
from config import CATEGORIES, apply_theme
from utils import (
    show_onboarding, render_sidebar, render_top_menu, render_header, render_footer
)
st.set_page_config(
    page_title="MarketMind AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Import all page functions
from pages.dashboard import dashboard_page
from pages.sentiment_trends import sentiment_trends_page
from pages.ai_analysis import ai_analysis_page
from pages.pattern_mining import pattern_mining_page
from pages.entity_analysis import entity_analysis_page
from pages.glossary import glossary_page
from pages.classifier_demo import classifier_demo_page
from pages.learning_hub import learning_hub_page
from pages.model_accuracy import model_accuracy_page
from pages.methodology import methodology_page
from pages.economic_dashboard import economic_dashboard_page
from pages.shock_detection import shock_detection_page
from pages.causality_analysis import causality_analysis_page
from pages.market_history import market_history_page
from pages.volatility_analysis import volatility_analysis_page
from pages.event_impact import event_impact_page

try:
    from pages.company_comparison import company_comparison_page
except ImportError:
    company_comparison_page = None

try:
    from pages.correlation_analysis import correlation_analysis_page
except ImportError:
    correlation_analysis_page = None

# Import data loaders
from data_fetcher import load_reddit_data, add_sentiment, aggregate_sentiment, fetch_market_data
from data_loader import load_economic_data

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================
def initialize_session_state():
    """Initialize all session state variables."""
    # Set default page to GLOBAL MACRO category
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Economic Dashboard"  # First page in GLOBAL MACRO
    if 'current_category' not in st.session_state:
        st.session_state.current_category = "GLOBAL MACRO"    # First category
    if 'posts_data' not in st.session_state:
        st.session_state.posts_data = pd.DataFrame()
    if 'sentiment_data' not in st.session_state:
        st.session_state.sentiment_data = pd.DataFrame()
    if 'market_data' not in st.session_state:
        st.session_state.market_data = pd.DataFrame()
    if 'topics' not in st.session_state:
        st.session_state.topics = {}
    if 'patterns' not in st.session_state:
        st.session_state.patterns = pd.DataFrame()
    if 'model_results' not in st.session_state:
        st.session_state.model_results = pd.DataFrame()
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
    if 'economic_data' not in st.session_state:
        st.session_state.economic_data = {}
    if 'econ_df' not in st.session_state:
        st.session_state.econ_df = pd.DataFrame()
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

# ============================================================================
# DATA LOADING
# ============================================================================
def load_all_data():
    """Enhanced data loading with a centralized status card."""
    st.markdown("### System Initialization")
    load_card = st.container(border=True)
    
    with load_card:
        progress_bar = st.progress(0)
        status_message = st.empty()
        
        c1, c2, c3, c4, c5 = st.columns(5)
        steps = {
            "reddit": c1.empty(),
            "econ": c2.empty(),
            "market": c3.empty(),
            "sent": c4.empty(),
            "ml": c5.empty()
        }
        
        for key in ["reddit", "econ", "market", "sent", "ml"]:
            steps[key].caption(f"⭘ {key.capitalize()}")

    try:
        status_message.text("Loading Reddit CSV archives...")
        posts_df = load_reddit_data()
        steps["reddit"].success("Reddit Data")
        progress_bar.progress(20)

        status_message.text("Loading economic indicators...")
        economic_data, econ_df = load_economic_data('financial_forecasting_dataset.csv')
        st.session_state.economic_data = economic_data
        st.session_state.econ_df = econ_df
        steps["econ"].success("Economics")
        progress_bar.progress(40)

        status_message.text("Fetching market data...")
        if 'date_range' in st.session_state:
            start_date, end_date = st.session_state.date_range
            market_df = fetch_market_data(start_date, end_date)
            st.session_state.market_data = market_df
        steps["market"].success("Market Data")
        progress_bar.progress(60)

        status_message.text("Processing sentiment analysis...")
        if not posts_df.empty:
            posts_with_sentiment = add_sentiment(posts_df)
            st.session_state.posts_data = posts_with_sentiment
            st.session_state.sentiment_data = aggregate_sentiment(posts_with_sentiment)
        steps["sent"].success("Sentiment")
        progress_bar.progress(80)

        status_message.text("Training ML models...")
        from text_analysis import get_real_topics, get_real_patterns, get_real_model_results
        if len(posts_df) >= 10:
            st.session_state.topics = get_real_topics(posts_df)
            st.session_state.patterns = get_real_patterns(posts_df)
            st.session_state.model_results = get_real_model_results(posts_df)
        
        steps["ml"].success("ML Models")
        progress_bar.progress(100)
        status_message.info("System Ready")
        
        st.session_state.data_loaded = True
        time.sleep(0.5)
        st.rerun()

    except Exception as e:
        st.error(f"System Load Error: {str(e)}")
        st.session_state.data_loaded = False
    
    return st.session_state.data_loaded

# ============================================================================
# PAGE RENDERING
# ============================================================================
def render_page_content():
    """Render the content based on selected category and page."""
    category = st.session_state.current_category
    current_page = st.session_state.current_page
    
    page_functions = {
    "Dashboard": dashboard_page,
    "Economic Dashboard": economic_dashboard_page,
    "Sentiment Trends": sentiment_trends_page,
    "Pattern Mining": pattern_mining_page,
    "Entity Analysis": entity_analysis_page,
    "Company Comparison": company_comparison_page,
    "Correlation Analysis": correlation_analysis_page,
    "AI Analysis": ai_analysis_page,
    "Classifier Demo": classifier_demo_page,
    "Model Accuracy": model_accuracy_page,
    "Learning Hub": learning_hub_page,
    "Methodology": methodology_page,
    "Glossary": glossary_page,
    "Causality Analysis": causality_analysis_page,
    "Shock Detection": shock_detection_page,
    "Volatility Analysis": volatility_analysis_page,
    "Market History": market_history_page,
    "Event Impact": event_impact_page,
    
}
    
    if category == "Dashboard":
        dashboard_page()
        return
    
    if category in CATEGORIES:
        pages = CATEGORIES[category]
        if pages:
            tabs = st.tabs(pages)
            for i, page_name in enumerate(pages):
                with tabs[i]:
                    page_func = page_functions.get(page_name)
                    if page_func is not None:
                        page_func()
                    else:
                        st.error(f"Page '{page_name}' is not yet implemented")
        else:
            st.error(f"No pages defined for category: {category}")
    else:
        st.error(f"Unknown category: {category}")

# ============================================================================
# MAIN APP
# ============================================================================
def main():
    """Main application entry point."""
    
    initialize_session_state()
    apply_theme()
    
    if not st.session_state.data_loaded:
        success = load_all_data()
        if not success:
            st.error("Failed to load data. Please check your data files and try again.")
            st.stop()
    
    render_header()
    show_onboarding()
    render_sidebar()
    render_top_menu()
    render_page_content()
    render_footer()

if __name__ == "__main__":
    main()