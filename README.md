# SynthaTrial - In Silico Pharmacogenomics Platform

**Version: 0.2 (Beta)**

An MVP platform that simulates drug effects on synthetic patient cohorts using Agentic AI. The system processes VCF files to extract genetic variants, uses ChEMBL database for drug information, and employs RAG (Retrieval-Augmented Generation) with LLMs to predict drug response based on patient genetics.

> **⚠️ Safety disclaimer — not for clinical use**  
> **SynthaTrial is a research prototype.** It is a simulation and explanation engine, not a true pharmacogenomics predictor. All outputs are synthetic predictions and **must not be used for clinical decision-making**, diagnosis, or treatment. This software is not medical advice and must not be used as such.

---

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Create conda environment
conda create -n synthatrial python=3.10
conda activate synthatrial

# Install dependencies
conda install -c conda-forge rdkit pandas scipy scikit-learn
pip install langchain langchain-google-genai pinecone-client python-dotenv streamlit
```

### 2. Configure API Keys

Create a `.env` file:
```bash
GOOGLE_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key  # Optional (mock mode if missing)
PINECONE_INDEX=drug-index
```

### 3. Set Up Data

**VCF File (Optional):**
```bash
mkdir -p data/genomes
# Use v5b (v5a returns 404). See docs/VCF_CHROMOSOME_SET.md for chr10 and representative set.
curl -L https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz \
  -o data/genomes/chr22.vcf.gz
```
Any `.vcf.gz` in `data/genomes` whose filename contains the chromosome (e.g. `chr22`, `chr10`) is **auto-discovered**—you can use short names like `chr22.vcf.gz` or long names like `ALL.chr22.phase3_shapeit2_...vcf.gz`. Run `python main.py --sample-id HG00096` and the app will use discovered VCFs if you don’t pass `--vcf`.

**ChEMBL Database (Optional):**
```bash
mkdir -p data/chembl
curl -L https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_34/chembl_34_sqlite.tar.gz \
  -o data/chembl/chembl_34_sqlite.tar.gz
tar -xvzf data/chembl/chembl_34_sqlite.tar.gz -C data/chembl/
```

**Pinecone Index:**
```bash
python scripts/setup_pinecone_index.py
python scripts/ingest_chembl_to_pinecone.py  # Optional: populate with ChEMBL data
```

### 4. Run the Application

**Streamlit UI (Recommended):**
```bash
streamlit run app.py
```

**Command Line:**
```bash
# With VCF file (app auto-discovers data/genomes/ if --vcf omitted)
python main.py --vcf data/genomes/chr22.vcf.gz --sample-id HG00096

# Multi-chromosome (Big 3 + UGT1A1/SLCO1B1 when chr2/chr12 present)
python main.py --vcf data/genomes/chr22.vcf.gz --vcf-chr10 data/genomes/chr10.vcf.gz --drug-name Warfarin

# Manual profile
python main.py --cyp2d6-status poor_metabolizer

# Evaluation mode (CPIC-style benchmark)
python main.py --benchmark cpic_examples.json
```

---

## 📚 Documentation

**Comprehensive documentation is available in the `docs/` directory:**

- **[Documentation Index](docs/README.md)** - Overview of all documentation
- **[VCF chromosome set](docs/VCF_CHROMOSOME_SET.md)** - Recommended chromosomes (gold standard subset, v5b URLs)
- **[Deployment: Chromosome & ChEMBL data](docs/DEPLOYMENT_DATA.md)** - What to do with VCFs and ChEMBL when deploying (Docker, volumes, one-time download)
- **[Setup Guide](docs/setup.md)** - Complete installation and configuration
- **[Usage Guide](docs/usage.md)** - How to run simulations and interpret results
- **[Implementation Details](docs/implementation.md)** - Technical architecture and code
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[Paper Review](docs/paper-review.md)** - Research validation and results
- **[Concepts](docs/concepts/)** - Pharmacogenomics, RAG, and vector databases explained

**Quick Links:**
- [Complete Setup Guide](docs/setup.md) - Everything you need to get started
- [Usage Examples](docs/usage.md) - Command-line and web interface examples
- [Troubleshooting](docs/troubleshooting.md) - Fix common issues
- [Technical Details](docs/implementation.md) - How the system works

---

## 🏗️ Architecture

```
User Input (Drug SMILES + Patient Profile)
    ↓
[Input Processor] → Molecular Fingerprint (2048-bit vector)
    ↓
[Vector Search] → Similar Drugs (from ChEMBL/Pinecone or mock)
    ↓
[VCF Processor] → Genetic Variants + Allele Calling (CYP2D6, CYP2C19, CYP2C9, UGT1A1, SLCO1B1)
    ↓
[Variant DB] → PharmVar/CPIC allele→function mapping → Metabolizer status
    ↓
[Agent Engine] → LLM Prediction (RAG with retrieved context)
    ↓
