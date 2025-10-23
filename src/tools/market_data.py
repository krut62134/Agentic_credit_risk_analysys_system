import yfinance as yf
from datetime import datetime

def get_stock_price(ticker: str) -> dict:
    """Get current stock price and basic info"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            "ticker": ticker,
            "current_price": info.get('currentPrice', 'N/A'),
            "market_cap": info.get('marketCap', 'N/A'),
            "52_week_high": info.get('fiftyTwoWeekHigh', 'N/A'),
            "52_week_low": info.get('fiftyTwoWeekLow', 'N/A'),
            "pe_ratio": info.get('trailingPE', 'N/A'),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {"error": f"Failed to fetch data for {ticker}: {str(e)}"}


def get_company_fundamentals(ticker: str) -> dict:
    """Get key financial fundamentals"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            "ticker": ticker,
            "revenue": info.get('totalRevenue', 'N/A'),
            "total_debt": info.get('totalDebt', 'N/A'),
            "total_cash": info.get('totalCash', 'N/A'),
            "ebitda": info.get('ebitda', 'N/A'),
            "free_cash_flow": info.get('freeCashflow', 'N/A'),
            "return_on_equity": info.get('returnOnEquity', 'N/A'),
            "debt_to_equity": info.get('debtToEquity', 'N/A')
        }
    except Exception as e:
        return {"error": f"Failed to fetch fundamentals for {ticker}: {str(e)}"}


def compare_market_caps(tickers: list) -> dict:
    """Compare market capitalizations"""
    results = {}
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            results[ticker] = info.get('marketCap', 0)
        except:
            results[ticker] = 0
    
    # Sort by market cap
    sorted_results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True))
    
    return {
        "market_caps": sorted_results,
        "largest": max(sorted_results, key=sorted_results.get),
        "smallest": min(sorted_results, key=sorted_results.get)
    }


if __name__ == "__main__":
    # Test the tools
    print("Testing Market Data Tools\n")
    
    ticker = "AAPL"
    
    print(f"Stock Price for {ticker}:")
    print(get_stock_price(ticker))
    print()
    
    print(f"Fundamentals for {ticker}:")
    print(get_company_fundamentals(ticker))
    print()
    
    print("Comparing market caps:")
    print(compare_market_caps(["AAPL", "MSFT", "TSLA"]))
