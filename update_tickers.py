#!/usr/bin/env python3
"""
AEX Tickers Updater - Fetches current AEX stock tickers using yfinance API
Updates the tickers.json file with the latest components of the AEX index
"""

import json
import os
import logging
import sys
import time
import yfinance as yf

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ticker_updater.log')
    ]
)
logger = logging.getLogger(__name__)

# AEX index ticker
AEX_INDEX_TICKER = "^AEX"

def fetch_aex_components(validate=True):
    """
    Fetch AEX components using yfinance API
    
    Args:
        validate (bool): Whether to validate tickers by fetching their data
        
    Returns:
        list: List of ticker symbols
    """
    logger.info(f"Fetching AEX components using yfinance")
    
    try:
        # Get AEX index data
        aex_index = yf.Ticker(AEX_INDEX_TICKER)
        
        # Attempt to get components
        components = []
        
        # First method: Try to get components directly (may not work for all indices)
        try:
            if hasattr(aex_index, 'components'):
                components = list(aex_index.components)
            elif hasattr(aex_index.info, 'components'):
                components = list(aex_index.info['components'])
        except Exception as e:
            logger.warning(f"Could not get components directly: {e}")
        
        # Second method: Use a predefined list of major AEX stocks
        if not components:
            logger.info("Using predefined list of major AEX stocks")
            potential_tickers = [
                "ADYEN.AS", "ASML.AS", "AD.AS", "AKZA.AS", "ABN.AS", "DSM.AS", 
                "HEIA.AS", "IMCD.AS", "INGA.AS", "KPN.AS", "NN.AS", "PHIA.AS", 
                "RAND.AS", "REN.AS", "WKL.AS", "URW.AS", "UNA.AS", "MT.AS", 
                "RDSA.AS", "PRX.AS", "LIGHT.AS", "AGN.AS", "TKWY.AS" 
            ]
            
            # Remove duplicates
            potential_tickers = list(dict.fromkeys(potential_tickers))
            
            if validate:
                # Validate each ticker by trying to fetch its data
                valid_tickers = []
                for ticker in potential_tickers:
                    try:
                        stock = yf.Ticker(ticker)
                        info = stock.info
                        if info and 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
                            logger.info(f"Validated ticker: {ticker}")
                            valid_tickers.append(ticker)
                        else:
                            logger.warning(f"Could not validate ticker: {ticker}")
                    except Exception as e:
                        logger.warning(f"Error validating ticker {ticker}: {str(e)}")
                
                components = valid_tickers
            else:
                logger.info("Skipping validation, using all potential tickers")
                components = potential_tickers
        
        # Ensure all tickers have the .AS suffix and remove duplicates
        formatted_tickers = []
        seen = set()
        for ticker in components:
            if not ticker.endswith('.AS'):
                ticker = f"{ticker}.AS"
            if ticker not in seen:
                formatted_tickers.append(ticker)
                seen.add(ticker)
        
        if formatted_tickers:
            logger.info(f"Found {len(formatted_tickers)} AEX components")
            return formatted_tickers
        else:
            logger.error("Could not retrieve any valid AEX components")
            return None
    
    except Exception as e:
        logger.error(f"Error fetching AEX components: {str(e)}")
        return None

def update_tickers_file(tickers):
    """
    Update the tickers.json file with new ticker list
    """
    tickers_file = os.path.join(os.path.dirname(__file__), 'tickers.json')
    
    # Create backups directory if it doesn't exist
    backups_dir = os.path.join(os.path.dirname(__file__), 'backups')
    os.makedirs(backups_dir, exist_ok=True)
    
    backup_file = os.path.join(backups_dir, f'tickers_backup_{time.strftime("%Y%m%d_%H%M%S")}.json')
    
    # Create a backup of the current file
    if os.path.exists(tickers_file):
        with open(tickers_file, 'r') as f:
            original_content = f.read()
        
        with open(backup_file, 'w') as f:
            f.write(original_content)
        logger.info(f"Created backup of tickers.json at {backup_file}")
    
    # Update the tickers.json file
    try:
        data = {"AEX_TICKERS": tickers}
        
        # Write the JSON content directly without filepath comment
        with open(tickers_file, 'w') as f:
            json.dump(data, f, indent=4)
        
        logger.info(f"Updated {tickers_file} with {len(tickers)} tickers")
        return True
    except Exception as e:
        logger.error(f"Error updating tickers file: {str(e)}")
        return False

def main():
    """Main function to update AEX tickers"""
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Update AEX tickers from Yahoo Finance")
    parser.add_argument('--no-validate', dest='validate', action='store_false',
                      help='Skip validation of tickers (include all potential tickers)')
    parser.add_argument('--force', action='store_true',
                      help='Force update even if fewer than 10 tickers are found')
    parser.add_argument('--dry-run', action='store_true',
                      help='Show what would be updated without making changes')
    args = parser.parse_args()
    
    print("Updating AEX tickers from Yahoo Finance...")
    
    # Fetch AEX components
    tickers = fetch_aex_components(validate=args.validate)
    
    if not tickers:
        print("Error: Could not retrieve any AEX tickers. Check the logs for details.")
        return 1
    
    if len(tickers) < 10 and not args.force:  # Sanity check - AEX should have at least 10 components
        print(f"Warning: Only found {len(tickers)} tickers, which is fewer than expected.")
        print("This may indicate an issue with the data source.")
        print("Use --force to update anyway, or --no-validate to include all potential tickers.")
        return 1
    
    # Display the tickers
    print(f"\nFound {len(tickers)} AEX components:")
    for i, ticker in enumerate(tickers, 1):
        print(f"  {i}. {ticker}")
    
    if args.dry_run:
        print("\n✓ Dry run completed. No changes were made.")
        return 0
    
    # Update tickers file
    if update_tickers_file(tickers):
        print(f"\n✓ Successfully updated tickers.json with {len(tickers)} AEX components")
    else:
        print("\n✗ Failed to update tickers file. Check the logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
