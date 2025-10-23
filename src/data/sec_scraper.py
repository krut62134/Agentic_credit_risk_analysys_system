from sec_edgar_downloader import Downloader
import os

# Download 10-K filings
dl = Downloader("MyCompany", "email@example.com", download_folder="./../../data/raw")

# Download for multiple companies
tickers = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "JPM", "JNJ"]

for ticker in tickers:
    print(f"Downloading {ticker}...")
    dl.get("10-K", ticker, limit=1, download_details=True)
    print(f"✓ Downloaded {ticker} 10-K")

print("\n✓ All downloads complete")
