#!/bin/bash
# Quick demo of the validation tool for AEX stocks

echo "============================================="
echo "AEX Stock Validator Demo"
echo "============================================="
echo ""
echo "Checking a sample of AEX stocks for data availability..."
echo ""

# Run the validator on a few representative stocks
python ticker_validator.py ASML.AS KPN.AS AD.AS PRX.AS

echo ""
echo "============================================="
echo "To check all tickers from CSV file (default behavior), run:"
echo "python ticker_validator.py"
echo ""
echo "For a specific ticker with detailed info, run:"
echo "python ticker_validator.py --verbose TICKER.AS"
echo ""
echo "To generate a JSON configuration file:"
echo "python ticker_validator.py --from-csv --generate-config"
echo ""
echo "To customize wait time between tests:"
echo "python ticker_validator.py --wait 0.5"
echo "============================================="
