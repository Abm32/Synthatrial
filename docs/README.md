# SynthaTrial Documentation

Welcome to the SynthaTrial documentation. This directory contains comprehensive documentation organized for easy navigation.

## 📚 Documentation Structure

```
docs/
├── README.md              # This file - documentation index
├── setup.md               # Complete setup and installation guide
├── usage.md               # Usage examples and CLI reference
├── implementation.md      # Technical implementation details
├── troubleshooting.md     # Common issues and solutions
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
- **Genetic Profiling**: VCF file processing (1000 Genomes Project)
- **AI Simulation**: LLM-based pharmacogenomics prediction (Google Gemini)

### Big 3 Enzymes Support
- **CYP2D6** (Chromosome 22): ~25% of drugs
- **CYP2C19** (Chromosome 10): Antiplatelet drugs, PPIs
- **CYP2C9** (Chromosome 10): Anticoagulants, NSAIDs
- **Combined Coverage**: ~60-70% of clinically used drugs

### Validation and Testing
- **CPIC Compliance**: Follows clinical guidelines
- **Test Suite**: Comprehensive validation tests
- **Performance Benchmarks**: Timing and accuracy metrics
- **Research Validation**: 100% accuracy on test cases

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

# Run web interface
streamlit run app.py

# Run CLI simulation
python main.py --vcf data/genomes/chr22.vcf.gz --drug-name Codeine

# Test system
python tests/quick_test.py
```

### Key Files

- **Main application**: `app.py` (web), `main.py` (CLI)
- **Core modules**: `src/` directory
- **Test suite**: `tests/validation_tests.py`
- **Setup scripts**: `scripts/setup_pinecone_index.py`

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
- ✅ Complete setup and usage guides
- ✅ Comprehensive troubleshooting
- ✅ Technical implementation details
- ✅ Research validation and review
- ✅ Conceptual explanations

**Future Additions**:
- 🔄 API documentation (auto-generated)
- 🔄 Deployment guide (production setup)
- 🔄 Contributing guide (for developers)
- 🔄 Performance optimization guide

---

## 📊 System Overview

**SynthaTrial** is an In Silico Pharmacogenomics Platform (Version 0.3 Beta) that:

- Simulates drug effects on synthetic patient cohorts using Agentic AI
- Processes VCF files to extract genetic variants (Big 3 enzymes)
- Uses vector similarity search to find related drugs
- Employs LLMs with RAG for pharmacogenomics predictions
- Follows CPIC guidelines for clinical accuracy

**Target Users**: Researchers, drug developers, bioinformatics professionals, educators

**Status**: Research prototype (not for clinical decision-making)

---

*For the most up-to-date information, see the individual documentation files. Last updated: Documentation restructure.*