"""
Loading screen component with progress indicators.
"""
import streamlit as st
import time

def show_loading_screen():
    """Display a loading animation using Streamlit native elements."""
    
    # Create a placeholder for the entire loading screen
    loading_placeholder = st.empty()
    
    with loading_placeholder.container():
        # Use columns for centering
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Title with emoji
            st.markdown("""
            <div style="text-align: center;">
                <h1 style="font-size: 3rem; margin-bottom: 0;">🚀</h1>
                <h1 style="background: linear-gradient(135deg, #3B82F6, #F59E0B); 
                           -webkit-background-clip: text; 
                           -webkit-text-fill-color: transparent;
                           font-size: 2rem;
                           margin-bottom: 2rem;">
                    MarketMind
                </h1>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress bar
            progress_bar = st.progress(0)
            
            # Status text
            status_text = st.empty()
            status_text.markdown("#### ⏳ Initializing...")
            
            # Steps as separate containers
            st.markdown("### Loading Progress")
            
            step1_container = st.container()
            step2_container = st.container()
            step3_container = st.container()
            step4_container = st.container()
            step5_container = st.container()
            
            with step1_container:
                st.info("⭘ Loading Reddit data...")
            with step2_container:
                st.info("⭘ Loading economic indicators...")
            with step3_container:
                st.info("⭘ Fetching market data...")
            with step4_container:
                st.info("⭘ Processing sentiment analysis...")
            with step5_container:
                st.info("⭘ Training ML models...")
    
    return loading_placeholder, progress_bar, status_text, [step1_container, step2_container, step3_container, step4_container, step5_container]

def update_loading(placeholder, progress_bar, status_text, steps, progress, step_index=None, status=None):
    """Update the loading screen with progress."""
    
    # Update progress bar
    progress_bar.progress(progress)
    
    # Update status text
    if status:
        status_text.markdown(f"#### {status}")
    
    # Update step if provided - use a completely fresh container
    if step_index is not None and step_index < len(steps):
        # Clear the container by replacing its content
        with steps[step_index]:
            st.success(f"✅ {status.split('✅ ')[-1] if status and '✅' in status else 'Step completed'}")
    
    time.sleep(0.1)

def hide_loading_screen(placeholder, progress_bar, status_text, steps):
    """Hide the loading screen completely."""
    placeholder.empty()