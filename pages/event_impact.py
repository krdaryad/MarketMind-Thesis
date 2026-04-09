"""
Event Impact Assessment - Analyzing market reactions to specific events
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

def event_impact_page():
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="margin: 0;">Event Impact Assessment</h1>
        <p class="text-muted">Analyzing market and sentiment reactions to specific events</p>
    </div>
    """, unsafe_allow_html=True)
    
    sentiment_df = st.session_state.get('sentiment_data', pd.DataFrame())
    posts_df = st.session_state.get('posts_data', pd.DataFrame())
    market_df = st.session_state.get('market_data', pd.DataFrame())
    
    if sentiment_df.empty:
        st.warning("No sentiment data available")
        return
    
    sentiment_df = sentiment_df.copy()
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    
    # Define key events (you can modify these)
    events = {
        'GameStop Peak': '2021-01-28',
        'Fed Rate Decision': '2021-03-17',
        'CPI Release': '2021-02-10',
        'Jobs Report': '2021-02-05',
        'Congress Hearing': '2021-02-18'
    }
    
    st.markdown('<h3>Select Event to Analyze</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        selected_event = st.selectbox("Choose Event", list(events.keys()))
    
    with col2:
        event_window = st.slider("Analysis Window (days before/after)", 1, 30, 10)
    
    event_date = pd.to_datetime(events[selected_event])
    
    # Calculate date range
    start_date = event_date - timedelta(days=event_window)
    end_date = event_date + timedelta(days=event_window)
    
    # Filter data
    event_sentiment = sentiment_df[(sentiment_df['date'] >= start_date) & 
                                   (sentiment_df['date'] <= end_date)].copy()
    
    if event_sentiment.empty:
        st.warning(f"No data available for {selected_event}")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    event_sentiment['days_from_event'] = (event_sentiment['date'] - event_date).dt.days
    
    # Calculate pre and post averages
    pre_event = event_sentiment[event_sentiment['days_from_event'] < 0]
    post_event = event_sentiment[event_sentiment['days_from_event'] > 0]
    day_of_event = event_sentiment[event_sentiment['days_from_event'] == 0]
    
    pre_avg = pre_event['avg_compound'].mean() if not pre_event.empty else 0
    post_avg = post_event['avg_compound'].mean() if not post_event.empty else 0
    event_day_avg = day_of_event['avg_compound'].mean() if not day_of_event.empty else 0
    
    # Create visualization
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=event_sentiment['days_from_event'],
        y=event_sentiment['avg_compound'],
        mode='lines+markers',
        name='Sentiment Score',
        line=dict(color='#3B82F6', width=2),
        marker=dict(size=8, color='#3B82F6')
    ))
    
    # Add event marker
    fig.add_vline(x=0, line_dash="dash", line_color="#EF4444",
                  annotation_text=selected_event, annotation_position="top")
    
    # Add pre/post averages
    fig.add_hline(y=pre_avg, line_dash="dot", line_color="#F59E0B",
                  annotation_text=f"Pre-Event Avg: {pre_avg:.3f}")
    fig.add_hline(y=post_avg, line_dash="dot", line_color="#10B981",
                  annotation_text=f"Post-Event Avg: {post_avg:.3f}")
    
    fig.update_layout(
        title=f"Sentiment Impact: {selected_event}",
        xaxis_title=f"Days from Event (Day 0 = {event_date.strftime('%Y-%m-%d')})",
        yaxis_title="Sentiment Score",
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8A8F99')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Impact metrics
    st.markdown('<h4>Event Impact Metrics</h4>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        delta = post_avg - pre_avg
        st.metric("Sentiment Change", f"{delta:+.3f}", 
                  delta_color="normal" if delta > 0 else "inverse")
    with col2:
        st.metric("Pre-Event Avg", f"{pre_avg:.3f}")
    with col3:
        st.metric("Day of Event", f"{event_day_avg:.3f}")
    with col4:
        st.metric("Post-Event Avg", f"{post_avg:.3f}")
    
    # Impact classification
    if delta > 0.1:
        impact = "Strong Positive"
        color = "#10B981"
    elif delta > 0.03:
        impact = "Moderate Positive"
        color = "#34D399"
    elif delta > -0.03:
        impact = "Neutral"
        color = "#8A8F99"
    elif delta > -0.1:
        impact = "Moderate Negative"
        color = "#F97316"
    else:
        impact = "Strong Negative"
        color = "#EF4444"
    
    st.markdown(f"""
    <div style="margin-top: 1rem; background: {color}10; border-left: 4px solid {color}; padding: 1rem; border-radius: 8px;">
        <p style="margin: 0; font-size: 1rem; font-weight: bold; color: {color};">Impact Classification: {impact}</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.75rem; color: #8A8F99;">
            Sentiment changed by {delta:+.3f} points following the event.
            {'This suggests the event had a significant effect on investor sentiment.' if abs(delta) > 0.05 else 'This suggests limited impact on overall sentiment.'}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    event_impact_page()