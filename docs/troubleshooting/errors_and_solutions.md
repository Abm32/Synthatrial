# Errors and Solutions

This document catalogs all errors encountered during development and their solutions.

## Table of Contents
- [Streamlit UI Errors](#streamlit-ui-errors)
- [Database and SQL Errors](#database-and-sql-errors)
- [Vector Database Errors](#vector-database-errors)
- [Environment and Dependency Errors](#environment-and-dependency-errors)
- [VCF Processing Errors](#vcf-processing-errors)
- [ChEMBL Processing Errors](#chembl-processing-errors)

---

## Streamlit UI Errors

### Error: `StreamlitAPIException: st.session_state.smiles_input cannot be modified after the widget is instantiated`

**Error Message:**
```
streamlit.errors.StreamlitAPIException: st.session_state.smiles_input cannot be modified after the widget with key smiles_input is instantiated.
```

**Cause:**
- Directly assigning to `st.session_state.smiles_input` after creating a widget with the same key
- Streamlit doesn't allow modifying session state keys that are used by widgets in the same render cycle

**Solution:**
1. Use separate keys for widget values vs. example data:
   - Widget keys: `smiles_input`, `drug_name`
   - Example data keys: `example_smiles`, `example_drug`
2. Use default values from session state, not direct assignment:
   ```python
   # ❌ WRONG
   st.text_input("SMILES", key="smiles_input")
   st.session_state.smiles_input = "new_value"  # Error!
   
   # ✅ CORRECT
   default_smiles = st.session_state.get("example_smiles", "")
   st.text_input("SMILES", value=default_smiles, key="smiles_input")
   ```
3. Update example data, then call `st.rerun()`:
   ```python
   if st.button("Load Example"):
       st.session_state.example_smiles = "CC(=O)Nc1ccc(O)cc1"
       st.rerun()
   ```

**Files Modified:**
- `app.py` - Fixed session state handling for example buttons

**Reference:**
- Streamlit Session State API: https://docs.streamlit.io/library/api-reference/session-state

---

## Database and SQL Errors

### Error: `sqlite3.OperationalError: no such column: a.tid`

**Error Message:**
```
sqlite3.OperationalError: no such column: a.tid
```

**Cause:**
- Attempting to join `activities` table directly to `target_dictionary` using `tid`
- The `activities` table doesn't have a `tid` column directly
- Must join through the `assays` table first

**Solution:**
Update SQL queries to use the correct join path:
```sql
-- ❌ WRONG
SELECT * FROM activities a
JOIN target_dictionary t ON a.tid = t.tid

-- ✅ CORRECT
SELECT * FROM activities act
JOIN assays a ON act.assay_id = a.assay_id
JOIN target_dictionary t ON a.tid = t.tid
```

**Files Modified:**
- `src/chembl_processor.py` - Fixed `extract_drug_targets()` and `extract_side_effects()`

**ChEMBL Schema Understanding:**
- `activities` → `assays` (via `assay_id`)
- `assays` → `target_dictionary` (via `tid`)
- This is the correct join path for drug-target relationships

---

## Vector Database Errors

### Error: `Invalid type for variable '0'. Required value type is float and passed type was int`

**Error Message:**
```
ERROR ingesting batch 1: Invalid type for variable '0'. Required value type is float and passed type was int at ['values'][0]
```

**Cause:**
- Pinecone requires float values for vectors
- Morgan fingerprints return integers (0s and 1s)
- Directly passing integer list to Pinecone causes type error

**Solution:**
Convert fingerprint list to floats before ingestion:
```python
# ❌ WRONG
fingerprint = get_drug_fingerprint(smiles)  # Returns List[int]
return {'vector': fingerprint}  # Error: integers not allowed

# ✅ CORRECT
fingerprint = get_drug_fingerprint(smiles)  # Returns List[int]
fingerprint_float = [float(x) for x in fingerprint]  # Convert to floats
return {'vector': fingerprint_float}  # Success
```

**Files Modified:**
- `src/chembl_processor.py` - Added float conversion in `prepare_drug_for_vector_db()`

**Why This Matters:**
- Pinecone's vector database requires float32 values
- Integer vectors would cause type mismatch errors
- Float conversion preserves the binary nature (0.0 vs 1.0) while meeting API requirements

---

### Error: `Index 'drug-index' not found`

**Error Message:**
```
⚠️  Index 'drug-index' not found!
```

**Cause:**
- Pinecone index hasn't been created yet
- Index name mismatch
- API key not set correctly

**Solution:**
1. **Automated Setup (Recommended):**
   ```bash
   python setup_pinecone_index.py
   ```

2. **Manual Setup:**
   - Go to https://app.pinecone.io/
   - Create index: `drug-index`
   - Dimensions: `2048`
   - Metric: `cosine`

3. **Verify API Key:**
   ```bash
   export PINECONE_API_KEY="your_key_here"
   ```

**Files Created:**
- `setup_pinecone_index.py` - Automated index creation script

**Reference:**
- See `docs/setup/pinecone_setup.md` for detailed setup instructions

---

## Environment and Dependency Errors

### Error: `ModuleNotFoundError: No module named 'rdkit'`

**Error Message:**
```
ModuleNotFoundError: No module named 'rdkit'
```

**Cause:**
- RDKit not installed in current environment
- Wrong conda environment activated
- RDKit installation failed

**Solution:**
1. **Activate correct conda environment:**
   ```bash
   conda activate synthatrial
   ```

2. **Install RDKit:**
   ```bash
   conda install -c conda-forge rdkit
   ```

3. **Verify installation:**
   ```bash
   python -c "from rdkit import Chem; print('RDKit installed!')"
   ```

**Why Conda:**
- RDKit has complex binary dependencies
- Conda handles these better than pip
- Recommended installation method for RDKit

---

### Error: `ModuleNotFoundError: No module named 'pandas'`

**Error Message:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Cause:**
- Pandas not installed
- Unused import causing error (if pandas not needed)

**Solution:**
1. **If pandas is needed:**
   ```bash
   conda install pandas
   # or
   pip install pandas
   ```

2. **If pandas is not needed:**
   - Remove unused import from code
   - Example: Removed `import pandas as pd` from `src/vcf_processor.py`

**Files Modified:**
- `src/vcf_processor.py` - Removed unused pandas import

---

## VCF Processing Errors

### Error: `ChEMBL database not found`

**Error Message:**
```
ERROR: ChEMBL database not found!
```

**Cause:**
- ChEMBL tar.gz file not extracted
- Wrong file path
- Database file missing

**Solution:**
1. **Extract ChEMBL database:**
   ```bash
   cd data/chembl
   tar -xvzf chembl_34_sqlite.tar.gz -C data/chembl/
   ```

2. **Verify extraction:**
   ```bash
   ls -la data/chembl/chembl_34/chembl_34_sqlite/chembl_34.db
   ```

3. **Check path in code:**
   - The `find_chembl_db_path()` function checks multiple possible locations
   - Ensure database is in one of the expected paths

**Files Modified:**
- `src/chembl_processor.py` - Updated `find_chembl_db_path()` to check correct extraction path

**Expected Path Structure:**
```
data/chembl/
  └── chembl_34/
      └── chembl_34_sqlite/
          └── chembl_34.db
```

---

### Error: `VCF file not found` or `No variants found in CYP2D6 region`

**Error Message:**
```
ERROR: VCF file not found
# or
WARNING: No variants found in CYP2D6 region
```

**Cause:**
- VCF file not downloaded
- Wrong file path
- CYP2D6 region may have no variants (normal for some samples)

**Solution:**
1. **Download VCF file:**
   ```bash
   mkdir -p data/genomes
   curl -L https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
     -o data/genomes/chr22.vcf.gz
   ```

2. **Verify file exists:**
   ```bash
   ls -lh data/genomes/*.vcf.gz
   ```

3. **For "no variants" warning:**
   - This may be normal - CYP2D6 region is small
   - Try different sample IDs
   - Check if VCF file contains chromosome 22 data

**CYP Gene Regions:**
- CYP2D6: Chr22 (42522500-42530900)
- CYP2C19: Chr10 (96541615-96561468)
- CYP3A4: Chr7 (99376140-99391055)

---

## ChEMBL Processing Errors

### Error: `No drugs extracted from ChEMBL`

**Error Message:**
```
ERROR: No drugs extracted from ChEMBL
```

**Cause:**
- Database connection failed
- SQL query returned no results
- Database file corrupted
- Wrong database version

**Solution:**
1. **Verify database connection:**
   ```bash
   sqlite3 data/chembl/chembl_34/chembl_34_sqlite/chembl_34.db "SELECT COUNT(*) FROM molecule_dictionary;"
   ```

2. **Check query filters:**
   - Current query filters for `max_phase >= 2` (approved drugs)
   - May need to adjust filter if no results

3. **Verify database integrity:**
   ```bash
   sqlite3 data/chembl/chembl_34/chembl_34_sqlite/chembl_34.db "PRAGMA integrity_check;"
   ```

**Query Details:**
- Filters for approved drugs (phase 2+)
- Requires valid SMILES strings
- Skips invalid molecules

---

## General Debugging Tips

### 1. Check Environment
```bash
# Verify conda environment
conda info --envs
conda activate synthatrial

# Check Python version
python --version  # Should be 3.10

# Verify key packages
python -c "import rdkit, pandas, pinecone; print('All packages OK')"
```

### 2. Check API Keys
```bash
# Verify environment variables
echo $GOOGLE_API_KEY
echo $PINECONE_API_KEY

# Or check .env file
cat .env
```

### 3. Check File Paths
```bash
# Verify data files exist
ls -la data/chembl/chembl_34/chembl_34_sqlite/chembl_34.db
ls -la data/genomes/*.vcf.gz
```

### 4. Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 5. Test Individual Components
```bash
# Test VCF processing
python -c "from src.vcf_processor import *; print('VCF OK')"

# Test ChEMBL processing
python -c "from src.chembl_processor import *; print('ChEMBL OK')"

# Test vector search
python -c "from src.vector_search import *; print('Vector search OK')"
```

---

## Error Prevention Best Practices

1. **Always activate conda environment before running scripts**
2. **Verify API keys are set before running ingestion scripts**
3. **Check file paths match expected locations**
4. **Run validation tests after major changes**
5. **Keep error logs for debugging**
6. **Test with small datasets first (limit=10) before full runs**

---

## Getting Help

If you encounter an error not listed here:

1. Check the relevant module's documentation
2. Review the implementation guides in `docs/implementation/`
3. Run validation tests: `python tests/validation_tests.py`
4. Check logs for detailed error messages
5. Verify all prerequisites are met (see `docs/setup/`)

---

## Summary of All Fixes Applied

| Error | File Modified | Solution |
|-------|--------------|----------|
| StreamlitAPIException | `app.py` | Fixed session state handling |
| SQL join error | `src/chembl_processor.py` | Fixed SQL joins through assays table |
| Pinecone type error | `src/chembl_processor.py` | Convert integers to floats |
| RDKit not found | Environment | Use conda install |
| Pandas not found | `src/vcf_processor.py` | Removed unused import |
| ChEMBL path error | `src/chembl_processor.py` | Updated path checking |
| Index not found | Created `setup_pinecone_index.py` | Automated index creation |

---

*Last Updated: After VCF/ChEMBL implementation*
