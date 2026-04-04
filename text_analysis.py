"""
Text preprocessing, topic extraction, pattern mining, and model training.
"""
import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import label_binarize
from sklearn.model_selection import train_test_split
from mlxtend.frequent_patterns import fpgrowth, association_rules
import nltk
from nltk.corpus import stopwords
import streamlit as st

nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    """Basic cleaning: lowercase, remove punctuation, digits, stopwords."""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in stop_words and len(t) > 2]
    return ' '.join(tokens)

def extract_topics(posts_df, n_topics=5, n_top_words=10):
    """
    Run LDA on post texts and return a dictionary of topic: list of top words.
    """
    if posts_df.empty:
        return {f"Topic {i+1}": ["no data"]*n_top_words for i in range(n_topics)}

    # Preprocess texts
    processed = posts_df['text'].fillna('').apply(preprocess_text)
    # Remove empty documents
    processed = processed[processed.str.len() > 0]
    if len(processed) == 0:
        return {f"Topic {i+1}": ["no text"]*n_top_words for i in range(n_topics)}

    # Vectorize
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    dtm = vectorizer.fit_transform(processed)

    # Fit LDA
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(dtm)

    # Extract top words
    feature_names = vectorizer.get_feature_names_out()
    topics = {}
    for idx, topic in enumerate(lda.components_):
        top_words_idx = topic.argsort()[:-n_top_words-1:-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topics[f"Topic {idx+1}"] = top_words
    return topics

def extract_patterns(posts_df, min_support=0.01, min_confidence=0.5, max_len=3):
    """
    Use FP‑Growth to find frequent word sets and association rules.
    Returns a DataFrame with patterns, support, confidence, lift.
    """
    if posts_df.empty:
        return pd.DataFrame(columns=['pattern', 'support', 'confidence', 'lift'])

    # Preprocess each post into a set of words (presence only)
    processed = posts_df['text'].fillna('').apply(preprocess_text)
    # Keep only posts with at least one word
    valid = processed[processed.str.len() > 0]
    if len(valid) == 0:
        return pd.DataFrame(columns=['pattern', 'support', 'confidence', 'lift'])

    # Create a list of unique words across all posts (limit to frequent ones to avoid huge matrix)
    all_words = set()
    for doc in valid:
        all_words.update(doc.split())
    # If too many words, take most frequent? For simplicity, we'll use all, but it may be slow.
    # Instead, we can limit to top 500 words by frequency.
    word_counts = {}
    for doc in valid:
        for w in doc.split():
            word_counts[w] = word_counts.get(w, 0) + 1
    top_words = [w for w, c in sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:500]]
    # Build binary matrix
    onehot = []
    for doc in valid:
        words_set = set(doc.split())
        row = [1 if w in words_set else 0 for w in top_words]
        onehot.append(row)
    df_bin = pd.DataFrame(onehot, columns=top_words)

    # Run FP‑Growth
    frequent_itemsets = fpgrowth(df_bin, min_support=min_support, use_colnames=True)
    if frequent_itemsets.empty:
        return pd.DataFrame(columns=['pattern', 'support', 'confidence', 'lift'])

    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    if rules.empty:
        return pd.DataFrame(columns=['pattern', 'support', 'confidence', 'lift'])

    # Format output similar to synthetic patterns
    patterns = []
    for _, row in rules.iterrows():
        antecedent = ', '.join(list(row['antecedents']))
        consequent = ', '.join(list(row['consequents']))
        pattern = f"{antecedent} → {consequent}" if antecedent else consequent
        patterns.append({
            'pattern': pattern,
            'support': row['support'],
            'confidence': row['confidence'],
            'lift': row['lift']
        })
    return pd.DataFrame(patterns).sort_values('support', ascending=False).head(10)

