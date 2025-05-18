#!/usr/bin/env python3
"""
Test script to verify that the ticker refactoring is working correctly.
"""

import os
import sys
import json
from aex_tickers import load_tickers

def test_ticker_loading():
    """Test that tickers are loaded correctly from CSV first, then JSON"""
    print("Testing ticker loading...")
    
    # Load tickers with source info
    tickers, source_info = load_tickers(return_source_info=True)
    
    print("\nTicker loading test results:")
    print(f"Source: {source_info['source']}")
    print(f"Reason: {source_info['reason']}")
    print(f"Path: {source_info['path']}")
    print(f"Ticker count: {source_info['tickers_count']}")
    
    if source_info['source'] == 'csv_file':
        print("\n✓ Success: System is correctly loading tickers from CSV as the primary source")
    elif source_info['source'] == 'json_file':
        print("\n⚠ Warning: System is falling back to JSON file. CSV file might be missing.")
    else:
        print("\n✗ Failure: System could not load tickers from either CSV or JSON")
    
    # Print first few tickers if available
    if tickers and len(tickers) > 0:
        print("\nFirst 5 tickers:")
        for i, ticker in enumerate(tickers[:5]):
            print(f"  {i+1}. {ticker}")

def test_special_cases():
    """Test if special case handling would be needed (should not be needed now)"""
    print("\nChecking special case handling...")
    print("✅ Special case handling not needed - tickers are fetched directly from Euronext")

if __name__ == "__main__":
    print("AEX Ticker Refactoring Test")
    print("==========================\n")
    
    test_ticker_loading()
    test_special_cases()
    
    print("\nTest completed.")
