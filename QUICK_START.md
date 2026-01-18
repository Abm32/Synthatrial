# Quick Start Guide - Running Anukriti

## Prerequisites

1. **Activate conda environment:**
   ```bash
   conda activate synthatrial
   ```

2. **Set up API keys** (in `.env` file or environment):
   ```bash
   export GOOGLE_API_KEY="your-api-key"
   export PINECONE_API_KEY="your-api-key"  # Optional (uses mock data if not set)
   ```

---

## Running the Project

### Option 1: Single Chromosome (CYP2D6 only)

**Basic usage:**
```bash
python main.py \
  --vcf data/genomes/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --drug-name Codeine
```

**With custom drug:**
```bash
python main.py \
  --vcf data/genomes/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --drug-name "Your Drug Name" \
  --drug-smiles "CC(=O)Nc1ccc(O)cc1"
```

---

### Option 2: Big 3 Enzymes (CYP2D6 + CYP2C19 + CYP2C9) ⭐

**Test with Warfarin (CYP2C9 substrate):**
```bash
python main.py \
  --vcf data/genomes/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --vcf-chr10 data/genomes/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --drug-name Warfarin \
  --drug-smiles "CC(=O)CC(c1ccc(OC)cc1)c1c(O)c2ccccc2oc1=O"
```

**Test with Clopidogrel (CYP2C19 substrate):**
```bash
python main.py \
  --vcf data/genomes/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --vcf-chr10 data/genomes/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --drug-name Clopidogrel \
  --drug-smiles "CC(=O)N[C@@H]1CCc2ccccc2[C@H]1c1ccc(Cl)cc1"
```

**Test with Ibuprofen (CYP2C9 substrate):**
```bash
python main.py \
  --vcf data/genomes/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --vcf-chr10 data/genomes/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --drug-name Ibuprofen \
  --drug-smiles "CC(C)Cc1ccc(C(C)C(=O)O)cc1"
```

---

### Option 3: Manual Patient Profile (No VCF)

**Test without VCF files:**
```bash
python main.py \
  --cyp2d6-status poor_metabolizer \
  --drug-name Tramadol
```

---

## Example Test Cases

### Test Case 1: Codeine (CYP2D6)
```bash
python main.py \
  --vcf data/genomes/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --drug-name Codeine \
  --drug-smiles "CN1CC[C@]23C4=C5C=CC(=C4O)Oc4c5c(C[C@@H]1[C@@H]2C=C[C@@H]3O)cc(c4)O"
```

**Expected:** High risk for poor CYP2D6 metabolizers

---

### Test Case 2: Warfarin (CYP2C9) - Big 3 Enzymes
```bash
python main.py \
  --vcf data/genomes/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --vcf-chr10 data/genomes/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --drug-name Warfarin \
  --drug-smiles "CC(=O)CC(c1ccc(OC)cc1)c1c(O)c2ccccc2oc1=O" \
  --sample-id HG00096
```

**Expected:** High risk for poor CYP2C9 metabolizers (bleeding risk)

---

### Test Case 3: Clopidogrel (CYP2C19) - Big 3 Enzymes
```bash
python main.py \
  --vcf data/genomes/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --vcf-chr10 data/genomes/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --drug-name Clopidogrel \
  --drug-smiles "CC(=O)N[C@@H]1CCc2ccccc2[C@H]1c1ccc(Cl)cc1" \
  --sample-id HG00096
```

**Expected:** Medium risk for poor CYP2C19 metabolizers (reduced activation)

---

## Command-Line Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--vcf` | Path to chromosome 22 VCF file (CYP2D6) | `data/genomes/chr22.vcf.gz` |
| `--vcf-chr10` | Path to chromosome 10 VCF file (CYP2C19, CYP2C9) | `data/genomes/chr10.vcf.gz` |
| `--drug-name` | Name of the drug | `Warfarin` |
| `--drug-smiles` | SMILES string of the drug | `CC(=O)Nc1ccc(O)cc1` |
| `--sample-id` | Specific sample ID from VCF | `HG00096` |
| `--cyp2d6-status` | Manual CYP2D6 status (if not using VCF) | `poor_metabolizer` |

---

## Testing Scripts

### Run Full Test Suite
```bash
python scripts/test_chromosome10.py
```

### Check VCF File Integrity
```bash
python scripts/check_vcf_integrity.py data/genomes/chr10.vcf.gz
```

### Generate Validation Results
```bash
python scripts/generate_validation_results.py
```

### Benchmark Performance
```bash
python scripts/benchmark_performance.py
```

---

## Troubleshooting

### Issue: "VCF file not found"
**Solution:** Check file paths and ensure VCF files are downloaded:
```bash
ls -lh data/genomes/*.vcf.gz
```

### Issue: "No samples found in VCF file"
**Solution:** The VCF file might be corrupted or empty. Re-download it.

### Issue: "GOOGLE_API_KEY not found"
**Solution:** Set the API key:
```bash
export GOOGLE_API_KEY="your-key"
# Or add to .env file
```

### Issue: "ModuleNotFoundError"
**Solution:** Activate conda environment:
```bash
conda activate synthatrial
```

---

## Expected Output

When running successfully, you should see:

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
Genetics: CYP2D6 Extensive Metabolizer, CYP2C19 Poor Metabolizer
Conditions: Chronic Liver Disease (Mild)
Lifestyle: Alcohol: Moderate, Smoking: Non-smoker
Source: 1000 Genomes Project VCF

--- Step 1: Processing Drug ---
✓ Drug digitized: 2048-bit fingerprint

--- Step 2: Vector Similarity Search ---
✓ Found 3 similar drugs:
  1. Warfarin (ChEMBL ID: ...)
  2. ...

--- Step 3: AI Simulation ---
============================================================
SIMULATION RESULT
============================================================
RISK LEVEL: High
PREDICTED REACTION: ...
BIOLOGICAL MECHANISM: ...
```

---

## Next Steps

1. **Test with different drugs** (Warfarin, Clopidogrel, Ibuprofen)
2. **Try different sample IDs** from the VCF file
3. **Compare single vs. multi-chromosome** results
4. **Run validation tests** to verify accuracy

---

*For more details, see `docs/setup/chromosome10_setup.md`*
