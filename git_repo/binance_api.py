import requests
import pandas as pd
import time
from typing import Dict, List, Optional, Tuple, Union
import logging
from urllib.parse import urlencode

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceAPI:
    """Class to interact with the Binance US public API."""
    
    # Use Binance US API (spot market)
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
            # Enhanced headers for better request handling
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # Log the request attempt
            logger.info(f"Attempting to fetch data from {endpoint}")
            
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            # Log the response status
            logger.info(f"Response status code: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching 24hr ticker data: {e}")
            if hasattr(e, 'response') and e.response and hasattr(e.response, 'text'):
                logger.error(f"Response text: {e.response.text}")
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
        
        try:
            # Create params for the request
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            # Enhanced headers for better request handling
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # Log the request attempt
            logger.info(f"Attempting to fetch klines for {symbol} from {endpoint}")
            
            response = requests.get(endpoint, params=params, headers=headers, timeout=10)
            
            # Log the response status
            logger.info(f"Response status code: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching klines for {symbol}: {e}")
            if hasattr(e, 'response') and e.response and hasattr(e.response, 'text'):
                logger.error(f"Response text: {e.response.text}")
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
            # Enhanced headers for better request handling
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # Log the request attempt
            logger.info(f"Attempting to fetch exchange info from {endpoint}")
            
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            # Log the response status
            logger.info(f"Response status code: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching exchange info: {e}")
            if hasattr(e, 'response') and e.response and hasattr(e.response, 'text'):
                logger.error(f"Response text: {e.response.text}")
            return None
