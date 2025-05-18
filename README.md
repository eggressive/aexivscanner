<!-- filepath: /home/dimitar/python/aexivscanner/README.md -->
# AEX DCF Scanner

A live-updating Discounted Cash Flow (DCF) scanner for AEX (Amsterdam Exchange)
stocks that pulls data from Yahoo Finance API, calculates valuations, and ranks
stocks by undervaluation.

## Features

- Pulls real-time stock data from Euronext website
- Uses stored fair value estimates per stock
- Calculates key metrics:
  - Market Cap
  - Fair Market Cap
  - Discount Margin
  - Discount %
- Auto-ranks stocks by undervaluation
- Saves results to Excel with formatted output
- Centralized ticker management system:
  - Single source of truth for ticker symbols with CSV file
  - Robust error handling for API issues
  - Direct and reliable ticker data from Euronext
  - Automatic ticker updates with Euronext website integration

## Installation

### Standard Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Virtual Environment Installation (Recommended)

Using a virtual environment is recommended to avoid conflicts with other Python packages:

1. Clone this repository
2. Create a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS
source venv/bin/activate
# On Windows
venv\Scripts\activate
```

1. Install dependencies in the virtual environment:

```bash
pip install -r requirements.txt
```

1. When you're done, you can deactivate the virtual environment:

```bash
deactivate
```

## Usage

### Running the Scanner

Run the scanner:

```bash
python aex_scanner.py
```

Or use the convenience script that automatically applies the latest fair values:

```bash
./run_scanner.sh
```

The scanner will:

1. Fetch current price data for all AEX stocks
2. Calculate valuation metrics based on provided fair value estimates
3. Rank stocks by discount percentage (undervaluation)
4. Save results to an Excel file with timestamp

## Recent Refactoring

### 1. Ticker Management Refactoring

The codebase has been refactored to use a single source of truth for ticker symbols:

- **amsterdam_aex_tickers.csv** is now the primary source of ticker data
- **tickers.json** serves as a backup when the CSV is unavailable
- All components now share the same ticker data source

#### Key Changes

1. **Improved `aex_tickers.py` module as the central ticker provider**
   - Updated `load_tickers()` to prioritize loading from CSV file first
   - Added proper error handling and detailed diagnostics
   - Implemented CSV file parsing with comment handling
   - Added backup functionality through JSON file
   - Created CLI options to check ticker sources and update JSON

2. **Enhanced ticker management and diagnostics**
   - Added `check_ticker_source()` to provide detailed information about ticker sources
   - Improved `update_json_from_csv()` function to maintain backups of ticker data
   - Added `--investigate` option to help diagnose problematic tickers

3. **Improved ticker handling**
   - Removed hardcoded ticker lists in favor of loading from CSV
   - Relies fully on Euronext as the authoritative source for tickers
   - Improved validation logic for ticker data
   - Enhanced error messages to guide users when ticker sources can't be found

4. **Updated `euronext_tickers.py` to work with new model**
   - Made it populate the CSV file as the primary source of truth
   - Added functionality to update the JSON backup file automatically
   - Improved error handling and user feedback

5. **Added investigation tools**
   - Created better diagnostic messages throughout the codebase
   - Made the investigation tool more comprehensive

#### Benefits

1. **Single Source of Truth**: All components now share the same ticker data source
2. **Better Maintainability**: Easier to update ticker data across the entire system
3. **Improved Error Handling**: Clear error messages and diagnostics
4. **Direct Data Source**: Tickers come directly from Euronext, eliminating
   need for special case handling
5. **Better Documentation**: CLI options and code comments explain the system design

#### Management Commands

- `python aex_tickers.py --check` to verify ticker sources
- `python aex_tickers.py --update-json` to update JSON from CSV data
- `python aex_tickers.py --investigate` to diagnose problematic tickers
- `python euronext_tickers.py` to refresh ticker data from Euronext

### 2. Script Consolidation

To reduce redundancy and improve maintainability:

- Consolidated `validate_ticker.py`, `ticker_validator.py`, and
  `test_ticker_validation.py` into a single comprehensive validation tool
- The consolidated script now lives in `test_ticker_validation.py` with
  enhanced features:
  - Basic ticker validation (`--all` or specific tickers)
  - Field completeness checking (`--check-fields`)
  - Detailed information display (`--verbose`)
  - Full field listing (`--very-verbose`)
- Symlinks maintain backward compatibility:
  - `validate_ticker.py -> test_ticker_validation.py`
  - `ticker_validator.py -> test_ticker_validation.py`

## Fair Value Estimates

The system supports multiple ways to manage fair value estimates using a centralized
configuration system. All fair values are stored in `fair_values_config.json` and
managed through the `config_manager.py` module.

### Fair Value Sources

The system supports multiple fair value sources with a priority system:

1. **Manual Values**: Custom values entered manually (highest priority)
2. **DCF Model**: Automatically calculated DCF valuations using the integrated model
3. **Analyst Targets**: Automatic update using Yahoo Finance analyst target prices

You can view the current configuration and sources by running:

```bash
python config_manager.py --show
```

### Using the Built-in DCF Model

The system includes a sophisticated DCF model that can automatically calculate fair values:

```bash
python dcf_integration.py
```

The DCF model includes:

- **Multiple Valuation Methods**:
  - FCF-based DCF for non-financial companies
  - Earnings-based valuation for financial stocks (banks, insurance)
  - Price-to-Book valuation as a fallback for financial stocks
  - P/E multiple as a final fallback option

- **Features**:
  - Automatic detection of financial vs. non-financial stocks
  - Handling of negative free cash flows
  - Adjustment for company-specific growth rates
  - Risk-adjusted discount rates (WACC) based on beta
  - Detailed DCF report generation in Excel format

- **Report Generation**:

```bash
python dcf_integration.py --report
```

Creates a detailed Excel report with calculated fair values in the `outputs` directory.

- **Fair Value Updates**:

```bash
python dcf_integration.py --update
```

Updates the fair value configuration with calculated DCF values.

### Updating from Analyst Target Prices

The system can automatically fetch analyst consensus target prices from Yahoo Finance:

```bash
python fair_value_updater.py
```

This script will:

1. Fetch analyst target prices for all tickers in the centralized ticker list
2. Save the values to the configuration system under the 'analyst' source
3. Maintain backward compatibility with `fair_values.json`
4. Generate a detailed Excel report showing current prices vs. targets

The `fair_value_updater.py` script uses Yahoo Finance's `targetMeanPrice` data,
which represents the consensus price target from analysts covering each stock.
This provides an objective, market-based estimate of fair value that can be used
alongside or instead of your own DCF analysis.

### Managing Fair Value Priorities

You can control which fair value source takes precedence using:

```bash
python config_manager.py --set-priority manual dcf analyst
```

This example sets 'manual' as the highest priority, followed by 'dcf', then 'analyst'.
The scanner will use the highest priority fair value available for each ticker.

## Ticker Management System

The codebase uses a centralized ticker management system with a clear source
hierarchy:

1. `amsterdam_aex_tickers.csv` - Primary source of truth for all ticker symbols
2. `tickers.json` - Backup source used only when the CSV file is unavailable

### Adding More Stocks

To add more stocks to the scanner:

1. Add the ticker symbol to the `amsterdam_aex_tickers.csv` file
2. Add a corresponding fair value estimate to the `FAIR_VALUE_ESTIMATES` dictionary
   in aex_scanner.py
3. Run `python aex_tickers.py --update-json` to update the backup JSON file

### Updating AEX Tickers

You can automatically update the list of AEX components from Euronext:

```bash
# Update amsterdam_aex_tickers.csv with the latest AEX components
python euronext_tickers.py
```

This script will:

- Connect to Euronext to get the latest AEX components
- Extract both Euronext and Yahoo Finance ticker symbols
- Update the CSV file with the latest ticker symbols
- Automatically update the backup JSON file
- Create backups of previous ticker data

### Ticker Source Management

The application includes powerful tools to manage and check ticker symbols:

```bash
# Display all tickers with their source information
python aex_tickers.py --source

