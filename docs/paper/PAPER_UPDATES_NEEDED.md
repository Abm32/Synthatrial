# Paper Updates Needed

## Quick Reference: What to Change in anukriti.tex

### 1. Line 91 - Similarity Metric
**Change:** "Tanimoto/Jaccard similarity" → "cosine similarity"

### 2. Line 74 - Knowledge Graphs  
**Change:** "structured biomedical knowledge graphs" → "Retrieval-Augmented Generation (RAG) over structured biomedical knowledge bases"

### 3. Lines 111-113 - Add Specific Results
**Add:** Specific test case (codeine + poor metabolizer) with actual output

### 4. Line 116 - Performance Metrics
**Option A:** Measure and report actual values
**Option B:** Remove specific numbers, say "sub-second" and "few seconds"

### 5. Add Limitations Section
**Add:** Section discussing simplified inference, single chromosome, etc.

---

## Status: ✅ Core Features Implemented

- VCF processing: ✅ Working
- ChEMBL integration: ✅ Working  
- RAG pipeline: ✅ Working
- LLM predictions: ✅ Working
- End-to-end workflow: ✅ Working

**Paper is mostly accurate, needs minor terminology corrections.**
