"""
Data Generation Module
Generates synthetic market, sentiment, pattern, and model data
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

@st.cache_data
def generate_market_data():
    """Generate market data matching screenshots"""
    dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
    np.random.seed(42)
    
    returns = np.random.normal(0.0005, 0.012, len(dates))
    price = 4500 * np.exp(np.cumsum(returns))
    
    price[28] = price[28] * 0.98
    price[49] = price[49] * 0.95
    price[68] = price[68] * 0.93
    
    return pd.DataFrame({
        'date': dates,
        'spy': price,
        'vix': 20 - 15 * (price - price.min()) / (price.max() - price.min()) + np.random.normal(0, 1, len(dates)),
        'volume': np.random.randint(50000000, 150000000, len(dates))
    })

@st.cache_data
def generate_sentiment_data():
    """Generate sentiment data with timeline"""
    dates = ["Jan 1", "Jan 8", "Jan 15", "Jan 22", "Jan 29", "Feb 5", 
             "Feb 12", "Feb 19", "Feb 26", "Mar 4", "Mar 10", "Mar 17"]
    
    return pd.DataFrame({
        'date': dates,
        'positive': [12, 15, 14, 11, 8, 14, 16, 5, 18, 14, 4, 12],
        'neutral': [45, 48, 42, 44, 38, 52, 48, 32, 52, 52, 28, 48],
        'negative': [18, 22, 24, 20, 42, 24, 28, 52, 22, 38, 58, 32],
        'anomaly_score': [0.1, 0.15, 0.12, 0.08, 0.55, 0.1, 0.18, 0.82, 0.12, 0.2, 0.91, 0.14],
        'is_anomaly': [False, False, False, False, True, False, False, True, False, False, True, False]
    })

@st.cache_data
def generate_pattern_data():
    """Generate pattern mining data"""
    return {
        'topics': {
            'Tech Earnings': ['earnings', 'revenue', 'beat', 'guidance', 'AI', 'media'],
            'Market Crash Fear': ['crash', 'bubble', 'overvalued', 'correction', 'bear'],
            'Macro Economy': ['inflation', 'gdp', 'jobs', 'unemployment', 'cpi'],
            'Meme / YOLO': ['yolo', 'diamond', 'moon', 'tendies', 'app']
        },
        'patterns': pd.DataFrame([
            {"pattern": "fed, rates", "support": 23, "sentiment": "negative", "confidence": 0.85, "lift": 1.8},
            {"pattern": "earnings beat", "support": 17, "sentiment": "positive", "confidence": 0.92, "lift": 2.1},
            {"pattern": "market crash", "support": 12, "sentiment": "negative", "confidence": 0.78, "lift": 1.5},
            {"pattern": "bullish, tech", "support": 9, "sentiment": "positive", "confidence": 0.88, "lift": 1.9},
            {"pattern": "inflation, high", "support": 8, "sentiment": "negative", "confidence": 0.82, "lift": 1.6},
        ])
    }

@st.cache_data
def generate_model_performance():
    """Generate model accuracy data"""
    return pd.DataFrame({
        'Model': ['TF-IDF + GNB', 'Decision Tree', 'SVM (proposed)', 'Original TDM'],
        'Accuracy': [0.660, 0.580, 0.710, 0.513],
        'AUC': [0.74, 0.65, 0.79, 0.52],
        'Precision': [0.68, 0.59, 0.73, 0.51],
        'Recall': [0.64, 0.56, 0.69, 0.49]
    })

@st.cache_data
def generate_anomalies():
    """Generate anomaly data"""
    return [
        {"date": "Mar 10", "severity": "critical", "score": 0.91, 
         "cause": "Bank failure rumours — \"crash\" keyword frequency 5× normal",
         "impact": "Largest single-day negative sentiment volume in dataset"},
        {"date": "Feb 19", "severity": "high", "score": 0.82,
         "cause": "CPI report beat expectations — panic posts surged 280%",
         "impact": "VIX jumped from 14.2 → 19.8"},
        {"date": "Jan 29", "severity": "medium", "score": 0.55,
         "cause": "Unexpected FOMC minutes release — negative sentiment spike 3.2σ above mean",
         "impact": "S&P 500 dropped 1.2% same day"},
    ]

def generate_word_frequencies():
    """Generate word frequencies for word cloud"""
    word_freq = {}
    
    topics = st.session_state.pattern_data['topics']
    for topic, keywords in topics.items():
        for kw in keywords:
            word_freq[kw] = word_freq.get(kw, 0) + 15
    
    patterns = st.session_state.pattern_data['patterns']
    for _, row in patterns.iterrows():
        pattern = row['pattern']
        support = row['support']
        for word in pattern.replace(',', '').split():
            word_freq[word] = word_freq.get(word, 0) + support
    
    extra_terms = {
        'rates': 35, 'fed': 42, 'crash': 38, 'bullish': 30, 'earnings': 28,
        'recession': 25, 'tech': 22, 'inflation': 40, 'growth': 20, 'moon': 18,
        'dump': 15, 'hold': 25, 'squeeze': 12, 'volume': 18, 'puts': 20, 'calls': 22
    }
    for word, freq in extra_terms.items():
        word_freq[word] = word_freq.get(word, 0) + freq
    
    return word_freq