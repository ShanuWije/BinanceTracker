import requests
import pandas as pd
import time
import hmac
import hashlib
import os
from typing import Dict, List, Optional, Tuple, Union
import logging
from urllib.parse import urlencode

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceAPI:
    """Class to interact with the Binance Futures API."""
    
    # Use Binance Futures API
    BASE_URL = "https://fapi.binance.com/fapi/v1"
    
    # Get API credentials from environment variables
    API_KEY = os.environ.get("BINANCE_API_KEY", "")
    API_SECRET = os.environ.get("BINANCE_API_SECRET", "")
    
    @staticmethod
    def _get_signature(query_string: str) -> str:
        """
        Generate HMAC SHA256 signature for the request.
        
        Args:
            query_string (str): The query string to sign
            
        Returns:
            str: The signature
        """
        return hmac.new(
            BinanceAPI.API_SECRET.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def _create_auth_headers():
        """
        Create authentication headers for the request.
        
        Returns:
            dict: Headers with authentication information
        """
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'X-MBX-APIKEY': BinanceAPI.API_KEY
        }
    
    @staticmethod
    def fetch_24hr_ticker_data() -> Optional[List[Dict]]:
        """
        Fetch 24-hour price statistics for all symbols.
        
        Returns:
            Optional[List[Dict]]: List of ticker data or None if request fails
        """
        # Check if API credentials are available
        if not BinanceAPI.API_KEY or not BinanceAPI.API_SECRET:
            logger.error("API credentials missing. Please set BINANCE_API_KEY and BINANCE_API_SECRET environment variables.")
            return None
            
        endpoint = f"{BinanceAPI.BASE_URL}/ticker/24hr"
        
        try:
            # Get authentication headers
            headers = BinanceAPI._create_auth_headers()
            
            # Log the request attempt
            logger.info(f"Attempting to fetch data from {endpoint}")
            
            # Create timestamp for authentication
            timestamp = int(time.time() * 1000)
            params = {'timestamp': timestamp}
            
            # Create query string for signature
            query_string = urlencode(params)
            
            # Generate signature and add to params
            signature = BinanceAPI._get_signature(query_string)
            params['signature'] = signature
            
            # Make the request
            response = requests.get(
                endpoint, 
                headers=headers, 
                params=params,
                timeout=10
            )
            
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
        # Check if API credentials are available
        if not BinanceAPI.API_KEY or not BinanceAPI.API_SECRET:
            logger.error("API credentials missing. Please set BINANCE_API_KEY and BINANCE_API_SECRET environment variables.")
            return None
            
        endpoint = f"{BinanceAPI.BASE_URL}/klines"
        
        try:
            # Get authentication headers
            headers = BinanceAPI._create_auth_headers()
            
            # Create params for the request
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit,
                "timestamp": int(time.time() * 1000)
            }
            
            # Log the request attempt
            logger.info(f"Attempting to fetch klines for {symbol} from {endpoint}")
            
            # Create query string for signature
            query_string = urlencode(params)
            
            # Generate signature and add to params
            signature = BinanceAPI._get_signature(query_string)
            params['signature'] = signature
            
            response = requests.get(
                endpoint, 
                params=params, 
                headers=headers, 
                timeout=10
            )
            
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
        # Check if API credentials are available
        if not BinanceAPI.API_KEY or not BinanceAPI.API_SECRET:
            logger.error("API credentials missing. Please set BINANCE_API_KEY and BINANCE_API_SECRET environment variables.")
            return None
            
        endpoint = f"{BinanceAPI.BASE_URL}/exchangeInfo"
        
        try:
            # Get authentication headers
            headers = BinanceAPI._create_auth_headers()
            
            # Log the request attempt
            logger.info(f"Attempting to fetch exchange info from {endpoint}")
            
            # Create timestamp for authentication
            timestamp = int(time.time() * 1000)
            params = {'timestamp': timestamp}
            
            # Create query string for signature
            query_string = urlencode(params)
            
            # Generate signature and add to params
            signature = BinanceAPI._get_signature(query_string)
            params['signature'] = signature
            
            response = requests.get(
                endpoint, 
                headers=headers, 
                params=params,
                timeout=10
            )
            
            # Log the response status
            logger.info(f"Response status code: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching exchange info: {e}")
            if hasattr(e, 'response') and e.response and hasattr(e.response, 'text'):
                logger.error(f"Response text: {e.response.text}")
            return None
