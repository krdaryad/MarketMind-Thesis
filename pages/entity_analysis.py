"""
Entity Analysis page - using matched_company from CSV.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math
from data_fetcher import get_companies_list, filter_by_company

def entity_analysis_page():
    st.markdown('<h1> Entity Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">Named entity recognition and entity sentiment tracking</p>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    
    # Get data from session state
    posts_df = st.session_state.get('posts_data', pd.DataFrame())
    
    if posts_df.empty:
        st.warning("No data available. Please check your data source.")
        return
    
    # Get company statistics
    company_counts = posts_df['company_standard'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Top Entities by Mention</h3>', unsafe_allow_html=True)
        
        # Create bar chart
        fig = go.Figure([go.Bar(
            x=company_counts.head(10).values, 
            y=company_counts.head(10).index, 
            orientation='h', 
            marker_color='#3B82F6',
            text=company_counts.head(10).values,
            textposition='outside'
        )])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99'),
            height=400,
            xaxis_title="Mention Count"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Entity Sentiment Over Time</h3>', unsafe_allow_html=True)
        
        # Get sentiment data if available
        if 'compound' in posts_df.columns:
            # Calculate sentiment per company over time
            sentiment_df = st.session_state.get('sentiment_data', pd.DataFrame())
            if not sentiment_df.empty:
                dates = sentiment_df['date']
                fig = go.Figure()
                
                # Show top 3 companies
                top_companies = company_counts.head(3).index.tolist()
                colors = ['#10B981', '#F59E0B', '#EF4444']
                
                for company, color in zip(top_companies, colors):
                    company_posts = posts_df[posts_df['company_standard'] == company]
                    if not company_posts.empty:
                        company_posts['date'] = pd.to_datetime(company_posts['date'])
                        daily_sentiment = company_posts.groupby('date')['compound'].mean().reset_index()
                        fig.add_trace(go.Scatter(
                            x=daily_sentiment['date'], 
                            y=daily_sentiment['compound'], 
                            mode='lines', 
                            name=company, 
                            line=dict(width=2, color=color)
                        ))
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#8A8F99'),
                    xaxis_title="Date",
                    yaxis_title="Sentiment Score (Compound)",
                    height=400,
                    yaxis=dict(range=[-1, 1])
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sentiment data available for time series")
        else:
            st.info("Run sentiment analysis first to see entity sentiment over time")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Entity relationship graph - based on co-occurrence in posts
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Entity Co-occurrence Network</h3>', unsafe_allow_html=True)
    
    # Find co-occurring companies in posts
    co_occurrence = {}
    
    for _, row in posts_df.iterrows():
        # Get companies mentioned in this post
        companies_in_post = row.get('company_standard', '')
        if companies_in_post and pd.notna(companies_in_post):
            # Split if multiple? Usually one per row
            companies = [companies_in_post]
            
            for i, c1 in enumerate(companies):
                for c2 in companies[i+1:]:
                    key = tuple(sorted([c1, c2]))
                    co_occurrence[key] = co_occurrence.get(key, 0) + 1
    
    # Get top companies and connections
    top_entities = company_counts.head(8).index.tolist()
    
    # Build edges from co-occurrence
    edges = []
    for (c1, c2), weight in co_occurrence.items():
        if c1 in top_entities and c2 in top_entities:
            edges.append((c1, c2, weight))
    
    # Sort by weight and take top 10
    edges = sorted(edges, key=lambda x: x[2], reverse=True)[:15]
    
    # Create network visualization
    fig = go.Figure()
    
    # Position nodes in a circle
    pos = {}
    for i, node in enumerate(top_entities):
        angle = 2 * math.pi * i / len(top_entities)
        pos[node] = (math.cos(angle), math.sin(angle))
    
    # Add edges
    for edge in edges:
        fig.add_trace(go.Scatter(
            x=[pos[edge[0]][0], pos[edge[1]][0]],
            y=[pos[edge[0]][1], pos[edge[1]][1]],
            mode='lines',
            line=dict(color='#2A2E38', width=1 + min(edge[2] / 10, 5)),
            showlegend=False,
            hoverinfo='text',
            text=f"{edge[0]} ↔ {edge[1]}<br>Co-occurrences: {edge[2]}"
        ))
    
    # Add nodes
    node_sizes = [company_counts[node] / 10 + 20 for node in top_entities]
    fig.add_trace(go.Scatter(
        x=[pos[node][0] for node in top_entities],
        y=[pos[node][1] for node in top_entities],
        mode='markers+text',
        marker=dict(size=node_sizes, color='#3B82F6', line=dict(color='white', width=2)),
        text=top_entities,
        textposition="middle center",
        textfont=dict(color='white', size=10),
        showlegend=False,
        hoverinfo='text',
        texttemplate='%{text}',
        hovertemplate='<b>%{text}</b><br>Posts: %{marker.size:.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display co-occurrence table
    if edges:
        st.markdown('<h4>Top Co-occurring Entity Pairs</h4>', unsafe_allow_html=True)
        cooc_df = pd.DataFrame(edges, columns=['Entity 1', 'Entity 2', 'Co-occurrences'])
        st.dataframe(cooc_df, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Company details section
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Company Details</h3>', unsafe_allow_html=True)
    
    selected_entity = st.selectbox("Select Company to Analyze", top_entities)
    
    if selected_entity:
        entity_posts = filter_by_company(posts_df, selected_entity)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Posts", len(entity_posts))
        with col2:
            if 'score' in entity_posts.columns:
                st.metric("Avg Score", f"{entity_posts['score'].mean():.0f}")
        with col3:
            if 'num_comments' in entity_posts.columns:
                st.metric("Total Comments", entity_posts['num_comments'].sum())
        
        st.markdown('<h4>Recent Posts</h4>', unsafe_allow_html=True)
        recent_posts = entity_posts.sort_values('created', ascending=False).head(10)
        display_cols = ['created', 'title', 'score', 'num_comments']
        if 'sentiment' in recent_posts.columns:
            display_cols.append('sentiment')
        
        st.dataframe(recent_posts[display_cols], use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)