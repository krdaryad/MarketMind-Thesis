"""
Granger Causality Analysis - Corrected for Monthly Data Frequency
Uses monthly Consumer Sentiment (FRED UMCSENT) and monthly S&P 500 returns
Includes VECM for adjustment speed estimation
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def causality_analysis_page():
    st.markdown('<h1>Granger Causality Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">Testing if Consumer Sentiment predicts market movements (Monthly frequency)</p>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="card" style="padding: 1rem; margin-bottom: 1rem;">
        <h3 style="font-size: 1.1rem; margin-top: 0;">Research Hypothesis (Monthly Alignment)</h3>
        <p style="font-size: 0.85rem; margin-bottom: 0.5rem;">
            <strong>H₀ (Null):</strong> Past consumer sentiment does NOT help predict monthly market returns.<br>
            <strong>H₁ (Alternative):</strong> Past consumer sentiment DOES help predict monthly market returns.<br>
            <strong>Decision Rule:</strong> Reject H₀ if p < 0.05 (95% confidence level)
        </p>
        <hr style="margin: 0.75rem 0;">
        <p style="font-size: 0.7rem; color: #64748B; margin: 0;">
            <strong>Methodology:</strong> Both series aligned to monthly frequency (end of month).<br>
            No forward-filling – avoids look-ahead bias.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Load data from session state or fetch fresh
    econ_df = st.session_state.get('econ_df', pd.DataFrame())
    
    if econ_df.empty or 'consumer_sentiment' not in econ_df.columns:
        with st.spinner("Loading Consumer Sentiment data from FRED..."):
            try:
                from data_loader import load_real_economic_data
                ticker = "SPY"
                start_date = "2000-01-01"  # Longer history for monthly analysis
                end_date = datetime.today().strftime("%Y-%m-%d")
                economic_data, econ_df = load_real_economic_data(ticker, start_date, end_date)
                st.session_state.econ_df = econ_df
                st.session_state.economic_data = economic_data
            except Exception as e:
                st.error(f"Error loading data: {e}")
                return
    
    if 'consumer_sentiment' not in econ_df.columns:
        st.error("Consumer Sentiment data not available.")
        return
    
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
    
    # ------------------------------------------------------------
    # CORRECTED: Monthly alignment (NO forward-filling)
    # ------------------------------------------------------------
    df.set_index('date', inplace=True)
    monthly_prices = df[price_col].resample('ME').last()
    monthly_sentiment = df['consumer_sentiment'].resample('ME').last()
    
    monthly_df = pd.DataFrame({
        'price': monthly_prices,
        'consumer_sentiment': monthly_sentiment
    }).dropna()
    
    # Calculate monthly log returns
    monthly_df['market_return'] = np.log(monthly_df['price'] / monthly_df['price'].shift(1))
    monthly_df = monthly_df.dropna()
    
    if len(monthly_df) < 24:
        st.warning(f"Need at least 24 months of data. Found {len(monthly_df)} months.")
        return
    
    # Prepare data for Granger test
    test_data = monthly_df[['market_return', 'consumer_sentiment']].dropna()
    
    st.sidebar.markdown("### Test Configuration (Monthly Lags)")
    max_lag = st.sidebar.slider(
        "Maximum Lag (Months)",
        min_value=1, max_value=12, value=6,
        help="Number of previous months to test for predictive power"
    )
    
    show_reverse = st.sidebar.checkbox(
        "Show Reverse Causality Test", value=True,
        help="Test if market returns also predict consumer sentiment (control test)"
    )
    
    from statsmodels.tsa.stattools import grangercausalitytests
    
    # ---------- Forward test: Sentiment -> Returns ----------
    st.markdown('''
    <div class="card" style="padding: 0.5rem;">
        <h3 style="font-size: 1.1rem; margin-top: 0;">Test: Consumer Sentiment → S&P 500 Monthly Returns</h3>
    ''', unsafe_allow_html=True)
    
    results = {}
    for lag in range(1, max_lag + 1):
        try:
            test_result = grangercausalitytests(test_data[['market_return', 'consumer_sentiment']], maxlag=lag, verbose=False)
            p_value = test_result[lag][0]['ssr_ftest'][1]
            results[lag] = p_value
        except Exception:
            results[lag] = 1.0
    
    best_lag = min(results, key=results.get)
    best_p = results[best_lag]
    is_significant = best_p < 0.05
    
    confidence = (1 - best_p) * 100
    confidence_display = f"{confidence:.1f}%" if confidence < 99.95 else ">99.9%"
    
    if is_significant:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.05)); 
                    border-left: 4px solid #10B981; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
            <p style="font-size: 1rem; font-weight: bold; color: #10B981; margin: 0;">
                Causation Found (p = {best_p:.4f} < 0.05)
            </p>
            <p style="font-size: 0.85rem; margin: 0.5rem 0 0 0;">
                Consumer Sentiment Granger-causes market returns at {best_lag} month(s) lag.
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
    
    fig = go.Figure()
    fig.add_hrect(y0=0, y1=0.05, line_width=0, fillcolor="rgba(16,185,129,0.15)",
                  annotation_text="Significance (p < 0.05)", annotation_position="top left", annotation_font_size=10)
    fig.add_hrect(y0=0, y1=0.01, line_width=0, fillcolor="rgba(16,185,129,0.3)",
                  annotation_text="Strong Evidence (p < 0.01)", annotation_position="top left", annotation_font_size=10)
    fig.add_trace(go.Scatter(
        x=list(results.keys()), y=list(results.values()),
        mode='lines+markers', name='Sentiment → Returns',
        line=dict(color='#3B82F6', width=3), marker=dict(size=10)
    ))
    fig.add_trace(go.Scatter(
        x=[best_lag], y=[best_p], mode='markers',
        name=f'Best lag: {best_lag} month(s)',
        marker=dict(size=15, color='#F59E0B', symbol='star', line=dict(width=2, color='white'))
    ))
    fig.update_layout(
        title="Granger Causality: Monthly Consumer Sentiment vs. S&P 500 Returns",
        xaxis_title="Lag (Months)", yaxis_title="p-value (lower = stronger evidence)",
        yaxis_type="log", yaxis_range=[-4, 0], height=450,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#8A8F99')
    )
    st.plotly_chart(fig, use_container_width=True, key="granger_main")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        status_color = "#10B981" if is_significant else "#EF4444"
        status_text = "Significant" if is_significant else "Not Significant"
        st.markdown(f"<div class='metric-card' style='text-align:center;'><p class='tech-label'>Causality Status</p><p class='tech-val' style='color:{status_color};'>{status_text}</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card' style='text-align:center;'><p class='tech-label'>Optimal Lag</p><p class='tech-val' style='color:#3B82F6;'>{best_lag} Month(s)</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card' style='text-align:center;'><p class='tech-label'>Confidence Level</p><p class='tech-val' style='color:#F59E0B;'>{confidence_display}</p></div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ---------- Reverse test: Returns -> Sentiment ----------
    if show_reverse:
        st.markdown('''
        <div class="card" style="padding: 0.5rem;">
            <h3 style="font-size: 1.1rem; margin-top: 0;">Control Test: Returns → Consumer Sentiment</h3>
        ''', unsafe_allow_html=True)
        
        # Prepare data in correct order: dependent = consumer_sentiment, independent = market_return
        reverse_data = test_data[['consumer_sentiment', 'market_return']].dropna()
        reverse_results = {}
        for lag in range(1, max_lag + 1):
            try:
                test_result = grangercausalitytests(reverse_data, maxlag=lag, verbose=False)
                p_value = test_result[lag][0]['ssr_ftest'][1]
                reverse_results[lag] = p_value
            except Exception:
                reverse_results[lag] = 1.0
        
        if any(v < 1.0 for v in reverse_results.values()):
            best_rev_lag = min(reverse_results, key=reverse_results.get)
            best_rev_p = reverse_results[best_rev_lag]
            
            fig_rev = go.Figure()
            fig_rev.add_hrect(y0=0, y1=0.05, line_width=0, fillcolor="rgba(16,185,129,0.15)")
            fig_rev.add_trace(go.Scatter(
                x=list(reverse_results.keys()), y=list(reverse_results.values()),
                mode='lines+markers', name='Returns → Sentiment',
                line=dict(color='#EF4444', width=2), marker=dict(size=8)
            ))
            fig_rev.update_layout(
                title="Control: Do Market Returns Predict Consumer Sentiment?",
                xaxis_title="Lag (Months)", yaxis_title="p-value",
                yaxis_type="log", yaxis_range=[-4, 0], height=400,
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#8A8F99')
            )
            st.plotly_chart(fig_rev, use_container_width=True, key="granger_reverse")
            
            if best_p < best_rev_p:
                st.markdown(f"""
                <div style="margin-top:1rem; background:rgba(16,185,129,0.1); border-radius:8px; padding:0.75rem;">
                    <p style="font-size:0.8rem; margin:0;"><strong>Conclusion:</strong> Consumer sentiment is a pure lead indicator.<br>
                    Forward causality (p={best_p:.4f}) is stronger than reverse (p={best_rev_p:.4f}).</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="margin-top:1rem; background:rgba(245,158,11,0.1); border-radius:8px; padding:0.75rem;">
                    <p style="font-size:0.8rem; margin:0;"><strong>Conclusion:</strong> A feedback loop exists.<br>
                    Both directions show causality (Forward: p={best_p:.4f}, Reverse: p={best_rev_p:.4f}).</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Could not compute reverse causality – check data alignment.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ---------- Cointegration and VECM ----------
    with st.expander("Robustness: Cointegration & Vector Error Correction Model (VECM)"):
        from statsmodels.tsa.vector_ar.vecm import coint_johansen, VECM
        
        # Johansen test
        data_coint = test_data[['consumer_sentiment', 'market_return']].dropna().values
        if len(data_coint) > 20:
            johansen = coint_johansen(data_coint, det_order=0, k_ar_diff=1)
            trace_stat = johansen.lr1[0]
            trace_crit = johansen.cvt[0, 1]  # 95% critical value
            st.markdown(f"""
            **Johansen Cointegration Test** (trace statistic):<br>
            Test statistic = {trace_stat:.2f}<br>
            95% critical value = {trace_crit:.2f}<br>
            {'✓ Series are cointegrated (long‑run relationship exists)' if trace_stat > trace_crit else '✗ No cointegration detected'}
            """, unsafe_allow_html=True)
            
            # VECM estimation if cointegration present
            if trace_stat > trace_crit:
                st.markdown("---")
                st.markdown("#### Speed of Adjustment (Error Correction Term)")
                try:
                    # Use levels (price, not returns) for VECM
                    vecm_data = monthly_df[['consumer_sentiment', 'price']].dropna()
                    model = VECM(vecm_data, k_ar_diff=1, coint_rank=1, deterministic='ci')
                    vecm_result = model.fit()
                    
                    # Adjustment coefficients (alpha)
                    adjust_price = vecm_result.alpha[1, 0]      # price equation
                    adjust_sentiment = vecm_result.alpha[0, 0]  # sentiment equation
                    
                    half_life = abs(np.log(2) / adjust_price) if adjust_price != 0 else float('inf')
                    
                    st.markdown(f"""
                    <div style="background:rgba(59,130,246,0.05); border-radius:8px; padding:0.75rem;">
                        <p><strong>Error Correction Term (α):</strong></p>
                        <ul>
                            <li><strong>Market price</strong> corrects <strong>{abs(adjust_price)*100:.1f}%</strong> of the disequilibrium each month.</li>
                            <li><strong>Consumer sentiment</strong> corrects <strong>{abs(adjust_sentiment)*100:.1f}%</strong> of the disequilibrium each month.</li>
                        </ul>
                        <p style="font-size:0.75rem;">
                            <strong>Interpretation:</strong> 
                            {'A negative α for price means that when price is above equilibrium, it decreases toward it.' if adjust_price < 0 else 'Price moves away from equilibrium – unusual.'}
                            The half‑life of a shock is approximately <strong>{half_life:.1f} months</strong>.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    
                except Exception as e:
                    st.warning(f"VECM failed: {e}")
            else:
                st.info("No cointegration detected – VECM not appropriate. Use VAR on differenced data instead.")
        else:
            st.info("Insufficient data for cointegration test (need >20 months).")
    
    with st.expander("Methodology (Corrected for Monthly Frequency)"):
        st.markdown("""
        **Why this version is statistically sound:**
        
        1. **No forward‑filling** – Both series are aligned at monthly frequency using end‑of‑month values. Avoids look‑ahead bias.
        2. **Log returns** – Ensures stationarity, a prerequisite for Granger causality.
        3. **Monthly lags** – Respects the actual data frequency; a 1‑month lag means the previous month's sentiment.
        4. **No artificial daily points** – Eliminates spurious significance caused by interpolated data.
        5. **VECM adjustment speed** – Quantifies how quickly the market returns to equilibrium after a sentiment shock.
        
        **Interpretation:**
        - p < 0.05 → Reject null (sentiment predicts returns)
        - p > 0.05 → No predictive relationship detected
        - VECM α (negative) → speed of correction toward long‑run equilibrium
        """)
    
if __name__ == "__main__":
    causality_analysis_page()