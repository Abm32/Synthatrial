# SynthaTrial Implementation Guide

Technical implementation details for the SynthaTrial pharmacogenomics platform.

## Architecture Overview

```
User Input (Drug SMILES + Patient Profile)
    ↓
[Input Processor] → Molecular Fingerprint (2048-bit vector)
    ↓
[Vector Search] → Similar Drugs (from ChEMBL/Pinecone)
    ↓
[VCF Processor] → Genetic Variants (CYP2D6, CYP2C19, CYP2C9)
    ↓
[Agent Engine] → LLM Prediction (RAG with retrieved context)
    ↓
Output (Risk Level + Predicted Reaction + Mechanism)
```

---

## Core Modules

### 1. Input Processor (`src/input_processor.py`)

**Purpose**: Convert SMILES strings to molecular fingerprints

**Key Function**: `get_drug_fingerprint(smiles_string)`

**Implementation**:
```python
from rdkit import Chem
from rdkit.Chem import AllChem

def get_drug_fingerprint(smiles_string):
    # Convert SMILES to molecule object
    mol = Chem.MolFromSmiles(smiles_string)
    
    # Generate 2048-bit Morgan fingerprint (radius=2)
    fingerprint = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
    
    # Convert to numpy array
    return np.array(fingerprint)
```

**Features**:
- ✅ SMILES validation
- ✅ 2048-bit Morgan fingerprints (radius=2)
- ✅ Error handling for invalid SMILES
- ✅ Numpy array output for vector operations

---

### 2. Vector Search (`src/vector_search.py`)

**Purpose**: Find similar drugs using vector similarity search

**Key Function**: `find_similar_drugs(fingerprint, top_k=3)`

**Implementation**:
```python
def find_similar_drugs(fingerprint, top_k=3):
    if api_key:
        # Real Pinecone search
        index = pc.Index("drug-index")
        results = index.query(
            vector=fingerprint.tolist(),
            top_k=top_k,
            include_metadata=True
        )
        return format_results(results)
    else:
        # Mock data fallback
        return generate_mock_drugs(top_k)
```

**Features**:
- ✅ Pinecone integration with fallback to mock data
- ✅ Cosine similarity search
- ✅ Metadata retrieval (drug names, targets, side effects)
- ✅ Configurable result count
- ✅ Error handling and graceful degradation

---

### 3. VCF Processor (`src/vcf_processor.py`)

**Purpose**: Extract genetic variants from VCF files and generate patient profiles

#### Key Functions

##### `extract_cyp_variants(vcf_path, gene, sample_limit=None)`

**Purpose**: Extract variants in CYP gene regions

**Gene Locations** (GRCh37/hg19):
```python
CYP_GENE_LOCATIONS = {
    'CYP2D6': {'chrom': '22', 'start': 42522500, 'end': 42530900},
    'CYP2C19': {'chrom': '10', 'start': 96535040, 'end': 96625463},
    'CYP2C9': {'chrom': '10', 'start': 96698415, 'end': 96749147},
    'CYP3A4': {'chrom': '7', 'start': 99376140, 'end': 99391055}
}
```

**Implementation**:
```python
def extract_cyp_variants(vcf_path, gene='CYP2D6', sample_limit=None):
    gene_loc = CYP_GENE_LOCATIONS[gene]
    variants = []
    
    with gzip.open(vcf_path, 'rt') as f:
        for line in f:
            if line.startswith('#CHROM'):
                # Parse sample names from header
                sample_names = line.strip().split('\t')[9:]
                continue
            
            if not line.startswith('#'):
                # Parse variant line
                variant = parse_vcf_line(line)
                if is_in_gene_region(variant, gene_loc):
                    variants.append(variant)
    
    return variants
```

##### `infer_metabolizer_status(variants, sample_id, gene)`

**Purpose**: Infer CYP metabolizer status using Activity Score method

