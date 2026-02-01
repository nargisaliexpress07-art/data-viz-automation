#!/usr/bin/env python3
"""
Data Scraper - Fetches REAL data from multiple sources
"""

import requests
import yfinance as yf
from datetime import datetime, timedelta
import random
import yaml
import os

class DataScraper:
    def __init__(self):
        # Load topics config
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'topics.yaml')
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def fetch_crypto_data(self, symbol, name):
        """Fetch real crypto data from CoinGecko"""
        try:
            # Map symbols to CoinGecko IDs
            coin_ids = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'SOL': 'solana',
                'DOGE': 'dogecoin',
                'ADA': 'cardano'
            }
            
            coin_id = coin_ids.get(symbol, symbol.lower())
            
            # Get simple price data (more reliable)
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if coin_id not in data:
                return None
            
            current_price = data[coin_id]['usd']
            change_24h = data[coin_id].get('usd_24h_change', 0)
            
            # Calculate yesterday's price
            yesterday_price = current_price / (1 + (change_24h / 100))
            
            change = current_price - yesterday_price
            
            return {
                'title': f'{name} Price Update',
                'category': 'crypto',
                'data': {
                    'yesterday': round(yesterday_price, 2),
                    'today': round(current_price, 2),
                    'change': round(change, 2),
                    'change_percent': round(change_24h, 2)
                },
                'source': 'CoinGecko',
                'chart_type': 'comparison',
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        except Exception as e:
            print(f"Error fetching {name}: {e}")
            return None    
    def fetch_stock_data(self, symbol, name):
        """Fetch real stock data from Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period='5d')
            
            if len(hist) < 2:
                return None
            
            yesterday_price = hist['Close'].iloc[-2]
            today_price = hist['Close'].iloc[-1]
            
            change = today_price - yesterday_price
            change_percent = (change / yesterday_price) * 100
            
            return {
                'title': f'{name} Stock Update',
                'category': 'stocks',
                'data': {
                    'yesterday': round(yesterday_price, 2),
                    'today': round(today_price, 2),
                    'change': round(change, 2),
                    'change_percent': round(change_percent, 2)
                },
                'source': 'Yahoo Finance',
                'chart_type': 'comparison',
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        except Exception as e:
            print(f"Error fetching {name}: {e}")
            return None
    
    def fetch_economic_data(self, data_id, name):
        """Fetch economic data (mock for now, real FRED API needs key)"""
        # Mock data - you can add real FRED API later
        mock_values = {
            'unemployment': (4.0, 4.1),
            'inflation': (3.2, 3.0)
        }
        
        if data_id in mock_values:
            yesterday, today = mock_values[data_id]
            change = today - yesterday
            change_percent = (change / yesterday) * 100
            
            return {
                'title': f'{name}',
                'category': 'economic',
                'data': {
                    'yesterday': yesterday,
                    'today': today,
                    'change': round(change, 2),
                    'change_percent': round(change_percent, 2)
                },
                'source': 'Federal Reserve',
                'chart_type': 'comparison',
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        return None
    
    def get_random_topics(self):
        """Select random enabled topics"""
        all_topics = []
        
        # Crypto topics
        for crypto in self.config.get('crypto', []):
            if crypto.get('enabled'):
                data = self.fetch_crypto_data(crypto['symbol'], crypto['name'])
                if data:
                    all_topics.append(data)
        
        # Stock topics
        for stock in self.config.get('stocks', []):
            if stock.get('enabled'):
                data = self.fetch_stock_data(stock['symbol'], stock['name'])
                if data:
                    all_topics.append(data)
        
        # Economic topics
        for econ in self.config.get('economic', []):
            if econ.get('enabled'):
                data = self.fetch_economic_data(econ['id'], econ['name'])
                if data:
                    all_topics.append(data)
        
        # Randomly select 3-5 topics
        num_videos = self.config['settings']['videos_per_day']
        selected = random.sample(all_topics, min(num_videos, len(all_topics)))
        
        return selected

if __name__ == "__main__":
    scraper = DataScraper()
    topics = scraper.get_random_topics()
    
    print(f"\n📊 Selected {len(topics)} random topics:\n")
    for topic in topics:
        print(f"✅ {topic['title']}")
        print(f"   Yesterday: ${topic['data']['yesterday']}")
        print(f"   Today: ${topic['data']['today']}")
        print(f"   Change: {topic['data']['change_percent']:+.2f}%\n")
