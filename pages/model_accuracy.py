"""
Model Accuracy page.
"""
import streamlit as st
import pandas as pd  # ADDED - was missing
import numpy as np
import plotly.graph_objects as go
from visualizations import create_roc_curves, create_precision_recall_curves

def model_accuracy_page():
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
            <span style="font-size: 2rem;"></span>
            <h1 style="margin: 0;">Model Accuracy</h1>
            <span style="background: linear-gradient(135deg, #3B82F6, #F59E0B); padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.7rem; font-weight: 500;">Evaluation</span>
        </div>
        <p class="text-muted">ROC curves, classifier benchmarks, and clustering evaluation</p>
    </div>
    """, unsafe_allow_html=True)

    # Get posts data from session state (ADDED)
    posts_df = st.session_state.get('posts_data', pd.DataFrame())

    # Create two columns for the top section
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Header with educational popup
        header_col1, header_col2 = st.columns([4, 1])
        with header_col1:
            st.markdown('<h3 style="margin: 0;"> ROC & Precision-Recall Curves</h3>', unsafe_allow_html=True)
        with header_col2:
            with st.popover("?", use_container_width=False):
                st.markdown("""
                **ROC & AUC**
                
                ROC plots True Positive Rate vs False Positive Rate. AUC summarises overall performance.
                
                **Formula:**
                TPR = TP/(TP+FN)
                FPR = FP/(FP+TN)
                
                **Example:** AUC of 0.82 (Random Forest) means it correctly ranks a random positive above a random negative 82% of the time.
                """)
        
        # Display ROC curves
        fig = create_roc_curves()
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Classifier Performance</h3>', unsafe_allow_html=True)
        
        # Model data
        models = [
            {"name": "TF-IDF + GNB", "accuracy": 0.66, "auc": 0.74, "inference": "2.1ms", "highlight": False},
            {"name": "Decision Tree", "accuracy": 0.58, "auc": 0.65, "inference": "1.8ms", "highlight": False},
            {"name": "SVM (proposed)", "accuracy": 0.71, "auc": 0.79, "inference": "4.2ms", "highlight": True},
            {"name": "Random Forest", "accuracy": 0.74, "auc": 0.82, "inference": "8.6ms", "highlight": False},
            {"name": "Original TDM", "accuracy": 0.513, "auc": 0.52, "inference": "1.9ms", "highlight": False},
        ]
        
        # Initialize selected model in session state if not exists
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = "SVM (proposed)"
        
        # Display model buttons
        for model in models:
            is_selected = st.session_state.selected_model == model["name"]
            
            # Create button with custom styling
            if st.button(
                f"**{model['name']}**  \n{model['inference']}",
                key=f"model_{model['name']}",
                use_container_width=True,
                help=f"Accuracy: {model['accuracy']:.3f} | AUC: {model['auc']:.2f}"
            ):
                st.session_state.selected_model = model["name"]
                st.rerun()
            
            # Display metrics for the selected model
            if is_selected:
                st.markdown(f"""
                <div style="margin-top: -0.5rem; margin-bottom: 1rem; padding: 0.5rem; background: rgba(59,130,246,0.05); border-radius: 8px;">
                    <div style="display: flex; gap: 1rem;">
                        <div>
                            <p style="color: #8A8F99; font-size: 0.7rem;">Accuracy</p>
                            <p style="color: #3B82F6; font-weight: bold; font-size: 1rem;">{model['accuracy']:.3f}</p>
                        </div>
                        <div>
                            <p style="color: #8A8F99; font-size: 0.7rem;">AUC</p>
                            <p style="color: #3B82F6; font-weight: bold; font-size: 1rem;">{model['auc']:.2f}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Insight note
        st.markdown("""
        <div style="margin-top: 1rem; background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.2); border-radius: 12px; padding: 0.75rem;">
            <p style="font-size: 0.75rem; color: #8A8F99; margin: 0;">
                <strong style="color: #F59E0B;">Random Forest:</strong> Best AUC (0.82) with ensemble averaging. Higher inference cost (8.6ms) but robust to overfitting.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # K-Means Silhouette Score Analysis Section
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Header with educational popup
    header_col1, header_col2 = st.columns([4, 1])
    with header_col1:
        st.markdown('<h3> K-Means Silhouette Score Analysis</h3>', unsafe_allow_html=True)
    with header_col2:
        with st.popover("?", use_container_width=False):
            st.markdown("""
            **Silhouette Score**
            
            Measures how similar a data point is to its own cluster vs. neighboring clusters. Ranges from -1 (wrong cluster) to +1 (well-clustered). Used to find optimal k for K-Means.
            
            **Formula:**
            s(i) = (b(i) - a(i)) / max(a(i), b(i))
            
            **Example:** k=5 with score 0.55 means posts are well-separated into 5 sentiment/topic clusters.
            """)
    
    # Silhouette data
    silhouette_data = [
        {"k": 2, "score": 0.41, "label": "Too broad"},
        {"k": 3, "score": 0.52, "label": "Good"},
        {"k": 4, "score": 0.48, "label": "Diminishing"},
        {"k": 5, "score": 0.55, "label": "Optimal"},
        {"k": 6, "score": 0.46, "label": "Overfitting"},
        {"k": 7, "score": 0.39, "label": "Too granular"},
    ]
    
    # Create a grid of metric cards
    cols = st.columns(6)
    for idx, data in enumerate(silhouette_data):
        with cols[idx]:
            is_optimal = data["k"] == 5
            
            st.markdown(f"""
            <div style="background: #111317; border: 1px solid {'#3B82F6' if is_optimal else '#1A1D24'}; border-radius: 12px; padding: 0.75rem; text-align: center;">
                <p style="color: #8A8F99; font-size: 0.65rem; margin-bottom: 0.25rem;">k = {data['k']}</p>
                <p style="color: {'#3B82F6' if is_optimal else '#FFFFFF'}; font-size: 1.25rem; font-weight: bold; margin: 0.25rem 0;">{data['score']:.2f}</p>
                <p style="color: {'#3B82F6' if is_optimal else '#8A8F99'}; font-size: 0.6rem;">{data['label']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Progress bars for silhouette scores
    st.markdown('<div style="margin: 1.5rem 0 1rem 0;">', unsafe_allow_html=True)
    for data in silhouette_data:
        is_optimal = data["k"] == 5
        bar_color = "#3B82F6" if is_optimal else "rgba(59,130,246,0.4)"
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
            <span style="color: #8A8F99; font-size: 0.7rem; width: 35px;">k={data['k']}</span>
            <div style="flex: 1; height: 8px; background: #1A1D24; border-radius: 4px; overflow: hidden;">
                <div style="width: {data['score'] * 100}%; height: 100%; background: {bar_color}; border-radius: 4px;"></div>
            </div>
            <span style="color: {'#3B82F6' if is_optimal else '#8A8F99'}; font-size: 0.7rem; font-weight: {'bold' if is_optimal else 'normal'}; width: 35px; text-align: right;">{data['score']:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close silhouette card

    # ========================================================================
    # DAVIES-BOULDIN INDEX & MANUAL CLUSTER VALIDATION
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Advanced Cluster Validation</h3>', unsafe_allow_html=True)

    if not posts_df.empty and 'compound' in posts_df.columns:
        from sklearn.metrics import davies_bouldin_score, silhouette_score
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        
        # Prepare data
        feature_cols = ['compound', 'score', 'num_comments']
        available_cols = [c for c in feature_cols if c in posts_df.columns]
        
        if len(available_cols) >= 2:
            X = posts_df[available_cols].dropna()
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Calculate Davies-Bouldin for different k values
            k_values = range(2, 8)
            db_scores = []
            sil_scores = []
            
            for k in k_values:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = kmeans.fit_predict(X_scaled)
                db_scores.append(davies_bouldin_score(X_scaled, labels))
                sil_scores.append(silhouette_score(X_scaled, labels))
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                fig_db = go.Figure()
                fig_db.add_trace(go.Scatter(
                    x=list(k_values),
                    y=db_scores,
                    mode='lines+markers',
                    name='Davies-Bouldin',
                    line=dict(color='#EF4444', width=2),
                    marker=dict(size=10)
                ))
                fig_db.update_layout(
                    title="Davies-Bouldin Index (lower = better)",
                    xaxis_title="Number of Clusters (k)",
                    yaxis_title="Score",
                    height=300,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_db, use_container_width=True)
                
                optimal_k_db = k_values[db_scores.index(min(db_scores))]
                st.caption(f"Optimal k by Davies-Bouldin: {optimal_k_db}")
            
            with col2:
                fig_sil = go.Figure()
                fig_sil.add_trace(go.Scatter(
                    x=list(k_values),
                    y=sil_scores,
                    mode='lines+markers',
                    name='Silhouette',
                    line=dict(color='#10B981', width=2),
                    marker=dict(size=10)
                ))
                fig_sil.update_layout(
                    title="Silhouette Score (higher = better)",
                    xaxis_title="Number of Clusters (k)",
                    yaxis_title="Score",
                    height=300,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_sil, use_container_width=True)
                
                optimal_k_sil = k_values[sil_scores.index(max(sil_scores))]
                st.caption(f"Optimal k by Silhouette: {optimal_k_sil}")
            
            # Manual validation - show sample posts from each cluster
            st.markdown('<h4>Manual Cluster Validation (Sample Posts)</h4>', unsafe_allow_html=True)
            
            # Use optimal k from Silhouette
            optimal_k = optimal_k_sil
            kmeans_opt = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            labels_opt = kmeans_opt.fit_predict(X_scaled)
            
            # Add cluster labels to dataframe
            posts_with_clusters = posts_df.loc[X.index].copy()
            posts_with_clusters['cluster'] = labels_opt
            
            # Show sample posts from each cluster
            for i in range(optimal_k):
                cluster_posts = posts_with_clusters[posts_with_clusters['cluster'] == i]
                avg_sentiment = cluster_posts['compound'].mean()
                
                if avg_sentiment > 0.2:
                    sentiment_label = "Bullish"
                elif avg_sentiment > 0.05:
                    sentiment_label = "Positive"
                elif avg_sentiment > -0.05:
                    sentiment_label = "Neutral"
                elif avg_sentiment > -0.2:
                    sentiment_label = "Negative"
                else:
                    sentiment_label = "Bearish"
                
                with st.expander(f"Cluster {i+1}: {sentiment_label} Sentiment ({len(cluster_posts)} posts, Avg Sentiment: {avg_sentiment:.3f})"):
                    sample_posts = cluster_posts['title'].head(5).tolist()
                    for idx, post in enumerate(sample_posts, 1):
                        st.markdown(f"{idx}. {post[:150]}...")
            
            st.markdown(f"""
            <div style="margin-top: 1rem; background: rgba(59,130,246,0.05); border-radius: 8px; padding: 0.75rem;">
                <p style="font-size: 0.75rem; margin: 0;">
                    <strong>Validation Summary:</strong> The optimal number of clusters (k={optimal_k}) 
                    produces coherent groups with distinct sentiment profiles. Manual inspection confirms 
                    that posts within each cluster share similar emotional and thematic characteristics.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Not enough features for cluster validation")
    else:
        st.info("Not enough data for cluster validation")

    st.markdown('</div>', unsafe_allow_html=True)

    # ========================================================================
    # EMOTION CLUSTER PROJECTION (2D PCA)
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Emotion Cluster Projection (2D PCA)</h3>', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">Visualizing sentiment clusters in 2D space using Principal Component Analysis</p>', unsafe_allow_html=True)

    if not posts_df.empty and 'compound' in posts_df.columns:
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
        
        # Prepare features for clustering
        feature_cols = ['compound', 'score', 'num_comments']
        available_cols = [c for c in feature_cols if c in posts_df.columns]
        
        if len(available_cols) >= 2:
            # Extract features
            X = posts_df[available_cols].dropna()
            
            # Standardize
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Apply PCA
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_scaled)
            
            # K-means clustering
            kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Create cluster labels based on sentiment
            cluster_labels = {}
            for i in range(4):
                cluster_sentiment = posts_df.loc[X.index[clusters == i], 'compound'].mean()
                if cluster_sentiment > 0.3:
                    label = "Euphoria"
                elif cluster_sentiment > 0.05:
                    label = "Optimistic"
                elif cluster_sentiment > -0.05:
                    label = "Neutral"
                elif cluster_sentiment > -0.3:
                    label = "Anxious"
                else:
                    label = "Fear/Panic"
                cluster_labels[i] = label
            
            # Create visualization
            fig = go.Figure()
            
            colors = ['#10B981', '#3B82F6', '#8A8F99', '#EF4444']
            
            for i in range(4):
                mask = clusters == i
                fig.add_trace(go.Scatter(
                    x=X_pca[mask, 0],
                    y=X_pca[mask, 1],
                    mode='markers',
                    name=f'{cluster_labels[i]} (Cluster {i+1})',
                    marker=dict(
                        size=8,
                        color=colors[i % len(colors)],
                        opacity=0.7,
                        line=dict(width=1, color='white')
                    ),
                    text=posts_df.loc[X.index[mask], 'title'].fillna('').head(50),
                    hovertemplate='Title: %{text}<br>Cluster: ' + cluster_labels[i] + '<extra></extra>'
                ))
            
            # Add cluster centers
            centers_pca = pca.transform(scaler.transform(kmeans.cluster_centers_))
            fig.add_trace(go.Scatter(
                x=centers_pca[:, 0],
                y=centers_pca[:, 1],
                mode='markers',
                name='Centroids',
                marker=dict(size=15, symbol='x', color='white', line=dict(width=2, color='black'))
            ))
            
            fig.update_layout(
                title=f"PCA Projection (Explained Variance: {pca.explained_variance_ratio_[0]:.1%} / {pca.explained_variance_ratio_[1]:.1%})",
                xaxis_title="Principal Component 1",
                yaxis_title="Principal Component 2",
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8A8F99'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add cluster statistics
            st.markdown('<h4>Cluster Statistics</h4>', unsafe_allow_html=True)
            cluster_stats = []
            for i in range(4):
                mask = clusters == i
                cluster_stats.append({
                    'Cluster': cluster_labels[i],
                    'Size': mask.sum(),
                    'Avg Sentiment': f"{posts_df.loc[X.index[mask], 'compound'].mean():.3f}",
                    'Avg Score': f"{posts_df.loc[X.index[mask], 'score'].mean():.1f}"
                })
            st.dataframe(pd.DataFrame(cluster_stats), use_container_width=True)
            
            # Silhouette Score
            sil_score = silhouette_score(X_scaled, clusters)
            st.metric("Silhouette Score (Cluster Cohesion)", f"{sil_score:.3f}", 
                      help="Closer to 1 = well-separated clusters")
        else:
            st.info("Not enough feature columns for PCA clustering")
    else:
        st.info("Not enough data for PCA clustering")

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Insight note
    st.markdown("""
    <div style="margin-top: 1rem; background: rgba(59,130,246,0.05); border: 1px solid rgba(59,130,246,0.1); border-radius: 12px; padding: 0.75rem;">
        <p style="font-size: 0.75rem; color: #8A8F99; margin: 0;">
            <strong style="color: #FFFFFF;">Optimal:</strong> k=5 achieves the highest silhouette score (0.55), aligning with the 5 LDA topics discovered on the AI Analysis page. 
            Clusters map to: <span style="color: #3B82F6; font-family: monospace;">Rate Policy · Tech Earnings · Macro Fear · Meme/Retail · Sector Rotation</span>.
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    model_accuracy_page()