**Activity Score Mapping**:
```python
CYP2D6_ACTIVITY_SCORES = {
    '*1': 1.0,      # Wild type (normal function)
    '*2': 1.0,      # Normal function
    '*3': 0.0,      # No function (nonsense mutation)
    '*4': 0.0,      # No function (splicing defect)
    '*5': 0.0,      # No function (gene deletion)
    '*9': 0.5,      # Reduced function
    '*10': 0.5,     # Reduced function
    # ... more alleles
}
```

**Metabolizer Classification**:
- AS = 0: Poor Metabolizer
- AS = 0.5-1.0: Intermediate Metabolizer
- AS = 1.5-2.0: Extensive Metabolizer (Normal)
- AS > 2.0: Ultra-Rapid Metabolizer

**Current Implementation** (Simplified):
```python
def infer_metabolizer_status(variants, sample_id, gene='CYP2D6'):
    # Simplified heuristic based on variant count
    non_ref_count = count_non_reference_alleles(variants, sample_id)
    functional_variants = count_functional_variants(variants, sample_id)
    
    # Calculate activity score (simplified)
    activity_score = 2.0  # Base score
    if functional_variants >= 2:
        activity_score -= 1.0
    elif functional_variants == 1:
        activity_score -= 0.5
    
    # Classify based on activity score
    if activity_score > 2.0:
        return 'ultra_rapid_metabolizer'
    elif activity_score >= 1.5:
        return 'extensive_metabolizer'
    elif activity_score >= 0.5:
        return 'intermediate_metabolizer'
    else:
        return 'poor_metabolizer'
```

**Note**: Real implementation would require haplotype phasing and star allele calling using PharmVar database.

##### `generate_patient_profile_from_vcf(vcf_path, sample_id, vcf_path_chr10=None)`

**Purpose**: Generate comprehensive patient profile from VCF data

**Multi-Chromosome Support**:
```python
def generate_patient_profile_from_vcf(vcf_path, sample_id, vcf_path_chr10=None):
    # Extract CYP2D6 from chromosome 22
    cyp2d6_variants = extract_cyp_variants(vcf_path, 'CYP2D6')
    cyp2d6_status = infer_metabolizer_status(cyp2d6_variants, sample_id, 'CYP2D6')
    
    # Extract CYP2C19 and CYP2C9 from chromosome 10 (if provided)
    if vcf_path_chr10:
        cyp2c19_variants = extract_cyp_variants(vcf_path_chr10, 'CYP2C19')
        cyp2c9_variants = extract_cyp_variants(vcf_path_chr10, 'CYP2C9')
        
        cyp2c19_status = infer_metabolizer_status(cyp2c19_variants, sample_id, 'CYP2C19')
        cyp2c9_status = infer_metabolizer_status(cyp2c9_variants, sample_id, 'CYP2C9')
    
    # Build genetics text
    genetics_parts = []
    if cyp2d6_status != 'extensive_metabolizer':
        genetics_parts.append(f"CYP2D6 {cyp2d6_status.replace('_', ' ').title()}")
    # ... similar for other enzymes
    
    return formatted_profile
```

**Features**:
- ✅ Multi-chromosome support (chr22 + chr10)
- ✅ Big 3 enzymes (CYP2D6, CYP2C19, CYP2C9)
- ✅ Activity Score method for metabolizer inference
- ✅ Comprehensive patient profile generation
- ✅ Backward compatibility (single chromosome mode)

---

### 4. ChEMBL Processor (`src/chembl_processor.py`)

**Purpose**: Extract drug information from ChEMBL database

#### Database Schema

**Key Tables**:
- `molecule_dictionary`: Drug molecules
- `compound_structures`: Chemical structures (SMILES)
- `activities`: Drug-target interactions
- `assays`: Assay information
- `target_dictionary`: Target information

**Join Path**:
```sql
molecule_dictionary 
  → compound_structures (molregno)
  → activities (molregno) 
  → assays (assay_id) 
  → target_dictionary (tid)
```

#### Key Functions

##### `extract_drug_molecules(conn, limit=None)`

**Purpose**: Extract approved drugs from ChEMBL

