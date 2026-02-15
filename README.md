# SynthaTrial — In Silico Pharmacogenomics Platform

**Version 0.3 (Beta)**

Simulates drug–gene interactions using Agentic AI: VCF-based allele calling, **deterministic CPIC/PharmVar-aligned CYP2C19** (curated tables in `data/pgx/`), RAG with similar drugs, and LLM-generated risk and mechanism. Benchmark-validated; PGx data is versioned in repo (no live API at runtime).

> **⚠️ Not for clinical use**
> SynthaTrial is a **research prototype**. Outputs are synthetic and must **not** be used for clinical decision-making, diagnosis, or treatment. Not medical advice.
>
> **Limitations:** Incomplete allele coverage; no copy-number/structural variants (CNVs) for CYP2D6 yet; current allele calling supports single-variant defining alleles (e.g. CYP2C19*2)—multi-variant haplotypes and CNVs are future work; phenotype and drug guidance are guideline-derived (CPIC/PharmVar) where data files exist but are not a substitute for clinical testing.

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

**Chromosomes used for profile generation** (genes in `src/vcf_processor.py`):

| Chromosome | Genes | Size | Required? |
|------------|-------|------|-----------|
| **chr22** | CYP2D6 | ~200 MB | Yes for VCF profiles |
| **chr10** | CYP2C19, CYP2C9 | ~700 MB | Recommended (Big 3) |
| **chr2** | UGT1A1 | ~1.2 GB | Optional |
| **chr12** | SLCO1B1 | ~700 MB | Optional |
| **chr6, chr11, chr19** | Not yet implemented (reserved for future PGx genes) | ~915 MB, ~700 MB, ~330 MB | Downloadable; not used for profiles |
| **ChEMBL** | Drug similarity (Pinecone) | ~1–2 GB | Optional (mock if missing) |

If you have chr6, chr11, or chr19 in `data/genomes/`, they are discovered but **not used**—no genes are mapped to them. Only chr2, chr10, chr12, chr22 drive the patient genetics pipeline.

**EBI 1000 Genomes (v5b):**
Base: `https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/`

- chr2: `ALL.chr2.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz`
- chr6: `ALL.chr6.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz`
- chr10: `ALL.chr10.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz`
- chr11: `ALL.chr11.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz`
- chr12: `ALL.chr12.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz`
- chr19: `ALL.chr19.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz`
- chr22: `ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz`

**One-time setup (local):**
```bash
mkdir -p data/genomes data/chembl
python scripts/data_initializer.py --vcf chr22 chr10
# Optional ChEMBL:
# curl -L -o data/chembl/chembl_34_sqlite.tar.gz https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_34/chembl_34_sqlite.tar.gz
# tar -xzf data/chembl/chembl_34_sqlite.tar.gz -C data/chembl
```

Any `.vcf.gz` in `data/genomes/` whose filename contains the chromosome (e.g. `chr22`, `chr10`) is **auto-discovered**. No need to pass `--vcf` if files are there.

**PGx curated data (`data/pgx/`):** Allele definitions (PharmVar-style TSV) and diplotype→phenotype (CPIC JSON) are stored in the repo for reproducibility. There is no single open API for star-allele calling; we use one-time curated tables. See `data/pgx/sources.md` for PharmVar, CPIC, Ensembl, dbSNP and versioning. Validate: `python scripts/update_pgx_data.py --validate`. Optional refresh: `python scripts/update_pgx_data.py --gene cyp2c19` (then update `sources.md` and commit).

---

## Deployment (Docker)

Data is not in the image. Two options:

1. **Volume mount:** Pre-download into `./data/genomes` and `./data/chembl` on the host; production Compose mounts `./data` → `/app/data`.
2. **Download in container:** Start once, then e.g. `docker exec <container> python scripts/data_initializer.py --vcf chr22 chr10`. Use a **named volume** for `/app/data` so data persists.

