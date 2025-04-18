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
        Process 24-hour ticker data into a DataFrame for Binance Futures.
        
        Args:
            data (List[Dict]): Raw ticker data from Binance Futures API
            
        Returns:
            pd.DataFrame: Processed DataFrame with relevant information
        """
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # Convert numeric columns - column names may be different in futures API
        numeric_columns = [
            'volume', 'quoteVolume', 'priceChange', 'priceChangePercent',
            'weightedAvgPrice', 'lastPrice', 'lastQty', 'openPrice',
            'highPrice', 'lowPrice', 'prevClosePrice', 'count', 
            'baseVolume', 'quoteVolume'
        ]
        
        # In futures API the volume fields might have different names
        if 'baseVolume' in df.columns and 'volume' not in df.columns:
            df['volume'] = df['baseVolume']
            
        if 'quoteVolume' not in df.columns and 'volume' in df.columns and 'lastPrice' in df.columns:
            # If quoteVolume is missing, calculate it
            df['quoteVolume'] = df['volume'] * df['lastPrice']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # In futures market, most pairs are perpetual contracts ending with USDT
        df = df[df['symbol'].str.endswith('USDT') | df['symbol'].str.endswith('BUSD') | df['symbol'].str.contains('USDT_')]
        
        # Extract the base asset (e.g., BTC from BTCUSDT)
        # Futures symbols may have different patterns (like BTCUSDT_PERP)
        df['baseAsset'] = df['symbol'].str.replace('USDT$|BUSD$|USDT_.*$|BUSD_.*$', '', regex=True)
        
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
        
    @staticmethod
    def get_high_volume_change_coins(min_volume: float = 10000000.0, limit: int = 20) -> pd.DataFrame:
        """
        Get coins with the highest 24-hour price change percentage that also have more than
        the specified minimum volume in USDT.
        
        Args:
            min_volume (float): Minimum 24-hour USDT volume threshold (default: 10 million USDT)
            limit (int): Number of top coins to return
            
        Returns:
            pd.DataFrame: DataFrame with high volume change coins
        """
        # Get 24-hour data
        ticker_data = BinanceAPI.fetch_24hr_ticker_data()
        if not ticker_data:
            return pd.DataFrame()
        
        df = DataProcessor.process_24hr_ticker_data(ticker_data)
        
        if df.empty:
            return df
        
        # Log volume statistics to help debug
        logger.info(f"Total pairs: {len(df)}")
        logger.info(f"Max volume: {df['quoteVolume'].max():.2f} USDT")
        logger.info(f"Min volume: {df['quoteVolume'].min():.2f} USDT")
        logger.info(f"Median volume: {df['quoteVolume'].median():.2f} USDT")
        logger.info(f"Pairs with > {min_volume} USDT volume: {len(df[df['quoteVolume'] >= min_volume])}")
            
        # Check if requested minimum volume is too high for current market conditions
        max_available_volume = df['quoteVolume'].max()
        
        # Filter by minimum volume
        if max_available_volume < min_volume:
            # Requested volume threshold is higher than any available pair
            logger.warning(f"Requested min volume {min_volume} USDT is higher than max available volume {max_available_volume:.2f} USDT")
            
            # Use top 25% by volume instead
            adjusted_min_volume = df['quoteVolume'].quantile(0.75)
            logger.info(f"Using adjusted minimum volume: {adjusted_min_volume:.2f} USDT")
            high_volume_df = df[df['quoteVolume'] >= adjusted_min_volume]
            
            # Store the adjusted minimum volume to display in UI
            df.attrs['adjusted_min_volume'] = adjusted_min_volume
            df.attrs['used_adjusted_volume'] = True
        else:
            # Use the requested minimum volume
            high_volume_df = df[df['quoteVolume'] >= min_volume]
            df.attrs['used_adjusted_volume'] = False
            
        # If still empty (which shouldn't happen with the quantile approach), use top 20 pairs
        if high_volume_df.empty:
            logger.warning("Still no pairs after adjustment, using top 20 by volume")
            high_volume_df = df.sort_values(by='quoteVolume', ascending=False).head(20)
            df.attrs['used_adjusted_volume'] = True
            
        # Sort by price change percentage (absolute value for largest changes in either direction)
        high_volume_df = high_volume_df.sort_values(by='priceChangePercent', ascending=False).head(limit)
        
        # Select and rename columns for display
        result = high_volume_df[['symbol', 'baseAsset', 'lastPrice', 'priceChangePercent', 'quoteVolume']]
        result = result.rename(columns={
            'baseAsset': 'Coin',
            'lastPrice': 'Price (USDT)',
            'priceChangePercent': 'Change 24h (%)',
            'quoteVolume': 'Volume (USDT)'
        })
        
        return result
