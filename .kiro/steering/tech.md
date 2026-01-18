# Technology Stack

## Core Technologies

- **Python 3.10+** - Primary language
- **RDKit** - Molecular fingerprinting and cheminformatics
- **Pinecone** - Vector similarity search database
- **Google Gemini** - LLM for pharmacogenomics analysis (default: gemini-2.5-flash, supports gemini-1.5-flash, gemini-2.5-pro)
- **LangChain** - LLM integration framework with enhanced RAG capabilities
- **Streamlit** - Modern web interface with gradient styling and comprehensive UX
- **SQLite** - ChEMBL database storage
- **Multi-chromosome VCF processing** - Big 3 enzymes support (CYP2D6, CYP2C19, CYP2C9)
- **Activity Score method** - CPIC/PharmVar guideline-based metabolizer status inference

## Key Dependencies

```
rdkit>=2023.9.1
pandas>=2.0.0
scipy>=1.11.0
scikit-learn>=1.3.0
langchain>=0.1.0
langchain-google-genai>=0.1.0
pinecone>=5.0.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
streamlit>=1.28.0
```

## Environment Setup

### Installation
```bash
# Create conda environment (required for RDKit)
conda create -n synthatrial python=3.10
conda activate synthatrial

# Install RDKit via conda (required)
conda install -c conda-forge rdkit pandas scipy scikit-learn

# Install other dependencies via pip
pip install langchain langchain-google-genai pinecone-client python-dotenv streamlit
```

### Environment Variables
Create `.env` file with:
```bash
GOOGLE_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key  # Optional (mock mode if missing)
PINECONE_INDEX=drug-index
GEMINI_MODEL=gemini-2.5-flash  # Optional, defaults to gemini-2.5-flash
```

## Common Commands

### Setup Commands
```bash
# Setup Pinecone index
python scripts/setup_pinecone_index.py

# Ingest ChEMBL data to Pinecone
python scripts/ingest_chembl_to_pinecone.py

# Download VCF data (chromosome 22 - CYP2D6)
curl -L https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz -o data/genomes/chr22.vcf.gz

# Download VCF data (chromosome 10 - CYP2C19, CYP2C9) - NEW
curl -L https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz -o data/genomes/chr10.vcf.gz

# Download ChEMBL database (optional)
curl -L https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_34/chembl_34_sqlite.tar.gz -o data/chembl/chembl_34_sqlite.tar.gz
tar -xvzf data/chembl/chembl_34_sqlite.tar.gz -C data/chembl/

# Verify VCF file integrity (optional)
python scripts/check_vcf_integrity.py data/genomes/chr10.vcf.gz
python scripts/check_vcf_integrity.py data/genomes/chr22.vcf.gz
```

### Running the Application
```bash
# Web interface (recommended)
streamlit run app.py

# Command line interface - Single chromosome (CYP2D6 only)
python main.py --vcf data/genomes/chr22.vcf.gz --sample-id HG00096

# Command line interface - Multi-chromosome (Big 3 enzymes: CYP2D6, CYP2C19, CYP2C9)
python main.py --vcf data/genomes/chr22.vcf.gz --vcf-chr10 data/genomes/chr10.vcf.gz --sample-id HG00096

# CYP2D6 status override (single enzyme)
python main.py --cyp2d6-status poor_metabolizer

# Test specific drug interactions
python main.py --vcf data/genomes/chr22.vcf.gz --vcf-chr10 data/genomes/chr10.vcf.gz --drug-name Warfarin --sample-id HG00096
python main.py --vcf data/genomes/chr22.vcf.gz --vcf-chr10 data/genomes/chr10.vcf.gz --drug-name Clopidogrel --sample-id HG00096
```

### Testing
```bash
# Quick integration test
python tests/quick_test.py

# Full validation suite
python tests/validation_tests.py

# Test chromosome 10 integration (Big 3 enzymes)
python scripts/test_chromosome10.py

# Check VCF file integrity
python scripts/check_vcf_integrity.py data/genomes/chr10.vcf.gz

# Generate CPIC guideline validation results
python scripts/generate_validation_results.py

# Benchmark performance metrics
python scripts/benchmark_performance.py

# List available Gemini models
python scripts/list_models.py
python scripts/list_models_v2.py
```

## Architecture Notes

- **Modular design**: Separate processors for input, vector search, VCF, ChEMBL, and AI engine
- **Multi-chromosome support**: Processes chromosome 22 (CYP2D6) and chromosome 10 (CYP2C19, CYP2C9) for Big 3 enzyme coverage
- **Activity Score method**: CPIC/PharmVar guideline-based metabolizer status inference
- **Lazy initialization**: LLM and database connections initialized when needed
- **Mock mode support**: Graceful fallback when API keys are missing with realistic example data
- **Error handling**: Comprehensive error handling with user-friendly messages
- **Batch processing**: Efficient batch operations for large datasets
- **Backward compatibility**: Single-chromosome mode maintained for existing workflows
- **Performance benchmarking**: Built-in tools for measuring vector retrieval, LLM simulation, and end-to-end timing
- **CPIC compliance**: Validation against Clinical Pharmacogenetics Implementation Consortium guidelines

## Development Guidelines

- Use conda for RDKit installation (pip installation often fails)
- Always check for API keys before making external calls
- Implement mock modes for testing without credentials
- Follow CPIC guidelines for pharmacogenomics predictions
- Use descriptive error messages for user guidance
- **Documentation**: Use streamlined structure in `docs/` - single files for setup, usage, implementation, troubleshooting, and paper review
- **Testing**: Run validation tests after changes (`python tests/validation_tests.py`)
- **Performance**: Use benchmarking tools to measure system performance (`python scripts/benchmark_performance.py`)