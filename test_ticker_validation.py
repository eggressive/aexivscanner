#!/usr/bin/env python3
"""
Test script to validate specific tickers with improved retry logic
"""

import logging
import time
import random
import yfinance as yf
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def validate_ticker_with_retries(ticker):
    """
    Validate a ticker with robust retry logic
    
    Args:
        ticker (str): The ticker symbol to validate
        
    Returns:
        bool: True if validation successful, False otherwise
    """
    max_retries = 3
    retries = 0
    validated = False
    
    while retries <= max_retries and not validated:
        try:
            logger.info(f"Attempting to validate {ticker} (attempt {retries + 1}/{max_retries + 1})...")
            stock = yf.Ticker(ticker)
            info = stock.info
            if info and 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
                logger.info(f"✅ Successfully validated ticker: {ticker}")
                logger.info(f"Market Price: {info.get('regularMarketPrice')}")
                logger.info(f"Company Name: {info.get('shortName', 'N/A')}")
                return True
            else:
                if retries < max_retries:
                    retries += 1
                    wait_time = 2 * (2 ** retries) * (1 + random.random())
                    logger.warning(f"⚠️ Could not validate ticker: {ticker}. Retrying in {wait_time:.2f}s")
                    time.sleep(wait_time)
                else:
                    logger.warning(f"❌ Could not validate ticker after {max_retries + 1} attempts: {ticker}")
                    return False
        except (ConnectionError, Timeout, HTTPError) as e:
            if retries < max_retries:
                retries += 1
                wait_time = 3 * (2 ** retries) * (1 + random.random())  # Longer wait for HTTP errors
                logger.warning(f"⚠️ Error validating ticker {ticker}: {str(e)}. Retrying in {wait_time:.2f}s")
                time.sleep(wait_time)
            else:
                logger.error(f"❌ Error validating ticker {ticker} after {max_retries + 1} attempts: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"❌ Unexpected error validating ticker {ticker}: {str(e)}")
            return False
    
    return validated

if __name__ == "__main__":
    # List of problematic tickers to test
    problematic_tickers = ["ASML.AS", "IMCD.AS", "INGA.AS", "MT.AS", "RDSA.AS", "TKWY.AS"]
    
    # Test each ticker with improved validation
    for ticker in problematic_tickers:
        print(f"\n{'=' * 50}")
        print(f"Testing ticker: {ticker}")
        print(f"{'=' * 50}")
        success = validate_ticker_with_retries(ticker)
        print(f"Result: {'Success' if success else 'Failed'}")
        # Wait between tests to avoid rate limiting
        time.sleep(3)
