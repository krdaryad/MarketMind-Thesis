"""
Economic History & Sentiment – Premium FinTech Design
Interactive timeline with sentiment arc visualization, bento metrics, and media snippets
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

def market_history_page():
    # ============================================================================
    # PAGE HEADER
    # ============================================================================
    st.markdown('<h1>Economic History & Sentiment</h1>', unsafe_allow_html=True)
    st.markdown('<p class="text-muted">How crowd psychology drove the greatest market crashes and bubbles — from 1929 to 2020</p>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    # ============================================================================
    # CUSTOM CSS - Only increased the two smallest fonts
    # ============================================================================
    st.markdown("""
    <style>
    .bento-card {
        background: rgba(59, 130, 246, 0.03);
        border: 1px solid rgba(59, 130, 246, 0.15);
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        transition: all 0.2s ease;
    }
    .bento-card:hover {
        border-color: #3B82F6;
        background: rgba(59, 130, 246, 0.08);
        transform: translateY(-2px);
    }
    .bento-label {
        font-size: 0.65rem;
        color: #8A8F99;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0;
    }
    .bento-value {
        font-size: 1.2rem;
        font-weight: bold;
        color: #3B82F6;
        margin: 0.25rem 0 0 0;
    }
    .media-snippet {
        background: #111317;
        border-left: 3px solid;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.75rem;
        font-size: 0.85rem;  /* INCREASED from 0.75rem */
        font-style: italic;
        transition: all 0.2s ease;
    }
    .media-snippet:hover {
        transform: translateX(4px);
    }
    .media-positive { border-left-color: #10B981; }
    .media-negative { border-left-color: #EF4444; }
    .media-neutral { border-left-color: #8A8F99; }
    .year-badge {
        background: #3B82F6;
        color: white;
        display: inline-block;
        padding: 0.3rem 1.2rem;
        border-radius: 30px;
        font-size: 1rem;
        font-weight: bold;
    }
    /* Sentiment cycle badges */
    .cycle-badge {
        text-align: center;
        background: #111317;
        border-radius: 20px;
        padding: 0.4rem 0.1rem;
        border: 1px solid rgba(59,130,246,0.2);
    }
    .cycle-badge .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin: 0 auto 4px auto;
    }
    .cycle-badge .label {
        font-size: 0.6rem;
        color: #E2E8F0;
    }
    /* Phase legend */
    .phase-legend-item {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.7rem;
    }
    /* Card description */
    .card-description {
        color: #E2E8F0;
        font-size: 0.85rem;
        line-height: 1.5;
        margin-top: 1rem;
    }
    /* Sentiment phase text - INCREASED smallest font */
    .phase-text {
        font-size: 0.8rem;  /* INCREASED from 0.7rem */
        margin-top: 0.3rem;
        color: #8A8F99;
    }
    .phase-period {
        font-size: 0.7rem;
        color: #64748B;
    }
    /* Duration badges */
    .info-badge {
        background: #1A1D24;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.75rem;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

    # ============================================================================
    # PHASE CONFIGURATION
    # ============================================================================
    phase_config = {
        "euphoria": {"label": "Euphoria", "color": "#10B981", "bg": "rgba(16,185,129,0.1)"},
        "denial": {"label": "Denial", "color": "#F59E0B", "bg": "rgba(245,158,11,0.1)"},
        "panic": {"label": "Panic", "color": "#EF4444", "bg": "rgba(239,68,68,0.1)"},
        "capitulation": {"label": "Capitulation", "color": "#DC2626", "bg": "rgba(220,38,38,0.1)"},
        "recovery": {"label": "Recovery", "color": "#3B82F6", "bg": "rgba(59,130,246,0.1)"},
    }

    # ============================================================================
    # CRISES DATA
    # ============================================================================
    crises = [
        {
            "id": "crisis_1929",
            "year": "1929",
            "title": "The Great Crash",
            "subtitle": "Wall Street Crash & Great Depression",
            "peakDecline": "-89%",
            "duration": "34 months",
            "sentimentArc": "Euphoria → Denial → Panic → Capitulation",
            "description": "The most devastating stock market crash in US history. Fueled by excessive speculation, margin buying (up to 90% leverage), and blind optimism, the Dow Jones lost 89% of its value from peak to trough.",
            "sentimentPhases": [
                {"phase": "euphoria", "period": "1927–Sep 1929", "description": "New Era thinking. Shoe-shine boys giving stock tips. Margin debt at unprecedented levels."},
                {"phase": "denial", "period": "Oct 1929 (Week 1)", "description": "Initial 11% drop dismissed as healthy correction. J.P. Morgan organized banker pool to stabilize prices."},
                {"phase": "panic", "period": "Oct 28–29", "description": "16M shares traded on Black Tuesday. Margin calls triggered forced selling cascade."},
                {"phase": "capitulation", "period": "1930–1932", "description": "Dead cat bounces crushed remaining optimism. Bank failures destroyed savings."},
                {"phase": "recovery", "period": "1933–1937", "description": "New Deal programs. SEC established 1934. Dow didn't recover 1929 levels until 1954."},
            ],
            "keyIndicators": [
                {"label": "Peak Dow", "value": "381.17"},
                {"label": "Trough Dow", "value": "41.22"},
                {"label": "Margin Rate", "value": "Up to 90%"},
                {"label": "Bank Failures", "value": "9,000+"},
                {"label": "Unemployment", "value": "25%"},
                {"label": "Recovery Time", "value": "25 years"},
            ],
            "priceData": [
                    {"t": 1927, "v": 200, "phase": "euphoria"},
                    {"t": 1928, "v": 300, "phase": "euphoria"},
                    {"t": 1929.75, "v": 381, "phase": "euphoria"},  # Sep 1929 = 1929.75
                    {"t": 1929.83, "v": 230, "phase": "panic"},     # Oct 29 = 1929.83
                    {"t": 1930.33, "v": 294, "phase": "denial"},    # Apr 1930 = 1930.33
                    {"t": 1930.92, "v": 164, "phase": "capitulation"}, # Dec 1930 = 1930.92
                    {"t": 1931.42, "v": 156, "phase": "capitulation"}, # Jun 1931 = 1931.42
                    {"t": 1932.5, "v": 41, "phase": "capitulation"},   # Jul 1932 = 1932.5
                    {"t": 1933, "v": 99, "phase": "recovery"},
                    {"t": 1937, "v": 194, "phase": "recovery"},
                ],
            "lessons": [
                "Extreme leverage amplifies both gains and catastrophic losses",
                "Public euphoria and new paradigm narratives are contrarian indicators",
                "Regulatory absence allows systemic risk to compound invisibly",
                "Recovery timelines can span decades, not months",
            ],
            "mediaHeadlines": [
                {"text": "Stocks have reached what looks like a permanently high plateau — Irving Fisher, Oct 1929", "sentiment": "positive"},
                {"text": "Wall Street Lays an Egg — Variety, Oct 30 1929", "sentiment": "negative"},
                {"text": "Worst Stock Crash Stemmed by Banks — NYT, Oct 25 1929", "sentiment": "neutral"},
            ],
        },
        {
            "id": "crisis_1987",
            "year": "1987",
            "title": "Black Monday",
            "subtitle": "Program Trading & Portfolio Insurance Failure",
            "peakDecline": "-22.6% (1 day)",
            "duration": "1 day crash, 2-year recovery",
            "sentimentArc": "Complacency → Shock → Panic → Swift Recovery",
            "description": "On October 19, 1987, the Dow Jones fell 22.6% in a single session — the largest one-day percentage decline in history. Automated program trading and portfolio insurance strategies created a self-reinforcing selling cascade.",
            "sentimentPhases": [
                {"phase": "euphoria", "period": "Jan–Aug 1987", "description": "Dow up 44% YTD by August. Portfolio insurance gave false sense of security."},
                {"phase": "denial", "period": "Oct 14–16", "description": "Market dropped 10% in 3 days. Analysts called it profit-taking."},
                {"phase": "panic", "period": "Oct 19", "description": "508-point drop. NYSE volume 604M shares. Portfolio insurance overwhelmed buy orders."},
                {"phase": "capitulation", "period": "Oct 20 morning", "description": "Futures indicated another 20% drop. Fed pledged liquidity."},
                {"phase": "recovery", "period": "Oct 20 PM–1989", "description": "Markets stabilized after Fed intervention. Circuit breakers introduced."},
            ],
            "keyIndicators": [
                {"label": "Single-Day Drop", "value": "-22.6%"},
                {"label": "Points Lost", "value": "508"},
                {"label": "Volume", "value": "604M shares"},
                {"label": "Portfolio Insurance", "value": "$60-90B"},
                {"label": "Fed Response", "value": "Same day"},
                {"label": "Recovery Time", "value": "2 years"},
            ],
            "priceData": [
                {"t": "Jan 87", "v": 1900, "phase": "euphoria"},
                {"t": "Aug 87", "v": 2722, "phase": "euphoria"},
                {"t": "Oct 16", "v": 2400, "phase": "denial"}, 
                {"t": "Oct 19", "v": 1738, "phase": "panic"},
                {"t": "Oct 20", "v": 1841, "phase": "recovery"}, 
                {"t": "Dec 87", "v": 1939, "phase": "recovery"},
                {"t": "Jun 88", "v": 2100, "phase": "recovery"}, 
                {"t": "Sep 89", "v": 2750, "phase": "recovery"},
            ],
            "lessons": [
                "Algorithmic trading can create feedback loops that amplify crashes",
                "Central bank communication is a powerful sentiment stabilization tool",
                "Circuit breakers and market structure reforms matter",
                "Speed of Fed response directly correlates with recovery speed",
            ],
            "mediaHeadlines": [
                {"text": "The Stock Market's Crash: Does 1987 Equal 1929? — NYT, Oct 20", "sentiment": "negative"},
                {"text": "Fed Pledges to Supply Liquidity — WSJ, Oct 20", "sentiment": "neutral"},
                {"text": "Panic Grips Markets Worldwide — FT, Oct 20", "sentiment": "negative"},
            ],
        },
        {
            "id": "crisis_2000",
            "year": "2000",
            "title": "Dot-Com Bubble",
            "subtitle": "Internet Mania & Irrational Exuberance",
            "peakDecline": "-78% (NASDAQ)",
            "duration": "30 months",
            "sentimentArc": "Irrational Exuberance → Denial → Grinding Bear → Reset",
            "description": "The dot-com bubble saw NASDAQ rise 400% from 1995 to March 2000, driven by speculative frenzy over internet companies with no earnings. When the bubble burst, $5 trillion in market value evaporated.",
            "sentimentPhases": [
                {"phase": "euphoria", "period": "1998–Mar 2000", "description": "IPOs doubling on first day. Eyeballs over earnings. Day trading became a lifestyle."},
                {"phase": "denial", "period": "Mar–Sep 2000", "description": "Initial 10% drop seen as buying opportunity. Analysts maintained price targets."},
                {"phase": "panic", "period": "Oct 2000–Mar 2001", "description": "Dot-coms burning through cash. Mass layoffs in Silicon Valley."},
                {"phase": "capitulation", "period": "Sep 2001–Oct 2002", "description": "9/11 added geopolitical shock. Accounting scandals destroyed remaining trust."},
                {"phase": "recovery", "period": "2003–2015", "description": "Survivors built real businesses. NASDAQ recovered peak in April 2015."},
            ],
            "keyIndicators": [
                {"label": "NASDAQ Peak", "value": "5,048"},
                {"label": "NASDAQ Trough", "value": "1,114"},
                {"label": "Value Destroyed", "value": "$5 trillion"},
                {"label": "Failed Dot-Coms", "value": "~500"},
                {"label": "Avg IPO 1st Day", "value": "+65%"},
                {"label": "Recovery Time", "value": "15 years"},
            ],
            "priceData": [
                    {"t": 1998, "v": 2000, "phase": "euphoria"},
                    {"t": 1999, "v": 4000, "phase": "euphoria"},
                    {"t": 2000.2, "v": 5048, "phase": "euphoria"},   # Mar 2000 = 2000.2
                    {"t": 2000.75, "v": 3800, "phase": "denial"},    # Sep 2000 = 2000.75
                    {"t": 2001.2, "v": 2000, "phase": "panic"},      # Mar 2001 = 2001.2
                    {"t": 2001.75, "v": 1500, "phase": "panic"},     # Sep 2001 = 2001.75
                    {"t": 2002.83, "v": 1114, "phase": "capitulation"}, # Oct 2002 = 2002.83
                    {"t": 2004, "v": 2000, "phase": "recovery"},
                    {"t": 2007, "v": 2800, "phase": "recovery"},
                    {"t": 2015, "v": 5000, "phase": "recovery"},
                ],
            "lessons": [
                "Revenue and profit matter — eyeballs is not a business model",
                "When taxi drivers discuss stock picks, the bubble is near its peak",
                "Survivorship bias: Amazon survived, but 499 others didn't",
                "Regulatory failure to address IPO allocation corruption enabled the mania",
            ],
            "mediaHeadlines": [
                {"text": "Amazon.bomb — Barron's cover, May 1999 (too early, but eventually right)", "sentiment": "negative"},
                {"text": "Dow 36,000 — Book published Oct 1999 at Dow 10,000", "sentiment": "positive"},
                {"text": "Irrational Exuberance — Greenspan, Dec 1996", "sentiment": "neutral"},
            ],
        },
        {
            "id": "crisis_2008",
            "year": "2008",
            "title": "Global Financial Crisis",
            "subtitle": "Subprime Mortgage Collapse & Systemic Failure",
            "peakDecline": "-57% (S&P 500)",
            "duration": "17 months",
            "sentimentArc": "Greed → Confusion → Terror → Government Rescue",
            "description": "The 2008 GFC was triggered by the collapse of the US housing bubble, amplified by complex derivatives that spread toxic assets globally. Lehman Brothers' bankruptcy on September 15, 2008, triggered a global credit freeze.",
            "sentimentPhases": [
                {"phase": "euphoria", "period": "2004–2006", "description": "Housing prices never go down. NINJA loans. CDO machine generated $500B per year."},
                {"phase": "denial", "period": "Feb 2007–Mar 2008", "description": "Subprime losses called contained. Bear Stearns collapsed but markets hit new highs."},
                {"phase": "panic", "period": "Sep–Oct 2008", "description": "Lehman bankruptcy. AIG bailout. Money market fund broke the buck. VIX hit 89.53."},
                {"phase": "capitulation", "period": "Nov 2008–Mar 2009", "description": "S&P 500 hit 666.79. Auto industry bailout. Global recession confirmed."},
                {"phase": "recovery", "period": "Mar 2009–2013", "description": "QE1, QE2, Operation Twist. Zero interest rates for 7 years. S&P recovered by 2013."},
            ],
            "keyIndicators": [
                {"label": "S&P 500 Trough", "value": "666.79"},
                {"label": "Wealth Destroyed", "value": "$19.2T"},
                {"label": "Jobs Lost", "value": "8.7M"},
                {"label": "TARP Size", "value": "$700B"},
                {"label": "Peak VIX", "value": "89.53"},
                {"label": "Recovery Time", "value": "4 years"},
            ],
            "priceData": [
                    {"t": 2006, "v": 1400, "phase": "euphoria"},
                    {"t": 2007.83, "v": 1565, "phase": "euphoria"},  # Oct 2007 = 2007.83
                    {"t": 2008.2, "v": 1300, "phase": "denial"},    # Mar 2008 = 2008.2
                    {"t": 2008.75, "v": 1200, "phase": "panic"},    # Sep 2008 = 2008.75
                    {"t": 2008.92, "v": 850, "phase": "panic"},     # Nov 2008 = 2008.92
                    {"t": 2009.2, "v": 666, "phase": "capitulation"}, # Mar 2009 = 2009.2
                    {"t": 2009.92, "v": 1115, "phase": "recovery"}, # Dec 2009 = 2009.92
                    {"t": 2011, "v": 1260, "phase": "recovery"},
                    {"t": 2013, "v": 1565, "phase": "recovery"},
                ],
            "lessons": [
                "Complexity and opacity in financial instruments creates hidden systemic risk",
                "Rating agency conflicts of interest can mask true risk levels",
                "Too big to fail creates moral hazard that encourages excessive risk-taking",
                "Sentiment unanimity (housing never falls) is a warning sign, not reassurance",
            ],
            "mediaHeadlines": [
                {"text": "Is This the Big One? — CNBC, Sep 15 2008", "sentiment": "negative"},
                {"text": "Stocks Surge on Bailout Plan — only to fall 40% more", "sentiment": "positive"},
                {"text": "Worst Crisis Since '30s, With No End Yet in Sight — WSJ, Sep 2008", "sentiment": "negative"},
            ],
        },
        {
            "id": "crisis_2020",
            "year": "2020",
            "title": "COVID-19 Crash",
            "subtitle": "Fastest Bear Market in History",
            "peakDecline": "-34% (S&P 500)",
            "duration": "33 days (crash), 5 months (recovery)",
            "sentimentArc": "Shock → Panic → Fed Put → Euphoria",
            "description": "COVID-19 triggered the fastest bear market in history — the S&P 500 fell 34% in just 33 days. The Fed deployed $3T in stimulus within weeks. Markets fully recovered by August 2020.",
            "sentimentPhases": [
                {"phase": "denial", "period": "Jan–Feb 2020", "description": "COVID seen as China problem. Markets hit all-time highs on Feb 19."},
                {"phase": "panic", "period": "Feb 20–Mar 23", "description": "4 circuit breaker triggers in 2 weeks. VIX hit 82.69. Oil futures went negative."},
                {"phase": "capitulation", "period": "Mar 23", "description": "S&P bottomed at 2,237. Fed announced unlimited QE. Whatever it takes moment."},
                {"phase": "recovery", "period": "Apr–Aug 2020", "description": "Fastest recovery ever. Retail trading exploded. Stocks only go up meme."},
                {"phase": "euphoria", "period": "Sep 2020–Jan 2021", "description": "SPACs, meme stocks, crypto mania. GME squeeze became ultimate retail sentiment event."},
            ],
            "keyIndicators": [
                {"label": "Crash Duration", "value": "33 days"},
                {"label": "S&P 500 Drop", "value": "-34%"},
                {"label": "Peak VIX", "value": "82.69"},
                {"label": "Fed Stimulus", "value": "$3T+"},
                {"label": "Reddit VADER Low", "value": "-0.61"},
                {"label": "Recovery Time", "value": "5 months"},
            ],
            "priceData": [
                {"t": "Jan 20", "v": 3300, "phase": "denial"},
                {"t": "Feb 19", "v": 3386, "phase": "denial"},
                {"t": "Mar 9", "v": 2746, "phase": "panic"}, 
                {"t": "Mar 16", "v": 2386, "phase": "panic"},
                {"t": "Mar 23", "v": 2237, "phase": "capitulation"}, 
                {"t": "Apr 20", "v": 2870, "phase": "recovery"},
                {"t": "Jun 20", "v": 3100, "phase": "recovery"}, 
                {"t": "Aug 20", "v": 3500, "phase": "recovery"},
                {"t": "Nov 20", "v": 3600, "phase": "euphoria"}, 
                {"t": "Jan 21", "v": 3800, "phase": "euphoria"},
            ],
            "lessons": [
                "Central bank speed of response is the number one factor in sentiment recovery",
                "Social media (Reddit) became a primary sentiment amplifier in this crisis",
                "Compressed crash and recovery cycles create new behavioral patterns",
                "Retail investor sentiment now moves markets — not just institutional flows",
            ],
            "mediaHeadlines": [
                {"text": "Stocks Only Go Up — r/wallstreetbets mantra, Apr 2020", "sentiment": "positive"},
                {"text": "Is This the End of Capitalism? — multiple outlets, Mar 2020", "sentiment": "negative"},
                {"text": "Fed Goes All In — Bloomberg, Mar 23 2020", "sentiment": "neutral"},
            ],
        },
    ]

    # ============================================================================
    # HELPER FUNCTIONS
    # ============================================================================
    def create_sentiment_arc_chart(price_data, crisis_title):
        df = pd.DataFrame(price_data)
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df["t"],
            y=df["v"],
            mode="lines",
            line=dict(color="#3B82F6", width=3),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.15)",
            name="Price Index"
        ))
        
        for phase in phase_config.keys():
            phase_df = df[df["phase"] == phase]
            if not phase_df.empty:
                fig.add_trace(go.Scatter(
                    x=phase_df["t"],
                    y=phase_df["v"],
                    mode="markers",
                    marker=dict(size=10, color=phase_config[phase]["color"], symbol="circle", line=dict(width=2, color="white")),
                    name=phase_config[phase]["label"]
                ))
        
        fig.update_layout(
            title=f"Price Movement & Sentiment Phases: {crisis_title}",
            xaxis_title="Date",
            yaxis_title="Index Value",
            height=350,
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8A8F99", size=11),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

    def sentiment_cycle_diagram():
        phases = ["Optimism", "Excitement", "Euphoria", "Anxiety", "Denial", "Fear", "Panic", "Capitulation", "Depression", "Hope"]
        colors = ["#10B981", "#10B981", "#10B981", "#F59E0B", "#F59E0B", "#EF4444", "#DC2626", "#DC2626", "#8A8F99", "#3B82F6"]
        
        cols = st.columns(len(phases))
        for i, (label, color) in enumerate(zip(phases, colors)):
            with cols[i]:
                st.markdown(f"""
                <div class="cycle-badge">
                    <div class="dot" style="background: {color};"></div>
                    <div class="label">{label}</div>
                </div>
                """, unsafe_allow_html=True)

    def phase_legend():
        st.markdown('<div style="display: flex; flex-wrap: wrap; gap: 0.75rem; margin: 1rem 0 1.5rem 0;">', unsafe_allow_html=True)
        for key, cfg in phase_config.items():
            st.markdown(f"""
            <div class="phase-legend-item" style="background: {cfg['bg']}; border: 1px solid {cfg['color']}30;">
                <div style="width: 10px; height: 10px; background: {cfg['color']}; border-radius: 50%;"></div>
                <span style="color: {cfg['color']};">{cfg['label']}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================================
    # MAIN PAGE CONTENT
    # ============================================================================

    # Sentiment cycle overview
    st.markdown('''
    <div class="card" style="padding: 1rem;">
        <h3 style="font-size: 1.1rem; margin-top: 0;">The Universal Market Sentiment Cycle</h3>
        <p class="text-muted">Every major crash follows a remarkably similar emotional arc. Understanding these phases — and recognizing which one you are in — is the core insight of behavioral finance.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    sentiment_cycle_diagram()
    st.markdown('<br>', unsafe_allow_html=True)

    # Phase legend
    phase_legend()

    # Crisis timeline - Each crisis in its own card
    for crisis in crises:
        expand_key = f"expanded_{crisis['id']}"
        if expand_key not in st.session_state:
            st.session_state[expand_key] = False

        st.markdown(f'''
        <div class="card" style="padding: 1rem;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                <div class="year-badge">{crisis['year']}</div>
                <h3 style="font-size: 1.1rem; margin: 0;">{crisis['title']}</h3>
            </div>
            <p style="color: #8A8F99; font-size: 0.9rem; margin-bottom: 0.5rem;">{crisis['subtitle']}</p>
            <div style="display: flex; gap: 0.5rem; margin: 0.5rem 0;">
                <span class="info-badge">Duration: {crisis['duration']}</span>
                <span class="info-badge">Sentiment Arc: {crisis['sentimentArc']}</span>
            </div>
        ''', unsafe_allow_html=True)
        
        # Tabs
        tab1, tab2 = st.tabs(["Market Movement", "Crisis Details"])
        
        with tab1:
            fig = create_sentiment_arc_chart(crisis["priceData"], crisis["title"])
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{crisis['id']}")
            st.markdown(f'<p class="card-description">{crisis["description"]}</p>', unsafe_allow_html=True)
        
        with tab2:
            # Key Indicators - 3x2 grid
            st.markdown('<h4 style="font-size: 0.9rem;">Key Indicators</h4>', unsafe_allow_html=True)
            bento_cols = st.columns(3)
            for i, indicator in enumerate(crisis["keyIndicators"]):
                with bento_cols[i % 3]:
                    st.markdown(f"""
                    <div class="bento-card">
                        <p class="bento-label">{indicator['label']}</p>
                        <p class="bento-value">{indicator['value']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Sentiment Phases
            st.markdown('<h4 style="font-size: 0.9rem; margin-top: 1rem;">Sentiment Phase Breakdown</h4>', unsafe_allow_html=True)
            for sp in crisis["sentimentPhases"]:
                cfg = phase_config[sp["phase"]]
                st.markdown(f"""
                <div style="border-left: 3px solid {cfg['color']}; background: #111317; border-radius: 8px; padding: 0.75rem; margin-bottom: 0.75rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                        <div style="width: 10px; height: 10px; background: {cfg['color']}; border-radius: 50%;"></div>
                        <span style="font-weight: bold; color: {cfg['color']};">{cfg['label']}</span>
                        <span class="phase-period">{sp['period']}</span>
                    </div>
                    <p class="phase-text">{sp['description']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Media Headlines
            st.markdown('<h4 style="font-size: 0.9rem; margin-top: 1rem;">Media Sentiment Snapshots</h4>', unsafe_allow_html=True)
            for h in crisis["mediaHeadlines"]:
                sentiment_class = "media-positive" if h["sentiment"] == "positive" else ("media-negative" if h["sentiment"] == "negative" else "media-neutral")
                st.markdown(f'<div class="media-snippet {sentiment_class}">{h["text"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)

    # Cross-crisis comparison table
    st.markdown('''
    <div class="card" style="padding: 1rem;">
        <h3 style="font-size: 1.1rem; margin-top: 0;">Cross-Crisis Comparison</h3>
    </div>
    ''', unsafe_allow_html=True)

    comp_data = []
    for c in crises:
        recovery_time = next((k["value"] for k in c["keyIndicators"] if k["label"] == "Recovery Time"), "N/A")
        comp_data.append({
            "Crisis": f"{c['title']} ({c['year']})",
            "Peak Decline": c["peakDecline"],
            "Crash Duration": c["duration"],
            "Recovery Time": recovery_time,
            "Sentiment Arc": c["sentimentArc"],
        })
    df_comp = pd.DataFrame(comp_data)
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    # Final insight
    st.markdown('''
    <div class="card" style="padding: 1rem; text-align: center;">
        <p style="font-size: 0.9rem; font-style: italic;">"The four most dangerous words in investing: <span style="color: #3B82F6; font-weight: bold;">This time is different.</span>"</p>
        <p style="font-size: 0.7rem; color: #8A8F99;">— Sir John Templeton</p>
        <hr style="margin: 1rem 0; border-color: #1A1D24;">
        <p class="text-muted">Across 100 years of market history, the emotional cycle remains constant. Technology changes, instruments evolve, but human psychology — fear, greed, denial, and capitulation — is the one constant that NLP sentiment analysis can now quantify in real-time.</p>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    market_history_page()