Without any data, the app runs in manual profile mode with mock drug search. For Render: use `render.yaml` and set env vars (e.g. `GOOGLE_API_KEY`) in the dashboard.

---

## Commands

| Command | Description |
|--------|-------------|
| `streamlit run app.py` | Web UI (default port 8501) |
| `python api.py` | FastAPI backend (port 8000); UI can call `/analyze`. Interactive API docs: http://localhost:8000/docs |
| `python main.py --drug-name <name>` | CLI simulation (auto-discovers VCFs in `data/genomes/`) |
| `python main.py --vcf <path> [--vcf-chr10 <path>] --drug-name Warfarin` | CLI with explicit VCFs |
| `python main.py --benchmark cpic_examples.json` | Evaluation: predicted vs expected phenotype, match %. Supports allele-based (`expected_phenotype`) and CYP2C19 variant-based (`variants` + `expected` display). |
| `python scripts/update_pgx_data.py --validate` | Validate `data/pgx/` TSV and JSON. Use `--gene cyp2c19` for optional refresh. |
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

**Trust boundaries:** Deterministic PGx core (CPIC/PharmVar) + generative interpretation layer (LLM). Allele calling and phenotype translation use versioned tables only; the LLM adds free-text interpretation and is audited via RAG context.

**Genes:** CYP2D6 (chr22), CYP2C19/CYP2C9 (chr10), UGT1A1 (chr2), SLCO1B1 (chr12). For **CYP2C19**, when curated data exists (`data/pgx/pharmvar/cyp2c19_alleles.tsv`, `data/pgx/cpic/cyp2c19_phenotypes.json`), allele calling and phenotype are **deterministic** and CPIC/PharmVar-aligned via `src/allele_caller.py` (`interpret_cyp2c19(patient_variants)` for simple rsid→alt; VCF pipeline uses same data). Otherwise fallback to `src/variant_db.py`. Profiles show e.g. `CYP2C19 *1/*2 → Intermediate Metabolizer (CPIC)`. PGx data is versioned in repo; see `data/pgx/sources.md`.

