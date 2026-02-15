# SynthaTrial Documentation

Welcome to the SynthaTrial documentation. This directory contains comprehensive documentation organized for easy navigation.

> **⚠️ Safety disclaimer**  
> **SynthaTrial is a research prototype.** It is a simulation and explanation engine, not a certified pharmacogenomics predictor. All outputs are synthetic predictions and **must not be used for clinical decision-making**, diagnosis, or treatment. Not for use as medical advice software.

## 📚 Documentation Structure

```
docs/
├── README.md              # This file - documentation index
├── setup.md               # Complete setup and installation guide
├── usage.md               # Usage examples and CLI reference
├── implementation.md      # Technical implementation details
├── troubleshooting.md     # Common issues and solutions
├── DEPLOYMENT_DATA.md     # VCF and ChEMBL data when deploying (Docker, volumes)
├── VCF_CHROMOSOME_SET.md  # Recommended chromosome set (v5b, gold standard)
├── paper-review.md        # Research paper review and validation
└── concepts/              # Conceptual explanations
    ├── pharmacogenomics.md
    ├── rag_explained.md
    └── vector_databases.md
```

---

## 🚀 Quick Start

**New to SynthaTrial?** Follow this path:

1. **[Setup Guide](setup.md)** - Install dependencies and configure the system
2. **[Usage Guide](usage.md)** - Learn how to run simulations and interpret results
3. **[Concepts](concepts/)** - Understand the underlying science and technology

**Having Issues?** Check the **[Troubleshooting Guide](troubleshooting.md)**

---

## 📖 Documentation by Purpose

### Getting Started
- **[Setup Guide](setup.md)** - Complete installation and configuration
  - Environment setup (conda, pip)
  - API key configuration
  - Data download (VCF files, ChEMBL database)
  - Verification and testing

### Using the System
- **[Usage Guide](usage.md)** - How to run pharmacogenomics simulations
  - Web interface (Streamlit)
  - Command-line interface
  - Example test cases
  - API usage (Python)

### Deploying
- **[Deployment data](DEPLOYMENT_DATA.md)** - VCF and ChEMBL data when deploying (Docker, volumes)
- **[Docker guide](docker.md)** - Containers, Compose, SSL

### Understanding the Technology
- **[Implementation Guide](implementation.md)** - Technical details
  - Architecture overview
  - Module responsibilities
  - Data flow and processing
  - Performance characteristics

### Solving Problems
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions
  - Installation problems
  - API key issues
  - VCF file problems
  - Performance issues

### Research and Validation
- **[Paper Review](paper-review.md)** - Research paper analysis
  - Technical accuracy validation
  - Test results and benchmarks
  - Publication readiness assessment

### Conceptual Background
- **[Pharmacogenomics](concepts/pharmacogenomics.md)** - Science behind the system
- **[RAG Explained](concepts/rag_explained.md)** - Retrieval-Augmented Generation
- **[Vector Databases](concepts/vector_databases.md)** - Molecular similarity search

---

## 🎯 Find What You Need

### "I want to..."

