# AEX DCF Scanner

A live-updating Discounted Cash Flow (DCF) scanner for AEX (Amsterdam Exchange) stocks that pulls data from Yahoo Finance API, calculates valuations, and ranks stocks by undervaluation.

## Features

- 📥 Pulls real-time stock data from Yahoo Finance API
- 🧠 Uses stored fair value estimates per stock
- 🔍 Calculates key metrics:
  - Market Cap
  - Fair Market Cap
  - Discount Margin
  - Discount %
- 📊 Auto-ranks stocks by undervaluation
- 💾 Saves results to Excel with formatted output

## Installation

1. Clone this repository
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the scanner:

```bash
python aex_scanner.py
```

The script will:

1. Fetch current price data for all AEX stocks
2. Calculate valuation metrics based on provided fair value estimates
3. Rank stocks by discount percentage (undervaluation)
4. Save results to an Excel file with timestamp

## Fair Value Estimates

Fair value estimates are stored in the `FAIR_VALUE_ESTIMATES` dictionary in `aex_scanner.py`. You can update these values based on your own DCF analysis or other valuation methods.

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
