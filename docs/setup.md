# SynthaTrial Setup Guide

Complete setup guide for the SynthaTrial pharmacogenomics platform.

> **⚠️ Safety disclaimer** — SynthaTrial is a **research prototype**. Outputs are synthetic predictions and must not be used for clinical decision-making. Not medical advice.

## Quick Start

### 1. Activate Environment
```bash
conda activate synthatrial
# Or create new environment:
# conda create -n synthatrial python=3.10 -y
# conda activate synthatrial
```

### 2. Install Dependencies
```bash
# Install RDKit (required for molecular fingerprints)
conda install -c conda-forge rdkit -y

# Install other dependencies
pip install pandas scipy scikit-learn langchain langchain-openai pinecone-client langchain-google-genai psycopg2-binary python-dotenv streamlit
```

### 3. Set API Keys
Create a `.env` file in the project root:
```bash
GOOGLE_API_KEY="your_google_api_key"
PINECONE_API_KEY="your_pinecone_api_key"
```

### 4. Quick Test (Big 3 Enzymes - Recommended)
```bash
# Download VCF files (optional - for real genetic data). Use v5b (EBI); see docs/VCF_CHROMOSOME_SET.md.
python scripts/data_initializer.py --vcf chr22 chr10
# Or manually: mkdir -p data/genomes && curl -L -o data/genomes/chr22.vcf.gz \
#   https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz

# Test with Warfarin (CYP2C9 substrate). App auto-discovers VCFs in data/genomes.
python main.py --drug-name Warfarin --drug-smiles "CC(=O)CC(c1ccc(OC)cc1)c1c(O)c2ccccc2oc1=O"
# Or with explicit paths: python main.py --vcf data/genomes/chr22.vcf.gz --vcf-chr10 data/genomes/chr10.vcf.gz --drug-name Warfarin

# Optional: run evaluation benchmark (no VCF needed)
python main.py --benchmark cpic_examples.json

# Optional: start API for Streamlit UI backend
python api.py   # default port 8000
```

---

## Prerequisites

- **Python 3.10+**
- **Conda** (required for RDKit installation)
- **API Keys**: Google API Key (required), Pinecone API Key (optional)

---

## Step 1: Environment Setup

### Create Conda Environment

```bash
# Create conda environment (required for RDKit)
conda create -n synthatrial python=3.10 -y
conda activate synthatrial

# Install RDKit via conda (required)
conda install -c conda-forge rdkit pandas scipy scikit-learn -y

# Install other dependencies via pip
pip install langchain langchain-google-genai pinecone-client python-dotenv streamlit
```

### Alternative: pip-only Installation

```bash
pip install -r requirements.txt
```

**Note**: RDKit installation via pip often fails. Conda is strongly recommended.

---

## Step 2: API Keys Configuration

Create a `.env` file in the project root:

```bash
GOOGLE_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key  # Optional (mock mode if missing)
PINECONE_INDEX=drug-index
GEMINI_MODEL=gemini-2.5-flash  # Optional, defaults to gemini-2.5-flash
```

**Or export in terminal:**
```bash
export GOOGLE_API_KEY="your_google_api_key"
export PINECONE_API_KEY="your_pinecone_api_key"
```

### API Key Requirements

- **GOOGLE_API_KEY**: **Required** for LLM simulation
- **PINECONE_API_KEY**: **Optional** (system uses mock data if not set)

---

## Step 3: Data Setup

### VCF Files (Genomic Data)

Download VCF files from 1000 Genomes Project:

```bash
mkdir -p data/genomes

# Chromosome 22 (CYP2D6) - Required
curl -L https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  -o data/genomes/chr22.vcf.gz

# Chromosome 10 (CYP2C19, CYP2C9) - Optional but recommended for "Big 3" enzymes
curl -L https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  -o data/genomes/chr10.vcf.gz
```

**File Sizes**:
- Chromosome 22: ~200 MB
- Chromosome 10: ~700 MB

