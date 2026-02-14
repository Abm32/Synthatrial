"""
Vector Search Module

Handles similarity search using Pinecone vector database.
Includes mock mode for testing without API credentials.
"""

import logging
from typing import List, Optional

from pinecone import Pinecone
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.config import config
from src.exceptions import VectorSearchError

# Set up logging
logger = logging.getLogger(__name__)

# Global Pinecone client and index (lazy initialization)
_pinecone_client: Optional[Pinecone] = None
_pinecone_index = None


def _get_pinecone_index():
    """
    Get or initialize Pinecone index with lazy loading.

    Returns:
        Pinecone Index object or None if unavailable

    Raises:
        VectorSearchError: If initialization fails and no fallback available
    """
    global _pinecone_client, _pinecone_index

    if _pinecone_index is not None:
        return _pinecone_index

    if not config.PINECONE_API_KEY:
        logger.warning("PINECONE_API_KEY not found - will use mock data mode")
        return None

    try:
        logger.info("Initializing Pinecone connection...")
        _pinecone_client = Pinecone(api_key=config.PINECONE_API_KEY)
        _pinecone_index = _pinecone_client.Index(config.PINECONE_INDEX)
        logger.info(f"✓ Connected to Pinecone index: {config.PINECONE_INDEX}")
        return _pinecone_index
    except Exception as e:
        logger.warning(
            f"Could not initialize Pinecone: {e} - falling back to mock data"
        )
        return None


def find_similar_drugs(vector: List[int], top_k: Optional[int] = None) -> List[str]:
    """
    Queries the database for similar drugs using vector similarity search.

    Args:
        vector: Molecular fingerprint as a list of integers
        top_k: Number of similar drugs to return (default: from config)

    Returns:
        List of formatted drug strings with structure information:
        ["Drug Name | SMILES: ... | Side Effects: ... | Targets: ...", ...]

    Raises:
        VectorSearchError: If vector search fails and no fallback available
    """
    if top_k is None:
        top_k = config.PINECONE_TOP_K

    # Validate vector
    if not vector or len(vector) != config.FINGERPRINT_BITS:
        raise VectorSearchError(
            f"Invalid vector size: expected {config.FINGERPRINT_BITS}, got {len(vector) if vector else 0}",
            query_vector_size=len(vector) if vector else 0,
        )

    # Get Pinecone index (with fallback to mock)
    index = _get_pinecone_index()

    # Fallback to mock data if Pinecone unavailable
    if index is None:
        logger.info("Using mock data for vector search")
        return _get_mock_drugs()

    # Convert vector to float (Pinecone requires float vectors)
    vector_float = [float(x) for x in vector]

    logger.info(f"Searching for {top_k} similar drugs in Pinecone...")

    try:
        results = _query_pinecone_with_retry(index, vector_float, top_k)

        # Format the output for the LLM with structure information
        found_drugs = []
        for match in results["matches"]:
            drug_name = match["metadata"].get("name", "Unknown")
            smiles = match["metadata"].get("smiles", "Not available")
            side_effects = match["metadata"].get("known_side_effects", "None listed")
            targets = match["metadata"].get("targets", "Unknown")

            # Format: Name | SMILES: ... | Side Effects: ... | Targets: ...
            drug_info = f"{drug_name} | SMILES: {smiles} | Side Effects: {side_effects} | Targets: {targets}"
            found_drugs.append(drug_info)

        logger.info(f"Found {len(found_drugs)} similar drugs")
        return found_drugs

    except Exception as e:
        logger.error(f"Vector search failed: {e}", exc_info=True)
        # Fallback to mock data on error
        logger.warning("Falling back to mock data due to error")
        return _get_mock_drugs()


from src.resilience import CircuitBreakerOpenError, circuit_breaker


@circuit_breaker(failure_threshold=5, reset_timeout=30, name="Pinecone-DB")
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    retry=retry_if_exception_type((Exception,)),
    reraise=True,
)
def _query_pinecone_with_retry(index, vector: List[float], top_k: int):
    """
    Query Pinecone with retry logic and circut breaker.
    """
    try:
        return index.query(vector=vector, top_k=top_k, include_metadata=True)
    except Exception as e:
        logger.warning(f"Pinecone query failed (will retry if circuit closed): {e}")
        raise VectorSearchError(
            f"Pinecone query failed: {str(e)}",
            index_name=config.PINECONE_INDEX,
            query_vector_size=len(vector),
        ) from e


def _get_mock_drugs() -> List[str]:
    """
    Return mock drug data for testing/fallback.

    Returns:
        List of formatted mock drug strings
    """
    return [
        "Mock Drug A | SMILES: CC(=O)O | Side Effects: Nausea | Targets: Unknown",
        "Mock Drug B | SMILES: CC(C)CC1=CC=C(C=C1)C(C)C(=O)O | Side Effects: Headache | Targets: Unknown",
        "Mock Drug C | SMILES: CC1=CC=C(C=C1)C(=O)O | Side Effects: Dizziness | Targets: Unknown",
    ]
