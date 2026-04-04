"""
Educational Tooltip Helper Module
"""

import streamlit as st
from modules.glossary_data import get_glossary

def tooltip(term):
    """Return a clickable educational popup for a term"""
    glossary = get_glossary()
    term_data = next((t for t in glossary if t["term"].lower() == term.lower()), None)
    
    if term_data:
        with st.popover("🎓", use_container_width=False):
            st.markdown(f"**{term_data['term']}**")
            st.markdown(term_data['definition'])
            if term_data.get('formula'):
                st.markdown(f"**Formula:** `{term_data['formula']}`")
            if term_data.get('related'):
                st.markdown(f"**Related:** {', '.join(term_data['related'])}")
    else:
        st.markdown(f"<span class='education-icon' title='No info yet'>🎓</span>", unsafe_allow_html=True)