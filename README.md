# AEX DCF Scanner

A live-updating Discounted Cash Flow (DCF) scanner for AEX (Amsterdam Exchange) stocks that pulls data from Yahoo Finance API, calculates valuations, and ranks stocks by undervaluation.

## Recent Refactoring

The codebase has been refactored to use a single source of truth for ticker symbols:

- **amsterdam_aex_tickers.csv** is now the primary source of ticker data
- **tickers.json** serves as a backup when the CSV is unavailable
- All components now share the same ticker data source
- Special case handling for problematic tickers has been implemented

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

3. Install dependencies in the virtual environment:

   ```bash
   pip install -r requirements.txt
   ```

4. When you're done, you can deactivate the virtual environment:

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

## Fair Value Estimates

The system supports multiple ways to manage fair value estimates, which are stored in the `FAIR_VALUE_ESTIMATES` dictionary in `aex_scanner.py`.

### Fair Value Sources

Fair values can be obtained from:

1. **SimplyWall.st**: Manual entry using the helper script
2. **Analyst Targets**: Automatic update using Yahoo Finance analyst target prices
3. **Custom DCF Analysis**: Manual entry based on your own DCF calculations
4. **Built-in DCF Model**: Automatically calculated DCF valuations using the integrated model

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
  Updates the `FAIR_VALUE_ESTIMATES` dictionary in `aex_scanner.py` with calculated DCF values.

### Updating from SimplyWall.st

You can use the included helper script to easily update fair values from [SimplyWall.st](https://simplywall.st/):

1. Visit SimplyWall.st and look up the fair value for each stock
   - Example: [ASML on SimplyWall.st](https://simplywall.st/stocks/nl/semiconductors/ams-asml/asml-holding-shares/valuation)
   - Look for "Fair Value" displayed in the Valuation section (e.g., "€621.59 per share")
2. Run the helper script:

   ```bash
   ./update_simply_wall_st.py
   ```

   The script will automatically:
   - Load any previously saved values from `simplywall_fair_values.json`
   - Apply all saved values to `aex_scanner.py`
   - Allow you to enter additional values

3. Enter the ticker and fair value when prompted:

   ```bash
   > INGA.AS 43.98
   > ASML.AS 756.22
   > done
   ```

4. To only apply previously saved values (in *simplywall_fair_values.json*) without entering interactive mode:

   ```bash
   ./update_simply_wall_st.py --apply-only
   ```

5. For a guided experience, use the convenient shell script:

   ```bash
   ./update_fair_values.sh
   ```

### Updating from Analyst Target Prices

The system can automatically fetch analyst consensus target prices from Yahoo Finance:

```bash
python fair_value_updater.py
```

This script will:
1. Fetch analyst target prices for all tickers in the centralized ticker list
2. Save the values to `fair_values.json`
3. Update the fair value estimates in `aex_scanner.py`
4. Generate a detailed Excel report showing current prices vs. targets

The `fair_value_updater.py` script uses Yahoo Finance's `targetMeanPrice` data point, which represents the consensus price target from analysts covering each stock. This provides an objective, market-based estimate of fair value that can be used alongside or instead of your own DCF analysis.

The script will update the values in `aex_scanner.py` and keep a record of all updates in `simplywall_fair_values.json`. Each time you run the scanner (via `run_scanner.sh` or `aex_cli.py`), it will automatically apply all saved values to ensure your scanner is using the most recent fair values.

## Ticker Management System

The codebase uses a centralized ticker management system with a clear source hierarchy:

1. `amsterdam_aex_tickers.csv` - Primary source of truth for all ticker symbols
2. `tickers.json` - Backup source used only when the CSV file is unavailable

### Adding More Stocks

To add more stocks to the scanner:

1. Add the ticker symbol to the `amsterdam_aex_tickers.csv` file
2. Add a corresponding fair value estimate to the `FAIR_VALUE_ESTIMATES` dictionary in aex_scanner.py
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

# Investigate problematic tickers
python aex_tickers.py --investigate
```

The system provides detailed diagnostics about where ticker symbols are being loaded from and ensures consistent ticker data by using Euronext as the authoritative source.

## Output

The scanner generates an Excel file in the `outputs/` directory with the following metrics:

- **Ticker**: Stock ticker symbol (Amsterdam Exchange)
- **Company**: Company name
- **Current Price**: Current stock price in Euros
- **Fair Value**: Estimated fair value per share based on DCF analysis
- **Market Cap (M)**: Current market capitalization in millions
- **Fair Market Cap (M)**: Fair market capitalization based on fair value in millions
- **Discount Margin (M)**: Difference between fair and current market cap in millions
- **Discount %**: How undervalued/overvalued the stock is

Stocks are ranked by discount percentage (undervaluation) in descending order. The output file name contains a timestamp to keep track of when each scan was performed (e.g., `aex_stock_valuation_20250516_111000.xlsx`).

### Excel Features

- **Header Descriptions**: Each column has a description explaining the data
- **Conditional Formatting**:
  - Undervalued stocks (≥10% discount) are highlighted in green
  - Overvalued stocks (≥10% premium) are highlighted in red
- **Formatted Numbers**: All values are properly formatted with currency and percentage indicators

### Visualization Features

The scanner includes a visualization tool that generates the following charts in the `visualizations/` directory:

- **Discount Percentage Bar Chart**: Shows which stocks are most undervalued/overvalued
- **Current Price vs Fair Value**: Side-by-side comparison of current stock prices and fair values
- **Market Cap Comparison**: Visual comparison of current versus fair market capitalization
- **Discount Margin Waterfall**: Shows the absolute discount/premium in millions of euros

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

- **aex_scanner.py**: Main scanner logic and fair value calculations
- **aex_tickers.py**: Central ticker management module
- **amsterdam_aex_tickers.csv**: Primary source of ticker data
- **tickers.json**: Backup source of ticker data
- **fair_value_updater.py**: Updates fair values from Yahoo Finance analyst targets
- **euronext_tickers.py**: Updates ticker data from Euronext
- **investigate_problematic_tickers.py**: Diagnostic tool for ticker issues

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

### Investigating Problematic Tickers

For a deeper analysis of ticker issues, use the investigation tool:

```bash
# Run the ticker investigation tool
python aex_tickers.py --investigate
```

The investigation tool will:

- Load tickers from the primary CSV source
- Test each ticker against the Yahoo Finance API
- Identify problematic tickers and provide diagnostics
- Check data availability and completeness for each ticker
- Provide detailed information about ticker validity

This helps ensure that all tickers from Euronext are properly formatted and compatible with Yahoo Finance's data API.

## License

See the LICENSE file for details.
