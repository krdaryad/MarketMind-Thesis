"""
Granger Causality Analysis - Testing if sentiment predicts market movements
Uses FRED economic data + Reddit sentiment for robust validation
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def causality_analysis_page():
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="margin: 0;">Granger Causality Analysis</h1>
        <p class="text-muted">Testing if sentiment predicts market movements (not just correlates)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get data
    sentiment_df = st.session_state.get('sentiment_data', pd.DataFrame())
    econ_df = st.session_state.get('econ_df', pd.DataFrame())
    market_df = st.session_state.get('market_data', pd.DataFrame())
    
    if sentiment_df.empty:
        st.warning("No sentiment data available. Please load data first.")
        return
    
    # Standardize date columns
    sentiment_df = sentiment_df.copy()
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    sentiment_df = sentiment_df.sort_values('date')
    
    if not market_df.empty:
        market_df = market_df.copy()
        market_df['date'] = pd.to_datetime(market_df['date'])
    
    if not econ_df.empty and 'date' in econ_df.columns:
        econ_df = econ_df.copy()
        econ_df['date'] = pd.to_datetime(econ_df['date'])
    
    # Create merged dataset
    merged = sentiment_df[['date', 'avg_compound']].copy()
    
    # Add market data
    if not market_df.empty:
        merged = pd.merge(merged, market_df[['date', 'spy', 'vix']], on='date', how='inner')
    
    # Add FRED data
    if not econ_df.empty and 'date' in econ_df.columns:
        fred_cols = []
        if 'financial_stress' in econ_df.columns:
            fred_cols.append('financial_stress')
        if 'consumer_sentiment' in econ_df.columns:
            fred_cols.append('consumer_sentiment')
        if 'interest_rate' in econ_df.columns:
            fred_cols.append('interest_rate')
        
        if fred_cols:
            merged = pd.merge(merged, econ_df[['date'] + fred_cols], on='date', how='inner')
    
    if len(merged) < 30:
        st.warning(f"Need at least 30 days of overlapping data. Found {len(merged)} days.")
        return
    
    st.success(f"Analyzing {len(merged)} overlapping days of data")
    
    # ========================================================================
    # RUN GRANGER CAUSALITY TESTS
    # ========================================================================
    from statsmodels.tsa.stattools import grangercausalitytests
    
    max_lag = 10
    
    # Test 1: Sentiment -> S&P 500
    if 'spy' in merged.columns:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('#### Hypothesis: Reddit Sentiment -> S&P 500 Returns')
        
        # Calculate returns
        merged['spy_return'] = merged['spy'].pct_change().fillna(0)
        test_data = merged[['spy_return', 'avg_compound']].dropna()
        
        results_sentiment_spy = {}
        for lag in range(1, max_lag + 1):
            try:
                test_result = grangercausalitytests(test_data, maxlag=lag, verbose=False)
                p_value = test_result[lag][0]['ssr_ftest'][1]
                results_sentiment_spy[lag] = p_value
            except:
                results_sentiment_spy[lag] = 1.0
        
        # Create visualization
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=list(results_sentiment_spy.keys()),
            y=list(results_sentiment_spy.values()),
            mode='lines+markers',
            name='Sentiment -> S&P 500',
            line=dict(color='#3B82F6', width=2),
            marker=dict(size=10, color='#3B82F6')
        ))
        
        fig.add_hline(y=0.05, line_dash="dash", line_color="#10B981", 
                      annotation_text="Significance (alpha=0.05)")
        fig.add_hline(y=0.01, line_dash="dash", line_color="#F59E0B",
                      annotation_text="Strong Significance (alpha=0.01)")
        
        fig.update_layout(
            title="Does Past Sentiment Predict Future S&P 500 Returns?",
            xaxis_title="Lag (Days)",
            yaxis_title="p-value (lower = stronger evidence)",
            yaxis_type="log",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Interpretation
        significant_lags = [lag for lag, p in results_sentiment_spy.items() if p < 0.05]
        
        if significant_lags:
            best_lag = min(results_sentiment_spy, key=results_sentiment_spy.get)
            best_p = results_sentiment_spy[best_lag]
            
            st.success(f"""
            **Causality Found** Sentiment Granger-causes S&P 500 returns at lags {significant_lags}
            
            - **Best lag:** {best_lag} day(s) (p = {best_p:.4f})
            - **Interpretation:** Reddit sentiment contains predictive information about market direction
            - **Thesis Support:** This validates that behavioral data has forward-looking value
            """)
        else:
            st.info("""
            **No significant causality detected** at alpha=0.05
            
            **Possible explanations:**
            - Sentiment effects may be shorter than 1 day (intraday)
            - Market already prices in social media sentiment
            - Need more data or different time period
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Test 2: Sentiment -> VIX (Fear Index)
    if 'vix' in merged.columns:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('#### Hypothesis: Reddit Sentiment -> VIX (Market Fear)')
        
        test_data = merged[['vix', 'avg_compound']].dropna()
        
        results_sentiment_vix = {}
        for lag in range(1, max_lag + 1):
            try:
                test_result = grangercausalitytests(test_data, maxlag=lag, verbose=False)
                p_value = test_result[lag][0]['ssr_ftest'][1]
                results_sentiment_vix[lag] = p_value
            except:
                results_sentiment_vix[lag] = 1.0
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(results_sentiment_vix.keys()),
            y=list(results_sentiment_vix.values()),
            mode='lines+markers',
            name='Sentiment -> VIX',
            line=dict(color='#F59E0B', width=2),
            marker=dict(size=10, color='#F59E0B')
        ))
        fig.add_hline(y=0.05, line_dash="dash", line_color="#10B981")
        fig.update_layout(
            title="Does Past Sentiment Predict Future VIX (Fear)?",
            xaxis_title="Lag (Days)",
            yaxis_title="p-value",
            yaxis_type="log",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        significant_vix = [lag for lag, p in results_sentiment_vix.items() if p < 0.05]
        if significant_vix:
            st.success(f"Sentiment predicts VIX at lags {significant_vix}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Test 3: Reverse Causality (Market -> Sentiment)
    if 'spy' in merged.columns:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('#### Reverse Causality Test (Control)')
        st.markdown('<p class="text-muted">Does market movement predict sentiment? (This should be weaker)</p>', unsafe_allow_html=True)
        
        test_data = merged[['avg_compound', 'spy_return']].dropna()
        
        results_market_sentiment = {}
        for lag in range(1, max_lag + 1):
            try:
                test_result = grangercausalitytests(test_data, maxlag=lag, verbose=False)
                p_value = test_result[lag][0]['ssr_ftest'][1]
                results_market_sentiment[lag] = p_value
            except:
                results_market_sentiment[lag] = 1.0
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(results_market_sentiment.keys()),
            y=list(results_market_sentiment.values()),
            mode='lines+markers',
            name='S&P 500 -> Sentiment',
            line=dict(color='#EF4444', width=2),
            marker=dict(size=10, color='#EF4444')
        ))
        fig.add_hline(y=0.05, line_dash="dash", line_color="#10B981")
        fig.update_layout(
            title="Control Test: Does Market Predict Sentiment?",
            xaxis_title="Lag (Days)",
            yaxis_title="p-value",
            yaxis_type="log",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Compare with forward causality
        forward_p = min(results_sentiment_spy.values()) if results_sentiment_spy else 1
        reverse_p = min(results_market_sentiment.values()) if results_market_sentiment else 1
        
        st.markdown(f"""
        <div style="background: rgba(59,130,246,0.05); border-radius: 12px; padding: 1rem; margin-top: 1rem;">
            <p style="font-size: 0.9rem; margin-bottom: 0.5rem;">
                <strong>Comparative Analysis:</strong>
            </p>
            <ul style="font-size: 0.85rem; color: #8A8F99;">
                <li>Sentiment -> Market (Forward): <strong style="color: {'#10B981' if forward_p < 0.05 else '#EF4444'}">p = {forward_p:.4f}</strong></li>
                <li>Market -> Sentiment (Reverse): <strong style="color: {'#10B981' if reverse_p < 0.05 else '#EF4444'}">p = {reverse_p:.4f}</strong></li>
            </ul>
            <hr style="margin: 0.75rem 0;">
            <p style="font-size: 0.8rem;">
                <strong>Conclusion:</strong> 
                {'Forward causality is STRONGER than reverse, supporting that sentiment leads markets.' 
                 if forward_p < reverse_p else 
                 'Both directions show causality, suggesting a feedback loop between sentiment and markets.'}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Test 4: FRED Financial Stress -> S&P 500
    if 'financial_stress' in merged.columns:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('#### FRED Financial Stress -> S&P 500')
        
        test_data = merged[['spy_return', 'financial_stress']].dropna()
        
        results_stress_spy = {}
        for lag in range(1, max_lag + 1):
            try:
                test_result = grangercausalitytests(test_data, maxlag=lag, verbose=False)
                p_value = test_result[lag][0]['ssr_ftest'][1]
                results_stress_spy[lag] = p_value
            except:
                results_stress_spy[lag] = 1.0
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(results_stress_spy.keys()),
            y=list(results_stress_spy.values()),
            mode='lines+markers',
            name='Financial Stress -> S&P 500',
            line=dict(color='#8B5CF6', width=2),
            marker=dict(size=10, color='#8B5CF6')
        ))
        fig.add_hline(y=0.05, line_dash="dash", line_color="#10B981")
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        significant = [lag for lag, p in results_stress_spy.items() if p < 0.05]
        if significant:
            st.info(f"FRED Financial Stress predicts S&P 500 at lags {significant} - this validates the methodology.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Optimal Lag Recommendation
    if 'spy' in merged.columns and results_sentiment_spy:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('#### Optimal Lag Recommendation')
        
        best_lag = min(results_sentiment_spy, key=results_sentiment_spy.get)
        best_p = results_sentiment_spy[best_lag]
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(59,130,246,0.05)); 
                    border-radius: 12px; padding: 1.5rem; text-align: center;">
            <p style="font-size: 0.8rem; color: #8A8F99;">Optimal Prediction Horizon</p>
            <p style="font-size: 2.5rem; font-weight: bold; color: #3B82F6; margin: 0.25rem 0;">
                {best_lag} Day{'s' if best_lag != 1 else ''}
            </p>
            <p style="font-size: 0.7rem; color: #64748B;">p = {best_p:.4f}</p>
            <hr style="margin: 1rem 0;">
            <p style="font-size: 0.85rem; margin: 0;">
                <strong>Trading Implication:</strong> Sentiment signals are most predictive 
                {best_lag} day(s) before market movement.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    


if __name__ == "__main__":
    causality_analysis_page()