### ChEMBL Database (Optional)

```bash
mkdir -p data/chembl
curl -L https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_34/chembl_34_sqlite.tar.gz \
  -o data/chembl/chembl_34_sqlite.tar.gz
tar -xvzf data/chembl/chembl_34_sqlite.tar.gz -C data/chembl/
```

### Pinecone Index Setup

Run the automated setup script:

```bash
# Make sure PINECONE_API_KEY is set
python scripts/setup_pinecone_index.py
```

**Manual Setup** (if preferred):
1. Go to https://app.pinecone.io/
2. Create index:
   - **Name**: `drug-index`
   - **Dimensions**: `2048`
   - **Metric**: `cosine`

### Populate Pinecone with ChEMBL Data (Optional)

```bash
# Ingest ChEMBL drugs into Pinecone (takes 10-30 minutes)
python scripts/ingest_chembl_to_pinecone.py

# To ingest more drugs:
export CHEMBL_LIMIT=5000
python scripts/ingest_chembl_to_pinecone.py
```

---

## Step 4: Verification

### Quick Integration Test

```bash
python tests/quick_test.py
```

### Full Validation Suite

```bash
python tests/validation_tests.py
```

### Test VCF Processing

```bash
python -c "
from src.vcf_processor import get_sample_ids_from_vcf
samples = get_sample_ids_from_vcf('data/genomes/chr22.vcf.gz', limit=5)
print(f'Found {len(samples)} samples: {samples}')
"
```

### Verify Pinecone Connection

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

## Step 5: Running the Application

### Streamlit Web Interface (Recommended)

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

### Command Line Interface

#### Single Chromosome (CYP2D6 only)

```bash
python main.py --vcf data/genomes/chr22.vcf.gz --drug-name Codeine
```

#### Multiple Chromosomes (Big 3 enzymes: CYP2D6, CYP2C19, CYP2C9)

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --vcf-chr10 data/genomes/chr10.vcf.gz \
  --drug-name Warfarin
```

#### Manual Patient Profile (No VCF)

```bash
python main.py --cyp2d6-status poor_metabolizer --drug-name Tramadol
```

---

## Example Test Cases

### Test Case 1: Codeine (CYP2D6 substrate)

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --drug-name Codeine \
  --drug-smiles "CN1CC[C@]23C4=C5C=CC(=C4O)Oc4c5c(C[C@@H]1[C@@H]2C=C[C@@H]3O)cc(c4)O"
```

**Expected**: High risk for poor CYP2D6 metabolizers (no conversion to active morphine)

### Test Case 2: Warfarin (CYP2C9 substrate) - Big 3 Enzymes

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --vcf-chr10 data/genomes/chr10.vcf.gz \
  --drug-name Warfarin \
  --drug-smiles "CC(=O)CC(c1ccc(OC)cc1)c1c(O)c2ccccc2oc1=O" \
  --sample-id HG00096
```

**Expected**: High risk for poor CYP2C9 metabolizers (increased bleeding risk)

### Test Case 3: Clopidogrel (CYP2C19 substrate) - Big 3 Enzymes

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --vcf-chr10 data/genomes/chr10.vcf.gz \
  --drug-name Clopidogrel \
  --drug-smiles "CC(=O)N[C@@H]1CCc2ccccc2[C@H]1c1ccc(Cl)cc1" \
  --sample-id HG00096
```

**Expected**: Medium risk for poor CYP2C19 metabolizers (reduced activation)

---

## Command-Line Arguments Reference

| Argument | Description | Example |
|----------|-------------|---------|
| `--vcf` | Path to chromosome 22 VCF file (CYP2D6) | `data/genomes/chr22.vcf.gz` |
| `--vcf-chr10` | Path to chromosome 10 VCF file (CYP2C19, CYP2C9) | `data/genomes/chr10.vcf.gz` |
| `--drug-name` | Name of the drug | `Warfarin` |
| `--drug-smiles` | SMILES string of the drug | `CC(=O)Nc1ccc(O)cc1` |
| `--sample-id` | Specific sample ID from VCF (optional) | `HG00096` |
| `--cyp2d6-status` | Manual CYP2D6 status (if not using VCF) | `poor_metabolizer` |

