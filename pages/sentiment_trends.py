"""
Sentiment Trends page - using CSV data with tutorial highlights.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta
from visualizations import create_sentiment_trend_chart, create_heatmap, create_sankey_diagram, display_word_cloud
from data_fetcher import get_companies_list, filter_by_company
from event_data import add_event_hover_text, MARKET_EVENTS, get_event_color

def sentiment_trends_page():
    st.markdown('<h1>Sentiment Trends</h1>', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">Multi-dimensional analysis of sentiment patterns over time</p>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    # ========================================================================
    # LOAD DATA FROM SESSION STATE
    # ========================================================================
    sentiment_df = st.session_state.get('sentiment_data', pd.DataFrame())
    posts_df = st.session_state.get('posts_data', pd.DataFrame())
    market_df = st.session_state.get('market_data', pd.DataFrame())

    if sentiment_df.empty:
        st.warning("No sentiment data available. Please check your data source.")
        return

    # Ensure date column is datetime
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])

    # ========================================================================
    # COMPANY FILTER
    # ========================================================================
    companies = get_companies_list(posts_df) if not posts_df.empty else []
    selected_company = st.sidebar.selectbox("Filter by Company", ["All"] + companies)
    
    if selected_company != "All" and not posts_df.empty:
        filtered_posts = filter_by_company(posts_df, selected_company)
        filtered_posts = filtered_posts.copy()
        filtered_posts['date'] = pd.to_datetime(filtered_posts['date'])
        sentiment_df = filtered_posts.groupby('date').agg(
            positive=('sentiment', lambda x: (x == 'positive').sum()),
            neutral=('sentiment', lambda x: (x == 'neutral').sum()),
            negative=('sentiment', lambda x: (x == 'negative').sum()),
            avg_compound=('compound', 'mean')
        ).reset_index()
        sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])

    # ========================================================================
    # EVENT MARKERS SECTION (COMPLETELY REWRITTEN)
    # ========================================================================
    st.markdown('''
            <div class="card" data-tutorial="company-stats" style="padding: 0.5rem;">
                <h4> Sentiment with Real-World Events</h4>
            ''', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">Hover over markers to see what caused sentiment spikes</p>', unsafe_allow_html=True)
    # Create base figure
    fig_events = go.Figure()

    # Add main sentiment line
    fig_events.add_trace(go.Scatter(
        x=sentiment_df['date'],
        y=sentiment_df['avg_compound'],
        mode='lines',
        name='Sentiment Score',
        line=dict(color='#F59E0B', width=2),
        hovertemplate='<b>%{x|%b %d, %Y}</b><br>Sentiment: %{y:.3f}<extra></extra>'
    ))

    # Convert sentiment_df dates to string for easier comparison
    sentiment_date_strings = set(sentiment_df['date'].dt.strftime('%Y-%m-%d'))

    # Add event markers
    for date_str, event in MARKET_EVENTS.items():
        event_date = pd.to_datetime(date_str)
        
        # Check if event date is in our data range
        if date_str in sentiment_date_strings:
            # Get sentiment value at this exact date
            event_row = sentiment_df[sentiment_df['date'].dt.strftime('%Y-%m-%d') == date_str]
            if not event_row.empty:
                y_pos = event_row['avg_compound'].iloc[0]
                
                color = get_event_color(event['category'])
                
                # Add vertical line
                fig_events.add_vline(
                    x=event_date,
                    line_dash="dash",
                    line_color=color,
                    line_width=1.5,
                    opacity=0.5
                )
                
                # Add marker dot
                fig_events.add_trace(go.Scatter(
                    x=[event_date],
                    y=[y_pos],
                    mode='markers',
                    marker=dict(size=14, color=color, symbol='circle', line=dict(color='white', width=2)),
                    name=event['title'],
                    hovertemplate=f"""
                    <b> {date_str}</b><br>
                    <b>{event['title']}</b><br>
                    ━━━━━━━━━━━━━━━━━━━━<br>
                     {event['description']}<br>
                     Impact: {event['impact']}<br>
                     Sentiment: {y_pos:.3f}<br>
                    <extra></extra>
                    """,
                    showlegend=False
                ))

    fig_events.update_layout(
        title="Sentiment Trends with Real-World Event Markers (Feb-Mar 2021)",
        xaxis_title="Date",
        yaxis_title="Sentiment Score (Compound)",
        height=500,
        hovermode="x unified",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8A8F99')
    )

    st.plotly_chart(fig_events, use_container_width=True, key="sentiment_with_events")
    st.markdown('</div>', unsafe_allow_html=True)

    # ========================================================================
    # TABS
    # ========================================================================
    tab1, tab2, tab3, tab4, tab6 = st.tabs(["All Trends", "VIX Scatter", "Heatmap", "Forecast", "Word Cloud"])

    with tab1:

        fig = create_sentiment_trend_chart(sentiment_df)
        st.plotly_chart(fig, use_container_width=True, key="sentiment_trend_main")
        st.markdown("""
        <p class="text-muted">Sentiment volume over time. Positive (green), Neutral (gray), Negative (red).</p>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<h3>Sentiment vs VIX Scatter</h3>', unsafe_allow_html=True)
        
        if not market_df.empty and not sentiment_df.empty:
            sentiment_copy = sentiment_df.copy()
            sentiment_copy['date'] = pd.to_datetime(sentiment_copy['date'])
            market_copy = market_df.copy()
            market_copy['date'] = pd.to_datetime(market_copy['date'])
            merged = pd.merge(sentiment_copy, market_copy, left_on='date', right_on='date', how='inner')
            if not merged.empty:
                merged['sentiment_ratio'] = merged['positive'] / (merged['positive'] + merged['negative'] + 1)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=merged['vix'], 
                    y=merged['sentiment_ratio'],
                    mode='markers',
                    marker=dict(
                        size=10, 
                        color=merged['anomaly_score'] if 'anomaly_score' in merged.columns else merged['sentiment_ratio'], 
                        colorscale='Viridis', 
                        showscale=True,
                        colorbar=dict(title="Anomaly Score")
                    ),
                    text=merged['date'].dt.strftime('%Y-%m-%d'),
                    hovertemplate='Date: %{text}<br>VIX: %{x:.1f}<br>Sentiment Ratio: %{y:.2f}<extra></extra>'
                ))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#8A8F99'), 
                    xaxis_title="VIX (Fear Index)", 
                    yaxis_title="Positive Sentiment Ratio",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True, key="sentiment_vix_scatter")
                
                correlation = merged['vix'].corr(merged['sentiment_ratio'])
                st.markdown(f"""
                <div style="margin-top: 1rem; background: rgba(59,130,246,0.05); border-radius: 8px; padding: 0.75rem;">
                    <p style="font-size: 0.7rem; color: #8A8F99;">
                        <strong>Correlation:</strong> {correlation:.3f}<br>
                        {'Negative correlation: Higher fear = more negative sentiment' if correlation < 0 else 'Positive correlation: Fear and sentiment move together'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No overlapping dates between sentiment and market data.")
        else:
            st.info("Insufficient data for scatter plot.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<h3>Sentiment Correlation Heatmap</h3>', unsafe_allow_html=True)
        fig = create_heatmap()
        st.plotly_chart(fig, use_container_width=True, key="sentiment_heatmap")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown('<h3>Sentiment Forecast (Next 30 Days)</h3>', unsafe_allow_html=True)
        st.markdown('<p class="text-muted">Based on recent sentiment trends and mean reversion assumption</p>', unsafe_allow_html=True)
        
        if not sentiment_df.empty and len(sentiment_df) >= 7:
            sentiment_copy = sentiment_df.copy()
            sentiment_copy['ratio'] = sentiment_copy['positive'] / (sentiment_copy['positive'] + sentiment_copy['negative']).replace(0, 1)
            
            window = min(7, len(sentiment_copy))
            recent_ratios = sentiment_copy['ratio'].tail(window).values
            
            weights = np.exp(np.linspace(-1, 0, window))
            weights = weights / weights.sum()
            weighted_avg = np.average(recent_ratios, weights=weights)
            
            NEUTRAL_LEVEL = 0.5
            reversion_speed = 0.08
            
            forecast = []
            current_value = weighted_avg
            
            for i in range(30):
                current_value = current_value + reversion_speed * (NEUTRAL_LEVEL - current_value)
                noise = np.random.normal(0, 0.02 + i * 0.001)
                current_value = np.clip(current_value + noise, 0, 1)
                forecast.append(current_value)
            
            forecast = np.array(forecast)
            
            upper_bound = forecast + 0.08 + np.linspace(0, 0.05, 30)
            lower_bound = forecast - 0.08 - np.linspace(0, 0.05, 30)
            upper_bound = np.clip(upper_bound, 0, 1)
            lower_bound = np.clip(lower_bound, 0, 1)
            
            future_dates = pd.date_range(start=sentiment_copy['date'].max() + timedelta(days=1), periods=30, freq='D')
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=future_dates, y=upper_bound,
                mode='lines', name='Upper Bound (85% CI)',
                line=dict(width=0), showlegend=True,
                fillcolor='rgba(59,130,246,0.1)', fill='tonexty'
            ))
            
            fig.add_trace(go.Scatter(
                x=future_dates, y=lower_bound,
                mode='lines', name='Lower Bound (85% CI)',
                line=dict(width=0), showlegend=False,
                fill='tonexty'
            ))
            
            fig.add_trace(go.Scatter(
                x=future_dates, y=forecast,
                mode='lines', name='Forecast',
                line=dict(color='#3B82F6', width=2)
            ))
            
            historical_dates = sentiment_copy['date'].tail(14)
            historical_ratios = sentiment_copy['ratio'].tail(14)
            
            fig.add_trace(go.Scatter(
                x=historical_dates, y=historical_ratios,
                mode='lines+markers', name='Historical (Last 14 days)',
                line=dict(color='#F59E0B', width=2),
                marker=dict(size=6, color='#F59E0B')
            ))
            
            fig.add_hline(y=0.5, line_dash="dash", line_color="#8A8F99", 
                        annotation_text="Neutral (0.5)", annotation_position="top right")
            fig.add_hline(y=0.7, line_dash="dot", line_color="#10B981", 
                        annotation_text="Elevated", annotation_position="top right")
            fig.add_hline(y=0.3, line_dash="dot", line_color="#EF4444", 
                        annotation_text="Depressed", annotation_position="bottom right")
            
            fig.update_yaxes(range=[0, 1])
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8A8F99'),
                xaxis_title="Date",
                yaxis_title="Positive Sentiment Ratio",
                height=450,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True, key="sentiment_forecast")
            
            col1, col2 = st.columns(2)
            
            with col1:
                first_week_avg = forecast[:7].mean()
                last_week_avg = forecast[-7:].mean()
                trend_direction = "decreasing" if last_week_avg < first_week_avg else "increasing"
                
                st.markdown(f"""
                <div style="background: rgba(59,130,246,0.05); border-radius: 8px; padding: 0.75rem;">
                    <p style="font-size: 0.7rem; color: #8A8F99; margin: 0;">Forecast Trend</p>
                    <p style="font-size: 1.2rem; font-weight: bold; color: #3B82F6; margin: 0;">
                        {trend_direction.upper()}
                    </p>
                    <p style="font-size: 0.6rem; color: #64748B;">
                        Week 1: {first_week_avg:.2f} → Week 4: {last_week_avg:.2f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                current_level = weighted_avg
                if current_level > 0.65:
                    level_text = "Elevated / Euphoric"
                    level_color = "#10B981"
                elif current_level > 0.55:
                    level_text = "Mildly Positive"
                    level_color = "#34D399"
                elif current_level > 0.45:
                    level_text = "Neutral"
                    level_color = "#8A8F99"
                elif current_level > 0.35:
                    level_text = "Mildly Negative"
                    level_color = "#F97316"
                else:
                    level_text = "Depressed / Fearful"
                    level_color = "#EF4444"
                
                st.markdown(f"""
                <div style="background: rgba(59,130,246,0.05); border-radius: 8px; padding: 0.75rem;">
                    <p style="font-size: 0.7rem; color: #8A8F99; margin: 0;">Current Sentiment Level</p>
                    <p style="font-size: 1.2rem; font-weight: bold; color: {level_color}; margin: 0;">
                        {level_text}
                    </p>
                    <p style="font-size: 0.6rem; color: #64748B;">
                        Weighted average: {current_level:.3f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            if weighted_avg > 0.6:
                st.success("Forecast Interpretation: Positive sentiment is expected to remain elevated, with a gradual decline toward neutral levels.")
            elif weighted_avg < 0.4:
                st.error("Forecast Interpretation: Negative sentiment dominates. Recovery toward neutral levels is expected over the next 30 days.")
            else:
                st.info("Forecast Interpretation: Sentiment is near neutral levels. Expect moderate fluctuations around the current range.")
        else:
            st.warning("Not enough historical data (need at least 7 days) for reliable forecast.")
        
        st.markdown('</div>', unsafe_allow_html=True)

    with tab6:
        st.markdown('<h3>Word Cloud of All Posts</h3>', unsafe_allow_html=True)
        posts_data = st.session_state.get('posts_data', pd.DataFrame())
        if not posts_data.empty:
            all_text = ' '.join(posts_data['title'].fillna('')) + ' ' + ' '.join(posts_data['selftext'].fillna(''))
            words = all_text.split()
            from collections import Counter
            import re
            word_freq = Counter()
            stop_words = {'the', 'and', 'for', 'that', 'this', 'with', 'you', 'are', 'not', 'have', 'from', 'they', 'will', 'what', 'your', 'can', 'was', 'but', 'all', 'has', 'been', 'one', 'would', 'there', 'their', 'about', 'were', 'been', 'could', 'should', 'would', 'amp', 'get', 'out', 'like', 'just', 'know', 'people', 'time', 'good', 'well', 'now', 'then'}
            
            for word in words:
                clean_word = re.sub(r'[^\w\s]', '', word.lower())
                if len(clean_word) > 2 and clean_word not in stop_words:
                    word_freq[clean_word] += 1
            
            display_word_cloud(dict(word_freq.most_common(100)))
        else:
            st.info("No posts to display.")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    sentiment_trends_page()