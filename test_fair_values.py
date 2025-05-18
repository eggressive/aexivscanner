#!/usr/bin/env python3
"""
Test script to check which fair values are being used
"""

import logging
import sys

# Setup logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

# Import the configuration manager
from config_manager import load_fair_values

def main():
    """Compare fair values from different sources"""
    print("====== FAIR VALUE SOURCES COMPARISON ======")
    
    # Load values from different sources
    dcf_values = load_fair_values(source='dcf')
    manual_values = load_fair_values(source='manual')
    analyst_values = load_fair_values(source='analyst')
    combined_values = load_fair_values()  # This uses the priority system
    
    # Print some sample values for comparison
    sample_tickers = ["ASML.AS", "ADYEN.AS", "ABN.AS"]
    
    print("\n--- Sample Values ---")
    for ticker in sample_tickers:
        print(f"\n{ticker}:")
        print(f"DCF:     {dcf_values.get(ticker, 'N/A')}")
        print(f"Manual:  {manual_values.get(ticker, 'N/A')}")
        print(f"Analyst: {analyst_values.get(ticker, 'N/A')}")
        print(f"USED:    {combined_values.get(ticker, 'N/A')} (Based on priority)")
    
    # Compare all values to see which source is being used
    print("\n--- Source Usage Statistics ---")
    total_tickers = len(combined_values)
    using_dcf = 0
    using_manual = 0
    using_analyst = 0
    unknown = 0
    
    for ticker, value in combined_values.items():
        if ticker in dcf_values and abs(dcf_values[ticker] - value) < 0.01:
            using_dcf += 1
        elif ticker in manual_values and abs(manual_values[ticker] - value) < 0.01:
            using_manual += 1
        elif ticker in analyst_values and abs(analyst_values[ticker] - value) < 0.01:
            using_analyst += 1
        else:
            unknown += 1
    
    print(f"Total tickers: {total_tickers}")
    print(f"Using DCF values: {using_dcf} ({using_dcf/total_tickers*100:.1f}%)")
    print(f"Using Manual values: {using_manual} ({using_manual/total_tickers*100:.1f}%)")
    print(f"Using Analyst values: {using_analyst} ({using_analyst/total_tickers*100:.1f}%)")
    print(f"Unknown source: {unknown} ({unknown/total_tickers*100:.1f}%)")

if __name__ == "__main__":
    main()
