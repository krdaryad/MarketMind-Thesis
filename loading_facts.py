"""
Behavioral Finance Facts - Displayed during data loading operations
Separate fact pools for different types of operations
"""
import random
import streamlit as st

# Facts for data loading operations (data_fetcher.py)
DATA_LOADING_FACTS = [
    "Random Forest models use 100+ decision trees to reduce overfitting.",
    "VADER sentiment analysis achieves 96% accuracy on social media text.",
    "TF-IDF was invented in 1972 and remains a standard text processing method.",
    "LDA topic modeling assumes each document is a mixture of hidden topics.",
    "FP-Growth mines frequent patterns without generating candidate sets.",
    "Granger causality tests whether past values predict future values.",
    "The 2008 crisis VIX peak was 89.53 - the highest in history.",
    "GameStop stock rose 1,900% in January 2021 driven by Reddit sentiment.",
    "Tesla sentiment spikes 300% when Elon Musk tweets about the company.",
    "Survivorship Bias: We only hear about successful traders, never the failures.",
    "PCA reduces dimensionality while preserving 90%+ of data variance.",
    "t-SNE visualization preserves local neighborhood structures in high-dim data.",
]

# Facts for ML/Analysis operations (text_analysis.py)
ML_ANALYSIS_FACTS = [
   
    "Loss Aversion: The pain of losing $100 is twice as powerful as the joy of gaining $100.",
    "Herd Behavior: 39% of new money flows into last year's top performers.",
    "The Disposition Effect: Investors sell winning stocks too early but hold losing stocks too long.",
    "Recency Bias: The tendency to think the future will look exactly like the last 2 weeks.",
    "Anchoring: Investors rely too heavily on the first price they see for a stock.",
    "Overconfidence: Women outperform men by 40-100 basis points annually.",
    "The 'This Time Is Different' Fallacy: The four most dangerous words in investing.",
    "Confirmation Bias: Investors seek information that confirms their existing beliefs.",
    "The Endowment Effect: People demand more to give up an asset than to acquire it.",
    "Mental Accounting: People spend tax refunds more recklessly than regular paychecks.",
]

def get_data_loading_fact():
    """Get a fact for data loading operations (CSV, market data, sentiment)."""
    if 'data_loading_fact' not in st.session_state:
        st.session_state.data_loading_fact = random.choice(DATA_LOADING_FACTS)
    return st.session_state.data_loading_fact

def get_ml_analysis_fact():
    """Get a fact for ML/Analysis operations (topic modeling, patterns, training)."""
    if 'ml_analysis_fact' not in st.session_state:
        st.session_state.ml_analysis_fact = random.choice(ML_ANALYSIS_FACTS)
    return st.session_state.ml_analysis_fact

def reset_data_loading_fact():
    """Reset the data loading fact for a new page load."""
    if 'data_loading_fact' in st.session_state:
        del st.session_state.data_loading_fact

def reset_ml_analysis_fact():
    """Reset the ML analysis fact for a new page load."""
    if 'ml_analysis_fact' in st.session_state:
        del st.session_state.ml_analysis_fact

# Legacy function for backward compatibility
def get_random_fact():
    return get_data_loading_fact()