import streamlit as st
import datetime 
import pandas as pd

@st.cache_data
def get_course_data():
    return [
        {
            "id": "behavioral_foundations",
            "title": "Consumer Psychology in Asset Markets",
            "lessons": [
                {
                    "id": "b1",
                    "title": "The Herd Mentality",
                    "duration": "6 min",
                    "content": """Consumer behaviour in asset markets is rarely rational. One of the strongest drivers is **herding** – the tendency to follow what the crowd is doing.

**How herding works:**
• Investors observe others buying (e.g., GameStop, crypto) and assume they have superior information.
• Social media amplifies this effect – a few viral posts can trigger thousands of similar trades.
• The result: price bubbles and crashes that have little to do with company fundamentals.

**Our AI's role:** The system identifies 'high‑density clusters' of similar sentiment across Reddit posts. When many consumers express identical opinions, the dashboard flags potential herding behaviour – helping you distinguish genuine momentum from collective delusion.""",
                    "key_takeaway": "Herding turns social sentiment into a self‑fulfilling prophecy. Our AI helps you see when the crowd is moving as one.",
                    "quiz": {
                        "question": "Which behaviour describes a consumer buying an asset just because everyone else is?",
                        "options": ["Fundamental Analysis", "Herding Behavior", "Value Investing", "Risk Mitigation"],
                        "correct_index": 1,
                        "explanation": "Herding occurs when consumers follow the crowd's sentiment – a key volatility driver detected by our sentiment clustering."
                    }
                },
                {
                    "id": "b2",
                    "title": "Fear & Greed Cycles",
                    "duration": "7 min",
                    "content": """Market prices are driven by two primal emotions: **fear** and **greed**. These emotions alternate in cycles, often disconnected from economic reality.

**The cycle:**
1. **Greed (Euphoria)** – Prices rise, consumers fear missing out, they buy more → prices go higher.
2. **Fear (Panic)** – Prices fall, consumers worry about losses, they sell → prices crash further.

**Visualising emotion:** Our dashboard uses colour as a psychological mirror.  
- Emerald green encodes **greed / euphoria**  
- Crimson red encodes **fear / panic**  
- The saturation level tells you how intense the emotion is.

**Why this matters:** By seeing the crowd's emotional state at a glance, you can avoid buying at the peak of greed or selling at the bottom of fear.""",
                    "key_takeaway": "Markets are a pendulum between greed and fear. The dashboard’s colour coding makes this emotional cycle visible in real time.",
                    "quiz": {
                        "question": "What emotion typically drives a market crash according to behavioural finance?",
                        "options": ["Greed", "Fear", "Optimism", "Boredom"],
                        "correct_index": 1,
                        "explanation": "Fear triggers panic selling, which accelerates price declines – a pattern our anomaly timeline highlights in red."
                    }
                },
                {
                    "id": "b3",
                    "title": "Narrative Economics",
                    "duration": "6 min",
                    "content": """Narrative economics (Robert Shiller) studies how stories – not just facts – drive consumer behaviour. A single phrase can become a psychological trigger.

**Examples of market narratives:**
• "To the moon" – signals euphoric belief in unlimited upside.
• "Diamond hands" – encourages holding despite falling prices.
• "Crash" or "bloodbath" – amplifies fear and selling pressure.

**How our system helps:** The Word Cloud and FP‑Growth pattern mining extract the most frequent phrases and co‑occurring terms. When you see "inflation" + "fed" + "crash" appearing together across hundreds of posts, you know a bearish narrative is spreading through the crowd. Understanding the *story* helps you anticipate consumer reaction before price moves.""",
                    "key_takeaway": "Market narratives are social contagions. Our pattern mining reveals the contagious phrases driving consumer decisions.",
                    "quiz": {
                        "question": "What does 'narrative economics' study?",
                        "options": ["Interest rates", "Company balance sheets", "Stories that drive consumer behaviour", "Algorithmic trading"],
                        "correct_index": 2,
                        "explanation": "Narrative economics focuses on how popular stories and phrases spread through communities and influence asset markets."
                    }
                }
            ]
        },
        {
            "id": "behavioral_biases",
            "title": "Cognitive Biases & Decision‑Making",
            "lessons": [
                {
                    "id": "c1",
                    "title": "Loss Aversion & Disposition Effect",
                    "duration": "7 min",
                    "content": """Loss aversion is the observation that **losing €100 feels twice as painful as gaining €100 feels good**. This bias warps consumer decisions.

**The disposition effect:** Consumers hold losing investments too long (hoping to recover) and sell winning investments too early (locking in small gains).

**Sentiment signature:** In our data, loss aversion appears as a sudden shift from neutral to strongly negative sentiment after a price drop – but unusually low trading volume. The AI's anomaly timeline flags these emotional stalemates.""",
                    "key_takeaway": "Consumers feel losses more intensely than gains. Our sentiment analysis helps you spot when fear of loss is paralyzing the crowd.",
                    "quiz": {
                        "question": "Loss aversion means that:",
                        "options": ["People prefer gaining to losing", "Losses feel twice as painful as equivalent gains", "Investors are always rational", "Risk is ignored"],
                        "correct_index": 1,
                        "explanation": "Loss aversion is a core behavioural bias: the emotional impact of a loss is roughly twice that of an equal‑sized gain."
                    }
                },
                {
                    "id": "c2",
                    "title": "Confirmation Bias on Social Media",
                    "duration": "6 min",
                    "content": """Confirmation bias is the tendency to seek, interpret, and remember information that confirms your existing beliefs. On Reddit and Twitter, this creates **echo chambers**.

**How it distorts markets:**
• A consumer bullish on Tesla will upvote positive Tesla posts and ignore negative ones.
• The algorithm then shows them even more positive content – reinforcing the bias.
• The result: overconfidence and crowded trades that reverse violently when reality hits.

**Our system's countermeasure:** The dashboard shows **both** positive and negative sentiment trends side by side. The Sentiment Gap visualisation compares social media optimism with official consumer confidence indices – exposing when the crowd has detached from fundamentals.""",
                    "key_takeaway": "Confirmation bias hides risks. Our dual‑sentiment view forces you to see the full picture.",
                    "quiz": {
                        "question": "What is the main danger of confirmation bias for investors?",
                        "options": ["It makes them sell too early", "It causes them to ignore contradictory evidence", "It lowers trading costs", "It reduces volatility"],
                        "correct_index": 1,
                        "explanation": "Confirmation bias leads consumers to ignore warning signs, which can result in holding losing positions too long."
                    }
                },
                {
                    "id": "c3",
                    "title": "Overconfidence & Trading Frequency",
                    "duration": "5 min",
                    "content": """Overconfidence is the illusion that you have superior knowledge or skill. In asset markets, overconfident consumers trade **more frequently** – and often earn **lower returns** after costs.

**Behavioural signature:** Overconfident periods show high sentiment polarity (extreme positive or negative) combined with high post counts and comment activity. The anomaly timeline marks these as high‑intensity events.

**Practical lesson:** When our AI flags extreme sentiment *plus* unusually high discussion volume, be cautious. The crowd may be overconfident – a common prelude to reversals.""",
                    "key_takeaway": "Overconfidence leads to overtrading. Use our sentiment‑volume correlation to spot when the crowd is dangerously sure of itself.",
                    "quiz": {
                        "question": "Overconfident investors tend to:",
                        "options": ["Trade less frequently", "Earn higher returns", "Trade more frequently and earn lower returns", "Avoid social media"],
                        "correct_index": 2,
                        "explanation": "Studies show overconfident investors trade more often, incur higher transaction costs, and achieve lower net returns."
                    }
                }
            ]
        },
        {
            "id": "applied_analysis",
            "title": "Applied Consumer Analysis with AI",
            "lessons": [
                {
                    "id": "d1",
                    "title": "Reading the Anomaly Timeline",
                    "duration": "8 min",
                    "content": """The **Anomaly Timeline** is your window into shifts in consumer psychology. It works by calculating a rolling Z‑score of daily Reddit sentiment.

**How to read it:**
• Large markers = statistically unusual sentiment change (Z‑score ≥2).
• Green markers = sudden euphoria / greed.
• Red markers = sudden panic / fear.
• Hover over any marker to see the exact sentiment score, post count, and – where available – the triggering market event (e.g., “Tesla buys $1.5B Bitcoin”).

**Consumer behaviour insight:** Anomalies often occur just before price reversals. A green anomaly after a price drop may signal the start of a recovery; a red anomaly after a price rise may signal profit‑taking. Practice spotting these patterns.""",
                    "key_takeaway": "Statistically anomalous sentiment often precedes consumer‑driven price moves. Use the timeline as your early warning system.",
                    "quiz": {
                        "question": "What Z‑score threshold triggers an anomaly marker on the timeline?",
                        "options": ["≥ 1", "≥ 2", "≥ 3", "≥ 5"],
                        "correct_index": 1,
                        "explanation": "The system flags anomalies when the rolling Z‑score is 2 or higher, indicating sentiment is two standard deviations from its recent mean."
                    }
                },
                {
                    "id": "d2",
                    "title": "Using the Sentiment Gap",
                    "duration": "6 min",
                    "content": """The **Sentiment Gap** compares two sources of consumer confidence:
1. **Reddit sentiment** (our AI, based on thousands of retail posts)
2. **Official Consumer Sentiment** (UMCSENT from the University of Michigan)

**What the gap tells you:**  
When Reddit sentiment is much more positive than official measures → retail hype may be decoupled from fundamentals (potential bubble).  
When Reddit sentiment is much more negative → retail fear may be overdone (potential buying opportunity).

**How to interact:** The Economic Dashboard overlays both series. The filled area between them shows the gap magnitude – the larger the area, the bigger the divergence between crowd psychology and broader consumer confidence.""",
                    "key_takeaway": "Divergence between social sentiment and official surveys signals potential overreaction – either euphoria or panic.",
                    "quiz": {
                        "question": "A large positive Sentiment Gap (Reddit > Official) suggests:",
                        "options": ["Retail investors are unusually pessimistic", "The market is perfectly efficient", "Retail hype may be disconnected from reality", "Prices will definitely rise"],
                        "correct_index": 2,
                        "explanation": "When Reddit sentiment is far above official surveys, it indicates retail enthusiasm that may not be supported by broader economic conditions."
                    }
                },
                {
                    "id": "d3",
                    "title": "Pattern Mining for Consumer Triggers",
                    "duration": "7 min",
                    "content": """The **Pattern Mining page** uses FP‑Growth to discover which words frequently appear together in consumer discussions – without you having to guess.

**Example discovered rules:**
• "inflation" + "fed" + "rates" → "crash" (a bearish cluster)
• "moon" + "diamond" + "hold" → "gme" (a bullish cluster)

**How to use this:** Each rule has a **lift** value – how much more likely the consequence word appears when the antecedent words are present. Higher lift = stronger consumer association.  
The Sankey diagram visualises these flows: thick streams mean the consumer crowd strongly links those concepts.

**Consumer insight:** By monitoring which clusters grow over time, you can detect new narratives before they go mainstream.""",
                    "key_takeaway": "Pattern mining reveals the mental links consumers make between events and actions – turning text into a behavioural map.",
                    "quiz": {
                        "question": "What does a high 'lift' value indicate in association rule mining?",
                        "options": ["The rule is random", "The words are strongly associated in consumer posts", "The rule has low support", "The words never appear together"],
                        "correct_index": 1,
                        "explanation": "Lift measures how much more likely the consequent word(s) appear given the antecedent – high lift means a strong, meaningful association in consumer language."
                    }
                }
            ]
        }
    ]

