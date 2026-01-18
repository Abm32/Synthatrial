# Run Modes Explained: VCF vs Manual Profiles

## Overview

The Anukriti platform supports three different modes for running pharmacogenomic simulations, each with different levels of genetic detail and use cases.

---

## 🧬 Mode 1: Single Chromosome (CYP2D6 only)

### Command:
```bash
python main.py \
  --vcf data/genomes/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --drug-name Codeine \
  --drug-smiles "CN1CC[C@]23C4=C5C=CC(=C4O)Oc4c5c(C[C@@H]1[C@@H]2C=C[C@@H]3O)cc(c4)O"
```

### What It Does:
- **Uses real genetic data** from 1000 Genomes Project VCF file (chromosome 22)
- **Extracts CYP2D6 variants** from a specific patient sample (e.g., HG00096)
- **Calculates metabolizer status** using Activity Score method (star allele calling)
- **Only covers CYP2D6** enzyme (one of the "Big 3")

### Patient Profile Example:
```
ID: HG00096
Age: 45
Genetics: CYP2D6 Extensive Metabolizer
Conditions: Chronic Liver Disease (Mild)
Lifestyle: Alcohol: Moderate, Smoking: Non-smoker
Source: 1000 Genomes Project VCF
```

### When to Use:
- ✅ Testing CYP2D6-specific drugs (Codeine, Tramadol, Metoprolol)
- ✅ Quick testing without downloading chromosome 10 VCF
- ✅ When you only care about CYP2D6 metabolism

### Limitations:
- ❌ Cannot assess CYP2C19 or CYP2C9 metabolism
- ❌ Incomplete picture for drugs metabolized by multiple enzymes

---

## ⭐ Mode 2: Big 3 Enzymes (CYP2D6 + CYP2C19 + CYP2C9)

### Command:
```bash
python main.py \
  --vcf data/genomes/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --vcf-chr10 data/genomes/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --drug-name Warfarin \
  --drug-smiles "CC(=O)CC(c1ccc(OC)cc1)c1c(O)c2ccccc2oc1=O"
```

### What It Does:
- **Uses real genetic data** from TWO VCF files:
  - Chromosome 22 → CYP2D6 variants
  - Chromosome 10 → CYP2C19 and CYP2C9 variants
- **Extracts variants** for all three major CYP enzymes
- **Calculates metabolizer status** for each enzyme independently
- **Covers the "Big 3"** metabolic enzymes (most clinically important)

### Patient Profile Example:
```
ID: HG00096
Age: 45
Genetics: CYP2D6 Extensive Metabolizer, CYP2C19 Poor Metabolizer, CYP2C9 Intermediate Metabolizer
Conditions: Chronic Liver Disease (Mild)
Lifestyle: Alcohol: Moderate, Smoking: Non-smoker
Source: 1000 Genomes Project VCF
```

### When to Use:
- ✅ **Recommended for most use cases** - covers 80% of pharmacogenomic scenarios
- ✅ Testing drugs metabolized by CYP2C9 (Warfarin, Ibuprofen, Phenytoin)
- ✅ Testing drugs metabolized by CYP2C19 (Clopidogrel, Omeprazole, Sertraline)
- ✅ Comprehensive pharmacogenomic assessment
- ✅ Research and clinical simulation

### Advantages:
- ✅ Most comprehensive genetic profile
- ✅ Real patient data from 1000 Genomes Project
- ✅ Accurate metabolizer status calculation (Activity Score method)
- ✅ Can assess multi-enzyme drug metabolism

---

## 🔧 Mode 3: Manual Patient Profile (No VCF)

### Command:
```bash
python main.py \
  --cyp2d6-status poor_metabolizer \
  --drug-name Tramadol \
  --drug-smiles "CC(=O)Nc1ccc(O)cc1"
```

### What It Does:
- **Does NOT use VCF files** - no real genetic data
- **Uses manually specified** CYP2D6 metabolizer status
- **Simplified patient profile** with only CYP2D6 information
- **No genetic variant analysis** - just a status label

### Patient Profile Example:
```
ID: SP-01
Age: 45
Genetics: CYP2D6 Poor Metabolizer
Conditions: Chronic Liver Disease (Mild)
Lifestyle: Alcohol consumer (Moderate)
```

### When to Use:
- ✅ **Quick testing** without VCF files
- ✅ **Demonstration purposes** - showing how the system works
- ✅ **Hypothetical scenarios** - "what if patient is a poor metabolizer?"
- ✅ When VCF files are not available or too large to download
- ✅ Testing the LLM reasoning without genetic complexity

### Limitations:
- ❌ **Not real patient data** - simulated/simplified
- ❌ **Only CYP2D6** - cannot specify CYP2C19 or CYP2C9
- ❌ **No variant-level detail** - just a status label
- ❌ **Less accurate** - doesn't use Activity Score calculation
- ❌ **Not suitable for research** - only for testing/demos

