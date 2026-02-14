# SynthaTrial Integration Flow Analysis

## Quick Reference: Integration Status

| Integration Point | Status | Notes |
|------------------|--------|-------|
| **RDKit → Fingerprinting** | ✅ Excellent | Clean, well-tested |
| **Pinecone → Vector Search** | ✅ Good | Has mock fallback |
| **Google Gemini → LLM** | ✅ Good | Needs retry logic |
| **VCF → Variant Extraction** | ✅ Good | Needs optimization |
| **ChEMBL → Drug Data** | ✅ Good | Side effects placeholder |
| **Streamlit → Components** | ✅ Good | Needs early API check |
| **CLI → Components** | ✅ Good | User-friendly errors needed |

---

## Detailed Integration Flow

### 1. Drug Input Flow

```
User Input (SMILES)
    ↓
[app.py / main.py]
    ↓
src/input_processor.py::get_drug_fingerprint()
    ├─ Validates SMILES (RDKit)
    ├─ Generates 2048-bit Morgan Fingerprint
    └─ Returns List[int]
    ↓
src/vector_search.py::find_similar_drugs()
    ├─ Checks Pinecone API key
    ├─ If available: Query Pinecone (cosine similarity)
    ├─ If unavailable: Return mock data
    └─ Returns List[str] (formatted drug info)
    ↓
src/agent_engine.py::run_simulation()
    ├─ Assembles prompt with:
    │   ├─ Drug name + SMILES
    │   ├─ Similar drugs (with SMILES)
    │   └─ Patient profile
    ├─ Calls Google Gemini API
    └─ Returns risk assessment
```

**Integration Quality: ✅ GOOD**
- Clear data flow
- Proper error handling at each step
- Fallback mechanisms in place

**Issues:**
- No caching of fingerprints
- No retry logic for API calls
- No validation between steps

---

### 2. Patient Profile Flow

```
Option A: Manual Profile
    ↓
[app.py sidebar / main.py args]
    ↓
Formatted string → agent_engine

Option B: VCF-Derived Profile
    ↓
VCF File (chr22 or chr10)
    ↓
src/vcf_processor.py::extract_cyp_variants()
    ├─ Parses VCF file (gzip support)
    ├─ Filters by gene region (CYP2D6, CYP2C19, CYP2C9)
    └─ Returns List[Dict] (variants)
    ↓
src/vcf_processor.py::infer_metabolizer_status()
    ├─ Looks up variants in variant_db.py
    ├─ Calculates Activity Score
    └─ Returns metabolizer status string
    ↓
src/vcf_processor.py::generate_patient_profile_from_vcf()
    ├─ Combines all enzyme statuses
    ├─ Adds age, conditions, lifestyle
    └─ Returns formatted string
    ↓
agent_engine::run_simulation()
```

**Integration Quality: ✅ GOOD**
- Supports both manual and VCF-derived profiles
- Multi-chromosome support (chr22 + chr10)
- Proper variant lookup using CPIC guidelines

**Issues:**
- Memory-intensive for large VCF files
- No progress indicators
- Hardcoded genome coordinates

---

### 3. ChEMBL Integration Flow

```
ChEMBL SQLite Database
    ↓
scripts/ingest_chembl_to_pinecone.py
    ↓
src/chembl_processor.py::batch_extract_drugs()
    ├─ Connects to ChEMBL SQLite
    ├─ Extracts approved drugs (phase 2+)
    ├─ Validates SMILES
    └─ Returns List[Dict]
    ↓
src/chembl_processor.py::prepare_drug_for_vector_db()
    ├─ Generates fingerprint (reuses input_processor)
    ├─ Extracts targets
    ├─ Extracts side effects (placeholder)
    └─ Returns Pinecone-ready record
    ↓
Pinecone Index (upsert)
```

**Integration Quality: ✅ GOOD**
- Proper batch processing
- SMILES validation
- Reuses existing fingerprint code

**Issues:**
- Side effects extraction is placeholder
- No connection pooling
- No transaction management

---

### 4. End-to-End Flow (Complete)

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                          │
│  ┌──────────────┐              ┌──────────────┐          │
│  │  Streamlit   │              │   CLI (main)  │          │
│  │   (app.py)   │              │   (main.py)   │          │
│  └──────┬───────┘              └──────┬───────┘          │
└─────────┼──────────────────────────────┼──────────────────┘
          │                              │
          └──────────────┬───────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   INPUT VALIDATION           │
          │   - SMILES format           │
          │   - Patient profile         │
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   MOLECULAR PROCESSING      │
          │   input_processor.py        │
          │   - SMILES → Fingerprint    │
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   VECTOR SEARCH             │
          │   vector_search.py          │
          │   - Find similar drugs      │
          │   - Fallback: mock data     │
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   PATIENT PROFILE            │
          │   vcf_processor.py          │
          │   - Manual or VCF-derived   │
          │   - Variant lookup          │
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   AI SIMULATION              │
          │   agent_engine.py            │
          │   - Assemble prompt          │
          │   - Call Gemini API         │
          │   - Parse response           │
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   RESULTS                   │
          │   - Risk level              │
          │   - Mechanism               │
          │   - Recommendations         │
          └─────────────────────────────┘
```

---

## Integration Dependencies

### External Dependencies:
1. **RDKit** (local) - ✅ No issues
2. **Pinecone API** (external) - ⚠️ Needs retry logic
3. **Google Gemini API** (external) - ⚠️ Needs retry logic
4. **VCF Files** (data) - ✅ Good support
5. **ChEMBL Database** (data) - ✅ Good support

### Internal Dependencies:
- All components properly isolated
- Clear interfaces between modules
- No circular dependencies

---

## Critical Integration Points

### 1. API Key Management
**Current:** Environment variables + .env file
**Status:** ✅ Good
**Improvement:** Add validation on startup

### 2. Error Propagation
**Current:** Basic try/except
**Status:** ⚠️ Needs improvement
**Improvement:** Custom exceptions, better context

### 3. Data Validation
**Current:** SMILES validation only
**Status:** ⚠️ Needs improvement
**Improvement:** Validate all inputs between steps

### 4. Caching
**Current:** None
**Status:** ❌ Missing
**Improvement:** Cache fingerprints, VCF parsing, LLM responses

### 5. Retry Logic
**Current:** None
**Status:** ❌ Missing
**Improvement:** Add retry for all external API calls

---

## Integration Test Scenarios

### Scenario 1: Happy Path
```
Input: Valid SMILES + Manual Profile
Expected: Full flow completes successfully
Status: ✅ Works
```

### Scenario 2: Missing API Keys
```
Input: Valid SMILES + No Pinecone Key
Expected: Falls back to mock data
Status: ✅ Works
```

### Scenario 3: Invalid SMILES
```
Input: Invalid SMILES string
Expected: Clear error message
Status: ✅ Works (ValueError)
```

### Scenario 4: VCF File Processing
```
Input: Large VCF file
Expected: Processes successfully
Status: ⚠️ Works but slow (needs optimization)
```

### Scenario 5: API Failure
```
Input: Valid input but API fails
Expected: Retry or graceful error
Status: ❌ No retry logic
```

---

## Recommendations Summary

### High Priority:
1. ✅ Add retry logic for API calls
2. ✅ Improve error handling
3. ✅ Centralize configuration

### Medium Priority:
4. ✅ Add caching
5. ✅ Add logging
6. ✅ Optimize VCF processing

### Low Priority:
7. ✅ Add async support
8. ✅ Add metrics/monitoring
9. ✅ Improve mock data

---

**Last Updated:** January 28, 2025
