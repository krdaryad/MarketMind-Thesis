"""
Inference Performance Benchmark for MarketMind Thesis
Run this script to generate Tables 4.4 and 4.5 for your thesis
"""

import time
import numpy as np
import pandas as pd
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from data_fetcher import load_reddit_data, add_sentiment

def run_inference_benchmark():
    """Run complete inference benchmark and save results."""
    
    print("=" * 60)
    print("MARKETMIND INFERENCE PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    # 1. Load data
    print("\n[1/5] Loading Reddit data...")
    posts_df = load_reddit_data()
    
    if posts_df.empty:
        print("ERROR: No data loaded. Check your CSV file path.")
        return
    
    # Add sentiment if not present
    if 'sentiment' not in posts_df.columns:
        print("[2/5] Adding sentiment labels...")
        posts_df = add_sentiment(posts_df)
    
    print(f"      Loaded {len(posts_df)} posts with sentiment labels")
    
    # 2. Vectorize text
    print("[3/5] Creating TF-IDF features...")
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    X = vectorizer.fit_transform(posts_df['text'].fillna(''))
    y = posts_df['sentiment']
    print(f"      Feature matrix shape: {X.shape}")
    
    # 3. Train models (or load pre-trained)
    print("[4/5] Training/loading models...")
    
    from sklearn.naive_bayes import GaussianNB
    from sklearn.svm import SVC
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    
    models = {}
    
    # Gaussian Naive Bayes
    print("      - Training Gaussian Naive Bayes...")
    gnb = GaussianNB()
    X_dense = X.toarray()
    gnb.fit(X_dense, y)
    models['Gaussian Naive Bayes'] = gnb
    
    # SVM
    print("      - Training SVM (may take 1-2 minutes)...")
    svm = SVC(kernel='linear', probability=True, random_state=42)
    svm.fit(X, y)
    models['SVM'] = svm
    
    # Decision Tree
    print("      - Training Decision Tree...")
    dt = DecisionTreeClassifier(max_depth=20, random_state=42)
    dt.fit(X, y)
    models['Decision Tree'] = dt
    
    # Random Forest
    print("      - Training Random Forest (may take 2-3 minutes)...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y)
    models['Random Forest'] = rf
    
    print("      All models trained successfully")
    
    # 4. Run inference benchmark
    print("[5/5] Running inference benchmarks...")
    
    batch_sizes = [1, 10, 50, 100, 250, 500]
    n_iterations = 20  # Number of times to repeat each test
    
    results = []
    
    for batch_size in batch_sizes:
        print(f"\n      Testing batch size: {batch_size}")
        
        for model_name, model in models.items():
            print(f"        - {model_name}...", end="", flush=True)
            
            times = []
            
            for iteration in range(n_iterations):
                # Randomly sample posts
                indices = np.random.choice(X.shape[0], batch_size, replace=False)
                X_batch = X[indices]
                
                # Measure inference time with nanosecond precision
                start = time.perf_counter_ns()
                
                if model_name == 'Gaussian Naive Bayes':
                    y_pred = model.predict(X_batch.toarray())
                else:
                    y_pred = model.predict(X_batch)
                
                end = time.perf_counter_ns()
                
                # Convert to milliseconds
                elapsed_ms = (end - start) / 1_000_000
                times.append(elapsed_ms)
            
            # Remove outliers using IQR method
            q1, q3 = np.percentile(times, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            filtered_times = [t for t in times if lower_bound <= t <= upper_bound]
            
            mean_ms = np.mean(filtered_times)
            std_ms = np.std(filtered_times)
            p95_ms = np.percentile(filtered_times, 95)
            p99_ms = np.percentile(filtered_times, 99)
            
            results.append({
                'model': model_name,
                'batch_size': batch_size,
                'mean_inference_ms': round(mean_ms, 1),
                'std_dev_ms': round(std_ms, 2),
                'p95_ms': round(p95_ms, 1),
                'p99_ms': round(p99_ms, 1),
                'iterations': len(filtered_times)
            })
            
            print(f" {round(mean_ms, 1)} ms")
    
    # 5. Create DataFrames and save results
    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE - SAVING RESULTS")
    print("=" * 60)
    
    df_results = pd.DataFrame(results)
    
    # Create Table 4.4 (Batch size comparison)
    table_44 = df_results.pivot(index='batch_size', columns='model', values='mean_inference_ms')
    table_44.to_csv('table_44_batch_inference.csv')
    print("\n✓ Table 4.4 saved to: table_44_batch_inference.csv")
    print("\n" + table_44.round(1).to_string())
    
    # Create Table 4.5 (Per-post statistics)
    per_post = []
    for model_name in models.keys():
        model_data = df_results[df_results['model'] == model_name]
        mean_per_post = (model_data['mean_inference_ms'] / model_data['batch_size']).mean()
        std_per_post = (model_data['std_dev_ms'] / model_data['batch_size']).mean()
        p95_per_post = (model_data['p95_ms'] / model_data['batch_size']).mean()
        p99_per_post = (model_data['p99_ms'] / model_data['batch_size']).mean()
        
        per_post.append({
            'model': model_name,
            'mean_ms_per_post': round(mean_per_post, 2),
            'std_dev_ms': round(std_per_post, 3),
            'p95_ms': round(p95_per_post, 2),
            'p99_ms': round(p99_per_post, 2)
        })
    
    table_45 = pd.DataFrame(per_post)
    table_45.to_csv('table_45_per_post_inference.csv', index=False)
    print("\n✓ Table 4.5 saved to: table_45_per_post_inference.csv")
    print("\n" + table_45.to_string())
    
    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE!")
    print("Results saved to CSV files for your thesis.")
    print("=" * 60)

if __name__ == "__main__":
    run_inference_benchmark()