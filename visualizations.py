"""
Plotly and matplotlib visualization functions.
"""
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit as st

def create_anomaly_timeline(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['anomaly_score'],
        mode='lines',
        name='Anomaly Score',
        line=dict(color='#EF4444', width=2),
        fill='tozeroy',
        fillcolor='rgba(239,68,68,0.2)',
        hovertemplate='Date: %{x}<br>Score: %{y:.3f}<extra></extra>'
    ))
    anomaly_df = df[df['is_anomaly']]
    for _, row in anomaly_df.iterrows():
        size = 8 if row['anomaly_score'] < 0.8 else 10 if row['anomaly_score'] < 0.9 else 12
        fig.add_trace(go.Scatter(
            x=[row['date']],
            y=[row['anomaly_score']],
            mode='markers',
            name='Anomaly',
            marker=dict(size=size, color='#F59E0B', symbol='circle', line=dict(color='white', width=2)),
            showlegend=False
        ))
    fig.add_hline(y=0.5, line_dash="dash", line_color="#F59E0B",
                 annotation_text="Threshold: 0.5", annotation_position="top right")
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8A8F99'),
        xaxis=dict(gridcolor='#1A1D24', tickangle=45),
        yaxis=dict(gridcolor='#1A1D24', range=[0, 1], title="Anomaly Score"),
        height=350,
        margin=dict(t=40, l=40, r=20, b=40)
    )
    return fig

def create_sentiment_trend_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['positive'], mode='lines+markers',
        name='Positive', line=dict(color='#10B981', width=2),
        marker=dict(size=6, color='#10B981')
    ))
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['neutral'], mode='lines+markers',
        name='Neutral', line=dict(color='#8A8F99', width=2),
        marker=dict(size=6, color='#8A8F99')
    ))
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['negative'], mode='lines+markers',
        name='Negative', line=dict(color='#EF4444', width=2),
        marker=dict(size=6, color='#EF4444')
    ))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8A8F99'),
        xaxis=dict(gridcolor='#1A1D24', title="Date"),
        yaxis=dict(gridcolor='#1A1D24', title="Sentiment Volume"),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=400
    )
    return fig

def create_roc_curves():
    fig = go.Figure()
    models = {
        'SVM': {'fpr': [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                'tpr': [0, 0.25, 0.45, 0.6, 0.72, 0.8, 0.86, 0.91, 0.95, 0.98, 1],
                'auc': 0.82},
        'GNB': {'fpr': [0, 0.15, 0.3, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1],
                'tpr': [0, 0.2, 0.38, 0.52, 0.64, 0.74, 0.82, 0.89, 0.95, 1],
                'auc': 0.76},
        'DTree': {'fpr': [0, 0.25, 0.45, 0.6, 0.7, 0.8, 0.9, 1],
                  'tpr': [0, 0.15, 0.3, 0.45, 0.58, 0.7, 0.85, 1],
                  'auc': 0.60}
    }
    for name, data in models.items():
        fig.add_trace(go.Scatter(
            x=data['fpr'], y=data['tpr'], mode='lines',
            name=f'{name} (AUC = {data["auc"]:.2f})',
            line=dict(width=2)
        ))
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode='lines',
        name='Random', line=dict(dash='dash', color='gray')
    ))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8A8F99'),
        xaxis=dict(title="False Positive Rate", gridcolor='#1A1D24'),
        yaxis=dict(title="True Positive Rate", gridcolor='#1A1D24'),
        height=400,
        legend=dict(x=0.7, y=0.2)
    )
    return fig

def create_precision_recall_curves():
    fig = go.Figure()
    models = {
        'SVM': {'recall': [0, 0.2, 0.35, 0.48, 0.6, 0.72, 0.85, 1],
                'precision': [1, 0.88, 0.82, 0.78, 0.74, 0.7, 0.65, 0.6],
                'auc': 0.79},
        'GNB': {'recall': [0, 0.18, 0.32, 0.45, 0.58, 0.7, 0.82, 1],
                'precision': [1, 0.85, 0.78, 0.72, 0.68, 0.64, 0.6, 0.55],
                'auc': 0.74},
        'DTree': {'recall': [0, 0.15, 0.28, 0.4, 0.52, 0.65, 0.78, 1],
                  'precision': [1, 0.82, 0.74, 0.68, 0.62, 0.58, 0.54, 0.5],
                  'auc': 0.65}
    }
    for name, data in models.items():
        fig.add_trace(go.Scatter(
            x=data['recall'], y=data['precision'], mode='lines',
            name=f'{name} (AUC = {data["auc"]:.2f})',
            line=dict(width=2)
        ))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8A8F99'),
        xaxis=dict(title="Recall", gridcolor='#1A1D24'),
        yaxis=dict(title="Precision", gridcolor='#1A1D24'),
        height=400
    )
    return fig

def create_sankey_diagram():
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=["Jan Positive", "Jan Neutral", "Jan Negative",
                   "Feb Positive", "Feb Neutral", "Feb Negative",
                   "Mar Positive", "Mar Neutral", "Mar Negative"],
            color=["#10B981", "#8A8F99", "#EF4444"] * 3
        ),
        link=dict(
            source=[0, 0, 1, 1, 2, 2, 3, 4, 5],
            target=[3, 4, 3, 4, 5, 5, 6, 7, 8],
            value=[15, 8, 10, 35, 5, 28, 12, 40, 30],
            color=["rgba(16,185,129,0.3)"] * 9
        )
    )])
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8A8F99', size=10),
        height=400
    )
    return fig

def create_heatmap():
    data = np.random.rand(8, 8)
    np.fill_diagonal(data, 1)
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=['SPY', 'VIX', 'Positive', 'Neutral', 'Negative', 'Volume', 'Volatility', 'Anomaly'],
        y=['SPY', 'VIX', 'Positive', 'Neutral', 'Negative', 'Volume', 'Volatility', 'Anomaly'],
        colorscale=[[0, '#EF4444'], [0.5, '#111317'], [1, '#10B981']],
        showscale=True
    ))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8A8F99'),
        height=500
    )
    return fig

def display_word_cloud(word_freq):
    """Display a word cloud from a frequency dictionary."""
    wordcloud = WordCloud(width=800, height=400, background_color='black', colormap='viridis').generate_from_frequencies(word_freq)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)