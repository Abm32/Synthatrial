# Recommended VCF Chromosome Set (1000 Genomes Phase 3)

This document describes a **scientifically representative** subset of chromosomes for use when disk space or compute is limited. It balances authenticity (diverse biology) with practicality (avoiding the largest chromosomes that can crash pipelines).

> **Note:** SynthaTrial is a research prototype; its outputs must not be used for clinical decision-making.

**Important:** 1000 Genomes EBI release uses **v5b** (not v5a). All URLs below use the correct version.

Base URL: `https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/`

---

## Minimum set (SynthaTrial pharmacogenomics)

For **drug–gene analysis only**, the pipeline needs:

| Priority   | Chromosome | Role in pipeline                    | Est. size |
|------------|------------|-------------------------------------|-----------|
| Required   | **Chr 22** | CYP2D6                              | ~196 MB   |
| Required   | **Chr 10** | CYP2C19, CYP2C9 (Big 3)             | ~707 MB   |
| Optional   | **Chr 2**  | UGT1A1 (e.g. irinotecan)            | ~1.2 GB   |
| Optional   | **Chr 12** | SLCO1B1 (e.g. statins)              | ~677 MB   |

Download:

```bash
mkdir -p data/genomes
cd data/genomes
wget https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz
wget https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz
```

---

## “Gold standard” representative set

For **broader, authentic genome-wide representation** (e.g. method validation, pipeline stress-testing, or publication-ready analyses), use a **diverse** subset rather than only the smallest or only the largest chromosomes.

| Priority   | Chromosome | Why include it | Est. VCF size |
|-----------|------------|----------------|----------------|
| Have/add  | **Chr 2**  | “Giant” chromosome; high variation, stress-tests scaling. | ~1.2 GB |
| **Add**   | **Chr 6**  | **MHC region** – most complex and variable part of the genome; many pipelines show interesting behaviour here. Important for credibility. | ~915 MB |
| **Add**   | **Chr 11**| High gene density; olfactory and hemoglobin clusters; good “real-world” gene-cluster test. | ~701 MB |
| **Add**   | **Chr 19**| **Highest gene density** of any chromosome; tests that the pipeline handles dense, noisy regions. | ~329 MB |
| Have      | **Chr 22**| Small, gene-rich; CYP2D6; manageable size. | ~196 MB |
| Optional  | **Chr X**  | Sex chromosome; for sex-linked traits. Different file version (v1c). Large (~1.8 GB). | ~1.8 GB |

**Why not only chr 1–3?**  
Largest chromosomes (1, 2, 3) can cause memory or runtime issues. Including 2 is useful; adding 1 and 3 often does not add much biological diversity for the cost.

**Why not only chr 21–22?**  
Smallest chromosomes under-represent genome complexity (e.g. no MHC, less gene-density variety).

**Why Chr 6 and Chr 19?**  
- **Chr 6:** MHC (immune); extreme diversity; many pipelines “break” or show interesting results here.  
- **Chr 19:** Highest gene density; ensures the pipeline is not just cruising through low-complexity regions.

---

## Download commands (v5b; EBI)

Replace `CHR` with the chromosome number (e.g. `2`, `6`, `10`, `11`, `19`, `22`). For chr X use the chrX URL below.

```bash
# Chr 2, 6, 10, 11, 19, 22 (v5b)
BASE="https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502"
for CHR in 2 6 10 11 19 22; do
  wget -O "chr${CHR}.vcf.gz" "${BASE}/ALL.chr${CHR}.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz"
done

# Chr X (different version: v1c) – optional, ~1.8 GB
wget -O chrX.vcf.gz "${BASE}/ALL.chrX.phase3_shapeit2_mvncall_integrated_v1c.20130502.genotypes.vcf.gz"
```

Using the project script (after it is updated to v5b and these chromosomes):

```bash
# Minimum for SynthaTrial (chr22, chr10)
python scripts/download_vcf_files.py --chromosomes chr22 chr10

# Representative set (chr2, 6, 10, 11, 19, 22)
python scripts/download_vcf_files.py --chromosomes chr2 chr6 chr10 chr11 chr19 chr22
```

---

## File naming (EBI release 20130502)

- **Autosomes (1–22):**  
  `ALL.chrN.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz`  
  Use **v5b**; v5a URLs are deprecated and return 404.

- **Chr X:**  
  `ALL.chrX.phase3_shapeit2_mvncall_integrated_v1c.20130502.genotypes.vcf.gz`

- **Chr Y / MT:**  
  Different naming; see the [EBI release index](https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/).

---

## Summary

- **Minimum for SynthaTrial:** Chr 22 + Chr 10 (v5b).  
- **Representative “gold standard” subset:** Chr 2, 6, 10, 11, 19, 22 (all v5b). Optionally Chr X (v1c) for sex-linked work.  
- Always use **v5b** (and EBI URLs) for autosomes; v5a is obsolete.
