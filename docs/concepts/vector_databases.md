# Vector Databases and Similarity Search

*SynthaTrial is a research prototype; its outputs must not be used for clinical decision-making.*

## What is a Vector Database?

A vector database is a specialized database designed to store and search high-dimensional vectors (arrays of numbers). Unlike traditional databases that search by exact matches, vector databases find similar items based on mathematical distance.

**Key Concept:** Similar items have similar vectors (close in mathematical space).

---

## Why Vector Databases for Drug Discovery?

### The Problem

We have millions of drugs. How do we find drugs similar to a new compound?

**Traditional Approach:**
- Compare SMILES strings character-by-character ❌ (doesn't capture chemical similarity)
- Search by name ❌ (doesn't help with new compounds)
- Manual expert review ❌ (too slow)

**Vector Database Approach:**
- Convert drugs to mathematical vectors (fingerprints) ✅
- Store vectors in database ✅
- Search by similarity (mathematical distance) ✅
- Fast, scalable, captures chemical structure ✅

---

## Molecular Fingerprints

### What is a Fingerprint?

A molecular fingerprint is a fixed-length binary vector (array of 0s and 1s) that represents a molecule's structure.

**Example:**
```
Molecule: Paracetamol (C8H9NO2)
Fingerprint: [0, 1, 0, 1, 1, 0, 0, 1, ..., 0, 1]  (2048 bits)
```

**Key Properties:**
- Same molecule → same fingerprint
- Similar molecules → similar fingerprints
- Different molecules → different fingerprints

### Morgan Fingerprints (What We Use)

**Definition:** Circular fingerprints that capture local structure around each atom.

**How It Works:**
1. Start at each atom in the molecule
2. Look at neighbors within radius R (we use radius 2)
3. Encode structural patterns as bits
4. Result: 2048-bit binary vector

**Why Radius 2?**
- Radius 1: Too local (misses important patterns)
- Radius 2: Good balance (captures functional groups)
- Radius 3+: Too broad (loses specificity)

**Example:**
```
Molecule: C-C-O (ethanol)
Radius 0: Just atoms (C, C, O)
Radius 1: Atoms + direct neighbors
Radius 2: Atoms + neighbors + neighbors of neighbors
```

**Code:**
```python
from rdkit import Chem
from rdkit.Chem import AllChem

mol = Chem.MolFromSmiles("CC(=O)Nc1ccc(O)cc1")  # Paracetamol
fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)
# Returns: 2048-bit binary vector
```

---

## Similarity Metrics

### Cosine Similarity (What Pinecone Uses)

**Definition:** Measures the angle between two vectors, not their magnitude.

**Formula:**
```
cosine_similarity = (A · B) / (||A|| × ||B||)
```

**Range:** -1 to 1
- 1.0 = Identical (same direction)
- 0.0 = Orthogonal (perpendicular)
- -1.0 = Opposite

**Why Cosine for Molecules?**
- Focuses on structural patterns (direction)
- Less sensitive to molecule size
- Good for binary fingerprints

**Example:**
```
Drug A: [1, 0, 1, 0, 1, ...]
Drug B: [1, 0, 1, 0, 1, ...]  # Identical
Similarity: 1.0

Drug A: [1, 0, 1, 0, 1, ...]
Drug B: [0, 1, 0, 1, 0, ...]  # Completely different
Similarity: 0.0
```

### Tanimoto/Jaccard Similarity (Mentioned in Paper)

**Definition:** Measures overlap between two binary sets.

**Formula:**
```
tanimoto = (A ∩ B) / (A ∪ B)
```

**Range:** 0 to 1
- 1.0 = Identical sets
- 0.0 = No overlap

**Why Not Used:**
- Pinecone uses cosine similarity by default
- For binary fingerprints, cosine and Tanimoto are similar
- Cosine is more efficient for large-scale search

**Note:** Our paper mentions Tanimoto, but implementation uses cosine (both are valid for binary fingerprints).

---

## Pinecone Vector Database

### What is Pinecone?

Pinecone is a managed vector database service. We use it to store drug fingerprints and search for similar drugs.

**Why Pinecone?**
- ✅ Managed service (no server setup)
- ✅ Fast similarity search
- ✅ Free tier available
- ✅ Easy API
- ✅ Scales to millions of vectors

### How We Use Pinecone

**1. Index Creation:**
```python
# Create index with 2048 dimensions (fingerprint size)
index = pc.create_index(
    name="drug-index",
    dimension=2048,
    metric="cosine"
)
```

**2. Ingestion:**
```python
# Convert drug to fingerprint
fingerprint = get_drug_fingerprint(smiles)  # List[int]
fingerprint_float = [float(x) for x in fingerprint]  # Convert to floats

# Store in Pinecone
index.upsert(vectors=[{
    'id': 'drug_123',
    'values': fingerprint_float,
    'metadata': {
        'name': 'Paracetamol',
        'smiles': 'CC(=O)Nc1ccc(O)cc1',
        'targets': 'COX-1, COX-2'
    }
}])
```

**3. Search:**
```python
# Query for similar drugs
results = index.query(
    vector=fingerprint_float,
    top_k=3,  # Get top 3 similar drugs
    include_metadata=True
)

# Returns:
# [
#   {'id': 'drug_123', 'score': 0.95, 'metadata': {'name': 'Paracetamol'}},
#   {'id': 'drug_456', 'score': 0.87, 'metadata': {'name': 'Ibuprofen'}},
#   {'id': 'drug_789', 'score': 0.82, 'metadata': {'name': 'Aspirin'}}
# ]
```

---

## Retrieval-Augmented Generation (RAG)

### What is RAG?

RAG combines vector search with LLMs to provide context-aware responses.

**Traditional LLM:**
- Only uses training data
- May hallucinate
- No access to specific databases

**RAG-Enhanced LLM:**
- Searches vector database for relevant context
- Uses retrieved context in prompt
- More accurate, grounded responses

### How We Use RAG

**1. User Input:**
```
Drug: New compound (SMILES)
Patient: Poor metabolizer
```

**2. Vector Search:**
```python
# Find similar drugs
similar_drugs = find_similar_drugs(drug_fingerprint)
# Returns: ["Paracetamol", "Ibuprofen", "Aspirin"]
```

**3. Retrieve Context:**
```python
# Get metadata for similar drugs
context = {
    'similar_drugs': similar_drugs,
    'known_side_effects': ['Nausea', 'Liver toxicity'],
    'cyp_interactions': ['CYP2D6 substrate']
}
```

**4. LLM Prompt:**
```python
prompt = f"""
You are a pharmacogenomics expert.

Drug: {drug_name}
Similar drugs: {similar_drugs}
Patient: {patient_profile}

Based on similar drugs and patient genetics, predict:
1. Risk level
2. Predicted reaction
3. Biological mechanism
"""
```

**5. LLM Response:**
- Uses retrieved context (similar drugs)
- Grounds predictions in known data
- More accurate than LLM alone

---

## Performance Characteristics

### Search Speed

**Pinecone Performance:**
- Query latency: <200ms (as claimed in paper)
- Scales to millions of vectors
- Sub-second search even with large databases

**Why Fast:**
- Optimized vector search algorithms
- Approximate nearest neighbor (ANN) search
- Distributed infrastructure

### Accuracy

**Fingerprint Quality:**
- Morgan fingerprints capture chemical structure well
- Similar molecules → similar fingerprints
- Good for drug similarity search

**Limitations:**
- May miss subtle differences
- Doesn't capture 3D structure
- Binary fingerprints lose some information

---

## Comparison with Other Approaches

### 1. Exact String Matching

**Approach:** Compare SMILES strings character-by-character

**Problems:**
- `CC(=O)O` vs `CC(=O)OH` → Different strings, same molecule
- Doesn't capture chemical similarity
- Too rigid

**Verdict:** ❌ Not suitable for similarity search

---

### 2. Graph Neural Networks (GNNs)

**Approach:** Use deep learning to learn molecular representations

**Advantages:**
- Can capture complex patterns
- Learns from data
- Very accurate

**Disadvantages:**
- Requires training data
- More complex
- Slower inference

**Verdict:** ✅ Better for accuracy, but more complex

---

### 3. Molecular Fingerprints (Our Approach)

**Advantages:**
- Fast (pre-computed)
- No training needed
- Good balance of speed and accuracy
- Industry standard

**Disadvantages:**
- Fixed representation
- May miss subtle patterns
- Binary encoding loses some information

**Verdict:** ✅ Good for MVP, widely used in industry

---

## Future Improvements

### 1. Hybrid Approaches

Combine fingerprints with GNNs:
- Use fingerprints for fast initial search
- Use GNNs for detailed comparison

### 2. Multi-Modal Vectors

Combine multiple representations:
- Molecular fingerprints
- 3D structure
- Pharmacophore features
- Target binding profiles

### 3. Learned Embeddings

Train embeddings on drug-target interactions:
- Learn from ChEMBL data
- Capture functional similarity
- Better than structure-only fingerprints

---

## Key Takeaways

1. **Vector databases enable fast similarity search** - Essential for drug discovery
2. **Molecular fingerprints encode structure** - Morgan fingerprints are industry standard
3. **Cosine similarity works well** - Good for binary fingerprints
4. **RAG combines search with LLMs** - Provides context-aware predictions
5. **Performance is excellent** - Sub-second search even with millions of drugs

---

## Resources

- **RDKit Documentation:** https://www.rdkit.org/docs/
- **Pinecone Documentation:** https://docs.pinecone.io/
- **Vector Database Comparison:** https://www.pinecone.io/learn/vector-databases/
- **Molecular Fingerprints:** https://www.rdkit.org/docs/GettingStartedInPython.html#molecular-fingerprints

---

*This document explains vector databases and similarity search concepts used in SynthaTrial. For implementation details, see `docs/implementation/`.*
