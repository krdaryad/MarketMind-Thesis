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
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Key Metrics Comparison</h3>', unsafe_allow_html=True)
    
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
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Post Volume by Company</h3>', unsafe_allow_html=True)
    
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
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Engagement Metrics</h3>', unsafe_allow_html=True)
        
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
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Sentiment Distribution Comparison</h3>', unsafe_allow_html=True)
        
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
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h3>Average Sentiment Score</h3>', unsafe_allow_html=True)
            
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
    # TIME SERIES COMPARISON (if data available)
    # ========================================================================
    if len(selected_companies) <= 5:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Sentiment Over Time</h3>', unsafe_allow_html=True)
        st.markdown('<p class="text-muted">Daily net sentiment (positive - negative) / total posts</p>', unsafe_allow_html=True)
        
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
                
                fig.add_trace(go.Scatter(
                    x=daily['date'],
                    y=daily['net_sentiment'],
                    mode='lines+markers',
                    name=company,
                    line=dict(width=2),
                    marker=dict(size=4),
                    hovertemplate=f'{company}<br>Date: %{{x|%Y-%m-%d}}<br>Net Sentiment: %{{y:.2f}}<extra></extra>'
                ))
        
        if fig.data:
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8A8F99'),
                xaxis_title="Date",
                yaxis_title="Net Sentiment",
                yaxis=dict(range=[-1, 1], tickformat='.2f'),
                height=450,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough time series data for sentiment comparison")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # CO-OCCURRENCE ANALYSIS
    # ========================================================================
    if len(selected_companies) > 1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Co-occurrence Analysis</h3>', unsafe_allow_html=True)
        st.markdown('<p class="text-muted">How often are these companies mentioned together in the same post?</p>', unsafe_allow_html=True)
        
        # Calculate co-occurrence matrix
        co_occurrence = {}
        total_posts_with_companies = 0
        
        for _, row in posts_df.iterrows():
            companies_in_post = row.get('company_standard', '')
            if companies_in_post and pd.notna(companies_in_post):
                # Handle multiple companies (if any are comma-separated)
                if isinstance(companies_in_post, str):
                    companies_list = [c.strip() for c in companies_in_post.split(',') if c.strip() in selected_companies]
                else:
                    companies_list = [companies_in_post] if companies_in_post in selected_companies else []
                
                if len(companies_list) >= 2:
                    total_posts_with_companies += 1
                    for i, c1 in enumerate(companies_list):
                        for c2 in companies_list[i+1:]:
                            key = tuple(sorted([c1, c2]))
                            co_occurrence[key] = co_occurrence.get(key, 0) + 1
        
        # Create co-occurrence matrix
        if co_occurrence:
            cooc_matrix = pd.DataFrame(0, index=selected_companies, columns=selected_companies)
            for (c1, c2), count in co_occurrence.items():
                cooc_matrix.loc[c1, c2] = count
                cooc_matrix.loc[c2, c1] = count
            
            # Display heatmap
            fig = go.Figure(data=go.Heatmap(
                z=cooc_matrix.values,
                x=cooc_matrix.columns,
                y=cooc_matrix.index,
                colorscale='Viridis',
                text=cooc_matrix.values,
                texttemplate='%{text}',
                textfont={"size": 10},
                hoverongaps=False
            ))
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8A8F99'),
                height=450,
                title="Number of posts mentioning both companies"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if total_posts_with_companies > 0:
                st.markdown(f"""
                <div style="margin-top: 1rem; background: rgba(59,130,246,0.05); border-radius: 8px; padding: 0.75rem;">
                    <p style="font-size: 0.7rem; color: #8A8F99;">
                        <strong>Analysis:</strong> Found {len(co_occurrence)} co-occurrence pairs across {total_posts_with_companies} posts.
                        Darker cells indicate stronger relationships between companies.
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"No co-occurrences found for selected companies. Try selecting companies that appear together in posts.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # SUMMARY STATISTICS
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
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