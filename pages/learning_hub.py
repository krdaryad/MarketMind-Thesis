import streamlit as st
import datetime 
import pandas as pd
# 1. PERFORMANCE: Use @st.cache_data
@st.cache_data
def get_course_data():
    return [
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
                    "key_takeaway": "VADER's compound score aggregates individual word sentiments into a single polarity value.",
                    "quiz": {
                        "question": "What compound score would classify text as 'Bullish' according to VADER?",
                        "options": ["<= -0.05", ">= 0.05", "= 0", ">= 0.5"],
                        "correct_index": 1,
                        "explanation": "VADER classifies text as Bullish when the compound score is >= 0.05."
                    }
                }
            ]
        },
        {
            "id": "advanced",
            "title": "Advanced Sentiment Techniques",
            "lessons": [
                {
                    "id": "a1",
                    "title": "VADER: Lexicon-Based Sentiment",
                    "duration": "8 min",
                    "content": """VADER (Valence Aware Dictionary and sEntiment Reasoner) is specifically attuned to sentiments expressed in social media.

**Key features:**
• Handles emojis, capitalization, and punctuation
• Boosts intensity with exclamation marks
• Amplifies sentiment with ALL CAPS words
• Recognizes degree modifiers (e.g., 'very good' vs 'good')""",
                    "key_takeaway": "VADER excels at social media text because it accounts for typographical emphasis and slang.",
                    "quiz": {
                        "question": "Which feature makes VADER particularly good for social media analysis?",
                        "options": ["Only works with formal text", "Handles capitalization and punctuation", "Requires labeled training data", "Ignores text formatting"],
                        "correct_index": 1,
                        "explanation": "VADER's ability to handle ALL CAPS, punctuation, and degree modifiers makes it ideal for social media content."
                    }
                },
                {
                    "id": "a2",
                    "title": "Transformers & BERT",
                    "duration": "10 min",
                    "content": """Modern sentiment analysis uses Transformer-based models like BERT (Bidirectional Encoder Representations from Transformers).

**Advantages over traditional methods:**
• Understands context (e.g., 'not good' vs 'good')
• Captures long-range dependencies
• Pre-trained on massive text corpora
• Can be fine-tuned for specific domains (finance, healthcare)""",
                    "key_takeaway": "Transformers understand word context bidirectionally, solving the 'not good' problem that lexicon-based methods struggle with.",
                    "quiz": {
                        "question": "What key advantage do Transformers have over lexicon-based sentiment analysis?",
                        "options": ["They are faster to run", "They understand context and negation", "They require no training data", "They only work with numbers"],
                        "correct_index": 1,
                        "explanation": "Transformers understand contextual relationships, including negations like 'not good', which lexicon-based methods often miss."
                    }
                },
                {
                    "id": "a3",
                    "title": "Financial Sentiment Analysis",
                    "duration": "6 min",
                    "content": """Financial sentiment analysis requires domain-specific models due to unique terminology.

**Challenges:**
• 'Bull' and 'bear' have special meanings
• Numbers and percentages are critical
• Need to understand market context
• Avoiding false signals from noise

**Best practices:**
• Use finance-specific models (FinBERT)
• Combine with technical indicators
• Backtest strategies before deployment""",
                    "key_takeaway": "General sentiment models often fail in finance; domain-specific models like FinBERT significantly outperform generic approaches.",
                    "quiz": {
                        "question": "Why might a general sentiment model perform poorly on financial text?",
                        "options": ["Financial text has domain-specific terms like 'bull' and 'bear'", "Financial text is too short", "Sentiment doesn't matter in finance", "General models are too slow"],
                        "correct_index": 0,
                        "explanation": "Financial text contains domain-specific terminology (bull, bear, long, short) that general models aren't trained to interpret correctly."
                    }
                }
            ]
        },
        {
            "id": "practical",
            "title": "Practical Implementation",
            "lessons": [
                {
                    "id": "p1",
                    "title": "Building a Sentiment Pipeline",
                    "duration": "12 min",
                    "content": """A complete sentiment analysis pipeline includes:

**1. Data Collection**
• News APIs (Bloomberg, Reuters)
• Twitter/Facebook APIs
• Reddit (r/wallstreetbets)

**2. Preprocessing**
• Remove noise (URLs, mentions)
• Handle special characters
• Normalize text (lowercase, stemming)

**3. Sentiment Scoring**
• Apply VADER or FinBERT
• Generate polarity scores

**4. Signal Generation**
• Aggregate scores over time windows
• Set thresholds for trading signals
• Combine with price action""",
                    "key_takeaway": "A robust sentiment pipeline requires careful preprocessing and multiple validation steps before generating trading signals.",
                    "quiz": {
                        "question": "What is the correct order of steps in a sentiment analysis pipeline?",
                        "options": ["Signal Generation → Scoring → Preprocessing → Collection", "Collection → Preprocessing → Scoring → Signal Generation", "Scoring → Collection → Preprocessing → Signal Generation", "Preprocessing → Collection → Scoring → Signal Generation"],
                        "correct_index": 1,
                        "explanation": "The logical flow is: collect raw data, preprocess it, apply sentiment scoring, then generate trading signals from the results."
                    }
                },
                {
                    "id": "p2",
                    "title": "Backtesting Sentiment Strategies",
                    "duration": "10 min",
                    "content": """Backtesting ensures your sentiment strategy works before risking real capital.

**Key metrics to track:**
• Sharpe Ratio (risk-adjusted returns)
• Maximum Drawdown
• Win Rate & Profit Factor
• Correlation with market benchmarks

**Common pitfalls:**
• Look-ahead bias (using future data)
• Survivorship bias (ignoring failed companies)
• Overfitting to historical patterns

**Validation approach:**
• Train on 2018-2021 data
• Validate on 2022 data
• Test on 2023-2024 out-of-sample data""",
                    "key_takeaway": "Always backtest sentiment strategies with strict out-of-sample validation to avoid overfitting.",
                    "quiz": {
                        "question": "What is 'look-ahead bias' in backtesting?",
                        "options": ["Testing on future data", "Using only successful companies", "Ignoring transaction costs", "Using too much historical data"],
                        "correct_index": 0,
                        "explanation": "Look-ahead bias occurs when your backtest accidentally uses information that wouldn't have been available at the trading time."
                    }
                },
                {
                    "id": "p3",
                    "title": "Risk Management for Sentiment Trading",
                    "duration": "8 min",
                    "content": """Sentiment signals are probabilistic, not guaranteed.

**Essential risk controls:**
• Position sizing (never risk >2% per trade)
• Stop-losses (even with strong sentiment)
• Sentiment confirmation (require multiple sources)
• Sentiment reversal detection

**Red flags to avoid:**
• Trading against strong technical trends
• Ignoring market-wide sentiment shifts
• Overleveraging based on one signal

**Best practice:** Use sentiment as one of several signals (price, volume, fundamentals) before entering trades.""",
                    "key_takeaway": "Sentiment analysis is a probabilistic tool; always combine with strict risk management rules.",
                    "quiz": {
                        "question": "What's the recommended maximum risk per trade when using sentiment signals?",
                        "options": ["10%", "5%", "2%", "15%"],
                        "correct_index": 2,
                        "explanation": "Professional traders typically risk no more than 1-2% of capital per trade, regardless of signal strength."
                    }
                }
            ]
        }
    ]

