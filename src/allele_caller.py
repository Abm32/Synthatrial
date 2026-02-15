"""
Deterministic allele caller and CPIC phenotype translation.

Uses curated PharmVar allele definitions (TSV) and CPIC phenotype tables (JSON)
for reproducible, guideline-derived calling. No hardcoded allele logic when
data files are present.

Layer 1: PharmVar allele definitions (rsid + alt → star allele)
Layer 2: CPIC diplotype → phenotype
Layer 3: Drug guidance remains in agent/UI (CPIC/PharmGKB-derived, labeled as such)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Default base for PGx data (repo-relative)
DEFAULT_PGX_DIR = Path(__file__).resolve().parent.parent / "data" / "pgx"


def load_pharmvar_table(path: str | Path) -> "pd.DataFrame":
    """Load PharmVar-style allele table (TSV: allele, rsid, alt, function)."""
    import pandas as pd

    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"PharmVar table not found: {path}")
    df = pd.read_csv(p, sep="\t", comment="#", dtype=str)
    df = df.apply(lambda c: c.str.strip() if c.dtype == object else c)
    return df


def _genotype_to_alleles(ref: str, alt: str, gt: str) -> List[str]:
    """Convert VCF REF, ALT, GT to list of two allele bases (one per chromosome)."""
    alleles: List[str] = []
    for part in gt.replace("|", "/").split("/"):
        part = part.strip()
        if part == "0" or part == ".":
            alleles.append(ref)
        elif part == "1":
            alleles.append(alt)
        else:
            alleles.append(ref)
    while len(alleles) < 2:
        alleles.append(ref)
    return alleles[:2]


def call_star_alleles(
    variants: Dict[str, Tuple[str, str, str]],
    allele_table: "pd.DataFrame",
) -> Dict[str, int]:
    """
    Determine star-allele copy counts from sample genotypes.

    variants: rsid -> (ref, alt, gt) from VCF. gt is e.g. "0/1", "1/1".
    allele_table: DataFrame with columns allele, rsid, alt (and optionally function).

    Returns dict allele -> count (0, 1, or 2). *1 is implied when no variant detected.
    """
    import pandas as pd

    allele_counts: Dict[str, int] = {}
    for _, row in allele_table.iterrows():
        allele = str(row.get("allele", "")).strip()
        rsid = str(row.get("rsid", "")).strip()
        defining_alt = str(row.get("alt", "")).strip()
        if not allele or rsid in ("-", "") or defining_alt in ("-", ""):
            continue
        if rsid not in variants:
            continue
        ref, alt, gt = variants[rsid]
        two = _genotype_to_alleles(ref, alt, gt)
        count = sum(1 for a in two if a == defining_alt)
        if count > 0:
            allele_counts[allele] = allele_counts.get(allele, 0) + count
    return allele_counts


def build_diplotype(allele_counts: Dict[str, int]) -> str:
    """
    Build diplotype string from allele copy counts (e.g. {"*2": 1} -> "*1/*2").
    Assumes diploid; pads with *1 to length 2.
    """
    expanded: List[str] = []
    for star, count in allele_counts.items():
        expanded.extend([star] * count)
    while len(expanded) < 2:
        expanded.append("*1")
    expanded = sorted(expanded)[:2]
    return f"{expanded[0]}/{expanded[1]}"


def load_cpic_translation(path: str | Path) -> Dict[str, str]:
    """Load CPIC diplotype -> phenotype (display) JSON. Skips keys starting with '_'."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"CPIC file not found: {path}")
    with open(p, "r") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def diplotype_to_phenotype(diplotype: str, translation: Dict[str, str]) -> str:
    """Return CPIC phenotype label for a diplotype, or 'Unknown' if not in table."""
    normalized = diplotype.strip()
    return translation.get(normalized, "Unknown")


def cpic_display_to_normalized(display: str) -> str:
    """Map CPIC display phenotype to internal normalized form for benchmarking."""
    d = display.strip().lower()
    if "normal" in d:
        return "extensive_metabolizer"
    if "intermediate" in d:
        return "intermediate_metabolizer"
    if "poor" in d:
        return "poor_metabolizer"
    if "rapid" in d and "ultra" not in d:
        return "extensive_metabolizer"  # Rapid = increased; treat as extensive for pipeline
    if "ultra" in d or "ultrarapid" in d:
        return "ultra_rapid_metabolizer"
    return "unknown"


def get_pgx_paths(
    gene: str, base_dir: Optional[Path] = None
) -> Tuple[Optional[Path], Optional[Path]]:
    """Return (pharmvar_tsv_path, cpic_json_path) for a gene if both exist."""
    base = base_dir or DEFAULT_PGX_DIR
    gene_lower = gene.lower()
    pv = base / "pharmvar" / f"{gene_lower}_alleles.tsv"
    cpic = base / "cpic" / f"{gene_lower}_phenotypes.json"
    return (pv if pv.is_file() else None, cpic if cpic.is_file() else None)


def call_gene_from_variants(
    gene: str,
    variants: Dict[str, Tuple[str, str, str]],
    base_dir: Optional[Path] = None,
) -> Optional[Dict]:
    """
    If curated data exists for the gene, run deterministic allele call and CPIC lookup.
    variants: rsid -> (ref, alt, gt).
    Returns dict with diplotype, phenotype_display, phenotype_normalized, alleles_detected; or None if no data.
    """
    pv_path, cpic_path = get_pgx_paths(gene, base_dir)
    if not pv_path or not cpic_path:
        return None
    try:
        table = load_pharmvar_table(pv_path)
        translation = load_cpic_translation(cpic_path)
    except Exception:
        return None
    allele_counts = call_star_alleles(variants, table)
    diplotype = build_diplotype(allele_counts)
    phenotype_display = diplotype_to_phenotype(diplotype, translation)
    phenotype_normalized = cpic_display_to_normalized(phenotype_display)
    alleles_detected = []
    for star, count in allele_counts.items():
        alleles_detected.extend([star] * count)
    return {
        "diplotype": diplotype,
        "phenotype_display": phenotype_display,
        "phenotype_normalized": phenotype_normalized,
        "alleles_detected": alleles_detected,
    }
