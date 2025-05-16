# AEX DCF Scanner

A live-updating Discounted Cash Flow (DCF) scanner for AEX (Amsterdam Exchange) stocks that pulls data from Yahoo Finance API, calculates valuations, and ranks stocks by undervaluation.

## Features

- Pulls real-time stock data from Yahoo Finance API
- Uses stored fair value estimates per stock
- Calculates key metrics:
  - Market Cap
  - Fair Market Cap
  - Discount Margin
  - Discount %
- Auto-ranks stocks by undervaluation
- Saves results to Excel with formatted output

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

Fair value estimates are stored in the `FAIR_VALUE_ESTIMATES` dictionary in `aex_scanner.py`. You can update these values based on your own DCF analysis or other valuation methods.

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

The script will update the values in `aex_scanner.py` and keep a record of all updates in `simplywall_fair_values.json`. Each time you run the scanner (via `run_scanner.sh` or `aex_cli.py`), it will automatically apply all saved values to ensure your scanner is using the most recent fair values.

## Adding More Stocks

To add more stocks to the scanner:

1. Add the ticker symbol to the `AEX_TICKERS` list
2. Add a corresponding fair value estimate to the `FAIR_VALUE_ESTIMATES` dictionary

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
  - Files are named with timestamps, e.g. `aex_stock_valuation_20250516_111000.xlsx`
  
- **visualizations/**: Contains all generated charts and visualizations
  - Charts are organized by type and include timestamps
  
- **backups/**: Contains backup files created when updating fair values
  - Backups are created automatically before making changes

This organization keeps your workspace clean and makes it easier to find specific files.

## Troubleshooting & Data Validation

### Handling Data Issues

The scanner now includes robust error handling for common issues:

- **Rate Limiting**: Implements exponential backoff with jitter to handle API rate limits
- **Connection Issues**: Automatically retries failed connections
- **Data Validation**: Validates data completeness before processing
- **Error Reporting**: Provides detailed logs of data quality issues

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

## License

See the LICENSE file for details.
