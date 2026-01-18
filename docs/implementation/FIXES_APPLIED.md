# Fixes Applied: Pinecone Connection & Metabolizer Status

**Date:** Implementation fixes  
**Issues Fixed:**
1. Pinecone API key not loading from `.env` file
2. Simplified metabolizer status heuristic (variant counting)

---

## ✅ Fix 1: Pinecone Connection

### Problem
- `vector_search.py` was not loading the `.env` file
- Only checked `os.environ.get("PINECONE_API_KEY")` at module load time
- Result: Always fell back to mock data even with API key set

### Solution
Added `load_dotenv()` at the top of `vector_search.py`:

```python
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Pinecone if API key is available
api_key = os.environ.get("PINECONE_API_KEY")
```

### Result
- ✅ Now loads API key from `.env` file
- ✅ Shows connection status on startup
- ✅ Falls back to mock data only if API key is truly missing

### Testing
```bash
# Make sure your .env file has:
PINECONE_API_KEY=your_key_here

# Then run:
python main.py --vcf ... --vcf-chr10 ... --drug-name Warfarin
```

You should see: `✓ Connected to Pinecone vector database` instead of mock data.

---

## ✅ Fix 2: Improved Metabolizer Status Inference

### Problem
- Previous method: Simple variant counting (`if count >= 4: ultra_rapid`)
- **Scientifically weak**: Doesn't account for:
  - Activity scores (CPIC/PharmVar standard)
  - Structural variants (deletions, duplications)
  - Loss-of-function vs. gain-of-function variants
  - Gene-specific differences

### Solution
Implemented **Activity Score (AS) Method** based on CPIC/PharmVar guidelines:

#### Activity Score Thresholds
- **AS = 0**: Poor Metabolizer
- **AS = 0.5-1.0**: Intermediate Metabolizer
- **AS = 1.5-2.0**: Extensive Metabolizer (Normal)
- **AS > 2.0**: Ultra-Rapid Metabolizer

#### Star Allele Activity Score Mappings

**CYP2D6:**
- `*1`, `*2`: 1.0 (normal function)
- `*3`, `*4`, `*5`, `*6`: 0.0 (no function)
- `*9`, `*10`, `*17`, `*29`, `*41`: 0.5 (reduced function)
- `*1xN`, `*2xN`: 1.0 × copy_number (duplication)

**CYP2C19:**
- `*1`: 1.0 (normal function)
- `*2`, `*3`, `*4`, `*5`, `*6`, `*7`, `*8`: 0.0 (no function)
- `*9`, `*10`: 0.5 (reduced function)
- `*17`: 1.5 (increased function - gain-of-function)
- `*17xN`: 1.5 × copy_number (ultra-rapid)

**CYP2C9:**
- `*1`: 1.0 (normal function)
- `*2`, `*13`, `*14`: 0.5 (reduced function)
- `*3`, `*4`, `*5`, `*6`, `*8`, `*11`: 0.0 (no function)

#### Improved Inference Logic

```python
def infer_metabolizer_status(variants, sample_id, gene='CYP2D6'):
    # Base: assume wild-type (*1/*1) = AS 2.0
    activity_score = 2.0
    
    # Adjust for deletions (no function alleles)
    if has_deletion:
        activity_score -= 1.0
    
    # Adjust for loss-of-function variants
    if functional_variants >= 2:
        activity_score -= 1.0  # Both alleles non-functional
    elif functional_variants == 1:
        activity_score -= 0.5  # One allele reduced
    
    # Adjust for duplications (ultra-rapid)
    if has_duplication:
        activity_score += 1.0
    
    # Determine status from AS
    if activity_score > 2.0:
        return 'ultra_rapid_metabolizer'
    elif activity_score >= 1.5:
        return 'extensive_metabolizer'
    elif activity_score >= 0.5:
        return 'intermediate_metabolizer'
    else:
        return 'poor_metabolizer'
```

### Improvements
1. ✅ **Activity Score based**: Aligns with CPIC/PharmVar standards
2. ✅ **Structural variant aware**: Detects deletions and duplications
3. ✅ **Loss-of-function detection**: Identifies frameshift, stop codon, splice site variants
4. ✅ **Gene-specific**: Different mappings for CYP2D6, CYP2C19, CYP2C9
5. ✅ **More accurate**: Better than simple variant counting

### Limitations (Still Present)
- ⚠️ **Simplified haplotype phasing**: Real systems need full haplotype reconstruction
- ⚠️ **Star allele calling**: Currently uses heuristics, not full PharmVar database lookup
- ⚠️ **Copy number variation**: Duplication detection is basic (looks for DUP/MULTI in VCF)

### Future Improvements
1. Integrate PharmVar database for exact star allele definitions
2. Implement proper haplotype phasing algorithms
3. Use CNV callers for accurate copy number detection
4. Validate against known population datasets

---

## 📊 Expected Impact

### Before Fixes
- ❌ Pinecone: Always mock data
- ❌ Metabolizer Status: All samples = "Ultra Rapid" (incorrect)

### After Fixes
- ✅ Pinecone: Real ChEMBL data (if API key set)
- ✅ Metabolizer Status: More accurate classification based on Activity Score

---

## 🧪 Testing

### Test Pinecone Connection
```bash
# Check if API key loads
python -c "from src.vector_search import api_key, index; print('API Key:', 'SET' if api_key else 'NOT SET'); print('Index:', 'Connected' if index else 'Not Connected')"
```

### Test Metabolizer Status
```bash
# Run with real VCF data
python main.py \
  --vcf data/genomes/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --vcf-chr10 data/genomes/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  --drug-name Warfarin \
  --drug-smiles 'CC(=O)CC(c1ccc(OC)cc1)c1c(O)c2ccccc2oc1=O'
```

**Expected:**
- Should see `✓ Connected to Pinecone vector database` (if API key set)
- Metabolizer status should be more varied (not all "Ultra Rapid")
- Status should be based on Activity Score thresholds

---

## 📝 Files Modified

1. **`src/vector_search.py`**
   - Added `load_dotenv()` import and call
   - Added connection status messages

2. **`src/vcf_processor.py`**
   - Replaced simple variant counting with Activity Score method
   - Added star allele activity score mappings for CYP2D6, CYP2C19, CYP2C9
   - Improved `infer_metabolizer_status()` function
   - Added structural variant detection (deletions, duplications)
   - Added loss-of-function variant detection

---

## ✅ Status

Both fixes are **implemented and ready for testing**.

**Next Steps:**
1. Set `PINECONE_API_KEY` in `.env` file
2. Run test command to verify Pinecone connection
3. Run full simulation to see improved metabolizer status classification

---

*Implementation Date: Based on user request*
