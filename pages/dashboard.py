"""
Dashboard page - using CSV data with tutorial highlights.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from config import DEFAULT_START, DEFAULT_END
from data_fetcher import (
    load_reddit_data, filter_by_company, filter_by_date, filter_by_sentiment, filter_by_score,
    fetch_market_data, add_sentiment, aggregate_sentiment,
    get_company_stats, get_companies_list
)
from text_analysis import get_real_topics, get_real_patterns, get_real_model_results
from visualizations import create_heatmap, create_sentiment_trend_chart

def dashboard_page():
    st.markdown('<h1>Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">Overview · Market Correlation · Sentiment Trends</p>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    # ========================================================================
    # DATA LOADING WITH CACHE (Improvement #1 - already in data_fetcher.py)
    # ========================================================================
    posts_df = load_reddit_data()
    
    if posts_df.empty:
        st.error("No data loaded. Please check your CSV file path.")
        return
    
    # Get date range from sidebar
    if 'date_range' not in st.session_state:
        st.session_state.date_range = [datetime(2021, 2, 1), datetime(2021, 2, 28)]
    
    start_date, end_date = st.session_state.date_range
    
    # Filter by date
    posts_df = filter_by_date(posts_df, start_date, end_date)
    
    if posts_df.empty:
        st.warning(f"No posts found for date range {start_date} to {end_date}")
        return
    
    # Company filter from sidebar
    companies = get_companies_list(posts_df)
    selected_company = st.session_state.get('selected_company', 'All')
    
    if selected_company != 'All':
        posts_df = filter_by_company(posts_df, selected_company)
    
    # Sentiment filter
    sentiment_filter = st.session_state.get('sentiment_filter', 'All')
    posts_df = filter_by_sentiment(posts_df, sentiment_filter)
    
    # Score filter
    min_score = st.session_state.get('min_score', 0)
    posts_df = filter_by_score(posts_df, min_score)
    
    # Add sentiment
    posts_df = add_sentiment(posts_df)
    sentiment_df = aggregate_sentiment(posts_df)
    
    # ========================================================================
    # SESSION STATE OPTIMIZATION (Improvement #3 - Store only derived data)
    # ========================================================================
    # Only store what's needed for other pages
    st.session_state.posts_data = posts_df
    st.session_state.sentiment_data = sentiment_df
    
    # ========================================================================
    # DATA GHOSTING FIX (Improvement #5 - Clear state when data insufficient)
    # ========================================================================
    if len(posts_df) >= 10:
        st.session_state.topics = get_real_topics(posts_df)
        st.session_state.patterns = get_real_patterns(posts_df)
        st.session_state.model_results = get_real_model_results(posts_df)
    else:
        # Clear ghost data when insufficient posts
        st.session_state.topics = {"Not enough data": ["Need at least 10 posts"]}
        st.session_state.patterns = pd.DataFrame(columns=['pattern', 'support', 'confidence', 'lift'])
        st.session_state.model_results = pd.DataFrame(columns=['Model', 'Accuracy', 'AUC', 'Precision', 'Recall'])
    
    # Fetch market data
    market_df = fetch_market_data(start_date, end_date)
    st.session_state.market_data = market_df
    
    # Company stats
    company_stats = get_company_stats(posts_df)
    
    # ========================================================================
    # METRIC CARDS - TUTORIAL HIGHLIGHT
    # ========================================================================
    st.markdown('<div data-tutorial="metric-cards">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_posts = len(posts_df)
        st.markdown(f"""
        <div class="metric-card" style="padding: 0.75rem;">
            <p class="tech-label" style="font-size: 0.7rem;">Total Posts</p>
            <p class="tech-val" style="font-size: 1.5rem;">{total_posts:,}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        unique_companies = posts_df['company_standard'].nunique()
        st.markdown(f"""
        <div class="metric-card" style="padding: 0.75rem;">
            <p class="tech-label" style="font-size: 0.7rem;">Companies Mentioned</p>
            <p class="tech-val" style="font-size: 1.5rem;">{unique_companies}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_score = posts_df['score'].mean() if not posts_df.empty else 0
        st.markdown(f"""
        <div class="metric-card" style="padding: 0.75rem;">
            <p class="tech-label" style="font-size: 0.7rem;">Avg Post Score</p>
            <p class="tech-val" style="font-size: 1.5rem;">{avg_score:.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_comments = posts_df['num_comments'].sum() if not posts_df.empty else 0
        st.markdown(f"""
        <div class="metric-card" style="padding: 0.75rem;">
            <p class="tech-label" style="font-size: 0.7rem;">Total Comments</p>
            <p class="tech-val" style="font-size: 1.5rem;">{total_comments:,}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # MARKET METRICS ROW
    # ========================================================================
    st.markdown('<br>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not market_df.empty and 'spy' in market_df.columns:
            spy_first = market_df['spy'].iloc[0] if len(market_df) > 0 else market_df['spy'].iloc[-1]
            spy_last = market_df['spy'].iloc[-1]
            spy_change = ((spy_last - spy_first) / spy_first) * 100 if spy_first != 0 else 0
            st.markdown(f"""
            <div class="metric-card" style="padding: 0.75rem;">
                <p class="tech-label" style="font-size: 0.7rem;">S&P 500</p>
                <p class="tech-val" style="font-size: 1.5rem;">{spy_change:+.2f}%</p>
                <p class="tech-label" style="font-size:0.6rem;">{spy_last:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""<div class="metric-card" style="padding: 0.75rem;"><p class="tech-label" style="font-size: 0.7rem;">S&P 500</p><p class="tech-val" style="font-size: 1.5rem;">N/A</p></div>""", unsafe_allow_html=True)

    with col2:
        if not market_df.empty and 'vix' in market_df.columns and not market_df['vix'].isna().all():
            vix_val = market_df['vix'].iloc[-1]
            st.markdown(f"""
            <div class="metric-card" style="padding: 0.75rem;">
                <p class="tech-label" style="font-size: 0.7rem;">VIX (Fear Index)</p>
                <p class="tech-val" style="font-size: 1.5rem;">{vix_val:.1f}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""<div class="metric-card" style="padding: 0.75rem;"><p class="tech-label" style="font-size: 0.7rem;">VIX</p><p class="tech-val" style="font-size: 1.5rem;">N/A</p></div>""", unsafe_allow_html=True)

    with col3:
        if not market_df.empty and 'treasury' in market_df.columns and not market_df['treasury'].isna().all():
            treasury_val = market_df['treasury'].iloc[-1]
            st.markdown(f"""
            <div class="metric-card" style="padding: 0.75rem;">
                <p class="tech-label" style="font-size: 0.7rem;">10Y Treasury Yield</p>
                <p class="tech-val" style="font-size: 1.5rem;">{treasury_val:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""<div class="metric-card" style="padding: 0.75rem;"><p class="tech-label" style="font-size: 0.7rem;">10Y Treasury</p><p class="tech-val" style="font-size: 1.5rem;">N/A</p></div>""", unsafe_allow_html=True)
    
    # ========================================================================
    # TABS
    # ========================================================================
    tab1, tab2, tab3, tab4 = st.tabs(["Company Stats", "Market Overview", "Sentiment Trends", "Post Analysis"])
    
    with tab1:
        # ====================================================================
        # COMPANY STATS - WITH EMPTY STATE HANDLING (Improvement #2)
        # ====================================================================
        if company_stats is not None and not company_stats.empty:
            st.markdown('''
            <div class="card" data-tutorial="company-stats" style="padding: 1rem;">
                <h3 style="font-size: 1.1rem; margin-top: 0;">Company Statistics</h3>
            ''', unsafe_allow_html=True)
            
            # Display top companies chart
            top_companies = company_stats.head(10)
            if not top_companies.empty:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=top_companies['post_count'],
                    y=top_companies['company_standard'],
                    orientation='h',
                    marker_color='#3B82F6',
                    text=top_companies['post_count'],
                    textposition='outside'
                ))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#8A8F99', size=11),
                    xaxis_title="Number of Posts",
                    yaxis_title="Company",
                    height=350,
                    margin=dict(l=0, r=0, t=20, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Display stats table
            st.markdown('<h4 style="font-size: 0.9rem;">Detailed Stats</h4>', unsafe_allow_html=True)
            display_stats = company_stats.copy()
            if 'avg_compound' in display_stats.columns:
                display_stats['avg_compound'] = display_stats['avg_compound'].round(3)
            st.dataframe(display_stats, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No company statistics available for the selected filters. Try selecting a different date range or company.")
    
    with tab2:
        # ====================================================================
        # MARKET OVERVIEW - WITH EMPTY STATE HANDLING (Improvement #2)
        # ====================================================================
        col1, col2 = st.columns(2)
        
        with col1:
            if not market_df.empty and 'spy' in market_df.columns and 'date' in market_df.columns:
                st.markdown('''
                <div class="card" data-tutorial="market-charts" style="padding: 1rem;">
                    <h3 style="font-size: 1.1rem; margin-top: 0;">Market Performance</h3>
                ''', unsafe_allow_html=True)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=market_df['date'], 
                    y=market_df['spy'],
                    mode='lines', 
                    name='S&P 500',
                    line=dict(color='#3B82F6', width=2)
                ))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#8A8F99', size=11), 
                    xaxis=dict(gridcolor='#1A1D24'),
                    yaxis=dict(gridcolor='#1A1D24'), 
                    height=320,
                    title="S&P 500 Performance",
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="card" style="padding: 1rem;"><h3 style="font-size: 1.1rem;">Market Performance</h3><p>No market data available for the selected date range.</p></div>', unsafe_allow_html=True)

        with col2:
            if (not market_df.empty and 'vix' in market_df.columns and 'date' in market_df.columns 
                and not market_df['vix'].isna().all()):
                st.markdown('''
                <div class="card" style="padding: 1rem;">
                    <h3 style="font-size: 1.1rem; margin-top: 0;">VIX Volatility</h3>
                ''', unsafe_allow_html=True)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=market_df['date'], 
                    y=market_df['vix'],
                    mode='lines', 
                    name='VIX',
                    line=dict(color='#EF4444', width=2),
                    fill='tozeroy', 
                    fillcolor='rgba(239,68,68,0.1)'
                ))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#8A8F99', size=11), 
                    xaxis=dict(gridcolor='#1A1D24'),
                    yaxis=dict(gridcolor='#1A1D24'), 
                    height=320,
                    title="VIX - Market Fear Gauge",
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="card" style="padding: 1rem;"><h3 style="font-size: 1.1rem;">VIX Volatility</h3><p>No VIX data available for the selected date range.</p></div>', unsafe_allow_html=True)
    
    with tab3:
        # ====================================================================
        # SENTIMENT TRENDS - WITH EMPTY STATE HANDLING (Improvement #2)
        # ====================================================================
        if sentiment_df is not None and not sentiment_df.empty:
            st.markdown('''
            <div class="card" data-tutorial="sentiment-chart" style="padding: 1rem;">
                <h3 style="font-size: 1.1rem; margin-top: 0;">Sentiment Trends Over Time</h3>
            ''', unsafe_allow_html=True)
            
            fig = create_sentiment_trend_chart(sentiment_df)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card" style="padding: 1rem;"><h3 style="font-size: 1.1rem;">Sentiment Trends</h3><p>No sentiment data available for the selected filters.</p></div>', unsafe_allow_html=True)
        
        # Sentiment stats row
        if sentiment_df is not None and not sentiment_df.empty:
            col1, col2, col3 = st.columns(3)
            total_posts_sentiment = sentiment_df[['positive', 'neutral', 'negative']].sum().sum()
            
            with col1:
                pos_count = sentiment_df['positive'].sum()
                pos_pct = (pos_count / total_posts_sentiment * 100) if total_posts_sentiment > 0 else 0
                st.markdown(f"""
                <div class="metric-card" style="padding: 0.75rem;">
                    <p class="tech-label" style="font-size: 0.7rem;">Positive Posts</p>
                    <p class="tech-val" style="font-size: 1.5rem;">{pos_count:,}</p>
                    <p class="tech-label" style="font-size:0.6rem;">{pos_pct:.1f}% of total</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                neu_count = sentiment_df['neutral'].sum()
                neu_pct = (neu_count / total_posts_sentiment * 100) if total_posts_sentiment > 0 else 0
                st.markdown(f"""
                <div class="metric-card" style="padding: 0.75rem;">
                    <p class="tech-label" style="font-size: 0.7rem;">Neutral Posts</p>
                    <p class="tech-val" style="font-size: 1.5rem;">{neu_count:,}</p>
                    <p class="tech-label" style="font-size:0.6rem;">{neu_pct:.1f}% of total</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                neg_count = sentiment_df['negative'].sum()
                neg_pct = (neg_count / total_posts_sentiment * 100) if total_posts_sentiment > 0 else 0
                st.markdown(f"""
                <div class="metric-card" style="padding: 0.75rem;">
                    <p class="tech-label" style="font-size: 0.7rem;">Negative Posts</p>
                    <p class="tech-val" style="font-size: 1.5rem;">{neg_count:,}</p>
                    <p class="tech-label" style="font-size:0.6rem;">{neg_pct:.1f}% of total</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Add average sentiment score
            if 'avg_compound' in sentiment_df.columns:
                avg_sentiment = sentiment_df['avg_compound'].mean()
                sentiment_color = "#10B981" if avg_sentiment > 0.05 else ("#EF4444" if avg_sentiment < -0.05 else "#F59E0B")
                st.markdown(f"""
                <div class="metric-card" style="padding: 0.75rem; margin-top: 0.5rem;">
                    <p class="tech-label" style="font-size: 0.7rem;">Average Sentiment Score</p>
                    <p class="tech-val" style="font-size: 1.5rem; color: {sentiment_color};">{avg_sentiment:.3f}</p>
                    <p class="tech-label" style="font-size:0.6rem;">(Positive > 0.05, Neutral -0.05 to 0.05, Negative < -0.05)</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab4:
        # ====================================================================
        # RECENT POSTS - WITH EMPTY STATE HANDLING (Improvement #2)
        # ====================================================================
        if posts_df is not None and not posts_df.empty:
            st.markdown('''
            <div class="card" style="padding: 1rem;">
                <h3 style="font-size: 1.1rem; margin-top: 0;">Recent Posts</h3>
            ''', unsafe_allow_html=True)
            
            # Display recent posts
            display_cols = ['created', 'title', 'company_standard', 'score', 'num_comments']
            if 'sentiment' in posts_df.columns:
                display_cols.append('sentiment')
            
            recent_posts = posts_df.sort_values('created', ascending=False).head(20)
            
            # Format the dataframe for display
            display_df = recent_posts[display_cols].copy()
            if 'created' in display_df.columns:
                display_df['created'] = pd.to_datetime(display_df['created']).dt.strftime('%Y-%m-%d %H:%M')
            
            st.dataframe(display_df, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card" style="padding: 1rem;"><h3 style="font-size: 1.1rem;">Recent Posts</h3><p>No posts available for the selected filters.</p></div>', unsafe_allow_html=True)


if __name__ == "__main__":
    dashboard_page()