import chromadb
from chromadb.utils import embedding_functions
import os
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor
import numpy as np

load_dotenv()


# ---------------------------------------------------------------------
# Parallel embedding worker
# ---------------------------------------------------------------------
def embed_worker(chunks_subset):
    """Worker process: embeds a subset of chunks"""
    from chromadb.utils import embedding_functions
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    return embedding_fn(chunks_subset)


# ---------------------------------------------------------------------
# Main Credit RAG system
# ---------------------------------------------------------------------
class CreditRAGSystem:
    """RAG system for SEC 10-K filings"""

    def __init__(self, persist_directory="data/chroma_db_parallel"):
        """Initialize ChromaDB with local embeddings"""
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_directory)

        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self.collection = self.client.get_or_create_collection(
            name="credit_documents",
            embedding_function=self.embedding_function
        )

    # -----------------------------------------------------------------
    def chunk_document(self, text: str, chunk_size: int = 1000, overlap: int = 200):
        """Split document into overlapping chunks"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > chunk_size * 0.5:
                    end = start + last_period + 1
                    chunk = text[start:end]
            chunks.append(chunk.strip())
            start = end - overlap
        return chunks

    # -----------------------------------------------------------------
    def add_document(self, ticker: str, document_text: str, doc_type: str = "10-K", n_workers: int = 4):
        """Add a 10-K document to the vector store (parallelized embedding)"""
        print(f"\nAdding {ticker} {doc_type} to RAG system...")

        chunks = self.chunk_document(document_text)
        print(f"  Created {len(chunks)} chunks")

        # Split chunks evenly across workers
        chunk_splits = np.array_split(chunks, n_workers)
        chunk_splits = [list(split) for split in chunk_splits if len(split) > 0]

        print(f"  Using {n_workers} parallel workers for embedding...")

        # Parallel embedding
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            embeddings = list(executor.map(embed_worker, chunk_splits))

        # Combine all embeddings
        embeddings = np.vstack(embeddings)
        print(f"  Embedding complete. Adding to ChromaDB...")

        ids = [f"{ticker}_{doc_type}_{j}" for j in range(len(chunks))]
        metadatas = [
            {
                "ticker": ticker,
                "doc_type": doc_type,
                "chunk_id": j,
                "total_chunks": len(chunks)
            }
            for j in range(len(chunks))
        ]

        self.collection.add(
            documents=chunks,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids
        )

        print(f"  ✓ Added {ticker} ({len(chunks)} chunks, parallel embedded)")

    # -----------------------------------------------------------------
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
        query = "risk factors business risks financial risks market risks operational risks"
        return self.retrieve(query, ticker, n_results)

    def get_financial_performance(self, ticker: str, n_results: int = 3):
        query = "revenue earnings profit loss performance results operations financial condition"
        return self.retrieve(query, ticker, n_results)

    def get_debt_discussion(self, ticker: str, n_results: int = 3):
        query = "debt obligations borrowings liquidity capital structure financing"
        return self.retrieve(query, ticker, n_results)


# ---------------------------------------------------------------------
# Build database from multiple tickers
# ---------------------------------------------------------------------
def build_rag_database(tickers: list, persist_directory="data/chroma_db_parallel", n_workers=4):
    """Build RAG database for multiple companies"""
    rag = CreditRAGSystem(persist_directory)

    for ticker in tickers:
        filepath = None
        search_path = f"data/raw/sec-edgar-filings/{ticker}/10-K"
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

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

        rag.add_document(ticker, text, n_workers=n_workers)

    print("\n✓ RAG database built successfully")
    return rag


# ---------------------------------------------------------------------
# Script entry point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    tickers = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'JPM', 'JNJ']
    rag = build_rag_database(tickers, n_workers=16)

    print("\n" + "=" * 70)
    print("TESTING RAG RETRIEVAL")
    print("=" * 70)

    results = rag.get_risk_factors("AAPL", n_results=2)

    print("\nTop 2 risk factor chunks for AAPL:")
    for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
        print(f"\nChunk {i + 1}:")
        print(f"  {doc[:200]}...")

