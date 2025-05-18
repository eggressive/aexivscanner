#!/usr/bin/env python3
"""
AEX DCF Scanner - Configuration Management Module

This module handles configuration loading and saving for the AEX DCF Scanner.
It provides a centralized way to manage fair value estimates from different sources.
"""

import os
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('config_manager.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration constants
FAIR_VALUES_CONFIG_FILE = 'fair_values_config.json'
CONFIG_BACKUP_DIR = 'backups'

def load_fair_values(source=None):
    """
    Load fair values from configuration file
    
    Args:
        source (str, optional): If provided, only return values from this source.
                               Options: 'manual', 'dcf', 'analyst', 'all' (default)
    
    Returns:
        dict: Dictionary of ticker symbols to fair values
    """
    if not os.path.exists(FAIR_VALUES_CONFIG_FILE):
        logger.warning(f"{FAIR_VALUES_CONFIG_FILE} not found, creating with empty values")
        
        # Initialize with any existing fair value files
        config = {'sources': {}}
        
        # Try to import from dcf_fair_values.json
        if os.path.exists('dcf_fair_values.json'):
            try:
                with open('dcf_fair_values.json', 'r') as f:
                    dcf_data = json.load(f)
                    if 'values' in dcf_data:
                        config['sources']['dcf'] = dcf_data['values']
                        logger.info("Imported values from dcf_fair_values.json")
            except Exception as e:
                logger.error(f"Error importing from dcf_fair_values.json: {str(e)}")
        
        # Try to import from fair_values.json (analyst values)
        if os.path.exists('fair_values.json'):
            try:
                with open('fair_values.json', 'r') as f:
                    analyst_data = json.load(f)
                    config['sources']['analyst'] = analyst_data
                    logger.info("Imported values from fair_values.json")
            except Exception as e:
                logger.error(f"Error importing from fair_values.json: {str(e)}")
        
        # Save the initial configuration
        save_config(config)
        
        # Return empty if we couldn't initialize anything
        if not config['sources']:
            return {}
    
    try:
        with open(FAIR_VALUES_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        # Handle source filtering
        if source == 'all' or source is None:
            # Combine all sources based on priority
            combined_values = {}
            sources = config.get('sources', {})
            
            # Get from all available sources based on priority
            for src in config.get('priority', ['manual', 'dcf', 'analyst']):
                if src in sources:
                    for ticker, value in sources[src].items():
                        if ticker not in combined_values:  # Only add if not already added from higher priority
                            combined_values[ticker] = value
            
            return combined_values
        elif source in config.get('sources', {}):
            return config['sources'][source]
        else:
            logger.warning(f"Source '{source}' not found in configuration")
            return {}
        
    except Exception as e:
        logger.error(f"Error loading fair values: {str(e)}")
        return {}

def save_fair_values(values, source='manual'):
    """
    Save fair values to configuration file
    
    Args:
        values (dict): Dictionary of ticker symbols to fair values
        source (str): Source of the fair values. Options: 'manual', 'dcf', 'analyst'
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create backup directory if it doesn't exist
        os.makedirs(CONFIG_BACKUP_DIR, exist_ok=True)
        
        # Load existing configuration if available
        config = {}
        if os.path.exists(FAIR_VALUES_CONFIG_FILE):
            try:
                with open(FAIR_VALUES_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                
                # Create a backup before modifying
                backup_file = f"{CONFIG_BACKUP_DIR}/fair_values_config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(backup_file, 'w') as f:
                    json.dump(config, f, indent=4)
                logger.info(f"Created backup at {backup_file}")
            except Exception as e:
                logger.warning(f"Could not create backup: {str(e)}")
        
        # Initialize structure if needed
        if 'sources' not in config:
            config['sources'] = {}
        
        # Set default priority if not present
        if 'priority' not in config:
            config['priority'] = ['manual', 'dcf', 'analyst']
        
        # Update the source values
        config['sources'][source] = values
        
        # Record update time
        config['last_updated'] = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': source
        }
        
        # Save the updated configuration
        with open(FAIR_VALUES_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        
        logger.info(f"Saved {len(values)} fair values from source '{source}'")
        return True
    except Exception as e:
        logger.error(f"Error saving fair values: {str(e)}")
        return False

def save_config(config):
    """
    Save the entire configuration
    
    Args:
        config (dict): Complete configuration dictionary
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(FAIR_VALUES_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")
        return False

def get_source_priority():
    """
    Get the priority order of fair value sources
    
    Returns:
        list: List of sources in priority order
    """
    try:
        if os.path.exists(FAIR_VALUES_CONFIG_FILE):
            with open(FAIR_VALUES_CONFIG_FILE, 'r') as f:
                config = json.load(f)
            return config.get('priority', ['manual', 'dcf', 'analyst'])
        return ['manual', 'dcf', 'analyst']  # Default priority
    except Exception as e:
        logger.error(f"Error getting source priority: {str(e)}")
        return ['manual', 'dcf', 'analyst']  # Default priority

def set_source_priority(priority_list):
    """
    Set the priority order of fair value sources
    
    Args:
        priority_list (list): List of sources in priority order
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not all(src in ['manual', 'dcf', 'analyst'] for src in priority_list):
            logger.error("Invalid priority list. Valid sources: 'manual', 'dcf', 'analyst'")
            return False
        
        if os.path.exists(FAIR_VALUES_CONFIG_FILE):
            with open(FAIR_VALUES_CONFIG_FILE, 'r') as f:
                config = json.load(f)
            
            config['priority'] = priority_list
            
            with open(FAIR_VALUES_CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            
            logger.info(f"Updated source priority: {priority_list}")
            return True
        else:
            logger.error(f"{FAIR_VALUES_CONFIG_FILE} not found")
            return False
    except Exception as e:
        logger.error(f"Error setting source priority: {str(e)}")
        return False

def initialize_from_scanner_py():
    """
    Initialize configuration from aex_scanner.py
    
    This is a one-time migration function to extract FAIR_VALUE_ESTIMATES 
    from aex_scanner.py and save them to the configuration file.
    """
    try:
        scanner_file = 'aex_scanner.py'
        if not os.path.exists(scanner_file):
            logger.error(f"{scanner_file} not found")
            return False
        
        # Read the file content
        with open(scanner_file, 'r') as f:
            content = f.read()
        
        # Find the FAIR_VALUE_ESTIMATES dictionary using regex
        import re
        pattern = r"FAIR_VALUE_ESTIMATES\s*=\s*{([^}]*)}"
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            logger.error(f"Could not find FAIR_VALUE_ESTIMATES in {scanner_file}")
            return False
            
        # Extract the dictionary content and parse it
        dict_content = match.group(1)
        fair_values = {}
        
        # Parse each line of the dictionary
        for line in dict_content.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Extract key and value using regex
            kv_match = re.match(r"'([^']+)':\s*([\d\.e+-]+),?", line)
            if kv_match:
                key = kv_match.group(1)
                try:
                    value = float(kv_match.group(2))
                    fair_values[key] = value
                except ValueError:
                    logger.warning(f"Could not parse value for key {key}: {kv_match.group(2)}")
        
        if fair_values:
            # Save as manual source (highest priority)
            save_fair_values(fair_values, source='manual')
            logger.info(f"Initialized {len(fair_values)} fair values from {scanner_file}")
            return True
        else:
            logger.error(f"Could not extract any fair values from {scanner_file}")
            return False
    
    except Exception as e:
        logger.error(f"Error initializing from scanner.py: {str(e)}")
        return False

if __name__ == "__main__":
    # If run directly, initialize configuration
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AEX DCF Scanner Configuration Manager"
    )
    
    parser.add_argument(
        '--init', 
        action='store_true',
        help='Initialize configuration from aex_scanner.py'
    )
    
    parser.add_argument(
        '--set-priority',
        nargs='+',
        choices=['manual', 'dcf', 'analyst'],
        help='Set the priority order of fair value sources'
    )
    
    parser.add_argument(
        '--show',
        action='store_true',
        help='Show current configuration'
    )
    
    args = parser.parse_args()
    
    if args.init:
        initialize_from_scanner_py()
    
    if args.set_priority:
        set_source_priority(args.set_priority)
    
    if args.show or (not args.init and not args.set_priority):
        try:
            if os.path.exists(FAIR_VALUES_CONFIG_FILE):
                with open(FAIR_VALUES_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                
                print("\nAEX DCF Scanner Configuration")
                print("============================\n")
                
                print(f"Priority Order: {config.get('priority', ['manual', 'dcf', 'analyst'])}")
                
                if 'last_updated' in config:
                    print(f"\nLast Updated: {config['last_updated']['time']} (Source: {config['last_updated']['source']})")
                
                print("\nAvailable Sources:")
                for source, values in config.get('sources', {}).items():
                    print(f"- {source}: {len(values)} fair values")
                
                print("\nCombined Fair Values:")
                combined = load_fair_values()
                print(f"- Total: {len(combined)} fair values")
            else:
                print(f"\nConfiguration file {FAIR_VALUES_CONFIG_FILE} not found.")
                print("Run with --init to initialize from aex_scanner.py")
        except Exception as e:
            print(f"Error showing configuration: {str(e)}")