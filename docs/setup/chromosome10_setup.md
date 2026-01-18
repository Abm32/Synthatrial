# Chromosome 10 Setup Guide

## Overview

This guide explains how to set up Chromosome 10 support for Anukriti, enabling the "Big 3" enzymes: **CYP2D6**, **CYP2C19**, and **CYP2C9**.

By adding Chromosome 10, Anukriti will cover metabolic pathways for **~60-70% of all clinically used drugs** (up from ~25% with CYP2D6 alone).

---

## Why Chromosome 10?

### Enzyme Coverage

| Enzyme | Chromosome | Key Drugs Metabolized | Clinical Impact |
|--------|------------|----------------------|-----------------|
| **CYP2D6** | 22 | Codeine, Tramadol, Metoprolol, Antidepressants | ~25% of drugs |
| **CYP2C19** | 10 | Clopidogrel (Plavix), Omeprazole, PPIs | Antiplatelet, GI drugs |
| **CYP2C9** | 10 | Warfarin, Ibuprofen, Phenytoin, NSAIDs | Anticoagulation, pain management |

### Combined Coverage

- **CYP2D6 alone**: ~25% of clinically used drugs
- **Big 3 enzymes (CYP2D6 + CYP2C19 + CYP2C9)**: ~60-70% of clinically used drugs

This represents a **massive jump** from "Proof of Concept" to "Major Platform."

---

## Step 1: Download Chromosome 10 VCF File

### Download Command

```bash
# Navigate to your data directory
cd data/genomes/

# Download Chromosome 10 VCF (Approx 500MB - 800MB)
wget https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz

# Verify download
ls -lh ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz
```

### Expected File Size

- **Chromosome 10**: ~500-800 MB (compressed)
- **Chromosome 22**: ~100-200 MB (compressed)

---

## Step 2: Gene Coordinates

The system uses the following coordinates (GRCh37/hg19):

| Gene | Chromosome | Start Position | End Position |
|------|------------|----------------|--------------|
| **CYP2C19** | 10 | 96,535,040 | 96,625,463 |
| **CYP2C9** | 10 | 96,698,415 | 96,749,147 |
| **CYP2D6** | 22 | 42,522,500 | 42,530,900 |

These coordinates are automatically configured in `src/vcf_processor.py`.

---

## Step 3: Usage

### Command-Line Usage

#### Single Chromosome (CYP2D6 only)

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --drug-name Codeine \
  --sample-id HG00096
```

#### Multiple Chromosomes (Big 3 enzymes)

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --vcf-chr10 data/genomes/chr10.vcf.gz \
  --drug-name Warfarin \
  --sample-id HG00096
```

### Python API Usage

```python
from src.vcf_processor import generate_patient_profile_from_vcf

# Single chromosome
profile = generate_patient_profile_from_vcf(
    vcf_path="data/genomes/chr22.vcf.gz",
    sample_id="HG00096",
    vcf_path_chr10=None  # Only CYP2D6
)

# Multiple chromosomes (Big 3)
profile = generate_patient_profile_from_vcf(
    vcf_path="data/genomes/chr22.vcf.gz",
    sample_id="HG00096",
    vcf_path_chr10="data/genomes/chr10.vcf.gz"  # CYP2C9 + CYP2C19
)
```

---

## Step 4: Example Test Cases

### CYP2C19 Test: Clopidogrel

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --vcf-chr10 data/genomes/chr10.vcf.gz \
  --drug-name Clopidogrel \
  --drug-smiles "CC(=O)N[C@@H]1CCc2ccccc2[C@H]1c1ccc(Cl)cc1" \
  --sample-id HG00096
```

**Expected**: Medium risk for poor CYP2C19 metabolizers (reduced activation to active metabolite)

### CYP2C9 Test: Warfarin

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --vcf-chr10 data/genomes/chr10.vcf.gz \
  --drug-name Warfarin \
  --drug-smiles "CC(=O)CC(c1ccc(OC)cc1)c1c(O)c2ccccc2oc1=O" \
  --sample-id HG00096
```

**Expected**: High risk for poor CYP2C9 metabolizers (increased bleeding risk)

