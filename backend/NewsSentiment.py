
import numpy as np

from newsapi import NewsApiClient
from transformers import pipeline
from datetime import datetime, timedelta

import plotly.graph_objects as go

from backend.configuration import NEWSAPI_KEY


class MarketSentiment:
    
    def __init__(self):
        
        self._wordList = list()
        self._sentimentDict = dict()
        
        self.newsapi = NewsApiClient(api_key=NEWSAPI_KEY)  
        self.sentiment_classifier = pipeline("sentiment-analysis", 
                                             model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
        return
    
    
    def addWord(self, word):
        
        if isinstance(word, str):
            if word not in self._wordList:
                self._wordList.append(word)
        else:
            raise ValueError("Only strings are allowed as words.")
        
        if word not in self._sentimentDict:
            self._computeWordSentiment(word)
        
        return
    
    
    def removeWord(self, word):
        
        if word in self._wordList:
            self._wordList.remove(word)
        
        return
    
    
    def getSentiment(self):
        return self._sentimentDict
    
    
    def _computeWordSentiment(self, word):
        
        end_date = datetime.now()
        start_date = datetime.now()-timedelta(days=7)
        
        all_articles = self.newsapi.get_everything(q=word,
                                              from_param=start_date,
                                              to=end_date,
                                              language='en',
                                              sort_by='relevancy')
        
        s = list()
        
        for article in all_articles['articles']:
            
            try:
                sentiment_string = article['title']+'. '+article['description']+'. '+article['content']
            except:
                continue
                
            if word.lower() not in sentiment_string.lower():
                continue
            sentiment = self.sentiment_classifier(sentiment_string)
            #print(sentiment_string,"\n",sentiment,"\n")
            
            s.append(sentiment[0]['label'])
            
        self._sentimentDict[word] = s




class SentimentBullet:
    
    def __init__(self, sentimentDict):
        self.sentimentDict = sentimentDict
        self.fig = None
        self._generate_plot()
        return
    
    def _generate_plot(self):
        
        map_sentiment = {'positive':1,'neutral':0,'negative':-1}
        
        fig = go.Figure()
        
        i = 0
        
        for word in self.sentimentDict:
            
            s = self.sentimentDict[word]
            
            if len(s)==0:
                continue
              
            fig.add_trace(go.Indicator(
                mode = "delta", value = np.mean([map_sentiment[x] for x in s]),
                delta = {'reference': 0},
                domain = {'x': [0, 0.2], 'y': [i*0.2+0.1, (i+1)*0.2]},
                title = {'text': word},
                gauge = {
                    'shape': "bullet",
                    'axis': {'range': [-1, 1]},
                    'threshold': {
                        'line': {'color': "black", 'width': 2},
                        'thickness': 0.75,
                        'value': 0},
                    'steps': [
                        {'range': [-1, -0.6], 'color': "red"},
                        {'range': [-0.6, -0.2], 'color': "orange"},
                        {'range': [-0.2, 0.2], 'color': "yellow"},
                        {'range': [0.2, 0.6], 'color': "yellowgreen"},
                        {'range': [0.6, 1], 'color': "green"}],
                    'bar': {'color': "black"}})

            )
            i+=1
            
        
        fig.update_layout(height=400, width=200, margin={'t':0, 'b':0, 'l':0})
        
        self.fig = fig
        
        return