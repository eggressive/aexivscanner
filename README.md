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

The scanner generates an Excel file with the following metrics:

- Company name
- Current Price
- Fair Value
- Market Cap (in millions)
- Fair Market Cap (in millions)
- Discount Margin (in millions)
- Discount Percentage

Stocks are ranked by discount percentage (undervaluation) in descending order.

## License

See the LICENSE file for details.
