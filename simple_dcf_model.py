#!/usr/bin/env python3
"""
AEX Simple DCF Model - A simplified DCF calculation
"""

import yfinance as yf
import pandas as pd
import numpy as np
import logging
import time
import sys

# Configure logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # Log to stdout for immediate visibility
)
logger = logging.getLogger(__name__)

def calculate_dcf(ticker_symbol):
    """A simplified DCF calculation based on available free cash flow data"""
    
    logger.info(f"Starting DCF calculation for {ticker_symbol}")
    
    try:
        # Get ticker data
        ticker = yf.Ticker(ticker_symbol)
        logger.info(f"Retrieved ticker data for {ticker_symbol}")
        
        # Get basic info
        info = ticker.info
        company_name = info.get('shortName', ticker_symbol)
        current_price = info.get('currentPrice')
        shares_outstanding = info.get('sharesOutstanding')
        
        logger.info(f"Company: {company_name}, Current Price: {current_price}, Shares: {shares_outstanding}")
        
        # Get cash flow data
        cashflow = ticker.cashflow
        logger.info(f"Retrieved cash flow data with shape: {cashflow.shape if isinstance(cashflow, pd.DataFrame) else 'None'}")
        
        # Check if free cash flow data is available
        if isinstance(cashflow, pd.DataFrame) and 'Free Cash Flow' in cashflow.index:
            fcf_data = cashflow.loc['Free Cash Flow'].dropna()
            logger.info(f"Free Cash Flow data: {fcf_data}")
            
            if len(fcf_data) > 0:
                recent_fcf = fcf_data.iloc[0]
                logger.info(f"Recent FCF: {recent_fcf}")
            else:
                logger.warning("No FCF data available in cash flow statement")
                return None
        else:
            # Try from info attribute
            logger.info("Trying to get FCF from info attribute")
            if 'freeCashflow' in info and info['freeCashflow'] is not None:
                recent_fcf = info['freeCashflow']
                logger.info(f"FCF from info: {recent_fcf}")
            else:
                logger.warning("No FCF data available")
                return None
        
        # Simple DCF settings
        growth_rate = 0.03       # Conservative 3% growth
        wacc = 0.10              # 10% discount rate
        terminal_growth = 0.025  # 2.5% terminal growth
        forecast_years = 5       # 5 year forecast
        
        # Try to get better growth rate if available
        if 'revenueGrowth' in info and info['revenueGrowth'] is not None:
            growth_rate = min(max(info['revenueGrowth'], 0.01), 0.15)  # Cap between 1% and 15%
            logger.info(f"Using revenue growth rate: {growth_rate:.2%}")
        
        # Simple DCF calculation
        # 1. Project future cash flows
        projected_cash_flows = []
        for year in range(1, forecast_years + 1):
            projected_fcf = recent_fcf * (1 + growth_rate) ** year
            projected_cash_flows.append(projected_fcf)
            logger.info(f"Year {year} projected FCF: {projected_fcf:,.2f}")
            
        # 2. Calculate terminal value
        terminal_value = projected_cash_flows[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
        logger.info(f"Terminal value: {terminal_value:,.2f}")
        
        # 3. Calculate present value of cash flows
        present_values = []
        for year, cash_flow in enumerate(projected_cash_flows, 1):
            pv = cash_flow / (1 + wacc) ** year
            present_values.append(pv)
            logger.info(f"Year {year} PV: {pv:,.2f}")
            
        # 4. Calculate present value of terminal value
        terminal_pv = terminal_value / (1 + wacc) ** forecast_years
        logger.info(f"Terminal value PV: {terminal_pv:,.2f}")
        
        # 5. Calculate enterprise value
        enterprise_value = sum(present_values) + terminal_pv
        logger.info(f"Enterprise value: {enterprise_value:,.2f}")
        
        # 6. Calculate fair value per share
        fair_value = enterprise_value / shares_outstanding
        logger.info(f"Fair value per share: {fair_value:.2f}")
        
        # Calculate discount/premium
        discount_percent = ((fair_value / current_price) - 1) * 100
        logger.info(f"Discount/premium: {discount_percent:.2f}%")
        
        return {
            'ticker': ticker_symbol,
            'company': company_name,
            'fair_value': fair_value,
            'current_price': current_price,
            'discount_percent': discount_percent,
            'growth_rate': growth_rate,
            'wacc': wacc
        }
        
    except Exception as e:
        logger.error(f"Error calculating DCF for {ticker_symbol}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Test with ASML
    ticker = "ASML.AS"
    result = calculate_dcf(ticker)
    
    if result:
        print(f"\nDCF Results for {ticker}:")
        print(f"Company: {result['company']}")
        print(f"Fair Value: €{result['fair_value']:.2f}")
        print(f"Current Price: €{result['current_price']:.2f}")
        print(f"Discount/Premium: {result['discount_percent']:.2f}%")
    else:
        print(f"Failed to calculate DCF for {ticker}")
        
    # Test with ING
    ticker = "INGA.AS"
    result = calculate_dcf(ticker)
    
    if result:
        print(f"\nDCF Results for {ticker}:")
        print(f"Company: {result['company']}")
        print(f"Fair Value: €{result['fair_value']:.2f}")
        print(f"Current Price: €{result['current_price']:.2f}")
        print(f"Discount/Premium: {result['discount_percent']:.2f}%")
    else:
        print(f"Failed to calculate DCF for {ticker}")
