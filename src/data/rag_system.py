import chromadb
from chromadb.utils import embedding_functions
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class CreditRAGSystem:
    """RAG system for SEC 10-K filings"""
    
    def __init__(self, persist_directory="data/chroma_db"):
        """Initialize ChromaDB with FREE local embeddings"""
        self.persist_directory = persist_directory
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Create ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Use FREE local sentence-transformers embeddings
        # This runs on your laptop, no API costs
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"  # Fast, good quality, free
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="credit_documents",
            embedding_function=self.embedding_function
        )
    
    def chunk_document(self, text: str, chunk_size: int = 1000, overlap: int = 200):
        """Split document into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > chunk_size * 0.5:
                    end = start + last_period + 1
                    chunk = text[start:end]
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def add_document(self, ticker: str, document_text: str, doc_type: str = "10-K"):
        """Add a 10-K document to the vector store"""
        
        print(f"\nAdding {ticker} {doc_type} to RAG system...")
        
        # Chunk the document
        chunks = self.chunk_document(document_text)
        print(f"  Created {len(chunks)} chunks")
        
        # Add in batches to avoid ChromaDB limit
        batch_size = 5000
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            
            # Create unique IDs and metadata for this batch
            ids = [f"{ticker}_{doc_type}_{j}" for j in range(i, i + len(batch_chunks))]
            metadatas = [
                {
                    "ticker": ticker,
                    "doc_type": doc_type,
                    "chunk_id": j,
                    "total_chunks": len(chunks)
                }
                for j in range(i, i + len(batch_chunks))
            ]
            
            # Add batch to ChromaDB
            self.collection.add(
                documents=batch_chunks,
                metadatas=metadatas,
                ids=ids
            )
            print(f"  Added batch {i//batch_size + 1} ({len(batch_chunks)} chunks)")
        
        print(f"  ✓ Added {ticker} to vector database")
    
    def retrieve(self, query: str, ticker: str = None, n_results: int = 5):
        """Retrieve relevant chunks for a query"""
        
        where_filter = {"ticker": ticker} if ticker else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        return {
            "documents": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "distances": results["distances"][0]
        }
    
    def get_risk_factors(self, ticker: str, n_results: int = 3):
        """Retrieve risk factor sections"""
        query = "risk factors business risks financial risks market risks operational risks"
        return self.retrieve(query, ticker, n_results)
    
    def get_financial_performance(self, ticker: str, n_results: int = 3):
        """Retrieve financial performance discussions"""
        query = "revenue earnings profit loss performance results operations financial condition"
        return self.retrieve(query, ticker, n_results)
    
    def get_debt_discussion(self, ticker: str, n_results: int = 3):
        """Retrieve debt and capital structure sections"""
        query = "debt obligations borrowings liquidity capital structure financing"
        return self.retrieve(query, ticker, n_results)

def build_rag_database(tickers: list):
    """Build RAG database for multiple companies"""
    
    rag = CreditRAGSystem()
    
    for ticker in tickers:
        # Find the 10-K file using your structure: data/raw/sec-edgar-filings/TICKER/10-K/
        filepath = None
        search_path = f"data/raw/sec-edgar-filings/{ticker}/10-K"
        
        # Also check root level sec-edgar-filings
        if not os.path.exists(search_path):
            search_path = f"sec-edgar-filings/{ticker}/10-K"
        
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file == 'full-submission.txt':
                    filepath = os.path.join(root, file)
                    break
            if filepath:
                break
        
        if not filepath:
            print(f"No 10-K found for {ticker} in {search_path}")
            continue
        
        # Read document
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        # Add to RAG system
        rag.add_document(ticker, text)
    
    print("\n✓ RAG database built successfully")
    return rag

if __name__ == "__main__":
    # Build database for companies
    tickers = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'JPM', 'JNJ']
    rag = build_rag_database(tickers)
    
    # Test retrieval
    print("\n" + "="*70)
    print("TESTING RAG RETRIEVAL")
    print("="*70)
    
    results = rag.get_risk_factors("AAPL", n_results=2)
    
    print("\nTop 2 risk factor chunks for AAPL:")
    for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
        print(f"\nChunk {i+1}:")
        print(f"  {doc[:200]}...")
