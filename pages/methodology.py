import streamlit as st

def methodology_page():

    st.title("Methodology")
    st.markdown('<p style="color: #64748b; font-size: 1.1rem;">Data pipeline, feature engineering, and analysis methods</p>', unsafe_allow_html=True)
    st.divider()
    
    posts_df = st.session_state.get('posts_data', None)
    if posts_df is not None and not posts_df.empty:
        total_posts = len(posts_df)
        unique_companies = posts_df['company_standard'].nunique() if 'company_standard' in posts_df.columns else 0
        avg_score = posts_df['score'].mean()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Posts", f"{total_posts:,}")
        m2.metric("Companies", unique_companies)
        m3.metric("Avg Score", f"{avg_score:.1f}")
    
    st.write("##")  

    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        with st.container(border=True):
            st.subheader("Data Collection")
            st.markdown("""
            Reddit posts were sourced from finance communities like r/wallstreetbets and r/stocks during the February–March 2021 meme‑stock event.  
            Each record includes post text, sentiment label (positive/neutral/negative), score, comments, and a timestamp.  
            Market data (S&P 500, VIX, 10‑year Treasury) comes from Yahoo Finance and the FRED API, used as visual overlays on the timeline.
            """)
        
        st.write("##")
        
        with st.container(border=True):
            st.subheader("Feature Engineering")
            st.markdown("""
            Text is converted to numerical features using TF‑IDF vectorisation (top 1000 terms, n‑grams 1‑3).  
            Sentiment is scored with VADER – a simple, explainable lexicon model that gives each post a polarity value.  
            Company names are extracted and standardised for entity tracking.  
            Daily sentiment is aggregated, and a rolling Z‑score detects anomalies – these become the coloured markers on the timeline.  
            FP‑Growth finds frequent word pairs (e.g. “inflation” + “fed”), visualised as a Sankey diagram.  
            LDA topic modelling (k=5 topics) reveals hidden themes in the conversation.
            """)
    
    with col2:
        with st.container(border=True):
            st.subheader("Model Training")
            st.markdown("""
            Four lightweight classifiers are compared: Gaussian Naive Bayes, Support Vector Machine, Decision Tree (max_depth=20), and Random Forest (100 trees).  
            Decision Tree is the fastest (< 0.01 ms per post) – ideal for keeping the dashboard responsive.  
            Random Forest offers the best accuracy at ~0.55 ms per post.  
            For unsupervised clustering, K‑Means (k=4) groups posts into emotion regimes – Euphoria (green), Fear/Panic (red), Neutral/Calm (blue), Mixed/Anxious (orange).  
            All model metrics (confusion matrix, radar chart, confidence scores) are shown directly in the UI for transparency.
            """)
            
        st.write("##")

        with st.container(border=True):
            st.subheader("Performance Optimizations")
            st.markdown("""
            Streamlit’s `@st.cache_data` stores sentiment and FRED API results – repeat visits are nearly instant.  
            TF‑IDF matrices are stored as sparse arrays (< 0.5 MB) to save memory.  
            All aggregations use vectorised Pandas operations, not slow loops.  
            Heavy models load only when you visit the AI Analysis page (lazy loading).  
            **Measured results** (from thesis Section 4.3):  
            • Decision Tree inference: < 0.01 ms/post  
            • Total memory footprint: 279 MB (fits on a mobile device)  
            • Cold start 2.8 s → warm cache 0.9 s (68% faster)  
            • Hover tooltips appear in < 30 ms, filters response ~150 ms
            """)

    st.write("##")

    with st.expander("Future Roadmap: From Data Visualization to Immersive Experience", expanded=True):
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### Creative Interaction & UX")
            st.markdown("""
            **Customizable 'Widget' Workspace**  
            A drag-and-drop dashboard using `@dnd-kit`, allowing users to build bespoke layouts (KPIs, Radar, Heatmaps) that persist via `localStorage` for personalized auditing.

            **Scrollytelling Case Studies**  
            Full-screen, scroll-driven narratives for the 'GME Squeeze' and 'COVID Crash.' Implements sticky charts and fade-in chapter cards synced to a scroll-progress reference line.

            **Collaborative Annotation Mode**  
            A Canvas-based `AnnotationOverlay` enabling users to draw directly over charts. Features 4-color palettes, variable line-weights, and high-res PNG export for report generation.
            """)

        with c2:
            st.markdown("### Sensory Systems & Accessibility")
            st.markdown("""
            **WebAudio Sentiment Sonification**  
            An interactive `SoundContext` using synth tones to represent market regimes. Automatic triggering on hover: **Bright A5** for Euphoria, **Low Sawtooth** for Fear, and **Sine waves** for Neutrality.

            **Integrated Defense Framework**  
            A native 1920×1080 slide deck mode (`/defense`) featuring grid overviews, arrow-key navigation, and Fullscreen API support—designed specifically for academic presentation.

            **Multilingual i18n Architecture**  
            A robust `LanguageContext` supporting EN/LT (English/Lithuanian) transitions for all thesis-critical strings, ensuring global accessibility and local academic compliance.
            """)



if __name__ == "__main__":
    methodology_page()