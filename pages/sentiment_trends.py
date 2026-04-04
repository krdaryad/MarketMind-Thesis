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

def sentiment_trends_page():
    st.markdown('<h1>📈 Sentiment Trends</h1>', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">Multi-dimensional analysis of sentiment patterns over time</p>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    # Get sentiment data from session state
    sentiment_df = st.session_state.get('sentiment_data', pd.DataFrame())
    posts_df = st.session_state.get('posts_data', pd.DataFrame())
    market_df = st.session_state.get('market_data', pd.DataFrame())

    if sentiment_df.empty:
        st.warning("No sentiment data available. Please check your data source.")
        return

    # Company filter
    companies = get_companies_list(posts_df) if not posts_df.empty else []
    selected_company = st.sidebar.selectbox("Filter by Company", ["All"] + companies)
    
    if selected_company != "All" and not posts_df.empty:
        filtered_posts = filter_by_company(posts_df, selected_company)
        filtered_posts = filtered_posts.copy()
        filtered_posts['date'] = pd.to_datetime(filtered_posts['date'])
        sentiment_df = filtered_posts.groupby('date').agg(
            positive=('sentiment', lambda x: (x == 'positive').sum()),
            neutral=('sentiment', lambda x: (x == 'neutral').sum()),
            negative=('sentiment', lambda x: (x == 'negative').sum())
        ).reset_index()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["All Trends", "VIX Scatter", "Heatmap", "Forecast", "Flow", "Word Cloud"])

    with tab1:
        # ====================================================================
        # SENTIMENT CHART - TUTORIAL HIGHLIGHT
        # ====================================================================
        st.markdown('<div class="card" data-tutorial="sentiment-chart">', unsafe_allow_html=True)
        fig = create_sentiment_trend_chart(sentiment_df)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
        <p class="text-muted">Sentiment volume over time. Positive (green), Neutral (gray), Negative (red).</p>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        # ====================================================================
        # VIX SCATTER - TUTORIAL HIGHLIGHT
        # ====================================================================
        st.markdown('<div class="card" data-tutorial="vix-tab">', unsafe_allow_html=True)
        st.markdown('<h3>Sentiment vs VIX Scatter</h3>', unsafe_allow_html=True)
        if not market_df.empty and not sentiment_df.empty:
            sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
            merged = pd.merge(sentiment_df, market_df, left_on='date', right_on='date', how='inner')
            if not merged.empty:
                # Calculate sentiment ratio for y-axis
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
                st.plotly_chart(fig, use_container_width=True)
                
                # Add correlation info
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
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Sentiment Correlation Heatmap</h3>', unsafe_allow_html=True)
        fig = create_heatmap()
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Sentiment Forecast (Next 30 Days)</h3>', unsafe_allow_html=True)
        if not sentiment_df.empty:
            if 'anomaly_score' in sentiment_df.columns:
                last_score = sentiment_df['anomaly_score'].iloc[-1]
            else:
                sentiment_ratio = sentiment_df['positive'] / (sentiment_df['positive'] + sentiment_df['negative'] + 1)
                last_score = sentiment_ratio.iloc[-1]
            
            future_dates = pd.date_range(start=sentiment_df['date'].max() + timedelta(days=1), periods=30, freq='D')
            # Simple moving average forecast
            if len(sentiment_df) >= 7:
                window = min(7, len(sentiment_df))
                recent_avg = sentiment_df['positive'].tail(window).mean() if 'positive' in sentiment_df.columns else last_score
                base_forecast = np.linspace(recent_avg, recent_avg * 0.8, 30)
            else:
                base_forecast = np.linspace(last_score, 0.3, 30)
            
            forecast = base_forecast + np.random.normal(0, 0.05, 30)
            forecast = np.clip(forecast, 0, 1)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=future_dates, y=forecast,
                mode='lines', name='Forecast',
                line=dict(color='#3B82F6', width=2),
                fill='tozeroy', fillcolor='rgba(59,130,246,0.2)'
            ))
            fig.add_hline(y=0.5, line_dash="dash", line_color="#F59E0B", annotation_text="Neutral Threshold")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8A8F99'), xaxis_title="Date", yaxis_title="Predicted Positive Ratio",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for forecast.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab5:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Sentiment Flow (Sankey Diagram)</h3>', unsafe_allow_html=True)
        st.markdown('<p class="text-muted">Shows how sentiment shifts between months.</p>', unsafe_allow_html=True)
        fig = create_sankey_diagram()
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab6:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Word Cloud of All Posts</h3>', unsafe_allow_html=True)
        posts_df = st.session_state.get('posts_data', pd.DataFrame())
        if not posts_df.empty:
            # Combine all text from titles and selftext
            all_text = ' '.join(posts_df['title'].fillna('')) + ' ' + ' '.join(posts_df['selftext'].fillna(''))
            
            # Filter out common words and short words
            words = all_text.split()
            from collections import Counter
            import re
            word_freq = Counter()
            stop_words = {'the', 'and', 'for', 'that', 'this', 'with', 'you', 'are', 'not', 'have', 'from', 'they', 'will', 'what', 'your', 'can', 'was', 'but', 'all', 'has', 'been', 'one', 'would', 'there', 'their', 'about', 'were', 'been', 'could', 'should', 'would', 'amp', 'get', 'out', 'like', 'just', 'know', 'people', 'time', 'good', 'well', 'now', 'then'}
            
            for word in words:
                # Filter out URLs, punctuation, and short words
                clean_word = re.sub(r'[^\w\s]', '', word.lower())
                if len(clean_word) > 2 and clean_word not in stop_words:
                    word_freq[clean_word] += 1
            
            display_word_cloud(dict(word_freq.most_common(100)))
        else:
            st.info("No posts to display.")
        st.markdown('</div>', unsafe_allow_html=True)