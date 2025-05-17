#!/usr/bin/env python3
"""
AEX DCF Model - Discounted Cash Flow calculation module for stock valuation

This module implements a DCF model that can calculate fair values for stocks based on:
- Free Cash Flow data
- Earnings (for financial stocks like banks)
- Growth rates and discount rates

It provides multiple calculation methods suitable for different industries.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import logging
import time
import random
import os
import sys
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('dcf_model.log')
    ]
)
logger = logging.getLogger(__name__)

class DCFModel:
    """
    DCF Model class that implements various DCF calculation methods
    suitable for different industries and data availability scenarios.
    """
    
    def __init__(self):
        """Initialize DCF Model with default parameters"""
        self.default_params = {
            'growth_years': 5,                  # Number of years for the growth phase
            'default_growth_rate': 0.03,        # Default growth rate if unavailable
            'default_terminal_growth': 0.025,   # Terminal growth rate (perpetuity)
            'default_wacc': 0.095,              # Default weighted average cost of capital
            'confidence_threshold': 0.60,       # Confidence threshold for data quality
            'max_retries': 3,                   # Max retries for API calls
            'retry_delay': 2,                   # Base delay (seconds) for retries
            'pe_ratio_banks': 10.0,             # Default PE ratio for banking sector
            'output_dir': 'outputs'             # Directory for saving outputs
        }
        
        # Ensure output directory exists
        os.makedirs(self.default_params['output_dir'], exist_ok=True)
        logger.info("DCF Model initialized with default parameters")
        
    def fetch_with_retry(self, ticker_symbol):
        """
        Fetch ticker data with retry logic for rate limiting
        
        Args:
            ticker_symbol (str): The ticker symbol to fetch data for
            
        Returns:
            yf.Ticker: The Yahoo Finance ticker object
        """
        retries = 0
        while retries <= self.default_params['max_retries']:
            try:
                stock = yf.Ticker(ticker_symbol)
                info = stock.info
                
                # Check if response seems valid
                if not info or not isinstance(info, dict) or 'shortName' not in info:
                    if retries < self.default_params['max_retries']:
                        retries += 1
                        wait_time = self.default_params['retry_delay'] * (1 + random.random())
                        logger.warning(f"Incomplete data for {ticker_symbol}. Retrying in {wait_time:.2f}s (attempt {retries}/{self.default_params['max_retries']})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise ValueError("Received incomplete data after maximum retries")
                
                return stock
                
            except (ConnectionError, Timeout, HTTPError) as e:
                if retries < self.default_params['max_retries']:
                    retries += 1
                    wait_time = self.default_params['retry_delay'] * (2 ** retries) * (1 + random.random())
                    logger.warning(f"Rate limit or connection error for {ticker_symbol}: {str(e)}. Retrying in {wait_time:.2f}s (attempt {retries}/{self.default_params['max_retries']})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch data for {ticker_symbol} after {self.default_params['max_retries']} retries: {str(e)}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error fetching data for {ticker_symbol}: {str(e)}")
                raise
        
        return None
    
    def is_financial_stock(self, ticker):
        """
        Determine if a stock is a financial stock (bank, insurance, etc.)
        based on sector/industry classification
        
        Args:
            ticker (yf.Ticker): Yahoo Finance ticker object
            
        Returns:
            bool: True if the stock is a financial stock, False otherwise
        """
        try:
            info = ticker.info
            
            # Look for sector or industry information
            sector = info.get('sector', '').lower()
            industry = info.get('industry', '').lower()
            
            # Check if sector or industry indicates a financial company
            financial_keywords = ['bank', 'financ', 'insurance', 'invest', 'credit']
            
            for keyword in financial_keywords:
                if (keyword in sector) or (keyword in industry):
                    logger.info(f"Detected financial stock: {ticker.ticker} (Sector: {sector}, Industry: {industry})")
                    return True
                    
            # Special case for known financial stocks in AEX
            known_financials = ['INGA.AS', 'ABN.AS', 'NN.AS', 'AGN.AS', 'ASRNL.AS']
            if ticker.ticker in known_financials:
                logger.info(f"Known financial stock detected: {ticker.ticker}")
                return True
                
            return False
            
        except Exception as e:
            logger.warning(f"Error determining if {ticker.ticker} is a financial stock: {str(e)}")
            return False
            
    def get_financial_data(self, ticker):
        """
        Get relevant financial data based on the stock type
        
        Args:
            ticker (yf.Ticker): Yahoo Finance ticker object
            
        Returns:
            dict: Dictionary with relevant financial data
        """
        data = {
            'free_cash_flow': None,
            'earnings': None,
            'book_value': None,
            'revenue': None,
            'growth_rate': None,
            'is_financial': False,
            'confidence': 0.0
        }
        
        try:
            info = ticker.info
            is_financial = self.is_financial_stock(ticker)
            data['is_financial'] = is_financial
            
            # Get FCF data - useful for regular stocks
            try:
                cashflow = ticker.cashflow
                if isinstance(cashflow, pd.DataFrame) and not cashflow.empty:
                    if 'Free Cash Flow' in cashflow.index:
                        fcf_data = cashflow.loc['Free Cash Flow'].dropna()
                        if len(fcf_data) > 0:
                            # Use most recent FCF
                            data['free_cash_flow'] = fcf_data.iloc[0]
                            data['confidence'] = 0.7
                    
                    # For banks, operating cash flow is often negative, so use earnings instead
                    if is_financial or data['free_cash_flow'] is None or data['free_cash_flow'] < 0:
                        # Try to get Net Income data
                        income_stmt = ticker.income_stmt
                        if isinstance(income_stmt, pd.DataFrame) and not income_stmt.empty:
                            for income_row in ['Net Income', 'Net Income Common Stockholders']:
                                if income_row in income_stmt.index:
                                    income_data = income_stmt.loc[income_row].dropna()
                                    if len(income_data) > 0:
                                        data['earnings'] = income_data.iloc[0]
                                        data['confidence'] = 0.8
                                        break
            except Exception as e:
                logger.warning(f"Error getting cash flow/income data for {ticker.ticker}: {str(e)}")
            
            # If we still don't have FCF or earnings, try info attribute
            if data['free_cash_flow'] is None and data['earnings'] is None:
                if 'freeCashflow' in info and info['freeCashflow'] is not None:
                    data['free_cash_flow'] = info['freeCashflow']
                    data['confidence'] = 0.6
                
                if 'netIncomeToCommon' in info and info['netIncomeToCommon'] is not None:
                    data['earnings'] = info['netIncomeToCommon']
                    data['confidence'] = 0.6
                    
            # Get book value (especially important for financial stocks)
            balance_sheet = ticker.balance_sheet
            if isinstance(balance_sheet, pd.DataFrame) and not balance_sheet.empty:
                for equity_row in ['Total Stockholder Equity', 'Stockholders Equity', 'Common Stock Equity']:
                    if equity_row in balance_sheet.index:
                        equity_data = balance_sheet.loc[equity_row].dropna()
                        if len(equity_data) > 0:
                            data['book_value'] = equity_data.iloc[0]
                            break
            
            # Get revenue
            if 'totalRevenue' in info and info['totalRevenue'] is not None:
                data['revenue'] = info['totalRevenue']
                
            # Get growth rate estimate
            if 'revenueGrowth' in info and info['revenueGrowth'] is not None:
                data['growth_rate'] = min(max(info['revenueGrowth'], -0.05), 0.20)  # Cap between -5% and 20%
            
            # For earnings growth, try to calculate from historical data if available
            try:
                if isinstance(income_stmt, pd.DataFrame) and not income_stmt.empty:
                    for income_row in ['Net Income', 'Net Income Common Stockholders']:
                        if income_row in income_stmt.index:
                            income_series = income_stmt.loc[income_row].dropna()
                            if len(income_series) >= 3:  # Need at least 3 years of data
                                oldest = income_series.iloc[-1]
                                newest = income_series.iloc[0]
                                years = len(income_series) - 1
                                
                                if oldest > 0 and newest > 0:
                                    cagr = (newest / oldest) ** (1 / years) - 1
                                    cagr = min(max(cagr, -0.05), 0.20)  # Cap between -5% and 20%
                                    
                                    # Average with revenue growth if available
                                    if data['growth_rate'] is not None:
                                        data['growth_rate'] = (data['growth_rate'] + cagr) / 2
                                    else:
                                        data['growth_rate'] = cagr
                                    break
            except Exception as e:
                logger.warning(f"Error calculating earnings growth for {ticker.ticker}: {str(e)}")
            
            # If still no growth rate, use default
            if data['growth_rate'] is None:
                data['growth_rate'] = self.default_params['default_growth_rate']
                
            return data
            
        except Exception as e:
            logger.error(f"Error getting financial data for {ticker.ticker}: {str(e)}")
            return data
    
    def get_wacc(self, ticker):
        """
        Estimate WACC (Weighted Average Cost of Capital) for a stock
        
        Args:
            ticker (yf.Ticker): Yahoo Finance ticker object
            
        Returns:
            float: Estimated WACC
        """
        try:
            info = ticker.info
            is_financial = self.is_financial_stock(ticker)
            
            # Start with a base rate
            base_rate = 0.08  # 8%
            
            # Adjust for beta if available
            if 'beta' in info and info['beta'] is not None and info['beta'] > 0:
                beta = info['beta']
                risk_premium = 0.04  # 4% risk premium
                
                # For financial stocks, increase the risk premium slightly
                if is_financial:
                    risk_premium = 0.045
                
                # Calculate WACC based on beta
                wacc = base_rate + (beta - 1) * risk_premium
                
                # Apply reasonable bounds
                return min(max(wacc, 0.07), 0.16)  # Between 7% and 16%
                
            # If beta not available, use default with slight adjustment for financials
            if is_financial:
                return self.default_params['default_wacc'] + 0.01  # Slightly higher for financials
            return self.default_params['default_wacc']
            
        except Exception as e:
            logger.warning(f"Error calculating WACC for {ticker.ticker}: {str(e)}")
            return self.default_params['default_wacc']
    
    def calculate_dcf(self, ticker_symbol, custom_params=None):
        """
        Calculate DCF fair value for a given ticker
        
        Args:
            ticker_symbol (str): Yahoo Finance ticker symbol
            custom_params (dict, optional): Custom parameters for the DCF model
            
        Returns:
            dict: Dictionary with DCF calculation results
        """
        logger.info(f"Calculating DCF fair value for {ticker_symbol}")
        
        # Merge custom parameters with defaults
        params = self.default_params.copy()
        if custom_params:
            params.update(custom_params)
        
        try:
            # Fetch stock data
            stock = self.fetch_with_retry(ticker_symbol)
            if stock is None:
                logger.error(f"Failed to fetch data for {ticker_symbol}")
                return {
                    'ticker': ticker_symbol,
                    'fair_value': None,
                    'calculation_method': 'failed',
                    'error': 'Failed to fetch stock data'
                }
            
            # Get basic stock information
            info = stock.info
            company_name = info.get('shortName', ticker_symbol)
            current_price = info.get('currentPrice')
            shares_outstanding = info.get('sharesOutstanding')
            
            if not current_price or not shares_outstanding:
                logger.error(f"Missing required data for {ticker_symbol}: current_price or shares_outstanding")
                return {
                    'ticker': ticker_symbol,
                    'company': company_name,
                    'fair_value': None,
                    'calculation_method': 'failed',
                    'error': 'Missing price or shares outstanding data'
                }
            
            # Get financial data
            financial_data = self.get_financial_data(stock)
            is_financial = financial_data['is_financial']
            
            # Select valuation method based on available data and company type
            calculation_method = "DCF"
            fair_value = None
            
            # For financial stocks or when FCF is negative, use earnings-based valuation
            if is_financial or (financial_data['free_cash_flow'] is None or financial_data['free_cash_flow'] <= 0):
                if financial_data['earnings'] and financial_data['earnings'] > 0:
                    # Use earnings-based valuation for financials
                    fair_value = self.calculate_earnings_based_value(stock, financial_data, params)
                    calculation_method = "Earnings-Based"
                elif financial_data['book_value'] and financial_data['book_value'] > 0:
                    # Fall back to price-to-book for financials if earnings not available
                    fair_value = self.calculate_ptb_value(stock, financial_data, params)
                    calculation_method = "Price-to-Book"
            else:
                # Use standard DCF for non-financials with positive FCF
                fair_value = self.calculate_fcf_based_value(stock, financial_data, params)
                calculation_method = "FCF-Based DCF"
            
            # If all methods failed, try one more earnings multiple approach
            if fair_value is None and 'trailingEps' in info and info['trailingEps'] is not None:
                eps = info['trailingEps']
                if eps > 0:
                    # Use a standard industry multiple (conservative)
                    industry_pe = 15  # Conservative PE ratio
                    fair_value = eps * industry_pe
                    calculation_method = "P/E Multiple"
            
            if fair_value is None:
                logger.error(f"Could not calculate fair value for {ticker_symbol} with any method")
                return {
                    'ticker': ticker_symbol,
                    'company': company_name,
                    'fair_value': None,
                    'calculation_method': 'failed',
                    'error': 'Insufficient data for valuation'
                }
            
            # Calculate discount/premium
            discount_percent = ((fair_value / current_price) - 1) * 100
            
            # Cap fair value to be within reasonable bounds of current price
            # This prevents extreme outliers from skewing results
            max_premium = 300  # Cap at 300% premium
            min_discount = -80  # Cap at 80% discount
            
            if discount_percent > max_premium:
                logger.warning(f"Capping extreme premium for {ticker_symbol}: {discount_percent:.1f}% -> {max_premium}%")
                fair_value = current_price * (1 + max_premium / 100)
                discount_percent = max_premium
            elif discount_percent < min_discount:
                logger.warning(f"Capping extreme discount for {ticker_symbol}: {discount_percent:.1f}% -> {min_discount}%")
                fair_value = current_price * (1 + min_discount / 100)
                discount_percent = min_discount
            
            return {
                'ticker': ticker_symbol,
                'company': company_name,
                'fair_value': fair_value,
                'current_price': current_price,
                'discount_percent': discount_percent,
                'calculation_method': calculation_method
            }
            
        except Exception as e:
            logger.error(f"Error calculating DCF for {ticker_symbol}: {str(e)}")
            return {
                'ticker': ticker_symbol,
                'fair_value': None,
                'calculation_method': 'failed',
                'error': str(e)
            }
    
    def calculate_fcf_based_value(self, ticker, financial_data, params):
        """
        Calculate DCF value based on Free Cash Flow
        
        Args:
            ticker (yf.Ticker): Yahoo Finance ticker object
            financial_data (dict): Financial data from get_financial_data
            params (dict): Model parameters
            
        Returns:
            float: Fair value per share
        """
        try:
            fcf = financial_data['free_cash_flow']
            if fcf is None or fcf <= 0:
                logger.warning(f"Invalid FCF for {ticker.ticker}: {fcf}")
                return None
                
            growth_rate = financial_data['growth_rate'] or params['default_growth_rate']
            shares_outstanding = ticker.info.get('sharesOutstanding')
            
            # Get WACC
            wacc = self.get_wacc(ticker)
            terminal_growth = params['default_terminal_growth']
            
            # Project future cash flows
            projected_cash_flows = []
            for year in range(1, params['growth_years'] + 1):
                projected_fcf = fcf * (1 + growth_rate) ** year
                projected_cash_flows.append(projected_fcf)
                
            # Calculate terminal value
            terminal_value = projected_cash_flows[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
            
            # Calculate present value of cash flows
            present_values = []
            for year, cash_flow in enumerate(projected_cash_flows, 1):
                pv = cash_flow / (1 + wacc) ** year
                present_values.append(pv)
                
            # Calculate present value of terminal value
            terminal_pv = terminal_value / (1 + wacc) ** params['growth_years']
            
            # Calculate enterprise value
            enterprise_value = sum(present_values) + terminal_pv
            
            # Account for cash and debt if available
            net_cash = 0
            if 'totalCash' in ticker.info and 'totalDebt' in ticker.info:
                total_cash = ticker.info.get('totalCash', 0)
                total_debt = ticker.info.get('totalDebt', 0)
                net_cash = total_cash - total_debt
                
            # Calculate equity value
            equity_value = enterprise_value + net_cash
            
            # Calculate fair value per share
            fair_value = equity_value / shares_outstanding
            
            return fair_value
            
        except Exception as e:
            logger.error(f"Error in FCF-based valuation for {ticker.ticker}: {str(e)}")
            return None
    
    def calculate_earnings_based_value(self, ticker, financial_data, params):
        """
        Calculate value based on earnings (for financial stocks)
        
        Args:
            ticker (yf.Ticker): Yahoo Finance ticker object
            financial_data (dict): Financial data from get_financial_data
            params (dict): Model parameters
            
        Returns:
            float: Fair value per share
        """
        try:
            earnings = financial_data['earnings']
            if earnings is None or earnings <= 0:
                logger.warning(f"Invalid earnings for {ticker.ticker}: {earnings}")
                return None
                
            growth_rate = financial_data['growth_rate'] or params['default_growth_rate']
            shares_outstanding = ticker.info.get('sharesOutstanding')
            
            # Use a higher discount rate for earnings (more uncertain than FCF)
            wacc = self.get_wacc(ticker) + 0.01  # Add 1% to account for higher uncertainty
            terminal_growth = params['default_terminal_growth']
            
            # Project future earnings
            projected_earnings = []
            for year in range(1, params['growth_years'] + 1):
                projected_earning = earnings * (1 + growth_rate) ** year
                projected_earnings.append(projected_earning)
                
            # Calculate terminal value (using a PE ratio approach)
            terminal_pe = 12.0  # Conservative terminal PE ratio
            if financial_data['is_financial']:
                terminal_pe = 10.0  # Even more conservative for financials
                
            terminal_value = projected_earnings[-1] * terminal_pe
            
            # Calculate present value of earnings
            present_values = []
            for year, earning in enumerate(projected_earnings, 1):
                pv = earning / (1 + wacc) ** year
                present_values.append(pv)
                
            # Calculate present value of terminal value
            terminal_pv = terminal_value / (1 + wacc) ** params['growth_years']
            
            # Calculate total equity value (for earnings model, this is direct equity value)
            equity_value = sum(present_values) + terminal_pv
            
            # Calculate fair value per share
            fair_value = equity_value / shares_outstanding
            
            return fair_value
            
        except Exception as e:
            logger.error(f"Error in earnings-based valuation for {ticker.ticker}: {str(e)}")
            return None
    
    def calculate_ptb_value(self, ticker, financial_data, params):
        """
        Calculate value based on price-to-book ratio (for financial stocks)
        
        Args:
            ticker (yf.Ticker): Yahoo Finance ticker object
            financial_data (dict): Financial data from get_financial_data
            params (dict): Model parameters
            
        Returns:
            float: Fair value per share
        """
        try:
            book_value = financial_data['book_value']
            if book_value is None or book_value <= 0:
                logger.warning(f"Invalid book value for {ticker.ticker}: {book_value}")
                return None
                
            shares_outstanding = ticker.info.get('sharesOutstanding')
            
            # For financial stocks, price-to-book is a common valuation metric
            # Use a reasonable multiple based on ROE if available
            ptb_multiple = 1.0  # Default at 1x book value
            
            # Adjust based on ROE if available
            if 'returnOnEquity' in ticker.info and ticker.info['returnOnEquity'] is not None:
                roe = ticker.info['returnOnEquity']
                
                # Adjust PTB based on ROE (higher ROE justifies higher PTB)
                if roe > 0.20:  # Excellent ROE (>20%)
                    ptb_multiple = 2.0
                elif roe > 0.15:  # Very good ROE (15-20%)
                    ptb_multiple = 1.7
                elif roe > 0.10:  # Good ROE (10-15%)
                    ptb_multiple = 1.4
                elif roe > 0.05:  # Average ROE (5-10%)
                    ptb_multiple = 1.0
                else:  # Below average ROE (<5%)
                    ptb_multiple = 0.8
            
            # Calculate fair value per share
            book_value_per_share = book_value / shares_outstanding
            fair_value = book_value_per_share * ptb_multiple
            
            return fair_value
            
        except Exception as e:
            logger.error(f"Error in price-to-book valuation for {ticker.ticker}: {str(e)}")
            return None
            
    def generate_dcf_report(self, ticker_symbols):
        """
        Generate a DCF analysis report for multiple tickers
        
        Args:
            ticker_symbols (list): List of ticker symbols
            
        Returns:
            str: Path to the generated Excel report
        """
        results = []
        for ticker in ticker_symbols:
            try:
                result = self.calculate_dcf(ticker)
                if result and 'fair_value' in result and result['fair_value'] is not None:
                    results.append(result)
                else:
                    logger.warning(f"Failed to calculate fair value for {ticker}")
            except Exception as e:
                logger.error(f"Error in DCF calculation for {ticker}: {str(e)}")
        
        if not results:
            logger.error("No valid DCF results to save")
            return None
            
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Generate Excel file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_path = os.path.join(self.default_params['output_dir'], f'dcf_values_{timestamp}.xlsx')
        
        try:
            # Save to Excel
            df.to_excel(excel_path, index=False)
            logger.info(f"DCF report saved to {excel_path}")
            return excel_path
        except Exception as e:
            logger.error(f"Error saving DCF report: {str(e)}")
            return None
            
    def generate_fair_values_dict(self, ticker_symbols):
        """
        Generate a dictionary of fair values for use in AEX scanner
        
        Args:
            ticker_symbols (list): List of ticker symbols
            
        Returns:
            dict: Dictionary mapping ticker symbols to fair values
        """
        fair_values = {}
        for ticker in ticker_symbols:
            try:
                result = self.calculate_dcf(ticker)
                if result and 'fair_value' in result and result['fair_value'] is not None:
                    fair_values[ticker] = result['fair_value']
                    logger.info(f"DCF fair value for {ticker}: {result['fair_value']:.2f} ({result['calculation_method']})")
            except Exception as e:
                logger.error(f"Error generating fair value for {ticker}: {str(e)}")
                
        return fair_values

def calculate_dcf_fair_values(ticker_symbols):
    """
    Helper function to calculate DCF fair values for a list of tickers
    
    Args:
        ticker_symbols (list): List of ticker symbols
        
    Returns:
        dict: Dictionary mapping ticker symbols to their DCF fair values
    """
    dcf_model = DCFModel()
    return dcf_model.generate_fair_values_dict(ticker_symbols)

def generate_dcf_report(ticker_symbols):
    """
    Helper function to generate a DCF report for multiple tickers
    
    Args:
        ticker_symbols (list): List of ticker symbols
        
    Returns:
        str: Path to the generated Excel report
    """
    dcf_model = DCFModel()
    return dcf_model.generate_dcf_report(ticker_symbols)

if __name__ == "__main__":
    # Test with some AEX stocks
    test_tickers = ["ASML.AS", "INGA.AS", "ADYEN.AS", "ABN.AS", "KPN.AS"]
    
    print("Calculating DCF fair values for test tickers...")
    dcf_model = DCFModel()
    
    for ticker in test_tickers:
        result = dcf_model.calculate_dcf(ticker)
        if result and 'fair_value' in result and result['fair_value'] is not None:
            print(f"{result['ticker']} ({result['company']}): "
                  f"Fair Value: €{result['fair_value']:.2f}, "
                  f"Current: €{result['current_price']:.2f}, "
                  f"Discount: {result['discount_percent']:.2f}%, "
                  f"Method: {result['calculation_method']}")
        else:
            print(f"Could not calculate fair value for {ticker}")
            
    # Generate a report with all tickers
    report_path = generate_dcf_report(test_tickers)
    if report_path:
        print(f"DCF report saved to {report_path}")
