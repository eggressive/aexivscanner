#!/usr/bin/env python3
"""
AEX Fair Value Updater - Fetches analyst target prices to update fair value estimates
"""

import yfinance as yf
import pandas as pd
import json
import os
import logging
import time
import random
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fair_value_updates.log')
    ]
)
logger = logging.getLogger(__name__)

# Import AEX stock tickers from central module
from aex_tickers import AEX_TICKERS

def update_fair_values():
    """
    Fetch analyst target prices and update fair values
    """
    logger.info("Starting fair value update process...")
    
    fair_values_file = 'fair_values.json'
    
    # Create outputs directory if it doesn't exist
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Import configuration manager
    from config_manager import load_fair_values
    
    # Load existing fair values from configuration if available
    try:
        # Load analyst values specifically, or initialize empty
        fair_values = load_fair_values(source='analyst') or {}
        logger.info(f"Loaded existing fair values for {len(fair_values)} stocks from configuration")
    except Exception as e:
        logger.error(f"Error loading fair values from configuration: {str(e)}")
        # Fall back to legacy file
        if os.path.exists(fair_values_file):
            try:
                with open(fair_values_file, 'r') as f:
                    fair_values = json.load(f)
                    logger.info(f"Loaded existing fair values from legacy file for {len(fair_values)} stocks")
            except Exception as e:
                logger.error(f"Error loading legacy fair values: {str(e)}")
                fair_values = {}
        else:
            fair_values = {}
    
    # Create a DataFrame to store results
    results = []
    
    # Add retry configuration
    max_retries = 3
    retry_delay = 2  # in seconds
    
    for ticker in AEX_TICKERS:
        retries = 0
        while retries <= max_retries:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Get analyst target price
                target_price = info.get('targetMeanPrice')
                current_price = info.get('currentPrice')
                name = info.get('shortName', ticker)
                
                # Validate data completeness
                if not target_price or not current_price:
                    logger.warning(f"No target price or current price available for {ticker}")
                    break
                
                # Calculate premium/discount
                premium_discount = ((target_price / current_price) - 1) * 100
                
                # Get existing fair value if available
                existing_fair_value = fair_values.get(ticker, None)
                
                # Update fair value
                fair_values[ticker] = target_price
                
                results.append({
                    'Ticker': ticker,
                    'Name': name,
                    'Current Price': current_price,
                    'Analyst Target': target_price,
                    'Previous Fair Value': existing_fair_value,
                    'Premium/Discount %': premium_discount
                })
                
                logger.info(f"Updated {ticker}: Target Price = {target_price}")
                break  # Success, exit retry loop
                
            except Exception as e:
                if retries < max_retries:
                    retries += 1
                    wait_time = retry_delay * (2 ** retries) * (1 + random.random())
                    logger.warning(f"Error fetching data for {ticker}, retrying in {wait_time:.2f} seconds: {str(e)}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to update {ticker} after {max_retries} retries: {str(e)}")
                    break
    
    # Save updated fair values to both the configuration system and legacy file
    from config_manager import save_fair_values
    
    # Save to configuration system
    try:
        save_fair_values(fair_values, source='analyst')
        logger.info(f"Saved updated fair values to configuration")
    except Exception as e:
        logger.error(f"Error saving fair values to configuration: {str(e)}")
    
    # Save to legacy file for backward compatibility
    try:
        with open(fair_values_file, 'w') as f:
            json.dump(fair_values, f, indent=4)
        logger.info(f"Saved updated fair values to legacy file {fair_values_file}")
    except Exception as e:
        logger.error(f"Error saving fair values to legacy file: {str(e)}")
    
    # Create DataFrame and save to Excel
    if results:
        df = pd.DataFrame(results)
        excel_file_name = f"fair_value_updates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        excel_file_path = os.path.join(output_dir, excel_file_name)
        
        df.to_excel(excel_file_path, index=False)
        logger.info(f"Saved update report to {excel_file_path}")
        
        return fair_values, excel_file_path
    else:
        logger.warning("No updates were made")
        return fair_values, None

def update_scanner_file(fair_values):
    """
    Legacy method to update the fair value estimates in the aex_scanner.py file
    Now redirects to the configuration system
    """
    logger.info("update_scanner_file() is deprecated. Using configuration system instead.")
    
    try:
        from config_manager import save_fair_values
        return save_fair_values(fair_values, source='analyst')
    except Exception as e:
        logger.error(f"Error updating fair values: {str(e)}")
        return False

if __name__ == "__main__":
    fair_values, report_file = update_fair_values()
    update_scanner_file(fair_values)
    
    if report_file:
        print(f"Fair values updated successfully! Report saved to {report_file}")
        print(f"You can find the report in the outputs directory.")
    else:
        print("No fair value updates were made.")
