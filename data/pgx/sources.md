# PGx data sources and versioning

SynthaTrial uses **one-time curated tables** (versioned in the repo), not live APIs, for star-allele calling. This keeps results reproducible and avoids dependency on external services at runtime.

## Why no single “PGx API”?

Pharmacogenomics data is openly available but **fragmented**:

| Source        | What it provides              | API?                    | How we use it                          |
|---------------|-------------------------------|-------------------------|----------------------------------------|
| **PharmVar**  | Star-allele definitions       | Download / API docs      | Curated TSV in `pharmvar/`             |
| **CPIC**      | Diplotype → phenotype, guidelines | REST API + file server | Curated JSON in `cpic/`                |
| **PharmGKB**  | Drug–gene annotations         | API (may need registration) | Reference only                        |
| **Ensembl**   | rsID → position, consequences | Open REST API           | Optional variant metadata              |
| **dbSNP**     | Variant definitions           | NCBI API                | Optional verification                  |

**Best practice:** Download or export curated tables once, document version and date, and ship them in `data/pgx/`. Do not call external APIs during allele calling.

---

## PharmVar (allele definitions)

- **Site:** https://www.pharmvar.org/
- **Downloads:** https://www.pharmvar.org/download — TSV, VCF, FASTA per gene.
- **API:** Programmatic access documented at https://www.pharmvar.org/documentation (for building/updating tables, not at runtime).

Our format: `pharmvar/<gene>_alleles.tsv` with columns `allele`, `rsid`, `alt`, `function`. *1 is default (no row). Source and version should be recorded below when you refresh.

---

## CPIC (phenotype translation)

- **Guidelines:** https://cpicpgx.org/guidelines/
- **Files:** https://files.cpicpgx.org/data/report/current/ (e.g. allele summary, gene-specific tables).
- **API:** https://api.cpicpgx.org — REST API for alleles, genes, guidelines (for building/updating tables).

Our format: `cpic/<gene>_phenotypes.json` — diplotype string → phenotype label (e.g. `"*1/*2"` → `"Intermediate Metabolizer"`). Document CPIC guideline version and date when you refresh.

---

## Ensembl (variant metadata)

- **REST API:** https://rest.ensembl.org/
- Example: `GET https://rest.ensembl.org/variation/human/rs4244285?content-type=application/json` for chromosome, position, alleles. Useful for validating rsIDs or building region-based pipelines; not required for the curated TSV/JSON in this repo.

---

## NCBI dbSNP

- **API:** https://api.ncbi.nlm.nih.gov/variation/v0/beta/refsnp/<id> (e.g. 4244285 for rs4244285). Useful for verifying alleles; not required for curated tables.

---

## Versioning (this repo)

When you update `pharmvar/` or `cpic/` files, record here:

| Data set      | Source / version | Date updated |
|---------------|------------------|--------------|
| cyp2c19_alleles.tsv | PharmVar minimal set (*2, *3, *17) | (initial) |
| cyp2c19_phenotypes.json | CPIC genotype–phenotype mapping | (initial) |

Run `python scripts/update_pgx_data.py --validate` to check existing files. Use `scripts/update_pgx_data.py` (and its `--help`) to refresh from upstream when needed; then update this table and commit.
