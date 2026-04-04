import streamlit as st

def learning_hub_page():
    # 1. INITIALIZE SESSION STATE
    if "completed_lessons" not in st.session_state:
        st.session_state.completed_lessons = set()
    
    # Check current theme (Assumes you have a 'dark_mode' toggle in session_state)
    is_dark = st.session_state.get("dark_mode", True)

    # 2. DATASET (Preserved exactly)
    modules = [
        {
            "id": "foundations",
            "title": "Sentiment Analysis Foundations",
            "lessons": [
                {
                    "id": "f1",
                    "title": "What Is Sentiment Analysis?",
                    "duration": "5 min",
                    "content": """Sentiment analysis (or opinion mining) is the computational study of people's opinions, sentiments, and emotions expressed in text. In financial markets, it involves extracting bullish or bearish signals from news, social media, and analyst reports.

**The three main approaches are:**
• Rule-based: Uses lexicons (word lists) with predefined sentiment scores
• Machine Learning: Trains classifiers on labeled data
• Hybrid: Combines both for better accuracy""",
                    "key_takeaway": "Sentiment analysis converts unstructured text into actionable trading signals.",
                    "quiz": {
                        "question": "Which approach uses predefined word lists with sentiment scores?",
                        "options": ["Machine Learning", "Rule-based", "Deep Learning", "Reinforcement Learning"],
                        "correct_index": 1,
                        "explanation": "Rule-based approaches like VADER use curated lexicons where each word has a predefined sentiment score."
                    }
                },
                {
                    "id": "f2",
                    "title": "TF-IDF: Turning Text into Numbers",
                    "duration": "7 min",
                    "content": """Machines need numerical representations. TF-IDF (Term Frequency–Inverse Document Frequency) is the most common method.

• Term Frequency (TF): How often a word appears in a document
• Inverse Document Frequency (IDF): Penalizes words that appear in many documents""",
                    "key_takeaway": "TF-IDF gives high scores to words that are frequent in a document but rare across the corpus.",
                    "quiz": {
                        "question": "A word that appears in almost every document will have:",
                        "options": ["High TF-IDF", "Low IDF", "High IDF", "No TF score"],
                        "correct_index": 1,
                        "explanation": "When a word appears in most documents, IDF approaches 0."
                    }
                },
                {
                    "id": "f3",
                    "title": "Understanding Sentiment Polarity",
                    "duration": "4 min",
                    "content": """Sentiment polarity measures the degree of positivity or negativity in text, typically on a scale from -1 to +1.

**Classification thresholds:**
• Compound >= 0.05 -> Bullish
• Compound <= -0.05 -> Bearish""",
                    "key_takeaway": "VADER's compound score aggregates individual word sentiments into a single polarity value."
                }
            ]
        }
    ]

    # 3. HEADER & PROGRESS
    st.title("Learning Hub")
    
    all_lesson_ids = [l["id"] for m in modules for l in m["lessons"]]
    total_count = len(all_lesson_ids)
    completed_count = len(st.session_state.completed_lessons)
    
    progress_val = completed_count / total_count if total_count > 0 else 0
    st.progress(progress_val)
    st.caption(f"Course Progress: {completed_count} of {total_count} lessons completed")
    st.divider()

    # 4. TABBED NAVIGATION
    module_titles = [m["title"] for m in modules]
    module_tabs = st.tabs(module_titles)

    for i, tab in enumerate(module_tabs):
        with tab:
            current_module = modules[i]
            lesson_titles = [l["title"] for l in current_module["lessons"]]
            
            selected_lesson_name = st.selectbox(
                "Select Lesson", 
                lesson_titles, 
                key=f"select_{current_module['id']}"
            )
            
            lesson = next(l for l in current_module["lessons"] if l["title"] == selected_lesson_name)
            
            # Content Rendering - Using border=True ensures card visibility in Light Mode
            st.subheader(lesson["title"])
            st.caption(f"Estimated reading time: {lesson['duration']}")
            
            with st.container(border=True):
                # We use standard markdown to allow the theme-based text color to take over
                st.markdown(lesson["content"])
            
            # Use st.info for the Takeaway so it gets a theme-compatible blue background
            st.info(f"**Key Takeaway**: {lesson['key_takeaway']}")

            # 5. QUIZ LOGIC
            if "quiz" in lesson:
                st.write("---")
                quiz = lesson["quiz"]
                
                if lesson["id"] in st.session_state.completed_lessons:
                    st.success("Knowledge check completed for this lesson.")
                
                # The form will now respect the Light Mode background for inputs
                with st.form(key=f"form_{lesson['id']}"):
                    choice = st.radio(quiz["question"], quiz["options"])
                    submitted = st.form_submit_button("Submit Answer")
                    
                    if submitted:
                        if quiz["options"].index(choice) == quiz["correct_index"]:
                            st.session_state.completed_lessons.add(lesson["id"])
                            st.success(f"Correct! {quiz['explanation']}")
                            # Balloon effect works well in both modes
                            st.balloons()
                        else:
                            st.error(f"Not quite. {quiz['explanation']}")

if __name__ == "__main__":
    learning_hub_page()
