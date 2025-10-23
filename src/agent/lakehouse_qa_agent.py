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

from src.data.lakehouse import CreditLakehouse
import duckdb

class LakehouseQAAgent:
    """Q&A Agent using LangChain + Groq"""
    
    def __init__(self, model="llama-3.3-70b-versatile"):
        """Initialize with LangChain"""
        self.llm = ChatGroq(
            temperature=0,
            model_name=model,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.lakehouse = CreditLakehouse()
        
        # SQL generation prompt
        self.sql_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a SQL expert. Generate DuckDB queries. Return ONLY the SQL, no explanations."),
            ("user", "{prompt}")
        ])
        
        # Answer generation prompt
        self.answer_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a financial analyst. Provide clear, conversational answers."),
            ("user", "{prompt}")
        ])
        
        # Create chains
        self.sql_chain = self.sql_prompt | self.llm | StrOutputParser()
        self.answer_chain = self.answer_prompt | self.llm | StrOutputParser()
        
        print("Lakehouse Q&A Agent (LangChain + Groq) loaded\n")
    
    def answer_question(self, question: str) -> str:
        """Answer using LangChain chains"""
        
        print(f"Question: {question}\n")
        
        df = self.lakehouse.read_all()
        
        if df.empty:
            return "No data in lakehouse."
        
        print("Step 1/3: Loading lakehouse data...")
        print(f"  Found {len(df)} analyses\n")
        
        # Generate SQL
        print("Step 2/3: Generating SQL query...")
        
        sql_prompt_text = f"""Generate DuckDB SQL query for this question.

Question: {question}

Table: df
Columns: {', '.join(df.columns.tolist())}

Sample:
{df.head(2).to_string()}

Return ONLY SQL query."""

        sql_query = self.sql_chain.invoke({"prompt": sql_prompt_text})
        
        # Clean SQL
        sql_query = sql_query.strip().replace("```sql", "").replace("```", "").strip()
        print(f"  SQL: {sql_query}\n")
        
        # Execute
        print("Step 3/3: Executing query...")
        try:
            result = duckdb.query(sql_query).df()
            print(f"  Retrieved {len(result)} rows\n")
        except Exception as e:
            return f"Query failed: {str(e)}"
        
        # Generate answer
        answer_prompt_text = f"""Answer this question based on the query result.

Question: {question}

Result:
{result.to_string()}

Provide clear, conversational answer."""

        answer = self.answer_chain.invoke({"prompt": answer_prompt_text})
        
        print("="*70)
        print("ANSWER:")
        print("="*70)
        print(answer)
        print("="*70)
        
        return answer
    
    def show_available_data(self):
        """Show lakehouse contents"""
        df = self.lakehouse.read_all()
        
        print("="*70)
        print("LAKEHOUSE DATA")
        print("="*70)
        print(f"Analyses: {len(df)}")
        print(f"Companies: {', '.join(df['ticker'].unique())}")
        print(f"Columns: {', '.join(df.columns.tolist())}")
        print("="*70)


def main():
    agent = LakehouseQAAgent()
    agent.show_available_data()
    
    print("\nAsk questions:")
    print("- What's Apple's credit rating?")
    print("- Which company has highest debt?\n")
    
    while True:
        question = input("\nQuestion (or 'quit'): ")
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if question.strip():
            agent.answer_question(question)


if __name__ == "__main__":
    main()
