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
    # Find the latest Excel file
    files = [f for f in os.listdir('.') if f.startswith('aex_stock_valuation_') and f.endswith('.xlsx')]
    
    if not files:
        print("No scanner results found. Run aex_scanner.py first.")
        return
    
    latest_file = max(files)
    print(f"Creating visualizations based on {latest_file}")
    
    # Read the data
    df = pd.read_excel(latest_file, index_col=0)
    
    # Clean up the data for visualization
    df['Discount %'] = df['Discount %'].str.rstrip('%').astype(float)
    for col in ['Market Cap (M)', 'Fair Market Cap (M)', 'Discount Margin (M)']:
        df[col] = df[col].str.replace(',', '').astype(float)
    
    df['Current Price'] = df['Current Price'].astype(float)
    df['Fair Value'] = df['Fair Value'].astype(float)
    
    # Create output directory
    vis_dir = 'visualizations'
    os.makedirs(vis_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Discount Percentage Bar Chart
    plt.figure(figsize=(14, 8))
    colors = ['green' if x >= 0 else 'red' for x in df['Discount %']]
    plt.bar(df.index, df['Discount %'], color=colors)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.title('AEX Stocks - Discount Percentage', fontsize=16)
    plt.xlabel('Stock Ticker', fontsize=12)
    plt.ylabel('Discount %', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    for i, v in enumerate(df['Discount %']):
        plt.text(i, v + (1 if v >= 0 else -3), f"{v:.1f}%", 
                 ha='center', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f"{vis_dir}/discount_percentage_{timestamp}.png", dpi=300)
    
    # 2. Current Price vs Fair Value
    plt.figure(figsize=(14, 8))
    x = np.arange(len(df.index))
    width = 0.35
    
    plt.bar(x - width/2, df['Current Price'], width, label='Current Price')
    plt.bar(x + width/2, df['Fair Value'], width, label='Fair Value')
    
    plt.xlabel('Stock Ticker', fontsize=12)
    plt.ylabel('Price (€)', fontsize=12)
    plt.title('Current Price vs Fair Value', fontsize=16)
    plt.xticks(x, df.index, rotation=45)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{vis_dir}/price_comparison_{timestamp}.png", dpi=300)
    
    # 3. Market Cap Comparison
    plt.figure(figsize=(14, 8))
    
    plt.bar(x - width/2, df['Market Cap (M)'], width, label='Current Market Cap')
    plt.bar(x + width/2, df['Fair Market Cap (M)'], width, label='Fair Market Cap')
    
    plt.xlabel('Stock Ticker', fontsize=12)
    plt.ylabel('Market Cap (Millions €)', fontsize=12)
    plt.title('Current vs Fair Market Cap', fontsize=16)
    plt.xticks(x, df.index, rotation=45)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{vis_dir}/market_cap_comparison_{timestamp}.png", dpi=300)
    
    # 4. Discount Margin Waterfall Chart
    plt.figure(figsize=(16, 8))
    
    # Sort by discount margin
    waterfall_df = df.sort_values(by='Discount Margin (M)', ascending=False)
    colors = ['green' if x >= 0 else 'red' for x in waterfall_df['Discount Margin (M)']]
    
    plt.bar(waterfall_df.index, waterfall_df['Discount Margin (M)'], color=colors)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.title('AEX Stocks - Discount Margin (in Millions €)', fontsize=16)
    plt.xlabel('Stock Ticker', fontsize=12)
    plt.ylabel('Discount Margin (M)', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    for i, v in enumerate(waterfall_df['Discount Margin (M)']):
        plt.text(i, v + (10 if v >= 0 else -100), f"{v:.1f}M", 
                 ha='center', fontsize=9, fontweight='bold')
        
    plt.tight_layout()
    plt.savefig(f"{vis_dir}/discount_margin_{timestamp}.png", dpi=300)
    
    print(f"Visualizations saved to {vis_dir}/")

if __name__ == "__main__":
    visualize_latest_results()
