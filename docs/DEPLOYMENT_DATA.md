# Deployment: Chromosome VCFs and ChEMBL Data

When deploying SynthaTrial, **chromosome VCF files** and the **ChEMBL database** are **not** included in the Docker image or the repo (they are large and listed in `.gitignore`). You must provide them at deploy time using one of the approaches below.

> **⚠️ Safety disclaimer** — SynthaTrial is a **research prototype**. Outputs are synthetic predictions and must not be used for clinical decision-making.

---

## What you need

| Data | Purpose | Size (approx) | Required? |
|------|---------|----------------|-----------|
| **VCF chr22** | CYP2D6 (pharmacogenomics) | ~200 MB | **Yes** for VCF-based profiles |
| **VCF chr10** | CYP2C19, CYP2C9 (Big 3 enzymes) | ~700 MB | Recommended for full drug–gene analysis |
| **VCF chr2, chr12** | UGT1A1, SLCO1B1 | ~1.2 GB, ~700 MB | Optional; enables full multi-gene profile |
| **ChEMBL SQLite** | Drug similarity search (Pinecone ingestion) | ~1–2 GB | Optional; app uses mock data if missing |

Without any VCFs, the app runs in **manual profile mode** (no VCF-derived genetics). Without ChEMBL, **vector search uses mock data** (limited drug set).

---

## Option 1: Volume mount (recommended for production)

Pre-download data on the **host** (or a build server), then mount it into the container. Production Compose already mounts `./data` → `/app/data`.

### One-time setup on the host

```bash
# Create directories (same structure as repo)
mkdir -p data/genomes data/chembl

# Minimal: CYP2D6 only (~200 MB)
curl -L -o data/genomes/chr22.vcf.gz \
  https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz

# Recommended: Big 3 enzymes (~900 MB extra)
curl -L -o data/genomes/chr10.vcf.gz \
  https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz

# Optional: UGT1A1 + SLCO1B1 (chr2, chr12) – use data_initializer or see docs/VCF_CHROMOSOME_SET.md
python scripts/data_initializer.py --vcf chr22 chr10 chr2 chr12

# Optional: ChEMBL (~1–2 GB)
curl -L -o data/chembl/chembl_34_sqlite.tar.gz \
  https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_34/chembl_34_sqlite.tar.gz
tar -xzf data/chembl/chembl_34_sqlite.tar.gz -C data/chembl/
```

Then start the stack; the container will see `data/genomes/` and `data/chembl/` via the existing `./data:/app/data` volume.

---

## Option 2: Download inside the container (after first start)

If you don’t pre-populate `./data`, start the container once, then run the initializer **inside** the container. Use a **named volume** for `/app/data` so downloads persist across restarts.

### Using a named volume for data

In `docker-compose.prod.yml` you can switch to a named volume for data:

```yaml
volumes:
  - synthatrial-data:/app/data:rw  # persistent data
  - ./logs:/app/logs:rw
  - ./.env:/app/.env:ro
# ...
volumes:
  synthatrial-data:
```

Then after first start:

```bash
# Minimal VCF (chr22 + chr10)
docker exec synthatrial-prod python scripts/data_initializer.py --vcf chr22 chr10

# VCF + ChEMBL (larger, slower)
docker exec synthatrial-prod python scripts/data_initializer.py --all
```

Subsequent restarts will keep using the same volume, so you only download once.

---

## Option 3: Optional download on first start (env-driven)

You can trigger a one-time download when the container starts by setting an env var and handling it in your entrypoint (or a wrapper script). Example idea:

- `SYNTHA_DOWNLOAD_DATA=chr22,chr10` → run `python scripts/data_initializer.py --vcf chr22 chr10` before starting the app.
- Use a **persistent volume** for `/app/data` so the next start doesn’t re-download.

This is not implemented by default because downloads can be slow and may fail in restricted environments; implement only if you want “first-start” automation.

---

## Summary

| Approach | When to use |
|----------|-------------|
| **Volume mount** (Option 1) | Production: you control where and when data is downloaded; image stays small. |
| **Download in container** (Option 2) | Quick deploy: start container, run `data_initializer` once, use named volume for persistence. |
| **No data** | App still runs: manual profile mode, mock drug search; no VCF-based genetics. |

- **Chromosome files**: Any `.vcf.gz` in `data/genomes/` whose filename contains the chromosome (e.g. `chr22`, `chr10`, `chr2`, `chr12`) is auto-discovered. See `docs/VCF_CHROMOSOME_SET.md` for the full recommended set.
- **ChEMBL**: Place the extracted SQLite DB in `data/chembl/` (e.g. `data/chembl/chembl_34_sqlite/chembl_34.db`). If present and `PINECONE_API_KEY` is set, you can run `python scripts/ingest_chembl_to_pinecone.py` to populate the vector index.
