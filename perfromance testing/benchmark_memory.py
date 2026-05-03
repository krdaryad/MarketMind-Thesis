"""
Memory Usage Benchmark for MarketMind Thesis
Run this to measure memory consumption of different components
"""

import psutil
import os
import time
import pandas as pd
import tracemalloc

def measure_memory_usage(func, *args, **kwargs):
    """Measure peak memory usage of a function."""
    tracemalloc.start()
    
    # Get baseline
    baseline = tracemalloc.get_traced_memory()[1]
    
    # Run function
    result = func(*args, **kwargs)
    
    # Get peak
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    memory_mb = (peak - baseline) / (1024 * 1024)
    
    return result, memory_mb

def memory_benchmark():
    """Run comprehensive memory benchmark."""
    
    print("=" * 60)
    print("MARKETMIND MEMORY USAGE BENCHMARK")
    print("=" * 60)
    
    results = []
    
    # 1. Baseline memory (after imports)
    process = psutil.Process(os.getpid())
    baseline_mb = process.memory_info().rss / (1024 * 1024)
    print(f"\nBaseline memory (after imports): {baseline_mb:.1f} MB")
    results.append({'component': 'Baseline (imports)', 'memory_mb': round(baseline_mb, 1)})
    
    # 2. Load Reddit data
    from data_fetcher import load_reddit_data
    print("\nLoading Reddit data...")
    start_mem = process.memory_info().rss / (1024 * 1024)
    posts_df = load_reddit_data()
    end_mem = process.memory_info().rss / (1024 * 1024)
    print(f"  Memory increase: {end_mem - start_mem:.1f} MB")
    results.append({'component': 'Reddit DataFrame', 'memory_mb': round(end_mem - start_mem, 1)})
    
    # 3. Add sentiment
    from data_fetcher import add_sentiment
    print("\nAdding sentiment analysis...")
    start_mem = process.memory_info().rss / (1024 * 1024)
    posts_with_sentiment = add_sentiment(posts_df)
    end_mem = process.memory_info().rss / (1024 * 1024)
    print(f"  Memory increase: {end_mem - start_mem:.1f} MB")
    results.append({'component': 'Sentiment Analysis', 'memory_mb': round(end_mem - start_mem, 1)})
    
    # 4. Load ML models
    print("\nLoading pre-trained models...")
    start_mem = process.memory_info().rss / (1024 * 1024)
    import joblib
    models = joblib.load('models/sentiment_models.pkl')
    end_mem = process.memory_info().rss / (1024 * 1024)
    print(f"  Memory increase: {end_mem - start_mem:.1f} MB")
    results.append({'component': 'ML Models (4 classifiers)', 'memory_mb': round(end_mem - start_mem, 1)})
    
    # 5. Load vectorizer
    print("\nLoading TF-IDF vectorizer...")
    start_mem = process.memory_info().rss / (1024 * 1024)
    vectorizer = joblib.load('models/vectorizer.pkl')
    end_mem = process.memory_info().rss / (1024 * 1024)
    print(f"  Memory increase: {end_mem - start_mem:.1f} MB")
    results.append({'component': 'TF-IDF Vectorizer', 'memory_mb': round(end_mem - start_mem, 1)})
    
    # 6. Create feature matrix
    print("\nCreating TF-IDF feature matrix...")
    start_mem = process.memory_info().rss / (1024 * 1024)
    X = vectorizer.transform(posts_with_sentiment['text'].fillna(''))
    end_mem = process.memory_info().rss / (1024 * 1024)
    print(f"  Memory increase: {end_mem - start_mem:.1f} MB")
    results.append({'component': 'TF-IDF Matrix (sparse)', 'memory_mb': round(end_mem - start_mem, 1)})
    
    # 7. Total memory
    total_mb = process.memory_info().rss / (1024 * 1024)
    print(f"\nTotal memory usage: {total_mb:.1f} MB")
    results.append({'component': 'TOTAL', 'memory_mb': round(total_mb, 1)})
    
    # Save results
    df = pd.DataFrame(results)
    df.to_csv('memory_benchmark.csv', index=False)
    print("\n✓ Results saved to: memory_benchmark.csv")
    print("\n" + df.to_string())
    
    return df

if __name__ == "__main__":
    # Install psutil if not already installed
    try:
        import psutil
    except ImportError:
        print("Installing psutil...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'psutil'])
        import psutil
    
    memory_benchmark()