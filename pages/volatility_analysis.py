"""
Volatility Trend Analysis - Rolling volatility and sentiment correlation
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from event_data import MARKET_EVENTS, get_event_color

def volatility_analysis_page():
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="margin: 0;">Volatility Trend Analysis</h1>
        <p class="text-muted">Rolling volatility patterns and sentiment correlation with event markers</p>
    </div>
    """, unsafe_allow_html=True)
    
    sentiment_df = st.session_state.get('sentiment_data', pd.DataFrame())
    posts_df = st.session_state.get('posts_data', pd.DataFrame())
    
    if sentiment_df.empty:
        st.warning("No sentiment data available")
        return
    
    sentiment_df = sentiment_df.copy()
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    sentiment_df = sentiment_df.sort_values('date')
    
    # Calculate rolling volatility of sentiment
    sentiment_df['sentiment_volatility'] = sentiment_df['avg_compound'].rolling(7, min_periods=3).std()
    sentiment_df['sentiment_volatility_30d'] = sentiment_df['avg_compound'].rolling(30, min_periods=10).std()
    
    # Calculate volume volatility if available
    if 'post_count' in sentiment_df.columns:
        sentiment_df['volume_volatility'] = sentiment_df['post_count'].rolling(7, min_periods=3).std()
    
    # Get sentiment date strings for event filtering
    sentiment_date_strings = set(sentiment_df['date'].dt.strftime('%Y-%m-%d'))
    
    # Create figure with subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Sentiment Score', 'Sentiment Volatility (7-day rolling)', 'Post Volume Volatility'),
        vertical_spacing=0.12,
        shared_xaxes=True
    )
    
    # Row 1: Sentiment Score
    fig.add_trace(go.Scatter(
        x=sentiment_df['date'],
        y=sentiment_df['avg_compound'],
        mode='lines',
        name='Sentiment Score',
        line=dict(color='#3B82F6', width=2),
        fill='tozeroy',
        fillcolor='rgba(59,130,246,0.1)',
        hovertemplate='<b>%{x|%b %d, %Y}</b><br>Sentiment: %{y:.3f}<extra></extra>'
    ), row=1, col=1)
    fig.add_hline(y=0.05, line_dash="dash", line_color="#10B981", row=1, col=1,
                  annotation_text="Bullish Threshold")
    fig.add_hline(y=-0.05, line_dash="dash", line_color="#EF4444", row=1, col=1,
                  annotation_text="Bearish Threshold")
    
    # Row 2: Sentiment Volatility
    fig.add_trace(go.Scatter(
        x=sentiment_df['date'],
        y=sentiment_df['sentiment_volatility'],
        mode='lines',
        name='Sentiment Volatility',
        line=dict(color='#F59E0B', width=2),
        fill='tozeroy',
        fillcolor='rgba(245,158,11,0.2)',
        hovertemplate='<b>%{x|%b %d, %Y}</b><br>Volatility: %{y:.4f}<extra></extra>'
    ), row=2, col=1)
    
    # Add high volatility threshold
    high_vol_threshold = sentiment_df['sentiment_volatility'].quantile(0.75)
    fig.add_hline(y=high_vol_threshold, line_dash="dash", line_color="#EF4444", row=2, col=1,
                  annotation_text=f"High Volatility (>{high_vol_threshold:.3f})")
    
    # Row 3: Volume Volatility
    if 'volume_volatility' in sentiment_df.columns:
        fig.add_trace(go.Scatter(
            x=sentiment_df['date'],
            y=sentiment_df['volume_volatility'],
            mode='lines',
            name='Volume Volatility',
            line=dict(color='#EC4899', width=2),
            fill='tozeroy',
            fillcolor='rgba(236,72,153,0.2)',
            hovertemplate='<b>%{x|%b %d, %Y}</b><br>Volume Volatility: %{y:.1f}<extra></extra>'
        ), row=3, col=1)
    
    # ========================================================================
    # ADD EVENT MARKERS TO ALL SUBPLOTS
    # ========================================================================
    for date_str, event in MARKET_EVENTS.items():
        event_date = pd.to_datetime(date_str)
        
        # Check if event date is in our data range
        if date_str in sentiment_date_strings:
            
            # Get sentiment value at this date for marker position
            event_row = sentiment_df[sentiment_df['date'].dt.strftime('%Y-%m-%d') == date_str]
            if not event_row.empty:
                y_pos_row1 = event_row['avg_compound'].iloc[0]
                y_pos_row2 = event_row['sentiment_volatility'].iloc[0]
                y_pos_row3 = event_row['volume_volatility'].iloc[0] if 'volume_volatility' in sentiment_df.columns else None
                
                color = get_event_color(event['category'])
                
                # Add vertical line to all rows
                for row in range(1, 4):
                    fig.add_vline(
                        x=event_date,
                        line_dash="dash",
                        line_color=color,
                        line_width=1,
                        opacity=0.4,
                        row=row, col=1
                    )
                
                # Add marker dot to Row 1 (Sentiment Score)
                fig.add_trace(go.Scatter(
                    x=[event_date],
                    y=[y_pos_row1],
                    mode='markers',
                    marker=dict(size=12, color=color, symbol='circle', line=dict(color='white', width=2)),
                    name=event['title'],
                    hovertemplate=f"""
                    <b> {date_str}</b><br>
                    <b>{event['title']}</b><br>
                    ━━━━━━━━━━━━━━━━━━━━<br>
                     {event['description']}<br>
                     Impact: {event['impact']}<br>
                     Sentiment: {y_pos_row1:.3f}<br>
                    <extra></extra>
                    """,
                    showlegend=False
                ), row=1, col=1)
                
                # Add marker dot to Row 2 (Volatility)
                fig.add_trace(go.Scatter(
                    x=[event_date],
                    y=[y_pos_row2],
                    mode='markers',
                    marker=dict(size=12, color=color, symbol='circle', line=dict(color='white', width=2)),
                    name=event['title'],
                    hovertemplate=f"""
                    <b> {date_str}</b><br>
                    <b>{event['title']}</b><br>
                    ━━━━━━━━━━━━━━━━━━━━<br>
                     {event['description']}<br>
                     Impact: {event['impact']}<br>
                     Volatility: {y_pos_row2:.4f}<br>
                    <extra></extra>
                    """,
                    showlegend=False
                ), row=2, col=1)
                
                # Add marker dot to Row 3 (Volume Volatility) if available
                if y_pos_row3 is not None:
                    fig.add_trace(go.Scatter(
                        x=[event_date],
                        y=[y_pos_row3],
                        mode='markers',
                        marker=dict(size=12, color=color, symbol='circle', line=dict(color='white', width=2)),
                        name=event['title'],
                        hovertemplate=f"""
                        <b> {date_str}</b><br>
                        <b>{event['title']}</b><br>
                        ━━━━━━━━━━━━━━━━━━━━<br>
                         {event['description']}<br>
                         Impact: {event['impact']}<br>
                         Volume Volatility: {y_pos_row3:.1f}<br>
                        <extra></extra>
                        """,
                        showlegend=False
                    ), row=3, col=1)

    fig.update_layout(
        height=900,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8A8F99')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # VOLATILITY STATISTICS WITH EVENT CONTEXT
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Volatility Statistics</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Sentiment Volatility", f"{sentiment_df['sentiment_volatility'].mean():.4f}")
    with col2:
        st.metric("Max Sentiment Volatility", f"{sentiment_df['sentiment_volatility'].max():.4f}")
    with col3:
        st.metric("High Volatility Periods", f"{(sentiment_df['sentiment_volatility'] > high_vol_threshold).sum()} days")
    with col4:
        volatility_sentiment_corr = sentiment_df['sentiment_volatility'].corr(sentiment_df['avg_compound'].abs())
        st.metric("Volatility-Sentiment Correlation", f"{volatility_sentiment_corr:.3f}")
    
    # Find highest volatility event
    max_vol_idx = sentiment_df['sentiment_volatility'].idxmax()
    max_vol_date = sentiment_df.loc[max_vol_idx, 'date']
    max_vol_date_str = max_vol_date.strftime('%Y-%m-%d')
    
    # Check if this date has an event
    if max_vol_date_str in MARKET_EVENTS:
        event = MARKET_EVENTS[max_vol_date_str]
        st.markdown(f"""
        <div style="margin-top: 1rem; background: rgba(239,68,68,0.1); border-left: 4px solid #EF4444; border-radius: 8px; padding: 0.75rem;">
            <p style="font-size: 0.75rem; margin: 0;">
                <strong> Peak Volatility Event:</strong> The highest sentiment volatility occurred on <strong>{max_vol_date.strftime('%B %d, %Y')}</strong><br>
                 <strong>{event['title']}</strong><br>
                 {event['description']}<br>
                 Impact: {event['impact']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    volatility_analysis_page()