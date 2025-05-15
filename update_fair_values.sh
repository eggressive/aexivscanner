#!/bin/bash
# Update fair values from SimplyWall.st

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

echo "======================================="
echo "SimplyWall.st Fair Value Updater"
echo "======================================="
echo ""
echo "This script will help you update fair values from SimplyWall.st"
echo ""
echo "Instructions:"
echo "1. Visit SimplyWall.st for each stock (e.g., https://simplywall.st/stocks/nl/semiconductors/ams-asml/asml-holding-shares/valuation)"
echo "2. Find the 'Fair Value' displayed in the Valuation section"
echo "3. Enter ticker and fair value when prompted (format: TICKER VALUE)"
echo "4. Type 'done' when finished"
echo ""

# Run the SimplyWall.st updater
python3 update_simply_wall_st.py

echo ""
echo "Fair values have been updated."
echo "Run './run_scanner.sh' to refresh the scanner with the new values."
