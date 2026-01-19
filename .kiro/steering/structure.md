# Project Structure

## Directory Organization

```
SynthaTrial/
├── .env                       # Environment variables (create from .env.example)
├── .env.example              # Environment template
├── README.md                 # Main project documentation
├── requirements.txt          # Python dependencies
├── app.py                    # Streamlit web interface
├── main.py                   # CLI entry point
├── src/                      # Core application modules
│   ├── __init__.py
│   ├── input_processor.py    # SMILES → Molecular fingerprint conversion
│   ├── vector_search.py      # Pinecone similarity search
│   ├── agent_engine.py       # LLM-based pharmacogenomics simulation
│   ├── vcf_processor.py      # VCF file processing and genetic analysis
│   ├── variant_db.py         # Targeted variant lookup database (PharmVar Tier 1)
│   └── chembl_processor.py   # ChEMBL database integration
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── quick_test.py         # Quick integration tests
│   └── validation_tests.py   # Comprehensive validation suite
├── scripts/                  # Utility and setup scripts
│   ├── README.md
│   ├── setup_pinecone_index.py      # Pinecone index creation
│   ├── ingest_chembl_to_pinecone.py # ChEMBL data ingestion
│   ├── list_models.py               # Available LLM models
│   ├── list_models_v2.py            # Enhanced model listing with API queries
│   ├── benchmark_performance.py     # Performance benchmarking (vector retrieval, LLM, end-to-end)
│   ├── test_chromosome10.py         # Big 3 enzymes integration testing
│   ├── check_vcf_integrity.py       # VCF file validation and integrity checking
│   └── generate_validation_results.py # CPIC guideline validation and accuracy metrics
├── data/                     # Data storage (create directories as needed)
│   ├── chembl/              # ChEMBL database files
│   │   └── chembl_34_sqlite/
│   │       └── chembl_34.db
│   └── genomes/             # VCF genomic data files
│       ├── ALL.chr22.*.vcf.gz  # Chromosome 22 (CYP2D6)
│       └── ALL.chr10.*.vcf.gz  # Chromosome 10 (CYP2C19, CYP2C9)
└── docs/                    # Comprehensive documentation
    ├── README.md            # Documentation index
    ├── setup.md             # Complete setup and installation guide (includes quick start)
    ├── usage.md             # Usage examples and CLI reference (includes run modes)
    ├── implementation.md    # Technical implementation details
    ├── troubleshooting.md   # Common issues and solutions
    ├── paper-review.md      # Research paper review and validation
    ├── concepts/            # Conceptual explanations
    │   ├── pharmacogenomics.md
    │   ├── rag_explained.md
    │   └── vector_databases.md
    └── paper/               # Research paper materials (remaining files)
        ├── FINAL_PAPER_REVIEW.md
        ├── FINAL_RESULTS_ANALYSIS.md
        └── VALIDATION_RESULTS.md
```

## Module Responsibilities

### Core Modules (`src/`)

- **`input_processor.py`**: Validates SMILES strings and converts to 2048-bit Morgan fingerprints using RDKit
- **`vector_search.py`**: Handles Pinecone vector database operations with mock mode fallback and enhanced metadata (SMILES, targets, side effects)
- **`agent_engine.py`**: LLM integration using LangChain and Google Gemini for pharmacogenomics analysis with enhanced CPIC guideline-based prompting, structural analysis using SMILES strings, and comprehensive drug interaction predictions
- **`vcf_processor.py`**: Processes VCF files to extract CYP enzyme variants and generate patient profiles. Supports multi-chromosome analysis (chromosomes 10 and 22) for Big 3 enzymes (CYP2D6, CYP2C19, CYP2C9) with targeted variant lookup and Activity Score method for CPIC-compliant metabolizer status inference
- **`variant_db.py`**: Targeted variant lookup database containing Tier 1 Clinical Variants (CPIC Level A) from PharmVar with activity scores and structural variant detection
- **`chembl_processor.py`**: Extracts drug information from ChEMBL SQLite database

### Entry Points

- **`app.py`**: Streamlit web interface with modern gradient UI, comprehensive patient profiling, example use cases, and enhanced user experience with real-time validation
- **`main.py`**: Command-line interface supporting both VCF and manual patient profiles. Supports single-chromosome (CYP2D6 only) and multi-chromosome (Big 3 enzymes) analysis with `--vcf-chr10` parameter for chromosome 10 data

### Testing (`tests/`)

- **`quick_test.py`**: Fast integration tests for imports, file existence, and basic functionality
- **`validation_tests.py`**: Comprehensive test suite with known CYP2D6 substrates and expected outcomes

### Scripts (`scripts/`)

- **`setup_pinecone_index.py`**: Creates Pinecone index with correct configuration (2048 dimensions, cosine metric)
- **`ingest_chembl_to_pinecone.py`**: Batch ingestion of ChEMBL drugs into Pinecone vector database
- **`list_models.py`**: Lists available Gemini models for testing different LLM versions
- **`list_models_v2.py`**: Enhanced model listing with direct API queries and detailed model information
- **`test_chromosome10.py`**: Comprehensive testing suite for Big 3 enzymes integration and multi-chromosome functionality
- **`check_vcf_integrity.py`**: Validates VCF file integrity, checks for corruption, and verifies download completeness with detailed reporting
- **`generate_validation_results.py`**: Generates comprehensive validation results for research and paper documentation with CPIC compliance metrics
- **`benchmark_performance.py`**: Performance benchmarking for single and multi-chromosome processing with detailed timing analysis

### Documentation (`docs/`)

- **`README.md`**: Documentation index and navigation guide
- **`setup.md`**: Complete setup and installation guide (consolidated from multiple setup files, includes quick start)
- **`usage.md`**: Usage examples and CLI reference with comprehensive test cases (includes run modes guide)
- **`implementation.md`**: Technical implementation details and architecture (consolidated from multiple implementation files)
- **`troubleshooting.md`**: Common issues and solutions (consolidated from multiple troubleshooting files)
- **`paper-review.md`**: Research paper review and validation results (consolidated from multiple paper files)
- **`concepts/`**: Conceptual explanations (pharmacogenomics, RAG, vector databases)

## File Naming Conventions

- **Python modules**: Snake case (e.g., `input_processor.py`)
- **Classes**: Pascal case (e.g., `DrugProcessor`)
- **Functions**: Snake case (e.g., `get_drug_fingerprint`)
- **Constants**: Upper snake case (e.g., `VALIDATION_CASES`)
- **Data files**: Descriptive names with appropriate extensions (e.g., `chembl_34.db`, `chr22.vcf.gz`, `chr10.vcf.gz`)

## Import Patterns

```python
# Standard library imports first
import os
import sys
from typing import List

# Third-party imports
import pandas as pd
from rdkit import Chem
from langchain_google_genai import ChatGoogleGenerativeAI

# Local imports last
from src.input_processor import get_drug_fingerprint
from src.vector_search import find_similar_drugs
```

## Configuration Management

- **Environment variables**: Stored in `.env` file, loaded via `python-dotenv`
- **Default values**: Provided for optional configurations (e.g., `GEMINI_MODEL`)
- **Graceful fallbacks**: Mock modes when API keys are missing
- **Validation**: Check for required files and configurations at runtime

## Error Handling Patterns

- **Descriptive error messages**: Include specific guidance for resolution
- **Graceful degradation**: Continue with reduced functionality when possible
- **User-friendly output**: Clear status messages and progress indicators
- **Exception chaining**: Preserve original error context while providing user guidance