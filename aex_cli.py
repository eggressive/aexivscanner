#!/usr/bin/env python3
"""
AEX DCF Scanner - Main CLI interface
"""

import argparse
import sys
import os
import subprocess
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('aex_cli.log')
    ]
)
logger = logging.getLogger(__name__)

def run_scanner():
    """Run the AEX scanner"""
    logger.info("Running AEX Scanner...")
    subprocess.run([sys.executable, 'aex_scanner.py'])
    
def run_visualizer():
    """Run the visualizer to create charts and graphs"""
    logger.info("Running Visualizer...")
    subprocess.run([sys.executable, 'aex_visualizer.py'])
    
def update_fair_values():
    """Run the fair value updater"""
    logger.info("Running Fair Value Updater...")
    # First apply any saved SimplyWall.st values
    logger.info("Applying saved SimplyWall.st fair values...")
    subprocess.run([sys.executable, 'update_simply_wall_st.py', '--apply-only'])
    # Then run the analyst target price updater
    logger.info("Fetching analyst target prices...")
    subprocess.run([sys.executable, 'fair_value_updater.py'])
    
def setup_environment():
    """Check and set up the environment"""
    logger.info("Checking environment...")
    
    # Create required directories
    required_dirs = ['outputs', 'visualizations', 'backups']
    for directory in required_dirs:
        if not os.path.exists(directory):
            logger.info(f"Creating {directory} directory...")
            os.makedirs(directory, exist_ok=True)
    
    # Check for required files
    required_files = [
        'aex_scanner.py',
        'aex_visualizer.py',
        'fair_value_updater.py',
        'update_simply_wall_st.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
            
    if missing_files:
        logger.error(f"Missing required files: {', '.join(missing_files)}")
        return False
    
    # Check for required packages
    try:
        import pandas
        import numpy
        import yfinance
        import openpyxl
        import matplotlib
        logger.info("All required packages are installed")
        return True
    except ImportError as e:
        logger.error(f"Missing required packages: {str(e)}")
        print("Installing required packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AEX DCF Scanner - Calculate valuation metrics for AEX stocks"
    )
    
    parser.add_argument(
        '-s', '--scan', 
        action='store_true', 
        help='Run the scanner to get current valuation metrics'
    )
    
    parser.add_argument(
        '-v', '--visualize', 
        action='store_true', 
        help='Create visualizations from the latest scan results'
    )
    
    parser.add_argument(
        '-u', '--update', 
        action='store_true', 
        help='Update fair value estimates from analyst targets'
    )
    
    parser.add_argument(
        '-a', '--all', 
        action='store_true', 
        help='Run all components: update, scan, and visualize'
    )
    
    args = parser.parse_args()
    
    # Check environment
    if not setup_environment():
        print("Environment setup failed. Please check the logs.")
        return
    
    # If no arguments provided, show help
    if not args.scan and not args.visualize and not args.update and not args.all:
        parser.print_help()
        return
    
    # Run all components
    if args.all:
        print("Running complete DCF analysis workflow...")
        update_fair_values()
        run_scanner()
        run_visualizer()
        return
    
    # Run individual components
    if args.update:
        update_fair_values()
        
    if args.scan:
        run_scanner()
        
    if args.visualize:
        run_visualizer()

if __name__ == "__main__":
    print(f"AEX DCF Scanner - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    main()
