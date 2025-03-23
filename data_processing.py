import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from binance_api import BinanceAPI
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Class to process data from Binance API."""
    
    @staticmethod
    def process_24hr_ticker_data(data: List[Dict]) -> pd.DataFrame:
        """
        Process 24-hour ticker data into a DataFrame.
        
        Args:
            data (List[Dict]): Raw ticker data from Binance API
            
        Returns:
            pd.DataFrame: Processed DataFrame with relevant information
        """
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # Convert numeric columns
        numeric_columns = [
            'volume', 'quoteVolume', 'priceChange', 'priceChangePercent',
            'weightedAvgPrice', 'lastPrice', 'lastQty', 'openPrice',
            'highPrice', 'lowPrice', 'prevClosePrice', 'count'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Filter out non-standard trading pairs (keep only USDT pairs for simplicity)
        df = df[df['symbol'].str.endswith('USDT')]
        
        # Calculate additional metrics
        df['baseAsset'] = df['symbol'].str.replace('USDT', '')
        
        return df
    
    @staticmethod
    def process_weekly_data(symbols: List[str]) -> pd.DataFrame:
        """
        Fetch and process 7-day data for given symbols.
        
        Args:
            symbols (List[str]): List of trading pair symbols
            
        Returns:
            pd.DataFrame: DataFrame with 7-day volume and price change data
        """
        results = []
        
        for symbol in symbols:
            klines = BinanceAPI.fetch_klines(symbol, interval="1d", limit=7)
            
            if not klines:
                continue
                
            # Calculate 7-day volume and price change
            try:
                volumes = [float(k[5]) for k in klines]  # Volume is at index 5
                prices = [float(k[4]) for k in klines]   # Close price is at index 4
                
                total_volume = sum(volumes)
                price_change = ((prices[-1] - prices[0]) / prices[0]) * 100 if prices[0] > 0 else 0
                
                results.append({
                    'symbol': symbol,
                    'volume_7d': total_volume,
                    'price_change_7d': price_change
                })
            except (IndexError, ValueError) as e:
                logger.error(f"Error processing weekly data for {symbol}: {e}")
        
        return pd.DataFrame(results) if results else pd.DataFrame()
    
    @staticmethod
    def get_top_volume_coins(period: str = '24h', limit: int = 20) -> pd.DataFrame:
        """
        Get top coins by trading volume.
        
        Args:
            period (str): Time period ('24h' or '7d')
            limit (int): Number of top coins to return
            
        Returns:
            pd.DataFrame: DataFrame with top volume coins
        """
        if period == '24h':
            # Get 24-hour data
            ticker_data = BinanceAPI.fetch_24hr_ticker_data()
            if not ticker_data:
                return pd.DataFrame()
            
            df = DataProcessor.process_24hr_ticker_data(ticker_data)
            
            if df.empty:
                return df
                
            # Sort by quote volume (USDT volume)
            df = df.sort_values(by='quoteVolume', ascending=False).head(limit)
            
            # Select and rename columns for display
            result = df[['symbol', 'baseAsset', 'lastPrice', 'priceChangePercent', 'quoteVolume', 'volume']]
            result = result.rename(columns={
                'baseAsset': 'Coin',
                'lastPrice': 'Price (USDT)',
                'priceChangePercent': 'Change 24h (%)',
                'quoteVolume': 'Volume (USDT)',
                'volume': 'Volume (Coin)'
            })
            
            return result
            
        elif period == '7d':
            # Get 24-hour data first to determine top coins
            ticker_data = BinanceAPI.fetch_24hr_ticker_data()
            if not ticker_data:
                return pd.DataFrame()
                
            df_24h = DataProcessor.process_24hr_ticker_data(ticker_data)
            
            if df_24h.empty:
                return df_24h
                
            # Get top symbols by 24h volume
            top_symbols = df_24h.sort_values(by='quoteVolume', ascending=False).head(limit)['symbol'].tolist()
            
            # Get 7-day data for these symbols
            df_7d = DataProcessor.process_weekly_data(top_symbols)
            
            if df_7d.empty:
                return df_7d
                
            # Merge with 24h data to get complete information
            result = pd.merge(
                df_24h[['symbol', 'baseAsset', 'lastPrice', 'quoteVolume']], 
                df_7d, 
                on='symbol', 
                how='inner'
            )
            
            # Sort by 7-day volume
            result = result.sort_values(by='volume_7d', ascending=False).head(limit)
            
            # Select and rename columns for display
            result = result[['symbol', 'baseAsset', 'lastPrice', 'price_change_7d', 'volume_7d']]
            result = result.rename(columns={
                'baseAsset': 'Coin',
                'lastPrice': 'Price (USDT)',
                'price_change_7d': 'Change 7d (%)',
                'volume_7d': 'Volume 7d (USDT)'
            })
            
            return result
        
        return pd.DataFrame()
