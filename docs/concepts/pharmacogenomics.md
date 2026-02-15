# Pharmacogenomics Concepts

> **Note:** SynthaTrial is a research prototype for simulation and explanation. It is not a certified clinical pharmacogenomics predictor; its outputs must not be used for clinical decision-making.

**In SynthaTrial:** Genes covered are CYP2D6 (chr22), CYP2C19/CYP2C9 (chr10), UGT1A1 (chr2), SLCO1B1 (chr12). Allele calling (*1, *2, *4…) is mapped to function via a PharmVar/CPIC-style table (`variant_db.ALLELE_FUNCTION_MAP`). Evaluation mode: `python main.py --benchmark cpic_examples.json`. See [Implementation](implementation.md) and [Usage](usage.md).

## What is Pharmacogenomics?

Pharmacogenomics is the study of how an individual's genetic makeup affects their response to drugs. It combines pharmacology (the science of drugs) and genomics (the study of genes and their functions).

**Key Principle:** Different people respond differently to the same drug due to genetic variations.

---

## Core Concepts

### 1. Drug Metabolism

**Definition:** The process by which the body breaks down and eliminates drugs.

**Key Enzymes:**
- **CYP450 Family**: Cytochrome P450 enzymes are responsible for metabolizing most drugs
- **CYP2D6**: Metabolizes ~25% of all drugs (antidepressants, beta-blockers, opioids)
- **CYP2C19**: Metabolizes proton pump inhibitors, antidepressants, antiplatelet drugs
- **CYP3A4**: Metabolizes ~50% of all drugs (statins, calcium channel blockers, many others)

**Why It Matters:**
- Genetic variations in these enzymes affect how fast drugs are metabolized
- Too fast → drug cleared before it works
- Too slow → drug accumulates, causing toxicity

---

### 2. Metabolizer Status

Based on genetic variants, individuals are classified into metabolizer phenotypes:

#### CYP2D6 Metabolizer Types

1. **Ultra-Rapid Metabolizer (UM)**
   - Multiple functional copies of CYP2D6 gene
   - Metabolizes drugs very quickly
   - May need higher doses
   - Example: Some individuals have 3+ copies of functional alleles

2. **Extensive Metabolizer (EM)** - Normal
   - Standard number of functional copies
   - Normal drug metabolism
   - Standard dosing usually appropriate

3. **Intermediate Metabolizer (IM)**
   - Reduced enzyme activity
   - Slower metabolism than normal
   - May need dose adjustments

