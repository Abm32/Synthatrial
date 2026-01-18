"""
Vector Search Module

Handles similarity search using Pinecone vector database.
Includes mock mode for testing without API credentials.
"""

from typing import List
import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables from .env file
load_dotenv()

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
        print("✓ Connected to Pinecone vector database")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize Pinecone: {e}")
        print("   Falling back to mock data mode")
else:
    print("⚠️  PINECONE_API_KEY not found - using mock data mode")


def find_similar_drugs(vector: List[int], top_k: int = 3) -> List[str]:
    """
    Queries the database for the top 3 most similar drugs.
    
    Args:
        vector: Molecular fingerprint as a list of integers
        top_k: Number of similar drugs to return (default: 3)
        
    Returns:
        List of formatted drug strings with structure information:
        ["Drug Name | SMILES: ... | Side Effects: ... | Targets: ...", ...]
    """
    # Safety check: if API key is missing, return mock data
    if not api_key or not index:
        return [
            "Mock Drug A | SMILES: CC(=O)O | Side Effects: Nausea | Targets: Unknown",
            "Mock Drug B | SMILES: CC(C)CC1=CC=C(C=C1)C(C)C(=O)O | Side Effects: Headache | Targets: Unknown",
            "Mock Drug C | SMILES: CC1=CC=C(C=C1)C(=O)O | Side Effects: Dizziness | Targets: Unknown"
        ]

    try:
        results = index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format the output for the LLM with structure information
        found_drugs = []
        for match in results['matches']:
            drug_name = match['metadata'].get('name', 'Unknown')
            smiles = match['metadata'].get('smiles', 'Not available')
            side_effects = match['metadata'].get('known_side_effects', 'None listed')
            targets = match['metadata'].get('targets', 'Unknown')
            
            # Format: Name | SMILES: ... | Side Effects: ... | Targets: ...
            drug_info = f"{drug_name} | SMILES: {smiles} | Side Effects: {side_effects} | Targets: {targets}"
            found_drugs.append(drug_info)
            
        return found_drugs
    except Exception as e:
        print(f"Vector DB Error: {e}")
        return ["Error retrieving similar drugs"]
