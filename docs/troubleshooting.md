# SynthaTrial Troubleshooting Guide

Complete troubleshooting guide for common issues and their solutions.

> **⚠️ Safety disclaimer** — SynthaTrial is a **research prototype**. Outputs must not be used for clinical decision-making.

## Quick Diagnostics

### System Check

```bash
# Check environment
conda info --envs
conda activate synthatrial

# Check Python version
python --version  # Should be 3.10+

# Verify key packages
python -c "import rdkit, pandas, pinecone; print('All packages OK')"

# Check API keys
echo $GOOGLE_API_KEY
echo $PINECONE_API_KEY

# Verify data files
ls -la data/chembl/chembl_34_sqlite/chembl_34.db
ls -la data/genomes/*.vcf.gz
```

### Quick Integration Test

```bash
python tests/quick_test.py
```

### Evaluation benchmark (no VCF required)

```bash
python main.py --benchmark cpic_examples.json
```

Expect a table of predicted vs expected phenotype and an overall match %. If the API or UI are used, ensure the backend returns `similar_drugs_used`, `genetics_summary`, and `context_sources` for RAG transparency.

---

## Installation Issues

### RDKit Installation Problems

**Error**: `ModuleNotFoundError: No module named 'rdkit'`

**Solutions**:

1. **Use Conda (Recommended)**:
   ```bash
   conda activate synthatrial
   conda install -c conda-forge rdkit -y
   ```

2. **Verify Installation**:
   ```bash
   python -c "from rdkit import Chem; print('RDKit installed!')"
   ```

3. **If Still Failing**:
   ```bash
   # Create fresh environment
   conda create -n synthatrial-new python=3.10 -y
   conda activate synthatrial-new
   conda install -c conda-forge rdkit pandas scipy scikit-learn -y
   ```

**Why Conda**: RDKit has complex binary dependencies that conda handles better than pip.

### Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'X'`

**Solutions**:

```bash
# Install missing packages
pip install python-dotenv streamlit langchain langchain-google-genai pinecone-client

# Or install all requirements
pip install -r requirements.txt
```

### Environment Issues

**Error**: Wrong Python version or packages not found

**Solutions**:

```bash
# Activate correct environment
conda activate synthatrial

# Verify environment
which python
python --version

# List installed packages
conda list
```

---

## API Key Issues

### Google API Key Problems

**Error**: `GOOGLE_API_KEY not found` or `API key invalid`

**Solutions**:

1. **Set API Key**:
   ```bash
   # Option 1: Environment variable
   export GOOGLE_API_KEY="your-api-key"

   # Option 2: .env file
   echo "GOOGLE_API_KEY=your-api-key" >> .env
   ```

2. **Verify API Key**:
   ```bash
   python -c "import os; print('API Key:', os.getenv('GOOGLE_API_KEY')[:10] + '...')"
   ```

3. **Test API Connection**:
   ```bash
   python scripts/list_models_v2.py
   ```

### Pinecone API Key Issues

**Error**: `Index not found` or `Pinecone connection failed`

**Solutions**:

1. **Set API Key** (Optional - system uses mock data if not set):
   ```bash
   export PINECONE_API_KEY="your-api-key"
   ```

2. **Create Index**:
   ```bash
   python scripts/setup_pinecone_index.py
   ```

3. **Verify Connection**:
   ```bash
   python -c "
   from src.vector_search import find_similar_drugs
   from src.input_processor import get_drug_fingerprint
   fp = get_drug_fingerprint('CC(=O)Nc1ccc(O)cc1')
   drugs = find_similar_drugs(fp)
   print(f'Found {len(drugs)} similar drugs')
   "
   ```

---

## VCF File Issues

### VCF File Not Found

**Error**: `VCF file not found` or `FileNotFoundError`

**Solutions**:

1. **Check File Exists**:
   ```bash
   ls -lh data/genomes/*.vcf.gz
   ```

2. **Download Missing Files**:
   ```bash
   mkdir -p data/genomes

   # Chromosome 22 (CYP2D6)
   curl -L https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
     -o data/genomes/chr22.vcf.gz

   # Chromosome 10 (CYP2C19, CYP2C9)
   curl -L https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
     -o data/genomes/chr10.vcf.gz
   ```

### VCF File Corruption

**Error**: `gzip: unexpected end of file` or `No samples found`

**Symptoms**:
- File size too small
- Cannot read file
- Gzip test fails

**Solutions**:

1. **Check File Integrity**:
   ```bash
   python scripts/check_vcf_integrity.py data/genomes/chr22.vcf.gz
   ```

2. **Test Gzip Integrity**:
   ```bash
   gzip -t data/genomes/chr22.vcf.gz && echo "OK" || echo "CORRUPTED"
   ```

