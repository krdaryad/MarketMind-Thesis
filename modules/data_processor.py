"""
Data Processing Module - Phase 1 & 2 Analysis
Handles data loading, cleaning, feature engineering, and transformation
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class DataProcessor:
    def __init__(self):
        self.df = None
        self.X_sample = None
        self.count_vect = None
        self.tfidf_vect = None
        self.tdm_df = None
        self.tfidf_df = None
        
    def load_data(self, filepath):
        """Load and prepare the dataset"""
        self.df = pd.read_csv(filepath)
        print(f"Loaded dataset: {self.df.shape}")
        
        # Create main dataframe with text and label
        X = self.df[['text', 'label']].copy()
        X['label_name'] = X['label'].map({1.0: 'positive', 0.0: 'neutral', -1.0: 'negative'})
        
        # Clean data
        X = X.dropna(subset=['text'])
        X = X.drop_duplicates(subset=['text'])
        
        # Create sample
        self.X_sample = X.sample(n=min(500, len(X)), random_state=42)
        
        return self.X_sample
    
    def create_features(self, df=None):
        """Create text-based features"""
        if df is None:
            df = self.X_sample
            
        # Feature creation
        df['text_length'] = df['text'].str.len()
        df['word_count'] = df['text'].str.split().str.len()
        df['avg_word_length'] = df['text_length'] / df['word_count']
        df['exclamation_count'] = df['text'].str.count('!')
        df['question_count'] = df['text'].str.count('\?')
        df['capital_ratio'] = df['text'].apply(
            lambda x: sum(1 for c in x if c.isupper()) / len(x) if len(x) > 0 else 0
        )
        
        return df
    
    def create_term_document_matrix(self, df=None, max_features=1000):
        """Create term-document matrix using CountVectorizer"""
        if df is None:
            df = self.X_sample
            
        self.count_vect = CountVectorizer(max_features=max_features, stop_words='english')
        X_counts = self.count_vect.fit_transform(df['text'])
        
        terms = self.count_vect.get_feature_names_out()
        self.tdm_df = pd.DataFrame(X_counts.toarray(), columns=terms, index=df.index)
        
        # Calculate term frequencies
        term_frequencies = np.asarray(X_counts.sum(axis=0)).flatten()
        
        return self.tdm_df, term_frequencies, self.count_vect
    
    def create_tfidf_matrix(self, df=None, max_features=1000):
        """Create TF-IDF matrix"""
        if df is None:
            df = self.X_sample
            
        self.tfidf_vect = TfidfVectorizer(max_features=max_features, stop_words='english')
        X_tfidf = self.tfidf_vect.fit_transform(df['text'])
        
        terms = self.tfidf_vect.get_feature_names_out()
        self.tfidf_df = pd.DataFrame(X_tfidf.toarray(), columns=terms, index=df.index)
        
        return self.tfidf_df, self.tfidf_vect
    
    def reduce_dimensions(self, X, method='pca', n_components=2):
        """Reduce dimensionality for visualization"""
        if method == 'pca':
            reducer = PCA(n_components=n_components, random_state=42)
        elif method == 'svd':
            reducer = TruncatedSVD(n_components=n_components, random_state=42)
        else:
            raise ValueError(f"Unknown method: {method}")
            
        X_reduced = reducer.fit_transform(X)
        return X_reduced, reducer