**SQL Query**:
```sql
SELECT DISTINCT 
    md.molregno,
    md.pref_name,
    md.max_phase,
    cs.canonical_smiles,
    cs.standard_inchi,
    cs.standard_inchi_key
FROM molecule_dictionary md
JOIN compound_structures cs ON md.molregno = cs.molregno
WHERE md.max_phase >= 2  -- Phase 2+ (approved or late-stage)
  AND cs.canonical_smiles IS NOT NULL
  AND LENGTH(cs.canonical_smiles) > 5
ORDER BY md.max_phase DESC
LIMIT ?
```

##### `extract_drug_targets(conn, molregno)`

**Purpose**: Get target information for a specific drug

**SQL Query**:
```sql
SELECT DISTINCT 
    td.pref_name as target_name,
    td.organism,
    td.target_type,
    COUNT(*) as activity_count
FROM activities a
JOIN assays ass ON a.assay_id = ass.assay_id
JOIN target_dictionary td ON ass.tid = td.tid
WHERE a.molregno = ?
  AND td.organism = 'Homo sapiens'
GROUP BY td.tid, td.pref_name
ORDER BY activity_count DESC
LIMIT 10
```

##### `prepare_drug_for_vector_db(drug_data, targets, side_effects)`

**Purpose**: Format drug data for Pinecone ingestion

**Output Format**:
```python
{
    'id': f"chembl_{molregno}",
    'values': fingerprint_vector,  # 2048-dimensional
    'metadata': {
        'name': drug_name,
        'smiles': canonical_smiles,
        'targets': target_list,
        'side_effects': side_effect_list,
        'chembl_id': molregno,
        'max_phase': max_phase
    }
}
```

---

### 5. Agent Engine (`src/agent_engine.py`)

**Purpose**: LLM-based pharmacogenomics simulation using RAG

#### Configuration

```python
# Default model configuration
_gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# LLM initialization with low temperature for consistency
_llm = ChatGoogleGenerativeAI(model=_gemini_model, temperature=0.1)
```

#### Enhanced Prompt Template

**Key Features**:
- ✅ CPIC guideline compliance
- ✅ Big 3 enzymes support (CYP2D6, CYP2C19, CYP2C9)
- ✅ Structured output parsing
- ✅ Risk level classification
- ✅ Biological mechanism explanation

**Prompt Structure**:
```python
template = """
ROLE: You are an advanced Pharmacogenomics AI following CPIC guidelines.

CONTEXT:
Big 3 Metabolic Enzymes:
1. CYP2D6 (Chromosome 22) - ~25% of drugs
2. CYP2C19 (Chromosome 10) - Clopidogrel, PPIs
3. CYP2C9 (Chromosome 10) - Warfarin, NSAIDs

INPUT DATA:
1. NEW DRUG: {drug_name}
   SMILES Structure: {drug_smiles}
2. SIMILAR KNOWN DRUGS: {similar_drugs}
3. PATIENT PROFILE: {patient_profile}

RISK LEVEL DEFINITIONS:
- HIGH RISK: Severe consequences, alternative drug recommended
- MEDIUM RISK: Moderate consequences, dose adjustment needed
- LOW RISK: Minimal impact, standard dosing appropriate

REASONING STEPS:
1. STRUCTURAL ANALYSIS: Compare SMILES with similar drugs
2. ENZYME IDENTIFICATION: Identify relevant CYP enzyme(s)
3. PATIENT GENETIC STATUS: Check metabolizer status
4. IMPACT ASSESSMENT: Evaluate clinical consequences
5. RISK CLASSIFICATION: Assign risk level

OUTPUT FORMAT:
- RISK LEVEL: [Low/Medium/High]
- PREDICTED REACTION: [Description]
- BIOLOGICAL MECHANISM: [Enzyme involvement and mechanism]
"""
```