---

## 📊 Comparison Table

| Feature | Single Chromosome | Big 3 Enzymes | Manual Profile |
|---------|------------------|---------------|----------------|
| **Uses VCF Files** | ✅ Yes (chr22) | ✅ Yes (chr22 + chr10) | ❌ No |
| **Real Genetic Data** | ✅ Yes | ✅ Yes | ❌ No (simulated) |
| **CYP2D6 Coverage** | ✅ Yes | ✅ Yes | ✅ Yes (manual) |
| **CYP2C19 Coverage** | ❌ No | ✅ Yes | ❌ No |
| **CYP2C9 Coverage** | ❌ No | ✅ Yes | ❌ No |
| **Activity Score Method** | ✅ Yes | ✅ Yes | ❌ No |
| **Star Allele Calling** | ✅ Yes | ✅ Yes | ❌ No |
| **Variant-Level Detail** | ✅ Yes | ✅ Yes | ❌ No |
| **Use Case** | CYP2D6 drugs only | Comprehensive | Testing/Demo |
| **Accuracy** | High (for CYP2D6) | Highest | Low (simplified) |
| **File Size** | ~205 MB | ~943 MB total | 0 MB |

---

## 🎯 Which Mode Should You Use?

### Use **Single Chromosome** when:
- Testing CYP2D6-specific drugs (Codeine, Tramadol)
- Quick testing without downloading large files
- Limited storage/bandwidth

### Use **Big 3 Enzymes** (Recommended) when:
- **Most use cases** - covers majority of pharmacogenomic scenarios
- Testing Warfarin, Clopidogrel, or other multi-enzyme drugs
- Research or clinical simulation
- Need comprehensive genetic assessment

### Use **Manual Profile** when:
- Quick testing/demonstration
- VCF files not available
- Testing hypothetical scenarios
- Learning how the system works

---

## 🔬 Technical Differences

### VCF Mode (Single or Big 3):
1. **Reads VCF file** → Parses compressed genomic data
2. **Extracts variants** → Finds SNPs/indels in CYP gene regions
3. **Star allele calling** → Maps variants to known alleles (*1, *2, *3, etc.)
4. **Activity Score calculation** → Sums activity scores from alleles
5. **Metabolizer status inference** → Converts activity score to status
6. **Patient profile generation** → Creates detailed genetic profile

### Manual Mode:
1. **Takes status directly** → Uses `--cyp2d6-status` argument
2. **Creates simple profile** → No genetic variant analysis
3. **No star alleles** → Just a status label
4. **No Activity Score** → Direct status assignment

---

## 📈 Example Scenarios

### Scenario 1: Codeine (CYP2D6 substrate)
- **Single Chromosome**: ✅ Perfect - Codeine is primarily CYP2D6
- **Big 3 Enzymes**: ✅ Works but overkill
- **Manual Profile**: ✅ Works for testing

### Scenario 2: Warfarin (CYP2C9 substrate)
- **Single Chromosome**: ❌ Cannot assess CYP2C9
- **Big 3 Enzymes**: ✅ Perfect - Warfarin is CYP2C9 substrate
- **Manual Profile**: ❌ Cannot specify CYP2C9 status

### Scenario 3: Clopidogrel (CYP2C19 substrate)
- **Single Chromosome**: ❌ Cannot assess CYP2C19
- **Big 3 Enzymes**: ✅ Perfect - Clopidogrel requires CYP2C19 activation
- **Manual Profile**: ❌ Cannot specify CYP2C19 status

---

## 💡 Key Takeaways

1. **VCF files = Real genetic data** from actual patients (1000 Genomes Project)
2. **Manual mode = Simplified simulation** for testing/demos
3. **Big 3 Enzymes = Most comprehensive** - recommended for most use cases
4. **Single Chromosome = Quick testing** - good for CYP2D6-only drugs
5. **Activity Score method** (used in VCF modes) is more accurate than simple status labels

---

## 🔍 What Are VCF Files?

**VCF (Variant Call Format)** files contain:
- **Genetic variants** (SNPs, indels) from real individuals
- **1000 Genomes Project** data - population-scale genomics
- **Chromosome-specific** - one file per chromosome
- **Compressed format** (.vcf.gz) - large files (~200-700 MB each)
- **Sample IDs** - each column represents a different person (HG00096, HG00097, etc.)

**Example VCF entry:**
```
22  42522500  rs123456  A  G  0.95  PASS  AC=1234  GT:DP  0|1:45
```
- Chromosome 22, position 42522500
- Reference allele: A, Alternate allele: G
- Sample genotype: 0|1 (heterozygous)

---

For more details, see:
- [VCF Integration](docs/implementation/vcf_integration.md)
- [Chromosome 10 Setup](docs/setup/chromosome10_setup.md)
- [Pharmacogenomics Concepts](docs/concepts/pharmacogenomics.md)
