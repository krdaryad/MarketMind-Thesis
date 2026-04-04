"""
Pattern Mining Module - Phase 2 Pattern Discovery
Implements FP-Growth and frequent pattern mining
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import warnings
warnings.filterwarnings('ignore')

class PatternMiner:
    def __init__(self):
        self.frequent_patterns = {}
        self.pattern_dfs = {}
        
    def create_term_document_df(self, df, max_features=500):
        """Create term-document matrix for pattern mining"""
        count_vect = CountVectorizer(max_features=max_features, stop_words='english')
        X_counts = count_vect.fit_transform(df['text'])
        words = count_vect.get_feature_names_out()
        term_document_df = pd.DataFrame(X_counts.toarray(), columns=words)
        return term_document_df, count_vect
    
    def filter_top_bottom_words(self, term_document_df, top_percent=0.05, bottom_percent=0.01):
        """Filter out extremely frequent and rare words"""
        word_sums = term_document_df.sum(axis=0)
        sorted_words = word_sums.sort_values()
        total_words = len(sorted_words)
        
        top_n = int(top_percent * total_words)
        bottom_n = int(bottom_percent * total_words)
        
        words_to_remove = pd.concat([sorted_words.head(bottom_n), sorted_words.tail(top_n)]).index
        return term_document_df.drop(columns=words_to_remove)
    
    def manual_frequent_pattern_mining(self, term_document_df, min_support=2):
        """Manual pattern mining for frequent itemsets"""
        patterns = []
        term_support = term_document_df.sum(axis=0)
        
        # Single terms
        for term in term_document_df.columns:
            support = term_support[term]
            if support >= min_support:
                patterns.append({
                    'Pattern': term,
                    'Support': support,
                    'Length': 1
                })
        
        # Word pairs (limited to avoid explosion)
        terms = list(term_document_df.columns)
        for i in range(min(len(terms), 50)):
            for j in range(i+1, min(len(terms), 50)):
                term1, term2 = terms[i], terms[j]
                co_occurrence = ((term_document_df[term1] > 0) & (term_document_df[term2] > 0)).sum()
                if co_occurrence >= min_support:
                    patterns.append({
                        'Pattern': f"{term1} {term2}",
                        'Support': co_occurrence,
                        'Length': 2
                    })
        
        return pd.DataFrame(patterns).sort_values('Support', ascending=False)
    
    def mine_patterns_by_sentiment(self, X_sample, min_support_dict=None):
        """Mine patterns separately for each sentiment category"""
        if min_support_dict is None:
            min_support_dict = {'positive': 3, 'neutral': 5, 'negative': 3}
        
        categories = X_sample['label_name'].unique()
        
        for category in categories:
            category_df = X_sample[X_sample['label_name'] == category].copy()
            
            # Create term-document matrix
            term_doc_df, _ = self.create_term_document_df(category_df)
            
            # Filter words
            filtered_df = self.filter_top_bottom_words(term_doc_df)
            
            # Mine patterns
            min_support = min_support_dict.get(category, 3)
            patterns_df = self.manual_frequent_pattern_mining(filtered_df, min_support)
            
            self.frequent_patterns[category] = patterns_df
            
        return self.frequent_patterns