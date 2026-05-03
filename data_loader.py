import pandas as pd
import yfinance as yf
from fredapi import Fred
import streamlit as st
from datetime import datetime
import numpy as np
from loading_facts import get_data_loading_fact  


FRED_API_KEY = st.secrets["FRED_API_KEY"]
fred = Fred(api_key=FRED_API_KEY)


@st.cache_data(ttl=86400, show_spinner=False)  
def load_real_economic_data(ticker, start_date="2020-01-01", end_date=None):
    """Fetch real-world data from FRED and Yahoo Finance."""
    
    
    fact = get_data_loading_fact()
    
    if end_date is None:
        end_date = datetime.today().strftime("%Y-%m-%d")
    
    try:
        # data from Yahoo Finance
        with st.spinner(f"Fetching stock data for {ticker}...\n\n {fact}"):  # witha fun fact
            stock_df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if stock_df.empty:
                st.warning(f"No stock data found for {ticker}")
                return {}, pd.DataFrame()
            
            stock_df = stock_df[['Close']].reset_index()
            stock_df.columns = ['date', 'close']
        #official api source attributes and descriptions, which I chose 
        macro_series = {
           
            'gdp': 'GDPC1',                    # Real GDP
            'inflation': 'CPIAUCSL',           # CPI All Urban Consumers
            'unemployment': 'UNRATE',          # Unemployment Rate
            'interest_rate': 'FEDFUNDS',       # Federal Funds Rate
            'consumer_sentiment': 'UMCSENT',   # University of Michigan Consumer Sentiment
            
            
            'financial_stress': 'STLFSI4',     # St. Louis Fed Financial Stress Index
            'initial_claims': 'ICSA',          # Weekly jobless claims
            'continuing_claims': 'CCSA',       # Continuing unemployment claims
            'vix': 'VIXCLS',                   # CBOE Volatility Index (VIX)
            'sp500': 'SP500',                  # S&P 500 Index Level
            
            
            'm2_money_supply': 'M2SL',         # Broad money supply
            'm1_money_supply': 'M1SL',         # Narrow money supply
            'treasury_10yr': 'DGS10',          # 10-Year Treasury Rate
            'treasury_2yr': 'DGS2',            # 2-Year Treasury Rate
            
           
            'building_permits': 'PERMIT',      # Housing permits
            'industrial_production': 'INDPRO', # Industrial output
            'new_orders': 'ANDENO',            # Manufacturing new orders
            
            
            'core_inflation': 'CPILFESL',      # Core CPI (ex food & energy)
            'ppi': 'PPIACO',                   # Producer Price Index
        }
        
        macro_frames = []
        
        
        fact_fred = get_data_loading_fact()
        
        for name, series_id in macro_series.items():
            try:
                with st.spinner(f"Fetching {name} data from FRED...\n\n {fact_fred}"):
                    s = fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
                    if s is not None and not s.empty:
                        df_temp = pd.DataFrame(s, columns=[name]).reset_index()
                        df_temp.columns = ['date', name]
                        macro_frames.append(df_temp)
            except Exception as e:
                st.warning(f"Could not fetch {name} data: {e}")

        #  merging everything
        final_df = stock_df
        for m_df in macro_frames:
            final_df = pd.merge(final_df, m_df, on='date', how='left')

        # clean data with a forward fill macro data (monthly/quarterly to daily)
        final_df = final_df.sort_values('date')
        
        macro_cols = list(macro_series.keys())
        for col in macro_cols:
            if col in final_df.columns:
                final_df[col] = final_df[col].ffill()
        
        # fixing any remaining NaN values
        final_df = final_df.bfill()
        
        final_df['Ticker'] = ticker # Calculate Derived Indicators
        
        # Calculate market stress (volatility-based)
        final_df['returns'] = final_df['close'].pct_change()
        final_df['market_stress'] = final_df['returns'].rolling(20).std() * (252 ** 0.5)
        final_df['market_stress'] = final_df['market_stress'].fillna(0)
        
        # calculate yield spread (10 - 2)
        if 'treasury_10yr' in final_df.columns and 'treasury_2yr' in final_df.columns:
            final_df['yield_spread'] = final_df['treasury_10yr'] - final_df['treasury_2yr']
            final_df['recession_signal'] = (final_df['yield_spread'] < 0).astype(int) #recession signal
        
        # real interest rate
        if 'interest_rate' in final_df.columns and 'inflation' in final_df.columns:
            final_df['real_rate'] = final_df['interest_rate'] - final_df['inflation'] #nominal-inflation
        
        final_df['event_flag'] = (abs(final_df['returns']) > 0.02).astype(int) #flgs for days with >2% moves
    
        ticker_data = {ticker: final_df.set_index('date')} #dictionary structure
        
        return ticker_data, final_df

    except Exception as e:
        st.error(f"Error fetching live data: {e}")
        return {}, pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)  
def load_economic_data(file_path):
    """Load economic indicators from CSV file (legacy function)."""
    
    fact = get_data_loading_fact()
    
    try:
        with st.spinner(f"Loading economic data from CSV...\n\n {fact}"):
            df = pd.read_csv(file_path)
            
            df['Date'] = pd.to_datetime(df['Date'])
            
            df.rename(columns={
                'Date': 'date',
                'GDP (%)': 'gdp',
                'Inflation (%)': 'inflation',
                'Interest Rate (%)': 'interest_rate',
                'Unemployment (%)': 'unemployment',
                'Market Stress Level': 'market_stress',
                'Event Flag': 'event_flag'
            }, inplace=True)
            
            tickers = df['Ticker'].unique()
            ticker_data = {}
            
            for ticker in tickers:
                ticker_data[ticker] = df[df['Ticker'] == ticker].copy()
                ticker_data[ticker].set_index('date', inplace=True)
            
            return ticker_data, df
        
    except Exception as e:
        st.error(f"Error loading economic data: {e}")
        return {}, pd.DataFrame()


def merge_sentiment_with_economics(sentiment_df, economic_data, ticker):
    """Merge sentiment data with economic indicators."""
    if sentiment_df.empty or ticker not in economic_data:
        return pd.DataFrame()
    
    econ_df = economic_data[ticker].reset_index()
    sentiment_df_copy = sentiment_df.copy()
    sentiment_df_copy['date'] = pd.to_datetime(sentiment_df_copy['date'])
    
    merged = pd.merge(sentiment_df_copy, econ_df, on='date', how='inner')
    return merged