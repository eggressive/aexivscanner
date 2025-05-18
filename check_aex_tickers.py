#!/usr/bin/env python3
"""
AEX Index Ticker Checker - Lists and validates all AEX tickers using yfinance

This script helps troubleshoot ticker issues by:
1. Attempting to fetch the actual AEX Index components directly from Yahoo Finance
2. Retrieving data for each common ticker to validate its existence
3. Displaying detailed information about each ticker's validity
"""

import yfinance as yf
import pandas as pd
import time
import random
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
import logging
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# AEX index ticker
AEX_INDEX_TICKER = "^AEX"

# Known typical AEX tickers to check
TYPICAL_AEX_TICKERS = [
    "ADYEN.AS", "ASML.AS", "AD.AS", "AKZA.AS", "ABN.AS", "DSM.AS", 
    "HEIA.AS", "IMCD.AS", "INGA.AS", "KPN.AS", "NN.AS", "PHIA.AS", 
    "RAND.AS", "REN.AS", "WKL.AS", "URW.AS", "UNA.AS", "MT.AS", 
    "RDSA.AS", "PRX.AS", "LIGHT.AS", "AGN.AS", "TKWY.AS",
    # Alternative Shell tickers that might be valid
    "SHEL.AS", "SHELL.AS"
]

def validate_ticker(ticker, max_retries=3):
    """Validate a ticker and return its data with detailed information"""
    print(f"\n{Fore.CYAN}Checking {ticker}...{Style.RESET_ALL}")
    
    retries = 0
    while retries <= max_retries:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check if we received meaningful data
            if info and len(info) > 5:
                # Extract key information
                name = info.get('shortName', info.get('longName', 'Unknown'))
                price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
                market_cap = info.get('marketCap', 'N/A')
                currency = info.get('currency', 'N/A')
                exchange = info.get('exchange', 'N/A')
                
                if market_cap != 'N/A':
                    market_cap_str = f"{market_cap / 1_000_000_000:.2f} billion {currency}"
                else:
                    market_cap_str = 'N/A'
                
                print(f"{Fore.GREEN}✓ Valid ticker!{Style.RESET_ALL}")
                print(f"  Company: {Fore.YELLOW}{name}{Style.RESET_ALL}")
                print(f"  Price: {price} {currency}")
                print(f"  Market Cap: {market_cap_str}")
                print(f"  Exchange: {exchange}")
                print(f"  Data points: {len(info)}")
                
                return {
                    "ticker": ticker,
                    "valid": True,
                    "name": name,
                    "price": price,
                    "market_cap": market_cap,
                    "currency": currency,
                    "exchange": exchange,
                    "data_points": len(info)
                }
            else:
                if retries < max_retries:
                    retries += 1
                    wait_time = 2 * (2 ** retries) * (1 + random.random())
                    print(f"{Fore.YELLOW}⚠️ Insufficient data. Retrying in {wait_time:.2f}s (attempt {retries}/{max_retries}){Style.RESET_ALL}")
                    time.sleep(wait_time)
                else:
                    print(f"{Fore.RED}❌ Got response but with insufficient data{Style.RESET_ALL}")
                    return {
                        "ticker": ticker,
                        "valid": False,
                        "error": "Insufficient data",
                        "data_points": len(info) if info else 0
                    }
        except (ConnectionError, Timeout, HTTPError) as e:
            if retries < max_retries:
                retries += 1
                wait_time = 3 * (2 ** retries) * (1 + random.random())
                print(f"{Fore.YELLOW}⚠️ Connection error: {str(e)}. Retrying in {wait_time:.2f}s (attempt {retries}/{max_retries}){Style.RESET_ALL}")
                time.sleep(wait_time)
            else:
                print(f"{Fore.RED}❌ Connection error: {str(e)}{Style.RESET_ALL}")
                return {
                    "ticker": ticker,
                    "valid": False,
                    "error": f"Connection error: {str(e)}"
                }
        except Exception as e:
            print(f"{Fore.RED}❌ Unexpected error: {str(e)}{Style.RESET_ALL}")
            return {
                "ticker": ticker,
                "valid": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    return {
        "ticker": ticker,
        "valid": False,
        "error": "Maximum retries exceeded"
    }

def try_get_index_components():
    """Attempt to get AEX components directly from Yahoo Finance"""
    print(f"\n{Fore.BLUE}Attempting to get AEX components directly from Yahoo Finance...{Style.RESET_ALL}")
    try:
        # Get AEX index data
        aex_index = yf.Ticker(AEX_INDEX_TICKER)
        
        # Try to get components (this may not work reliably)
        if hasattr(aex_index, 'components'):
            components = list(aex_index.components)
            print(f"{Fore.GREEN}Successfully retrieved {len(components)} components directly from Yahoo Finance!{Style.RESET_ALL}")
            return components
        elif hasattr(aex_index.info, 'components'):
            components = list(aex_index.info['components'])
            print(f"{Fore.GREEN}Successfully retrieved {len(components)} components from index info!{Style.RESET_ALL}")
            return components
        else:
            print(f"{Fore.RED}Could not get components directly - API doesn't provide this data{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}Error getting index components: {str(e)}{Style.RESET_ALL}")
        return None

def check_all_tickers():
    """Check and validate all potential AEX tickers"""
    # First try to get components directly (though this often doesn't work)
    direct_components = try_get_index_components()
    
    # Either use direct components or fall back to our typical list
    tickers_to_check = direct_components or TYPICAL_AEX_TICKERS
    
    print(f"\n{Fore.BLUE}Checking {len(tickers_to_check)} potential AEX tickers...{Style.RESET_ALL}")
    
    results = {
        "valid": [],
        "invalid": []
    }
    
    # Track all unique valid tickers
    all_valid_tickers = set()
    
    # Validate each ticker
    for ticker in tickers_to_check:
        # Add small delay to avoid rate limiting
        time.sleep(0.5)
        
        result = validate_ticker(ticker)
        if result["valid"]:
            results["valid"].append(result)
            all_valid_tickers.add(ticker)
        else:
            results["invalid"].append(result)
    
    # Print summary
    print(f"\n{Fore.BLUE}===== SUMMARY ====={Style.RESET_ALL}")
    print(f"Found {len(results['valid'])} valid tickers out of {len(tickers_to_check)} checked")
    
    # Print valid tickers
    print(f"\n{Fore.GREEN}Valid AEX Tickers:{Style.RESET_ALL}")
    for i, result in enumerate(results['valid'], 1):
        print(f"{i}. {result['ticker']}: {result['name']} - {result['price']} {result['currency']}")
    
    # Print invalid tickers
    print(f"\n{Fore.RED}Invalid or Problematic Tickers:{Style.RESET_ALL}")
    for i, result in enumerate(results['invalid'], 1):
        print(f"{i}. {result['ticker']}: {result.get('error', 'Unknown error')}")
    
    print(f"\n{Fore.YELLOW}Recommended JSON configuration:{Style.RESET_ALL}")
    print(f"{{")
    print(f'    "AEX_TICKERS": [')
    print(f"        " + ",\n        ".join([f'"{ticker}"' for ticker in all_valid_tickers]))
    print(f"    ]")
    print(f"}}")

if __name__ == "__main__":
    check_all_tickers()
