# Retrieval-Augmented Generation (RAG) Explained

*SynthaTrial is a research prototype; its outputs must not be used for clinical decision-making.*

## What is RAG?

**Retrieval-Augmented Generation (RAG)** is a technique that combines:
1. **Retrieval:** Finding relevant information from a knowledge base
2. **Augmentation:** Adding that information to an LLM prompt
3. **Generation:** Using the LLM to generate responses based on retrieved context

**Key Idea:** Instead of relying solely on the LLM's training data, we give it specific, relevant context from our own database.

---

## Why RAG?

### Problems with LLMs Alone

1. **Training Data Limitations:**
   - LLMs are trained on data up to a certain date
   - May not know about latest drugs or research
   - Can't access proprietary databases

2. **Hallucination:**
   - LLMs may make up information
   - No way to verify accuracy
   - Can be confident about wrong answers

3. **No Access to Specific Data:**
   - Can't query ChEMBL database directly
   - Can't access patient VCF files
   - Limited to what it was trained on

### How RAG Solves This

1. **Retrieves Real Data:**
   - Searches our ChEMBL database
   - Finds similar drugs with known effects
   - Gets actual, verifiable information

2. **Grounds Responses:**
   - LLM uses retrieved context
   - Less likely to hallucinate
   - Can cite sources (similar drugs)

3. **Access to Specific Data:**
   - Can use our drug database
   - Can use patient genetic data
   - Combines general knowledge with specific data

---

## How RAG Works (Step by Step)

### Step 1: User Query

**Input:**
```
Drug: New compound (SMILES: CC(=O)Nc1ccc(O)cc1)
Patient: Poor metabolizer (CYP2D6*4/*4)
```

---

### Step 2: Convert to Vector

**What We Do:**
```python
# Convert drug SMILES to fingerprint
fingerprint = get_drug_fingerprint("CC(=O)Nc1ccc(O)cc1")
# Returns: [0, 1, 0, 1, 1, 0, ..., 1]  (2048 bits)
```

**Why:**
- Need numerical representation for search
- Fingerprint captures chemical structure
- Can compare with other drugs

---

### Step 3: Retrieve Similar Drugs

**What We Do:**
```python
# Search Pinecone for similar drugs
similar_drugs = find_similar_drugs(fingerprint, top_k=3)
# Returns: ["Paracetamol", "Ibuprofen", "Aspirin"]
```

**What Happens:**
1. Pinecone searches vector database
2. Finds drugs with similar fingerprints
3. Returns top 3 matches with metadata

**Retrieved Context:**
```python
{
    "Paracetamol": {
        "targets": "COX-1, COX-2",
        "side_effects": "Liver toxicity in overdose",
        "cyp_interactions": "CYP2D6 substrate"
    },
    "Ibuprofen": {
        "targets": "COX-1, COX-2",
        "side_effects": "GI bleeding",
        "cyp_interactions": "CYP2C9 substrate"
    },
    "Aspirin": {
        "targets": "COX-1",
        "side_effects": "GI bleeding, Reye's syndrome",
        "cyp_interactions": "CYP2C9 substrate"
    }
}
```

---

### Step 4: Augment LLM Prompt

**What We Do:**
```python
prompt = f"""
You are a pharmacogenomics expert analyzing drug safety.

DRUG INFORMATION:
- Name: {drug_name}
- SMILES: {smiles}
- Structure: Similar to {similar_drugs}

SIMILAR DRUGS (for reference):
1. Paracetamol:
   - Targets: COX-1, COX-2
   - Known side effects: Liver toxicity in overdose
   - CYP interactions: CYP2D6 substrate

2. Ibuprofen:
   - Targets: COX-1, COX-2
   - Known side effects: GI bleeding
   - CYP interactions: CYP2C9 substrate

3. Aspirin:
   - Targets: COX-1
   - Known side effects: GI bleeding, Reye's syndrome
   - CYP interactions: CYP2C9 substrate

PATIENT PROFILE:
- CYP2D6 Status: Poor Metabolizer (*4/*4)
- CYP2C19 Status: Extensive Metabolizer
- Medical Conditions: Chronic Liver Disease (Mild)
- Lifestyle: Alcohol consumer (Moderate)

TASK:
Based on the similar drugs and patient genetics, predict:
1. Risk Level (Low/Medium/High)
2. Predicted Reaction (detailed analysis)
3. Biological Mechanism (how genetics affects drug metabolism)

Be specific and reference the similar drugs when relevant.
"""
```

**Key Points:**
- Includes retrieved context (similar drugs)
- Includes patient profile
- Gives LLM specific, relevant information
- Asks for structured output

---

### Step 5: LLM Generation

**What Happens:**
1. LLM receives augmented prompt
2. Uses retrieved context to ground predictions
3. References similar drugs when relevant
4. Generates structured response

