#!/bin/bash
# AEX DCF Scanner runner script

# Navigate to the script directory
cd "$(dirname "$0")"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it to run this script."
    exit 1
fi

# Check if dependencies are installed
if [ ! -f ".deps_installed" ]; then
    echo "Installing dependencies..."
    python3 -m pip install -r requirements.txt
    touch .deps_installed
fi

# Run the CLI with all options
python3 aex_cli.py --all

# Open the visualizations directory if it exists
if [ -d "visualizations" ]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open visualizations/
    else
        echo "Visualizations created in: $(pwd)/visualizations/"
    fi
fi
