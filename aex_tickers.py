#!/usr/bin/env python3
"""
AEX Tickers Module - Single source of truth for AEX ticker symbols

Usage:
    python aex_tickers.py             # Display all tickers
    python aex_tickers.py --source    # Display tickers with source info
    python aex_tickers.py --check     # Check validity of ticker source
    python aex_tickers.py --update-json  # Update JSON file from CSV
"""

import json
import os
import logging
import sys
import argparse
import csv
import time
import shutil
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

def update_json_from_csv(tickers, json_file):
    """
    Updates the tickers.json file with tickers from the CSV file
    
    Args:
        tickers (list): List of ticker symbols to save
        json_file (str): Path to the JSON file
    """
    backups_dir = os.path.join(os.path.dirname(__file__), 'backups')
    os.makedirs(backups_dir, exist_ok=True)
    
    # Create backup if the file exists
    if os.path.exists(json_file):
        backup_file = os.path.join(backups_dir, f'tickers_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        try:
            shutil.copy2(json_file, backup_file)
            logger.info(f"Created backup of tickers.json at {backup_file}")
        except Exception as e:
            logger.warning(f"Failed to create backup: {str(e)}")
    
    # Update the JSON file
    try:
        data = {"AEX_TICKERS": tickers}
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info(f"Updated {json_file} with {len(tickers)} tickers from CSV file")
        return True
    except Exception as e:
        logger.error(f"Error updating JSON file: {str(e)}")
        return False

def load_tickers(return_source_info=False, update_json=False):
    """
    Load AEX tickers using the following priority:
    1. CSV file (amsterdam_aex_tickers.csv) - primary source of truth
    2. JSON file (tickers.json) - fallback option
    
    Args:
        return_source_info (bool): If True, returns a tuple of (tickers, source_info)
                                  If False, returns just the list of tickers
        update_json (bool): If True and tickers are loaded from CSV, update the JSON file
    
    Returns:
        If return_source_info=False: List of ticker symbols
        If return_source_info=True: Tuple of (tickers, source_info) where source_info is a dict
    """
    # Define file paths
    csv_file = os.path.join(os.path.dirname(__file__), 'amsterdam_aex_tickers.csv')
    tickers_file = os.path.join(os.path.dirname(__file__), 'tickers.json')
    
    source_info = {
        'source': 'error', 
        'reason': 'No ticker sources available', 
        'path': None,
        'tickers_count': 0
    }
    
    # Try loading from CSV file first (primary source of truth)
    try:
        if os.path.exists(csv_file):
            csv_tickers = []
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
                        csv_tickers.append(row['yahoo_ticker'].strip())
            
            if csv_tickers and len(csv_tickers) > 0:
                logger.info(f"Loaded {len(csv_tickers)} tickers from {csv_file}")
                source_info = {
                    'source': 'csv_file',
                    'reason': 'Successfully loaded from Amsterdam AEX CSV file',
                    'path': csv_file,
                    'tickers_count': len(csv_tickers)
                }
                
                # Update the JSON file if requested for backup purposes
                if update_json:
                    update_json_from_csv(csv_tickers, tickers_file)
                    
                if return_source_info:
                    return csv_tickers, source_info
                return csv_tickers
            else:
                logger.warning(f"CSV file found but no valid tickers extracted from {csv_file}")
        else:
            logger.warning(f"CSV file {csv_file} not found, trying JSON fallback")
    except Exception as e:
        logger.warning(f"Error loading tickers from CSV: {str(e)}, trying JSON fallback")
    
    # Fallback: Try loading from JSON file
    try:
        if os.path.exists(tickers_file):
            with open(tickers_file, 'r') as f:
                # Handle commented JSON by skipping lines that start with //
                json_content = ""
                for line in f:
                    if not line.strip().startswith('//'):
                        json_content += line
                
                # Parse the JSON content
                if json_content:
                    data = json.loads(json_content)
                    if 'AEX_TICKERS' in data and len(data['AEX_TICKERS']) > 0:
                        logger.info(f"Loaded {len(data['AEX_TICKERS'])} tickers from {tickers_file}")
                        source_info = {
                            'source': 'json_file',
                            'reason': 'Successfully loaded from file',
                            'path': tickers_file,
                            'tickers_count': len(data['AEX_TICKERS'])
                        }
                        if return_source_info:
                            return data['AEX_TICKERS'], source_info
                        return data['AEX_TICKERS']
                else:
                    logger.warning(f"Invalid ticker data in {tickers_file}, using default tickers")
                    source_info['reason'] = 'Invalid ticker data in file'
                    source_info['path'] = tickers_file
        else:
            logger.warning(f"Tickers file {tickers_file} not found, using default tickers")
            source_info['reason'] = 'File not found'
            source_info['path'] = tickers_file
    except Exception as e:
        logger.error(f"Error loading tickers from {tickers_file}: {str(e)}")
        source_info['reason'] = f'Error loading file: {str(e)}'
        source_info['path'] = tickers_file
    
    # Return empty list if no tickers are found
    empty_list = []
    source_info['source'] = 'no_tickers_found'
    logger.error("No ticker sources available. Using empty list.")
    
    if return_source_info:
        return empty_list, source_info
    return empty_list

# Load tickers and get source info (but don't export the source info)
tickers, source_info = load_tickers(return_source_info=True)
# Export the tickers list directly
AEX_TICKERS = tickers

def check_ticker_source():
    """
    Check if tickers are being loaded from the expected source
    and provide detailed diagnostic information
    """
    tickers, source = load_tickers(return_source_info=True)
    
    print("AEX Tickers - Source Information")
    print("================================")
    print(f"Source type: {source['source'].upper()}")
    
    if source['source'] == 'csv_file':
        print(f"CSV file path: {source['path']}")
        print(f"Tickers count: {source['tickers_count']}")
        print(f"Status: {source['reason']}")
        print("\n✓ System is using tickers from the CSV file as the primary source of truth.")
    elif source['source'] == 'json_file':
        print(f"JSON file path: {source['path']}")
        print(f"Tickers count: {source['tickers_count']}")
        print(f"Status: {source['reason']}")
        print("\n⚠ System is using tickers from the JSON backup file.")
        print("  Consider running euronext_tickers.py to refresh the CSV file.")
    else:
        print(f"Reason: {source['reason']}")
        print(f"Path attempted: {source['path']}")
        print(f"Tickers count: {source['tickers_count']}")
        print("\n⚠ System could not load tickers from either the CSV or JSON file!")
        print("\nTo fix this issue:")
        print("1. Run euronext_tickers.py to generate/update the amsterdam_aex_tickers.csv file")
        print("2. Ensure file permissions are correct")
        print("3. Check that the CSV file has the correct format with a 'yahoo_ticker' column")

def display_tickers_with_source():
    """Display all tickers with source information"""
    tickers, source = load_tickers(return_source_info=True)
    
    print(f"AEX Tickers ({len(tickers)}) - Source: {source['source'].upper()}")
    print("========================================================")
    
    # Column headers
    print(f"{'#':>3} {'Ticker':<10}")
    print("-" * 15)
    
    # Print tickers
    for i, ticker in enumerate(tickers, 1):
        print(f"{i:>3} {ticker:<10}")
    
    print("\nSource Details:")
    if source['source'] == 'json_file':
        print(f"✓ Loaded from: {source['path']}")
    else:
        print(f"⚠ Using default tickers because: {source['reason']}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AEX Tickers module - manage ticker symbols')
    parser.add_argument('--source', action='store_true', help='Display tickers with source information')
    parser.add_argument('--check', action='store_true', help='Check ticker source and configuration')
    parser.add_argument('--update-json', action='store_true', help='Update tickers.json from amsterdam_aex_tickers.csv')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    if args.update_json:
        # Load tickers from CSV and update JSON
        tickers, source = load_tickers(return_source_info=True)
        if source['source'] == 'csv_file':
            json_file = os.path.join(os.path.dirname(__file__), 'tickers.json')
            if update_json_from_csv(tickers, json_file):
                print(f"Successfully updated {json_file} with {len(tickers)} tickers from CSV file")
            else:
                print(f"Error updating JSON file from CSV")
        else:
            print(f"Cannot update JSON: Failed to load tickers from CSV file")
            print(f"Reason: {source['reason']}")
    elif args.check:
        check_ticker_source()
    elif args.source:
        display_tickers_with_source()
    else:
        # Default behavior - just print the tickers
        tickers = load_tickers()
        print(f"Loaded {len(tickers)} AEX tickers:")
        for ticker in tickers:
            print(f"  {ticker}")
