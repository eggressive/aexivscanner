#!/usr/bin/env python3
"""
AEX DCF Visualizer - Create visualizations of the scanner results
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from datetime import datetime
import numpy as np

def visualize_latest_results():
    """
    Find the latest scanner results file and create visualizations
    """
    # Define the outputs directory where scanner results are stored
    outputs_dir = 'outputs'
    
    # Ensure outputs directory exists
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir, exist_ok=True)
        print(f"Created {outputs_dir} directory.")
    
    # Find the latest Excel file in the outputs directory
    files = [f for f in os.listdir(outputs_dir) if f.startswith('aex_stock_valuation_') and f.endswith('.xlsx')]
    
    if not files:
        print("No scanner results found in the outputs directory. Run aex_scanner.py first.")
        return
    
    latest_file = max(files)
    latest_file_path = os.path.join(outputs_dir, latest_file)
    print(f"Creating visualizations based on {latest_file}")
    
    # Read the data
    df = pd.read_excel(latest_file_path)
    
    # Print column names for debugging
    print(f"Columns in Excel file: {df.columns.tolist()}")
    print(f"First row: {df.iloc[0].tolist()}")
    
    # Skip first two rows (title and descriptions) and use the third row as header
    df = pd.read_excel(latest_file_path, header=2)
    
    # Print the actual data columns now
    print(f"Data columns: {df.columns.tolist()}")
    
    # Find the discount percentage column
    discount_col = [col for col in df.columns if 'Discount' in col and '%' in col]
    if discount_col:
        discount_col = discount_col[0]
        # Clean the data if it's string format
        if df[discount_col].dtype == object:
            df[discount_col] = df[discount_col].astype(str).str.rstrip('%').astype(float)
        print(f"Found discount column: {discount_col}")
    else:
        print("Warning: Could not find Discount % column")
        return
        
    # Find market cap related columns
    market_cap_cols = [col for col in df.columns if 'Market Cap' in col or 'Cap' in col or 'Margin' in col]
    for col in market_cap_cols:
        if df[col].dtype == object:  # If column is string type
            df[col] = df[col].str.replace(',', '').astype(float)
            
    price_col = next((col for col in df.columns if 'Price' in col), None)
    fair_value_col = next((col for col in df.columns if 'Fair Value' in col or 'Value' in col), None)
    
    if price_col:
        df[price_col] = df[price_col].astype(float)
    if fair_value_col:
        df[fair_value_col] = df[fair_value_col].astype(float)
    
    # Create output directory
    vis_dir = 'visualizations'
    os.makedirs(vis_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Discount Percentage Bar Chart
    plt.figure(figsize=(14, 8))
    colors = ['green' if x >= 0 else 'red' for x in df[discount_col]]
    plt.bar(df.index, df[discount_col], color=colors)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.title('AEX Stocks - Discount Percentage', fontsize=16)
    plt.xlabel('Stock Ticker', fontsize=12)
    plt.ylabel('Discount %', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    for i, (idx, v) in enumerate(zip(df.index, df[discount_col])):
        plt.text(i, v + (1 if v >= 0 else -3), f"{v:.1f}%", 
                 ha='center', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f"{vis_dir}/discount_percentage_{timestamp}.png", dpi=300)
    
    # Proceed with other visualizations only if we have the required columns
    if price_col and fair_value_col:
        # 2. Current Price vs Fair Value
        plt.figure(figsize=(14, 8))
        x = np.arange(len(df.index))
        width = 0.35
        
        plt.bar(x - width/2, df[price_col], width, label='Current Price')
        plt.bar(x + width/2, df[fair_value_col], width, label='Fair Value')
        
        plt.xlabel('Stock Ticker', fontsize=12)
        plt.ylabel('Price (€)', fontsize=12)
        plt.title('Current Price vs Fair Value', fontsize=16)
        plt.xticks(x, df.index, rotation=45)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f"{vis_dir}/price_comparison_{timestamp}.png", dpi=300)
    else:
        print("Skipping Price vs Fair Value chart due to missing columns")
    
    # Clean numerical columns with currency formatting
    market_cap_cols = [col for col in df.columns if 'Market Cap' in col or 'Cap' in col or 'Margin' in col]
    for col in market_cap_cols:
        if df[col].dtype == object:  # If column is string type
            df[col] = df[col].str.replace(',', '').astype(float)
            
    price_col = next((col for col in df.columns if 'Current Price' in col), None)
    fair_value_col = next((col for col in df.columns if 'Fair Value' in col), None)
    
    if price_col and df[price_col].dtype == object:
        df[price_col] = df[price_col].astype(str).str.replace(',', '').astype(float)
    if fair_value_col and df[fair_value_col].dtype == object:
        df[fair_value_col] = df[fair_value_col].astype(str).str.replace(',', '').astype(float)
        
    # Find market cap columns
    market_cap_col = next((col for col in df.columns if 'Market Cap' in col and '(M)' in col and 'Fair' not in col), None)
    fair_market_cap_col = next((col for col in df.columns if 'Fair Market' in col), None)
    discount_margin_col = next((col for col in df.columns if 'Margin' in col), None)
    
    # Set ticker as index for better plotting
    if 'Ticker' in df.columns:
        df = df.set_index('Ticker')
    
    # Print the data types to help debugging
    print(f"Data types: {df.dtypes}")
    print(f"Found {len(df)} stocks for visualization")
    
    
    # 4. Discount Margin Waterfall Chart
    if discount_margin_col:
        plt.figure(figsize=(16, 8))
        
        # Sort by discount margin
        waterfall_df = df.sort_values(by=discount_margin_col, ascending=False)
        colors = ['green' if x >= 0 else 'red' for x in waterfall_df[discount_margin_col]]
        
        plt.bar(waterfall_df.index, waterfall_df[discount_margin_col], color=colors)
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.title('AEX Stocks - Discount Margin (in Millions €)', fontsize=16)
        plt.xlabel('Stock Ticker', fontsize=12)
        plt.ylabel('Discount Margin (M)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        for i, v in enumerate(waterfall_df[discount_margin_col]):
            plt.text(i, v + (10 if v >= 0 else -100), f"{v:.1f}M", 
                     ha='center', fontsize=9, fontweight='bold')
            
        plt.tight_layout()
        plt.savefig(f"{vis_dir}/discount_margin_{timestamp}.png", dpi=300)
    else:
        print("Skipping Discount Margin waterfall chart due to missing column")
    
    print(f"Visualizations saved to {vis_dir}/")

if __name__ == "__main__":
    visualize_latest_results()
