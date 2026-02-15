# Documentation

All project documentation lives in the **root [README.md](../README.md)**.

It covers: quick start, data (VCF + ChEMBL, **PGx curated data** in `data/pgx/` with PharmVar/CPIC sources and versioning, including **Warfarin** CYP2C9 + VKORC1 and **SLCO1B1**), **drug-triggered PGx** (`src/pgx_triggers.py`: genetics summary shows only drug-relevant genes—Warfarin → CYP2C9 + VKORC1; Statins → SLCO1B1; Clopidogrel → CYP2C19), deployment, commands (including **benchmark** for CPIC, Warfarin, and SLCO1B1 and **update_pgx_data**), architecture (deterministic CYP2C19, Warfarin, SLCO1B1; `allele_caller`, `warfarin_caller`, `slco1b1_caller`, `pgx_triggers`), project structure, troubleshooting, requirements, and resources (PharmVar, CPIC, PharmGKB, Ensembl).