3. **Re-download if Corrupted**:
   ```bash
   # Delete corrupted file
   rm data/genomes/chr22.vcf.gz

   # Re-download with resume capability
   wget -c https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
     -O data/genomes/chr22.vcf.gz
   ```

### Expected File Sizes

| Chromosome | Expected Size | File Pattern |
|------------|---------------|--------------|
| Chr 22 | ~200 MB | `chr22.vcf.gz` |
| Chr 10 | ~700 MB | `chr10.vcf.gz` |

### VCF Download Issues

**Issue**: Download interrupted or very slow

**Solutions**:

1. **Resume Download**:
   ```bash
   cd data/genomes/
   wget -c https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz
   ```

2. **Background Download**:
   ```bash
   nohup wget -c <url> > download.log 2>&1 &
   ```

3. **Check Progress**:
   ```bash
   watch -n 5 'ls -lh data/genomes/chr10.vcf.gz'
   ```

### No Variants Found

**Error**: `No variants found in CYP2D6 region`

**Causes & Solutions**:

1. **Normal for Some Samples**: CYP gene regions are small, some samples may have no variants
   ```bash
   # Try different sample ID
   python main.py --vcf data/genomes/chr22.vcf.gz --sample-id HG00097
   ```

2. **Wrong Chromosome**: Ensure VCF file contains correct chromosome
   ```bash
   zcat data/genomes/chr22.vcf.gz | head -20 | grep "^#CHROM"
   ```

3. **Check Available Samples**:
   ```bash
   python -c "
   from src.vcf_processor import get_sample_ids_from_vcf
   samples = get_sample_ids_from_vcf('data/genomes/chr22.vcf.gz', limit=10)
   print('Available samples:', samples)
   "
   ```

---

## Database Issues

### ChEMBL Database Problems

**Error**: `ChEMBL database not found`

**Solutions**:

1. **Extract Database**:
   ```bash
   cd data/chembl
   tar -xvzf chembl_34_sqlite.tar.gz
   ```

2. **Verify Extraction**:
   ```bash
   ls -la data/chembl/chembl_34_sqlite/chembl_34.db
   ```

3. **Test Database Connection**:
   ```bash
   sqlite3 data/chembl/chembl_34_sqlite/chembl_34.db "SELECT COUNT(*) FROM molecule_dictionary;"
   ```

**Expected Path Structure**:
```
data/chembl/
  └── chembl_34_sqlite/
      └── chembl_34.db
```

### SQL Errors

**Error**: `sqlite3.OperationalError: no such column: a.tid`

**Cause**: Incorrect SQL join path in ChEMBL queries

**Solution**: This is fixed in the current implementation. If you encounter this:
```bash
git pull  # Get latest fixes
```

**Technical Details**: Must join `activities` → `assays` → `target_dictionary`, not directly.

---

## Vector Database Issues

### Pinecone Index Issues

**Error**: `Index 'drug-index' not found`

**Solutions**:

1. **Automated Setup**:
   ```bash
   python scripts/setup_pinecone_index.py
   ```

2. **Manual Setup**:
   - Go to https://app.pinecone.io/
   - Create index: `drug-index`
   - Dimensions: `2048`
   - Metric: `cosine`

3. **Verify Index**:
   ```bash
   python -c "
   from pinecone import Pinecone
   import os
   pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
   index = pc.Index('drug-index')
   print('Index ready!')
   "
   ```

### Mock Data vs Real Data

**Issue**: Getting "Mock Drug A/B/C" instead of real drug names

**Cause**: Pinecone API key not set or index empty

**Solutions**:

1. **Set API Key**:
   ```bash
   export PINECONE_API_KEY="your-key"
   ```

2. **Populate Index**:
   ```bash
   python scripts/ingest_chembl_to_pinecone.py
   ```

3. **Verify Data**:
   ```bash
   python -c "
   from pinecone import Pinecone
   import os
   pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
   index = pc.Index('drug-index')
   stats = index.describe_index_stats()
   print(f'Vectors in index: {stats.total_vector_count}')
   "
   ```

**Note**: Mock data is fine for testing - the system works correctly either way.

---

## Performance Issues

### Slow VCF Processing

**Issue**: VCF processing takes very long

**Normal Performance**:
- Chromosome 22: 1-3 minutes
- Chromosome 10: 3-8 minutes

**Solutions**:

1. **Use Sample Limits for Testing**:
   ```python
   # In code, limit samples for faster testing
   variants = extract_cyp_variants(vcf_path, gene, sample_limit=1)
   ```

