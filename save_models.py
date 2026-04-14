"""
Run this script ONCE on your desktop to train and save all models.
After this, your app will always load pre-trained models (no more training on load).
"""

import pandas as pd
import joblib
import os
from data_fetcher import load_reddit_data, add_sentiment
from text_analysis import extract_topics, extract_patterns, train_models
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def save_all_models():
    """Train and save all ML models to disk for fast loading."""
    
    print("=" * 60)
    print("SAVING PRE-TRAINED MODELS FOR FAST LOADING")
    print("=" * 60)
    
    os.makedirs('models', exist_ok=True)
    
    # 1. Load and process data
    print("\n1. Loading Reddit data...")
    posts_df = load_reddit_data()
    
    if posts_df.empty:
        print("ERROR: Could not load Reddit data")
        return
    
    if 'sentiment' not in posts_df.columns:
        print("2. Adding sentiment labels...")
        posts_df = add_sentiment(posts_df)
    
    print(f"   Loaded {len(posts_df)} posts")
    
    # 2. Extract and save LDA topics
    print("\n3. Extracting LDA topics...")
    topics = extract_topics(posts_df)
    joblib.dump(topics, 'models/topics.pkl')
    print(f"   ✓ Topics saved (keys: {list(topics.keys())})")
    
    # 3. Extract and save FP-Growth patterns
    print("\n4. Mining frequent patterns (FP-Growth)...")
    patterns = extract_patterns(posts_df)
    joblib.dump(patterns, 'models/patterns.pkl')
    print(f"   ✓ Patterns saved ({len(patterns)} patterns)")
    
    # 4. Train and save model performance metrics
    print("\n5. Training classification models for metrics...")
    model_results = train_models(posts_df)
    joblib.dump(model_results, 'models/model_results.pkl')
    print(f"   ✓ Model results saved")
    
    # 5. Train and save the actual ML models
    print("\n6. Training ML models for classifier demo...")
    
    # Prepare data
    df = posts_df[posts_df['text'].notna() & (posts_df['text'].str.len() > 10)].copy()
    X_text = df['text'].fillna('')
    y = df['sentiment']
    
    # Vectorize
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    X = vectorizer.fit_transform(X_text)
    
    # Train models
    models = {}
    
    # Gaussian Naive Bayes
    print("   - Training Gaussian Naive Bayes...")
    gnb = GaussianNB()
    X_train_dense = X.toarray()
    gnb.fit(X_train_dense, y)
    models['Gaussian Naive Bayes'] = gnb
    
    # SVM
    print("   - Training SVM...")
    svm = SVC(kernel='linear', probability=True, random_state=42)
    svm.fit(X, y)
    models['SVM'] = svm
    
    # Decision Tree
    print("   - Training Decision Tree...")
    dt = DecisionTreeClassifier(random_state=42)
    dt.fit(X, y)
    models['Decision Tree'] = dt
    
    # Random Forest
    print("   - Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y)
    models['Random Forest'] = rf
    
    # Save
    joblib.dump(models, 'models/sentiment_models.pkl')
    joblib.dump(vectorizer, 'models/vectorizer.pkl')
    print("   ✓ ML models saved")
    
    # Show file sizes
    print("\n" + "=" * 60)
    print("ALL MODELS SAVED SUCCESSFULLY!")
    print("Files in 'models/' directory:")
    for f in os.listdir('models'):
        size = os.path.getsize(f'models/{f}') / 1024
        print(f"   - {f}: {size:.1f} KB")
    print("=" * 60)
    print("\n✅ You can now run your app - models will load instantly!")

if __name__ == "__main__":
    save_all_models()