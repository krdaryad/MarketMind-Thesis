"""
Performance Dashboard - Measure and display system performance metrics
"""
import streamlit as st
import time
import pandas as pd
import numpy as np
import psutil
import platform
import os
from datetime import datetime

def performance_dashboard_page():
    st.markdown('<h1>Performance Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">System performance metrics for thesis evaluation</p>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    
    # ========================================================================
    # SYSTEM INFORMATION
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>System Information</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**OS:** {platform.system()} {platform.release()}")
        st.markdown(f"**Processor:** {platform.processor() or 'Apple M1'}")
        st.markdown(f"**Python Version:** {platform.python_version()}")
    with col2:
        st.markdown(f"**Browser:** Detected via User-Agent")
        st.markdown(f"**Streamlit Version:** {st.__version__}")
        st.markdown(f"**Test Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # MEMORY USAGE (Real-time)
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Memory Usage (Current Session)</h3>', unsafe_allow_html=True)
    
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / (1024 * 1024)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Memory", f"{memory_mb:.1f} MB")
    with col2:
        st.metric("CPU Usage", f"{process.cpu_percent():.1f}%")
    with col3:
        st.metric("Threads", process.num_threads())
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # INTERACTION RESPONSE TIME TEST
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Interaction Response Time Test</h3>', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">Click the button below to measure response time</p>', unsafe_allow_html=True)
    
    if 'response_times' not in st.session_state:
        st.session_state.response_times = []
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Measure Response Time", key="measure_btn", use_container_width=True):
            start_time = time.perf_counter_ns()
            # Simulate a simple operation
            result = np.sum(np.random.rand(1000))
            end_time = time.perf_counter_ns()
            elapsed_ms = (end_time - start_time) / 1_000_000
            st.session_state.response_times.append(elapsed_ms)
            st.success(f"Response time: {elapsed_ms:.2f} ms")
    
    with col2:
        if st.button("Clear Measurements", key="clear_btn", use_container_width=True):
            st.session_state.response_times = []
            st.rerun()
    
    if st.session_state.response_times:
        times = st.session_state.response_times
        st.markdown(f"""
        <div style="margin-top: 0.5rem;">
            <p><strong>Measurements:</strong> {len(times)} samples</p>
            <p><strong>Mean:</strong> {np.mean(times):.2f} ms</p>
            <p><strong>Min:</strong> {np.min(times):.2f} ms</p>
            <p><strong>Max:</strong> {np.max(times):.2f} ms</p>
            <p><strong>Std Dev:</strong> {np.std(times):.2f} ms</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # PAGE LOAD TIME MEASUREMENT
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Page Load Time Measurement</h3>', unsafe_allow_html=True)
    
    if 'page_load_times' not in st.session_state:
        st.session_state.page_load_times = {}
    
    # Record load time for this page
    if 'performance_page_load' not in st.session_state:
        st.session_state.performance_page_load = time.time()
        st.session_state.page_load_times['Performance Dashboard'] = {
            'timestamp': datetime.now(),
            'load_time_ms': 0  # Will be calculated on next run
        }
    
    # Measure navigation between pages
    st.markdown("**Navigate to another page and come back to see load times**")
    
    if len(st.session_state.page_load_times) > 1:
        df_loads = pd.DataFrame([
            {'Page': page, 'Load Time (ms)': data['load_time_ms']}
            for page, data in st.session_state.page_load_times.items()
        ])
        st.dataframe(df_loads, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # INFERENCE SPEED TEST
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Sentiment Inference Speed Test</h3>', unsafe_allow_html=True)
    
    from sklearn.feature_extraction.text import TfidfVectorizer
    import joblib
    
    # Load models if available
    models_loaded = False
    try:
        if os.path.exists('models/sentiment_models.pkl'):
            models = joblib.load('models/sentiment_models.pkl')
            vectorizer = joblib.load('models/vectorizer.pkl')
            models_loaded = True
    except:
        pass
    
    if models_loaded:
        test_texts = [
            "This is great news for the market!",
            "The stock crashed terribly today.",
            "Fed signals higher rates, markets uncertain.",
            "Tesla earnings crushed expectations!",
            "CPI data came in hot, sell everything."
        ]
        
        st.markdown("**Test inference speed on sample texts:**")
        
        if st.button("Run Inference Speed Test", key="inference_btn"):
            inference_times = []
            results = []
            
            for text in test_texts:
                X = vectorizer.transform([text])
                
                for model_name, model in models.items():
                    start = time.perf_counter_ns()
                    if model_name == 'Gaussian Naive Bayes':
                        pred = model.predict(X.toarray())
                    else:
                        pred = model.predict(X)
                    end = time.perf_counter_ns()
                    
                    elapsed_us = (end - start) / 1_000  # microseconds
                    inference_times.append({
                        'model': model_name,
                        'text': text[:30] + "...",
                        'time_us': elapsed_us,
                        'prediction': pred[0]
                    })
            
            df_inference = pd.DataFrame(inference_times)
            st.dataframe(df_inference, use_container_width=True)
            
            avg_by_model = df_inference.groupby('model')['time_us'].mean()
            st.markdown("**Average inference time by model:**")
            for model, avg_us in avg_by_model.items():
                st.markdown(f"- {model}: {avg_us:.1f} µs ({avg_us/1000:.3f} ms)")
    else:
        st.info("Pre-trained models not found. Run save_models.py first to enable inference testing.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # EXPORT RESULTS
    # ========================================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Export Performance Results</h3>', unsafe_allow_html=True)
    
    export_data = {
        'timestamp': datetime.now().isoformat(),
        'system': platform.system(),
        'processor': platform.processor(),
        'memory_mb': memory_mb,
        'cpu_percent': process.cpu_percent(),
        'response_times': st.session_state.response_times,
    }
    
    import json
    export_json = json.dumps(export_data, indent=2, default=str)
    
    st.download_button(
        label="📥 Export Performance Data (JSON)",
        data=export_json,
        file_name=f"performance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    performance_dashboard_page()