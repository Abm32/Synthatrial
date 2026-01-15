# SynthaTrial - In Silico Pharmacogenomics Platform

**Version: 0.2 (Beta)**

An MVP platform that simulates drug effects on synthetic patient cohorts using Agentic AI. The system processes VCF files to extract genetic variants, uses ChEMBL database for drug information, and employs RAG (Retrieval-Augmented Generation) with LLMs to predict drug response based on patient genetics.

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
curl -L https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  -o data/genomes/chr22.vcf.gz
```

**ChEMBL Database (Optional):**
```bash
mkdir -p data/chembl
curl -L https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_34/chembl_34_sqlite.tar.gz \
  -o data/chembl/chembl_34_sqlite.tar.gz
tar -xvzf data/chembl/chembl_34_sqlite.tar.gz -C data/chembl/
```

**Pinecone Index:**
```bash
python setup_pinecone_index.py
python ingest_chembl_to_pinecone.py  # Optional: populate with ChEMBL data
```

### 4. Run the Application

**Streamlit UI (Recommended):**
```bash
streamlit run app.py
```

**Command Line:**
```bash
# With VCF file
python main.py --vcf data/genomes/chr22.vcf.gz --sample-id HG00096

# With manual profile
python main.py --cyp2d6-status poor_metabolizer
```

---

## 📚 Documentation

**Comprehensive documentation is available in the `docs/` directory:**

- **[Documentation Index](docs/README.md)** - Overview of all documentation
- **[Setup Guides](docs/setup/)** - Detailed setup instructions
- **[Implementation Details](docs/implementation/)** - How things work
- **[Troubleshooting](docs/troubleshooting/)** - Errors and solutions
- **[Concepts](docs/concepts/)** - Pharmacogenomics, RAG, vector databases explained

**Quick Links:**
- [VCF & ChEMBL Setup](docs/setup/vcf_chembl_setup.md)
- [Pinecone Setup](docs/setup/pinecone_setup.md)
- [Errors & Solutions](docs/troubleshooting/errors_and_solutions.md)
- [Implementation Summary](docs/implementation/implementation_summary.md)

---

## 🏗️ Architecture

```
User Input (Drug SMILES + Patient Profile)
    ↓
[Input Processor] → Molecular Fingerprint (2048-bit vector)
    ↓
[Vector Search] → Similar Drugs (from ChEMBL/Pinecone)
    ↓
[VCF Processor] → Genetic Variants (CYP2D6, CYP2C19, CYP3A4)
    ↓
[Agent Engine] → LLM Prediction (RAG with retrieved context)
    ↓
Output (Risk Level + Predicted Reaction + Mechanism)
```

---

## 📁 Project Structure

```
SynthaTrial/
├── docs/                      # Comprehensive documentation
│   ├── setup/                 # Setup guides
│   ├── implementation/        # Implementation details
│   ├── troubleshooting/      # Errors and solutions
│   ├── concepts/              # Conceptual explanations
│   └── paper/                 # Paper review
├── src/
│   ├── input_processor.py     # SMILES → Fingerprint
│   ├── vector_search.py       # Pinecone similarity search
│   ├── agent_engine.py        # LLM-based simulation
│   ├── vcf_processor.py      # VCF file processing
│   └── chembl_processor.py    # ChEMBL database integration
├── tests/
│   ├── validation_tests.py   # Comprehensive test suite
│   └── quick_test.py          # Quick integration test
├── data/
│   ├── chembl/               # ChEMBL database files
│   └── genomes/              # VCF files
├── app.py                     # Streamlit web UI
├── main.py                    # CLI entry point
├── ingest_chembl_to_pinecone.py  # ChEMBL ingestion script
├── setup_pinecone_index.py    # Pinecone index setup
└── requirements.txt           # Python dependencies
```

---

## ✨ Features

- ✅ **VCF File Processing** - Extract genetic variants from 1000 Genomes Project VCF files
- ✅ **ChEMBL Integration** - Extract drug information from ChEMBL database
- ✅ **Vector Similarity Search** - Find similar drugs using molecular fingerprints
- ✅ **RAG-Enhanced LLM** - Retrieval-Augmented Generation for accurate predictions
- ✅ **Patient Profile Generation** - Create profiles from VCF data or manual input
- ✅ **Streamlit UI** - User-friendly web interface
- ✅ **Comprehensive Testing** - Validation test suite

---

## 🔧 Key Components

### Input Processor
Converts SMILES strings to 2048-bit Morgan fingerprints using RDKit.

### Vector Search
Searches Pinecone vector database for similar drugs based on molecular structure.

### VCF Processor
Extracts CYP gene variants (CYP2D6, CYP2C19, CYP3A4) from VCF files and infers metabolizer status.

### ChEMBL Processor
Extracts approved drugs, targets, and side effects from ChEMBL SQLite database.

### Agent Engine
Uses Gemini LLM with RAG to predict drug response based on patient genetics and similar drugs.

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
- **VCF Integration:** [docs/implementation/vcf_integration.md](docs/implementation/vcf_integration.md)
- **ChEMBL Integration:** [docs/implementation/chembl_integration.md](docs/implementation/chembl_integration.md)

---

## 🐛 Troubleshooting

**Common issues and solutions are documented in:**
- [Errors and Solutions](docs/troubleshooting/errors_and_solutions.md)

**Quick fixes:**
- **RDKit not found:** Use `conda install -c conda-forge rdkit`
- **Pinecone index not found:** Run `python setup_pinecone_index.py`
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