Output (Risk Level + Interpretation + RAG context: similar drugs, genetics, sources)
```

---

## 📁 Project Structure

```
SynthaTrial/
├── docs/                      # Documentation (setup, usage, implementation, deployment, concepts)
├── src/
│   ├── input_processor.py     # SMILES → Morgan fingerprint
│   ├── vector_search.py      # Pinecone similarity search (ChEMBL/mock)
│   ├── agent_engine.py        # LLM simulation (RAG)
│   ├── vcf_processor.py       # VCF parsing, allele calling, profile generation
│   ├── variant_db.py         # PharmVar/CPIC allele→function map, phenotype prediction
│   └── chembl_processor.py   # ChEMBL database integration
├── tests/
│   ├── validation_tests.py   # Full test suite
│   └── quick_test.py         # Quick integration test
├── data/
│   ├── chembl/               # ChEMBL SQLite (optional)
│   └── genomes/              # VCF files (chr2, 10, 12, 22, etc.; optional)
├── app.py                     # Streamlit UI (with prediction-context panel)
├── main.py                    # CLI + --benchmark evaluation mode
├── api.py                     # FastAPI /analyze (returns RAG context)
├── cpic_examples.json         # CPIC-style benchmark examples
├── scripts/
│   ├── data_initializer.py   # Download VCF/ChEMBL
│   ├── download_vcf_files.py # Chromosome VCF downloads
│   ├── setup_pinecone_index.py
│   └── ingest_chembl_to_pinecone.py
└── requirements.txt
```

---

## ✨ Features

- ✅ **VCF File Processing** - Multi-chromosome (chr2, 10, 12, 22) with auto-discovery in `data/genomes/`
- ✅ **Allele Calling & Interpretation** - PharmVar/CPIC-style mapping (*1, *2, *4… → function); profiles show allele call when available
- ✅ **Pharmacogenomics Genes** - CYP2D6, CYP2C19, CYP2C9 (Big 3) + UGT1A1 (irinotecan), SLCO1B1 (statins)
- ✅ **ChEMBL Integration** - Drug data for Pinecone vector search (mock mode if no key)
- ✅ **RAG-Enhanced LLM** - Simulation and explanation with retrieved similar drugs
- ✅ **Transparent RAG Context** - UI and API show similar drugs used, genetics summary, and data sources
- ✅ **Evaluation Mode** - `python main.py --benchmark cpic_examples.json` for predicted vs expected phenotype and match %
- ✅ **Patient Profile Generation** - From VCF or manual input; optional allele-level detail
- ✅ **Streamlit UI** - Web interface with prediction-context panel
- ✅ **REST API** - FastAPI `/analyze` with optional RAG context in response
- ✅ **Comprehensive Testing** - Validation tests and quick integration test

---

## 🔧 Key Components

### Input Processor
Converts SMILES strings to 2048-bit Morgan fingerprints using RDKit.

### Vector Search
Searches Pinecone vector database for similar drugs based on molecular structure.

### VCF Processor
Extracts gene variants (CYP2D6, CYP2C19, CYP2C9, UGT1A1, SLCO1B1) from multi-chromosome VCFs and infers metabolizer status with **allele calling** (*1, *2, *4…) and PharmVar/CPIC-style interpretation. Auto-discovers VCFs in `data/genomes/`. Evaluation mode: `python main.py --benchmark cpic_examples.json`.

### ChEMBL Processor
Extracts approved drugs, targets, and side effects from ChEMBL SQLite database.

### Agent Engine
Uses Gemini LLM with RAG for simulation and explanation of drug–gene interactions (research prototype; not for clinical use).

---

## 🚢 Deploying

Chromosome VCF files and the ChEMBL database are **not** included in the repo or Docker image (they are large and gitignored). For deployment options (volume mount, one-time download in container, minimal vs full data), see **[Deployment: Chromosome & ChEMBL data](docs/DEPLOYMENT_DATA.md)**.

---

## 🧪 Testing

```bash
# Run validation tests
python tests/validation_tests.py

# Quick integration test
python tests/quick_test.py
```

---

## 📖 Learn More

- **Pharmacogenomics Concepts:** [docs/concepts/pharmacogenomics.md](docs/concepts/pharmacogenomics.md)
- **Vector Databases:** [docs/concepts/vector_databases.md](docs/concepts/vector_databases.md)
- **RAG Explained:** [docs/concepts/rag_explained.md](docs/concepts/rag_explained.md)
- **Implementation (VCF, variant DB, API):** [docs/implementation.md](docs/implementation.md)

---

## 🐛 Troubleshooting

**Common issues and solutions are documented in:**
- [Troubleshooting Guide](docs/troubleshooting.md)

**Quick fixes:**
- **RDKit not found:** Use `conda install -c conda-forge rdkit`
- **Pinecone index not found:** Run `python scripts/setup_pinecone_index.py`
- **ChEMBL database not found:** Extract the tar.gz file (see setup guide)

---

## 📝 Requirements

- Python 3.10+
- Conda (for RDKit installation)
- API Keys:
  - Google API Key (required for Gemini LLM)
  - Pinecone API Key (optional, mock mode if missing)

---

## 🔗 Resources

- **1000 Genomes Project:** https://www.internationalgenome.org/
- **ChEMBL Database:** https://www.ebi.ac.uk/chembl/
- **Pinecone:** https://www.pinecone.io/
- **RDKit:** https://www.rdkit.org/
- **PharmVar:** https://www.pharmvar.org/ (CYP allele definitions)

---

## 📄 License

This is an MVP prototype for research and development purposes.

---

## 🙏 Acknowledgments

- 1000 Genomes Project for genomic data
- ChEMBL team for drug database
- RDKit community for cheminformatics tools
- LangChain for LLM integration framework

---

*For detailed documentation, see [docs/README.md](docs/README.md)*
