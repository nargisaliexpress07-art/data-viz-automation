#!/usr/bin/env python3
"""
Data Scraper - Fetches economic data from public APIs
"""

import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class DataScraper:
    def __init__(self):
        self.data_sources = {
            'inflation': 'https://api.stlouisfed.org/fred/series/observations',
            'unemployment': 'https://api.stlouisfed.org/fred/series/observations',
            'gdp': 'https://api.stlouisfed.org/fred/series/observations'
        }
    
    def fetch_inflation_data(self):
        """Fetch latest inflation data"""
        # Using mock data for now (you can add real API later)
        return {
            'title': 'US Inflation Rate',
            'data': {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'values': [3.4, 3.2, 3.5, 3.4, 3.3, 3.0]
            },
            'source': 'Federal Reserve Economic Data',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'chart_type': 'line'
        }
    
    def fetch_unemployment_data(self):
        """Fetch latest unemployment data"""
        return {
            'title': 'US Unemployment Rate',
            'data': {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'values': [3.7, 3.9, 3.8, 3.9, 4.0, 4.1]
            },
            'source': 'Bureau of Labor Statistics',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'chart_type': 'line'
        }
    
    def fetch_stock_data(self):
        """Fetch stock market data"""
        return {
            'title': 'S&P 500 Performance',
            'data': {
                'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                'values': [4500, 4520, 4510, 4550, 4580]
            },
            'source': 'Yahoo Finance',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'chart_type': 'bar'
        }
    
    def get_daily_topics(self):
        """Get list of topics to create videos for"""
        topics = []
        
        # Only create videos on weekdays
        if True:  # Always generate topics (for testing)
            topics.append(self.fetch_inflation_data())
            topics.append(self.fetch_unemployment_data())
            topics.append(self.fetch_stock_data())
        
        return topics

if __name__ == "__main__":
    scraper = DataScraper()
    topics = scraper.get_daily_topics()
    
    print(f"Found {len(topics)} topics to create videos for:")
    for topic in topics:
        print(f"  - {topic['title']}")
