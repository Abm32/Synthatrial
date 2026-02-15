# SynthaTrial — In Silico Pharmacogenomics Platform

**Version 0.2 (Beta)**

Simulates drug–gene interactions using Agentic AI: VCF-based allele calling, PharmVar/CPIC-style interpretation, RAG with similar drugs, and LLM-generated risk and mechanism.

> **⚠️ Not for clinical use**  
> SynthaTrial is a **research prototype**. Outputs are synthetic and must **not** be used for clinical decision-making, diagnosis, or treatment. Not medical advice.

---

## Quick Start

```bash
conda create -n synthatrial python=3.10 && conda activate synthatrial
conda install -c conda-forge rdkit pandas scipy scikit-learn -y
pip install -r requirements.txt
```

Create `.env`: `GOOGLE_API_KEY=...` (required), `PINECONE_API_KEY=...` (optional, mock if missing), `PINECONE_INDEX=drug-index`.

**Run:** `streamlit run app.py` (UI) or `python main.py --drug-name Warfarin` (CLI). For VCF-based profiles, put `.vcf.gz` files in `data/genomes/` (see [Data](#data-vcf--chembl)) or pass `--vcf` / `--vcf-chr10`.

---

## Data (VCF + ChEMBL)

VCF and ChEMBL are **not** in the repo (gitignored). The app runs without them (manual profile + mock drug search).

| Data | Purpose | Size | Required? |
|------|---------|------|-----------|
| **chr22** | CYP2D6 | ~200 MB | Yes for VCF profiles |
| **chr10** | CYP2C19, CYP2C9 | ~700 MB | Recommended (Big 3) |
| **chr2, chr12** | UGT1A1, SLCO1B1 | ~1.2 GB, ~700 MB | Optional |
| **ChEMBL** | Drug similarity (Pinecone) | ~1–2 GB | Optional (mock if missing) |

**EBI 1000 Genomes (v5b):**  
Base: `https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/`  
- chr22: `ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz`  
- chr10: `ALL.chr10.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz`  
- chr2, chr12: same pattern with `chr2` / `chr12`.

**One-time setup (local):**
```bash
mkdir -p data/genomes data/chembl
python scripts/data_initializer.py --vcf chr22 chr10
# Optional ChEMBL:
# curl -L -o data/chembl/chembl_34_sqlite.tar.gz https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_34/chembl_34_sqlite.tar.gz
# tar -xzf data/chembl/chembl_34_sqlite.tar.gz -C data/chembl
```

Any `.vcf.gz` in `data/genomes/` whose filename contains the chromosome (e.g. `chr22`, `chr10`) is **auto-discovered**. No need to pass `--vcf` if files are there.

---

## Deployment (Docker)

Data is not in the image. Two options:

1. **Volume mount:** Pre-download into `./data/genomes` and `./data/chembl` on the host; production Compose mounts `./data` → `/app/data`.
2. **Download in container:** Start once, then e.g. `docker exec <container> python scripts/data_initializer.py --vcf chr22 chr10`. Use a **named volume** for `/app/data` so data persists.

Without any data, the app runs in manual profile mode with mock drug search.

---

## Commands

| Command | Description |
|--------|-------------|
| `streamlit run app.py` | Web UI (default port 8501) |
| `python api.py` | FastAPI backend (port 8000); UI can call `/analyze` |
| `python main.py --drug-name <name>` | CLI simulation (auto-discovers VCFs in `data/genomes/`) |
| `python main.py --vcf <path> [--vcf-chr10 <path>] --drug-name Warfarin` | CLI with explicit VCFs |
| `python main.py --benchmark cpic_examples.json` | Evaluation: predicted vs expected phenotype, match % |
| `python tests/quick_test.py` | Quick integration test |
| `python tests/validation_tests.py` | Full test suite |

**CLI args:** `--drug-name`, `--drug-smiles`, `--vcf`, `--vcf-chr10`, `--sample-id`, `--cyp2d6-status`, `--benchmark <json>`.

---

## Architecture

```
User Input (Drug SMILES + Patient Profile)
    ↓
[Input Processor] → 2048-bit Morgan fingerprint (RDKit)
    ↓
[Vector Search] → Similar drugs (ChEMBL/Pinecone or mock)
    ↓
[VCF Processor] → Variants + allele calling (chr22, 10, 2, 12)
    ↓
[Variant DB] → PharmVar/CPIC allele→function → metabolizer status
    ↓
[Agent Engine] → LLM prediction (RAG)
    ↓
Output: risk level, interpretation, + RAG context (similar drugs, genetics, sources)
```

**Genes:** CYP2D6 (chr22), CYP2C19/CYP2C9 (chr10), UGT1A1 (chr2), SLCO1B1 (chr12). Allele calling (*1, *2, *4…) and interpretation in `src/variant_db.py` (`ALLELE_FUNCTION_MAP`). Profiles can show e.g. `CYP2D6 *1/*4 (Poor Metabolizer)`.

**RAG transparency:** API response and UI show `similar_drugs_used`, `genetics_summary`, `context_sources` so predictions are auditable.

---

## Project Structure

```
SynthaTrial/
├── README.md           # This file (all important details)
├── app.py              # Streamlit UI
├── main.py             # CLI + --benchmark
├── api.py              # FastAPI /analyze
├── cpic_examples.json  # CPIC-style benchmark examples
├── requirements.txt
├── src/
│   ├── input_processor.py   # SMILES → fingerprint
│   ├── vector_search.py     # Pinecone / mock
│   ├── agent_engine.py      # LLM simulation
│   ├── vcf_processor.py     # VCF parsing, allele call, profile
│   ├── variant_db.py        # Allele map, phenotype prediction
│   └── chembl_processor.py # ChEMBL integration
├── scripts/
│   ├── data_initializer.py  # Download VCF/ChEMBL
│   ├── download_vcf_files.py
│   ├── setup_pinecone_index.py
│   └── ingest_chembl_to_pinecone.py
├── tests/
│   ├── validation_tests.py
│   └── quick_test.py
└── data/
    ├── genomes/   # VCFs (optional)
    └── chembl/    # ChEMBL SQLite (optional)
```

---

## Troubleshooting

- **RDKit not found:** `conda install -c conda-forge rdkit`
- **GOOGLE_API_KEY missing:** Set in `.env` or environment; required for LLM.
- **Pinecone/index:** Optional; app uses mock drugs if not set. To use ChEMBL: `python scripts/setup_pinecone_index.py` then `python scripts/ingest_chembl_to_pinecone.py`
- **VCF not found:** Ensure files are in `data/genomes/` with chromosome in filename (e.g. `chr22`, `chr10`) or pass `--vcf` / `--vcf-chr10`.
- **Benchmark:** `python main.py --benchmark cpic_examples.json` (no VCF needed).

---

## Requirements

- Python 3.10+
- Conda (recommended for RDKit)
- GOOGLE_API_KEY (required for simulation)
- PINECONE_API_KEY (optional)

---

## Resources

- 1000 Genomes: https://www.internationalgenome.org/
- ChEMBL: https://www.ebi.ac.uk/chembl/
- PharmVar: https://www.pharmvar.org/
- RDKit: https://www.rdkit.org/

---

*Research prototype. Not for clinical use.*
