# ChEMBL Integration Implementation

## Overview

This document details the implementation of ChEMBL database integration for extracting drug information and populating the vector database.

**File:** `src/chembl_processor.py`

---

## Purpose

Extract drug information from ChEMBL SQLite database to:
1. Get approved drugs (phase 2+)
2. Extract drug-target interactions
3. Generate molecular fingerprints
4. Prepare data for Pinecone vector database

---

## ChEMBL Database Structure

### Key Tables

1. **`molecule_dictionary`**
   - Drug molecules
   - Fields: `molregno`, `pref_name`, `max_phase`

2. **`compound_structures`**
   - Chemical structures
   - Fields: `molregno`, `canonical_smiles`, `standard_inchi`

3. **`activities`**
   - Drug-target interactions
   - Fields: `molregno`, `assay_id`, `standard_value`, `standard_type`

4. **`assays`**
   - Assay information
   - Fields: `assay_id`, `tid` (target ID)

5. **`target_dictionary`**
   - Target information
   - Fields: `tid`, `pref_name`, `organism`, `target_type`

### Join Path

```
molecule_dictionary
  ↓ (molregno)
compound_structures
  ↓ (molregno)
activities
  ↓ (assay_id)
assays
  ↓ (tid)
target_dictionary
```

**Important:** The `activities` table doesn't have `tid` directly. Must join through `assays`.

---

## Key Functions

### 1. `connect_chembl(db_path)`

**Purpose:** Connect to ChEMBL SQLite database

**Input:**
- `db_path`: Path to ChEMBL database file

**Output:**
- SQLite connection object

**Error Handling:**
- Raises `FileNotFoundError` if database doesn't exist

---

### 2. `extract_drug_molecules(conn, limit=None)`

**Purpose:** Extract approved drugs from ChEMBL

**Input:**
- `conn`: SQLite connection
- `limit`: Maximum number of drugs to extract

**Output:**
- List of drug dictionaries:
  ```python
  {
      'molregno': 12345,
      'name': 'Paracetamol',
      'max_phase': 4,  # Approved
      'smiles': 'CC(=O)Nc1ccc(O)cc1',
      'inchi': 'InChI=1S/C8H9NO2/...',
      'inchi_key': 'RZVAJINKPMORJF-UHFFFAOYSA-N'
  }
  ```

**Query Logic:**
```sql
SELECT 
    m.molregno,
    m.pref_name,
    m.max_phase,
    cs.canonical_smiles,
    cs.standard_inchi,
    cs.standard_inchi_key
FROM molecule_dictionary m
JOIN compound_structures cs ON m.molregno = cs.molregno
WHERE 
    m.max_phase >= 2  -- Approved drugs only
    AND cs.canonical_smiles IS NOT NULL
    AND cs.canonical_smiles != ''
ORDER BY m.max_phase DESC, m.pref_name
LIMIT ?
```

**Filtering:**
- Only phase 2+ drugs (approved or in late-stage trials)
- Must have valid SMILES string
- Validates SMILES using RDKit

---

### 3. `extract_drug_targets(conn, molregno)`

**Purpose:** Extract target information for a drug

**Input:**
- `conn`: SQLite connection
- `molregno`: ChEMBL molecule registration number

**Output:**
- List of target dictionaries:
  ```python
  {
      'tid': 12345,
      'name': 'COX-1',
      'organism': 'Human',
      'type': 'SINGLE PROTEIN',
      'activity_type': 'IC50',
      'value': 0.5,
      'units': 'nM',
      'relation': '='
  }
  ```

**Query Logic:**
```sql
SELECT DISTINCT
    t.tid,
    t.pref_name,
    t.organism,
    t.target_type,
    act.standard_type,
    act.standard_value,
    act.standard_units,
    act.standard_relation
FROM activities act
JOIN assays a ON act.assay_id = a.assay_id
JOIN target_dictionary t ON a.tid = t.tid
WHERE 
    act.molregno = ?
    AND act.standard_value IS NOT NULL
    AND act.standard_type IN ('IC50', 'Ki', 'Kd', 'EC50', 'ED50')
ORDER BY act.standard_value ASC
LIMIT 10
```

**Key Points:**
- Joins through `assays` table (important!)
- Filters for meaningful activity types
- Returns top 10 targets (by potency)

---

### 4. `extract_side_effects(conn, molregno)`

**Purpose:** Infer side effects from CYP enzyme interactions

**Input:**
- `conn`: SQLite connection
- `molregno`: ChEMBL molecule registration number

**Output:**
- List of side effect descriptions

**Current Implementation:**
- Checks if drug targets CYP enzymes
- Infers potential drug-drug interactions
- Note: ChEMBL doesn't directly store side effects

**Query:**
```sql
SELECT DISTINCT t.pref_name
FROM activities act
JOIN assays a ON act.assay_id = a.assay_id
JOIN target_dictionary t ON a.tid = t.tid
WHERE act.molregno = ?
AND (t.pref_name LIKE '%CYP%' OR t.pref_name LIKE '%cytochrome%')
```

**Future Improvements:**
- Integrate with SIDER database
- Use MedDRA terminology
- Include contraindications

---

### 5. `prepare_drug_for_vector_db(drug, conn)`

**Purpose:** Prepare drug record for Pinecone ingestion

**Input:**
- `drug`: Drug dictionary from `extract_drug_molecules()`
- `conn`: SQLite connection

