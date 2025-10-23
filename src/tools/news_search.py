from tavily import TavilyClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class NewsSearchTool:
    """Search recent news using Tavily API"""
    
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in .env")
        self.client = TavilyClient(api_key=api_key)
    
    def search_company_news(self, ticker: str, max_results: int = 5) -> dict:
        """Search recent news about a company"""
        
        query = f"{ticker} stock financial news credit risk debt earnings"
        
        try:
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=max_results,
                days=30  # Last 30 days
            )
            
            results = []
            for result in response.get('results', []):
                results.append({
                    "title": result.get('title'),
                    "url": result.get('url'),
                    "content": result.get('content'),
                    "published_date": result.get('published_date', 'Unknown'),
                    "score": result.get('score', 0)
                })
            
            return {
                "ticker": ticker,
                "query": query,
                "news_count": len(results),
                "results": results,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return {
                "error": f"News search failed: {str(e)}",
                "ticker": ticker
            }
    
    def get_news_summary(self, ticker: str) -> str:
        """Get a text summary of recent news"""
        
        news = self.search_company_news(ticker, max_results=3)
        
        if "error" in news:
            return f"Failed to fetch news for {ticker}"
        
        summary = f"Recent news for {ticker} (last 30 days):\n\n"
        
        for i, article in enumerate(news['results'], 1):
            summary += f"{i}. {article['title']}\n"
            summary += f"   {article['content'][:200]}...\n"
            summary += f"   Source: {article['url']}\n\n"
        
        return summary


if __name__ == "__main__":
    # Test the tool
    news_tool = NewsSearchTool()
    
    ticker = "AAPL"
    print(f"Searching news for {ticker}...\n")
    
    results = news_tool.search_company_news(ticker, max_results=3)
    
    if "error" in results:
        print(results["error"])
    else:
        print(f"Found {results['news_count']} articles\n")
        
        for i, article in enumerate(results['results'], 1):
            print(f"{i}. {article['title']}")
            print(f"   {article['content'][:150]}...")
            print(f"   URL: {article['url']}\n")