### CYP2C9 Test: Ibuprofen

```bash
python main.py \
  --vcf data/genomes/chr22.vcf.gz \
  --vcf-chr10 data/genomes/chr10.vcf.gz \
  --drug-name Ibuprofen \
  --drug-smiles "CC(C)Cc1ccc(C(C)C(=O)O)cc1" \
  --sample-id HG00096
```

**Expected**: Medium risk for poor CYP2C9 metabolizers (reduced clearance, monitor for GI effects)

---

## Step 5: Verify Installation

### Check Gene Coordinates

```python
from src.vcf_processor import CYP_GENE_LOCATIONS

print("Gene Locations:")
for gene, loc in CYP_GENE_LOCATIONS.items():
    print(f"  {gene}: Chr{loc['chrom']}, {loc['start']}-{loc['end']}")
```

**Expected Output**:
```
Gene Locations:
  CYP2D6: Chr22, 42522500-42530900
  CYP2C19: Chr10, 96535040-96625463
  CYP2C9: Chr10, 96698415-96749147
  CYP3A4: Chr7, 99376140-99391055
```

### Test Variant Extraction

```python
from src.vcf_processor import extract_cyp_variants

# Test CYP2C19 extraction
variants = extract_cyp_variants(
    "data/genomes/chr10.vcf.gz",
    gene="CYP2C19",
    sample_limit=1
)
print(f"Found {len(variants)} CYP2C19 variants")

# Test CYP2C9 extraction
variants = extract_cyp_variants(
    "data/genomes/chr10.vcf.gz",
    gene="CYP2C9",
    sample_limit=1
)
print(f"Found {len(variants)} CYP2C9 variants")
```

---

## Technical Details

### Updated Files

1. **`src/vcf_processor.py`**:
   - Added CYP2C9 to `CYP_GENE_LOCATIONS`
   - Updated CYP2C19 coordinates
   - Enhanced `generate_patient_profile_from_vcf()` to support multiple VCF files
   - Added `generate_patient_profile_multi_chromosome()` helper function

2. **`src/agent_engine.py`**:
   - Updated prompt to include CYP2C19 and CYP2C9 information
   - Added CPIC guidelines for CYP2C19 and CYP2C9 substrates
   - Enhanced reasoning steps to identify relevant enzymes

3. **`main.py`**:
   - Added `--vcf-chr10` argument
   - Enhanced help text with examples
   - Improved error messages

### Performance Considerations

- **Chromosome 10 VCF**: Larger than chromosome 22 (~500-800 MB vs ~100-200 MB)
- **Processing Time**: ~2-5 minutes per chromosome (depends on file size)
- **Memory**: ~500 MB - 1 GB RAM per VCF file

---

## Troubleshooting

### Issue: "VCF file not found"

**Solution**: Ensure the file path is correct and the file exists:
```bash
ls -lh data/genomes/chr10.vcf.gz
```

### Issue: "No variants found"

**Possible Causes**:
1. Wrong chromosome in VCF file
2. Sample ID not found in VCF
3. Gene coordinates don't match VCF build (should be GRCh37/hg19)

**Solution**: Verify VCF file contains chromosome 10 data:
```bash
zcat data/genomes/chr10.vcf.gz | head -20
```

### Issue: "Warning: Could not extract CYP2C9 variants"

**Solution**: Check that:
1. VCF file is for chromosome 10
2. File is not corrupted
3. Gene coordinates are within the VCF range

---

## Next Steps

1. **Download Chromosome 7** (CYP3A4) for even broader coverage
2. **Add validation test cases** for CYP2C19 and CYP2C9 substrates
3. **Update paper** to reflect Big 3 enzyme coverage
4. **Benchmark performance** with multiple chromosomes

---

## References

- **1000 Genomes Project**: https://www.internationalgenome.org/
- **CPIC Guidelines**: https://cpicpgx.org/
- **PharmGKB**: https://www.pharmgkb.org/
- **CYP2C19 Gene**: https://www.pharmgkb.org/gene/PA124
- **CYP2C9 Gene**: https://www.pharmgkb.org/gene/PA125

---

*Last Updated: Chromosome 10 implementation*
