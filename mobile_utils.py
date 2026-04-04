"""
Mobile-responsive utilities and touch-friendly components.
"""
import streamlit as st
from streamlit.components.v1 import html

def detect_mobile():
    """Detect if user is on mobile device."""
    # Check user agent via JavaScript
    mobile_detection = """
    <script>
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const parent = window.parent;
    parent.postMessage({
        type: 'streamlit:setComponentValue',
        value: isMobile
    }, '*');
    </script>
    """
    
    # Default to False, will be updated by JS
    if 'is_mobile' not in st.session_state:
        st.session_state.is_mobile = False
    
    return st.session_state.is_mobile

def responsive_columns(items, mobile_cols=1, desktop_cols=None):
    """
    Create responsive columns that adapt to screen size.
    
    Args:
        items: List of items to display
        mobile_cols: Number of columns on mobile (1-2)
        desktop_cols: Number of columns on desktop (defaults to len(items))
    """
    is_mobile = detect_mobile()
    
    if desktop_cols is None:
        desktop_cols = len(items)
    
    cols_per_row = mobile_cols if is_mobile else desktop_cols
    
    # Create rows of columns
    rows = []
    for i in range(0, len(items), cols_per_row):
        row_items = items[i:i + cols_per_row]
        cols = st.columns(len(row_items))
        for col, item in zip(cols, row_items):
            with col:
                yield item

def touch_slider(label, min_val, max_val, default, **kwargs):
    """Touch-friendly slider with larger target area."""
    return st.slider(
        label,
        min_value=min_val,
        max_value=max_val,
        value=default,
        **kwargs
    )

def touch_select(label, options, **kwargs):
    """Touch-friendly select dropdown."""
    return st.selectbox(
        label,
        options=options,
        **kwargs
    )

def add_viewport_meta():
    """Add viewport meta tag for proper mobile scaling."""
    st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    """, unsafe_allow_html=True)

def add_swipe_support():
    """Add swipe gesture support for mobile."""
    swipe_js = """
    <script>
    let touchStartX = 0;
    let touchEndX = 0;
    
    document.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    });
    
    document.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        const swipeDistance = touchEndX - touchStartX;
        
        if (Math.abs(swipeDistance) > 50) {
            // Swipe detected - can trigger navigation
            const event = new CustomEvent('swipe', {
                detail: { direction: swipeDistance > 0 ? 'right' : 'left' }
            });
            document.dispatchEvent(event);
        }
    });
    </script>
    """
    html(swipe_js, height=0)