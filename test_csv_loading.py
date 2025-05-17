#!/usr/bin/env python3

import os
import csv

# Define file paths
csv_file = 'amsterdam_aex_tickers.csv'

print(f"Looking for CSV file: {csv_file}")
print(f"File exists: {os.path.exists(csv_file)}")

if os.path.exists(csv_file):
    try:
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
            print(f"Loaded {len(csv_tickers)} tickers from {csv_file}")
            print("First 5 tickers:", csv_tickers[:5])
        else:
            print(f"CSV file found but no valid tickers extracted from {csv_file}")
    except Exception as e:
        print(f"Error loading tickers from CSV: {e}")
else:
    print(f"CSV file {csv_file} not found")
