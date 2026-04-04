"""
Functions to fetch and process data from CSV file.
"""
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
import re
import time
import hashlib
import joblib
import os
from config import CSV_FILE_PATH, COMPANY_TICKERS, DEBUG_MODE, COLORS, MODELS_DIR

# ============================================================================
# DATA LOADING WITH PROGRESS
# ============================================================================
@st.cache_data(ttl=3600)
def load_reddit_data():
    """Load reddit posts from CSV file with progress tracking."""
    start_time = time.time()
    
    try:
        with st.spinner("📊 Loading Reddit data..."):
            df = pd.read_csv(CSV_FILE_PATH)
            
            # Convert date column to datetime
            df['created'] = pd.to_datetime(df['created'])
            df['date'] = df['created'].dt.date
            
            # Clean up company names
            df['matched_company'] = df['matched_company'].fillna('').str.strip()
            
            # Standardize company names for consistency
            company_standard = {
                'Apple': 'Apple',
                'AAPL': 'Apple',
                'TSLA': 'Tesla',
                'Tesla': 'Tesla',
                'Amazon': 'Amazon',
                'AMZN': 'Amazon',
                'Google': 'Google',
                'GOOG': 'Google',
                'GOOGL': 'Google',
                'Microsoft': 'Microsoft',
                'MSFT': 'Microsoft'
            }
            
            # Apply standardization
            df['company_standard'] = df['matched_company'].map(company_standard).fillna(df['matched_company'])
            
            # Filter out posts with no company
            df = df[df['company_standard'] != '']
            
            # Combine title and selftext for analysis
            df['text'] = df['title'].fillna('') + ' ' + df['selftext'].fillna('')
            
            # Filter out deleted/removed posts
            df = df[~df['author'].str.contains('deleted', na=False, case=False)]
            df = df[df['selftext'] != '[deleted]']
            
            if DEBUG_MODE:
                st.sidebar.info(f"Data loaded in {time.time() - start_time:.2f}s")
                st.sidebar.success(f"Loaded {len(df):,} posts")
            
            return df
            
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        st.info(f"Please ensure file exists at: {CSV_FILE_PATH}")
        return pd.DataFrame()

def get_data_version(df):
    """Calculate data version based on hash."""
    if df.empty:
        return "empty"
    df_hash = pd.util.hash_pandas_object(df).values
    return hashlib.md5(df_hash).hexdigest()[:8]

def validate_data_quality(df):
    """Validate data quality and return summary statistics."""
    if df.empty:
        return {}
    
    # Calculate missing values
    missing_text = df['text'].isna().sum() if 'text' in df.columns else 0
    missing_company = df['company_standard'].isna().sum() if 'company_standard' in df.columns else 0
    
    return {
        'total_posts': len(df),
        'date_range_start': df['created'].min() if 'created' in df.columns else None,
        'date_range_end': df['created'].max() if 'created' in df.columns else None,
        'companies_count': df['company_standard'].nunique() if 'company_standard' in df.columns else 0,
        'top_companies': df['company_standard'].value_counts().head(5).to_dict() if 'company_standard' in df.columns else {},
        'avg_post_score': df['score'].mean() if 'score' in df.columns else 0,
        'total_comments': df['num_comments'].sum() if 'num_comments' in df.columns else 0,
        'missing_text': missing_text,
        'missing_company': missing_company,
        'unique_authors': df['author'].nunique() if 'author' in df.columns else 0,
        'data_completeness': (1 - (missing_text + missing_company) / (2 * len(df))) * 100 if len(df) > 0 else 0
    }

def get_companies_list(df):
    """Get list of unique companies from data."""
    if df.empty:
        return []
    return sorted(df['company_standard'].unique())

def filter_by_company(df, company):
    """Filter posts by company."""
    if df.empty or not company or company == 'All':
        return df
    return df[df['company_standard'] == company]

def filter_by_date(df, start_date, end_date):
    """Filter posts by date range."""
    if df.empty:
        return df
    # Convert to datetime for comparison
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    mask = (df['created'] >= start_dt) & (df['created'] <= end_dt)
    return df[mask]

def filter_by_sentiment(df, sentiment_filter):
    """Filter posts by sentiment."""
    if df.empty or not sentiment_filter or sentiment_filter == 'All':
        return df
    if 'sentiment' not in df.columns:
        return df
    return df[df['sentiment'] == sentiment_filter.lower()]

def filter_by_score(df, min_score):
    """Filter posts by minimum score."""
    if df.empty or min_score <= 0:
        return df
    if 'score' not in df.columns:
        return df
    return df[df['score'] >= min_score]