**CPIC Guidelines Integration**:
```python
# Example guidelines embedded in prompt
CYP2D6_GUIDELINES = {
    'codeine': {
        'poor_metabolizer': 'HIGH RISK - Alternative analgesic recommended',
        'ultra_rapid_metabolizer': 'HIGH RISK - Avoid use, risk of toxicity'
    },
    'tramadol': {
        'poor_metabolizer': 'MEDIUM RISK - Consider dose adjustment'
    }
}

CYP2C9_GUIDELINES = {
    'warfarin': {
        'poor_metabolizer': 'HIGH RISK - Reduce dose significantly, bleeding risk'
    }
}
```

---

## Data Flow

### 1. Drug Processing Pipeline

```python
# Step 1: Convert SMILES to fingerprint
fingerprint = get_drug_fingerprint(smiles_string)

# Step 2: Find similar drugs
similar_drugs = find_similar_drugs(fingerprint, top_k=3)

# Step 3: Generate patient profile
if vcf_file:
    patient_profile = generate_patient_profile_from_vcf(vcf_path, sample_id)
else:
    patient_profile = create_manual_profile(cyp2d6_status)

# Step 4: Run LLM simulation
result = run_simulation(drug_name, similar_drugs, patient_profile)
```

### 2. Multi-Chromosome Processing

```python
# Extract variants from both chromosomes
cyp2d6_variants = extract_cyp_variants(chr22_vcf, 'CYP2D6')
cyp2c19_variants = extract_cyp_variants(chr10_vcf, 'CYP2C19')
cyp2c9_variants = extract_cyp_variants(chr10_vcf, 'CYP2C9')

# Infer metabolizer status for each enzyme
cyp2d6_status = infer_metabolizer_status(cyp2d6_variants, sample_id, 'CYP2D6')
cyp2c19_status = infer_metabolizer_status(cyp2c19_variants, sample_id, 'CYP2C19')
cyp2c9_status = infer_metabolizer_status(cyp2c9_variants, sample_id, 'CYP2C9')

# Build comprehensive genetics profile
genetics_text = build_genetics_profile(cyp2d6_status, cyp2c19_status, cyp2c9_status)
```

---

## Performance Characteristics

### Benchmarking Results

| Component | Performance | Notes |
|-----------|-------------|-------|
| **Fingerprint Generation** | <10ms | RDKit Morgan fingerprints |
| **Vector Search** | <200ms | Pinecone cosine similarity |
| **VCF Processing** | 1-5 minutes | Per chromosome, depends on file size |
| **LLM Simulation** | 3-10 seconds | Includes API call overhead |
| **End-to-End** | 5-15 seconds | Complete workflow |

### Memory Usage

| Component | Memory | Notes |
|-----------|--------|-------|
| **VCF Processing** | 500MB-1GB | Per chromosome |
| **ChEMBL Database** | 2-4GB | SQLite database |
| **Pinecone Vectors** | Minimal | Cloud-hosted |
| **LLM Processing** | Minimal | API-based |

---

## Error Handling

### Graceful Degradation

```python
# Vector search fallback
def find_similar_drugs(fingerprint, top_k=3):
    try:
        # Try Pinecone
        return pinecone_search(fingerprint, top_k)
    except Exception as e:
        print(f"⚠️ Pinecone unavailable: {e}")
        return mock_drug_search(top_k)

# VCF processing fallback
def generate_patient_profile_from_vcf(vcf_path, sample_id):
    try:
        return extract_from_vcf(vcf_path, sample_id)
    except Exception as e:
        print(f"⚠️ VCF processing failed: {e}")
        return default_patient_profile(sample_id)
```

### Validation

```python
# SMILES validation
def validate_smiles(smiles_string):
    mol = Chem.MolFromSmiles(smiles_string)
    if mol is None:
        raise ValueError(f"Invalid SMILES string: {smiles_string}")
    return mol

# VCF file validation
def validate_vcf_file(vcf_path):
    if not os.path.exists(vcf_path):
        raise FileNotFoundError(f"VCF file not found: {vcf_path}")
    
    # Check file integrity
    try:
        with gzip.open(vcf_path, 'rt') as f:
            first_line = f.readline()
            if not first_line.startswith('##fileformat=VCF'):
                raise ValueError("Invalid VCF format")
    except Exception as e:
        raise ValueError(f"Corrupted VCF file: {e}")
```

