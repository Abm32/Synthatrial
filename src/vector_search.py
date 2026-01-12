"""
Vector Search Module

Handles similarity search using Pinecone vector database.
Includes mock mode for testing without API credentials.
"""

from typing import List
import os
from pinecone import Pinecone

# Set your API Key in terminal: export PINECONE_API_KEY="your_key"
# Or use python-dotenv to load from .env file
pc = None
index = None

# Initialize Pinecone if API key is available
api_key = os.environ.get("PINECONE_API_KEY")
if api_key:
    try:
        pc = Pinecone(api_key=api_key)
        # Connect to your index (Create one named 'drug-index' on Pinecone website first)
        # Ensure you create the index on the Pinecone dashboard with 2048 dimensions
        index = pc.Index("drug-index")
    except Exception as e:
        print(f"Warning: Could not initialize Pinecone: {e}")


def find_similar_drugs(vector: List[int], top_k: int = 3) -> List[str]:
    """
    Queries the database for the top 3 most similar drugs.
    
    Args:
        vector: Molecular fingerprint as a list of integers
        top_k: Number of similar drugs to return (default: 3)
        
    Returns:
        List of formatted drug strings: ["Drug Name (Side Effect: ...)", ...]
    """
    # Safety check: if API key is missing, return mock data
    if not api_key or not index:
        return [
            "Mock Drug A (Side Effect: Nausea)",
            "Mock Drug B (Side Effect: Headache)",
            "Mock Drug C (Side Effect: Dizziness)"
        ]

    try:
        results = index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format the output for the LLM
        found_drugs = []
        for match in results['matches']:
            drug_name = match['metadata'].get('name', 'Unknown')
            side_effects = match['metadata'].get('known_side_effects', 'None listed')
            found_drugs.append(f"{drug_name} (Side Effects: {side_effects})")
            
        return found_drugs
    except Exception as e:
        print(f"Vector DB Error: {e}")
        return ["Error retrieving similar drugs"]
