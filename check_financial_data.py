#!/usr/bin/env python3
"""
Check available financial data for implementing DCF model
"""

import yfinance as yf
import pandas as pd
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_available_data(ticker_symbol="ASML.AS"):
    """Check what financial data is available through yfinance for DCF calculation"""
    logger.info(f"Checking available financial data for {ticker_symbol}")
    
    try:
        # Get ticker data
        ticker = yf.Ticker(ticker_symbol)
        
        # Check for cash flow data
        logger.info("\nCash Flow Statement:")
        try:
            cashflow = ticker.cashflow
            if isinstance(cashflow, pd.DataFrame) and not cashflow.empty:
                logger.info(f"Cash flow data available with {cashflow.shape[0]} rows and {cashflow.shape[1]} columns")
                logger.info("Cash flow columns (first 10): " + ", ".join(cashflow.index[:10]))
                
                # Check for Free Cash Flow specifically
                fcf_indicators = ["Free Cash Flow", "FreeCashFlow", "freeCashFlow"]
                for indicator in fcf_indicators:
                    if indicator in cashflow.index:
                        logger.info(f"Found '{indicator}' in cash flow data!")
                        # Display a few years of data if available
                        fcf_data = cashflow.loc[indicator]
                        logger.info(f"Recent values: {fcf_data}")
                        
                logger.info("\nCash flow data sample (first 5 rows):")
                logger.info(cashflow.iloc[:5])
            else:
                logger.info("No cash flow data available")
        except Exception as e:
            logger.error(f"Error getting cash flow data: {str(e)}")
        
        # Check for financial info from info attribute
        logger.info("\nFinancial Info from info attribute:")
        try:
            info = ticker.info
            financial_keys = [
                'freeCashflow', 'operatingCashflow', 'totalCash', 'totalDebt',
                'returnOnEquity', 'revenueGrowth', 'operatingMargins', 'beta'
            ]
            
            available_keys = []
            for key in financial_keys:
                if key in info:
                    available_keys.append(f"{key}: {info[key]}")
            
            if available_keys:
                logger.info("Available financial indicators: " + ", ".join(available_keys))
            else:
                logger.info("No relevant financial indicators found in info attribute")
        except Exception as e:
            logger.error(f"Error getting info attribute: {str(e)}")
            
        # Check historical growth rates
        logger.info("\nHistorical Growth Data:")
        try:
            financials = ticker.financials
            if isinstance(financials, pd.DataFrame) and not financials.empty:
                logger.info(f"Financial data available with {financials.shape[0]} rows and {financials.shape[1]} columns")
                logger.info("Financial statement rows (first 10): " + ", ".join(financials.index[:10]))
            else:
                logger.info("No financial statement data available")
        except Exception as e:
            logger.error(f"Error getting financial statements: {str(e)}")
            
        # Check analyst recommendations for growth estimates
        logger.info("\nAnalyst Recommendations:")
        try:
            recommendations = ticker.recommendations
            if isinstance(recommendations, pd.DataFrame) and not recommendations.empty:
                logger.info(f"Recommendations data available with {recommendations.shape[0]} rows")
                logger.info(recommendations.head())
            else:
                logger.info("No recommendations data available")
                
            # Check for analyst estimates
            logger.info("\nAnalyst Estimates:")
            estimates = ticker.get_analyst_forecast()
            if isinstance(estimates, pd.DataFrame) and not estimates.empty:
                logger.info(f"Analyst estimates available: {estimates.columns}")
                logger.info(estimates.head())
            else:
                logger.info("No analyst estimates available")
        except Exception as e:
            logger.error(f"Error getting recommendations/estimates: {str(e)}")
            
        # Check for Balance Sheet
        logger.info("\nBalance Sheet Data:")
        try:
            balance = ticker.balance_sheet
            if isinstance(balance, pd.DataFrame) and not balance.empty:
                logger.info(f"Balance sheet data available with {balance.shape[0]} rows")
                logger.info("Balance sheet rows (first 10): " + ", ".join(balance.index[:10]))
            else:
                logger.info("No balance sheet data available")
        except Exception as e:
            logger.error(f"Error getting balance sheet: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error during data check for {ticker_symbol}: {str(e)}")
        
if __name__ == "__main__":
    check_available_data()
    # Uncomment to test another ticker
    # check_available_data("INGA.AS")
