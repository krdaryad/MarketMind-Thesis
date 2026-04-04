"""
Model Accuracy page.
"""
import streamlit as st
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
        st.markdown('<h3>⚡ Classifier Performance</h3>', unsafe_allow_html=True)
        
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
            highlight_class = "text-chart-3" if model["highlight"] else "text-foreground"
            
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
        with st.popover("🎓", use_container_width=False):
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
            border_style = "border-primary/30 bg-primary/5" if is_optimal else "border-border bg-card"
            text_color = "text-primary" if is_optimal else "text-foreground"
            
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
    
    # Insight note
    st.markdown("""
    <div style="margin-top: 1rem; background: rgba(59,130,246,0.05); border: 1px solid rgba(59,130,246,0.1); border-radius: 12px; padding: 0.75rem;">
        <p style="font-size: 0.75rem; color: #8A8F99; margin: 0;">
            <strong style="color: #FFFFFF;">Optimal:</strong> k=5 achieves the highest silhouette score (0.55), aligning with the 5 LDA topics discovered on the AI Analysis page. 
            Clusters map to: <span style="color: #3B82F6; font-family: monospace;">Rate Policy · Tech Earnings · Macro Fear · Meme/Retail · Sector Rotation</span>.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)