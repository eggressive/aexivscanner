#!/usr/bin/env python3
"""
Unified Ticker Validator

A comprehensive tool for validating stock tickers on Yahoo Finance with features:
    - Colorized console output
    - Robust retry logic with exponential backoff
    - Detailed reporting on validation results
    - Generation of ticker configuration files

Usage:
    # Default behavior (tests all tickers from CSV with wait=1s):
    python ticker_validator.py                              # Default: --from-csv --wait 1
    
    # Specific ticker validation:
    python ticker_validator.py ASML.AS INGA.AS MT.AS        # Validate specific tickers
    python ticker_validator.py --verbose ASML.AS            # Show detailed information
    python ticker_validator.py --check-fields ASML.AS       # Check for key data fields
    
    # Using CSV ticker source:
    python ticker_validator.py --from-csv                   # Test all tickers from CSV
    python ticker_validator.py --from-csv --wait 2          # Customize wait time between tests
    python ticker_validator.py --from-csv --generate-config # Generate JSON configuration
    
Options:
    --verbose, -v       : Show detailed ticker information
    --very-verbose, -vv : Show all available ticker fields
    --check-fields, -c  : Check for completeness of key data fields
    --from-csv, -csv    : Load tickers from amsterdam_aex_tickers.csv
    --generate-config, -g: Generate JSON configuration for valid tickers
    --wait, -w          : Set wait time between tests (default: 3s, 1s when no parameters used)
    --no-color, -nc     : Disable colored output
    
Note: Running without parameters (python ticker_validator.py) defaults to --from-csv with wait=1s
"""

import logging
import time
import random
import sys
import argparse
import os
import csv
import json
import yfinance as yf
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

# Try to import colorama for colored output
try:
    import colorama
    from colorama import Fore, Style
    colorama.init()
    HAS_COLORAMA = True
except ImportError:
    # Create dummy Fore and Style classes if colorama is not available
    class DummyColor:
        def __getattr__(self, name):
            return ""
    
    Fore = DummyColor()
    Style = DummyColor()
    HAS_COLORAMA = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants for validation

# Key fields we want to check for data completeness
KEY_FIELDS = [
    'shortName', 'longName', 'currentPrice', 'regularMarketPrice', 
    'sharesOutstanding', 'marketCap', 'volume', 'averageVolume', 
    'exchange', 'currency'
]

# Global settings for console output
USE_COLOR = True

def print_color(text, color=None, **kwargs):
    """Print colored text if color is enabled"""
    if USE_COLOR and color:
        print(f"{color}{text}{Style.RESET_ALL}", **kwargs)
    else:
        print(text, **kwargs)

def load_tickers_from_csv(csv_file=None):
    """
    Load tickers from the CSV file
    
    Args:
        csv_file (str): Path to CSV file, defaults to amsterdam_aex_tickers.csv
        
    Returns:
        list: List of ticker symbols
    """
    if csv_file is None:
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
            
            # Check if required column exists
            if reader.fieldnames and 'yahoo_ticker' not in reader.fieldnames:
                logger.error(f"CSV file missing 'yahoo_ticker' column. Available columns: {', '.join(reader.fieldnames)}")
                print_color(f"Error: CSV file doesn't have a 'yahoo_ticker' column.", Fore.RED)
                return tickers
                
            # Extract tickers
            for row in reader:
                if 'yahoo_ticker' in row and row['yahoo_ticker'].strip():
                    tickers.append(row['yahoo_ticker'].strip())
        
        logger.info(f"Loaded {len(tickers)} tickers from {csv_file}")
    except Exception as e:
        logger.error(f"Error loading tickers from CSV: {str(e)}")
        print_color(f"Error loading tickers: {str(e)}", Fore.RED)
    
    return tickers



