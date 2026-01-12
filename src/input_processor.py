"""
Input Processor Module

Handles SMILES string validation and conversion to molecular fingerprints.
"""

from typing import List
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
import numpy as np

def get_drug_fingerprint(smiles: str) -> List[int]:
    """
    Converts a SMILES string into a 2048-bit vector.
    
    Args:
        smiles: SMILES string representing the chemical structure
        
    Returns:
        List of integers (0s and 1s) representing the 2048-bit Morgan fingerprint
        
    Raises:
        ValueError: If SMILES string is invalid
    """
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        raise ValueError("Invalid SMILES string")
    
    # Generate Morgan Fingerprint (Radius 2)
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
    
    # Convert to numpy array first, then to Python list
    arr = np.zeros((2048,), dtype=np.int32)
    DataStructs.ConvertToNumpyArray(fp, arr)
    return arr.tolist()
