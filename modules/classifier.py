"""
model trainiing Naive Bayes, Decision Trees, and evaluation
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class SentimentClassifier:
    def __init__(self):
        self.models = {}
        self.results = {}
        
    def prepare_data(self, X, y, test_size=0.3):
        """splitin data for training and testing"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        return X_train, X_test, y_train, y_test
    
    def train_multinomial_nb(self, X_train, y_train):
        """training Multinomial Naive Bayes (for count data)"""
        model = MultinomialNB()
        model.fit(X_train, y_train)
        return model
    
    def train_gaussian_nb(self, X_train, y_train):
        """training Gaussian Naive Bayes (for TF-IDF data)"""
        model = GaussianNB()
        model.fit(X_train, y_train)
        return model
    
    def train_decision_tree(self, X_train, y_train, max_depth=20):
        """Train Decision Tree classifier"""
        model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
        model.fit(X_train, y_train)
        return model
    
    def evaluate_model(self, model, X_test, y_test):
        """evaluating model and returning metrics"""
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        cm = confusion_matrix(y_test, y_pred)
        
        return {
            'accuracy': accuracy,
            'report': report,
            'confusion_matrix': cm,
            'predictions': y_pred
        }
    
    def compare_models(self, X_tdm, X_tfidf, y):
        """comparing all models on different feature types"""
        results = {}
      
        X_tdm_train, X_tdm_test, y_train, y_test = self.prepare_data(X_tdm, y)  #splits
        X_tfidf_train, X_tfidf_test, _, _ = self.prepare_data(X_tfidf, y)
        
        # mltinomial NB on TDM, same further
        mnb = self.train_multinomial_nb(X_tdm_train, y_train)
        results['Multinomial NB (TDM)'] = self.evaluate_model(mnb, X_tdm_test, y_test)
        
        gnb = self.train_gaussian_nb(X_tfidf_train, y_train)
        results['Gaussian NB (TF-IDF)'] = self.evaluate_model(gnb, X_tfidf_test, y_test)
        
        dt_tdm = self.train_decision_tree(X_tdm_train, y_train)
        results['Decision Tree (TDM)'] = self.evaluate_model(dt_tdm, X_tdm_test, y_test)
        
        dt_tfidf = self.train_decision_tree(X_tfidf_train, y_train)
        results['Decision Tree (TF-IDF)'] = self.evaluate_model(dt_tfidf, X_tfidf_test, y_test)
        
        self.results = results
        return results
    
    def get_best_model(self):
        """return the best performing model"""
        best = max(self.results.items(), key=lambda x: x[1]['accuracy'])
        return best[0], best[1]['accuracy']
    
    def plot_confusion_matrix(self, cm, labels=['negative', 'neutral', 'positive'], title='Confusion Matrix'):
        """plotting confusion matrix visualization"""
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=labels, yticklabels=labels, ax=ax)
        ax.set_title(title)
        ax.set_ylabel('True Label')
        ax.set_xlabel('Predicted Label')
        return fig