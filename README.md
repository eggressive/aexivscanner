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
- Multi-source fair value system:
  - DCF model-based valuations (primary source)
  - Manual override capability
  - Analyst target price integration
  - Configurable priority between sources

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

### 2. Fair Value Configuration System

The codebase has been refactored to use a configurable fair value system:

- **Multiple sources of fair values:** DCF model, manual inputs, and analyst targets
- **Configurable priority:** Define which source takes precedence (DCF is now primary)
- **Centralized configuration:** All fair values managed through `fair_values_config.json`

For detailed information on configuring and using the fair value system, see:
[Fair Value Configuration Guide](docs/fair_value_configuration.md)

## Scanner Output

The scanner generates an Excel file with the following columns:

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
- **tickers_config.json**: Validated ticker list generated by ticker validator
- **config_manager.py**: Fair value configuration management system
- **fair_values_config.json**: Configuration file storing all fair value data
- **fair_value_updater.py**: Updates fair values from Yahoo Finance analyst targets
- **euronext_tickers.py**: Updates ticker data from Euronext
- **dcf_model.py**: Core DCF modeling logic for stock valuation
- **dcf_integration.py**: Integrates the DCF model with the configuration system
- **aex_visualizer.py**: Creates visualizations of scanner results
- **ticker_validator.py**: Unified ticker validation system with config generation
- **test_ticker_validation.py**: Legacy ticker validation tool (superseded)
- **check_aex_tickers.py**: Legacy AEX ticker validation utility (superseded)
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

### Validating Tickers

To troubleshoot data issues with specific tickers, use the unified validation tool:

```bash
# Ticker validation (defaults to --from-csv --wait 1 if no parameters):
python ticker_validator.py                              # Default: validate all CSV tickers
python ticker_validator.py ASML.AS INGA.AS MT.AS        # Validate specific tickers
python ticker_validator.py --verbose ASML.AS            # Show detailed information
python ticker_validator.py --check-fields ASML.AS       # Check for key data fields
python ticker_validator.py --from-csv --wait 2          # Customize wait time between tests
python ticker_validator.py --generate-config            # Generate ticker configuration JSON
```

This comprehensive tool will:

- Check if ticker data is available from Yahoo Finance
- Validate which fields are present or missing
- Show current values for key metrics
- Generate a validated ticker configuration (JSON)
- Provide colorized output for better readability
- Implement robust retry logic for API failures
- Default to validating all CSV tickers with a 1-second delay

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

### Ticker Configuration Generation

The ticker validator can generate a validated configuration file (`tickers_config.json`) that contains only the tickers that successfully passed validation:

```bash
python ticker_validator.py --generate-config
```

This will:
1. Test all tickers (by default from CSV)
2. Create a JSON file containing only the valid tickers
3. Save the file as `tickers_config.json`

Example of generated configuration:
```json
{
    "TICKERS": [
        "ABN.AS",
        "AD.AS",
        "ADYEN.AS",
        "AGN.AS",
        "AKZA.AS",
        "ASM.AS",
        "ASML.AS",
        "ASRNL.AS",
        "BESI.AS"
    ]
}
```

This configuration serves as a quality-controlled list of tickers that are guaranteed to work with the Yahoo Finance API, which can be used as a reference when troubleshooting the ticker sources.

## License

See the LICENSE file for details.
