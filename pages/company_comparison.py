"""
Company Comparison page - Compare multiple companies side by side.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def company_comparison_page():
    st.markdown('<h1>Company Comparison</h1>', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">Compare sentiment, engagement, and discussion across companies</p>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    
    # Get data from session state
    posts_df = st.session_state.get('posts_data', pd.DataFrame())
    
    if posts_df.empty:
        st.warning("No data available. Please check your data source.")
        return
    
    # Get list of companies
    companies = sorted(posts_df['company_standard'].unique())
    
    # Check if we have any companies
    if not companies:
        st.warning("No companies found in the data.")
        return
    
    # Multi-select for companies to compare - define default_companies BEFORE using it
    default_companies = companies[:min(3, len(companies))]
    
    # Tutorial highlight for company selector
    st.markdown('<div data-tutorial="company-selector">', unsafe_allow_html=True)
    selected_companies = st.multiselect(
        "Select companies to compare",
        options=companies,
        default=default_companies,
        help="Choose up to 5 companies to compare side by side"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not selected_companies:
        st.info("Select at least one company to compare")
        return
    
    # Limit to 5 companies for readability
    if len(selected_companies) > 5:
        st.warning("For better readability, please select up to 5 companies.")
        selected_companies = selected_companies[:5]
    
    # ========================================================================
    # METRICS OVERVIEW
    # ========================================================================
    st.markdown('<h3> Key Metrics Comparison</h3>', unsafe_allow_html=True)
    
    # Calculate metrics for selected companies
    metrics_data = []
    for company in selected_companies:
        company_posts = posts_df[posts_df['company_standard'] == company]
        
        if len(company_posts) > 0:
            metrics_item = {
                'Company': company,
                'Total Posts': len(company_posts),
                'Avg Score': round(company_posts['score'].mean(), 1),
                'Total Comments': company_posts['num_comments'].sum(),
                'Avg Comments': round(company_posts['num_comments'].mean(), 1),
            }
            
            # Add sentiment percentages if available
            if 'sentiment' in company_posts.columns:
                metrics_item['Positive %'] = round((company_posts['sentiment'] == 'positive').mean() * 100, 1)
                metrics_item['Neutral %'] = round((company_posts['sentiment'] == 'neutral').mean() * 100, 1)
                metrics_item['Negative %'] = round((company_posts['sentiment'] == 'negative').mean() * 100, 1)
            
            # Add average compound score if available
            if 'compound' in company_posts.columns:
                metrics_item['Avg Sentiment'] = round(company_posts['compound'].mean(), 3)
            
            metrics_data.append(metrics_item)
    
    df_metrics = pd.DataFrame(metrics_data)
    
    if df_metrics.empty:
        st.warning("No metrics data available for selected companies")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Display metrics table
    st.dataframe(df_metrics, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # POST VOLUME CHART
    # ========================================================================
    st.markdown('''
            <div class="card" data-tutorial="company-stats" style="padding: 0.5rem;">
                <h4> Post Volume by Company</h4>
            ''', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_metrics['Company'],
        y=df_metrics['Total Posts'],
        marker_color='#3B82F6',
        text=df_metrics['Total Posts'],
        textposition='outside',
        name='Total Posts'
    ))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8A8F99'),
        xaxis_title="Company",
        yaxis_title="Number of Posts",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # ENGAGEMENT METRICS (if multiple companies)
    # ========================================================================
    if len(selected_companies) > 1:
        
        st.markdown('''
            <div class="card" data-tutorial="company-stats" style="padding: 0.5rem;">
                <h4> Engagement Metrics</h4>
            ''', unsafe_allow_html=True)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Avg Score bars
        fig.add_trace(go.Bar(
            x=df_metrics['Company'],
            y=df_metrics['Avg Score'],
            name='Avg Score',
            marker_color='#F59E0B',
            text=df_metrics['Avg Score'],
            textposition='outside'
        ), secondary_y=False)
        
        # Avg Comments line
        fig.add_trace(go.Scatter(
            x=df_metrics['Company'],
            y=df_metrics['Avg Comments'],
            name='Avg Comments',
            mode='lines+markers',
            marker=dict(color='#EF4444', size=10),
            line=dict(color='#EF4444', width=2),
            text=df_metrics['Avg Comments'],
            textposition='top center'
        ), secondary_y=True)
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99'),
            height=400,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        fig.update_yaxes(title_text="Avg Score", secondary_y=False)
        fig.update_yaxes(title_text="Avg Comments", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # SENTIMENT DISTRIBUTION
    # ========================================================================
    if 'Positive %' in df_metrics.columns:
        
        st.markdown('''
            <div class="card" data-tutorial="company-stats" style="padding: 0.5rem;">
                <h4> Sentiment Distribution Comparison</h4>
            ''', unsafe_allow_html=True)
        fig = go.Figure()
        
        for _, row in df_metrics.iterrows():
            fig.add_trace(go.Bar(
                name=row['Company'],
                x=['Positive', 'Neutral', 'Negative'],
                y=[row['Positive %'], row['Neutral %'], row['Negative %']],
                text=[f"{row['Positive %']:.1f}%", f"{row['Neutral %']:.1f}%", f"{row['Negative %']:.1f}%"],
                textposition='inside'
            ))
        
        fig.update_layout(
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99'),
            yaxis_title="Percentage (%)",
            height=400,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Average sentiment score if available
        if 'Avg Sentiment' in df_metrics.columns:
            
            st.markdown('''
            <div class="card" data-tutorial="company-stats" style="padding: 0.5rem;">
                <h4> Average Sentiment Score</h4>
            ''', unsafe_allow_html=True)
            fig = go.Figure()
            colors = ['#10B981' if x > 0.05 else '#EF4444' if x < -0.05 else '#F59E0B' for x in df_metrics['Avg Sentiment']]
            
            fig.add_trace(go.Bar(
                x=df_metrics['Company'],
                y=df_metrics['Avg Sentiment'],
                marker_color=colors,
                text=df_metrics['Avg Sentiment'],
                textposition='outside'
            ))
            fig.add_hline(y=0.05, line_dash="dash", line_color="#10B981", annotation_text="Positive Threshold")
            fig.add_hline(y=-0.05, line_dash="dash", line_color="#EF4444", annotation_text="Negative Threshold")
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8A8F99'),
                yaxis_title="Compound Sentiment Score",
                yaxis=dict(range=[-1, 1]),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
         # ========================================================================
    # TIME SERIES COMPARISON (with company-specific events)
    # ========================================================================
    if len(selected_companies) <= 5:
        st.markdown('''
            <div class="card" data-tutorial="company-stats" style="padding: 0.5rem;">
                <h4>Sentiment Over Time</h4>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown('<p class="text-muted">Daily net sentiment (positive - negative) / total posts. Hover over markers for company events.</p>', unsafe_allow_html=True)
        
        # ========================================================================
        # COMPANY-SPECIFIC EVENTS (February-March 2021)
        # ========================================================================
        company_events = {
            'Tesla': [
                {'date': '2021-02-08', 'title': 'Tesla Buys $1.5B Bitcoin', 'desc': 'Tesla announced $1.5 billion Bitcoin purchase', 'impact': 'Massive positive sentiment spike', 'color': '#10B981'},
                {'date': '2021-02-23', 'title': 'Tech Sell-off', 'desc': 'Tesla stock dropped 8% as yields rose', 'impact': 'Negative sentiment', 'color': '#EF4444'},
                {'date': '2021-03-15', 'title': 'Tesla Model Y Price Hike', 'desc': 'Tesla raised Model Y prices by $1,000', 'impact': 'Mixed sentiment', 'color': '#F59E0B'}
            ],
            'Apple': [
                {'date': '2021-02-17', 'title': 'Apple Car Rumors', 'desc': 'Reports of Apple developing electric vehicle', 'impact': 'Positive sentiment surge', 'color': '#10B981'},
                {'date': '2021-02-23', 'title': 'Tech Sell-off', 'desc': 'Apple dropped 3% amid rate concerns', 'impact': 'Negative sentiment', 'color': '#EF4444'},
                {'date': '2021-03-16', 'title': 'Apple M1 Chip Event', 'desc': 'Apple announced new M1-powered devices', 'impact': 'Positive sentiment', 'color': '#10B981'}
            ],
            'Amazon': [
                {'date': '2021-02-02', 'title': 'Bezos to Step Down as CEO', 'desc': 'Jeff Bezos announced transition to Executive Chair', 'impact': 'Mixed market reaction', 'color': '#F59E0B'},
                {'date': '2021-02-23', 'title': 'Tech Sell-off', 'desc': 'Amazon dropped 5% as yields rose', 'impact': 'Negative sentiment', 'color': '#EF4444'},
                {'date': '2021-03-02', 'title': 'Amazon AI Investment', 'desc': '$200B investment in AI fulfillment centers', 'impact': 'High volume, positive sentiment', 'color': '#10B981'}
            ],
            'Google': [
                {'date': '2021-02-01', 'title': 'Google Cloud & Ford Partnership', 'desc': 'Google Cloud announced partnership with Ford', 'impact': 'Tech sector optimism', 'color': '#10B981'},
                {'date': '2021-02-23', 'title': 'Tech Sell-off', 'desc': 'Google dropped 4% amid rate concerns', 'impact': 'Negative sentiment', 'color': '#EF4444'},
                {'date': '2021-03-23', 'title': 'Google $7B Office Investment', 'desc': 'Google announced $7B office expansion', 'impact': 'Positive sentiment', 'color': '#10B981'}
            ],
            'Microsoft': [
                {'date': '2021-02-23', 'title': 'Tech Sell-off', 'desc': 'Microsoft dropped 5% as yields rose', 'impact': 'Negative sentiment', 'color': '#EF4444'},
                {'date': '2021-03-09', 'title': 'Microsoft Teams Growth', 'desc': 'Teams hit 145M daily active users', 'impact': 'Positive sentiment', 'color': '#10B981'},
                {'date': '2021-03-26', 'title': 'Microsoft $22B Army Contract', 'desc': 'Microsoft awarded $22B AR headset contract', 'impact': 'Strong positive sentiment', 'color': '#10B981'}
            ]
        }
        
        fig = go.Figure()
        
        for company in selected_companies:
            company_posts = posts_df[posts_df['company_standard'] == company].copy()
            if not company_posts.empty and 'sentiment' in company_posts.columns:
                # Convert date to datetime if needed
                if 'date' in company_posts.columns:
                    company_posts['date'] = pd.to_datetime(company_posts['date'])
                elif 'created' in company_posts.columns:
                    company_posts['date'] = pd.to_datetime(company_posts['created']).dt.date
                
                # Group by date and calculate net sentiment
                daily = company_posts.groupby('date').agg(
                    positive=('sentiment', lambda x: (x == 'positive').sum()),
                    neutral=('sentiment', lambda x: (x == 'neutral').sum()),
                    negative=('sentiment', lambda x: (x == 'negative').sum())
                ).reset_index()
                
                daily['net_sentiment'] = (daily['positive'] - daily['negative']) / (daily['positive'] + daily['neutral'] + daily['negative'] + 1)
                daily['date'] = pd.to_datetime(daily['date'])
                daily = daily.sort_values('date')
                
                # Add main sentiment line for the company
                fig.add_trace(go.Scatter(
                    x=daily['date'],
                    y=daily['net_sentiment'],
                    mode='lines',
                    name=company,
                    line=dict(width=2),
                    hovertemplate=f'{company}<br>Date: %{{x|%Y-%m-%d}}<br>Net Sentiment: %{{y:.2f}}<extra></extra>'
                ))
                
                # Add company-specific event markers
                if company in company_events:
                    for event in company_events[company]:
                        event_date = pd.to_datetime(event['date'])
                        
                        # Find sentiment value at event date
                        event_row = daily[daily['date'].dt.strftime('%Y-%m-%d') == event['date']]
                        if not event_row.empty:
                            y_pos = event_row['net_sentiment'].iloc[0]
                        else:
                            # Find nearest date
                            nearest_idx = (daily['date'] - event_date).abs().idxmin()
                            y_pos = daily.loc[nearest_idx, 'net_sentiment']
                        
                        # Add marker
                        fig.add_trace(go.Scatter(
                            x=[event_date],
                            y=[y_pos],
                            mode='markers',
                            marker=dict(
                                size=12, 
                                color=event['color'], 
                                symbol='circle', 
                                line=dict(color='white', width=2)
                            ),
                            name=f"{company}: {event['title']}",
                            showlegend=False,
                            hovertemplate=f"""
                            <b>{company} - {event['title']}</b><br>
                             {event['date']}<br>
                             {event['desc']}<br>
                             Impact: {event['impact']}<br>
                             Sentiment: {y_pos:.2f}<br>
                            <extra></extra>
                            """
                        ))
                        
                        # Add vertical line for major events (NO annotation_text!)
                        if event['impact'] in ['Massive positive sentiment spike', 'Strong positive sentiment']:
                            fig.add_vline(
                                x=event_date,
                                line_dash="dot",
                                line_color=event['color'],
                                line_width=1,
                                opacity=0.3
                            )
        
        
        
        
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99'),
            xaxis_title="Date",
            yaxis_title="Net Sentiment",
            yaxis=dict(range=[-1, 1], tickformat='.2f'),
            height=500,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add summary of company events
        with st.expander(" Company-Specific Events (Feb-Mar 2021)"):
            for company in selected_companies:
                if company in company_events:
                    st.markdown(f"**{company}**")
                    for event in company_events[company]:
                        color_icon = "🟢" if event['color'] == '#10B981' else ("🔴" if event['color'] == '#EF4444' else "🟡")
                        st.markdown(f"&nbsp;&nbsp;{color_icon} **{event['date']}** - {event['title']}: {event['desc']}")
                    st.markdown("")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # SUMMARY STATISTICS
    # ========================================================================

    st.markdown('<h3>Summary Statistics</h3>', unsafe_allow_html=True)
    
    total_posts_all = df_metrics['Total Posts'].sum()
    total_comments_all = df_metrics['Total Comments'].sum()
    avg_score_all = df_metrics['Avg Score'].mean()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Posts (All)", f"{total_posts_all:,}")
    with col2:
        st.metric("Total Comments (All)", f"{total_comments_all:,}")
    with col3:
        st.metric("Avg Score (All)", f"{avg_score_all:.1f}")
    
    # Find top company by posts
    top_company = df_metrics.loc[df_metrics['Total Posts'].idxmax(), 'Company']
    top_posts = df_metrics['Total Posts'].max()
    st.markdown(f"""
    <div style="margin-top: 1rem; background: rgba(59,130,246,0.05); border-radius: 8px; padding: 0.75rem;">
        <p style="font-size: 0.7rem; color: #8A8F99;">
            <strong>Top Company:</strong> {top_company} with {top_posts:,} posts
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    company_comparison_page()