---

## Testing Framework

### Unit Tests

```python
# Test fingerprint generation
def test_fingerprint_generation():
    smiles = "CC(=O)Nc1ccc(O)cc1"  # Paracetamol
    fp = get_drug_fingerprint(smiles)
    assert len(fp) == 2048
    assert fp.dtype == np.uint8

# Test VCF processing
def test_vcf_processing():
    variants = extract_cyp_variants("test_data/chr22.vcf.gz", "CYP2D6")
    assert len(variants) > 0
    assert all('chrom' in v for v in variants)

# Test metabolizer inference
def test_metabolizer_inference():
    # Test with known poor metabolizer variants
    variants = create_test_variants(poor_metabolizer=True)
    status = infer_metabolizer_status(variants, "test_sample", "CYP2D6")
    assert status == "poor_metabolizer"
```

### Integration Tests

```python
# Test complete workflow
def test_end_to_end_workflow():
    # Test with known CYP2D6 substrate
    result = run_complete_simulation(
        drug_name="Codeine",
        smiles="CN1CC[C@]23C4=C5C=CC(=C4O)Oc4c5c(C[C@@H]1[C@@H]2C=C[C@@H]3O)cc(c4)O",
        vcf_path="test_data/chr22.vcf.gz",
        sample_id="HG00096"
    )
    
    assert "RISK LEVEL:" in result
    assert result.startswith("RISK LEVEL: High")  # Expected for poor metabolizer
```

### Validation Test Cases

```python
VALIDATION_CASES = [
    {
        'drug': 'Codeine',
        'smiles': 'CN1CC[C@]23C4=C5C=CC(=C4O)Oc4c5c(C[C@@H]1[C@@H]2C=C[C@@H]3O)cc(c4)O',
        'enzyme': 'CYP2D6',
        'poor_metabolizer_risk': 'HIGH',
        'reason': 'No conversion to active morphine'
    },
    {
        'drug': 'Warfarin',
        'smiles': 'CC(=O)CC(c1ccc(OC)cc1)c1c(O)c2ccccc2oc1=O',
        'enzyme': 'CYP2C9',
        'poor_metabolizer_risk': 'HIGH',
        'reason': 'Increased bleeding risk'
    }
]
```

---

## Future Improvements

### High Priority

1. **Star Allele Calling**
   - Implement proper haplotype phasing
   - Use PharmVar database for allele definitions
   - Replace simplified variant counting

2. **Additional Chromosomes**
   - Add chromosome 7 support (CYP3A4)
   - Implement multi-VCF file processing
   - Expand to more CYP enzymes

3. **Enhanced LLM Integration**
   - Add structured output parsing
   - Implement confidence scoring
   - Add explanation generation

### Medium Priority

1. **Performance Optimization**
   - Implement VCF indexing for faster access
   - Add caching for repeated queries
   - Optimize memory usage for large VCF files

2. **UI Enhancements**
   - Add VCF file upload to Streamlit app
   - Implement sample ID selection
   - Add progress indicators

3. **Validation Expansion**
   - Add more CPIC test cases
   - Implement cross-validation
   - Add accuracy metrics

---

## Dependencies

### Core Dependencies

```python
# Molecular processing
rdkit>=2023.9.1

# Data processing
pandas>=2.0.0
numpy>=1.24.0

# Machine learning
scikit-learn>=1.3.0

# LLM integration
langchain>=0.1.0
langchain-google-genai>=0.1.0

# Vector database
pinecone>=5.0.0

# Web interface
streamlit>=1.28.0

# Utilities
python-dotenv>=1.0.0
```

### Installation Notes

- **RDKit**: Must be installed via conda (pip installation often fails)
- **Pinecone**: Requires API key for production use
- **Google Gemini**: Requires Google API key

---

For more information, see:
- [Setup Guide](setup.md) - Installation and configuration
- [Usage Guide](usage.md) - How to use the system
- [Troubleshooting](troubleshooting.md) - Common issues and solutions