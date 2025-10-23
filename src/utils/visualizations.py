import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.lakehouse import CreditLakehouse

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

class CreditVisualizer:
    """Generate visualizations from lakehouse data"""
    
    def __init__(self):
        """Load data from lakehouse"""
        self.lakehouse = CreditLakehouse()
        self.df = self.lakehouse.read_all()
        
        if self.df.empty:
            raise ValueError("No data in lakehouse. Run pipeline first.")
        
        # Create output directory
        Path("outputs/charts").mkdir(parents=True, exist_ok=True)
    
    def plot_debt_to_equity(self):
        """Horizontal bar chart of debt-to-equity ratios"""
        plt.figure(figsize=(10, 6))
        
        # Filter out zeros (missing data)
        df_filtered = self.df[self.df['debt_to_equity'] > 0]
        df_sorted = df_filtered.sort_values('debt_to_equity', ascending=True)
        
        colors = ['red' if x > 100 else 'orange' if x > 50 else 'green' 
                  for x in df_sorted['debt_to_equity']]
        
        plt.barh(df_sorted['ticker'], df_sorted['debt_to_equity'], color=colors, alpha=0.7)
        plt.title('Debt-to-Equity Ratios by Company', fontsize=16, fontweight='bold')
        plt.xlabel('Debt-to-Equity Ratio (%)', fontsize=12)
        plt.ylabel('Company', fontsize=12)
        plt.axvline(x=50, color='orange', linestyle='--', alpha=0.5, label='Moderate Risk (50)')
        plt.axvline(x=100, color='red', linestyle='--', alpha=0.5, label='High Risk (100)')
        plt.legend()
        plt.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('outputs/charts/debt_to_equity.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: outputs/charts/debt_to_equity.png")
        plt.close()
    
    def plot_return_on_equity(self):
        """Bar chart of return on equity"""
        plt.figure(figsize=(10, 6))
        
        # Filter out zeros
        df_filtered = self.df[self.df['return_on_equity'] > 0]
        df_sorted = df_filtered.sort_values('return_on_equity', ascending=False)
        
        roe_pct = df_sorted['return_on_equity'] * 100
        colors = ['green' if x > 15 else 'orange' if x > 10 else 'red' for x in roe_pct]
        
        plt.bar(df_sorted['ticker'], roe_pct, color=colors, alpha=0.7)
        plt.title('Return on Equity by Company', fontsize=16, fontweight='bold')
        plt.xlabel('Company', fontsize=12)
        plt.ylabel('ROE (%)', fontsize=12)
        plt.axhline(y=15, color='green', linestyle='--', alpha=0.5, label='Strong (>15%)')
        plt.axhline(y=10, color='orange', linestyle='--', alpha=0.5, label='Adequate (>10%)')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('outputs/charts/return_on_equity.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: outputs/charts/return_on_equity.png")
        plt.close()
    
    def plot_debt_vs_cash(self):
        """Scatter plot: total debt vs total cash"""
        plt.figure(figsize=(10, 8))
        
        # Filter out zeros
        df_filtered = self.df[(self.df['total_debt'] > 0) & (self.df['total_cash'] > 0)]
        
        # Convert to billions
        debt_b = df_filtered['total_debt'] / 1e9
        cash_b = df_filtered['total_cash'] / 1e9
        
        plt.scatter(cash_b, debt_b, s=300, alpha=0.6, c=range(len(df_filtered)), cmap='viridis')
        
        # Add company labels
        for i, (idx, row) in enumerate(df_filtered.iterrows()):
            plt.annotate(row['ticker'], (cash_b.iloc[i], debt_b.iloc[i]), 
                        fontsize=12, fontweight='bold', ha='center')
        
        plt.title('Debt vs Cash Position', fontsize=16, fontweight='bold')
        plt.xlabel('Total Cash (Billions USD)', fontsize=12)
        plt.ylabel('Total Debt (Billions USD)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Add diagonal line (debt = cash)
        max_val = max(debt_b.max(), cash_b.max())
        plt.plot([0, max_val], [0, max_val], 'r--', alpha=0.5, label='Debt = Cash')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('outputs/charts/debt_vs_cash.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: outputs/charts/debt_vs_cash.png")
        plt.close()
    
    def generate_all(self):
        """Generate all visualizations"""
        print("\n" + "="*70)
        print("GENERATING VISUALIZATIONS")
        print("="*70 + "\n")
        
        self.plot_debt_to_equity()
        self.plot_return_on_equity()
        self.plot_debt_vs_cash()
        
        print("\n" + "="*70)
        print("✓ 3 CHARTS GENERATED")
        print("  Location: outputs/charts/")
        print("="*70)


if __name__ == "__main__":
    try:
        visualizer = CreditVisualizer()
        visualizer.generate_all()
    except ValueError as e:
        print(f"Error: {e}")
