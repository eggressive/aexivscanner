#!/usr/bin/env python3
"""
Ticker Data Validator - Check specific tickers for data completeness
Usage: python3 validate_ticker.py [ticker1] [ticker2] ...
       python3 validate_ticker.py --all   # to check all AEX tickers
"""

import sys
import yfinance as yf
import pandas as pd
import time
import random
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

# Import tickers list from the central module
sys.path.append('.')
try:
    from aex_tickers import AEX_TICKERS
except ImportError:
    print("WARNING: Could not import AEX_TICKERS from aex_tickers.py, using default list")
    # Default tickers as fallback
    AEX_TICKERS = [
        'ADYEN.AS', 'ASML.AS', 'AD.AS', 'AKZA.AS', 'ABN.AS', 'DSM.AS', 'HEIA.AS', 
        'IMCD.AS', 'INGA.AS', 'KPN.AS', 'NN.AS', 'PHIA.AS', 'RAND.AS', 'REN.AS', 
        'WKL.AS', 'URW.AS', 'UNA.AS', 'MT.AS', 'RDSA.AS', 'PRX.AS'
    ]

# Key fields we want to check
KEY_FIELDS = [
    'shortName', 'longName', 'currentPrice', 'sharesOutstanding', 'marketCap',
    'volume', 'averageVolume', 'exchange', 'currency'
]

def validate_ticker(ticker, verbosity=1, retry=True):
    """Validate a ticker and return its data"""
    print(f"Validating {ticker}...")
    
    max_retries = 3
    retries = 0
    
    while retries <= max_retries:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check if we have a valid response
            if not info or len(info) == 0:
                print(f"  ❌ ERROR: No data returned for {ticker}")
                if retry and retries < max_retries:
                    retries += 1
                    wait_time = 2 * (2 ** retries) * (1 + random.random())
                    print(f"  ⏳ Retrying in {wait_time:.2f}s (attempt {retries}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                return None
            
            # Get key stats
            stats = {}
            missing = []
            
            for field in KEY_FIELDS:
                value = info.get(field)
                stats[field] = value
                if value is None:
                    missing.append(field)
            
            if missing:
                print(f"  ⚠️ {ticker} is missing {len(missing)}/{len(KEY_FIELDS)} fields: {', '.join(missing)}")
            else:
                print(f"  ✅ {ticker} has all required fields")
            
            # Print data table
            if verbosity > 0:
                # Convert to DataFrame for better display
                df = pd.DataFrame([stats])
                df_transposed = df.T.reset_index()
                df_transposed.columns = ['Field', 'Value']
                
                print("\nKey fields:")
                for field, value in stats.items():
                    print(f"  {field}: {value}")
                
                if verbosity > 1:
                    print("\nAll available fields:")
                    all_fields = list(info.keys())
                    for i in range(0, len(all_fields), 5):
                        chunk = all_fields[i:i+5]
                        print("  " + ", ".join(chunk))
            
            return stats
        
        except (ConnectionError, Timeout, HTTPError) as e:
            print(f"  ❌ Connection error: {str(e)}")
            if retry and retries < max_retries:
                retries += 1
                wait_time = 2 * (2 ** retries) * (1 + random.random())
                print(f"  ⏳ Retrying in {wait_time:.2f}s (attempt {retries}/{max_retries})")
                time.sleep(wait_time)
            else:
                return None
        except Exception as e:
            print(f"  ❌ Unexpected error: {str(e)}")
            return None
    
    return None

def main():
    """Main function to validate tickers"""
    # Get tickers from command line or use all
    if len(sys.argv) < 2:
        print("Please specify ticker(s) to check or use --all for all AEX tickers")
        print("Example: python3 validate_ticker.py ADYEN.AS ASML.AS")
        return
    
    if sys.argv[1] == "--all":
        tickers = AEX_TICKERS
    else:
        tickers = sys.argv[1:]
    
    # Check verbosity flag
    verbosity = 1  # Default
    if "--verbose" in tickers:
        verbosity = 2
        tickers.remove("--verbose")
    elif "--quiet" in tickers:
        verbosity = 0
        tickers.remove("--quiet")
    
    results = {
        'complete': [],
        'incomplete': [],
        'failed': []
    }
    
    # Process each ticker
    for ticker in tickers:
        stats = validate_ticker(ticker, verbosity)
        
        if stats is None:
            results['failed'].append(ticker)
        elif None in stats.values():
            results['incomplete'].append(ticker)
        else:
            results['complete'].append(ticker)
        
        # Add a small delay between requests to avoid rate limiting
        if ticker != tickers[-1]:
            time.sleep(1 + random.random())
    
    # Print summary
    print("\n" + "="*50)
    print(f"VALIDATION SUMMARY ({len(tickers)} tickers checked)")
    print(f"✅ Complete:   {len(results['complete'])}/{len(tickers)}")
    print(f"⚠️ Incomplete: {len(results['incomplete'])}/{len(tickers)}")
    print(f"❌ Failed:     {len(results['failed'])}/{len(tickers)}")
    
    if results['incomplete']:
        print("\nIncomplete tickers: " + ", ".join(results['incomplete']))
    
    if results['failed']:
        print("\nFailed tickers: " + ", ".join(results['failed']))

if __name__ == "__main__":
    main()
