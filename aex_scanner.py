#!/usr/bin/env python3
"""
AEX DCF Scanner - Calculates valuation metrics and ranks AEX stocks by undervaluation
"""

import os
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import time
import openpyxl
from openpyxl.styles import PatternFill, Font
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('aex_scanner.log')
    ]
)
logger = logging.getLogger(__name__)

# AEX stock tickers
AEX_TICKERS = [
    'ADYEN.AS', 'ASML.AS', 'AD.AS', 'AKZA.AS', 'ABN.AS', 'DSM.AS', 'HEIA.AS', 
    'IMCD.AS', 'INGA.AS', 'KPN.AS', 'NN.AS', 'PHIA.AS', 'RAND.AS', 'REN.AS', 
    'WKL.AS', 'URW.AS', 'UNA.AS', 'MT.AS', 'RDSA.AS', 'RELX.AS', 'PRX.AS'
]

# Dictionary to store fair value estimates - add your own estimates from SimplyWall.st
# These are fair value estimates sourced from SimplyWall.st where available
FAIR_VALUE_ESTIMATES = {
    'ADYEN.AS': 1500.0,
    'ASML.AS': 621.59,  # Updated from SimplyWall.st on 2025-05-16
    'AD.AS': 52.58,  # Updated from SimplyWall.st on 2025-05-16
    'AKZA.AS': 105.0,
    'ABN.AS': 14.0,
    'DSM.AS': 141.75,  # Updated from SimplyWall.st on 2025-05-16
    'HEIA.AS': 120.0,
    'IMCD.AS': 170.0,
    'INGA.AS': 43.98,  # Updated from SimplyWall.st on 2025-05-16
    'KPN.AS': 9.75,  # Updated from SimplyWall.st on 2025-05-16
    'NN.AS': 45.0,
    'PHIA.AS': 50.0,
    'RAND.AS': 65.0,
    'REN.AS': 40.0,
    'WKL.AS': 125.0,
    'URW.AS': 80.0,
    'UNA.AS': 60.0,
    'MT.AS': 30.0,
    'RDSA.AS': 35.0,
    'RELX.AS': 40.0,
    'PRX.AS': 20.0,
}

class AEXScanner:
    def __init__(self):
        """Initialize AEX Scanner"""
        self.output_file = f"aex_stock_valuation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        self.data = {}
    
    def fetch_stock_data(self):
        """Fetch current stock data from Yahoo Finance"""
        logger.info("Fetching stock data from Yahoo Finance...")
        
        for ticker in AEX_TICKERS:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Extract relevant data
                self.data[ticker] = {
                    'name': info.get('shortName', ticker),
                    'price': info.get('currentPrice', None),
                    'shares_outstanding': info.get('sharesOutstanding', None),
                    'fair_value': FAIR_VALUE_ESTIMATES.get(ticker, None)
                }
                
                logger.info(f"Fetched data for {ticker}: {self.data[ticker]['name']}")
                
            except Exception as e:
                logger.error(f"Error fetching data for {ticker}: {str(e)}")
        
        # Remove tickers with incomplete data
        for ticker in list(self.data.keys()):
            if None in self.data[ticker].values():
                logger.warning(f"Removing {ticker} due to incomplete data")
                del self.data[ticker]
    
    def calculate_metrics(self):
        """Calculate valuation metrics for each stock"""
        logger.info("Calculating valuation metrics...")
        
        for ticker, stock_data in self.data.items():
            try:
                price = stock_data['price']
                shares = stock_data['shares_outstanding']
                fair_value = stock_data['fair_value']
                
                # Calculate metrics
                market_cap = price * shares
                fair_market_cap = fair_value * shares
                discount_margin = fair_market_cap - market_cap
                discount_percent = (discount_margin / fair_market_cap) * 100 if fair_market_cap != 0 else 0
                
                # Update data dictionary with calculated metrics
                self.data[ticker].update({
                    'market_cap': market_cap,
                    'fair_market_cap': fair_market_cap,
                    'discount_margin': discount_margin,
                    'discount_percent': discount_percent
                })
                
                logger.info(f"Calculated metrics for {ticker}: Discount %: {discount_percent:.2f}%")
                
            except Exception as e:
                logger.error(f"Error calculating metrics for {ticker}: {str(e)}")
    
    def rank_stocks(self):
        """Rank stocks by discount percentage (undervaluation)"""
        logger.info("Ranking stocks by discount percentage...")
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame.from_dict(self.data, orient='index')
        
        # Sort by discount percentage (descending)
        df = df.sort_values(by='discount_percent', ascending=False)
        
        return df
    
    def save_to_excel(self, df):
        """Save results to Excel file with formatting"""
        logger.info(f"Saving results to {self.output_file}...")
        
        # Create Excel writer
        with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
            # Convert to millions for market cap values
            df['market_cap_M'] = df['market_cap'] / 1_000_000
            df['fair_market_cap_M'] = df['fair_market_cap'] / 1_000_000
            df['discount_margin_M'] = df['discount_margin'] / 1_000_000
            
            # Select and rename columns for output
            output_df = df[[
                'name', 'price', 'fair_value', 
                'market_cap_M', 'fair_market_cap_M', 
                'discount_margin_M', 'discount_percent'
            ]].rename(columns={
                'name': 'Company',
                'price': 'Current Price',
                'fair_value': 'Fair Value',
                'market_cap_M': 'Market Cap (M)',
                'fair_market_cap_M': 'Fair Market Cap (M)',
                'discount_margin_M': 'Discount Margin (M)',
                'discount_percent': 'Discount %'
            })
            
            # Format numbers
            for col in ['Market Cap (M)', 'Fair Market Cap (M)', 'Discount Margin (M)']:
                output_df[col] = output_df[col].map('{:,.2f}'.format)
                
            output_df['Current Price'] = output_df['Current Price'].map('{:.2f}'.format)
            output_df['Fair Value'] = output_df['Fair Value'].map('{:.2f}'.format)
            output_df['Discount %'] = output_df['Discount %'].map('{:.2f}%'.format)
            
            # Write to Excel
            output_df.to_excel(writer, sheet_name='AEX Valuation', index=True, index_label='Ticker')
            
            # Apply formatting
            workbook = writer.book
            worksheet = writer.sheets['AEX Valuation']
            
            # Add a header with timestamp
            worksheet['A1'] = f"AEX Stock Valuation Scanner - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            worksheet.merge_cells('A1:H1')
            header_font = Font(bold=True, size=14)
            worksheet['A1'].font = header_font
            
        logger.info(f"Results saved to {self.output_file}")
        
    def run(self):
        """Run the full scanning process"""
        logger.info("Starting AEX DCF Scanner...")
        
        self.fetch_stock_data()
        self.calculate_metrics()
        ranked_df = self.rank_stocks()
        self.save_to_excel(ranked_df)
        
        logger.info("Scan completed successfully!")
        return self.output_file

if __name__ == "__main__":
    scanner = AEXScanner()
    output_file = scanner.run()
    print(f"Scan complete! Results saved to: {output_file}")
