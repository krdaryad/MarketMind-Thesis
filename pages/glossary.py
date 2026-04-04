import streamlit as st
import pandas as pd

def glossary_page():
    st.set_page_config(page_title="Interactive Glossary", layout="wide")

    # --- 1. DATASET ---
    glossary = [
        {"term": "ARIMA", "category": "stats", "definition": "Auto-Regressive Integrated Moving Average. A time-series forecasting model.", "formula": r"Y_t = c + \sum \phi_i Y_{t-i} + \sum \theta_j \epsilon_{t-j} + \epsilon_t", "related": ["RMSE", "Stationarity"]},
        {"term": "AUC", "category": "ml", "definition": "Area Under the (ROC) Curve. Measures overall classifier performance.", "related": ["ROC Curve", "TPR", "FPR"]},
        {"term": "Bag of Words", "category": "nlp", "definition": "A text representation that counts word occurrences, ignoring grammar.", "related": ["TF-IDF", "TDM"]},
        {"term": "Confusion Matrix", "category": "ml", "definition": "A table showing true vs predicted labels. Diagonal = correct.", "formula": r"\text{Acc} = \frac{TP + TN}{TP + TN + FP + FN}", "related": ["Precision", "Recall"]},
        {"term": "Correlation", "category": "stats", "definition": "Measures linear relationship between two variables (-1 to +1).", "formula": r"r = \frac{\sum(x-\bar{x})(y-\bar{y})}{\sqrt{\sum(x-\bar{x})^2\sum(y-\bar{y})^2}}", "related": ["VIX"]},
        {"term": "Decision Tree", "category": "ml", "definition": "Classifier splitting data into branches based on feature thresholds.", "related": ["SVM", "GNB"]},
        {"term": "F1 Score", "category": "ml", "definition": "Harmonic mean of precision and recall. Best for imbalanced classes.", "formula": r"F1 = 2 \cdot \frac{P \cdot R}{P + R}", "related": ["Precision", "Recall"]},
        {"term": "FPR", "category": "ml", "definition": "Proportion of actual negatives incorrectly classified as positive.", "formula": r"FPR = \frac{FP}{FP + TN}", "related": ["ROC Curve"]},
        {"term": "FP-Growth", "category": "ml", "definition": "Algorithm finding co-occurring sets without candidate pairs.", "formula": r"Supp = \frac{count(A \cup B)}{N}", "related": ["Association Rules"]},
        {"term": "GNB", "category": "ml", "definition": "Probabilistic classifier assuming Gaussian distribution.", "formula": r"P(c|f) \propto P(c) \prod P(f_i|c)", "related": ["TF-IDF"]},
        {"term": "Isolation Forest", "category": "ml", "definition": "Anomaly detection isolating observations by random splits.", "related": ["Z-Score"]},
        {"term": "LDA", "category": "nlp", "definition": "Unsupervised algorithm discovering hidden topics in documents.", "formula": r"P(w|d) = \sum_k P(w|t_k)P(t_k|d)", "related": ["Topic Modeling"]},
        {"term": "NER", "category": "nlp", "definition": "Identifying entities (people, places) in text.", "related": ["spaCy"]},
        {"term": "Precision", "category": "ml", "definition": "Ratio of correct positive predictions to total predicted positives.", "formula": r"Prec = \frac{TP}{TP + FP}", "related": ["Recall", "F1"]},
        {"term": "Recall", "category": "ml", "definition": "Ratio of correct positive predictions to total actual positives.", "formula": r"Rec = \frac{TP}{TP + FN}", "related": ["Precision"]},
        {"term": "RMSE", "category": "stats", "definition": "Root Mean Square Error. Measures average error magnitude.", "formula": r"RMSE = \sqrt{\frac{\sum(\hat{y}-y)^2}{n}}", "related": ["ARIMA"]},
        {"term": "ROC Curve", "category": "ml", "definition": "Plot showing the trade-off between TPR and FPR.", "related": ["AUC"]},
        {"term": "S&P 500", "category": "finance", "definition": "Stock market index tracking 500 large US companies.", "related": ["VIX"]},
        {"term": "Sankey Diagram", "category": "stats", "definition": "Flow diagram showing values migrating between categories.", "related": ["Data Viz"]},
        {"term": "Sentiment Analysis", "category": "nlp", "definition": "Determining emotional tone in text.", "related": ["NER", "TF-IDF"]},
        {"term": "Stationarity", "category": "stats", "definition": "Statistical properties that do not change over time.", "related": ["ARIMA"]},
        {"term": "SVM", "category": "ml", "definition": "Classifier finding the optimal hyperplane with maximum margin.", "related": ["Decision Tree"]},
        {"term": "TDM", "category": "nlp", "definition": "Matrix showing term frequencies across documents.", "related": ["TF-IDF"]},
        {"term": "TF-IDF", "category": "nlp", "definition": "Weights words by frequency relative to the corpus.", "formula": r"TF \cdot \log(\frac{N}{df})", "related": ["Bag of Words"]},
        {"term": "TPR", "category": "ml", "definition": "Proportion of actual positives correctly identified.", "formula": r"TPR = \frac{TP}{TP + FN}", "related": ["FPR"]},
        {"term": "VIX", "category": "finance", "definition": "Volatility Index measuring market 'fear' gauge.", "formula": r"VIX \approx \sigma \sqrt{\frac{365}{30}} 100", "related": ["S&P 500"]},
        {"term": "Word Cloud", "category": "stats", "definition": "Visual showing word size based on frequency.", "related": ["Bag of Words"]}
    ]

    # --- 2. SIDEBAR (SEARCH & FILTER) ---
    with st.sidebar:
        st.header(" Controls")
        
        # SEARCH INPUT
        search_query = st.text_input("Search terms...", placeholder="Type to filter...")
        
        # CATEGORY FILTER
        cat_options = {"All Categories": None, "Machine Learning": "ml", "NLP": "nlp", "Finance": "finance", "Statistics": "stats"}
        selected_label = st.selectbox("Filter by Category", list(cat_options.keys()))
        selected_cat = cat_options[selected_label]

        # FILTER LOGIC
        filtered_glossary = [
            item for item in glossary 
            if (not selected_cat or item['category'] == selected_cat) and
            (search_query.lower() in item['term'].lower() or search_query.lower() in item['definition'].lower())
        ]

        st.divider()
        
        # EXPORT BUTTON
        if filtered_glossary:
            df = pd.DataFrame(filtered_glossary)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"Export {len(filtered_glossary)} items to CSV",
                data=csv,
                file_name="filtered_glossary.csv",
                mime="text/csv",
                use_container_width=True
            )

    # --- 3. MAIN UI ---
    st.title(" Knowledge Glossary")
    st.write(f"Showing **{len(filtered_glossary)}** matching terms")

    # Layout colors
    styles = {
        "ml": {"c": "#3B82F6", "bg": "rgba(59,130,246,0.1)"},
        "nlp": {"c": "#F59E0B", "bg": "rgba(245,158,11,0.1)"},
        "finance": {"c": "#10B981", "bg": "rgba(16,185,129,0.1)"},
        "stats": {"c": "#8B5CF6", "bg": "rgba(139,92,246,0.1)"}
    }

    # Grid Rendering (3 columns)
    cols = st.columns(3)
    for idx, item in enumerate(filtered_glossary):
        with cols[idx % 3]:
            s = styles.get(item['category'])
            st.markdown(f"""
                <div style="background:{s['bg']}; color:{s['c']}; padding:2px 10px; border-radius:10px; display:inline-block; font-size:10px; font-weight:bold; text-transform:uppercase;">
                    {item['category']}
                </div>
                <h3 style="margin:10px 0 5px 0;">{item['term']}</h3>
                <p style="font-size:14px; color:#444;">{item['definition']}</p>
            """, unsafe_allow_html=True)
            
            if "formula" in item:
                with st.expander("Show Formula"):
                    st.latex(item['formula'])
            
            st.caption(f"Related: {', '.join(item['related'])}")
            st.divider()

if __name__ == "__main__":
    glossary_page()
