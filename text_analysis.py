"""
Text preprocessing, topic extraction, pattern mining, and model training.
"""
import pandas as pd
import numpy as np
import joblib
import os
import streamlit as st
from loading_facts import get_random_fact

# ============================================================================
# PATHS FOR PRE-TRAINED MODELS
# ============================================================================
MODELS_DIR = "models/"
TOPICS_PATH = os.path.join(MODELS_DIR, "topics.pkl")
PATTERNS_PATH = os.path.join(MODELS_DIR, "patterns.pkl")
MODEL_RESULTS_PATH = os.path.join(MODELS_DIR, "model_results.pkl")
SENTIMENT_MODELS_PATH = os.path.join(MODELS_DIR, "sentiment_models.pkl")
VECTORIZER_PATH = os.path.join(MODELS_DIR, "vectorizer.pkl")

# ============================================================================
# ENSURE MODELS DIRECTORY EXISTS
# ============================================================================
os.makedirs(MODELS_DIR, exist_ok=True)

# ============================================================================
# PRE-TRAINED MODEL LOADERS (ALWAYS USE THESE)
# ============================================================================

@st.cache_resource(show_spinner=False)
def get_preloaded_topics():
    """Load pre-trained LDA topics from disk."""
    if os.path.exists(TOPICS_PATH):
        fact = get_random_fact()
        with st.spinner(f"📚 Loading LDA topics...\n\n💡 {fact}"):
            return joblib.load(TOPICS_PATH)
    else:
        st.warning("Pre-trained topics not found. Run save_models.py first.")
        return {"Error": ["Run save_models.py on desktop"]}

@st.cache_resource(show_spinner=False)
def get_preloaded_patterns():
    """Load pre-trained FP-Growth patterns from disk."""
    if os.path.exists(PATTERNS_PATH):
        fact = get_random_fact()
        with st.spinner(f"🔍 Loading pattern mining results...\n\n💡 {fact}"):
            return joblib.load(PATTERNS_PATH)
    else:
        st.warning("Pre-trained patterns not found. Run save_models.py first.")
        return pd.DataFrame()

@st.cache_resource(show_spinner=False)
def get_preloaded_model_results():
    """Load pre-trained model performance metrics from disk."""
    if os.path.exists(MODEL_RESULTS_PATH):
        fact = get_random_fact()
        with st.spinner(f"🤖 Loading model performance data...\n\n💡 {fact}"):
            return joblib.load(MODEL_RESULTS_PATH)
    else:
        st.warning("Pre-trained model results not found. Run save_models.py first.")
        return pd.DataFrame()

@st.cache_resource(show_spinner=False)
def get_preloaded_models():
    """Load pre-trained ML models (SVM, Random Forest, etc.) from disk."""
    if os.path.exists(SENTIMENT_MODELS_PATH) and os.path.exists(VECTORIZER_PATH):
        fact = get_random_fact()
        with st.spinner(f"🧠 Loading ML models (Random Forest, SVM, GNB, Decision Tree)...\n\n💡 {fact}"):
            models = joblib.load(SENTIMENT_MODELS_PATH)
            vectorizer = joblib.load(VECTORIZER_PATH)
            return models, vectorizer
    else:
        st.warning("Pre-trained ML models not found. Run save_models.py on desktop first.")
        return None, None

# ============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS (for existing code that expects these names)
# ============================================================================

def get_real_topics(posts_df=None):
    """Get pre-trained LDA topics (posts_df ignored, kept for API compatibility)."""
    return get_preloaded_topics()

def get_real_patterns(posts_df=None):
    """Get pre-trained FP-Growth patterns (posts_df ignored)."""
    return get_preloaded_patterns()

def get_real_model_results(posts_df=None):
    """Get pre-trained model results (posts_df ignored)."""
    return get_preloaded_model_results()