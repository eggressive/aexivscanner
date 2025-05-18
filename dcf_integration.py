#!/usr/bin/env python3
"""
AEX DCF Integration - Integrates DCF calculations with the AEX scanner
"""

import os
import json
import logging
import sys
from datetime import datetime
from aex_tickers import AEX_TICKERS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('dcf_integration.log')
    ]
)
logger = logging.getLogger(__name__)

def update_fair_values_with_dcf():
    """
    Update fair values using the DCF model and save to the configuration
    """
    logger.info("Updating fair values with DCF calculations...")

    try:
        # Import here to avoid circular imports
        from dcf_model import calculate_dcf_fair_values
        from config_manager import save_fair_values
        
        # Calculate DCF fair values
        dcf_values = calculate_dcf_fair_values(AEX_TICKERS)
        
        if not dcf_values:
            logger.error("No DCF values were calculated")
            return False
        
        # Save to DCF-specific JSON file for backward compatibility
        dcf_file = 'dcf_fair_values.json'
        try:
            with open(dcf_file, 'w') as f:
                json.dump({
                    'values': dcf_values,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }, f, indent=4)
            logger.info(f"Saved {len(dcf_values)} DCF fair values to {dcf_file}")
        except Exception as e:
            logger.error(f"Error saving DCF fair values to legacy file: {str(e)}")
            # Continue anyway since this is just for backward compatibility
        
        # Save to the configuration system
        success = save_fair_values(dcf_values, source='dcf')
        
        if success:
            logger.info(f"Successfully saved {len(dcf_values)} DCF fair values to configuration")
            return True
        else:
            logger.error("Failed to save DCF fair values to configuration")
            return False
        
    except Exception as e:
        logger.error(f"Error updating fair values with DCF: {str(e)}")
        return False

def update_scanner_file(fair_values):
    """
    Legacy method to update the FAIR_VALUE_ESTIMATES dictionary in aex_scanner.py
    Now redirects to the configuration system
    
    Args:
        fair_values (dict): Dictionary of ticker symbols to fair values
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("update_scanner_file() is deprecated. Using configuration system instead.")
    
    try:
        from config_manager import save_fair_values
        return save_fair_values(fair_values, source='dcf')
    except Exception as e:
        logger.error(f"Error updating fair values: {str(e)}")
        return False

def generate_dcf_report():
    """
    Generate a detailed DCF analysis report for AEX stocks
    
    Returns:
        str: Path to the generated report or None if failed
    """
    try:
        from dcf_model import generate_dcf_report
        
        logger.info("Generating DCF analysis report...")
        report_path = generate_dcf_report(AEX_TICKERS)
        
        if report_path:
            logger.info(f"DCF report generated at {report_path}")
            return report_path
        else:
            logger.error("Failed to generate DCF report")
            return None
            
    except Exception as e:
        logger.error(f"Error generating DCF report: {str(e)}")
        return None

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--report':
            generate_dcf_report()
        elif sys.argv[1] == '--update':
            update_fair_values_with_dcf()
    else:
        # Default: Generate report and update fair values
        report_path = generate_dcf_report()
        success = update_fair_values_with_dcf()
        
        if report_path and success:
            print("\n✅ DCF Model Implementation Successful!")
            print(f"- DCF report saved to: {report_path}")
            print("- Fair values updated in aex_scanner.py")
            print("\nYou can now run the scanner to use the DCF fair values:")
            print("python aex_scanner.py")
        else:
            print("\n❌ There were some issues with the DCF implementation.")
            print("Check the dcf_integration.log file for details.")
