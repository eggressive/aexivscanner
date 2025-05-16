#!/bin/bash
# Quick demo of the validation tool for AEX stocks

echo "============================================="
echo "AEX Stock Validator Demo"
echo "============================================="
echo ""
echo "Checking a sample of AEX stocks for data availability..."
echo ""

# Run the validator on a few representative stocks
python validate_ticker.py ASML.AS KPN.AS DSM.AS RELX.AS

echo ""
echo "============================================="
echo "To check all AEX stocks, run:"
echo "python validate_ticker.py --all"
echo ""
echo "For a specific ticker with detailed info, run:"
echo "python validate_ticker.py --verbose TICKER.AS"
echo "============================================="
