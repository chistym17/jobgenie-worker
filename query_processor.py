import os
from dotenv import load_dotenv
from embedder import get_embedding
from qdrant_service import search_similar
from typing import Dict, List
import json

load_dotenv()

class QueryProcessor:
    def __init__(self):
        """Initialize the query processor"""
        self.test_queries = [
            "Find full-stack developer positions with React and Node.js",
            "Find jobs that require machine learning experience",
            "Find remote developer positions with competitive salary"
        ]

    def create_embedding(self, query: str) -> List[float]:
        """Create embedding from query text"""
        embedding = get_embedding(query)
        if not embedding:
            print("Failed to create query embedding")
            return []
        return embedding

    def format_results(self, results: list) -> list:
        """Extract essential fields from Qdrant results"""
        formatted_results = []
        for result in results:
            formatted_result = {
                'score': result.score,
                'payload': result.payload
            }
            formatted_results.append(formatted_result)
        return formatted_results

    def search_jobs(self, query: str) -> list:
        """Search for jobs using semantic search"""
        print(f"Searching for: {query}")
        
        try:
            query_embedding = self.create_embedding(query)
            
            if not query_embedding:
                return []
            
            results = search_similar(query_embedding)

            print(f"Search results: {results}")
            
            if not results:
                return []
            
            return self.format_results(results)
            
        except Exception as e:
            print(f"Error in search: {str(e)}")
            return []

    def test_searches(self):
        """Run predefined test searches"""
        print("Running test searches...")
        
        for query in self.test_queries:
            print(f"\nSearching for: {query}")
            results = self.search_jobs(query)
            for result in results:
                print(f"Score: {result['score']:.2f}")
                print(f"Title: {result['payload'].get('title', 'Unknown')}")
                print(f"Company: {result['payload'].get('company', 'Unknown')}")
                print("-" * 50)

if __name__ == '__main__':
    query_processor = QueryProcessor()
    query_processor.test_searches()
    