**Metabolizer Status Options:**
- `extensive_metabolizer` (normal)
- `intermediate_metabolizer` (reduced function)
- `poor_metabolizer` (no function)
- `ultra_rapid_metabolizer` (increased function)

---

## Enzyme Coverage

| Enzyme | Chromosome | Key Drugs Metabolized | Clinical Impact |
|--------|------------|----------------------|-----------------|
| **CYP2D6** | 22 | Codeine, Tramadol, Metoprolol, Antidepressants | ~25% of drugs |
| **CYP2C19** | 10 | Clopidogrel (Plavix), Omeprazole, PPIs | Antiplatelet, GI drugs |
| **CYP2C9** | 10 | Warfarin, Ibuprofen, Phenytoin, NSAIDs | Anticoagulation, pain management |

**Combined Coverage**: Big 3 enzymes cover ~60-70% of clinically used drugs

---

## Troubleshooting

### Installation Issues

**Issue**: "ModuleNotFoundError: No module named 'rdkit'"
```bash
# Solution: Install RDKit via conda
conda install -c conda-forge rdkit -y
```

**Issue**: "ModuleNotFoundError: No module named 'dotenv'"
```bash
# Solution: Install python-dotenv
pip install python-dotenv
```

### API Key Issues

**Issue**: "GOOGLE_API_KEY not found"
```bash
# Solution: Set the API key
export GOOGLE_API_KEY="your-key"
# Or add to .env file
echo "GOOGLE_API_KEY=your-key" >> .env
```

### VCF File Issues

**Issue**: "VCF file not found"
```bash
# Solution: Check file paths and ensure VCF files are downloaded
ls -lh data/genomes/*.vcf.gz
```

**Issue**: "No samples found in VCF file"
```bash
# Solution: Check VCF file integrity
python scripts/check_vcf_integrity.py data/genomes/chr22.vcf.gz
```

### Pinecone Issues

**Issue**: "Index not found"
```bash
# Solution: Run setup script
python scripts/setup_pinecone_index.py
```

**Issue**: "Invalid dimension"
```bash
# Solution: Index must have exactly 2048 dimensions
# Delete and recreate through setup script
```

---

## Performance Notes

- **VCF Processing**: ~1-5 minutes per chromosome
- **ChEMBL Extraction**: ~10-30 minutes for 1000 drugs
- **Pinecone Ingestion**: ~5-15 minutes for 1000 drugs
- **Vector Search**: <200ms per query
- **LLM Simulation**: ~3-10 seconds per patient

---

## Next Steps

1. ✅ Complete environment setup
2. ✅ Configure API keys
3. ✅ Download data files
4. ✅ Run validation tests
5. ✅ Test with example drugs
6. ✅ Compare single vs. multi-chromosome results

---

## Additional Scripts

### Check VCF File Integrity
```bash
python scripts/check_vcf_integrity.py data/genomes/chr10.vcf.gz
```

### Test Chromosome 10 Integration
```bash
python scripts/test_chromosome10.py
```

### Generate Validation Results
```bash
python scripts/generate_validation_results.py
```

### Benchmark Performance
```bash
python scripts/benchmark_performance.py
```

### List Available Gemini Models
```bash
python scripts/list_models.py
python scripts/list_models_v2.py
```

---

## Resources

- **1000 Genomes Project**: https://www.internationalgenome.org/
- **ChEMBL Database**: https://www.ebi.ac.uk/chembl/
- **Pinecone**: https://www.pinecone.io/
- **RDKit**: https://www.rdkit.org/
- **CPIC Guidelines**: https://cpicpgx.org/
- **PharmVar**: https://www.pharmvar.org/
