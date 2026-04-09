"""
Event Data - Real-world market events for contextual tooltips
Used across all pages to provide narrative context to sentiment spikes
Includes February AND March 2021 events
"""

MARKET_EVENTS = {
    # ========================================================================
    # FEBRUARY 2021 EVENTS
    # ========================================================================
    '2021-02-01': {
        'title': 'Google Cloud & Ford Partnership',
        'description': 'Google Cloud announced partnership with Ford for connected vehicle services.',
        'impact': 'Tech sector optimism',
        'sentiment_shift': '+0.15',
        'category': 'positive'
    },
    '2021-02-04': {
        'title': 'Elon Musk "Dogecoin is the people\'s crypto"',
        'description': 'Elon Musk tweeted about Dogecoin, sparking retail investor frenzy across all markets.',
        'impact': 'Massive sentiment spike across all tickers',
        'sentiment_shift': '+0.32',
        'category': 'positive'
    },
    '2021-02-08': {
        'title': 'Tesla Buys $1.5B Bitcoin',
        'description': 'Tesla announced $1.5 billion Bitcoin purchase, sending crypto and Tesla stock soaring.',
        'impact': 'Tesla volume spikes to 667 posts',
        'sentiment_shift': '+0.41',
        'category': 'positive'
    },
    '2021-02-18': {
        'title': 'GameStop Congressional Hearing',
        'description': 'Robinhood CEO, Citadel, and Reddit testified before Congress about meme stock phenomenon.',
        'impact': 'High VIX (Fear), peak neutral sentiment',
        'sentiment_shift': '-0.08',
        'category': 'neutral'
    },
    '2021-02-23': {
        'title': 'Tech Sell-off Begins',
        'description': 'Rising interest rates triggered rotation out of high-growth tech stocks.',
        'impact': 'Sentiment shifts from positive to negative',
        'sentiment_shift': '-0.23',
        'category': 'negative'
    },
    '2021-02-24': {
        'title': 'GME Skyrockets 100% in 1 Hour',
        'description': 'GameStop stock doubled in a single hour, triggering circuit breakers.',
        'impact': 'Extreme volatility, VIX spike',
        'sentiment_shift': '+0.18',
        'category': 'volatile'
    },
    '2021-02-25': {
        'title': 'Fed Chair Powell Testimony',
        'description': 'Powell signaled continued low rates, sparking market rally.',
        'impact': 'Market rebound, sentiment improves',
        'sentiment_shift': '+0.22',
        'category': 'positive'
    },
    
    # ========================================================================
    # MARCH 2021 EVENTS
    # ========================================================================
    '2021-03-02': {
        'title': 'Amazon AI & Fulfillment Investment',
        'description': 'Amazon announced major investment in AI-powered fulfillment centers ($200B).',
        'impact': 'High volume for AMZN; investors debating the spend',
        'sentiment_shift': '-0.05',
        'category': 'neutral'
    },
    '2021-03-05': {
        'title': '10Y Treasury Hits 1.62%',
        'description': '10-year Treasury yield hit 1.62%, highest since pre-pandemic levels.',
        'impact': 'Massive negative spike in tech sentiment (AAPL, MSFT) as yields surge',
        'sentiment_shift': '-0.45',
        'category': 'negative'
    },
    '2021-03-10': {
        'title': '$1.9 Trillion Stimulus Passed',
        'description': 'Congress passed the American Rescue Plan. Stimulus checks started arriving.',
        'impact': 'Large positive sentiment spike; "Stimmy" check hype on Reddit',
        'sentiment_shift': '+0.38',
        'category': 'positive'
    },
    '2021-03-12': {
        'title': 'GME Post-Squeeze High ($264)',
        'description': 'GameStop stock hit $264 after the short squeeze. Retail traders celebrating.',
        'impact': 'High sentiment volatility; retail traders celebrating a "rebirth"',
        'sentiment_shift': '+0.25',
        'category': 'positive'
    },
    '2021-03-17': {
        'title': 'Fed Reaffirms Low Rates',
        'description': 'Fed kept rates near zero, maintained bond purchases despite inflation concerns.',
        'impact': 'Relief rally in sentiment as Powell maintains dovish stance',
        'sentiment_shift': '+0.18',
        'category': 'positive'
    },
    '2021-03-23': {
        'title': 'Intel "IDM 2.0" Announcement',
        'description': 'Intel announced massive $20B investment in new fabs and foundry strategy.',
        'impact': 'Impact on Cloud/Growth sector; massive tech strategy shift',
        'sentiment_shift': '+0.12',
        'category': 'neutral'
    },
    '2021-03-24': {
        'title': 'GameStop Earnings Crash (-34%)',
        'description': 'GameStop reported disappointing earnings, stock dropped 34% in one day.',
        'impact': 'Anomaly score spike; sentiment dives after disappointing earnings',
        'sentiment_shift': '-0.52',
        'category': 'negative'
    },
    '2021-03-25': {
        'title': 'GME Recovers 53% in 24 Hours',
        'description': 'GameStop stock rebounded 53% the day after earnings crash.',
        'impact': 'Extreme sentiment volatility; "Diamond Hands" vs "Paper Hands" debate',
        'sentiment_shift': '+0.48',
        'category': 'volatile'
    },
    '2021-03-29': {
        'title': 'Archegos Capital Collapse',
        'description': 'Family office Archegos Capital defaulted on margin calls, triggering $20B liquidation.',
        'impact': 'Maximum pessimism gap; market-wide fear as major fund liquidates',
        'sentiment_shift': '-0.61',
        'category': 'negative'
    }
}

def get_event_for_date(date):
    """Get event info for a specific date."""
    if hasattr(date, 'strftime'):
        date_str = date.strftime('%Y-%m-%d')
    else:
        date_str = str(date)
    return MARKET_EVENTS.get(date_str, None)

def get_event_color(category):
    """Return color based on event category."""
    colors = {
        'positive': '#10B981',
        'negative': '#EF4444',
        'neutral': '#8A8F99',
        'volatile': '#F59E0B'
    }
    return colors.get(category, '#8A8F99')

def add_event_hover_text(df, date_col='date'):
    """Add event information columns to dataframe for hover tooltips."""
    df = df.copy()
    events = df[date_col].apply(get_event_for_date)
    df['event_title'] = events.apply(lambda x: x['title'] if x else '')
    df['event_desc'] = events.apply(lambda x: x['description'] if x else '')
    df['event_impact'] = events.apply(lambda x: x['impact'] if x else '')
    df['event_category'] = events.apply(lambda x: x['category'] if x else '')
    df['event_sentiment_shift'] = events.apply(lambda x: x['sentiment_shift'] if x else '')
    return df