# Check if tickers are loaded from the expected source
python aex_tickers.py --check

# Update the backup JSON file from the primary CSV
python aex_tickers.py --update-json
```

The system provides detailed diagnostics about where ticker symbols are being
loaded from and ensures consistent ticker data by using Euronext as the
authoritative source.

## Output

The scanner generates an Excel file in the `outputs/` directory with the
following metrics:

- **Ticker**: Stock ticker symbol (Amsterdam Exchange)
- **Company**: Company name
- **Current Price**: Current stock price in Euros
- **Fair Value**: Estimated fair value per share based on DCF analysis
- **Market Cap (M)**: Current market capitalization in millions
- **Fair Market Cap (M)**: Fair market capitalization based on fair value in millions
- **Discount Margin (M)**: Difference between fair and current market cap in millions
- **Discount %**: How undervalued/overvalued the stock is

Stocks are ranked by discount percentage (undervaluation) in descending order.
The output file name contains a timestamp to keep track of when each scan was
performed (e.g., `aex_stock_valuation_20250516_111000.xlsx`).

### Excel Features

- **Header Descriptions**: Each column has a description explaining the data
- **Conditional Formatting**:
  - Undervalued stocks (≥10% discount) are highlighted in green
  - Overvalued stocks (≥10% premium) are highlighted in red
- **Formatted Numbers**: All values are properly formatted with currency and
  percentage indicators

### Visualization Features

The scanner includes a visualization tool that generates the following charts
in the `visualizations/` directory:

- **Discount Percentage Bar Chart**: Shows which stocks are most undervalued/overvalued
- **Current Price vs Fair Value**: Side-by-side comparison of current stock prices
  and fair values
- **Market Cap Comparison**: Visual comparison of current versus fair market
  capitalization
- **Discount Margin Waterfall**: Shows the absolute discount/premium in millions
  of euros

To generate the visualizations, run:

```bash
python aex_visualizer.py
```

or use the automated workflow:

```bash
./run_scanner.sh
```

All visualizations are saved with timestamps to track when they were generated.

## Directory Structure

The scanner organizes its files in the following directories:

- **outputs/**: Contains all generated Excel files with the scan results
  - Includes scan results and fair value update reports
  - Files are named with timestamps, e.g., `aex_stock_valuation_20250516_111000.xlsx`

- **visualizations/**: Contains all generated charts and visualizations
  - Charts are organized by type and include timestamps
  - Includes discount percentage, price comparison, and margin charts

- **backups/**: Contains backup files created when updating data
  - Includes backups of tickers.json and aex_scanner.py
  - Backups are created automatically before making changes
  - Naming convention includes date and time of backup

## Key Files

The codebase includes the following important files:

- **aex_scanner.py**: Main scanner logic and scanner execution
- **aex_tickers.py**: Central ticker management module
- **amsterdam_aex_tickers.csv**: Primary source of ticker data
- **tickers.json**: Backup source of ticker data
- **config_manager.py**: Fair value configuration management system
- **fair_values_config.json**: Configuration file storing all fair value data
- **fair_value_updater.py**: Updates fair values from Yahoo Finance analyst targets
- **euronext_tickers.py**: Updates ticker data from Euronext
- **dcf_model.py**: Core DCF modeling logic for stock valuation
- **dcf_integration.py**: Integrates the DCF model with the configuration system
- **aex_visualizer.py**: Creates visualizations of scanner results
- **test_ticker_validation.py**: Consolidated ticker validation tool
- **check_aex_tickers.py**: AEX ticker validation utility
- **investigate_problematic_tickers.py**: Detailed ticker troubleshooting tool
- **aex_cli.py**: Command line interface for running the scanner
- **run_scanner.sh**: Convenience script for running the scanner with latest fair values

This organization ensures proper separation of concerns and makes maintenance easier.

## Troubleshooting & Data Validation

### Handling Data Issues

The scanner includes robust error handling for common issues:

- **Rate Limiting**: Implements exponential backoff with jitter to handle API rate limits
- **Connection Issues**: Automatically retries failed connections
- **Data Validation**: Validates data completeness before processing
- **Error Reporting**: Provides detailed logs of data quality issues
- **Direct Data Source**: Uses Euronext as authoritative source of ticker data

When running the scanner, you'll see a summary of successful and failed ticker retrievals:

```bash
Scan completed successfully!
Processed 17/21 tickers successfully.
Skipped 4 tickers due to data issues.
```

### Validating Individual Tickers

To troubleshoot data issues with specific tickers, use the included validation script:

```bash
# Check a specific ticker
python validate_ticker.py ASML.AS

# Check multiple tickers
python validate_ticker.py ADYEN.AS INGA.AS ASML.AS

# Check all AEX tickers
python validate_ticker.py --all

# Get more detailed information
python validate_ticker.py --verbose ASML.AS
```

This tool will:

- Check if the ticker data is available from Yahoo Finance
- Validate which fields are present or missing
- Show the current values for key metrics
- Help identify why certain tickers might be failing

Example output:

```bash
Validating ASML.AS...
  ✅ ASML.AS has all required fields

Key fields:
  shortName: ASML HOLDING
  longName: ASML Holding N.V.
  currentPrice: 675.6
  sharesOutstanding: 393200000
  marketCap: 265645916160
  volume: 148069
  averageVolume: 905397
  exchange: AMS
  currency: EUR
```

For tickers with issues, the output will indicate what's missing:

```bash
Validating DSM.AS...
  ⚠️ DSM.AS is missing 2/9 fields: currentPrice, sharesOutstanding
```

This helps ensure that all tickers from Euronext are properly formatted and
compatible with Yahoo Finance's data API.

## License

See the LICENSE file for details.
