# VCF and ChEMBL Integration Setup Guide

This guide explains how to set up and use the VCF file processing and ChEMBL database integration features.

## Prerequisites

1. **VCF File**: Chromosome 22 VCF file from 1000 Genomes Project
   - Already downloaded: `data/genomes/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz`
   - If missing, download from: https://www.internationalgenome.org/

2. **ChEMBL Database**: ChEMBL SQLite database
   - Already downloaded: `data/chembl/chembl_34_sqlite.tar.gz`
   - If missing, extract it:
     ```bash
     cd data/chembl
     tar -xvzf chembl_34_sqlite.tar.gz
     ```
   - The database should be at: `data/chembl/chembl_34_sqlite/chembl_34.db`

3. **Pinecone Account**: For vector database (free tier available)
   - Sign up at: https://www.pinecone.io/
   - Create an index named `drug-index` with 2048 dimensions

## Step 1: Extract ChEMBL Data to Pinecone

Run the ingestion script to populate Pinecone with real drug data:

```bash
# Make sure PINECONE_API_KEY is set
export PINECONE_API_KEY="your_pinecone_api_key"

# Run ingestion (this may take 10-30 minutes for 1000 drugs)
python ingest_chembl_to_pinecone.py
```

**Note**: By default, this ingests 1000 drugs. To ingest more:
```bash
export CHEMBL_LIMIT=5000  # Increase limit
python ingest_chembl_to_pinecone.py
```

## Step 2: Test VCF Processing

Test that VCF file processing works:

```bash
python -c "
from src.vcf_processor import get_sample_ids_from_vcf
samples = get_sample_ids_from_vcf('data/genomes/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz', limit=5)
print(f'Found {len(samples)} samples: {samples}')
"
```

## Step 3: Run Validation Tests

Run the complete validation test suite:

```bash
python tests/validation_tests.py
```

This will test:
- Drug fingerprint generation
- Vector similarity search
- CYP2D6 poor metabolizer scenarios
- VCF file processing
- ChEMBL database integration

## Step 4: Use VCF-Derived Patient Profiles

### Command Line (main.py)

```bash
# Use VCF file to generate patient profile
python main.py --vcf data/genomes/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz --sample-id HG00096

# Or use manual profile (default)
python main.py --cyp2d6-status poor_metabolizer
```

### Streamlit UI

The Streamlit UI (`app.py`) currently uses manual patient profiles. To add VCF support to the UI, you would need to:
1. Add a file uploader for VCF files
2. Add sample ID selector
3. Call `generate_patient_profile_from_vcf()` when VCF is provided

## Architecture Overview

### VCF Processing (`src/vcf_processor.py`)
- Parses VCF files (supports .gz compression)
- Extracts variants in CYP gene regions
- Infers metabolizer status from variants
- Generates patient profiles from genomic data

**CYP Gene Locations**:
- CYP2D6: Chromosome 22 (42522500-42530900)
- CYP2C19: Chromosome 10 (96541615-96561468)
- CYP3A4: Chromosome 7 (99376140-99391055)

### ChEMBL Processing (`src/chembl_processor.py`)
- Connects to ChEMBL SQLite database
- Extracts approved drugs (phase 2+)
- Retrieves drug-target interactions
- Generates molecular fingerprints
- Prepares data for Pinecone ingestion

### Vector Database Ingestion (`ingest_chembl_to_pinecone.py`)
- Extracts drugs from ChEMBL
- Generates fingerprints for each drug
- Ingests into Pinecone with metadata
- Includes drug names, targets, side effects

## Troubleshooting

### VCF File Issues

**Problem**: "VCF file not found"
- **Solution**: Ensure VCF file is in `data/genomes/` directory
- Check file name matches expected pattern

**Problem**: "No variants found in CYP2D6 region"
- **Solution**: This may be normal - CYP2D6 region is small
- Try extracting from a larger region or different chromosome

**Problem**: VCF parsing is slow
- **Solution**: VCF files are large. Processing may take several minutes
- Consider limiting sample count: `sample_limit=10`

### ChEMBL Database Issues

**Problem**: "ChEMBL database not found"
- **Solution**: Extract the tar.gz file:
  ```bash
  cd data/chembl
  tar -xvzf chembl_34_sqlite.tar.gz
  ```

**Problem**: "No drugs extracted"
- **Solution**: Check database file is not corrupted
- Verify SQLite can open the file: `sqlite3 data/chembl/chembl_34_sqlite/chembl_34.db`

**Problem**: Ingestion fails
- **Solution**: Check Pinecone API key is set correctly
- Verify index exists and has 2048 dimensions
- Check Pinecone dashboard for errors

### Pinecone Issues

**Problem**: "Index not found"
- **Solution**: Create index in Pinecone dashboard:
  - Name: `drug-index`
  - Dimensions: `2048`
  - Metric: `cosine`

**Problem**: "Rate limit exceeded"
- **Solution**: Reduce batch size or add delays between batches
- Free tier has rate limits

## Performance Notes

- **VCF Processing**: ~1-5 minutes per chromosome (depends on file size)
- **ChEMBL Extraction**: ~10-30 minutes for 1000 drugs
- **Pinecone Ingestion**: ~5-15 minutes for 1000 drugs (depends on network)
- **Vector Search**: <200ms (as claimed in paper)
- **LLM Simulation**: ~3-10 seconds per patient

## Next Steps

1. ✅ VCF processing implemented
2. ✅ ChEMBL integration implemented
3. ✅ Pinecone ingestion script created
4. ✅ Validation tests created
5. 🔄 Consider adding more chromosomes (CYP2C19, CYP3A4)
6. 🔄 Implement star allele calling for more accurate CYP2D6 status
7. 🔄 Add UI support for VCF file upload

## References

- 1000 Genomes Project: https://www.internationalgenome.org/
- ChEMBL Database: https://www.ebi.ac.uk/chembl/
- Pinecone: https://www.pinecone.io/
- CYP2D6 Allele Nomenclature: https://www.pharmvar.org/gene/CYP2D6