**Example Output:**
```
RISK LEVEL: Medium

PREDICTED REACTION:
Based on similarity to Paracetamol and patient's CYP2D6 poor metabolizer
status, there is moderate risk of:
- Reduced drug clearance (CYP2D6 is involved in metabolism)
- Potential accumulation in poor metabolizers
- Similar to Paracetamol, liver toxicity is a concern given patient's
  chronic liver disease

BIOLOGICAL MECHANISM:
The drug is a CYP2D6 substrate (similar to Paracetamol). In poor
metabolizers (CYP2D6*4/*4), the enzyme has reduced activity, leading to:
- Slower drug clearance
- Higher drug concentrations
- Increased risk of adverse effects
- Particularly concerning given patient's liver disease
```

**Why This is Better:**
- Grounded in real data (similar drugs)
- References specific drugs
- Explains mechanism
- Less likely to hallucinate

---

## RAG Architecture in SynthaTrial

```
┌─────────────┐
│ User Input  │
│ (Drug +     │
│  Patient)   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Convert to      │
│ Fingerprint     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐      ┌──────────────┐
│ Vector Search   │─────▶│ Pinecone DB  │
│ (Pinecone)      │      │ (Drug Vectors)│
└──────┬──────────┘      └──────────────┘
       │
       ▼
┌─────────────────┐
│ Retrieve        │
│ Similar Drugs   │
│ + Metadata      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Augment Prompt  │
│ with Context    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐      ┌──────────────┐
│ LLM Generation  │─────▶│ Gemini API   │
│ (Gemini)        │      │              │
└──────┬──────────┘      └──────────────┘
       │
       ▼
┌─────────────────┐
│ Final Prediction│
│ (Risk +         │
│  Mechanism)     │
└─────────────────┘
```

---

## Benefits of RAG in Our System

### 1. Accuracy

**Without RAG:**
- LLM relies only on training data
- May not know about specific drugs
- Can hallucinate interactions

**With RAG:**
- Uses actual ChEMBL data
- References real similar drugs
- Grounded in verifiable information

### 2. Relevance

**Without RAG:**
- Generic responses
- May not consider patient genetics
- Doesn't use similar drugs

**With RAG:**
- Specific to patient profile
- Uses similar drugs for context
- Personalized predictions

### 3. Explainability

**Without RAG:**
- Hard to explain why LLM said something
- No sources to cite

**With RAG:**
- Can cite similar drugs
- Can explain based on retrieved context
- More transparent

---

## Limitations

### 1. Retrieval Quality

**Problem:**
- If similar drugs aren't actually similar, context is wrong
- Vector search may miss relevant drugs
- Fingerprints may not capture all similarities

**Solution:**
- Use high-quality fingerprints (Morgan fingerprints)
- Retrieve multiple similar drugs (top_k=3)
- LLM can filter out irrelevant context

### 2. Context Window

**Problem:**
- LLMs have limited context windows
- Can't include all retrieved information
- May need to truncate context

**Solution:**
- Limit to top 3-5 similar drugs
- Summarize metadata
- Focus on most relevant information

### 3. LLM Interpretation

**Problem:**
- LLM may misinterpret retrieved context
- May over-rely on similar drugs
- May ignore patient-specific factors

**Solution:**
- Clear prompt structure
- Explicit instructions
- Structured output format

---

## Comparison with Other Approaches

### 1. LLM Only (No RAG)

**Approach:** Just ask LLM directly

**Problems:**
- No access to ChEMBL data
- May hallucinate
- Not grounded in real data

**Verdict:** ❌ Not suitable for our use case

---

### 2. Rule-Based System

**Approach:** Hard-coded rules (if CYP2D6 poor → high risk)

**Problems:**
- Too rigid
- Can't handle complex cases
- Requires expert knowledge for all drugs

**Verdict:** ❌ Too limited

---

### 3. RAG (Our Approach)

**Approach:** Retrieve similar drugs, augment prompt, generate

**Advantages:**
- Uses real data (ChEMBL)
- Flexible (LLM can reason)
- Grounded in similar drugs
- Can handle new drugs

**Verdict:** ✅ Best balance

---

## Future Improvements

### 1. Multi-Stage Retrieval

**Current:** Single vector search

**Future:**
- Stage 1: Find similar drugs (structure)
- Stage 2: Find drugs with similar targets
- Stage 3: Find drugs with similar side effects
- Combine all contexts

### 2. Re-Ranking

**Current:** Use top_k results directly

**Future:**
- Re-rank by relevance to patient
- Filter by CYP interactions
- Weight by clinical importance

### 3. Iterative RAG

**Current:** Single retrieval → generation

**Future:**
- Generate initial prediction
- Retrieve additional context if needed
- Refine prediction

---

## Key Takeaways

1. **RAG combines retrieval with generation** - Best of both worlds
2. **Retrieves real data** - Uses ChEMBL, not just training data
3. **Grounds LLM responses** - Less hallucination, more accuracy
4. **Enables personalized predictions** - Uses patient-specific data
5. **Improves explainability** - Can cite similar drugs

---

## Resources

- **RAG Paper:** https://arxiv.org/abs/2005.11401
- **LangChain RAG:** https://python.langchain.com/docs/use_cases/question_answering/
- **Vector Search:** See `docs/concepts/vector_databases.md`

---

*This document explains RAG concepts used in SynthaTrial. For implementation details, see `docs/implementation/`.*