**Output:**
- Dictionary ready for Pinecone:
  ```python
  {
      'id': 'chembl_12345',
      'vector': [0.0, 1.0, 0.0, ..., 1.0],  # Float list (2048 dims)
      'metadata': {
          'name': 'Paracetamol',
          'smiles': 'CC(=O)Nc1ccc(O)cc1',
          'max_phase': 4,
          'targets': 'COX-1, COX-2',
          'known_side_effects': 'Interacts with: CYP2D6',
          'chembl_id': 'CHEMBL12345'
      }
  }
  ```

**Key Steps:**
1. Generate molecular fingerprint (using `get_drug_fingerprint()`)
2. **Convert to floats** (Pinecone requirement)
3. Extract targets (top 5)
4. Extract side effects
5. Build metadata dictionary

**Critical Fix:**
- Must convert integer fingerprint to floats
- Pinecone requires `float32` values
- Error: `Invalid type for variable '0'. Required value type is float`

---

### 6. `batch_extract_drugs(db_path, limit=1000, batch_size=100)`

**Purpose:** Extract drugs in batches for efficient processing

**Input:**
- `db_path`: Path to ChEMBL database
- `limit`: Maximum number of drugs
- `batch_size`: Drugs per batch (for progress tracking)

**Output:**
- List of drug records ready for Pinecone

**Process:**
1. Connect to database
2. Extract drug molecules
3. For each drug:
   - Generate fingerprint
   - Extract targets
   - Extract side effects
   - Prepare for vector DB
4. Return all records

**Progress Tracking:**
- Prints batch progress every 100 drugs
- Useful for large extractions

---

## Ingestion Script

### `scripts/ingest_chembl_to_pinecone.py`

**Purpose:** Ingest ChEMBL drugs into Pinecone

**Process:**
1. Check Pinecone API key
2. Verify index exists
3. Extract drugs from ChEMBL
4. Prepare for ingestion
5. Ingest in batches (100 vectors per batch)
6. Report statistics

**Usage:**
```bash
export PINECONE_API_KEY="your_key"
python scripts/ingest_chembl_to_pinecone.py
```

**Configuration:**
- Default limit: 1000 drugs
- Override: `export CHEMBL_LIMIT=5000`

---

## Database Path Resolution

### `find_chembl_db_path()`

**Purpose:** Find ChEMBL database in common locations

**Checked Paths:**
```python
[
    'data/chembl/chembl_34/chembl_34_sqlite/chembl_34.db',  # Extracted tar.gz
    'data/chembl/chembl_34_sqlite/chembl_34.db',
    'data/chembl/chembl_34.db',
    'data/chembl/chembl.db',
    '../data/chembl/chembl_34/chembl_34_sqlite/chembl_34.db',
    '../data/chembl/chembl_34_sqlite/chembl_34.db',
]
```

**Returns:**
- First existing path, or `None` if not found

---

## Common Issues and Fixes

### Issue 1: SQL Join Error

**Error:** `no such column: a.tid`

**Cause:** Attempting to join `activities` directly to `target_dictionary`

**Fix:** Join through `assays` table:
```sql
-- Wrong
activities → target_dictionary

-- Correct
activities → assays → target_dictionary
```

**Files Modified:** `src/chembl_processor.py`

---

### Issue 2: Type Error in Pinecone

**Error:** `Invalid type for variable '0'. Required value type is float`

**Cause:** Passing integer list to Pinecone

**Fix:** Convert to floats:
```python
fingerprint_float = [float(x) for x in fingerprint]
```

**Files Modified:** `src/chembl_processor.py`

---

### Issue 3: Database Not Found

**Error:** `ChEMBL database not found`

**Cause:** Database not extracted from tar.gz

**Fix:**
```bash
cd data/chembl
tar -xvzf chembl_34_sqlite.tar.gz -C data/chembl/
```

**Expected Path:** `data/chembl/chembl_34/chembl_34_sqlite/chembl_34.db`

---

## Performance

### Extraction Time

- **1000 drugs:** ~10-30 minutes
- **10,000 drugs:** ~2-5 hours
- Depends on:
  - Database size
  - Number of targets per drug
  - Fingerprint generation speed

### Optimization Tips

1. **Limit extraction:** Start with 1000 drugs
2. **Batch processing:** Process in chunks
3. **Parallel processing:** Can parallelize fingerprint generation
4. **Cache results:** Save extracted data to avoid re-extraction

---

## Testing

### Unit Tests

See `tests/validation_tests.py` for:
- Database connection tests
- Drug extraction tests
- Target extraction tests
- Vector preparation tests

### Quick Test

```bash
python -c "
from src.chembl_processor import find_chembl_db_path, connect_chembl, extract_drug_molecules
db_path = find_chembl_db_path()
conn = connect_chembl(db_path)
drugs = extract_drug_molecules(conn, limit=5)
print(f'Found {len(drugs)} drugs')
conn.close()
"
```

---

## Future Improvements

### 1. Extended Data Extraction

- Drug-drug interactions
- Contraindications
- Dosing information
- Clinical trial data

### 2. Better Side Effect Data

- Integrate SIDER database
- Use MedDRA terminology
- Include severity levels

### 3. Performance Optimization

- Parallel processing
- Incremental updates
- Caching mechanisms

---

## References

- **ChEMBL Database:** https://www.ebi.ac.uk/chembl/
- **ChEMBL Schema:** https://www.ebi.ac.uk/chembl/documentation/schema
- **Pinecone Documentation:** https://docs.pinecone.io/

---

*For setup instructions, see `docs/setup/vcf_chembl_setup.md`*
