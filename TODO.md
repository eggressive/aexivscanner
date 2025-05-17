# AEX IV Scanner - TODOs

## Future Enhancements

1. Investigate ticker validation errors in update_tickers.py
   - Debug HTTP 500 errors occurring with several tickers (ASML.AS, IMCD.AS, INGA.AS, MT.AS, RDSA.AS, TKWY.AS)
   - Research why some tickers can't be validated (DSM.AS, URW.AS)
   - Implement more robust error handling for these specific cases
   - Consider adding a retry mechanism with longer delays for HTTP 500 errors
   - Update documentation with troubleshooting steps for ticker validation issues

2. Investigate possibility to download fair value estimates for free
   - Research public APIs that provide DCF or fair value estimates
   - Look for alternatives to SimplyWall.st that offer free data access
   - Explore web scraping options (with proper respect for terms of service)
   - Consider academic or open-source valuation models

3. Calculate simplified DCF model as a Python function
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

## Completed Enhancements

1. ✅ Implement robust error handling for Yahoo Finance API
   - Added exponential backoff with jitter for rate limiting
   - Implemented automatic retries for connection issues
   - Added comprehensive data validation
   - Created detailed error logging and reporting
   - Built a diagnostic tool (`validate_ticker.py`) for troubleshooting

2. ✅ Create a single source of truth for AEX stock tickers
   - AEX_TICKERS are now stored in tickers.json
   - All modules read from this common data source via aex_tickers.py:
     - aex_scanner.py
     - fair_value_updater.py
     - aex_visualizer.py
     - validate_ticker.py
   - Ensures consistent ticker lists across the application
   - Simplifies adding/removing stocks from the scanner
   
3. ✅ Remove hardcoded file paths from JSON files
   - Removed filepath comments from tickers.json
   - Updated update_tickers.py to not add filepath comments
   - Ensured all modules use relative paths consistently