2. **Check File Size**:
   ```bash
   ls -lh data/genomes/*.vcf.gz
   ```

3. **Monitor Progress**:
   - Look for "Found X variants..." messages
   - Processing is working if messages appear

### Slow LLM Responses

**Issue**: LLM simulation takes very long or times out

**Solutions**:

1. **Check Internet Connection**:
   ```bash
   ping google.com
   ```

2. **Verify API Key**:
   ```bash
   python scripts/list_models_v2.py
   ```

3. **Try Different Model**:
   ```bash
   export GEMINI_MODEL="gemini-1.5-flash"  # Faster model
   ```

4. **Check API Quotas**: Visit Google AI Studio to check usage limits

---

## Application Errors

### Streamlit Issues

**Error**: `StreamlitAPIException: st.session_state.X cannot be modified`

**Cause**: Session state key conflicts with widget keys

**Solution**: This is fixed in current version. If you encounter this:
```bash
git pull  # Get latest fixes
```

### Import Errors

**Error**: `ImportError: cannot import name 'X' from 'Y'`

**Solutions**:

1. **Check Module Structure**:
   ```bash
   ls -la src/
   ```

2. **Verify __init__.py Files**:
   ```bash
   touch src/__init__.py
   touch tests/__init__.py
   ```

3. **Check Python Path**:
   ```bash
   python -c "import sys; print(sys.path)"
   ```

---

## Testing and Validation

### Test Failures

**Issue**: Validation tests fail

**Solutions**:

1. **Run Individual Tests**:
   ```bash
   python tests/quick_test.py
   python tests/validation_tests.py
   ```

2. **Check Prerequisites**:
   ```bash
   # Ensure all data files exist
   ls -la data/chembl/chembl_34_sqlite/chembl_34.db
   ls -la data/genomes/*.vcf.gz
   ```

3. **Check API Keys**:
   ```bash
   python -c "import os; print('GOOGLE_API_KEY set:', bool(os.getenv('GOOGLE_API_KEY')))"
   ```

### Validation Errors

**Issue**: Known test cases fail

**Debugging Steps**:

1. **Enable Debug Logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Test Individual Components**:
   ```bash
   # Test fingerprint generation
   python -c "from src.input_processor import get_drug_fingerprint; print(len(get_drug_fingerprint('CC(=O)Nc1ccc(O)cc1')))"

   # Test vector search
   python -c "from src.vector_search import find_similar_drugs; from src.input_processor import get_drug_fingerprint; print(find_similar_drugs(get_drug_fingerprint('CC(=O)Nc1ccc(O)cc1')))"
   ```

3. **Check Expected vs Actual Results**:
   - Compare risk levels with CPIC guidelines
   - Verify metabolizer status inference

---

## Common Error Messages

### "No module named 'X'"

**Quick Fix**:
```bash
conda activate synthatrial
pip install X
```

### "File not found"

**Quick Fix**:
```bash
# Check file paths
ls -la data/
# Download missing files (see setup guide)
```

### "API key not found"

**Quick Fix**:
```bash
export GOOGLE_API_KEY="your-key"
# Or add to .env file
```

### "Index not found"

**Quick Fix**:
```bash
python scripts/setup_pinecone_index.py
```

### "Permission denied"

**Quick Fix**:
```bash
chmod +x scripts/*.py
# Or run with python explicitly
python scripts/script_name.py
```

---

## Getting Help

### Debug Information to Collect

When reporting issues, include:

1. **System Information**:
   ```bash
   python --version
   conda --version
   uname -a  # Linux/Mac
   ```

2. **Environment Information**:
   ```bash
   conda list
   pip list
   ```

3. **File Status**:
   ```bash
   ls -la data/chembl/
   ls -la data/genomes/
   ```

4. **Error Messages**: Full error traceback

5. **Steps to Reproduce**: Exact commands that caused the error

### Self-Help Checklist

Before asking for help:

- ✅ Activated correct conda environment
- ✅ Verified API keys are set
- ✅ Checked file paths exist
- ✅ Ran quick integration test
- ✅ Checked this troubleshooting guide
- ✅ Tried suggested solutions

### Additional Resources

- [Setup Guide](setup.md) - Installation instructions
- [Usage Guide](usage.md) - How to use the system
- [Implementation Guide](implementation.md) - Technical details
- Validation tests: `python tests/validation_tests.py`

---

## Prevention Tips

1. **Always activate conda environment** before running scripts
2. **Verify downloads** with integrity checker
3. **Test with small datasets** before full runs
4. **Keep backups** of working configurations
5. **Update regularly** to get latest fixes
6. **Monitor logs** for early warning signs

---

*For additional help, check the implementation guides or run the validation test suite.*
