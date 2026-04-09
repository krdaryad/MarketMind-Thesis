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
        st.markdown('''
            <div class="card" data-tutorial="company-stats" style="padding: 0.5rem;">
                <h4> Top Entities by Mention</h4>
            ''', unsafe_allow_html=True)
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

        st.markdown('''
            <div class="card" data-tutorial="company-stats" style="padding: 0.5rem;">
                <h4> Entity Sentiment Over Time</h4>
            ''', unsafe_allow_html=True)
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
    
    # ========================================================================
# ENTITY CO-OCCURRENCE NETWORK - FIXED VERSION
# ========================================================================
    st.markdown('''
    <div class="card" data-tutorial="company-stats" style="padding: 0.5rem;">
        <h4>Entity Co-occurrence Network</h4>
        <p class="text-muted">Shows which companies are discussed together in the same posts</p>
    ''', unsafe_allow_html=True)

    # Get company statistics
    company_counts = posts_df['company_standard'].value_counts()
    top_entities = company_counts.head(8).index.tolist()

    # ========================================================================
    # FIX 1: PROPER CO-OCCURRENCE DETECTION
    # ========================================================================
    co_occurrence = {}

    for _, row in posts_df.iterrows():
        companies_in_post = row.get('company_standard', '')
        
        if companies_in_post and pd.notna(companies_in_post):
            # Convert to string and split by comma (if multiple companies)
            companies_str = str(companies_in_post)
            
            # Split by comma, strip whitespace, remove empty strings
            companies = [c.strip() for c in companies_str.split(',') if c.strip()]
            
            # Only process if we have at least 2 companies in this post
            if len(companies) >= 2:
                for i, c1 in enumerate(companies):
                    for c2 in companies[i+1:]:
                        key = tuple(sorted([c1, c2]))
                        co_occurrence[key] = co_occurrence.get(key, 0) + 1

    # Debug: Check if we found any co-occurrences
    if not co_occurrence:
        st.info("ℹ No co-occurring company pairs found. Posts may only mention one company each.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # ========================================================================
        # FIX 2: BUILD EDGES FROM CO-OCCURRENCE
        # ========================================================================
        edges = []
        for (c1, c2), weight in co_occurrence.items():
            if c1 in top_entities and c2 in top_entities:
                edges.append((c1, c2, weight))
        
        # Sort by weight (highest first) - don't limit too aggressively
        edges = sorted(edges, key=lambda x: x[2], reverse=True)
        
        # Show top 15 edges, or all if fewer
        display_edges = edges[:15] if len(edges) > 15 else edges
        
        # ========================================================================
        # FIX 3: VISIBLE LINE COLOR (not dark on dark background)
        # ========================================================================
        fig = go.Figure()
        
        # Position nodes in a circle
        pos = {}
        for i, node in enumerate(top_entities):
            angle = 2 * math.pi * i / len(top_entities)
            pos[node] = (math.cos(angle), math.sin(angle))
        
        # Add edges with visible colors
        for edge in display_edges:
            # Calculate line width based on weight (thicker = more co-occurrences)
            line_width = 1 + min(edge[2] / 5, 6)
            
            fig.add_trace(go.Scatter(
                x=[pos[edge[0]][0], pos[edge[1]][0]],
                y=[pos[edge[0]][1], pos[edge[1]][1]],
                mode='lines',
                line=dict(color='#F59E0B', width=line_width),  # BRIGHT ORANGE - visible!
                opacity=0.7,
                showlegend=False,
                hoverinfo='text',
                text=f"{edge[0]} ↔ {edge[1]}<br>Co-occurrences: {edge[2]}"
            ))
        
        # Add nodes
        node_sizes = [max(20, company_counts[node] / 10 + 20) for node in top_entities]
        
        fig.add_trace(go.Scatter(
            x=[pos[node][0] for node in top_entities],
            y=[pos[node][1] for node in top_entities],
            mode='markers+text',
            marker=dict(
                size=node_sizes,
                color='#3B82F6',
                line=dict(color='#FFFFFF', width=2),
                opacity=0.9
            ),
            text=top_entities,
            textposition="middle center",
            textfont=dict(color='white', size=11, weight='bold'),
            showlegend=False,
            hoverinfo='text',
            hovertext=[f"{node}<br>Posts: {company_counts[node]}" for node in top_entities]
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            height=500,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ========================================================================
        # CO-OCCURRENCE TABLE
        # ========================================================================
        if display_edges:
            st.markdown('<h4>Top Co-occurring Entity Pairs</h4>', unsafe_allow_html=True)
            cooc_df = pd.DataFrame(display_edges, columns=['Entity 1', 'Entity 2', 'Co-occurrences'])
            st.dataframe(cooc_df, use_container_width=True)
            
            # Add insight about co-occurrence
            if len(display_edges) > 0:
                top_pair = display_edges[0]
                st.markdown(f"""
                <div style="margin-top: 0.5rem; background: rgba(59,130,246,0.05); border-radius: 8px; padding: 0.5rem;">
                    <p style="font-size: 0.7rem; color: #8A8F99; margin: 0;">
                        <strong>Insight:</strong> "{top_pair[0]}" and "{top_pair[1]}" are most frequently discussed together 
                        ({top_pair[2]} co-occurrences). This suggests a strong thematic or competitive relationship.
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
# ========================================================================
# ENTITY ANALYSIS - SHARE OF CONVERSATION (Replaces Broken Network Graph)
# ========================================================================
    st.markdown('''
    <div class="card" data-tutorial="company-stats" style="padding: 1rem;">
        <h4>Share of Conversation</h4>
        <p class="text-muted">Distribution of mentions across companies (single-company per post structure)</p>
    ''', unsafe_allow_html=True)

    # Get company statistics
    company_counts = posts_df['company_standard'].value_counts()
    top_entities = company_counts.head(8).index.tolist()

    # ========================================================================
    # OPTION A: DONUT CHART (Best for showing conversation share)
    # ========================================================================
    import plotly.express as px

    # Prepare data for donut chart
    donut_data = pd.DataFrame({
        'Company': company_counts.index,
        'Mentions': company_counts.values
    })

    # Create donut chart
    fig_donut = px.pie(
        donut_data, 
        values='Mentions', 
        names='Company', 
        hole=0.4,
        title='Share of Conversation by Company',
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig_donut.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8A8F99', size=12),
        height=450,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    fig_donut.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Mentions: %{value}<br>Share: %{percent}<extra></extra>'
    )

    st.plotly_chart(fig_donut, use_container_width=True)

    # Add insight about the dominant company
    top_company = company_counts.index[0]
    top_count = company_counts.values[0]
    total_mentions = company_counts.sum()
    top_percent = (top_count / total_mentions) * 100

    st.markdown(f"""
    <div style="margin-top: 0.5rem; background: rgba(59,130,246,0.05); border-radius: 8px; padding: 0.5rem;">
        <p style="font-size: 0.7rem; color: #8A8F99; margin: 0;">
            <strong>Insight:</strong> "{top_company}" dominates the conversation with {top_count} mentions 
            ({top_percent:.1f}% of all company discussions). This suggests significant retail investor interest in this stock.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ========================================================================
    # OPTION B: TOP COMPANIES BAR CHART (Alternative view)
    # ========================================================================
    st.markdown('''
    <div class="card" style="padding: 1rem;">
        <h4>Top Companies by Mention Volume</h4>
        <p class="text-muted">Which companies generate the most discussion?</p>
    ''', unsafe_allow_html=True)

    # Create bar chart for top 10 companies
    top_10_companies = company_counts.head(10)

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=top_10_companies.values,
        y=top_10_companies.index,
        orientation='h',
        marker=dict(
            color=top_10_companies.values,
            colorscale='Blues',
            showscale=False,
            line=dict(color='white', width=1)
        ),
        text=top_10_companies.values,
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Mentions: %{x}<extra></extra>'
    ))

    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8A8F99'),
        xaxis_title="Number of Mentions",
        yaxis_title="Company",
        height=400,
        margin=dict(l=0, r=0, t=20, b=20)
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ========================================================================
    # COMPANY DETAILS SECTION (Keep as is)
    # ========================================================================
    st.markdown('''
    <div class="card" style="padding: 1rem;">
        <h4>Company Details</h4>
    ''', unsafe_allow_html=True)

    if top_entities:
        selected_entity = st.selectbox("Select Company to Analyze", top_entities)
        
        if selected_entity:
            entity_posts = posts_df[posts_df['company_standard'] == selected_entity]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Posts", len(entity_posts))
            with col2:
                if 'score' in entity_posts.columns:
                    st.metric("Avg Score", f"{entity_posts['score'].mean():.0f}")
            with col3:
                if 'num_comments' in entity_posts.columns:
                    st.metric("Total Comments", entity_posts['num_comments'].sum())
            
            # Sentiment distribution for this company
            if 'sentiment' in entity_posts.columns:
                st.markdown('<h4>Sentiment Distribution</h4>', unsafe_allow_html=True)
                sent_counts = entity_posts['sentiment'].value_counts()
                
                # Sentiment pie chart for selected company
                sent_fig = go.Figure(data=[go.Pie(
                    labels=['Positive', 'Neutral', 'Negative'],
                    values=[
                        sent_counts.get('positive', 0),
                        sent_counts.get('neutral', 0),
                        sent_counts.get('negative', 0)
                    ],
                    marker_colors=['#10B981', '#8A8F99', '#EF4444'],
                    hole=0.3
                )])
                sent_fig.update_layout(
                    height=300,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#8A8F99')
                )
                st.plotly_chart(sent_fig, use_container_width=True)
            
            st.markdown('<h4>Recent Posts</h4>', unsafe_allow_html=True)
            recent_posts = entity_posts.sort_values('created', ascending=False).head(10)
            display_cols = ['created', 'title', 'score', 'num_comments']
            if 'sentiment' in recent_posts.columns:
                display_cols.append('sentiment')
            
            # Format datetime for better display
            if 'created' in recent_posts.columns:
                recent_posts['created'] = pd.to_datetime(recent_posts['created']).dt.strftime('%Y-%m-%d %H:%M')
            
            st.dataframe(recent_posts[display_cols], use_container_width=True)
    else:
        st.info("No company data available to display.")

    st.markdown('</div>', unsafe_allow_html=True)