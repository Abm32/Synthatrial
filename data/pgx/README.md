# PGx curated data (PharmVar / CPIC)

Research-grade allele definitions and phenotype translations. Not for clinical use.

- **pharmvar/** — Allele definitions (allele, rsid, alt, function). Source: PharmVar. *1 is the default when no variant is detected (no row required).
- **cpic/** — Diplotype → phenotype (CPIC guideline labels).

When these files exist, SynthaTrial uses them for deterministic allele calling and phenotype lookup. Use `interpret_cyp2c19(patient_variants)` for simple rsid→alt input; VCF pipeline uses the same data. Coverage is incomplete (e.g. no CNVs for CYP2D6); see root README disclaimers.
