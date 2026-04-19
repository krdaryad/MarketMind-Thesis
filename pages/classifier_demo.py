"""
Interactive classifier demo page - Uses real ML models trained on your data with tutorial highlights.
"""
import streamlit as st
import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score
import joblib
import os
import hashlib
from datetime import datetime

# In classifier_demo.py, update to use models trained on PhraseBank

@st.cache_resource

def get_trained_models():
    """Get or train sentiment models."""
    posts_df = st.session_state.get('posts_data', pd.DataFrame())
    
    # Try to load pre-trained models first
    if os.path.exists('models/sentiment_models.pkl'):
        try:
            data = joblib.load('models/sentiment_models.pkl')
            
            # Check different possible structures
            if isinstance(data, dict):
                if 'models' in data:
                    models = data['models']
                    vectorizer = data['vectorizer']
                    
                    # Get test data if available
                    X_train = data.get('X_train', None)
                    X_test = data.get('X_test', None)
                    y_train = data.get('y_train', None)
                    y_test = data.get('y_test', None)
                    
                    return models, vectorizer, X_train, X_test, y_train, y_test
                elif 'model' in data:
                    models = data['model']
                    vectorizer = data['vectorizer']
                    return models, vectorizer, None, None, None, None
            else:
                st.warning(f"Unexpected pkl format: {type(data)}")
                
        except Exception as e:
            st.warning(f"Could not load saved models: {e}")
    
    # Train new models
    if posts_df.empty:
        st.warning("No data available to train models.")
        return None, None, None, None, None, None
    
    result = train_and_cache_models(posts_df)
    return result


def train_and_cache_models(posts_df):
    """Train models on the data and cache them."""
    if posts_df.empty:
        return None, None, None, None, None, None
    
    # Prepare data
    df = posts_df[posts_df['text'].notna() & (posts_df['text'].str.len() > 10)].copy()
    if len(df) < 10:
        st.warning(f"Need at least 10 posts with text. Found {len(df)}.")
        return None, None, None, None, None, None
    
    X_text = df['text'].fillna('')
    y = df['sentiment']
    
    # Vectorize
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    X = vectorizer.fit_transform(X_text)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train models
    models = {}
    
    with st.spinner("Training models... (this may take a moment)"):
        # Gaussian Naive Bayes
        gnb = GaussianNB()
        X_train_dense = X_train.toarray()
        gnb.fit(X_train_dense, y_train)
        models['Gaussian Naive Bayes'] = gnb
        
        # SVM
        svm = SVC(kernel='linear', probability=True, random_state=42)
        svm.fit(X_train, y_train)
        models['SVM'] = svm
        
        # Decision Tree
        dt = DecisionTreeClassifier(random_state=42)
        dt.fit(X_train, y_train)
        models['Decision Tree'] = dt
        
        # Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        models['Random Forest'] = rf
    
    # Save models
    os.makedirs('models', exist_ok=True)
    save_data = {
        'models': models,
        'vectorizer': vectorizer,
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test
    }
    joblib.dump(save_data, 'models/sentiment_models.pkl')
    st.success(f"Saved {len(models)} models to cache!")
    
    return models, vectorizer, X_train, X_test, y_train, y_test

def predict_sentiment(text, model, vectorizer):
    """Predict sentiment for a given text."""
    if not text or not model or not vectorizer:
        return "neutral", 0.5
    
    # Vectorize the text
    X = vectorizer.transform([text])
    
    # Get prediction
    if hasattr(model, 'predict_proba'):
        # Get probabilities
        if isinstance(model, GaussianNB):
            # GNB needs dense array
            X_dense = X.toarray()
            proba = model.predict_proba(X_dense)[0]
        else:
            proba = model.predict_proba(X)[0]
        
        # Get class indices
        classes = model.classes_
        
        # Find index for each sentiment
        pos_idx = list(classes).index('positive') if 'positive' in classes else -1
        neu_idx = list(classes).index('neutral') if 'neutral' in classes else -1
        neg_idx = list(classes).index('negative') if 'negative' in classes else -1
        
        # Get probabilities
        pos_prob = proba[pos_idx] if pos_idx >= 0 else 0
        neu_prob = proba[neu_idx] if neu_idx >= 0 else 0
        neg_prob = proba[neg_idx] if neg_idx >= 0 else 0
        
        # Determine sentiment
        if pos_prob > 0.5:
            return "positive", pos_prob
        elif neg_prob > 0.5:
            return "negative", neg_prob
        else:
            return "neutral", neu_prob
    else:
        # Simple prediction without probabilities
        pred = model.predict(X)[0]
        return pred, 0.7

