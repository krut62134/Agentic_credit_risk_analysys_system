from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.rag_system import CreditRAGSystem

class PeerComparisonAgent:
    """Peer comparison using Groq + LangChain"""
    
    def __init__(self, model="llama-3.3-70b-versatile"):
        """Initialize with LangChain"""
        self.llm = ChatGroq(
            temperature=0.1,
            model_name=model,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        print("Loading RAG system...")
        self.rag = CreditRAGSystem()
        
        # Comparison prompt
        self.comparison_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a credit analyst specializing in peer comparisons."),
            ("user", "{prompt}")
        ])
        
        # Create chain
        self.comparison_chain = self.comparison_prompt | self.llm | StrOutputParser()
        
        print("Peer Comparison Agent (LangChain + Groq) loaded\n")
    
    def compare_companies(self, tickers: list):
        """Compare multiple companies"""
        
        print(f"\n{'='*70}")
        print("PEER COMPARISON ANALYSIS")
        print(f"Companies: {', '.join(tickers)}")
        print(f"{'='*70}\n")
        
        # Collect data
        company_data = {}
        
        for ticker in tickers:
            print(f"Gathering data for {ticker}...")
            
            debt_results = self.rag.get_debt_discussion(ticker, n_results=2)
            financial_results = self.rag.get_financial_performance(ticker, n_results=2)
            risk_results = self.rag.get_risk_factors(ticker, n_results=2)
            
            company_data[ticker] = {
                "debt": "\n".join(debt_results["documents"][:1]),
                "financial": "\n".join(financial_results["documents"][:1]),
                "risk": "\n".join(risk_results["documents"][:1])
            }
        
        print("\nGenerating comparative analysis...\n")
        
        # Build comparison text
        comparison_text = ""
        for ticker, data in company_data.items():
            comparison_text += f"\n{'='*50}\n{ticker}:\n{'='*50}\n"
            comparison_text += f"DEBT: {data['debt'][:800]}\n\n"
            comparison_text += f"FINANCIALS: {data['financial'][:800]}\n\n"
            comparison_text += f"RISKS: {data['risk'][:800]}\n\n"
        
        prompt_content = f"""Compare these companies based on SEC 10-K filings:

{comparison_text}

Provide structured comparison:

1. CREDIT STRENGTH RANKING (strongest to weakest with brief justification)

2. KEY DIFFERENTIATORS (what makes each unique)

3. COMPARATIVE RISK ASSESSMENT
   - Highest debt burden?
   - Best liquidity?
   - Most significant risks?

4. INVESTMENT RECOMMENDATION (which ONE from credit safety perspective)

Keep under 500 words."""

        # Use LangChain chain
        analysis = self.comparison_chain.invoke({"prompt": prompt_content})
        
        print(f"{'='*70}")
        print("PEER COMPARISON REPORT")
        print(f"{'='*70}\n")
        print(analysis)
        print(f"\n{'='*70}")
        
        return {
            "tickers": tickers,
            "analysis": analysis,
            "company_data": company_data
        }


def main():
    """Main execution"""
    
    if len(sys.argv) > 1:
        tickers = [t.upper() for t in sys.argv[1:]]
    else:
        ticker_input = input("Enter tickers (e.g., AAPL MSFT TSLA): ")
        tickers = [t.upper() for t in ticker_input.split()]
    
    if len(tickers) < 2:
        print("Need at least 2 companies")
        return
    
    agent = PeerComparisonAgent()
    result = agent.compare_companies(tickers)
    
    save = input("\nSave comparison? (y/n): ").lower()
    if save == 'y':
        import json
        output_file = f"outputs/peer_comparison_{'_'.join(tickers)}.json"
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
