"""
Financial Analysis Module - Phase 3 Market Analysis
Handles financial data, market regimes, and emotion detection
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class FinancialAnalyzer:
    def __init__(self):
        self.financial_data = None
        self.market_regimes = {}
        self.behavioral_features = None
        
    def load_financial_data(self, filepath):
        """Load financial forecasting dataset"""
        self.financial_data = pd.read_csv(filepath)
        self.financial_data['Date'] = pd.to_datetime(self.financial_data['Date'])
        return self.financial_data
    
    def analyze_market_regimes(self, ticker='AAPL'):
        """Analyze market regimes from financial data"""
        ticker_data = self.financial_data[self.financial_data['Ticker'] == ticker].copy()
        
        # Technical indicators
        ticker_data['Daily_Return'] = ticker_data['Close'].pct_change() * 100
        ticker_data['Volatility_5day'] = ticker_data['Daily_Return'].rolling(window=5).std()
        ticker_data['MA_20'] = ticker_data['Close'].rolling(window=20).mean()
        
        # Market regime classification
        ticker_data['Market_Regime'] = 'Neutral'
        ticker_data.loc[ticker_data['Daily_Return'] > 2, 'Market_Regime'] = 'Euphoric'
        ticker_data.loc[ticker_data['Daily_Return'] < -2, 'Market_Regime'] = 'Fearful'
        
        # Stress classification
        ticker_data['Stress_Level'] = 'Low'
        ticker_data.loc[ticker_data['Market Stress Level'] > 0.5, 'Stress_Level'] = 'Medium'
        ticker_data.loc[ticker_data['Market Stress Level'] > 0.8, 'Stress_Level'] = 'High'
        
        self.market_regimes[ticker] = ticker_data
        return ticker_data
    
    def detect_market_emotions(self, ticker_data):
        """Detect market emotions from financial indicators"""
        emotions = []
        for idx, row in ticker_data.iterrows():
            daily_return = row.get('Daily_Return', 0)
            stress = row.get('Market Stress Level', 0)
            volatility = row.get('Volatility_5day', 0)
            
            if daily_return > 5 and stress < 0.3:
                emotion = "Market Euphoria"
            elif daily_return < -5 and stress > 0.7:
                emotion = "Market Panic"
            elif volatility > ticker_data['Volatility_5day'].quantile(0.9):
                emotion = "Market Anxiety"
            elif stress > 0.5:
                emotion = "Market Stress"
            elif abs(daily_return) < 1:
                emotion = "Market Calm"
            else:
                emotion = "Market Normal"
            emotions.append(emotion)
        
        ticker_data['market_emotion'] = emotions
        return ticker_data
    
    def cluster_behavioral_emotions(self, behavioral_features, n_clusters=4):
        """Cluster behavioral data to find emotional patterns"""
        from sklearn.preprocessing import StandardScaler
        
        # Prepare features (exclude labels)
        clustering_features = behavioral_features.select_dtypes(include=[np.number])
        
        # Standardize
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(clustering_features.fillna(0))
        
        # Cluster
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(scaled_features)
        
        return clusters, kmeans