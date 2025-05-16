#!/bin/bash
# Update AEX tickers from Yahoo Finance

echo "========================================"
echo "AEX Ticker Updater"
echo "========================================"

# Check for help flag
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: ./update_aex_tickers.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --no-validate    Skip validation of tickers (include all potential tickers)"
    echo "  --force          Force update even if fewer than 10 tickers are found"
    echo "  --dry-run        Show what would be updated without making changes"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./update_aex_tickers.sh                  # Normal update with validation"
    echo "  ./update_aex_tickers.sh --no-validate    # Update without validating tickers"
    echo "  ./update_aex_tickers.sh --dry-run        # Preview update without changing files"
    exit 0
fi

echo "Fetching current AEX components from Yahoo Finance..."
echo ""

# Run the ticker updater script with any provided arguments
python3 update_tickers.py "$@"

# Check if update was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Verifying ticker source:"
    echo "========================================"
    
    # Verify the tickers after update
    python3 aex_tickers.py --check
fi