def validate_ticker(ticker, verbose=False, very_verbose=False, check_fields=False, max_retries=3):
    """
    Validate a ticker with robust retry logic and optional field checking
    
    Args:
        ticker (str): The ticker symbol to validate
        verbose (bool): Whether to print detailed information about the ticker
        very_verbose (bool): Whether to print all available fields
        check_fields (bool): Whether to check for completeness of key data fields
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        dict: Validation result with ticker data and status information
    """
    print_color(f"\nChecking {ticker}...", Fore.CYAN)
    
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
                
                print_color("✓ Valid ticker!", Fore.GREEN)
                print_color(f"  Company: {name}", Fore.YELLOW)
                print(f"  Price: {price} {currency}")
                print(f"  Market Cap: {market_cap_str}")
                print(f"  Exchange: {exchange}")
                print(f"  Data points: {len(info)}")
                
                # Field checking logic
                missing = []
                if check_fields:
                    stats = {}
                    
                    for field in KEY_FIELDS:
                        value = info.get(field)
                        stats[field] = value
                        if value is None:
                            missing.append(field)
                    
                    if missing:
                        print_color(f"⚠️ {ticker} is missing {len(missing)}/{len(KEY_FIELDS)} fields: {', '.join(missing)}", Fore.YELLOW)
                    else:
                        print_color(f"✓ {ticker} has all required fields", Fore.GREEN)
                
                # Print additional info if verbose mode is enabled
                if verbose:
                    print("\nDetailed information:")
                    print(f"  Full Name: {info.get('longName', 'N/A')}")
                    print(f"  Sector: {info.get('sector', 'N/A')}")
                    print(f"  Industry: {info.get('industry', 'N/A')}")
                    print(f"  Website: {info.get('website', 'N/A')}")
                    print(f"  Market Cap: {info.get('marketCap', 'N/A')}")
                    print(f"  52 Week High: {info.get('fiftyTwoWeekHigh', 'N/A')}")
                    print(f"  52 Week Low: {info.get('fiftyTwoWeekLow', 'N/A')}")
                
                # Print all available fields if very_verbose is enabled
                if very_verbose:
                    print("\nAll available fields:")
                    all_fields = list(info.keys())
                    for i in range(0, len(all_fields), 5):
                        chunk = all_fields[i:i+5]
                        print("  " + ", ".join(chunk))
                
                return {
                    "ticker": ticker,
                    "valid": True,
                    "name": name,
                    "price": price,
                    "market_cap": market_cap,
                    "currency": currency,
                    "exchange": exchange,
                    "data_points": len(info),
                    "missing_fields": missing
                }
            else:
                if retries < max_retries:
                    retries += 1
                    wait_time = 2 * (2 ** retries) * (1 + random.random())
                    print_color(f"⚠️ Insufficient data. Retrying in {wait_time:.2f}s (attempt {retries}/{max_retries})", Fore.YELLOW)
                    time.sleep(wait_time)
                else:
                    print_color(f"❌ Got response but with insufficient data", Fore.RED)
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
                print_color(f"⚠️ Connection error: {str(e)}. Retrying in {wait_time:.2f}s (attempt {retries}/{max_retries})", Fore.YELLOW)
                time.sleep(wait_time)
            else:
                print_color(f"❌ Connection error: {str(e)}", Fore.RED)
                return {
                    "ticker": ticker,
                    "valid": False,
                    "error": f"Connection error: {str(e)}"
                }
        except Exception as e:
            print_color(f"❌ Unexpected error: {str(e)}", Fore.RED)
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