def learning_hub_page():
    
    if "completed_lessons" not in st.session_state:
        st.session_state.completed_lessons = set()
    
    if "current_module_idx" not in st.session_state:
        st.session_state.current_module_idx = 0
    
    if "current_lesson_idx" not in st.session_state:
        st.session_state.current_lesson_idx = 0
    
    if "show_congrats" not in st.session_state:
        st.session_state.show_congrats = False
    if "survey_submitted" not in st.session_state:
        st.session_state.survey_submitted = False

    modules = get_course_data()
    
    st.title("Learning Hub")
    st.markdown("*Understanding consumer psychology in asset markets – supported by AI visualisation*")
    
    all_lesson_ids = [l["id"] for m in modules for l in m["lessons"]]
    total_count = len(all_lesson_ids)
    completed_count = len(st.session_state.completed_lessons)
    
    progress_val = completed_count / total_count if total_count > 0 else 0
    st.progress(progress_val)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Lessons", total_count)
    with col2:
        st.metric("Completed", completed_count)
    with col3:
        st.metric("Progress", f"{int(progress_val * 100)}%")
    
    if completed_count == total_count and total_count > 0:
        if not st.session_state.show_congrats:
            st.session_state.show_congrats = True
            st.balloons()
            st.success(" Congratulations! You've mastered consumer behaviour analysis! ")
        else:
            st.success(" Congratulations! You've mastered consumer behaviour analysis! ")
    else:
        st.session_state.show_congrats = False
    
    st.divider()
    
    st.subheader("Course Modules")
    
    module_cols = st.columns(len(modules))
    for idx, module in enumerate(modules):
        with module_cols[idx]:
            is_active = (idx == st.session_state.current_module_idx)
            if is_active:
                st.button(
                    module["title"],
                    key=f"module_{idx}",
                    use_container_width=True,
                    type="primary"
                )
            else:
                if st.button(
                    module["title"],
                    key=f"module_{idx}",
                    use_container_width=True,
                    type="secondary"
                ):
                    st.session_state.current_module_idx = idx
                    st.session_state.current_lesson_idx = 0
                    st.rerun()
    
    st.divider()
    
    current_module = modules[st.session_state.current_module_idx]
    current_lesson = current_module["lessons"][st.session_state.current_lesson_idx]
    
    st.caption(f"Module {st.session_state.current_module_idx + 1} of {len(modules)}")
    st.subheader(current_lesson['title'])
    st.caption(f"Estimated reading time: {current_lesson['duration']}")
    
    with st.container(border=True):
        st.markdown(current_lesson["content"])
    
    st.markdown(f"**Key Takeaway:** {current_lesson['key_takeaway']}")
    
    if "quiz" in current_lesson:
        with st.expander("Test Your Knowledge", expanded=True):
            quiz = current_lesson["quiz"]
            lesson_completed = current_lesson["id"] in st.session_state.completed_lessons
            
            if lesson_completed:
                st.success(" You've completed this lesson's knowledge check.")
            
            with st.form(key=f"form_{current_lesson['id']}"):
                choice = st.radio(quiz["question"], quiz["options"])
                submitted = st.form_submit_button("Submit Answer", disabled=lesson_completed)
                
                if submitted:
                    if quiz["options"].index(choice) == quiz["correct_index"]:
                        st.session_state.completed_lessons.add(current_lesson["id"])
                        st.success(f"✓ Correct! {quiz['explanation']}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"✗ Not quite. {quiz['explanation']}")
                        st.info(" Hint: Review the lesson content above and try again.")
    
    st.divider()
    
    col_left, col_center, col_right = st.columns([1, 1, 1])
    
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
    
    with col_center:
        lesson_num = st.session_state.current_lesson_idx + 1
        total_lessons_in_module = len(current_module["lessons"])
        st.markdown(
            f"<p style='text-align: center;'>Lesson {lesson_num} of {total_lessons_in_module}</p>", 
            unsafe_allow_html=True
        )
    
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
            if completed_count < total_count:
                st.info(" You've reached the end. Continue practicing to complete all lessons.")
    
    # Survey section
    if not st.session_state.survey_submitted:
        st.markdown("---")
        st.markdown("### System Evaluation Survey")
        st.markdown("*Please help evaluate the system for thesis purposes*")

        with st.form("ux_survey"):
            st.markdown("**1. Visual Clarity**")
            visual_clarity = st.slider("How clear and understandable are the visualizations?", 1, 5, 3, key="survey_clarity")
            
            st.markdown("**2. Interpretability**")
            interpretability = st.slider("How easy is it to interpret the sentiment analysis results?", 1, 5, 3, key="survey_interpret")
            
            st.markdown("**3. Exploratory Potential**")
            exploratory = st.slider("How well does the system support exploring data on your own?", 1, 5, 3, key="survey_explore")
            
            st.markdown("**4. Overall Satisfaction**")
            overall = st.slider("Overall satisfaction with the system", 1, 5, 3, key="survey_overall")
            
            feedback = st.text_area("Additional feedback (optional)", key="survey_feedback")
            
            submitted = st.form_submit_button("Submit Evaluation")
            
            if submitted:
                if 'survey_responses' not in st.session_state:
                    st.session_state.survey_responses = []
                
                st.session_state.survey_responses.append({
                    'timestamp': datetime.datetime.now(),
                    'visual_clarity': visual_clarity,
                    'interpretability': interpretability,
                    'exploratory': exploratory,
                    'overall': overall,
                    'feedback': feedback
                })
                
                st.session_state.survey_submitted = True
                st.success("Thank you for your feedback! This helps with thesis evaluation.")
                st.rerun()
    
    else:
        st.markdown("---")
        st.markdown("### System Evaluation Survey")
        st.success("Thank you for your feedback! This helps with thesis evaluation.")
        
        if 'survey_responses' in st.session_state and len(st.session_state.survey_responses) > 0:
            with st.expander("View Survey Summary (for Thesis)"):
                df_survey = pd.DataFrame(st.session_state.survey_responses)
                st.dataframe(df_survey.describe(), use_container_width=True)

if __name__ == "__main__":
    learning_hub_page()