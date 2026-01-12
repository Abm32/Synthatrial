# SynthaTrial - In Silico Pharmacogenomics Platform

**Version: 0.2 (Beta)**

An MVP platform that simulates drug effects on synthetic patient cohorts using Agentic AI. The system accepts chemical inputs (SMILES), converts them to molecular fingerprints, searches for similar drugs, and uses LLMs to predict physiological outcomes.

## Objective

Build a functional MVP of the "In Silico Pharmacogenomics" platform for Technical Founders/Developers.

---

## Phase 1: Environment & Tooling Setup

Before downloading terabytes of data, we need a robust environment. We use Conda because RDKit (the chemistry library) handles complex binary dependencies that standard pip sometimes struggles with.

### 1.1 Install Miniconda

**Download**: [Miniconda for your OS](https://docs.conda.io/en/latest/miniconda.html)

**Action**: Install it and open your terminal.

### 1.2 Create the Virtual Environment

Run these commands to create an isolated workspace for SynthaTrial:

```bash
# Create environment named 'synthatrial' with Python 3.10
conda create -n synthatrial python=3.10

# Activate the environment
conda activate synthatrial

# Install Core Libraries
# RDKit (Chemistry), Pandas (Data), Scikit-Learn (ML), PyTorch (AI)
conda install -c conda-forge rdkit pandas scipy scikit-learn
pip install langchain langchain-openai pinecone-client psycopg2-binary python-dotenv
```

---

## Phase 2: Data Acquisition (The "Raw Ingredients")

We need to download data from three specific global repositories. **Warning**: These datasets are massive. For the MVP, we will download "subsets" or query APIs where possible.

### 2.1 Genomic Data (The 1000 Genomes Project)

Instead of downloading the full 200TB, we will access the VCF (Variant Call Format) files for specific chromosomes. We use the UCSC mirror because it supports HTTPS, which is more reliable than the EBI FTP.

**Source**: [International Genome Sample Resource (IGSR)](https://www.internationalgenome.org/)

**MVP Action**: Download the "Phase 3 Integrated Variant Set" (smaller, easier to parse).

**Command (Terminal)**:

```bash
# Create data directory
mkdir -p data/genomes

# Download a sample chromosome (Chromosome 22 is the smallest autosome, good for testing)
# Option 1: Using wget (Linux/Mac)
wget https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  -P data/genomes/

# Option 2: Using curl (Windows/Universal - Use this if wget fails)
curl -L https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz \
  -o data/genomes/chr22.vcf.gz
```

### 2.2 Chemical Data (ChEMBL)

We need the database of drugs and their targets.

**Source**: [ChEMBL Database (EBI)](https://www.ebi.ac.uk/chembl/)

**MVP Action**: Download the SQLite version (single file, no server needed).

**Command**:

```bash
mkdir -p data/chembl
# Note: Check the latest version number (currently v33 or v34)
curl -L https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_34/chembl_34_sqlite.tar.gz \
  -o data/chembl/chembl_34_sqlite.tar.gz

# Extract it
tar -xvzf data/chembl/chembl_34_sqlite.tar.gz -C data/chembl/
```

### 2.3 Medical Literature (PubMed)

We cannot download all of PubMed easily (it's XML XML XML). For the MVP, we will use the BioPython library to query it live, or download the "Open Access Subset".

**Source**: [PubMed Open Access FTP](https://ftp.ncbi.nlm.nih.gov/pub/pmc/)

**MVP Action**: Use Bio.Entrez (Python wrapper) to fetch data on demand to save disk space.

---

## Phase 3: The "Glue" Code (Implementation)

Now we write the Python code to connect these datasets.

### 3.1 The Directory Structure

Organize your project folder like this:

```
/synthatrial
  /data
    /chembl
    /genomes
  /src
    __init__.py
    input_processor.py    # Handles SMILES strings
    vector_search.py      # Handles Pinecone/Similarity
    agent_engine.py       # Handles the LLM simulation
  main.py                 # The entry point
  requirements.txt        # Dependencies
  README.md              # This file
```

### 3.2 Step 1: Input Processor (`input_processor.py`)

This script takes the drug text (SMILES) and turns it into math.

**Key Function**: `get_drug_fingerprint(smiles)`
- Validates SMILES string using RDKit
- Generates Morgan Fingerprint (Radius 2, 2048 bits)
- Converts to Python list of integers (0s and 1s)

### 3.3 Step 2: Vector Search (`vector_search.py`)

This script finds similar drugs in your database. **Note**: You need a free API key from [Pinecone.io](https://www.pinecone.io/).

**Key Function**: `find_similar_drugs(vector)`
- Queries Pinecone index "drug-index" (create this on Pinecone dashboard with 2048 dimensions)
- Returns top 3 matches with metadata (Name, Side Effects)
- **CRITICAL**: Includes "Mock Mode" - if API key is missing, returns hardcoded dummy results

**Setup**:
1. Create a free account at Pinecone.io
2. Create an index named "drug-index" with 2048 dimensions
3. Set environment variable: `export PINECONE_API_KEY="your_key"`

### 3.4 Step 3: The Agentic Core (`agent_engine.py`)

This is the "Brain" that simulates the patient.

**Key Function**: `run_simulation(drug_name, similar_drugs, patient_profile)`
- Initializes ChatOpenAI (gpt-4o)
- Creates a PromptTemplate with Pharmacogenomics Expert persona
- Compares new drug to known similar drugs
- Analyzes patient's genetic markers (e.g., CYP2D6 status)
- Returns formatted prediction with Risk Level, Predicted Reaction, and Biological Mechanism

**Setup**:
- Set environment variable: `export OPENAI_API_KEY="your_key"`

### 3.5 Step 4: Tying it together (`main.py`)

The CLI entry point that orchestrates the entire workflow:

1. Defines a dummy synthetic patient string (ID, Age, Genetics, Conditions)
2. Defines a test drug (Paracetamol SMILES: `CC(=O)Nc1ccc(O)cc1`)
3. Calls `get_drug_fingerprint`
4. Calls `find_similar_drugs`
5. Calls `run_simulation`
6. Prints the final AI prediction clearly

---

## Usage

### Quick Start

1. **Set up environment variables** (create `.env` file or export):
   ```bash
   export GOOGLE_API_KEY="your_gemini_api_key"       # Required for LLM simulation
   export GEMINI_MODEL="gemini-1.5-flash"            # Optional override
export PINECONE_API_KEY="your_pinecone_api_key"   # Optional; mock mode if missing
   ```

2. **Run the simulation**:

   **Option A: Streamlit Web UI (Recommended)**
   ```bash
   streamlit run app.py
   ```
   Then open your browser to `http://localhost:8501`

   **Option B: Command Line Interface**
   ```bash
   python main.py
   ```

### Expected Output

```
--- Starting Simulation for Synthetic-Para-101 ---
-> Drug digitized.
-> Found 3 similar biological anchors.

--- SIMULATION RESULT ---
RISK LEVEL: Medium
PREDICTED REACTION: [AI-generated analysis]
BIOLOGICAL MECHANISM: [Explanation]
```

---

## Phase 4: Next Steps (Post-MVP)

### Ingestion Script
Write a script to read the ChEMBL SQLite file and push vectors to Pinecone (so `find_similar_drugs` actually works with real data).

### UI
Build a simple Streamlit frontend (`pip install streamlit`) so you can type in SMILES and see the result in a web browser.

### Deploy
Push this code to GitHub as proof of your "Technical Approach".

---

## Project Structure

```
SynthaTrial/
├── data/                  # Data storage directory
│   ├── chembl/           # ChEMBL database files
│   └── genomes/          # 1000 Genomes VCF files
├── src/
│   ├── __init__.py
│   ├── input_processor.py    # SMILES → Fingerprint conversion
│   ├── vector_search.py      # Pinecone similarity search
│   └── agent_engine.py       # LangChain LLM logic
├── app.py                    # Streamlit web UI (recommended)
├── main.py                   # CLI entry point
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Modules

### `input_processor.py`
- `get_drug_fingerprint(smiles)`: Converts SMILES to 2048-bit Morgan Fingerprint

### `vector_search.py`
- `find_similar_drugs(vector, top_k=3)`: Searches for similar drugs
- Includes mock mode for testing without Pinecone credentials

### `agent_engine.py`
- `run_simulation(drug_name, similar_drugs, patient_profile)`: Generates AI predictions

## Example Patient Profile

The default patient profile includes:
- **ID**: SP-01
- **Age**: 45
- **Genetics**: CYP2D6 Poor Metabolizer (Allele *4/*4)
- **Conditions**: Chronic Liver Disease (Mild)
- **Lifestyle**: Alcohol consumer (Moderate)

## Required API Keys

- **GOOGLE_API_KEY**: Required for LLM simulations (Gemini)
- **PINECONE_API_KEY**: Optional - system will use mock mode if not provided

## Notes

- The system gracefully handles missing Pinecone credentials by using mock data
- All modules include comprehensive error handling
- The LLM prompt is designed to provide clinical-grade pharmacogenomics analysis
- For MVP, mock mode allows testing without external API dependencies

## License

This is an MVP prototype for research and development purposes.
