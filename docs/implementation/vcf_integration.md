# VCF Integration Implementation

## Overview

This document details the implementation of VCF (Variant Call Format) file processing for extracting genetic variants and generating patient profiles.

**File:** `src/vcf_processor.py`

---

## Purpose

Extract genetic variants from VCF files (specifically from 1000 Genomes Project) to:
1. Identify CYP gene variants (CYP2D6, CYP2C19, CYP3A4)
2. Infer metabolizer status from variants
3. Generate patient profiles from genomic data

---

## Key Functions

### 1. `get_sample_ids_from_vcf(vcf_path, limit=None)`

**Purpose:** Extract sample IDs from VCF file header

**Input:**
- `vcf_path`: Path to VCF file (supports .gz)
- `limit`: Maximum number of samples to return

**Output:**
- List of sample IDs (e.g., `['HG00096', 'HG00097', ...]`)

**Implementation:**
```python
# Reads VCF header line
# Format: #CHROM POS ID REF ALT QUAL FILTER INFO FORMAT HG00096 HG00097 ...
# Extracts sample IDs from last line of header
```

---

### 2. `extract_cyp_variants(vcf_path, gene='CYP2D6', sample_id=None)`

**Purpose:** Extract variants in CYP gene regions

**Input:**
- `vcf_path`: Path to VCF file
- `gene`: Which CYP gene ('CYP2D6', 'CYP2C19', 'CYP3A4')
- `sample_id`: Specific sample to extract (None = all samples)

**Output:**
- List of variant dictionaries with:
  - `chrom`: Chromosome
  - `pos`: Position
  - `ref`: Reference allele
  - `alt`: Alternate allele
  - `genotype`: Sample genotype (e.g., '0/1', '1/1')
  - `sample_id`: Sample identifier

**Gene Regions:**
- **CYP2D6:** Chr22 (42522500-42530900)
- **CYP2C19:** Chr10 (96541615-96561468)
- **CYP3A4:** Chr7 (99376140-99391055)

**Implementation:**
```python
# 1. Open VCF file (handles .gz compression)
# 2. Parse header to find sample column indices
# 3. Iterate through variants
# 4. Check if variant is in CYP gene region
# 5. Extract genotype for specified sample(s)
# 6. Return list of variants
```

---

### 3. `infer_metabolizer_status(variants)`

**Purpose:** Infer CYP metabolizer status from variants

**Input:**
- `variants`: List of variant dictionaries

**Output:**
- Metabolizer status string:
  - `'poor_metabolizer'`
  - `'intermediate_metabolizer'`
  - `'extensive_metabolizer'`
  - `'ultra_rapid_metabolizer'`

**Current Implementation (Simplified):**
```python
# Counts variants in gene region
# Simplified logic:
# - Many variants → poor metabolizer (likely non-functional alleles)
# - Few variants → extensive metabolizer (likely functional)
# - No variants → extensive metabolizer (wild-type)
```

**Limitations:**
- Real implementation requires:
  - Haplotype phasing
  - Star allele calling
  - PharmVar database lookup
- Current version is simplified for MVP

---

### 4. `generate_patient_profile_from_vcf(vcf_path, sample_id, age=None)`

**Purpose:** Generate complete patient profile from VCF data

**Input:**
- `vcf_path`: Path to VCF file
- `sample_id`: Sample identifier
- `age`: Optional age (default: random 30-70)

**Output:**
- Patient profile dictionary:
  ```python
  {
      'id': 'HG00096',
      'age': 45,
      'cyp2d6_status': 'poor_metabolizer',
      'cyp2c19_status': 'extensive_metabolizer',
      'cyp3a4_status': 'extensive_metabolizer',
      'genetic_markers': 'CYP2D6*4/*4',
      'medical_conditions': 'None',
      'lifestyle': 'Standard'
  }
  ```

**Implementation:**
1. Extract CYP variants for all three genes
2. Infer metabolizer status for each
3. Format as patient profile
4. Add default medical conditions/lifestyle if not specified

---

## Usage Examples

### Example 1: Extract Sample IDs

```python
from src.vcf_processor import get_sample_ids_from_vcf

samples = get_sample_ids_from_vcf(
    'data/genomes/chr22.vcf.gz',
    limit=10
)
print(f"Found {len(samples)} samples: {samples}")
```

