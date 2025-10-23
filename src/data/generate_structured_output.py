import json
import csv
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agent.rag_credit_agent import RAGCreditAgent
from src.data.lakehouse import CreditLakehouse

'''
def analyze_and_structure(ticker: str) -> dict:
    """Run analysis and structure for lakehouse"""
    
    print(f"\nAnalyzing {ticker}...")
    
    # Run credit analysis (now uses Groq + LangChain)
    agent = RAGCreditAgent()
    result = agent.analyze_company(ticker, use_tools=True, use_news=True)
    
    # Extract structured data from new format
    structured = {
        "analysis_date": result['metadata']['analysis_date'].split()[0],  # Just date
        "ticker": result['metadata']['ticker'],
        "credit_rating": result['credit_assessment']['rating'],
        "stock_price": result['market_data'].get('stock_price', 'N/A'),
        "market_cap": result['market_data'].get('market_cap', 0),
        "total_debt": result['market_data'].get('total_debt', 0),
        "total_cash": result['market_data'].get('total_cash', 0),
        "debt_to_equity": result['market_data'].get('debt_to_equity', 0),
        "return_on_equity": result['market_data'].get('return_on_equity', 0),
        "free_cash_flow": result['market_data'].get('free_cash_flow', 0),
        "analysis_summary": result['credit_assessment']['analysis'][:500].replace('\n', ' ')
    }
    
    return structured
'''

def analyze_and_structure(ticker: str) -> dict:
    """Run analysis and structure for lakehouse"""
    
    print(f"\nAnalyzing {ticker}...")
    
    # Run credit analysis (now uses Groq + LangChain)
    agent = RAGCreditAgent()
    result = agent.analyze_company(ticker, use_tools=True, use_news=True)
    
    # Helper function to convert to number or 0
    def to_number(value, default=None):  # Changed default to None
        if value == 'N/A' or value is None or value == '':
            return default
        try:
            return float(value)
        except:
            return default

    # Then in structured dict:
    structured = {
        "analysis_date": result['metadata']['analysis_date'].split()[0],
        "ticker": result['metadata']['ticker'],
        "credit_rating": result['credit_assessment']['rating'],
        "stock_price": to_number(result['market_data'].get('stock_price')),
        "market_cap": to_number(result['market_data'].get('market_cap')),
        "total_debt": to_number(result['market_data'].get('total_debt')),
        "total_cash": to_number(result['market_data'].get('total_cash')),
        "debt_to_equity": to_number(result['market_data'].get('debt_to_equity')),
        "return_on_equity": to_number(result['market_data'].get('return_on_equity')),
        "free_cash_flow": to_number(result['market_data'].get('free_cash_flow')),
        "analysis_summary": result['credit_assessment']['analysis'][:500].replace('\n', ' ')
    }
    return structured


def process_companies(tickers: list, write_to_lakehouse=True, write_to_csv=True):
    """Process companies with Groq + LangChain pipeline"""
    
    lakehouse = CreditLakehouse() if write_to_lakehouse else None
    
    if write_to_csv:
        Path("data/processed").mkdir(parents=True, exist_ok=True)
    
    all_data = []
    
    for ticker in tickers:
        try:
            data = analyze_and_structure(ticker)
            all_data.append(data)
            
            # Write to lakehouse
            if lakehouse:
                lakehouse.write_analysis(data)
                print(f"✓ Written {ticker} to lakehouse")
            
            print(f"✓ Completed {ticker}")
            
        except Exception as e:
            print(f"✗ Failed {ticker}: {str(e)}")
    
    # Write CSV backup
    if write_to_csv and all_data:
        csv_file = "data/processed/credit_analysis.csv"
        fieldnames = all_data[0].keys()
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_data)
        
        print(f"\n✓ CSV backup: {csv_file}")
    
    print(f"\n{'='*70}")
    print("✓ PIPELINE COMPLETE (Groq + LangChain)")
    print(f"  Processed: {len(all_data)} companies")
    if lakehouse:
        print(f"  Lakehouse: data/lakehouse/credit_analysis")
    print(f"{'='*70}")
    
    return all_data

if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "JPM", "JNJ"]
    
    print("="*70)
    print("AUTOMATED CREDIT ANALYSIS PIPELINE")
    print("RAG → Groq AI → Lakehouse")
    print("="*70)
    
    process_companies(tickers, write_to_lakehouse=True, write_to_csv=True)
