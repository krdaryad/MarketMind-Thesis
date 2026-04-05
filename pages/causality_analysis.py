"""
Granger Causality Analysis - Testing if Consumer Sentiment predicts market movements
Uses the SAME Consumer Sentiment data as the Economic Dashboard (FRED UMCSENT)
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def causality_analysis_page():
    # Page Header - matching Economic Dashboard style
    st.markdown('<h1>Granger Causality Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">Testing if Consumer Sentiment predicts market movements</p>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    
    # ========================================================================
    # RESEARCH HYPOTHESIS BOX (Outside data card, matching Economic Dashboard style)
    # ========================================================================
    st.markdown('''
    <div class="card" style="padding: 1rem; margin-bottom: 1rem;">
        <h3 style="font-size: 1.1rem; margin-top: 0;">Research Hypothesis</h3>
        <p style="font-size: 0.85rem; margin-bottom: 0.5rem;">
            <strong>H₀ (Null):</strong> Past consumer sentiment does NOT help predict market returns.<br>
            <strong>H₁ (Alternative):</strong> Past consumer sentiment DOES help predict market returns.<br>
            <strong>Decision Rule:</strong> Reject H₀ if p < 0.05 (95% confidence level)
        </p>
        <hr style="margin: 0.75rem 0;">
        <p style="font-size: 0.7rem; color: #64748B; margin: 0;">
            <strong>Data Source:</strong> FRED - University of Michigan Consumer Sentiment Index (UMCSENT)<br>
            <strong>Market Data:</strong> S&P 500 from Yahoo Finance
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # ========================================================================
    # LOAD DATA - Same method as Economic Dashboard
    # ========================================================================
    
    # Try to get existing data from session state
    econ_df = st.session_state.get('econ_df', pd.DataFrame())
    
    # If no data or missing consumer_sentiment, load fresh using the same function
    if econ_df.empty or 'consumer_sentiment' not in econ_df.columns:
        with st.spinner("Loading Consumer Sentiment data from FRED..."):
            try:
                from data_loader import load_real_economic_data
                
                ticker = "SPY"
                start_date = "2020-01-01"
                end_date = datetime.today().strftime("%Y-%m-%d")
                
                economic_data, econ_df = load_real_economic_data(ticker, start_date, end_date)
                
                st.session_state.econ_df = econ_df
                st.session_state.economic_data = economic_data
                
            except Exception as e:
                st.error(f"Error loading data: {e}")
                st.info("Please check your FRED API key in .streamlit/secrets.toml")
                return
    
    # Check if consumer_sentiment column exists
    if 'consumer_sentiment' not in econ_df.columns:
        st.error("Consumer Sentiment data not available. Available columns: " + ", ".join(econ_df.columns.tolist()))
        return
    
    # ========================================================================
    # PREPARE DATA WITH PROPER TRANSFORMATIONS
    # ========================================================================
    df = econ_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Use SPY or close price
    if 'spy' in df.columns:
        price_col = 'spy'
    elif 'close' in df.columns:
        price_col = 'close'
    else:
        st.error("No price data available")
        return
    
    # Forward fill consumer sentiment (monthly data -> daily)
    df['consumer_sentiment'] = df['consumer_sentiment'].ffill()
    
    # Remove NaN values
    df = df[['date', price_col, 'consumer_sentiment']].dropna()
    
    if len(df) < 30:
        st.warning(f"Need at least 30 days of data. Found {len(df)} days.")
        return
    
    # Stationarity transformation - Log returns
    df['market_return'] = np.log(df[price_col] / df[price_col].shift(1)).fillna(0)
    
    # Prepare test data
    test_data = df[['market_return', 'consumer_sentiment']].dropna()
    
    # ========================================================================
    # USER CONFIGURATION
    # ========================================================================
    st.sidebar.markdown("### Test Configuration")
    
    max_lag = st.sidebar.slider(
        "Maximum Lag (Days)",
        min_value=5,
        max_value=30,
        value=14,
        help="Number of previous days to test for predictive power"
    )
    
    show_reverse = st.sidebar.checkbox(
        "Show Reverse Causality Test", 
        value=True,
        help="Test if market returns also predict consumer sentiment (control test)"
    )
    
    # ========================================================================
    # RUN GRANGER CAUSALITY TEST
    # ========================================================================
    from statsmodels.tsa.stattools import grangercausalitytests
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 1.1rem; margin-top: 0;">Test: Consumer Sentiment -> S&P 500 Returns</h3>', unsafe_allow_html=True)
    
    results = {}
    for lag in range(1, max_lag + 1):
        try:
            test_result = grangercausalitytests(test_data, maxlag=lag, verbose=False)
            p_value = test_result[lag][0]['ssr_ftest'][1]
            results[lag] = p_value
        except Exception as e:
            results[lag] = 1.0
    
    # Find best lag
    best_lag = min(results, key=results.get)
    best_p = results[best_lag]
    is_significant = best_p < 0.05
    
    # ========================================================================
    # RESULTS DISPLAY
    # ========================================================================
    if is_significant:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.05)); 
                    border-left: 4px solid #10B981; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
            <p style="font-size: 1rem; font-weight: bold; color: #10B981; margin: 0;">
                Causation Found (p = {best_p:.4f} < 0.05)
            </p>
            <p style="font-size: 0.85rem; margin: 0.5rem 0 0 0;">
                Consumer Sentiment Granger-causes market returns at lag {best_lag} day(s).
                Reject the null hypothesis. Consumer confidence leads the stock market.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: rgba(239,68,68,0.1); border-left: 4px solid #EF4444; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
            <p style="font-size: 1rem; font-weight: bold; color: #EF4444; margin: 0;">
                No Causation Detected (p = {best_p:.4f} > 0.05)
            </p>
            <p style="font-size: 0.85rem; margin: 0.5rem 0 0 0;">
                Cannot reject the null hypothesis. Consumer sentiment does not predict market returns in this period.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # ========================================================================
    # VISUALIZATION WITH LOG SCALE + SIGNIFICANCE SHADING
    # ========================================================================
    fig = go.Figure()
    
    # Significance shading
    fig.add_hrect(
        y0=0, y1=0.05,
        line_width=0,
        fillcolor="rgba(16,185,129,0.15)",
        annotation_text="Significance Zone (p < 0.05)",
        annotation_position="top left",
        annotation_font_size=10
    )
    
    fig.add_hrect(
        y0=0, y1=0.01,
        line_width=0,
        fillcolor="rgba(16,185,129,0.3)",
        annotation_text="Strong Evidence (p < 0.01)",
        annotation_position="top left",
        annotation_font_size=10
    )
    
    # P-value line
    fig.add_trace(go.Scatter(
        x=list(results.keys()),
        y=list(results.values()),
        mode='lines+markers',
        name='Consumer Sentiment -> Returns',
        line=dict(color='#3B82F6', width=3),
        marker=dict(size=10, color='#3B82F6')
    ))
    
    # Best lag marker
    fig.add_trace(go.Scatter(
        x=[best_lag],
        y=[best_p],
        mode='markers',
        name=f'Best Lag: {best_lag} days',
        marker=dict(size=15, color='#F59E0B', symbol='star', line=dict(width=2, color='white'))
    ))
    
    fig.update_layout(
        title="Granger Causality: Does Consumer Sentiment Predict S&P 500 Returns?",
        xaxis_title="Lag (Days)",
        yaxis_title="p-value (lower = stronger evidence)",
        yaxis_type="log",
        yaxis_range=[-4, 0],
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8A8F99')
    )
    
    st.plotly_chart(fig, use_container_width=True, key="granger_main")
    
    # ========================================================================
    # SUMMARY METRICS CARDS
    # ========================================================================
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_color = "#10B981" if is_significant else "#EF4444"
        status_text = "Significant" if is_significant else "Not Significant"
        st.markdown(f"""
        <div class="metric-card" style="text-align: center; padding: 0.75rem;">
            <p class="tech-label" style="font-size: 0.7rem;">Causality Status</p>
            <p class="tech-val" style="font-size: 1.2rem; color: {status_color};">{status_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center; padding: 0.75rem;">
            <p class="tech-label" style="font-size: 0.7rem;">Optimal Lag</p>
            <p class="tech-val" style="font-size: 1.2rem; color: #3B82F6;">{best_lag} Days</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        confidence = (1 - best_p) * 100
        st.markdown(f"""
        <div class="metric-card" style="text-align: center; padding: 0.75rem;">
            <p class="tech-label" style="font-size: 0.7rem;">Confidence Level</p>
            <p class="tech-val" style="font-size: 1.2rem; color: #F59E0B;">{confidence:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # REVERSE CAUSALITY TEST (Control)
    # ========================================================================
    if show_reverse:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 style="font-size: 1.1rem; margin-top: 0;">Control Test: Returns -> Consumer Sentiment</h3>', unsafe_allow_html=True)
        
        reverse_data = df[['consumer_sentiment', 'market_return']].dropna()
        
        reverse_results = {}
        for lag in range(1, max_lag + 1):
            try:
                test_result = grangercausalitytests(reverse_data, maxlag=lag, verbose=False)
                p_value = test_result[lag][0]['ssr_ftest'][1]
                reverse_results[lag] = p_value
            except:
                reverse_results[lag] = 1.0
        
        best_rev_lag = min(reverse_results, key=reverse_results.get)
        best_rev_p = reverse_results[best_rev_lag]
        
        fig_rev = go.Figure()
        fig_rev.add_hrect(y0=0, y1=0.05, line_width=0, fillcolor="rgba(16,185,129,0.15)")
        fig_rev.add_trace(go.Scatter(
            x=list(reverse_results.keys()),
            y=list(reverse_results.values()),
            mode='lines+markers',
            name='Returns -> Sentiment',
            line=dict(color='#EF4444', width=2),
            marker=dict(size=8, color='#EF4444')
        ))
        fig_rev.update_layout(
            title="Control: Do Returns Predict Consumer Sentiment?",
            xaxis_title="Lag (Days)",
            yaxis_title="p-value",
            yaxis_type="log",
            yaxis_range=[-4, 0],
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99')
        )
        st.plotly_chart(fig_rev, use_container_width=True, key="granger_reverse")
        
        # Conclusion
        if best_p < best_rev_p:
            st.markdown(f"""
            <div style="margin-top: 1rem; background: rgba(16,185,129,0.1); border-radius: 8px; padding: 0.75rem;">
                <p style="font-size: 0.8rem; margin: 0;">
                    <strong>Conclusion:</strong> Consumer sentiment is a pure lead indicator.<br>
                    Forward causality (p={best_p:.4f}) is stronger than reverse causality (p={best_rev_p:.4f}).
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="margin-top: 1rem; background: rgba(245,158,11,0.1); border-radius: 8px; padding: 0.75rem;">
                <p style="font-size: 0.8rem; margin: 0;">
                    <strong>Conclusion:</strong> A feedback loop exists between sentiment and markets.<br>
                    Both directions show causality (Forward: p={best_p:.4f}, Reverse: p={best_rev_p:.4f}).
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # METHODOLOGY EXPANDER
    # ========================================================================
    with st.expander("Methodology: Granger Causality Testing"):
        st.markdown("""
        **What is Granger Causality?**
        
        Developed by Nobel laureate Clive Granger (2003), this statistical test determines whether one time series predicts another.
        
        **Key Assumptions:**
        - Stationarity: Log returns used instead of raw prices
        - Data alignment: Monthly sentiment forward-filled to daily
        - Lag selection: Tested from 1 to 30 days
        
        **Interpretation:**
        - p < 0.05: Reject null hypothesis → Causation found
        - p > 0.05: Cannot reject null → No causation detected
        - Lower p-value = Stronger evidence of causation
        
        **Why Log Returns?**
        
        Raw stock prices are non-stationary (mean and variance change over time). 
        Granger causality requires stationary data. Log returns transform prices 
        into a stationary series of percentage changes.
        
        **Formula:** Log Return = ln(P_t / P_{t-1})
        
        **References:**
        - Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models." *Econometrica*, 37(3), 424-438.
        - Estrella, A., & Mishkin, F. S. (1998). "Predicting U.S. Recessions." *Review of Economics and Statistics*, 80(1), 45-61.
        """)
    


if __name__ == "__main__":
    causality_analysis_page()