def validate_tickers_list(tickers, verbose=False, very_verbose=False, check_fields=False, wait=3, generate_config=False):
    """
    Validate a list of tickers
    
    Args:
        tickers (list): List of tickers to validate
        verbose (bool): Whether to print detailed information
        very_verbose (bool): Whether to print all available fields
        check_fields (bool): Whether to check for completeness of key data fields
        wait (float): Wait time between ticker checks
        generate_config (bool): Whether to generate a JSON configuration file
        
    Returns:
        dict: Results with valid and invalid tickers
    """
    results = {
        "success": [],
        "failed": []
    }
    
    # Store detailed validation results for config generation
    validation_details = {
        "valid": [],
        "invalid": []
    }
    
    print(f"Will validate {len(tickers)} tickers" + 
          (f" with {wait}s delay between tests" if len(tickers) > 1 else ""))
    
    # Test each ticker
    for i, ticker in enumerate(tickers):
        print_color(f"\n{'=' * 50}", Fore.BLUE)
        print_color(f"Testing ticker: {ticker}", Fore.BLUE)
        print_color(f"{'=' * 50}", Fore.BLUE)
        
        # Add delay to avoid rate limiting (except for first ticker)
        if i > 0 and wait > 0:
            time.sleep(wait)
        
        result = validate_ticker(
            ticker, 
            verbose=verbose, 
            very_verbose=very_verbose, 
            check_fields=check_fields
        )
        
        # Track result
        if result["valid"]:
            results["success"].append(ticker)
            validation_details["valid"].append(result)
            print_color("Result: ✓ Success", Fore.GREEN)
        else:
            results["failed"].append(ticker)
            validation_details["invalid"].append(result)
            print_color(f"Result: ❌ Failed - {result.get('error', 'Unknown error')}", Fore.RED)
    
    # Print summary
    print_color("\n" + "=" * 50, Fore.BLUE)
    print_color("VALIDATION SUMMARY", Fore.BLUE)
    print_color("=" * 50, Fore.BLUE)
    print_color(f"✓ Successful: {len(results['success'])}/{len(tickers)}", Fore.GREEN)
    print_color(f"❌ Failed: {len(results['failed'])}/{len(tickers)}", Fore.RED)
    
    if results["failed"]:
        print("\nFailed tickers:")
        for ticker in results["failed"]:
            print(f"  - {ticker}")
    
    # Generate config if requested
    if generate_config:
        config_tickers = sorted(results["success"])
        
        if len(config_tickers) > 0:
            print_color("\nGenerating ticker configuration...", Fore.BLUE)
            
            config = {
                "TICKERS": config_tickers
            }
            
            # Print formatted JSON
            json_str = json.dumps(config, indent=4)
            print(json_str)
            
            # Save to file
            config_file = 'tickers_config.json'
            with open(config_file, 'w') as f:
                f.write(json_str)
            
            print_color(f"\nConfiguration saved to {config_file}", Fore.GREEN)
            print_color("You can rename this file or copy its contents to your main configuration.", Fore.YELLOW)
        else:
            print_color("\nNo valid tickers found, cannot generate configuration.", Fore.RED)
    
    return results

def main():
    """Main function"""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Unified Ticker Validator - A comprehensive tool for validating stock tickers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split('\n\nUsage:')[1] if '\n\nUsage:' in __doc__ else None
    )
    
    # Input source options
    parser.add_argument("tickers", nargs="*", help="One or more ticker symbols to validate")
    parser.add_argument("--from-csv", "-csv", action="store_true", 
                       help="Load tickers from amsterdam_aex_tickers.csv")
    
    # Display options
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Show detailed information for each ticker")
    parser.add_argument("--very-verbose", "-vv", action="store_true", 
                       help="Show all available fields for each ticker")
    parser.add_argument("--check-fields", "-c", action="store_true", 
                       help="Check for completeness of key data fields")
    parser.add_argument("--generate-config", "-g", action="store_true",
                       help="Generate JSON configuration for valid tickers")
    parser.add_argument("--wait", "-w", type=float, default=3.0, 
                      help="Wait time in seconds between ticker validations (default: 3.0)")
    parser.add_argument("--no-color", "-nc", action="store_true",
                      help="Disable colored output")
    
    args = parser.parse_args()
    
    # Check if we should disable color output
    global USE_COLOR
    if args.no_color:
        USE_COLOR = False
    elif not HAS_COLORAMA:
        print("Warning: colorama module not available, colored output disabled")
        USE_COLOR = False
    
    # Determine which tickers to test
    tickers_to_test = []
    
    # Load from CSV file
    if args.from_csv:
        print_color("Loading tickers from CSV file...", Fore.BLUE)
        tickers_to_test = load_tickers_from_csv()
        if not tickers_to_test:
            print_color("❌ No tickers found in the CSV file.", Fore.RED)
            return 1
    
    # Use specific tickers
    elif args.tickers:
        tickers_to_test = args.tickers
    
    # No tickers specified - default to CSV mode with wait=1
    else:
        print_color("No parameters specified. Defaulting to --from-csv mode with wait=1s", Fore.BLUE)
        tickers_to_test = load_tickers_from_csv()
        if not tickers_to_test:
            print_color("❌ No tickers found in the CSV file.", Fore.RED)
            return 1
        # Override wait time to 1 second for default behavior
        args.wait = 1.0
    
    # Validate tickers
    results = validate_tickers_list(
        tickers_to_test,
        verbose=args.verbose,
        very_verbose=args.very_verbose,
        check_fields=args.check_fields,
        wait=args.wait,
        generate_config=args.generate_config
    )
    
    # Return error code if all tickers failed
    if not results["success"] and results["failed"]:
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