- **Set up the system** → [Setup Guide](setup.md)
- **Run a simulation** → [Usage Guide](usage.md)
- **Run the CPIC benchmark** → `python main.py --benchmark cpic_examples.json` ([Usage](usage.md#mode-3-evaluation-benchmark))
- **Deploy (Docker, VCF/ChEMBL data)** → [Deployment data](DEPLOYMENT_DATA.md)
- **Understand how it works** → [Implementation Guide](implementation.md)
- **Fix an error** → [Troubleshooting Guide](troubleshooting.md)
- **Learn the concepts** → [Concepts](concepts/)
- **Review the research** → [Paper Review](paper-review.md)

### "I'm getting an error..."

1. Check [Troubleshooting Guide](troubleshooting.md)
2. Search for your specific error message
3. Follow the solution steps
4. If not found, check relevant implementation docs

### "I want to understand..."

- **Pharmacogenomics** → [concepts/pharmacogenomics.md](concepts/pharmacogenomics.md)
- **Vector search** → [concepts/vector_databases.md](concepts/vector_databases.md)
- **RAG** → [concepts/rag_explained.md](concepts/rag_explained.md)
- **System architecture** → [implementation.md](implementation.md)

---

## 🔍 Key Features Covered

### Core Functionality
- **Molecular Analysis**: SMILES → Morgan fingerprints (RDKit)
- **Similarity Search**: Vector database search (Pinecone)
- **Genetic Profiling**: VCF file processing (1000 Genomes Project); auto-discovery for chr1–chr22, chrX, chrY
- **AI Simulation**: LLM-based simulation and explanation (Google Gemini) — *research prototype, not for clinical use*

### Pharmacogenomics Genes (multi-chromosome)
- **CYP2D6** (chr22), **CYP2C19** / **CYP2C9** (chr10), **UGT1A1** (chr2), **SLCO1B1** (chr12)
- **Big 3** (CYP2D6, CYP2C19, CYP2C9): ~60–70% of clinically used drugs
- Profile generation uses all available chromosome VCFs; see [VCF chromosome set](VCF_CHROMOSOME_SET.md) and [Deployment data](DEPLOYMENT_DATA.md)

### Variant Interpretation & Evaluation
- **Allele calling**: *1, *2, *4… with PharmVar/CPIC-style mapping (`ALLELE_FUNCTION_MAP` in `variant_db.py`)
- **Evaluation mode**: `python main.py --benchmark cpic_examples.json` — predicted vs expected phenotype, match %
- **CPIC-style examples**: `cpic_examples.json` for reproducible benchmarking
- **Test suite**: `tests/validation_tests.py`, `tests/quick_test.py`

---

## 📝 Documentation Standards

All documentation follows these principles:

1. **Clear Structure**: Organized with headers and sections
2. **Practical Examples**: Code examples for every concept
3. **Error Solutions**: Documents common errors and fixes
4. **Cross-References**: Links between related documents
5. **Up-to-Date**: Reflects current implementation

---

## 🔄 Quick Reference

### Essential Commands

```bash
# Setup
conda create -n synthatrial python=3.10
conda activate synthatrial
conda install -c conda-forge rdkit
pip install -r requirements.txt

# Data (optional)
python scripts/data_initializer.py --vcf chr22 chr10

# Run web interface
streamlit run app.py

# Run API (for UI backend)
python api.py   # or uvicorn api:app

# CLI simulation (auto-discovers data/genomes/ if present)
python main.py --drug-name Warfarin

# Evaluation mode
python main.py --benchmark cpic_examples.json

# Test system
python tests/quick_test.py
```

### Key Files

- **Applications**: `app.py` (Streamlit UI), `main.py` (CLI + benchmark), `api.py` (FastAPI)
- **Core**: `src/vcf_processor.py`, `src/variant_db.py`, `src/agent_engine.py`, `src/vector_search.py`
- **Benchmark**: `cpic_examples.json`
- **Tests**: `tests/validation_tests.py`, `tests/quick_test.py`
- **Setup**: `scripts/data_initializer.py`, `scripts/setup_pinecone_index.py`

### Important Paths

- **Data files**: `data/genomes/` (VCF), `data/chembl/` (database)
- **Configuration**: `.env` file (API keys)
- **Documentation**: `docs/` directory

---

## 🆘 Getting Help

### Self-Help Checklist

Before asking for help:

- ✅ Read the relevant documentation section
- ✅ Check [troubleshooting guide](troubleshooting.md)
- ✅ Run `python tests/quick_test.py`
- ✅ Verify API keys and file paths
- ✅ Check that conda environment is activated

### Debug Information

When reporting issues, include:

1. **Error message**: Full traceback
2. **System info**: `python --version`, `conda --version`
3. **Environment**: `conda list`
4. **File status**: `ls -la data/`
5. **Steps to reproduce**: Exact commands used

---

## 🎯 Documentation Roadmap

**Current Status**:
- ✅ Setup, usage, implementation, deployment data, Docker
- ✅ Variant interpretation (allele map, benchmark mode) documented
- ✅ RAG transparency (UI/API context) and multi-chromosome profiles
- ✅ Safety disclaimers and research-prototype wording
- ✅ Conceptual guides and paper review

**Future Additions**:
- 🔄 API reference (auto-generated)
- 🔄 HLA-B*57:01 (abacavir) when HLA typing is added
- 🔄 Contributing guide

---

## 📊 System Overview

**SynthaTrial** is an In Silico Pharmacogenomics Platform (Version 0.2 Beta) that:

- **Simulates** drug–gene interactions using Agentic AI (research prototype; not for clinical use)
- **Processes VCFs** for multiple chromosomes (chr2, 10, 12, 22) with auto-discovery
- **Calls alleles** (*1, *2, *4…) and maps to function via PharmVar/CPIC-style table (`variant_db.ALLELE_FUNCTION_MAP`)
- **Profiles** CYP2D6, CYP2C19, CYP2C9, UGT1A1, SLCO1B1; planned: HLA-B*57:01
- **RAG**: Retrieves similar drugs (ChEMBL/Pinecone or mock), then LLM prediction; **UI and API expose** similar drugs used, genetics summary, and sources
- **Evaluation**: `--benchmark cpic_examples.json` for predicted vs expected phenotype and match %

**Target Users**: Researchers, drug developers, bioinformatics professionals, educators

**Status**: Research prototype — simulation and explanation only; **not for clinical decision-making**. See [Setup](setup.md), [Usage](usage.md), [Deployment data](DEPLOYMENT_DATA.md) for current workflows.

---

*For the most up-to-date information, see the individual documentation files.*
