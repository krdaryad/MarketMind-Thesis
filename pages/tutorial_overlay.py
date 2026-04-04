"""
Tutorial overlay that appears on each page with Next button.
"""
import streamlit as st

def get_tutorial_steps():
    """Define all tutorial steps with their target pages and elements."""
    return [
        {
            "id": 0,
            "title": "🎯 Welcome to MarketMind!",
            "message": "This tutorial will show you the key features. Click Next to begin.",
            "target_page": "Dashboard",
            "target_category": "Dashboard",
            "target_element": None,
            "highlight_text": None
        },
        {
            "id": 1,
            "title": "📊 Key Metrics",
            "message": "These cards show the most important metrics at a glance: total posts, companies mentioned, and engagement stats.",
            "target_page": "Dashboard",
            "target_category": "Dashboard",
            "target_element": "metric-cards",
            "highlight_text": "These cards show your key metrics"
        },
        {
            "id": 2,
            "title": "🏢 Company Statistics",
            "message": "See which companies are being discussed the most. The bar chart shows post volume by company.",
            "target_page": "Dashboard",
            "target_category": "Dashboard",
            "target_element": "company-stats",
            "highlight_text": "Top mentioned companies"
        },
        {
            "id": 3,
            "title": "📈 Sentiment Trends",
            "message": "Let's explore sentiment analysis. This chart shows how sentiment changes over time.",
            "target_page": "Sentiment Trends",
            "target_category": "Market Intelligence",
            "target_element": "sentiment-chart",
            "highlight_text": "Track sentiment over time"
        },
        {
            "id": 4,
            "title": "📉 VIX Correlation",
            "message": "See how sentiment relates to market fear (VIX). Higher fear often correlates with negative sentiment.",
            "target_page": "Sentiment Trends",
            "target_category": "Market Intelligence",
            "target_element": "vix-tab",
            "highlight_text": "Sentiment vs market fear"
        },
        {
            "id": 5,
            "title": "🤖 AI Analysis",
            "message": "Our AI models uncover hidden topics in discussions. LDA topic modeling finds key themes.",
            "target_page": "AI Analysis",
            "target_category": "AI Engine",
            "target_element": "topics-card",
            "highlight_text": "Discover hidden topics"
        },
        {
            "id": 6,
            "title": "🎯 Interactive Classifier",
            "message": "Test the sentiment classifier with your own text! Try different ML models.",
            "target_page": "Classifier Demo",
            "target_category": "AI Engine",
            "target_element": "classifier-input",
            "highlight_text": "Enter any text to see sentiment prediction"
        },
        {
            "id": 7,
            "title": "📚 Knowledge Base",
            "message": "Learn more with interactive courses, methodology explanations, and a comprehensive glossary.",
            "target_page": "Learning Hub",
            "target_category": "Knowledge Base",
            "target_element": "courses",
            "highlight_text": "Interactive courses"
        },
        {
            "id": 8,
            "title": "🎉 You're Ready!",
            "message": "You've completed the tour! Use the sidebar filters to explore data. Click the 🎓 button anytime to restart.",
            "target_page": "Dashboard",
            "target_category": "Dashboard",
            "target_element": None,
            "highlight_text": None
        }
    ]


def show_tutorial_overlay():
    """Display a tutorial overlay with Streamlit buttons (not HTML)."""
    
    # Only show if tutorial is active and not completed
    if not st.session_state.get('tutorial_active', False):
        return
    if st.session_state.get('tutorial_completed', False):
        return
    
    steps = get_tutorial_steps()
    current_step = st.session_state.get('tutorial_step', 0)
    
    if current_step >= len(steps):
        return
    
    step = steps[current_step]
    is_last_step = current_step == len(steps) - 1
    total_steps = len(steps)
    
    # Custom CSS for the overlay
    st.markdown("""
    <style>
    .tutorial-overlay-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        left: auto;
        width: 380px;
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .tutorial-card {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border: 1px solid #3B82F6;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
    }
    
    [data-theme="light"] .tutorial-card {
        background: linear-gradient(135deg, #FFFFFF, #F8FAFC);
        border: 1px solid #3B82F6;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
    }
    
    .tutorial-title {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #3B82F6;
    }
    
    .tutorial-message {
        font-size: 0.8rem;
        color: #8A8F99;
        margin-bottom: 1rem;
        line-height: 1.4;
    }
    
    .tutorial-progress {
        font-size: 0.7rem;
        color: #64748B;
        margin-bottom: 0.75rem;
    }
    
    .progress-bar-container {
        background: #1A1D24;
        border-radius: 10px;
        height: 4px;
        margin-bottom: 0.75rem;
        overflow: hidden;
    }
    
    .progress-bar-fill {
        background: linear-gradient(90deg, #3B82F6, #F59E0B);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    </style>
    
    <div class="tutorial-overlay-container">
        <div class="tutorial-card">
            <div class="tutorial-title">
                🎓 Tutorial Step {current_step + 1}/{total_steps}
            </div>
            <div class="tutorial-message">
                {step['message']}
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width: {((current_step + 1) / total_steps) * 100}%;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create the buttons using Streamlit (not HTML)
    # Use columns to position buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("❌ Skip", key="tutorial_skip_btn", use_container_width=True):
            st.session_state.tutorial_active = False
            st.session_state.tutorial_completed = True
            st.rerun()
    
    with col2:
        if st.button("← Prev", key="tutorial_prev_btn", use_container_width=True, disabled=(current_step == 0)):
            st.session_state.tutorial_step = current_step - 1
            # Navigate to previous step's page
            prev_step = steps[current_step - 1]
            if prev_step.get('target_page'):
                st.session_state.current_page = prev_step['target_page']
                if prev_step.get('target_category'):
                    st.session_state.current_category = prev_step['target_category']
                st.session_state.highlight_element = prev_step.get('target_element')
                st.session_state.highlight_text = prev_step.get('highlight_text')
            st.rerun()
    
    with col3:
        button_text = "Finish 🎉" if is_last_step else "Next →"
        if st.button(button_text, key="tutorial_next_btn", use_container_width=True, type="primary"):
            if is_last_step:
                # Complete tutorial
                st.session_state.tutorial_active = False
                st.session_state.tutorial_completed = True
                st.rerun()
            else:
                # Move to next step
                st.session_state.tutorial_step = current_step + 1
                # Navigate to next step's page
                next_step = steps[current_step + 1]
                if next_step.get('target_page'):
                    st.session_state.current_page = next_step['target_page']
                    if next_step.get('target_category'):
                        st.session_state.current_category = next_step['target_category']
                    st.session_state.highlight_element = next_step.get('target_element')
                    st.session_state.highlight_text = next_step.get('highlight_text')
                st.rerun()


def handle_tutorial_actions():
    """Handle tutorial actions (kept for compatibility)."""
    pass  # No longer needed as we use direct buttons


def apply_highlight(element_id, highlight_text):
    """Apply highlight to an element."""
    if element_id and highlight_text:
        # Show a toast notification
        st.toast(f"✨ {highlight_text}", icon="🎓")
        
        # Add CSS highlight
        st.markdown(f"""
        <style>
        @keyframes tutorial-pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(59,130,246,0.7); }}
            70% {{ box-shadow: 0 0 0 10px rgba(59,130,246,0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(59,130,246,0); }}
        }}
        [data-tutorial="{element_id}"] {{
            animation: tutorial-pulse 1s ease-out;
            border: 2px solid #3B82F6 !important;
            border-radius: 12px !important;
        }}
        </style>
        """, unsafe_allow_html=True)