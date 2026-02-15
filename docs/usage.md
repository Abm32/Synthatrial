# SynthaTrial Usage Guide

Complete guide for using the SynthaTrial pharmacogenomics platform.

> **⚠️ Safety disclaimer** — SynthaTrial is a **research prototype**. Outputs are synthetic predictions and must not be used for clinical decision-making. Not medical advice.

## Quick Start

### Web Interface (Recommended)

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501` for the interactive web interface with:
- Modern gradient UI and safety disclaimer
- Patient profile builder (genetics: CYP2D6, CYP2C19, CYP2C9, UGT1A1, SLCO1B1)
- **Prediction context panel**: shows similar drugs used, genetics summary, and data sources (ChEMBL/Pinecone or mock)
- Example drug cases and real-time validation

**Backend API** (optional): Run `python api.py` (or uvicorn) so the UI can call `/analyze`; the response includes `similar_drugs_used`, `genetics_summary`, and `context_sources` for transparency.

### Command Line Interface

```bash
# Basic usage with VCF file
python main.py --vcf data/genomes/chr22.vcf.gz --drug-name Codeine

# Multi-chromosome (Big 3 enzymes)
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --vcf-chr10 data/genomes/chr10.vcf.gz \
  --drug-name Warfarin

# Manual patient profile
python main.py --cyp2d6-status poor_metabolizer --drug-name Tramadol

# Evaluation mode (CPIC-style benchmark: predicted vs expected phenotype, match %)
python main.py --benchmark cpic_examples.json
```

**Note:** If VCFs exist in `data/genomes/`, you can omit `--vcf` and `--vcf-chr10`; the app auto-discovers chr22, chr10, chr2, chr12 and uses them for profile generation (CYP2D6, CYP2C19, CYP2C9, UGT1A1, SLCO1B1).

---

## Command-Line Reference

### Basic Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--benchmark` | Run evaluation: JSON file with gene/alleles/expected_phenotype; output match % | `cpic_examples.json` |
| `--drug-name` | Name of the drug | `Warfarin` |
| `--drug-smiles` | SMILES string of the drug | `CC(=O)Nc1ccc(O)cc1` |
| `--vcf` | Path to chromosome 22 VCF (CYP2D6); optional if discovered in data/genomes | `data/genomes/chr22.vcf.gz` |
| `--vcf-chr10` | Path to chr10 VCF (CYP2C19, CYP2C9); optional if discovered | `data/genomes/chr10.vcf.gz` |
| `--sample-id` | Sample ID from VCF | `HG00096` |
| `--cyp2d6-status` | Manual CYP2D6 status (if not using VCF) | `poor_metabolizer` |

### Metabolizer Status Options

- `extensive_metabolizer` - Normal function (default)
- `intermediate_metabolizer` - Reduced function
- `poor_metabolizer` - No function
- `ultra_rapid_metabolizer` - Increased function

---

## Usage Modes

### Mode 1: Single Chromosome (CYP2D6 only)

**Coverage**: ~25% of clinically used drugs

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --drug-name Codeine \
  --sample-id HG00096
```

**Use Cases**:
- CYP2D6 substrates: Codeine, Tramadol, Metoprolol, Antidepressants
- Quick testing and validation
- When only chromosome 22 data is available

### Mode 2: Multi-Chromosome (Big 3 Enzymes)

**Coverage**: ~60-70% of clinically used drugs

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --vcf-chr10 data/genomes/chr10.vcf.gz \
  --drug-name Warfarin \
  --sample-id HG00096
```

**Enzyme Coverage**:
- **CYP2D6** (Chr22): Codeine, Tramadol, Metoprolol, Antidepressants
- **CYP2C19** (Chr10): Clopidogrel, Omeprazole, PPIs
- **CYP2C9** (Chr10): Warfarin, Ibuprofen, Phenytoin, NSAIDs

