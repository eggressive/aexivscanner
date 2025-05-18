#!/usr/bin/env python3
"""
Test script to validate Yahoo Finance tickers with improved retry logic

Usage:
    python test_ticker_validation.py ASML.AS INGA.AS MT.AS  # Test specific tickers
    python test_ticker_validation.py --verbose ASML.AS      # Show detailed information
    python test_ticker_validation.py --all                  # Test all tickers from CSV
    python test_ticker_validation.py --all --wait 2         # Customize wait time between tests
    
Options:
    --verbose, -v  : Show detailed ticker information
    --all, -a      : Test all tickers from amsterdam_aex_tickers.csv
    --wait, -w     : Set wait time between tests (default: 3s)
"""

import logging
import time
import random
import sys
import argparse
import os
import csv
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

def validate_ticker_with_retries(ticker, verbose=False):
    """
    Validate a ticker with robust retry logic
    
    Args:
        ticker (str): The ticker symbol to validate
        verbose (bool): Whether to print detailed information about the ticker
        
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
                
                # Print additional info if verbose mode is enabled
                if verbose and info:
                    print("\nDetailed information:")
                    print(f"  Full Name: {info.get('longName', 'N/A')}")
                    print(f"  Sector: {info.get('sector', 'N/A')}")
                    print(f"  Industry: {info.get('industry', 'N/A')}")
                    print(f"  Website: {info.get('website', 'N/A')}")
                    print(f"  Market Cap: {info.get('marketCap', 'N/A')}")
                    print(f"  52 Week High: {info.get('fiftyTwoWeekHigh', 'N/A')}")
                    print(f"  52 Week Low: {info.get('fiftyTwoWeekLow', 'N/A')}")
                    
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

def load_all_tickers():
    """
    Load all tickers from the amsterdam_aex_tickers.csv file
    
    Returns:
        list: List of ticker symbols
    """
    csv_file = os.path.join(os.path.dirname(__file__), 'amsterdam_aex_tickers.csv')
    tickers = []
    
    if not os.path.exists(csv_file):
        logger.error(f"CSV file not found: {csv_file}")
        return tickers
    
    try:
        with open(csv_file, 'r') as f:
            # Skip lines that start with //
            while True:
                pos = f.tell()
                line = f.readline()
                if not line or not line.startswith('//'):
                    f.seek(pos)
                    break
            
            # Parse the CSV content
            reader = csv.DictReader(f)
            for row in reader:
                if 'yahoo_ticker' in row and row['yahoo_ticker'].strip():
                    tickers.append(row['yahoo_ticker'].strip())
        
        logger.info(f"Loaded {len(tickers)} tickers from {csv_file}")
    except Exception as e:
        logger.error(f"Error loading tickers from CSV: {str(e)}")
    
    return tickers

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Test script to validate Yahoo Finance tickers")
    parser.add_argument("tickers", nargs="*", help="One or more ticker symbols to validate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed information for each ticker")
    parser.add_argument("--all", "-a", action="store_true", help="Validate all tickers from amsterdam_aex_tickers.csv")
    parser.add_argument("--wait", "-w", type=float, default=3.0, 
                      help="Wait time in seconds between ticker validations (default: 3.0)")
    args = parser.parse_args()
    
    # Determine which tickers to test
    tickers_to_test = []
    
    # Check for --all or specific tickers
    if args.all:
        print("Loading all tickers from CSV file...")
        tickers_to_test = load_all_tickers()
        if not tickers_to_test:
            print("❌ No tickers found in the CSV file. Please run euronext_tickers.py first.")
            sys.exit(1)
    elif args.tickers:
        tickers_to_test = args.tickers
    else:
        parser.print_help()
        print("\nError: You must specify at least one ticker symbol or use the --all flag")
        sys.exit(1)
    
    print(f"Will validate {len(tickers_to_test)} tickers" + 
          (f" with {args.wait}s delay between tests" if len(tickers_to_test) > 1 else ""))
    
    # Track results
    results = {
        "success": [],
        "failed": []
    }
    
    # Test each ticker with improved validation
    for ticker in tickers_to_test:
        print(f"\n{'=' * 50}")
        print(f"Testing ticker: {ticker}")
        print(f"{'=' * 50}")
        
        success = validate_ticker_with_retries(ticker, verbose=args.verbose)
        
        print(f"Result: {'✅ Success' if success else '❌ Failed'}")
        
        # Track result
        if success:
            results["success"].append(ticker)
        else:
            results["failed"].append(ticker)
        
        # Wait between tests to avoid rate limiting (only if more tickers to test)
        if ticker != tickers_to_test[-1] and args.wait > 0:
            print(f"Waiting {args.wait}s before next ticker...")
            time.sleep(args.wait)
    
    # Print summary
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    print(f"✅ Successful: {len(results['success'])}/{len(tickers_to_test)}")
    print(f"❌ Failed: {len(results['failed'])}/{len(tickers_to_test)}")
    
    if results["failed"]:
        print("\nFailed tickers:")
        for ticker in results["failed"]:
            print(f"  - {ticker}")
    
    if not results["success"] and results["failed"]:
        sys.exit(1)  # Exit with error if all tickers failed
