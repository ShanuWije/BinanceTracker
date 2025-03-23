import requests
import pandas as pd
import time
from typing import Dict, List, Optional, Tuple, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceAPI:
    """Class to interact with the Binance public API."""
    
    # Use Binance.US API as an alternative that may have fewer restrictions
    BASE_URL = "https://api.binance.us/api/v3"
    
    @staticmethod
    def fetch_24hr_ticker_data() -> Optional[List[Dict]]:
        """
        Fetch 24-hour price statistics for all symbols.
        
        Returns:
            Optional[List[Dict]]: List of ticker data or None if request fails
        """
        endpoint = f"{BinanceAPI.BASE_URL}/ticker/24hr"
        
        try:
            # Add user-agent header to avoid potential blockage
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching 24hr ticker data: {e}")
            return None
    
    @staticmethod
    def fetch_klines(symbol: str, interval: str, limit: int = 7) -> Optional[List[List]]:
        """
        Fetch kline/candlestick data for a symbol.
        
        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            interval (str): Kline interval (e.g., "1d" for daily)
            limit (int): Number of data points to retrieve
            
        Returns:
            Optional[List[List]]: List of kline data or None if request fails
        """
        endpoint = f"{BinanceAPI.BASE_URL}/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        try:
            # Add user-agent header to avoid potential blockage
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(endpoint, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching klines for {symbol}: {e}")
            return None
    
    @staticmethod
    def fetch_exchange_info() -> Optional[Dict]:
        """
        Fetch exchange information including trading pairs.
        
        Returns:
            Optional[Dict]: Exchange information or None if request fails
        """
        endpoint = f"{BinanceAPI.BASE_URL}/exchangeInfo"
        
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching exchange info: {e}")
            return None