When chr2 and chr12 VCFs are present, **UGT1A1** (irinotecan) and **SLCO1B1** (statins) are also included in the profile. Profiles may show **allele calls** (e.g. CYP2D6 *1/*4) when inferred from VCF.

### Mode 3: Evaluation (Benchmark)

**Use Case**: Validate phenotype prediction against CPIC-style expected outcomes (research tool).

```bash
python main.py --benchmark cpic_examples.json
```

Output: table of gene, alleles, expected phenotype, predicted phenotype, match; then overall match %. Example file `cpic_examples.json` contains entries like `{"gene": "CYP2D6", "alleles": ["*1", "*4"], "expected_phenotype": "intermediate_metabolizer"}`.

### Mode 4: Manual Patient Profile

**Use Case**: Testing without VCF files or custom patient scenarios

```bash
python main.py \
  --cyp2d6-status poor_metabolizer \
  --drug-name Tramadol \
  --drug-smiles "CC(=O)Nc1ccc(O)cc1"
```

---

## Example Test Cases

### CYP2D6 Substrates

#### Codeine (High Risk for Poor Metabolizers)

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --drug-name Codeine \
  --drug-smiles "CN1CC[C@]23C4=C5C=CC(=C4O)Oc4c5c(C[C@@H]1[C@@H]2C=C[C@@H]3O)cc(c4)O"
```

**Expected**: High risk for poor metabolizers (no conversion to active morphine)

#### Tramadol (Medium Risk for Poor Metabolizers)

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --drug-name Tramadol \
  --drug-smiles "COc1cccc(C2(O)CCCCC2CN(C)C)c1"
```

**Expected**: Medium risk for poor metabolizers (reduced activation but manageable)

### CYP2C9 Substrates (Requires --vcf-chr10)

#### Warfarin (High Risk for Poor Metabolizers)

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --vcf-chr10 data/genomes/chr10.vcf.gz \
  --drug-name Warfarin \
  --drug-smiles "CC(=O)CC(c1ccc(OC)cc1)c1c(O)c2ccccc2oc1=O"
```

**Expected**: High risk for poor metabolizers (increased bleeding risk)

#### Ibuprofen (Medium Risk for Poor Metabolizers)

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --vcf-chr10 data/genomes/chr10.vcf.gz \
  --drug-name Ibuprofen \
  --drug-smiles "CC(C)Cc1ccc(C(C)C(=O)O)cc1"
```

**Expected**: Medium risk for poor metabolizers (reduced clearance, monitor GI effects)

### CYP2C19 Substrates (Requires --vcf-chr10)

#### Clopidogrel (Medium Risk for Poor Metabolizers)

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --vcf-chr10 data/genomes/chr10.vcf.gz \
  --drug-name Clopidogrel \
  --drug-smiles "CC(=O)N[C@@H]1CCc2ccccc2[C@H]1c1ccc(Cl)cc1"
```

**Expected**: Medium risk for poor metabolizers (reduced activation to active metabolite)

---

## Understanding Output

### Expected Output Format

```
--- Starting Simulation for Warfarin ---

[VCF Mode] Using patient profile from VCF files
  Chromosome 22: data/genomes/chr22.vcf.gz
  Chromosome 10: data/genomes/chr10.vcf.gz
  ✓ Big 3 enzymes enabled (CYP2D6, CYP2C19, CYP2C9)
  Sample ID: HG00096
  ✓ Generated patient profile from VCF

Patient Profile:
ID: HG00096
Age: 45
Genetics: CYP2D6 *1/*4 (Intermediate Metabolizer), CYP2C19 Poor Metabolizer, CYP2C9 *1/*3 (Extensive Metabolizer)
Conditions: Chronic Liver Disease (Mild)
Lifestyle: Alcohol: Moderate, Smoking: Non-smoker
Source: 1000 Genomes Project VCF

--- Step 1: Processing Drug ---
✓ Drug digitized: 2048-bit fingerprint

--- Step 2: Vector Similarity Search ---
✓ Found 3 similar drugs:
  1. Warfarin | SMILES: ... | Side Effects: ... | Targets: ...
  2. Similar Drug 2
  3. Similar Drug 3

--- Step 3: AI Simulation ---
============================================================
SIMULATION RESULT
============================================================
RISK LEVEL: High
PREDICTED REACTION: Increased bleeding risk due to reduced warfarin clearance...
BIOLOGICAL MECHANISM: CYP2C9 intermediate metabolizer status leads to...
```

### Risk Level Interpretation

- **LOW RISK**: Minimal impact, standard dosing appropriate
- **MEDIUM RISK**: Moderate consequences, manageable with dose adjustment or monitoring
- **HIGH RISK**: Severe consequences, alternative drug recommended or contraindicated

### Prediction Context (RAG Transparency)

In the **Streamlit UI**, after running an analysis, expand **"Prediction context (how this was derived)"**. You will see:

- **Genetics used**: The genetics line from the patient profile (e.g. CYP2D6 Poor Metabolizer, CYP2C9 *1/*3 (Extensive Metabolizer))
- **Similar drugs retrieved**: Names of drugs from vector search (ChEMBL/Pinecone or mock) used as RAG context
- **Sources**: Whether data came from "ChEMBL (via Pinecone)" or "Mock data (no Pinecone key)"

The **API** (`POST /analyze`) returns the same in the response: `similar_drugs_used`, `genetics_summary`, `context_sources`. This makes the prediction auditable and suitable for research use.

---

## Testing and Validation

### Quick Integration Test

```bash
python tests/quick_test.py
```

### Full Validation Suite

```bash
python tests/validation_tests.py
```

### Chromosome 10 Integration Test

```bash
python scripts/test_chromosome10.py
```

### VCF File Integrity Check

```bash
python scripts/check_vcf_integrity.py data/genomes/chr22.vcf.gz
python scripts/check_vcf_integrity.py data/genomes/chr10.vcf.gz
```

### Performance Benchmarking

```bash
python scripts/benchmark_performance.py
```

**Expected Performance**:
- Vector retrieval: <200ms
- LLM simulation: 3-10 seconds
- End-to-end workflow: 5-15 seconds

### Generate Validation Results

```bash
python scripts/generate_validation_results.py
```

---

## Advanced Usage

### Custom Drug Testing

```bash
python main.py \
  --drug-name "Custom Drug" \
  --drug-smiles "your_smiles_string_here" \
  --cyp2d6-status poor_metabolizer
```

### Specific Sample Testing

```bash
# Test specific sample from VCF
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --sample-id HG00097 \
  --drug-name Codeine

# List available samples
python -c "
from src.vcf_processor import get_sample_ids_from_vcf
samples = get_sample_ids_from_vcf('data/genomes/chr22.vcf.gz', limit=10)
print('Available samples:', samples)
"
```

### Batch Testing Multiple Drugs

```bash
# Test multiple CYP2C9 substrates
for drug in "Warfarin" "Ibuprofen" "Phenytoin"; do
  echo "Testing $drug..."
  python main.py \
    --vcf data/genomes/chr22.vcf.gz \
    --vcf-chr10 data/genomes/chr10.vcf.gz \
    --drug-name "$drug" \
    --sample-id HG00096
  echo "---"
done
```

---

## API Usage (Python)

### Basic Usage

```python
from src.input_processor import get_drug_fingerprint
from src.vector_search import find_similar_drugs
from src.agent_engine import run_simulation
from src.vcf_processor import generate_patient_profile_from_vcf

# Process drug
fingerprint = get_drug_fingerprint("CC(=O)Nc1ccc(O)cc1")
similar_drugs = find_similar_drugs(fingerprint)

# Generate patient profile from VCF
patient_profile = generate_patient_profile_from_vcf(
    vcf_path="data/genomes/chr22.vcf.gz",
    sample_id="HG00096",
    vcf_path_chr10="data/genomes/chr10.vcf.gz"  # Optional for Big 3
)

# Run simulation
result = run_simulation("Paracetamol", similar_drugs, patient_profile)
print(result)
```

### Multi-Chromosome Processing

```python
from src.vcf_processor import generate_patient_profile_multi_chromosome

# Big 3 enzymes
profile = generate_patient_profile_multi_chromosome(
    vcf_path_chr22="data/genomes/chr22.vcf.gz",
    vcf_path_chr10="data/genomes/chr10.vcf.gz",
    sample_id="HG00096"
)
```

---

## Common SMILES Strings

| Drug | SMILES |
|------|--------|
| **Paracetamol** | `CC(=O)Nc1ccc(O)cc1` |
| **Ibuprofen** | `CC(C)Cc1ccc(C(C)C(=O)O)cc1` |
| **Aspirin** | `CC(=O)Oc1ccccc1C(=O)O` |
| **Caffeine** | `CN1C=NC2=C1C(=O)N(C(=O)N2C)C` |
| **Codeine** | `CN1CC[C@]23C4=C5C=CC(=C4O)Oc4c5c(C[C@@H]1[C@@H]2C=C[C@@H]3O)cc(c4)O` |
| **Warfarin** | `CC(=O)CC(c1ccc(OC)cc1)c1c(O)c2ccccc2oc1=O` |
| **Clopidogrel** | `CC(=O)N[C@@H]1CCc2ccccc2[C@H]1c1ccc(Cl)cc1` |

---

## Troubleshooting

### Common Issues

**Issue**: "VCF file not found"
```bash
# Check file exists
ls -lh data/genomes/chr22.vcf.gz
```

**Issue**: "No samples found in VCF file"
```bash
# Check VCF integrity
python scripts/check_vcf_integrity.py data/genomes/chr22.vcf.gz
```

**Issue**: "GOOGLE_API_KEY not found"
```bash
# Set API key
export GOOGLE_API_KEY="your-key"
```

**Issue**: Mock drug data instead of real drugs
```bash
# Set Pinecone API key for real drug data
export PINECONE_API_KEY="your-key"
```

### Performance Issues

**Issue**: VCF processing is slow
- **Normal**: 1-5 minutes per chromosome
- **Solution**: Use smaller sample limits for testing

**Issue**: LLM simulation timeout
- **Solution**: Check internet connection and API key validity
- **Alternative**: Use different Gemini model (gemini-1.5-flash vs gemini-2.5-flash)

---

## Analysis and Results

### Understanding Metabolizer Status

The system uses a simplified heuristic for metabolizer status inference:
- **Extensive Metabolizer**: Normal enzyme function
- **Intermediate Metabolizer**: Reduced enzyme function
- **Poor Metabolizer**: No enzyme function
- **Ultra Rapid Metabolizer**: Increased enzyme function

**Note**: Current implementation uses variant counting, not star allele calling. For research purposes, this demonstrates the concept effectively.

### Clinical Accuracy

The system follows CPIC (Clinical Pharmacogenetics Implementation Consortium) guidelines:
- **High Risk**: Alternative drug recommended or contraindicated
- **Medium Risk**: Dose adjustment or monitoring recommended
- **Low Risk**: Standard dosing appropriate

### Big 3 Enzymes Coverage

| Enzyme | Drugs Covered | Clinical Impact |
|--------|---------------|-----------------|
| **CYP2D6** | ~25% of drugs | Antidepressants, opioids, beta-blockers |
| **CYP2C19** | Antiplatelet drugs | Clopidogrel, PPIs |
| **CYP2C9** | Anticoagulants, NSAIDs | Warfarin, ibuprofen |
| **Combined** | ~60-70% of drugs | Major clinical coverage |

---

## Next Steps

1. **Test with your own drugs**: Use custom SMILES strings
2. **Compare modes**: Single vs. multi-chromosome results
3. **Validate results**: Check against CPIC guidelines
4. **Performance testing**: Run benchmarks
5. **Integration**: Use Python API for custom applications

---

For more information, see:
- [Setup Guide](setup.md) - Installation and configuration
- [Implementation Details](implementation.md) - Technical details
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