def train_models(posts_df):
    """
    Train classifiers on sentiment labels and return metrics (accuracy, AUC, precision, recall).
    Returns a DataFrame similar to generate_model_performance().
    """
    if posts_df.empty:
        return pd.DataFrame(columns=['Model', 'Accuracy', 'AUC', 'Precision', 'Recall'])

    # Use only posts with non‑empty text
    df = posts_df[posts_df['text'].notna() & (posts_df['text'].str.len() > 0)].copy()
    if len(df) < 10:  # not enough data
        return pd.DataFrame(columns=['Model', 'Accuracy', 'AUC', 'Precision', 'Recall'])

    # Prepare features and labels
    X_text = df['text'].fillna('')
    y = df['sentiment']  # 'positive', 'neutral', 'negative'

    # Vectorize
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    X = vectorizer.fit_transform(X_text)

    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Models
    models = {
        'Gaussian Naive Bayes': GaussianNB(),
        'Decision Tree': DecisionTreeClassifier(),
        'SVM': SVC(kernel='linear', probability=True),
        'Random Forest': RandomForestClassifier(n_estimators=100)
    }

    results = []
    for name, model in models.items():
        try:
            # For GNB, X is sparse; we can convert to dense or use MultinomialNB? We'll use GaussianNB with dense.
            if name == 'Gaussian Naive Bayes':
                X_train_dense = X_train.toarray()
                X_test_dense = X_test.toarray()
                model.fit(X_train_dense, y_train)
                y_pred = model.predict(X_test_dense)
                # For AUC we need probabilities; GNB does not provide them directly? It does via predict_proba.
                if hasattr(model, 'predict_proba'):
                    y_proba = model.predict_proba(X_test_dense)
                else:
                    y_proba = None
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                if hasattr(model, 'predict_proba'):
                    y_proba = model.predict_proba(X_test)
                else:
                    y_proba = None

            # Metrics
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)

            # AUC (macro) – only if binary or if we have probabilities
            if y_proba is not None:
                classes = model.classes_
                y_test_bin = label_binarize(y_test, classes=classes)
                auc_macro = roc_auc_score(y_test_bin, y_proba, average='macro', multi_class='ovr')
            else:
                auc_macro = np.nan

            results.append({
                'Model': name,
                'Accuracy': acc,
                'AUC': auc_macro,
                'Precision': prec,
                'Recall': rec
            })
        except Exception as e:
            st.warning(f"Could not train {name}: {e}")
            results.append({'Model': name, 'Accuracy': np.nan, 'AUC': np.nan, 'Precision': np.nan, 'Recall': np.nan})

    return pd.DataFrame(results)

# Cached versions for performance
@st.cache_data(ttl=86400)
def get_real_topics(posts_df):
    return extract_topics(posts_df)

@st.cache_data(ttl=86400)
def get_real_patterns(posts_df):
    return extract_patterns(posts_df)

@st.cache_data(ttl=86400)
def get_real_model_results(posts_df):
    return train_models(posts_df)
# Add this function to text_analysis.py

def load_financial_phrasebank():
    """Load the Financial PhraseBank dataset for training."""
    try:
        df = pd.read_csv('all-data.csv')
        # Rename columns to match your existing code
        df = df.rename(columns={
            'Sentence': 'text',
            'Sentiment': 'sentiment'
        })
        # Clean sentiment labels (ensure lowercase)
        df['sentiment'] = df['sentiment'].str.lower()
        return df
    except Exception as e:
        print(f"Could not load Financial PhraseBank: {e}")
        return pd.DataFrame()

def train_models_with_phrasebank(posts_df):
    """
    Train models using Financial PhraseBank + your Reddit data.
    This gives you more robust training data.
    """
    # Load PhraseBank data
    phrasebank_df = load_financial_phrasebank()
    
    if phrasebank_df.empty:
        # Fall back to just Reddit data
        return train_models(posts_df)
    
    # Combine datasets
    if not posts_df.empty and 'text' in posts_df.columns and 'sentiment' in posts_df.columns:
        # Use only posts that have sentiment already
        reddit_train = posts_df[['text', 'sentiment']].dropna()
        combined_df = pd.concat([phrasebank_df, reddit_train], ignore_index=True)
        st.info(f"Training on {len(combined_df)} samples ({len(phrasebank_df)} from PhraseBank + {len(reddit_train)} from Reddit)")
    else:
        combined_df = phrasebank_df
        st.info(f"Training on {len(combined_df)} samples from Financial PhraseBank")
    
    # Now train models on combined dataset
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.model_selection import train_test_split
    from sklearn.naive_bayes import GaussianNB
    from sklearn.svm import SVC
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    
    X_text = combined_df['text'].fillna('')
    y = combined_df['sentiment']
    
    # Vectorize
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    X = vectorizer.fit_transform(X_text)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train models
    models = {}
    
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
    
    # Calculate metrics
    results = []
    for name, model in models.items():
        if name == 'Gaussian Naive Bayes':
            y_pred = model.predict(X_test.toarray())
        else:
            y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        
        results.append({
            'Model': name,
            'Accuracy': acc,
            'Precision': prec,
            'Recall': rec,
            'AUC': None  # For multi-class, you'd need one-vs-rest
        })
    
    return pd.DataFrame(results), vectorizer, models