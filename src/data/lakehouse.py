from deltalake import write_deltalake, DeltaTable
import pandas as pd
from pathlib import Path
from datetime import datetime

class CreditLakehouse:
    """Local Delta Lake lakehouse - Fabric replacement"""
    
    def __init__(self, lakehouse_path="data/lakehouse/credit_analysis"):
        """Initialize lakehouse"""
        self.lakehouse_path = lakehouse_path
        Path(lakehouse_path).mkdir(parents=True, exist_ok=True)
    
    def write_analysis(self, data: dict, mode="append"):
        """Write credit analysis to lakehouse (replaces Fabric API)"""
        
        # Convert to DataFrame
        df = pd.DataFrame([data])
        
        # Add metadata
        df['ingestion_timestamp'] = datetime.now()
        df['lakehouse_version'] = 1
        
        # Write to Delta Lake
        write_deltalake(
            self.lakehouse_path,
            df,
            mode=mode,
            schema_mode="merge"  # Auto-merge schema changes
        )
        
        print(f"✓ Written to lakehouse: {self.lakehouse_path}")
    
    def read_all(self) -> pd.DataFrame:
        """Read all data from lakehouse"""
        dt = DeltaTable(self.lakehouse_path)
        return dt.to_pandas()
    
    def query(self, sql: str) -> pd.DataFrame:
        """Query lakehouse with SQL using DuckDB"""
        import duckdb
        
        # Load delta table
        df = self.read_all()
        
        # Query with DuckDB
        result = duckdb.query(sql).df()
        return result
    
    def get_company_analysis(self, ticker: str) -> pd.DataFrame:
        """Get analysis for specific company"""
        df = self.read_all()
        return df[df['ticker'] == ticker]
    
    def get_latest_analyses(self, n: int = 10) -> pd.DataFrame:
        """Get N most recent analyses"""
        df = self.read_all()
        return df.sort_values('analysis_date', ascending=False).head(n)


if __name__ == "__main__":
    # Test lakehouse
    lakehouse = CreditLakehouse()
    
    # Sample data
    test_data = {
        "ticker": "AAPL",
        "analysis_date": "2025-10-23",
        "credit_rating": "AA",
        "debt_to_equity": 154.5,
        "market_cap": 3835498856448,
        "analysis_summary": "Strong creditworthiness with manageable debt levels"
    }
    
    lakehouse.write_analysis(test_data)
    print("\nReading from lakehouse:")
    print(lakehouse.read_all())