@st.cache_data(ttl=3600)
def fetch_market_data(start_date, end_date):
    """Fetch market data using yfinance and fredapi (avoiding pandas_datareader)."""
    import yfinance as yf
    from fredapi import Fred
    
    try:
        # 1. Download S&P 500 and VIX using yfinance (Stable)
        spy = yf.download("^GSPC", start=start_date, end=end_date, progress=False)
        vix = yf.download("^VIX", start=start_date, end=end_date, progress=False)

        df = pd.DataFrame(index=spy.index)
        
        # Handle yfinance MultiIndex columns if necessary
        if isinstance(spy.columns, pd.MultiIndex):
            df['spy'] = spy['Close'].iloc[:, 0]
            df['vix'] = vix['Close'].iloc[:, 0] if not vix.empty else np.nan
        else:
            df['spy'] = spy['Close']
            df['vix'] = vix['Close'] if not vix.empty else np.nan

        # 2. Use fredapi for Treasury data (Replaces the crashing pandas_datareader)
        try:
            fred = Fred(api_key=st.secrets["FRED_API_KEY"])
            treasury_series = fred.get_series('DGS10', start_date, end_date)
            df['treasury'] = treasury_series
        except Exception as e:
            st.sidebar.warning(f"FRED Error: {e}")
            df['treasury'] = np.nan

        # 3. Final formatting
        df = df.reset_index().rename(columns={'Date': 'date', 'index': 'date'})
        return df.ffill().fillna(0) # Fill gaps for weekends/holidays
        
    except Exception as e:
        if DEBUG_MODE:
            st.warning(f"Market Data Error: {e}")
        return pd.DataFrame()


def add_sentiment(df):
    """Add VADER sentiment scores to each post."""
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    import nltk
    
    try:
        nltk.data.find('sentiment/vader_lexicon')
    except LookupError:
        nltk.download('vader_lexicon', quiet=True)
    
    sia = SentimentIntensityAnalyzer()
    
    if df.empty:
        return df
    
    def get_compound(text):
        try:
            return sia.polarity_scores(str(text))['compound']
        except:
            return 0
    
    df['compound'] = df['text'].apply(get_compound)
    df['sentiment'] = df['compound'].apply(
        lambda x: 'positive' if x > 0.05 else ('negative' if x < -0.05 else 'neutral')
    )
    return df

def aggregate_sentiment(df):
    """Aggregate daily sentiment counts."""
    if df.empty:
        return pd.DataFrame(columns=['date', 'positive', 'neutral', 'negative'])
    
    # Ensure date column exists
    if 'date' not in df.columns and 'created' in df.columns:
        df['date'] = pd.to_datetime(df['created']).dt.date
    
    daily = df.groupby('date').agg(
        positive=('sentiment', lambda x: (x == 'positive').sum()),
        neutral=('sentiment', lambda x: (x == 'neutral').sum()),
        negative=('sentiment', lambda x: (x == 'negative').sum()),
        avg_compound=('compound', 'mean'),
        post_count=('id', 'count')
    ).reset_index()
    
    # Calculate anomaly score based on compound score deviation
    if len(daily) > 1:
        daily['anomaly_score'] = (daily['avg_compound'] - daily['avg_compound'].rolling(7, min_periods=1).mean()).abs()
        daily['anomaly_score'] = daily['anomaly_score'] / (daily['avg_compound'].rolling(7, min_periods=1).std() + 0.1)
        daily['anomaly_score'] = daily['anomaly_score'].clip(0, 1)
        daily['is_anomaly'] = daily['anomaly_score'] > 0.7
    else:
        daily['anomaly_score'] = 0
        daily['is_anomaly'] = False
    
    return daily

def fetch_entity_mentions(df, ticker_list):
    """Extract ticker mentions from post texts."""
    if df.empty:
        return pd.DataFrame()
    
    def extract_tickers(text):
        found = set()
        for ticker in ticker_list:
            if re.search(rf'\b{ticker}\b', text, re.IGNORECASE):
                found.add(ticker)
        return found
    
    df['tickers'] = df['text'].apply(extract_tickers)
    # Expand to separate rows per ticker
    exploded = df.explode('tickers').dropna(subset=['tickers'])
    if exploded.empty:
        return pd.DataFrame(columns=['ticker', 'date', 'compound'])
    
    return exploded[['tickers', 'date', 'compound']].rename(columns={'tickers': 'ticker'})

def get_company_stats(df):
    """Get statistics by company."""
    if df.empty:
        return pd.DataFrame()
    
    stats = df.groupby('company_standard').agg(
        post_count=('id', 'count'),
        avg_score=('score', 'mean'),
        total_comments=('num_comments', 'sum'),
        avg_compound=('compound', 'mean') if 'compound' in df.columns else ('score', lambda x: 0)
    ).reset_index()
    
    # Add sentiment classification
    if 'compound' in df.columns:
        stats['avg_sentiment'] = stats['avg_compound'].apply(
            lambda x: 'Positive' if x > 0.05 else ('Negative' if x < -0.05 else 'Neutral')
        )
    
    stats = stats.sort_values('post_count', ascending=False)
    return stats

def get_daily_sentiment_by_company(df, company):
    """Get daily sentiment for a specific company."""
    if df.empty:
        return pd.DataFrame()
    
    company_df = filter_by_company(df, company)
    if company_df.empty:
        return pd.DataFrame()
    
    return company_df.groupby('date').agg(
        positive=('sentiment', lambda x: (x == 'positive').sum()),
        neutral=('sentiment', lambda x: (x == 'neutral').sum()),
        negative=('sentiment', lambda x: (x == 'negative').sum()),
        avg_compound=('compound', 'mean')
    ).reset_index()

def check_for_new_data():
    """Check if new data is available."""
    if not os.path.exists(CSV_FILE_PATH):
        return False
    
    last_modified = os.path.getmtime(CSV_FILE_PATH)
    if last_modified > st.session_state.get('last_check', 0):
        st.session_state.last_check = last_modified
        return True
    return False