def classifier_demo_page():
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
            <h1 style="margin: 0;">Interactive Classifier</h1>
            <span style="background: linear-gradient(135deg, #3B82F6, #F59E0B); padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.7rem; font-weight: 500;">ML Models</span>
        </div>
        <p class="text-muted">Test the sentiment classifier with your own text using models trained on Reddit data</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize feedback storage in session state
    if 'feedback_history' not in st.session_state:
        st.session_state.feedback_history = []
    
    if 'current_prediction' not in st.session_state:
        st.session_state.current_prediction = None
    
    if 'current_confidence' not in st.session_state:
        st.session_state.current_confidence = None
    
    if 'current_text' not in st.session_state:
        st.session_state.current_text = ""

    # Get data from session state
    posts_df = st.session_state.get('posts_data', pd.DataFrame())
    
    if posts_df.empty:
        st.warning("No data available. Please load data first (go to Dashboard).")
        return
    
    # Train models (cached)
    @st.cache_resource
    @st.cache_resource
    def get_models():
        """Load pre-trained models instead of training from scratch."""
        
        # First, try to load your saved model results
        if os.path.exists('models/sentiment_models.pkl'):
            try:
                data = joblib.load('models/sentiment_models.pkl')
                models = data['models']
                vectorizer = data['vectorizer']
                
                # Create dummy X_test, y_test for display (or load from saved)
                X_train, X_test, y_train, y_test = None, None, None, None
                
                return models, vectorizer, X_train, X_test, y_train, y_test
            except Exception as e:
                st.warning(f"Could not load saved models: {e}")
        
        # Fallback to training on the fly
        return train_and_cache_models(posts_df)
    
    result = get_trained_models()
    if result[0] is None:
        st.warning("Could not load or train models. Please check your data.")
        return

    models, vectorizer, X_train, X_test, y_train, y_test = result
    
    if models is None:
        st.warning("Not enough data to train models. Need at least 10 posts with text content.")
        return
    
    # Model selection
    model_names = list(models.keys())
    selected_model = st.selectbox(
        "Select Model",
        model_names,
        help="Choose which ML model to use for prediction"
    )
    
    model = models[selected_model]
    
    # Create two columns for the main content
    col1, col2 = st.columns(2)

    with col1:
        # ====================================================================
        # CLASSIFIER INPUT - TUTORIAL HIGHLIGHT
        # ====================================================================
        
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
            <h3 style="margin: 0;">Enter a comment</h3>
        </div>
        """, unsafe_allow_html=True)

        # Text input with example
        example_texts = [
            "Fed signals higher‑for‑longer rates, markets tumble.",
            "Tesla earnings absolutely crushed it! To the moon!",
            "CPI came in hot again. We're never getting rate cuts.",
            "This market is insanely overvalued. Crash incoming",
            "SPY closed at 5254 today. Volume was average.",
        ]
        
        selected_example = st.selectbox("Try an example:", ["Custom"] + example_texts)
        
        if selected_example != "Custom":
            user_text = selected_example
        else:
            user_text = st.text_area(
                "",
                value="",
                height=100,
                placeholder="Type your text here...",
                label_visibility="collapsed"
            )
        
        if user_text:
            # Get prediction
            sentiment, confidence = predict_sentiment(user_text, model, vectorizer)
            
            # Store current prediction for feedback
            st.session_state.current_prediction = sentiment
            st.session_state.current_confidence = confidence
            st.session_state.current_text = user_text
            
            # Word highlighting (simple lexicon-based for explainability)
            sentiment_lexicon = {
                "fed": -0.3, "signals": -0.1, "higher": -0.8, "rates": -0.5,
                "markets": 0.1, "tumble": -0.9, "crash": -0.9, "surge": 0.8,
                "rally": 0.7, "boom": 0.6, "growth": 0.5, "fear": -0.7,
                "bullish": 0.6, "bearish": -0.6, "positive": 0.7, "negative": -0.7,
                "good": 0.5, "great": 0.8, "excellent": 0.9, "terrible": -0.8,
                "awful": -0.8, "amazing": 0.8, "crashing": -0.9, "soaring": 0.8,
                "moon": 0.9, "rocket": 0.8
            }
            
            words = re.findall(r'\b\w+(?:[-‑]\w+)*\b', user_text)
            word_weights = []
            for word in words:
                base_word = re.sub(r'[^\w\-]', '', word.lower())
                weight = sentiment_lexicon.get(base_word, 0.0)
                if weight != 0:
                    word_weights.append((word, weight))
            
            # Display highlighted words
            if word_weights:
                st.markdown('<p style="color: #8A8F99; font-size: 0.7rem;">Word-level sentiment:</p>', unsafe_allow_html=True)
                st.markdown('<div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.5rem 0;">', unsafe_allow_html=True)
                for word, weight in word_weights:
                    if weight < -0.3:
                        bg = "rgba(239,68,68,0.3)"
                        border = "#EF4444"
                        text_color = "#FFFFFF"
                    elif weight > 0.3:
                        bg = "rgba(16,185,129,0.3)"
                        border = "#10B981"
                        text_color = "#FFFFFF"
                    else:
                        bg = "#1A1D24"
                        border = "#2A2E38"
                        text_color = "#8A8F99"
                    st.markdown(f'<span style="background: {bg}; border: 1px solid {border}; border-radius: 999px; padding: 0.25rem 0.75rem; font-size: 0.875rem; color: {text_color};">{word}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Confidence slider (user can adjust)
            st.markdown('<p style="color: #8A8F99; font-size: 0.7rem; margin-top: 1rem;">Adjust confidence threshold</p>', unsafe_allow_html=True)
            threshold = st.slider(
                "",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.05,
                format="%.2f",
                label_visibility="collapsed",
                key="threshold_slider"
            )
            
            # Adjust sentiment based on threshold
            if confidence < threshold and sentiment != "neutral":
                final_sentiment = "neutral"
                final_confidence = threshold
            else:
                final_sentiment = sentiment
                final_confidence = confidence
            
            sentiment_color = {
                "positive": "#10B981",
                "neutral": "#F59E0B",
                "negative": "#EF4444"
            }.get(final_sentiment, "#8A8F99")
            
            # Display prediction result with Confidence Meter
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(59,130,246,0.05) 0%, rgba(59,130,246,0.02) 100%); border: 1px solid #1A1D24; border-radius: 12px; padding: 1rem; margin-top: 1rem;">
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <div style="background: #1A1D24; border-radius: 8px; padding: 0.5rem;">
                        <span style="font-size: 1.5rem;"> </span>
                    </div>
                    <div style="flex: 1;">
                        <p style="color: #8A8F99; font-size: 0.7rem; margin: 0;">{selected_model}</p>
                        <p style="margin: 0;">Prediction: <strong style="color: {sentiment_color};">{final_sentiment.upper()}</strong> <span style="color: #8A8F99;">({final_confidence:.1%} confidence)</span></p>
                    </div>
                </div>
                <div style="margin-top: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span style="color: #8A8F99; font-size: 0.7rem;">Confidence Meter</span>
                        <span style="color: {sentiment_color}; font-size: 0.7rem; font-weight: 500;">{final_confidence:.1%}</span>
                    </div>
                    <div style="width: 100%; height: 8px; background: #1A1D24; border-radius: 4px; overflow: hidden;">
                        <div style="width: {final_confidence*100}%; height: 100%; background: {sentiment_color}; border-radius: 4px; transition: width 0.3s ease;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ====================================================================
            # HUMAN-IN-THE-LOOP FEEDBACK BUTTONS
            # ====================================================================
            st.markdown("""
            <div style="margin-top: 1rem;">
                <p style="color: #8A8F99; font-size: 0.7rem; margin-bottom: 0.5rem;">Was this prediction correct?</p>
            </div>
            """, unsafe_allow_html=True)
            
            feedback_col1, feedback_col2 = st.columns(2)
            
            with feedback_col1:
                if st.button("Correct", key="feedback_correct", use_container_width=True):
                    # Store feedback
                    feedback_entry = {
                        'timestamp': datetime.now(),
                        'text': user_text,
                        'predicted_sentiment': final_sentiment,
                        'confidence': final_confidence,
                        'user_feedback': 'correct',
                        'model': selected_model
                    }
                    st.session_state.feedback_history.append(feedback_entry)
                    st.success("Thanks for the feedback! This helps improve the model.")
            
            with feedback_col2:
                if st.button("Incorrect", key="feedback_incorrect", use_container_width=True):
                    # Store feedback
                    feedback_entry = {
                        'timestamp': datetime.now(),
                        'text': user_text,
                        'predicted_sentiment': final_sentiment,
                        'confidence': final_confidence,
                        'user_feedback': 'incorrect',
                        'model': selected_model
                    }
                    st.session_state.feedback_history.append(feedback_entry)
                    
                    # Optional: Ask for correct sentiment
                    with st.expander("What was the correct sentiment?"):
                        correct_sentiment = st.radio(
                            "Select correct sentiment:",
                            ['positive', 'neutral', 'negative'],
                            key=f"correct_sentiment_{len(st.session_state.feedback_history)}"
                        )
                        if st.button("Submit correction"):
                            st.session_state.feedback_history[-1]['correct_sentiment'] = correct_sentiment
                            st.success("Correction recorded! This will help retrain the model.")
            
            # Display feedback stats if there's history
            if st.session_state.feedback_history:
                with st.expander("View Feedback History"):
                    feedback_df = pd.DataFrame(st.session_state.feedback_history)
                    st.dataframe(feedback_df[['timestamp', 'predicted_sentiment', 'confidence', 'user_feedback']], 
                                use_container_width=True)
                    
                    # Calculate feedback metrics
                    total_feedback = len(feedback_df)
                    correct_count = len(feedback_df[feedback_df['user_feedback'] == 'correct'])
                    accuracy_from_feedback = correct_count / total_feedback if total_feedback > 0 else 0
                    
                    st.metric("User Feedback Accuracy", f"{accuracy_from_feedback:.1%}", 
                             help="Percentage of predictions users marked as correct")
        else:
            st.info("Enter some text above to see sentiment prediction")
        
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        
        # Header with educational popup
        header_col1, header_col2 = st.columns([4, 1])
        with header_col1:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <h3 style="margin: 0;">Model Performance</h3>
            </div>
            """, unsafe_allow_html=True)
        with header_col2:
            with st.popover("?", use_container_width=False):
                st.markdown("""
                **Confusion Matrix**
                
                Shows how predictions compare to actual labels. Diagonal = correct predictions.
                
                **Formula:**
                Accuracy = (TP + TN) / (TP + TN + FP + FN)
                """)
        
        # Get model performance metrics
        if X_test is not None and y_test is not None:
            # Get predictions for the selected model
            if isinstance(model, GaussianNB):
                X_test_dense = X_test.toarray()
                y_pred = model.predict(X_test_dense)
            else:
                y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            # Display metrics
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("Accuracy", f"{accuracy:.1%}")
            with col_b:
                st.metric("Precision", f"{precision:.1%}")
            with col_c:
                st.metric("Recall", f"{recall:.1%}")
            with col_d:
                st.metric("F1 Score", f"{f1:.1%}")
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred, labels=['positive', 'neutral', 'negative'])
            cm_percent = cm / cm.sum(axis=1, keepdims=True) * 100
            
            # Display confusion matrix
            st.markdown('<p style="color: #8A8F99; font-size: 0.7rem; margin-top: 1rem;">Confusion Matrix (% of actual class)</p>', unsafe_allow_html=True)
            
            cm_df = pd.DataFrame(
                cm_percent,
                index=['Actual Positive', 'Actual Neutral', 'Actual Negative'],
                columns=['Pred Positive', 'Pred Neutral', 'Pred Negative']
            )
            
            st.dataframe(cm_df.round(1), use_container_width=True)
            
            # Insight note
            st.markdown("""
            <div style="margin-top: 1rem; background: rgba(59,130,246,0.05); border: 1px solid rgba(59,130,246,0.1); border-radius: 12px; padding: 0.75rem;">
                <p style="font-size: 0.7rem; color: #8A8F99; margin: 0;">
                    <strong style="color: #FFFFFF;">Interpretation:</strong> Diagonal values show correct predictions. 
                    High values on the diagonal indicate good model performance. 
                    Off-diagonal values show common misclassifications.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Not enough test data to show confusion matrix")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # MODEL COMPARISON SECTION
    # ========================================================================
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
        <h3 style="margin: 0;">Model Comparison</h3>
    </div>
    <p class="text-muted">How different models perform on the test set</p>
    """, unsafe_allow_html=True)
    
    # Calculate metrics for all models
    if X_test is not None and y_test is not None:
        comparison_data = []
        
        for name, m in models.items():
            if isinstance(m, GaussianNB):
                X_test_dense = X_test.toarray()
                y_pred = m.predict(X_test_dense)
            else:
                y_pred = m.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            comparison_data.append({
                'Model': name,
                'Accuracy': f"{accuracy:.1%}",
                'Precision': f"{precision:.1%}",
                'Recall': f"{recall:.1%}",
                'F1 Score': f"{f1:.1%}"
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Highlight best model
        best_accuracy = max([float(d['Accuracy'].rstrip('%')) for d in comparison_data])
        st.markdown(f"""
        <div style="margin-top: 1rem; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); border-radius: 12px; padding: 0.75rem;">
            <p style="font-size: 0.7rem; color: #10B981; margin: 0;">
                <strong>Best Model:</strong> {comparison_data[comparison_data.index(max(comparison_data, key=lambda x: float(x['Accuracy'].rstrip('%'))))]['Model']} with {best_accuracy:.1f}% accuracy
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    classifier_demo_page()