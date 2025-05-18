#!/usr/bin/env python3
"""
AEX Problematic Ticker Investigator - Detailed analysis of problematic ticker symbols

This script performs a deeper investigation of problematic tickers by:
1. Comparing old vs new tickers (e.g., RDSA.AS vs SHELL.AS)
2. Retrieving historic data availability
3. Testing different request patterns to diagnose API issues
4. Providing recommendations for ticker replacements
"""

import yfinance as yf
import pandas as pd
import time
import random
import json
import os
from datetime import datetime, timedelta
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

# Known problematic tickers and their potential replacements
PROBLEMATIC_TICKERS = {
    "RDSA.AS": ["SHELL.AS", "SHEL.AS"],  # Royal Dutch Shell is now Shell plc
    "DSM.AS": ["DSM.AS", "DSMN.AS"],    # DSM has merged with Firmenich to become DSM-Firmenich
    "URW.AS": ["URW.AS", "UNBP.AS"]     # Unibail-Rodamco-Westfield
}

def validate_ticker_deeply(ticker, max_retries=3):
    """Perform a deep validation of a ticker with multiple data points"""
    print(f"\n{Fore.CYAN}Deep validation of {ticker}...{Style.RESET_ALL}")
    
    result = {
        "ticker": ticker,
        "basic_info_valid": False,
        "historic_data_valid": False,
        "company_name": None,
        "errors": []
    }
    
    # 1. Try to get basic info
    retries = 0
    while retries <= max_retries:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check if we received meaningful data
            if info and len(info) > 10:  # More strict check for deep validation
                result["basic_info_valid"] = True
                result["company_name"] = info.get('shortName', info.get('longName', 'Unknown'))
                result["price"] = info.get('currentPrice', info.get('regularMarketPrice'))
                result["currency"] = info.get('currency')
                result["market_cap"] = info.get('marketCap')
                result["data_points"] = len(info)
                break
            else:
                if retries < max_retries:
                    retries += 1
                    wait_time = 2 * (2 ** retries) * (1 + random.random())
                    print(f"  ⚠️ Basic info insufficient. Retrying in {wait_time:.2f}s (attempt {retries}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    result["errors"].append("Insufficient basic info data")
                    print(f"  {Fore.RED}❌ Could not get sufficient basic info{Style.RESET_ALL}")
        except Exception as e:
            if retries < max_retries:
                retries += 1
                wait_time = 3 * (2 ** retries) * (1 + random.random())
                print(f"  ⚠️ Error getting basic info: {str(e)}. Retrying in {wait_time:.2f}s")
                time.sleep(wait_time)
            else:
                result["errors"].append(f"Basic info error: {str(e)}")
                print(f"  {Fore.RED}❌ Error getting basic info: {str(e)}{Style.RESET_ALL}")
                break
    
    # 2. Try to get historical data (better indicator of a valid ticker)
    retries = 0
    while retries <= max_retries:
        try:
            stock = yf.Ticker(ticker)
            # Get 1 month of historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            hist = stock.history(start=start_date, end=end_date)
            
            if not hist.empty and len(hist) > 5:
                result["historic_data_valid"] = True
                result["historic_data_days"] = len(hist)
                result["latest_close"] = hist['Close'].iloc[-1] if 'Close' in hist.columns else None
                break
            else:
                if retries < max_retries:
                    retries += 1
                    wait_time = 2 * (2 ** retries) * (1 + random.random())
                    print(f"  ⚠️ No historical data. Retrying in {wait_time:.2f}s (attempt {retries}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    result["errors"].append("No historical data available")
                    print(f"  {Fore.RED}❌ No historical data available{Style.RESET_ALL}")
        except Exception as e:
            if retries < max_retries:
                retries += 1
                wait_time = 3 * (2 ** retries) * (1 + random.random())
                print(f"  ⚠️ Error getting historical data: {str(e)}. Retrying in {wait_time:.2f}s")
                time.sleep(wait_time)
            else:
                result["errors"].append(f"Historical data error: {str(e)}")
                print(f"  {Fore.RED}❌ Error getting historical data: {str(e)}{Style.RESET_ALL}")
                break
    
    # 3. Determine overall validity
    result["valid"] = result["basic_info_valid"] and result["historic_data_valid"]
    
    # Print summary
    if result["valid"]:
        print(f"  {Fore.GREEN}✓ Ticker {ticker} is fully valid!{Style.RESET_ALL}")
        if result["company_name"]:
            print(f"  Company: {Fore.YELLOW}{result['company_name']}{Style.RESET_ALL}")
        if result.get("price") and result.get("currency"):
            print(f"  Price: {result['price']} {result['currency']}")
        if result.get("latest_close"):
            print(f"  Latest close: {result['latest_close']}")
        if result.get("historic_data_days"):
            print(f"  Historical data: {result['historic_data_days']} days available")
    else:
        print(f"  {Fore.RED}❌ Ticker {ticker} has issues:{Style.RESET_ALL}")
        if not result["basic_info_valid"]:
            print(f"  - Basic info: {Fore.RED}Invalid{Style.RESET_ALL}")
        if not result["historic_data_valid"]:
            print(f"  - Historical data: {Fore.RED}Invalid{Style.RESET_ALL}")
        if result["errors"]:
            for error in result["errors"]:
                print(f"  - Error: {error}")
    
    return result

def check_replacement_tickers():
    """Check and validate problematic tickers and their replacements"""
    print(f"\n{Fore.BLUE}=== Investigating Problematic AEX Tickers ==={Style.RESET_ALL}")
    
    results = {}
    replacements = {}
    
    # Check each problematic ticker and its alternatives
    for ticker, alternatives in PROBLEMATIC_TICKERS.items():
        print(f"\n{Fore.CYAN}Investigating {ticker} and potential replacements...{Style.RESET_ALL}")
        
        # Test the original problematic ticker
        original_result = validate_ticker_deeply(ticker)
        results[ticker] = original_result
        
        # Test alternative tickers
        alt_results = []
        for alt_ticker in alternatives:
            if alt_ticker != ticker:  # Skip if same as original
                print(f"\n{Fore.YELLOW}Testing alternative: {alt_ticker}{Style.RESET_ALL}")
                alt_result = validate_ticker_deeply(alt_ticker)
                alt_results.append(alt_result)
                results[alt_ticker] = alt_result
        
        # Determine best replacement
        best_replacement = None
        if original_result["valid"]:
            print(f"\n{ticker} is actually valid, no replacement needed")
            best_replacement = ticker
        else:
            valid_alternatives = [r for r in alt_results if r["valid"]]
            if valid_alternatives:
                best_replacement = valid_alternatives[0]["ticker"]
                print(f"\n{Fore.GREEN}Found valid replacement for {ticker}: {best_replacement}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}No valid replacement found for {ticker}!{Style.RESET_ALL}")
        
        replacements[ticker] = best_replacement
    
    # Generate tickers.json content with replacements
    try:
        # Load current tickers.json
        current_tickers_file = os.path.join(os.path.dirname(__file__), 'tickers.json')
        with open(current_tickers_file, 'r') as f:
            # Handle commented JSON by skipping lines that start with //
            json_content = ""
            for line in f:
                if not line.strip().startswith('//'):
                    json_content += line
            
            current_data = json.loads(json_content)
            current_tickers = current_data.get("AEX_TICKERS", [])
    except Exception as e:
        print(f"{Fore.RED}Error reading current tickers.json: {str(e)}{Style.RESET_ALL}")
        current_tickers = []
    
    # Create updated tickers list with replacements
    updated_tickers = []
    for ticker in current_tickers:
        if ticker in replacements and replacements[ticker] and ticker != replacements[ticker]:
            updated_tickers.append(replacements[ticker])  # Use replacement
            print(f"Replacing {ticker} with {replacements[ticker]}")
        else:
            updated_tickers.append(ticker)  # Keep original
    
    # Print summary and recommendations
    print(f"\n{Fore.BLUE}=== Summary and Recommendations ==={Style.RESET_ALL}")
    for ticker, replacement in replacements.items():
        if replacement and ticker != replacement:
            print(f"{Fore.YELLOW}• Replace {ticker} with {replacement}{Style.RESET_ALL}")
        elif replacement and ticker == replacement:
            print(f"{Fore.GREEN}• Keep {ticker} (it's valid){Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}• No valid replacement found for {ticker}{Style.RESET_ALL}")
    
    # Display recommended updated tickers.json
    print(f"\n{Fore.CYAN}Recommended updated tickers.json:{Style.RESET_ALL}")
    updated_data = {"AEX_TICKERS": updated_tickers}
    print(json.dumps(updated_data, indent=4))
    
    # Ask user if they want to update tickers.json
    print(f"\n{Fore.YELLOW}Would you like to update tickers.json with these changes? (y/n){Style.RESET_ALL}")
    choice = input().lower()
    if choice == 'y' or choice == 'yes':
        # Create backup
        backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, f'tickers_backup_{time.strftime("%Y%m%d_%H%M%S")}.json')
        
        try:
            # Backup current file
            with open(current_tickers_file, 'r') as f_in, open(backup_file, 'w') as f_out:
                f_out.write(f_in.read())
            print(f"{Fore.GREEN}Created backup at {backup_file}{Style.RESET_ALL}")
            
            # Update tickers.json
            with open(current_tickers_file, 'w') as f:
                json.dump(updated_data, f, indent=4)
            print(f"{Fore.GREEN}Successfully updated tickers.json!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error updating tickers.json: {str(e)}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No changes made to tickers.json{Style.RESET_ALL}")

if __name__ == "__main__":
    check_replacement_tickers()