def learning_hub_page():
    # 1. INITIALIZE SESSION STATE
    if "completed_lessons" not in st.session_state:
        st.session_state.completed_lessons = set()
    
    if "current_module_idx" not in st.session_state:
        st.session_state.current_module_idx = 0
    
    if "current_lesson_idx" not in st.session_state:
        st.session_state.current_lesson_idx = 0
    
    if "show_congrats" not in st.session_state:
        st.session_state.show_congrats = False
    
    # Load cached data
    modules = get_course_data()
    
    # 2. HEADER & PROGRESS
    st.title("Learning Hub")
    
    all_lesson_ids = [l["id"] for m in modules for l in m["lessons"]]
    total_count = len(all_lesson_ids)
    completed_count = len(st.session_state.completed_lessons)
    
    progress_val = completed_count / total_count if total_count > 0 else 0
    st.progress(progress_val)
    
    # Progress metrics without emojis
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Lessons", total_count)
    with col2:
        st.metric("Completed", completed_count)
    with col3:
        st.metric("Progress", f"{int(progress_val * 100)}%")
    
    # Show congratulations when all lessons are completed
    if completed_count == total_count and total_count > 0:
        if not st.session_state.show_congrats:
            st.session_state.show_congrats = True
            st.balloons()
            st.success("🎉 Congratulations! You've completed the entire course! 🎉")
        else:
            st.success("🎉 Congratulations! You've completed the entire course! 🎉")
    else:
        st.session_state.show_congrats = False
    
    st.divider()
    
    # 3. MODULE SWITCHER - Stylish buttons
    st.subheader("Course Modules")
    
    # Create styled module buttons
    module_cols = st.columns(len(modules))
    for idx, module in enumerate(modules):
        with module_cols[idx]:
            # Determine button style based on active module
            is_active = (idx == st.session_state.current_module_idx)
            
            # Use different button types for visual distinction
            if is_active:
                st.button(
                    module["title"],
                    key=f"module_{idx}",
                    use_container_width=True,
                    type="primary"  # Primary button for active module
                )
            else:
                if st.button(
                    module["title"],
                    key=f"module_{idx}",
                    use_container_width=True,
                    type="secondary"  # Secondary button for inactive modules
                ):
                    st.session_state.current_module_idx = idx
                    st.session_state.current_lesson_idx = 0  # Reset to first lesson of new module
                    st.rerun()
    
    st.divider()
    
    # 5. MAIN CONTENT AREA
    current_module = modules[st.session_state.current_module_idx]
    current_lesson = current_module["lessons"][st.session_state.current_lesson_idx]
    
    # Module and lesson navigation indicators
    st.caption(f"Module {st.session_state.current_module_idx + 1} of {len(modules)}")
    st.subheader(current_lesson['title'])
    st.caption(f"Estimated reading time: {current_lesson['duration']}")
    
    # Lesson content with border
    with st.container(border=True):
        st.markdown(current_lesson["content"])
    
    # Key takeaway with subtle styling
    st.markdown(f"**Key Takeaway:** {current_lesson['key_takeaway']}")
    
    # 6. QUIZ SECTION
    if "quiz" in current_lesson:
        with st.expander("Test Your Knowledge", expanded=True):
            quiz = current_lesson["quiz"]
            
            # Check if already completed
            lesson_completed = current_lesson["id"] in st.session_state.completed_lessons
            
            if lesson_completed:
                st.success(" You've completed this lesson's knowledge check.")
            
            # Quiz form
            with st.form(key=f"form_{current_lesson['id']}"):
                choice = st.radio(quiz["question"], quiz["options"])
                submitted = st.form_submit_button("Submit Answer", disabled=lesson_completed)
                
                if submitted:
                    if quiz["options"].index(choice) == quiz["correct_index"]:
                        st.session_state.completed_lessons.add(current_lesson["id"])
                        st.success(f"✓ Correct! {quiz['explanation']}")
                        st.balloons()
                        # Force rerun to update progress
                        st.rerun()
                    else:
                        st.error(f"✗ Not quite. {quiz['explanation']}")
                        st.info(" Hint: Review the lesson content above and try again.")
    
    # 7. NAVIGATION BUTTONS
    st.divider()
    
    col_left, col_center, col_right = st.columns([1, 1, 1])
    
    # Previous lesson button
    with col_left:
        if st.session_state.current_lesson_idx > 0:
            if st.button("← Previous Lesson", use_container_width=True):
                st.session_state.current_lesson_idx -= 1
                st.rerun()
        elif st.session_state.current_module_idx > 0:
            if st.button("← Previous Module", use_container_width=True):
                st.session_state.current_module_idx -= 1
                st.session_state.current_lesson_idx = len(modules[st.session_state.current_module_idx]["lessons"]) - 1
                st.rerun()
    
    # Current position indicator
    with col_center:
        lesson_num = st.session_state.current_lesson_idx + 1
        total_lessons_in_module = len(current_module["lessons"])
        st.markdown(
            f"<p style='text-align: center;'>Lesson {lesson_num} of {total_lessons_in_module}</p>", 
            unsafe_allow_html=True
        )
    
    # Next lesson button
    with col_right:
        if st.session_state.current_lesson_idx < len(current_module["lessons"]) - 1:
            if st.button("Next Lesson →", use_container_width=True):
                st.session_state.current_lesson_idx += 1
                st.rerun()
        elif st.session_state.current_module_idx < len(modules) - 1:
            if st.button("Next Module →", use_container_width=True):
                st.session_state.current_module_idx += 1
                st.session_state.current_lesson_idx = 0
                st.rerun()
        else:
            # Show message when at the end but not all lessons completed
            if completed_count < total_count:
                st.info("📚 You've reached the end. Continue practicing to complete all lessons.")
    
    # ========================================================================
    # USER EXPERIENCE SURVEY
    # ========================================================================
    st.markdown("---")
    st.markdown("### System Evaluation Survey")
    st.markdown("*Please help evaluate the system for thesis purposes*")

    with st.form("ux_survey"):
        st.markdown("**1. Visual Clarity**")
        visual_clarity = st.slider("How clear and understandable are the visualizations?", 1, 5, 3)
        
        st.markdown("**2. Interpretability**")
        interpretability = st.slider("How easy is it to interpret the sentiment analysis results?", 1, 5, 3)
        
        st.markdown("**3. Exploratory Potential**")
        exploratory = st.slider("How well does the system support exploring data on your own?", 1, 5, 3)
        
        st.markdown("**4. Overall Satisfaction**")
        overall = st.slider("Overall satisfaction with the system", 1, 5, 3)
        
        feedback = st.text_area("Additional feedback (optional)")
        
        submitted = st.form_submit_button("Submit Evaluation")
        
        if submitted:
            if 'survey_responses' not in st.session_state:
                st.session_state.survey_responses = []
            
            # FIXED: Use datetime.datetime.now() instead of datetime.now()
            st.session_state.survey_responses.append({
                'timestamp': datetime.datetime.now(),
                'visual_clarity': visual_clarity,
                'interpretability': interpretability,
                'exploratory': exploratory,
                'overall': overall,
                'feedback': feedback
            })
            
            st.success("Thank you for your feedback! This helps with thesis evaluation.")
            
            if len(st.session_state.survey_responses) > 0:
                st.markdown("### Survey Summary (for Thesis)")
                df_survey = pd.DataFrame(st.session_state.survey_responses)
                st.dataframe(df_survey.describe(), use_container_width=True)

if __name__ == "__main__":
    learning_hub_page()