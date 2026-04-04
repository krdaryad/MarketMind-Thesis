"""
Sentiment Shock Detection - Identifies statistically significant sentiment regime shifts
Using FRED economic data + Reddit sentiment for multi-source validation
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

def shock_detection_page():
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="margin: 0;">Sentiment Shock Detection</h1>
        <p class="text-muted">Identifying regime shifts using statistical anomaly detection (|Z| > 2)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get data from session state
    sentiment_df = st.session_state.get('sentiment_data', pd.DataFrame())
    econ_df = st.session_state.get('econ_df', pd.DataFrame())
    
    if sentiment_df.empty:
        st.warning("No sentiment data available. Please load data first.")
        return
    
    # Standardize date columns
    sentiment_df = sentiment_df.copy()
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    sentiment_df = sentiment_df.sort_values('date')
    
    if not econ_df.empty and 'date' in econ_df.columns:
        econ_df = econ_df.copy()
        econ_df['date'] = pd.to_datetime(econ_df['date'])
    
    # ========================================================================
    # DETECT SHOCKS IN REDDIT SENTIMENT
    # ========================================================================
    sentiment_df['rolling_mean'] = sentiment_df['avg_compound'].rolling(7, min_periods=1).mean()
    sentiment_df['rolling_std'] = sentiment_df['avg_compound'].rolling(7, min_periods=1).std()
    sentiment_df['z_score'] = (sentiment_df['avg_compound'] - sentiment_df['rolling_mean']) / sentiment_df['rolling_std'].replace(0, 0.1)
    sentiment_df['is_shock'] = np.abs(sentiment_df['z_score']) > 2
    
    # Identify shock clusters (consecutive days)
    sentiment_df['shock_cluster'] = (sentiment_df['is_shock'] != sentiment_df['is_shock'].shift()).cumsum()
    
    # Extract shock events
    shocks = []
    for cluster, group in sentiment_df[sentiment_df['is_shock']].groupby('shock_cluster'):
        if len(group) >= 1:
            shocks.append({
                'start_date': group['date'].iloc[0],
                'end_date': group['date'].iloc[-1],
                'duration': len(group),
                'peak_z': group['z_score'].abs().max(),
                'direction': 'Positive' if group['avg_compound'].mean() > 0 else 'Negative',
                'avg_sentiment': group['avg_compound'].mean(),
                'max_sentiment': group['avg_compound'].max(),
                'min_sentiment': group['avg_compound'].min()
            })
    
    # ========================================================================
    # DETECT SHOCKS IN FRED DATA (if available)
    # ========================================================================
    fred_indicators = []
    if not econ_df.empty:
        econ_df = econ_df.copy()
        
        if 'financial_stress' in econ_df.columns:
            econ_df['stress_rolling_mean'] = econ_df['financial_stress'].rolling(20, min_periods=1).mean()
            econ_df['stress_rolling_std'] = econ_df['financial_stress'].rolling(20, min_periods=1).std()
            econ_df['stress_z_score'] = (econ_df['financial_stress'] - econ_df['stress_rolling_mean']) / econ_df['stress_rolling_std'].replace(0, 0.1)
            econ_df['stress_shock'] = econ_df['stress_z_score'] > 2
            fred_indicators.append('Financial Stress')
        
        if 'vix' in econ_df.columns:
            econ_df['vix_rolling_mean'] = econ_df['vix'].rolling(20, min_periods=1).mean()
            econ_df['vix_rolling_std'] = econ_df['vix'].rolling(20, min_periods=1).std()
            econ_df['vix_z_score'] = (econ_df['vix'] - econ_df['vix_rolling_mean']) / econ_df['vix_rolling_std'].replace(0, 0.1)
            econ_df['vix_shock'] = econ_df['vix_z_score'] > 2
            fred_indicators.append('VIX')
        
        if 'consumer_sentiment' in econ_df.columns:
            econ_df['consumer_rolling_mean'] = econ_df['consumer_sentiment'].rolling(20, min_periods=1).mean()
            econ_df['consumer_rolling_std'] = econ_df['consumer_sentiment'].rolling(20, min_periods=1).std()
            econ_df['consumer_z_score'] = (econ_df['consumer_sentiment'] - econ_df['consumer_rolling_mean']) / econ_df['consumer_rolling_std'].replace(0, 0.1)
            econ_df['consumer_shock'] = econ_df['consumer_z_score'] < -2
            fred_indicators.append('Consumer Sentiment')
    
    # ========================================================================
    # CREATE MULTI-SOURCE VISUALIZATION
    # ========================================================================
    if fred_indicators:
        fig = make_subplots(
            rows=len(fred_indicators) + 1, cols=1,
            subplot_titles=['Reddit Sentiment'] + fred_indicators,
            vertical_spacing=0.08,
            shared_xaxes=True
        )
        
        # Row 1: Reddit Sentiment
        fig.add_trace(go.Scatter(
            x=sentiment_df['date'],
            y=sentiment_df['avg_compound'],
            mode='lines',
            name='Reddit Sentiment',
            line=dict(color='#3B82F6', width=2)
        ), row=1, col=1)
        
        # Add shock markers for sentiment
        shock_points = sentiment_df[sentiment_df['is_shock']]
        if not shock_points.empty:
            fig.add_trace(go.Scatter(
                x=shock_points['date'],
                y=shock_points['avg_compound'],
                mode='markers',
                name='Sentiment Shock',
                marker=dict(size=10, color='#EF4444', symbol='circle', line=dict(color='white', width=2))
            ), row=1, col=1)
        
        # Add threshold lines for sentiment
        fig.add_hline(y=0.05, line_dash="dash", line_color="#10B981", row=1, col=1, 
                      annotation_text="Bullish Threshold")
        fig.add_hline(y=-0.05, line_dash="dash", line_color="#EF4444", row=1, col=1,
                      annotation_text="Bearish Threshold")
        
        # Row 2+: FRED Indicators
        row = 2
        if 'financial_stress' in econ_df.columns:
            fig.add_trace(go.Scatter(
                x=econ_df['date'],
                y=econ_df['financial_stress'],
                mode='lines',
                name='Financial Stress',
                line=dict(color='#F59E0B', width=2),
                fill='tozeroy'
            ), row=row, col=1)
            
            stress_shocks = econ_df[econ_df['stress_shock']]
            if not stress_shocks.empty:
                fig.add_trace(go.Scatter(
                    x=stress_shocks['date'],
                    y=stress_shocks['financial_stress'],
                    mode='markers',
                    name='Stress Shock',
                    marker=dict(size=10, color='#EF4444', symbol='circle')
                ), row=row, col=1)
            
            fig.add_hline(y=0.5, line_dash="dash", line_color="#EF4444", row=row, col=1,
                          annotation_text="Elevated Stress")
            row += 1
        
        if 'vix' in econ_df.columns:
            fig.add_trace(go.Scatter(
                x=econ_df['date'],
                y=econ_df['vix'],
                mode='lines',
                name='VIX',
                line=dict(color='#EF4444', width=2),
                fill='tozeroy'
            ), row=row, col=1)
            
            vix_shocks = econ_df[econ_df['vix_shock']]
            if not vix_shocks.empty:
                fig.add_trace(go.Scatter(
                    x=vix_shocks['date'],
                    y=vix_shocks['vix'],
                    mode='markers',
                    name='VIX Shock',
                    marker=dict(size=10, color='#F59E0B', symbol='circle')
                ), row=row, col=1)
            
            fig.add_hline(y=25, line_dash="dash", line_color="#EF4444", row=row, col=1,
                          annotation_text="Extreme Fear")
            row += 1
        
        if 'consumer_sentiment' in econ_df.columns:
            fig.add_trace(go.Scatter(
                x=econ_df['date'],
                y=econ_df['consumer_sentiment'],
                mode='lines',
                name='Consumer Sentiment',
                line=dict(color='#10B981', width=2),
                fill='tozeroy'
            ), row=row, col=1)
            
            consumer_shocks = econ_df[econ_df['consumer_shock']]
            if not consumer_shocks.empty:
                fig.add_trace(go.Scatter(
                    x=consumer_shocks['date'],
                    y=consumer_shocks['consumer_sentiment'],
                    mode='markers',
                    name='Sentiment Drop',
                    marker=dict(size=10, color='#EF4444', symbol='circle')
                ), row=row, col=1)
            
            fig.add_hline(y=80, line_dash="dash", line_color="#F59E0B", row=row, col=1,
                          annotation_text="Neutral")
        
        fig.update_layout(
            height=800,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99'),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        fig.update_xaxes(title_text="Date", row=row-1, col=1)
        fig.update_yaxes(title_text="Sentiment Score", row=1, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        # Fallback to sentiment-only mode
        st.info("FRED data not available. Showing sentiment-only analysis.")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sentiment_df['date'],
            y=sentiment_df['avg_compound'],
            mode='lines',
            name='Sentiment',
            line=dict(color='#3B82F6', width=2)
        ))
        
        # Add 2-standard deviation bands
        fig.add_trace(go.Scatter(
            x=sentiment_df['date'],
            y=sentiment_df['rolling_mean'] + 2 * sentiment_df['rolling_std'],
            mode='lines',
            name='Upper Bound (+2 sigma)',
            line=dict(color='rgba(239,68,68,0.5)', width=1, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=sentiment_df['date'],
            y=sentiment_df['rolling_mean'] - 2 * sentiment_df['rolling_std'],
            mode='lines',
            name='Lower Bound (-2 sigma)',
            line=dict(color='rgba(239,68,68,0.5)', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(239,68,68,0.05)'
        ))
        
        shock_points = sentiment_df[sentiment_df['is_shock']]
        if not shock_points.empty:
            fig.add_trace(go.Scatter(
                x=shock_points['date'],
                y=shock_points['avg_compound'],
                mode='markers',
                name='Shock Detected',
                marker=dict(size=10, color='#EF4444', symbol='circle', line=dict(color='white', width=2))
            ))
        
        fig.update_layout(
            title="Sentiment Shock Detection (|Z| > 2)",
            xaxis_title="Date",
            yaxis_title="Sentiment Score",
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # SHOCK STATISTICS SUMMARY
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Shock Statistics Summary</h3>', unsafe_allow_html=True)
    
    # Calculate shock statistics
    sentiment_shocks = sentiment_df['is_shock'].sum()
    sentiment_shock_pct = (sentiment_shocks / len(sentiment_df)) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Reddit Sentiment Shocks", sentiment_shocks, f"{sentiment_shock_pct:.1f}% of days")
    
    if 'stress_shock' in econ_df.columns:
        stress_shocks = econ_df['stress_shock'].sum()
        stress_pct = (stress_shocks / len(econ_df)) * 100
        with col2:
            st.metric("Financial Stress Shocks", stress_shocks, f"{stress_pct:.1f}% of days")
    
    if 'vix_shock' in econ_df.columns:
        vix_shocks = econ_df['vix_shock'].sum()
        vix_pct = (vix_shocks / len(econ_df)) * 100
        with col3:
            st.metric("VIX Shock Events", vix_shocks, f"{vix_pct:.1f}% of days")
    
    if 'consumer_shock' in econ_df.columns:
        consumer_shocks = econ_df['consumer_shock'].sum()
        consumer_pct = (consumer_shocks / len(econ_df)) * 100
        with col4:
            st.metric("Consumer Sentiment Drops", consumer_shocks, f"{consumer_pct:.1f}% of days")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # DETAILED SHOCK EVENTS TABLE
    # ========================================================================
    if shocks:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Detected Shock Events</h3>', unsafe_allow_html=True)
        
        shock_df = pd.DataFrame(shocks)
        display_df = shock_df.copy()
        display_df['start_date'] = pd.to_datetime(display_df['start_date']).dt.strftime('%Y-%m-%d')
        display_df['end_date'] = pd.to_datetime(display_df['end_date']).dt.strftime('%Y-%m-%d')
        display_df['avg_sentiment'] = display_df['avg_sentiment'].round(3)
        display_df['peak_z'] = display_df['peak_z'].round(2)
        
        st.dataframe(display_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ====================================================================
        # THESIS INSIGHT
        # ====================================================================
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Thesis Insight: Multi-Source Validation</h3>', unsafe_allow_html=True)
        
        # Find the most significant shock
        worst_shock = shock_df.loc[shock_df['peak_z'].idxmax()]
        
        # Calculate correlation with FRED if available
        correlation_text = ""
        if not econ_df.empty and 'financial_stress' in econ_df.columns:
            merged_corr = pd.merge(
                sentiment_df[['date', 'avg_compound']],
                econ_df[['date', 'financial_stress']],
                on='date', how='inner'
            )
            correlation = merged_corr['avg_compound'].corr(merged_corr['financial_stress'])
            correlation_text = f"""
            <p style="font-size: 0.85rem; margin-top: 0.5rem;">
                <strong>Correlation with FRED Financial Stress:</strong> {correlation:.3f}
                {'(Positive correlation confirms Reddit sentiment reflects real economic stress)' if correlation > 0.2 else '(Weak correlation suggests unique dynamics in social media)'}
            </p>
            """
        
        st.markdown(f"""
        <div style="background: rgba(59,130,246,0.05); border-radius: 12px; padding: 1rem;">
            <p style="font-size: 0.9rem; margin-bottom: 0.5rem;">
                <strong>Key Finding:</strong> The most significant sentiment shock occurred 
                on <strong>{pd.to_datetime(worst_shock['start_date']).strftime('%Y-%m-%d')}</strong> 
                with a Z-score of <strong>{worst_shock['peak_z']:.2f}</strong>.
            </p>
            <p style="font-size: 0.85rem; color: #8A8F99;">
                This {worst_shock['direction'].lower()} shock lasted {worst_shock['duration']} days, 
                with sentiment swinging from {worst_shock['min_sentiment']:.3f} to {worst_shock['max_sentiment']:.3f}.
            </p>
            {correlation_text}
            
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        
        
    else:
        st.info("No significant sentiment shocks detected in the current data range.")


if __name__ == "__main__":
    shock_detection_page()