from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sys
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.rag_system import CreditRAGSystem
from src.tools.financial_calculator import calculate_debt_to_equity, assess_credit_rating
from src.tools.market_data import get_company_fundamentals, get_stock_price
from src.tools.news_search import NewsSearchTool

class RAGCreditAgent:
    """Credit Analyst Agent using RAG + Groq + LangChain"""
    
    def __init__(self, model="llama-3.3-70b-versatile"):  # Updated model
        """Initialize agent with RAG system and LLM"""
        self.llm = ChatGroq(
            temperature=0.1,
            model_name=model,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        print("Loading RAG system...")
        self.rag = CreditRAGSystem()
        print("Loading news search tool...")
        self.news_tool = NewsSearchTool()
        print("Agent initialized with Groq + LangChain\n")
        
        # Define analysis prompt template
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a senior credit analyst at Moody's. Provide clear, structured credit analysis."),
            ("user", "{prompt}")
        ])
        
        # Create chain
        self.analysis_chain = self.analysis_prompt | self.llm | StrOutputParser()
    
    def analyze_company(self, ticker: str, use_tools=True, use_news=True) -> dict:
        """Perform comprehensive credit analysis with structured output"""
        
        print(f"\n{'='*70}")
        print(f"CREDIT ANALYSIS REPORT: {ticker}")
        print(f"{'='*70}\n")
        
        # Step 1: Get real-time market data
        market_data = {}
        if use_tools:
            print("Step 1/6: Fetching real-time market data...")
            stock_data = get_stock_price(ticker)
            fundamentals = get_company_fundamentals(ticker)
            
            market_data = {
                "stock_price": stock_data.get('current_price', 'N/A'),
                "market_cap": fundamentals.get('market_cap', 0),
                "total_debt": fundamentals.get('total_debt', 0),
                "total_cash": fundamentals.get('total_cash', 0),
                "debt_to_equity": fundamentals.get('debt_to_equity', 0),
                "return_on_equity": fundamentals.get('return_on_equity', 0),
                "free_cash_flow": fundamentals.get('free_cash_flow', 0)
            }
            
            print(f"  Current Price: ${market_data['stock_price']}")
            print(f"  Debt-to-Equity: {market_data['debt_to_equity']}")
        
        # Step 2: Get recent news
        news_summary = ""
        if use_news:
            print("Step 2/6: Searching recent news...")
            news_summary = self.news_tool.get_news_summary(ticker)
            print("  Found recent articles")
        
        # Step 3-5: Retrieve from RAG
        print("Step 3/6: Analyzing risk factors...")
        risk_results = self.rag.get_risk_factors(ticker, n_results=3)
        risk_context = "\n\n".join(risk_results["documents"])
        
        print("Step 4/6: Analyzing financial performance...")
        financial_results = self.rag.get_financial_performance(ticker, n_results=3)
        financial_context = "\n\n".join(financial_results["documents"])
        
        print("Step 5/6: Analyzing debt and liquidity...")
        debt_results = self.rag.get_debt_discussion(ticker, n_results=3)
        debt_context = "\n\n".join(debt_results["documents"])
        
        # Step 6: Generate analysis with LangChain
        print("Step 6/6: Generating credit report with Groq AI...\n")
        
        prompt_content = f"""Analyze the creditworthiness of {ticker}.

MARKET DATA:
- Stock Price: ${market_data.get('stock_price', 'N/A')}
- Market Cap: ${market_data.get('market_cap', 'N/A')}
- Total Debt: ${market_data.get('total_debt', 'N/A')}
- Debt-to-Equity: {market_data.get('debt_to_equity', 'N/A')}

RECENT NEWS:
{news_summary[:1000]}

RISK FACTORS (from 10-K):
{risk_context[:1500]}

FINANCIAL PERFORMANCE (from 10-K):
{financial_context[:1500]}

DEBT & LIQUIDITY (from 10-K):
{debt_context[:1500]}

Provide structured analysis:

1. CREDIT STRENGTHS (3-4 points)
2. CREDIT CONCERNS (3-4 points)
3. OVERALL ASSESSMENT
   - Credit rating: AAA, AA, A, BBB, BB, B, or CCC
   - Brief justification (2-3 sentences)

Keep under 400 words."""

        # Use LangChain chain
        analysis_text = self.analysis_chain.invoke({"prompt": prompt_content})
        
        # Extract rating from analysis
        rating = self._extract_rating(analysis_text)
        
        # Display results
        print(f"{'='*70}")
        print(f"GROQ AI CREDIT ANALYSIS: {ticker}")
        print(f"{'='*70}\n")
        print(analysis_text)
        print(f"\n{'='*70}")
        
        # Structured output
        structured_output = {
            "metadata": {
                "ticker": ticker,
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "model": "groq-llama-3.2-90b",
                "framework": "langchain"
            },
            "market_data": market_data,
            "credit_assessment": {
                "rating": rating,
                "analysis": analysis_text
            },
            "data_sources": {
                "sec_10k": True,
                "market_data": use_tools,
                "news": use_news
            }
        }
        
        return structured_output
    
    def _extract_rating(self, text: str) -> str:
        """Extract credit rating from analysis text"""
        ratings = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]
        for rating in ratings:
            if rating in text:
                return rating
        return "Not Rated"


def main():
    """Main execution"""
    
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
    else:
        ticker = input("Enter company ticker (AAPL, MSFT, TSLA, GOOGL, AMZN, JPM, JNJ): ").upper()
    
    agent = RAGCreditAgent()
    result = agent.analyze_company(ticker, use_tools=True, use_news=True)
    
    # Save structured output
    save = input("\nSave report to file? (y/n): ").lower()
    if save == 'y':
        import json
        output_file = f"outputs/{ticker}_credit_report.json"
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