### Example 2: Extract CYP2D6 Variants

```python
from src.vcf_processor import extract_cyp_variants

variants = extract_cyp_variants(
    'data/genomes/chr22.vcf.gz',
    gene='CYP2D6',
    sample_id='HG00096'
)
print(f"Found {len(variants)} CYP2D6 variants")
```

### Example 3: Generate Patient Profile

```python
from src.vcf_processor import generate_patient_profile_from_vcf

profile = generate_patient_profile_from_vcf(
    'data/genomes/chr22.vcf.gz',
    sample_id='HG00096',
    age=45
)
print(profile)
```

---

## Integration with Main Script

### Command Line Usage

```bash
# Use VCF file to generate patient profile
python main.py --vcf data/genomes/chr22.vcf.gz --sample-id HG00096

# Or use manual profile (default)
python main.py --cyp2d6-status poor_metabolizer
```

### Code Integration

```python
# In main.py
if args.vcf:
    from src.vcf_processor import generate_patient_profile_from_vcf
    patient_profile = generate_patient_profile_from_vcf(
        args.vcf,
        args.sample_id
    )
else:
    # Use manual profile
    patient_profile = create_manual_profile(args.cyp2d6_status)
```

---

## File Format Understanding

### VCF File Structure

```
##fileformat=VCFv4.3
##contig=<ID=22,length=51304566>
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
#CHROM POS ID REF ALT QUAL FILTER INFO FORMAT HG00096 HG00097 ...
22 42522500 rs123 A G . PASS . GT 0/1 1/1 ...
22 42522510 rs456 C T . PASS . GT 0/0 0/1 ...
```

**Key Fields:**
- `#CHROM`: Chromosome number
- `POS`: Position on chromosome
- `REF`: Reference allele
- `ALT`: Alternate allele
- `GT`: Genotype (0=REF, 1=ALT)
  - `0/0`: Homozygous reference
  - `0/1`: Heterozygous
  - `1/1`: Homozygous alternate

---

## Performance Considerations

### File Size

- Chromosome 22 VCF: ~500MB compressed
- Full genome VCF: ~200GB+ compressed
- Processing time: ~1-5 minutes per chromosome

### Optimization Strategies

1. **Streaming Parsing:**
   - Don't load entire file into memory
   - Process line-by-line
   - Stop after finding target region

2. **Compression Handling:**
   - Use `gzip` module for .gz files
   - Transparent decompression
   - No need to extract first

3. **Region Filtering:**
   - Only process variants in CYP gene regions
   - Skip rest of chromosome
   - Reduces processing time

---

## Limitations

### 1. Simplified Metabolizer Inference

**Current:**
- Counts variants
- Simple heuristics
- Not clinically accurate

**Future:**
- Implement star allele calling
- Use PharmVar database
- Proper haplotype phasing

### 2. Single Chromosome Support

**Current:**
- Only processes chromosome 22 (CYP2D6)
- CYP2C19 (Chr10) and CYP3A4 (Chr7) need separate files

**Future:**
- Multi-chromosome support
- Combine multiple VCF files
- Or use full genome VCF

### 3. No Copy Number Variation (CNV) Detection

**Current:**
- Doesn't detect gene duplications/deletions
- Important for CYP2D6 (ultra-rapid metabolizers)

**Future:**
- Implement CNV detection
- Use read depth information
- Detect 0, 1, 2, 3+ copies

---

## Testing

### Unit Tests

See `tests/validation_tests.py` for:
- VCF file parsing tests
- Variant extraction tests
- Metabolizer status inference tests
- Patient profile generation tests

### Quick Test

```bash
python -c "
from src.vcf_processor import get_sample_ids_from_vcf
samples = get_sample_ids_from_vcf('data/genomes/chr22.vcf.gz', limit=5)
print(f'Found {len(samples)} samples')
"
```

---

## References

- **VCF Format Specification:** https://samtools.github.io/hts-specs/VCFv4.3.pdf
- **1000 Genomes Project:** https://www.internationalgenome.org/
- **CYP Gene Locations:** Ensembl Genome Browser
- **PharmVar:** https://www.pharmvar.org/ (for star allele definitions)

---

*For setup instructions, see `docs/setup/vcf_chembl_setup.md`*