**RAG transparency:** API response and UI show `similar_drugs_used`, `genetics_summary`, `context_sources` so predictions are auditable. For a step-by-step pipeline and how results are verified, see [How it works](#how-it-works-pipeline-and-verification) below.

---

## How it works (pipeline and verification)

### End-to-end flow

1. **Input** — You provide a **drug** (name or SMILES) and a **patient**: either manual genetics (e.g. pick CYP2D6/CYP2C19 status in the UI) or a **VCF file + sample ID** so the pipeline derives genetics from the genome.
2. **Drug fingerprint** — SMILES is converted to a 2048-bit Morgan fingerprint (RDKit). That vector is used to find **similar drugs** in ChEMBL (Pinecone) or a mock list.
3. **Patient genetics** — Two paths:
   - **Manual:** The profile is whatever you set in the UI or CLI (e.g. “CYP2C19 Intermediate Metabolizer”).
   - **VCF:** For each gene (CYP2D6, CYP2C19, CYP2C9, UGT1A1, SLCO1B1), the pipeline loads the right chromosome VCF (chr22, chr10, chr2, chr12), extracts variants in the gene region, and **calls star alleles** from those variants.
4. **Allele calling (CYP2C19 example)** — If `data/pgx/` exists for a gene (e.g. CYP2C19):
   - **PharmVar table** (`cyp2c19_alleles.tsv`): rsID + alt allele → star allele (*2, *3, *17, etc.).
   - **CPIC table** (`cyp2c19_phenotypes.json`): diplotype (e.g. *1/*2) → phenotype label (e.g. “Intermediate Metabolizer”).
   - From the VCF we get **rsid → (ref, alt, genotype)** per sample. The caller counts how many copies of each defining alt the sample has, builds a diplotype (e.g. *1/*2), and looks up the phenotype in the CPIC table. This is **deterministic** and **sourced** (no LLM). *Current implementation supports single-variant defining alleles (e.g. CYP2C19*2). Multi-variant haplotypes and CNVs are future work.*
   - If `data/pgx/` is missing for that gene, the pipeline falls back to `variant_db.py` (activity scores and internal mapping).
5. **Profile string** — The pipeline builds a single text profile (e.g. “CYP2C19 *1/*2 → Intermediate Metabolizer (CPIC), CYP2D6 Extensive Metabolizer, …”) and passes it to the **agent**.
6. **Agent (LLM)** — The model receives: drug name/SMILES, **similar drugs** from the vector search, and the **patient genetics** summary. It returns a risk level and free-text interpretation. The UI/API also return **RAG context** (similar drugs used, genetics summary, sources) so the result is auditable.
7. **Output** — Risk level, clinical interpretation, and (in UI/API) the three pipeline tabs: Patient Genetics, Similar Drugs Retrieved, Predicted Response + Risk.

### How verification works

- **Benchmark (`cpic_examples.json`)** — Each row has a gene, either **alleles** (e.g. *1/*2) or **variants** (e.g. rs4244285 → A), and an **expected** phenotype. The runner:
  - For **CYP2C19 + simple variants + “expected” (display):** calls `interpret_cyp2c19(variants)` and compares the returned phenotype string to `expected`.
  - For **allele-based or VCF-style variants:** uses `get_phenotype_prediction(gene, alleles)` or `call_gene_from_variants()` and compares **normalized** phenotype to `expected_phenotype`.
  - Reports **match %** (e.g. 11/11). This proves that allele calling and phenotype translation match the intended CPIC/PharmVar logic.
- **PGx data checks** — `python scripts/update_pgx_data.py --validate` checks that every TSV in `data/pgx/pharmvar/` has the required columns (allele, rsid, alt, function) and every JSON in `data/pgx/cpic/` is a valid diplotype→phenotype map. No runtime API is used for calling; all logic uses these versioned tables so runs are **reproducible**.

### Summary

| Stage            | What happens | Verified by |
|------------------|--------------|------------|
| Drug → fingerprint | RDKit Morgan | — |
| Similar drugs    | Vector search (ChEMBL or mock) | Shown in RAG context |
| VCF → variants   | Parse by gene region (chr2/10/12/22) | — |
| Variants → alleles | PharmVar TSV (or variant_db fallback) | Benchmark (expected vs predicted phenotype) |
| Alleles → phenotype | CPIC JSON (or activity-score logic) | Same benchmark |
| Phenotype + drugs → risk | LLM with RAG | RAG fields in output |

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
│   ├── allele_caller.py     # Deterministic CPIC/PharmVar calling (CYP2C19 first)
│   ├── vcf_processor.py     # VCF parsing, allele call, profile
│   ├── variant_db.py        # Allele map, phenotype prediction
│   └── chembl_processor.py # ChEMBL integration
├── scripts/
│   ├── data_initializer.py  # Download VCF/ChEMBL
│   ├── update_pgx_data.py   # Validate or refresh data/pgx (PharmVar/CPIC)
│   ├── download_vcf_files.py
│   ├── setup_pinecone_index.py
│   └── ingest_chembl_to_pinecone.py
├── tests/
│   ├── validation_tests.py
│   └── quick_test.py
└── data/
    ├── pgx/       # Curated PharmVar (TSV) + CPIC (JSON); used when present
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
- **PGx data:** Curated tables in `data/pgx/` (see `data/pgx/sources.md`). Validate: `python scripts/update_pgx_data.py --validate`.

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
- PharmVar: https://www.pharmvar.org/ (curated allele definition downloads)
- CPIC: https://cpicpgx.org/ (guidelines + phenotype translation tables)
- PharmGKB: https://www.pharmgkb.org/ (drug–gene annotations)
- Ensembl REST: https://rest.ensembl.org/ (variant metadata, rsID lookup)
- dbSNP: https://www.ncbi.nlm.nih.gov/snp/
- RDKit: https://www.rdkit.org/

---

*Research prototype. Not for clinical use.*
