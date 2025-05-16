# AEX IV Scanner - TODOs

## Completed Enhancements

1. ✅ Implement robust error handling for Yahoo Finance API
   - Added exponential backoff with jitter for rate limiting
   - Implemented automatic retries for connection issues
   - Added comprehensive data validation
   - Created detailed error logging and reporting
   - Built a diagnostic tool (`validate_ticker.py`) for troubleshooting

## Future Enhancements

1. Investigate possibility to download fair value estimates for free
   - Research public APIs that provide DCF or fair value estimates
   - Look for alternatives to SimplyWall.st that offer free data access
   - Explore web scraping options (with proper respect for terms of service)
   - Consider academic or open-source valuation models

2. Calculate simplified DCF model as a Python function
   - Implement basic DCF calculation based on:
     - Current free cash flow
     - Expected growth rate
     - Discount rate (WACC)
     - Terminal growth rate
   - Add this as an alternative fair value source
   - Create configuration options to choose between:
     - Manual fair values
     - SimplyWall.st values
     - Calculated DCF values

3. Create a single source of truth for AEX stock tickers
   - Move AEX_TICKERS dictionary to an external data file (JSON or YAML)
   - Update all modules to read from this common data source:
     - aex_scanner.py
     - fair_value_updater.py
     - aex_visualizer.py
     - validate_ticker.py
   - Ensures consistent ticker lists across the application
   - Simplifies adding/removing stocks from the scanner