4. **Poor Metabolizer (PM)**
   - Little or no functional enzyme
   - Very slow metabolism
   - Higher risk of drug accumulation and toxicity
   - Example: CYP2D6*4/*4 genotype (no functional enzyme)

**Clinical Impact:**
- Poor metabolizers of codeine → reduced conversion to morphine (less pain relief)
- Poor metabolizers of tamoxifen → reduced active metabolite (less effective cancer treatment)
- Ultra-rapid metabolizers of codeine → rapid conversion to morphine (overdose risk)

---

### 3. Genetic Variants and Alleles

**Allele:** A variant form of a gene

**Star Allele Nomenclature:**
- CYP2D6*1: Wild-type (normal function)
- CYP2D6*4: Non-functional variant (common in Europeans)
- CYP2D6*10: Reduced function variant (common in Asians)
- CYP2D6*17: Reduced function variant (common in Africans)

**Genotype Examples:**
- `*1/*1`: Two copies of normal allele → Extensive Metabolizer
- `*1/*4`: One normal, one non-functional → Intermediate Metabolizer
- `*4/*4`: Two non-functional copies → Poor Metabolizer

**How We Infer Status:**
- In our implementation, we use simplified variant counting
- Real clinical practice uses haplotype phasing and star allele calling
- PharmVar database provides official allele definitions

---

### 4. Drug-Drug Interactions

**Definition:** When one drug affects the metabolism of another drug.

**Types:**
1. **Inhibition:** One drug blocks the enzyme that metabolizes another
   - Example: Fluoxetine (antidepressant) inhibits CYP2D6
   - If taken with codeine, codeine won't be metabolized properly

2. **Induction:** One drug increases enzyme production
   - Example: Rifampin (antibiotic) induces CYP3A4
   - May cause other drugs to be cleared too quickly

**Why It Matters:**
- Multiple drugs can compound genetic effects
- Our system checks for CYP enzyme interactions in ChEMBL data

---

## How SynthaTrial Uses These Concepts

### 1. VCF File Processing

**What We Do:**
- Extract variants in CYP gene regions from VCF files
- Identify genetic variants that affect drug metabolism
- Infer metabolizer status from variants

**Example:**
```python
# Extract CYP2D6 variants from VCF
variants = extract_cyp_variants(vcf_file, gene="CYP2D6")

# Infer metabolizer status
status = infer_metabolizer_status(variants)
# Returns: "poor_metabolizer", "extensive_metabolizer", etc.
```

**Limitations:**
- Simplified inference (real systems use star allele calling)
- Only processes chromosome 22 (CYP2D6) currently
- Doesn't account for copy number variations (CNVs)

---

### 2. Patient Profile Generation

**What We Do:**
- Create patient profiles with genetic information
- Include metabolizer status for key CYP enzymes
- Add medical conditions and lifestyle factors

**Example Profile:**
```
Patient ID: HG00096
Age: 45
CYP2D6 Status: Poor Metabolizer (*4/*4)
CYP2C19 Status: Extensive Metabolizer
CYP3A4 Status: Extensive Metabolizer
Medical Conditions: Chronic Liver Disease (Mild)
Lifestyle: Alcohol consumer (Moderate)
```

**Why This Matters:**
- LLM uses this profile to predict drug response
- Poor metabolizer status → higher risk predictions
- Medical conditions → additional risk factors

---

### 3. Drug Similarity Search

**What We Do:**
- Find similar drugs using molecular fingerprints
- Retrieve known side effects and interactions
- Use this context for LLM predictions

**Example:**
```python
# Find similar drugs
similar_drugs = find_similar_drugs(drug_fingerprint)
# Returns: ["Paracetamol", "Ibuprofen", "Aspirin"]

# LLM uses these to predict:
# - Similar drugs with known CYP interactions
# - Known side effects in poor metabolizers
# - Clinical guidelines for similar drugs
```

---

### 4. LLM-Based Prediction

**What We Do:**
- Use LLM to analyze drug + patient profile
- Compare to similar drugs with known effects
- Predict risk level and biological mechanism

**LLM Prompt Includes:**
- Drug name and structure (SMILES)
- Similar drugs with known effects
- Patient's genetic profile (CYP status)
- Medical conditions and lifestyle

**Output:**
- Risk Level: Low/Medium/High
- Predicted Reaction: Detailed analysis
- Biological Mechanism: How genetics affects drug metabolism

---

## Clinical Applications

### 1. Personalized Dosing

**Example:**
- Patient is CYP2D6 poor metabolizer
- Prescribed codeine (requires CYP2D6 for activation)
- System predicts: "Reduced efficacy, consider alternative"

**Real-World Impact:**
- FDA recommends genetic testing before prescribing codeine to children
- Some hospitals test CYP2D6 status before certain treatments

---

### 2. Drug Selection

**Example:**
- Patient is CYP2C19 poor metabolizer
- Prescribed clopidogrel (antiplatelet, requires CYP2C19)
- System predicts: "Reduced activation, consider prasugrel"

**Real-World Impact:**
- Some guidelines recommend alternative drugs for poor metabolizers
- Genetic testing becoming more common in cardiology

---

### 3. Toxicity Prediction

**Example:**
- Patient is CYP2D6 poor metabolizer
- Prescribed tamoxifen (breast cancer treatment)
- System predicts: "Reduced active metabolite, higher risk of recurrence"

**Real-World Impact:**
- Some oncologists test CYP2D6 before prescribing tamoxifen
- Alternative treatments available for poor metabolizers

---

## Limitations and Future Work

### Current Limitations

1. **Simplified Inference:**
   - Real systems use complex haplotype phasing
   - We use simplified variant counting
   - Doesn't account for all genetic factors

2. **Limited Gene Coverage:**
   - Only CYP2D6, CYP2C19, CYP3A4
   - Many other genes affect drug response
   - Doesn't account for drug transporters

3. **No Copy Number Variations:**
   - CYP2D6 has CNVs (some people have 0, 1, 2, 3+ copies)
   - Our system doesn't detect CNVs from VCF

4. **No Population-Specific Data:**
   - Allele frequencies vary by ancestry
   - Our system doesn't stratify by population

### Future Improvements

1. **Star Allele Calling:**
   - Implement proper haplotype phasing
   - Use PharmVar database for allele definitions
   - More accurate metabolizer status

2. **Extended Gene Coverage:**
   - Add CYP1A2, CYP2C9, CYP2E1
   - Add drug transporters (P-glycoprotein)
   - Add drug receptors

3. **CNV Detection:**
   - Detect copy number variations
   - Important for CYP2D6 (ultra-rapid metabolizers)

4. **Population Stratification:**
   - Account for ancestry-specific allele frequencies
   - More accurate predictions for diverse populations

---

## Key Resources

- **PharmVar:** Pharmacogene Variation Consortium - Official allele definitions
  - https://www.pharmvar.org/

- **CPIC:** Clinical Pharmacogenetics Implementation Consortium - Guidelines
  - https://cpicpgx.org/

- **PharmGKB:** Pharmacogenomics Knowledge Base - Drug-gene interactions
  - https://www.pharmgkb.org/

- **1000 Genomes Project:** Genomic data we use
  - https://www.internationalgenome.org/

---

## Glossary

- **Allele:** A variant form of a gene
- **Genotype:** The genetic makeup of an individual
- **Phenotype:** The observable characteristics (e.g., metabolizer status)
- **Haplotype:** A set of genetic variants inherited together
- **Star Allele:** Standard nomenclature for pharmacogene variants (*1, *2, *4, etc.)
- **CNV:** Copy Number Variation - having different numbers of gene copies
- **Substrate:** A drug that is metabolized by an enzyme
- **Inhibitor:** A drug that blocks an enzyme
- **Inducer:** A drug that increases enzyme production

---

*This document explains the pharmacogenomics concepts used in SynthaTrial. For implementation details, see `docs/implementation/`.*
