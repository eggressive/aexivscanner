import time
import json
import os
import pandas as pd
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup headless Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

# Open Euronext AEX composition page
url = "https://live.euronext.com/en/popout-page/getIndexComposition/NL0000000107-XAMS"
driver.get(url)

# Wait until the table element is present
try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )
except Exception as e:
    print("Error waiting for table to load:", e)
    driver.quit()
    exit(1)

# Get page source after JS rendering
html = driver.page_source

# Close the browser
driver.quit()

# Use pandas to parse HTML tables
tables = pd.read_html(StringIO(html))
df = tables[0]

# Clean up column names
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Generate correct Euronext component links using ISINs
df['component_link'] = df['isin'].apply(lambda isin: f"https://live.euronext.com/en/product/equities/{isin}-XAMS")

# Setup browser again for scraping symbols from the /ipo page using JSON inside script tag
driver = webdriver.Chrome(options=options)
tickers = []

for isin in df['isin']:
    try:
        ipo_url = f"https://live.euronext.com/en/product/equities/{isin}-XAMS/ipo"
        driver.get(ipo_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "script[data-drupal-selector='drupal-settings-json']"))
        )
        script_tag = driver.find_element(By.CSS_SELECTOR, "script[data-drupal-selector='drupal-settings-json']")
        json_data = json.loads(script_tag.get_attribute("innerHTML"))
        symbol = json_data.get("custom", {}).get("instrument", {}).get("symbol", None)
        tickers.append(symbol)
    except Exception as e:
        print(f"Error fetching symbol for {isin}: {e}")
        tickers.append(None)

driver.quit()

# Add ticker symbols to DataFrame
df['euronext_ticker'] = tickers

# Map to Yahoo Finance ticker format (append .AS)
df['yahoo_ticker'] = df['euronext_ticker'].apply(lambda x: f"{x}.AS" if pd.notna(x) else None)

# Print cleaned output
print(df[['component', 'isin', 'euronext_ticker', 'yahoo_ticker']])

# Save to CSV as the primary source of truth
csv_path = os.path.join(os.path.dirname(__file__), "amsterdam_aex_tickers.csv")
df[['component', 'isin', 'euronext_ticker', 'yahoo_ticker']].to_csv(csv_path, index=False)
print(f"✅ Saved {len(df)} tickers to {csv_path}")

# Update tickers.json backup file via the aex_tickers module
try:
    from aex_tickers import load_tickers, update_json_from_csv
    tickers = list(df['yahoo_ticker'].dropna().values)
    json_path = os.path.join(os.path.dirname(__file__), "tickers.json")
    if update_json_from_csv(tickers, json_path):
        print(f"✅ Updated backup in {json_path} with {len(tickers)} tickers")
    else:
        print(f"❌ Failed to update JSON backup")
except Exception as e:
    print(f"❌ Error updating JSON backup: {str(e)}")
    
print("\nSuggestion: Run 'aex_scanner.py' to test the tickers with the latest data")
