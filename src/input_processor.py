"""
Input Processor Module

Handles SMILES string validation and conversion to molecular fingerprints.
Includes caching for performance optimization.
"""

import logging
from typing import Dict, List

import numpy as np
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem

from src.config import config
from src.exceptions import InvalidSMILESError

# Set up logging
logger = logging.getLogger(__name__)

# Cache for fingerprints (LRU cache with configurable size)
_fingerprint_cache: Dict[str, List[int]] = {}


def validate_smiles(smiles: str) -> bool:
    """
    Validate a SMILES string using RDKit.

    Args:
        smiles: SMILES string to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not smiles:
        return False

    try:
        mol = Chem.MolFromSmiles(smiles)
        return mol is not None
    except Exception:
        return False


def get_drug_fingerprint(smiles: str, use_cache: bool = None) -> List[int]:
    """
    Converts a SMILES string into a 2048-bit vector.

    Args:
        smiles: SMILES string representing the chemical structure
        use_cache: Whether to use caching (default: from config)

    Returns:
        List of integers (0s and 1s) representing the 2048-bit Morgan fingerprint

    Raises:
        InvalidSMILESError: If SMILES string is invalid
    """
    if use_cache is None:
        use_cache = config.ENABLE_CACHING

    # Check cache if enabled
    if use_cache and smiles in _fingerprint_cache:
        logger.debug(f"Using cached fingerprint for SMILES: {smiles[:50]}...")
        cached: List[int] = _fingerprint_cache[smiles]
        return cached

    # Validate and process SMILES
    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            raise InvalidSMILESError(smiles, reason="RDKit could not parse SMILES")

        logger.debug(f"Generating fingerprint for SMILES: {smiles[:50]}...")

        # Generate Morgan Fingerprint (Radius 2)
        fp = AllChem.GetMorganFingerprintAsBitVect(  # type: ignore[attr-defined]
            mol, config.FINGERPRINT_RADIUS, nBits=config.FINGERPRINT_BITS
        )

        # Convert to numpy array first, then to Python list
        arr = np.zeros((config.FINGERPRINT_BITS,), dtype=np.int32)
        DataStructs.ConvertToNumpyArray(fp, arr)
        fingerprint: List[int] = arr.tolist()

        # Cache if enabled
        if use_cache:
            _fingerprint_cache[smiles] = fingerprint
            logger.debug(f"Cached fingerprint for SMILES: {smiles[:50]}...")

        return fingerprint

    except InvalidSMILESError:
        raise
    except Exception as e:
        logger.error(f"Error processing SMILES: {e}", exc_info=True)
        raise InvalidSMILESError(smiles, reason=str(e)) from e


def clear_fingerprint_cache():
    """Clear the fingerprint cache."""
    global _fingerprint_cache
    _fingerprint_cache = {}
    logger.info("Fingerprint cache cleared")
