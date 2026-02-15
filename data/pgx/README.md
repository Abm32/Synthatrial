# PGx curated data (PharmVar / CPIC)

Research-grade allele definitions and phenotype translations. Not for clinical use.

- **pharmvar/** — Allele definitions (allele, rsid, alt, function). Source: PharmVar.
- **cpic/** — Diplotype → phenotype (CPIC guideline labels).

When these files exist, SynthaTrial uses them for deterministic allele calling and phenotype lookup instead of hardcoded maps. Coverage is incomplete (e.g. no CNVs for CYP2D6); see root README disclaimers.
