"""
Correlation Analysis page - Analyze sentiment-market correlations with economic indicators.
"""
import streamlit as st
import pandas as pd
import numpy as np  # ADDED - was missing
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_loader import merge_sentiment_with_economics
from data_fetcher import fetch_market_data

def correlation_analysis_page():
    st.markdown('<h1>Sentiment-Market Correlation</h1>', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">Analyze relationships between Reddit sentiment, market movements, and economic indicators</p>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    
    # Get data from session state
    sentiment_df = st.session_state.get('sentiment_data', pd.DataFrame())
    posts_df = st.session_state.get('posts_data', pd.DataFrame())
    
    if sentiment_df.empty:
        st.warning("No sentiment data available. Please check your data source.")
        return
    
    # Get date range from session state
    if 'date_range' in st.session_state:
        start_date, end_date = st.session_state.date_range
    else:
        start_date, end_date = pd.Timestamp('2021-02-01'), pd.Timestamp('2021-02-28')
    
    # Fetch market data for the date range
    with st.spinner("Loading market data..."):
        market_df = fetch_market_data(start_date, end_date)
    
    if market_df.empty:
        st.warning("No market data available for the selected date range.")
        return
    
    # ========================================================================
    # MERGE SENTIMENT WITH MARKET DATA
    # ========================================================================
    # Prepare sentiment data
    sentiment_agg = sentiment_df.copy()
    sentiment_agg['date'] = pd.to_datetime(sentiment_agg['date'])
    
    # Merge with market data
    market_df['date'] = pd.to_datetime(market_df['date'])
    merged_data = pd.merge(sentiment_agg, market_df, on='date', how='inner')
    
    if merged_data.empty:
        st.warning("No overlapping dates between sentiment and market data.")
        return
    
    st.success(f"Found {len(merged_data)} overlapping days for analysis")
    
    # ========================================================================
    # COMPANY SELECTION
    # ========================================================================
    companies = merged_data['company_standard'].unique() if 'company_standard' in merged_data.columns else []
    if len(companies) > 0:
        selected_company = st.selectbox("Select Company", ["All"] + list(companies))
        if selected_company != "All":
            merged_data = merged_data[merged_data['company_standard'] == selected_company]
            st.info(f"Showing data for {selected_company}")
    
    # ========================================================================
    # CURRENT MARKET INDICATORS
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Current Market Indicators</h3>', unsafe_allow_html=True)
    
    # Get latest values
    latest = merged_data.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'spy' in latest and not pd.isna(latest['spy']):
            # Calculate SPY change
            spy_first = merged_data['spy'].iloc[0] if len(merged_data) > 0 else latest['spy']
            spy_change = ((latest['spy'] - spy_first) / spy_first) * 100 if spy_first != 0 else 0
            spy_color = "#10B981" if spy_change >= 0 else "#EF4444"
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem;">
                <p style="color: #8A8F99; font-size: 0.7rem;">S&P 500</p>
                <p style="color: #FFFFFF; font-size: 1.5rem; font-weight: bold;">{latest['spy']:.2f}</p>
                <p style="color: {spy_color}; font-size: 0.7rem;">{spy_change:+.2f}% (period)</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 0.5rem;">
                <p style="color: #8A8F99; font-size: 0.7rem;">S&P 500</p>
                <p style="color: #8A8F99; font-size: 1.5rem;">N/A</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if 'vix' in latest and not pd.isna(latest['vix']):
            vix_color = "#EF4444" if latest['vix'] > 25 else ("#F59E0B" if latest['vix'] > 15 else "#10B981")
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem;">
                <p style="color: #8A8F99; font-size: 0.7rem;">VIX (Fear Index)</p>
                <p style="color: {vix_color}; font-size: 1.5rem; font-weight: bold;">{latest['vix']:.1f}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 0.5rem;">
                <p style="color: #8A8F99; font-size: 0.7rem;">VIX</p>
                <p style="color: #8A8F99; font-size: 1.5rem;">N/A</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if 'treasury' in latest and not pd.isna(latest['treasury']):
            treasury_color = "#F59E0B" if latest['treasury'] > 1.5 else "#10B981"
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem;">
                <p style="color: #8A8F99; font-size: 0.7rem;">10Y Treasury</p>
                <p style="color: {treasury_color}; font-size: 1.5rem; font-weight: bold;">{latest['treasury']:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 0.5rem;">
                <p style="color: #8A8F99; font-size: 0.7rem;">10Y Treasury</p>
                <p style="color: #8A8F99; font-size: 1.5rem;">N/A</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if 'avg_compound' in latest and not pd.isna(latest['avg_compound']):
            sentiment_color = "#10B981" if latest['avg_compound'] > 0.05 else ("#EF4444" if latest['avg_compound'] < -0.05 else "#F59E0B")
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem;">
                <p style="color: #8A8F99; font-size: 0.7rem;">Avg Sentiment</p>
                <p style="color: {sentiment_color}; font-size: 1.5rem; font-weight: bold;">{latest['avg_compound']:.3f}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 0.5rem;">
                <p style="color: #8A8F99; font-size: 0.7rem;">Avg Sentiment</p>
                <p style="color: #8A8F99; font-size: 1.5rem;">N/A</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # CORRELATION MATRIX
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Correlation Matrix</h3>', unsafe_allow_html=True)
    
    # Select columns for correlation
    corr_cols = ['positive', 'neutral', 'negative', 'avg_compound', 'compound', 
                 'spy', 'vix', 'treasury']
    available_cols = [c for c in corr_cols if c in merged_data.columns and not merged_data[c].isna().all()]
    
    if len(available_cols) >= 2:
        corr_matrix = merged_data[available_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        fig.update_layout(
            title="Correlations: Sentiment vs Market Indicators",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99'),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Interpretation
        st.markdown("""
        <div style="margin-top: 1rem; background: rgba(59,130,246,0.05); border: 1px solid rgba(59,130,246,0.1); border-radius: 12px; padding: 0.75rem;">
            <p style="font-size: 0.75rem; color: #8A8F99; margin: 0;">
                <strong>Interpretation:</strong><br>
                • Red/positive: Variables move together<br>
                • Blue/negative: Variables move opposite<br>
                • Values near 0 indicate no linear relationship
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Not enough numeric columns for correlation analysis")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # SENTIMENT VS MARKET TIME SERIES
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Sentiment vs Market Indicators Over Time</h3>', unsafe_allow_html=True)
    
    # Select market indicator to display
    market_indicators = ['spy', 'vix', 'treasury']
    available_indicators = [m for m in market_indicators if m in merged_data.columns]
    
    if available_indicators:
        selected_indicator = st.selectbox("Select Market Indicator", available_indicators)
        
        indicator_labels = {
            'spy': 'S&P 500 Price',
            'vix': 'VIX Volatility Index',
            'treasury': '10Y Treasury Yield (%)'
        }
        
        # Create dual-axis chart
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Sentiment (avg compound)
        fig.add_trace(go.Scatter(
            x=merged_data['date'],
            y=merged_data['avg_compound'],
            mode='lines',
            name='Avg Sentiment Score',
            line=dict(color='#F59E0B', width=2)
        ), secondary_y=False)
        
        # Market indicator
        fig.add_trace(go.Scatter(
            x=merged_data['date'],
            y=merged_data[selected_indicator],
            mode='lines',
            name=indicator_labels[selected_indicator],
            line=dict(color='#3B82F6', width=2)
        ), secondary_y=True)
        
        fig.update_layout(
            title=f"Sentiment vs {indicator_labels[selected_indicator]}",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99'),
            height=450,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        fig.update_yaxes(title_text="Sentiment Score", secondary_y=False)
        fig.update_yaxes(title_text=indicator_labels[selected_indicator], secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ========================================================================
        # TIME-LAGGED CORRELATION
        # ========================================================================
        st.markdown('<h3>Time-Lagged Correlation</h3>', unsafe_allow_html=True)
        st.markdown('<p class="text-muted">Does sentiment predict market movements?</p>', unsafe_allow_html=True)
        
        max_lag = 10
        lags = range(max_lag + 1)
        
        correlations = []
        for lag in lags:
            if len(merged_data) > lag:
                if lag == 0:
                    corr = merged_data['avg_compound'].corr(merged_data[selected_indicator])
                else:
                    corr = merged_data['avg_compound'].iloc[:-lag].corr(merged_data[selected_indicator].iloc[lag:])
                correlations.append(corr if not pd.isna(corr) else 0)
            else:
                correlations.append(0)
        
        fig_lag = go.Figure()
        fig_lag.add_trace(go.Scatter(
            x=list(lags),
            y=correlations,
            mode='lines+markers',
            line=dict(color='#3B82F6', width=2),
            marker=dict(size=8, color='#F59E0B')
        ))
        fig_lag.add_hline(y=0, line_dash="dash", line_color="gray")
        
        fig_lag.update_layout(
            title=f"Sentiment vs {indicator_labels.get(selected_indicator, selected_indicator)} (Lag Analysis)",
            xaxis_title="Days Lag (sentiment leads market)",
            yaxis_title="Correlation Coefficient",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99'),
            height=400
        )
        st.plotly_chart(fig_lag, use_container_width=True)
        
        # Find best lag
        if correlations:
            best_lag = correlations.index(max(correlations))
            st.markdown(f"""
            <div style="margin-top: 1rem; background: rgba(59,130,246,0.05); border: 1px solid rgba(59,130,246,0.1); border-radius: 12px; padding: 0.75rem;">
                <p style="font-size: 0.75rem; color: #8A8F99; margin: 0;">
                    <strong>Key Finding:</strong><br>
                    • Strongest correlation between sentiment and {indicator_labels.get(selected_indicator, selected_indicator)} occurs at lag <strong>{best_lag}</strong> day(s)<br>
                    • {'Sentiment appears to be a leading indicator for market movements' if max(correlations) > 0.1 else 'Sentiment does not strongly predict this market indicator'}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No market indicators available for time series analysis")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # SENTIMENT BREAKDOWN OVER TIME
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Sentiment Breakdown Over Time</h3>', unsafe_allow_html=True)
    
    if 'positive' in merged_data.columns and 'negative' in merged_data.columns:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=merged_data['date'],
            y=merged_data['positive'],
            mode='lines',
            name='Positive Posts',
            line=dict(color='#10B981', width=2),
            fill='tozeroy',
            fillcolor='rgba(16,185,129,0.2)'
        ))
        
        fig.add_trace(go.Scatter(
            x=merged_data['date'],
            y=merged_data['negative'],
            mode='lines',
            name='Negative Posts',
            line=dict(color='#EF4444', width=2),
            fill='tozeroy',
            fillcolor='rgba(239,68,68,0.2)'
        ))
        
        if 'neutral' in merged_data.columns:
            fig.add_trace(go.Scatter(
                x=merged_data['date'],
                y=merged_data['neutral'],
                mode='lines',
                name='Neutral Posts',
                line=dict(color='#8A8F99', width=2),
                fill='tozeroy',
                fillcolor='rgba(138,143,153,0.2)'
            ))
        
        fig.update_layout(
            title="Daily Sentiment Volume",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8A8F99'),
            height=400,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        fig.update_yaxes(title_text="Number of Posts")
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sentiment breakdown data not available")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # SENTIMENT-RETURN ALIGNMENT
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Sentiment-Return Alignment</h3>', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">Comparing sentiment direction with actual market returns</p>', unsafe_allow_html=True)

    if not sentiment_df.empty and not market_df.empty:
        # Prepare alignment data
        sentiment_aligned = sentiment_df.copy()
        sentiment_aligned['date'] = pd.to_datetime(sentiment_aligned['date'])
        market_aligned = market_df.copy()
        market_aligned['date'] = pd.to_datetime(market_aligned['date'])
        
        aligned = pd.merge(sentiment_aligned, market_aligned[['date', 'spy']], on='date', how='inner')
        
        if len(aligned) > 0:
            # Calculate daily returns
            aligned['returns'] = aligned['spy'].pct_change().fillna(0)
            
            # Determine sentiment direction (positive vs negative)
            aligned['sentiment_direction'] = aligned['avg_compound'].apply(
                lambda x: 'Bullish' if x > 0.05 else ('Bearish' if x < -0.05 else 'Neutral')
            )
            
            # Determine market direction
            aligned['market_direction'] = aligned['returns'].apply(
                lambda x: 'Up' if x > 0 else ('Down' if x < 0 else 'Flat')
            )
            
            # Calculate alignment
            aligned['aligned'] = ((aligned['sentiment_direction'] == 'Bullish') & (aligned['market_direction'] == 'Up')) | \
                                 ((aligned['sentiment_direction'] == 'Bearish') & (aligned['market_direction'] == 'Down')) | \
                                 ((aligned['sentiment_direction'] == 'Neutral') & (aligned['market_direction'] == 'Flat'))
            
            alignment_rate = aligned['aligned'].mean() * 100
            
            # Create confusion matrix style visualization
            confusion = pd.crosstab(aligned['sentiment_direction'], aligned['market_direction'])
            
            fig = go.Figure(data=go.Heatmap(
                z=confusion.values,
                x=confusion.columns,
                y=confusion.index,
                colorscale='Viridis',
                text=confusion.values,
                texttemplate='%{text}',
                textfont={"size": 14}
            ))
            
            fig.update_layout(
                title=f"Sentiment vs Market Direction (Alignment Rate: {alignment_rate:.1f}%)",
                xaxis_title="Actual Market Movement",
                yaxis_title="Sentiment Prediction",
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8A8F99')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Monthly alignment trend
            aligned['month'] = aligned['date'].dt.to_period('M')
            monthly_alignment = aligned.groupby('month')['aligned'].mean() * 100
            
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=monthly_alignment.index.astype(str),
                y=monthly_alignment.values,
                marker_color=['#10B981' if v > 50 else '#EF4444' for v in monthly_alignment.values],
                text=[f"{v:.1f}%" for v in monthly_alignment.values],
                textposition='outside'
            ))
            fig2.add_hline(y=50, line_dash="dash", line_color="#F59E0B", annotation_text="Random (50%)")
            
            fig2.update_layout(
                title="Monthly Sentiment-Market Alignment",
                xaxis_title="Month",
                yaxis_title="Alignment Rate (%)",
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8A8F99')
            )
            
            st.plotly_chart(fig2, use_container_width=True)
            
            # Summary
            st.markdown(f"""
            <div style="margin-top: 1rem; background: rgba(59,130,246,0.05); border-radius: 8px; padding: 0.75rem;">
                <p style="font-size: 0.75rem; margin: 0;">
                    <strong>Alignment Analysis:</strong> Sentiment correctly predicted market direction 
                    <strong>{alignment_rate:.1f}%</strong> of the time. 
                    {'This is significantly better than random (50%), validating the predictive power of sentiment.' 
                     if alignment_rate > 55 else 'This is near random, suggesting limited predictive power in this period.'}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Not enough overlapping data for alignment analysis")
    else:
        st.info("Need both sentiment and market data for alignment analysis")

    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # ECONOMIC INDICATOR MATRIX
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Economic Indicator Matrix</h3>', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">Multi-indicator correlation matrix for economic analysis</p>', unsafe_allow_html=True)

    # Get economic data
    econ_df = st.session_state.get('econ_df', pd.DataFrame())

    if not econ_df.empty:
        # Select numeric columns for correlation
        econ_cols = ['gdp', 'inflation', 'interest_rate', 'unemployment', 'consumer_sentiment', 
                     'financial_stress', 'vix', 'close']
        available_econ_cols = [c for c in econ_cols if c in econ_df.columns]
        
        if len(available_econ_cols) >= 2:
            corr_matrix = econ_df[available_econ_cols].corr()
            
            # Rename for better display
            display_names = {
                'gdp': 'GDP Growth',
                'inflation': 'Inflation',
                'interest_rate': 'Fed Rate',
                'unemployment': 'Unemployment',
                'consumer_sentiment': 'Consumer Sentiment',
                'financial_stress': 'Financial Stress',
                'vix': 'VIX',
                'close': 'Stock Price'
            }
            
            # Only rename columns that exist
            rename_dict = {k: v for k, v in display_names.items() if k in corr_matrix.columns}
            corr_matrix = corr_matrix.rename(index=rename_dict, columns=rename_dict)
            
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.index,
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_matrix.values, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title="Economic Indicator Correlation Matrix",
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8A8F99')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Key findings
            st.markdown("""
            <div style="margin-top: 1rem; background: rgba(59,130,246,0.05); border-radius: 8px; padding: 0.75rem;">
                <p style="font-size: 0.75rem; margin: 0;">
                    <strong>Key Economic Relationships:</strong><br>
                    • Red = Positive correlation (move together)<br>
                    • Blue = Negative correlation (move opposite)<br>
                    • Values near 0 indicate no linear relationship
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Not enough economic indicators for matrix")
    else:
        st.info("Economic data not available. Run Economic Dashboard first.")

    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # SUMMARY STATISTICS
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Summary Statistics</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Sentiment Metrics**")
        if 'avg_compound' in merged_data.columns:
            st.metric("Avg Sentiment Score", f"{merged_data['avg_compound'].mean():.3f}")
            st.metric("Max Sentiment", f"{merged_data['avg_compound'].max():.3f}")
            st.metric("Min Sentiment", f"{merged_data['avg_compound'].min():.3f}")
            st.metric("Sentiment Volatility", f"{merged_data['avg_compound'].std():.3f}")
    
    with col2:
        st.markdown("**Market Metrics**")
        if 'spy' in merged_data.columns:
            spy_return = ((merged_data['spy'].iloc[-1] - merged_data['spy'].iloc[0]) / merged_data['spy'].iloc[0]) * 100
            st.metric("S&P 500 Return", f"{spy_return:+.2f}%")
        if 'vix' in merged_data.columns:
            st.metric("Avg VIX", f"{merged_data['vix'].mean():.1f}")
        if 'treasury' in merged_data.columns:
            st.metric("Avg 10Y Yield", f"{merged_data['treasury'].mean():.2f}%")
    
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    correlation_analysis_page()