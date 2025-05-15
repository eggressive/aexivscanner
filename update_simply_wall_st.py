#!/usr/bin/env python3
"""
SimplyWall.st Fair Value Updater - Helper script to update fair values from SimplyWall.st
"""

import os
import re
import json
import sys
import argparse
from datetime import datetime

def update_fair_value(ticker, new_value):
    """Update a specific ticker's fair value in the aex_scanner.py file"""
    
    file_path = 'aex_scanner.py'
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return False
    
    try:
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Create backups directory if it doesn't exist
        backups_dir = 'backups'
        try:
            if not os.path.exists(backups_dir):
                os.makedirs(backups_dir)
                print(f"Created backup directory: {backups_dir}")
        except OSError as e:
            print(f"Warning: Could not create backup directory {backups_dir}: {str(e)}")
            print("Will save backup file in current directory.")
            backups_dir = '.'
        
        # Create a backup in the backups directory
        backup_file = f"{backups_dir}/aex_scanner_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        try:
            with open(backup_file, 'w') as f:
                f.write(content)
        except OSError as e:
            print(f"Warning: Could not create backup file {backup_file}: {str(e)}")
            print("Continuing without creating backup.")
        
        # Get the current date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Find the line with the ticker and replace it
        found = False
        for i, line in enumerate(lines):
            if f"'{ticker}':" in line or f'"{ticker}":' in line:
                # Extract the value and update it
                found = True
                # Replace the entire line
                lines[i] = f"    '{ticker}': {new_value},  # Updated from SimplyWall.st on {today}"
                break
                
        if not found:
            print(f"Warning: Could not find ticker {ticker} in the file")
            return False
            
        # Join the lines back together and write to the file
        updated_content = '\n'.join(lines)
        with open(file_path, 'w') as f:
            f.write(updated_content)
            
        print(f"Successfully updated fair value for {ticker} to {new_value}")
        print(f"Backup saved to {backup_file}")
        return True
        
    except Exception as e:
        print(f"Error updating fair value: {str(e)}")
        return False

def load_values_json():
    """Load ticker values from a JSON file"""
    
    file_path = 'simplywall_fair_values.json'
    
    # Load existing values if file exists
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                values = json.load(f)
                
            # Remove metadata key
            values.pop('_last_updated', None)
            return values
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in {file_path}: {str(e)}")
            print("The file exists but contains invalid JSON data.")
            return {}
        except OSError as e:
            print(f"Error reading file {file_path}: {str(e)}")
            print("The file exists but could not be read due to an OS error.")
            return {}
    else:
        print(f"No existing values file found at {file_path}")
        return {}

def save_values_json(ticker_values):
    """Save ticker values to a JSON file for future reference"""
    
    file_path = 'simplywall_fair_values.json'
    
    # Load existing values if file exists
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                existing_values = json.load(f)
                print(f"Successfully loaded existing values from {file_path}")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in {file_path}: {str(e)}")
            print("Creating new values file due to invalid JSON data.")
            existing_values = {}
        except OSError as e:
            print(f"Error reading file {file_path}: {str(e)}")
            print("Creating new values file due to file access issues.")
            existing_values = {}
    else:
        print(f"No existing values file found. Creating new file at {file_path}")
        existing_values = {}
    
    # Update with new values
    existing_values.update(ticker_values)
    
    # Add timestamp
    existing_values['_last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Save to file
    try:
        with open(file_path, 'w') as f:
            json.dump(existing_values, f, indent=4)
        print(f"Successfully saved values to {file_path}")
    except OSError as e:
        print(f"Error saving values to {file_path}: {str(e)}")
        print("Please check file permissions and disk space.")

def apply_saved_values():
    """Load values from the JSON file and apply them to the scanner file"""
    
    # Load saved values
    saved_values = load_values_json()
    
    if not saved_values:
        print("No previously saved values found.")
        return {}
        
    print(f"Found {len(saved_values)} previously saved fair values:")
    
    # Apply each value to the scanner file
    for ticker, value in saved_values.items():
        print(f"  - {ticker}: {value}")
        update_fair_value(ticker, value)
        
    print("\nAll saved values have been applied to the scanner file.")
    return saved_values

def main():
    """Main function to update fair values interactively"""
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Update fair values from SimplyWall.st'
    )
    parser.add_argument(
        '-a', '--apply-only',
        action='store_true',
        help='Only apply saved values without entering interactive mode'
    )
    args = parser.parse_args()
    
    print("SimplyWall.st Fair Value Updater")
    print("--------------------------------")
    
    # Load and apply saved values
    existing_values = apply_saved_values()
    
    # If --apply-only flag is set, exit after applying saved values
    if args.apply_only:
        print("\nApplied saved values and exiting.")
        return
    
    print("\nEnter additional ticker symbol and fair value from SimplyWall.st")
    print("Example: INGA.AS 43.98")
    print("Type 'done' when finished\n")
    
    ticker_values = {}
    
    while True:
        user_input = input("> ").strip()
        
        if user_input.lower() == 'done':
            break
        
        # Parse input
        parts = user_input.split()
        if len(parts) != 2:
            print("Invalid format. Please use: TICKER VALUE")
            continue
            
        ticker = parts[0]
        
        try:
            value = float(parts[1])
        except ValueError:
            print("Invalid value. Please enter a number.")
            continue
        
        # Update the fair value
        update_fair_value(ticker, value)
        
        # Store for JSON
        ticker_values[ticker] = value
    
    # Save all values to JSON if any were entered
    if ticker_values:
        save_values_json(ticker_values)
        
    print("\nUpdates complete!")

if __name__ == "__main__":
    main()
