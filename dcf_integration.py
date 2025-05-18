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
    Update fair values using the DCF model and save to the scanner
    """
    logger.info("Updating fair values with DCF calculations...")

    try:
        # Import here to avoid circular imports
        from dcf_model import calculate_dcf_fair_values
        
        # Calculate DCF fair values
        dcf_values = calculate_dcf_fair_values(AEX_TICKERS)
        
        if not dcf_values:
            logger.error("No DCF values were calculated")
            return False
        
        # Save to JSON file
        dcf_file = 'dcf_fair_values.json'
        try:
            with open(dcf_file, 'w') as f:
                json.dump({
                    'values': dcf_values,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }, f, indent=4)
            logger.info(f"Saved {len(dcf_values)} DCF fair values to {dcf_file}")
        except Exception as e:
            logger.error(f"Error saving DCF fair values: {str(e)}")
            return False
            
        # Update the scanner file
        return update_scanner_file(dcf_values)
        
    except Exception as e:
        logger.error(f"Error updating fair values with DCF: {str(e)}")
        return False

def update_scanner_file(fair_values):
    """
    Update the FAIR_VALUE_ESTIMATES dictionary in aex_scanner.py
    
    Args:
        fair_values (dict): Dictionary of ticker symbols to fair values
        
    Returns:
        bool: True if successful, False otherwise
    """
    scanner_file = 'aex_scanner.py'
    
    # Create backups directory if it doesn't exist
    backups_dir = 'backups'
    os.makedirs(backups_dir, exist_ok=True)
    
    try:
        # Read the file content
        with open(scanner_file, 'r') as f:
            content = f.read()
        
        # Create a backup
        backup_file = f"{backups_dir}/aex_scanner_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        try:
            with open(backup_file, 'w') as f:
                f.write(content)
            logger.info(f"Created backup at {backup_file}")
        except Exception as e:
            logger.warning(f"Failed to create backup: {str(e)}")
        
        # Find the FAIR_VALUE_ESTIMATES dictionary
        start_marker = "FAIR_VALUE_ESTIMATES = {"
        end_marker = "}"
        
        start_pos = content.find(start_marker)
        if start_pos == -1:
            logger.error("Could not find FAIR_VALUE_ESTIMATES in the scanner file")
            return False
            
        # Find the end of the dictionary
        start_pos += len(start_marker)
        level = 1
        end_pos = start_pos
        
        while level > 0 and end_pos < len(content):
            if content[end_pos] == '{':
                level += 1
            elif content[end_pos] == '}':
                level -= 1
            end_pos += 1
        
        # Create the new dictionary content
        new_dict_content = "\n"
        for ticker, value in fair_values.items():
            new_dict_content += f"    '{ticker}': {value},\n"
        
        # Replace the old dictionary content
        updated_content = content[:start_pos] + new_dict_content + content[end_pos-1:]
        
        # Write the updated content
        with open(scanner_file, 'w') as f:
            f.write(updated_content)
            
        logger.info(f"Successfully updated {scanner_file} with {len(fair_values)} DCF fair values")
        return True
        
    except Exception as e:
        logger.error(f"Error updating scanner file: {str(e)}")
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
