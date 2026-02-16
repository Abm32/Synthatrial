"""
Deterministic SLCO1B1 (statin myopathy) PGx: rs4149056 c.521T>C.

Uses curated variant table and CPIC-style phenotype map.
Triggered when drug is a statin (CPIC guideline).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

DEFAULT_PGX_DIR = Path(__file__).resolve().parent.parent / "data" / "pgx"


def _pgx_path(*parts: str, base_dir: Optional[Path] = None) -> Path:
    base = base_dir or DEFAULT_PGX_DIR
    return base.joinpath(*parts)


def alt_dosage(gt: str):
    """VCF genotype → ALT allele dosage (0, 1, or 2)."""
    if gt in ("0/0", "0|0"):
        return 0
    if gt in ("0/1", "1/0", "0|1", "1|0"):
        return 1
    if gt in ("1/1", "1|1"):
        return 2
    return None


def load_slco1b1_phenotypes(base_dir: Optional[Path] = None) -> Dict[str, str]:
    """Load SLCO1B1 genotype → phenotype (TT/TC/CC → risk level)."""
    path = _pgx_path("cpic", "slco1b1_phenotypes.json", base_dir=base_dir)
    if not path.is_file():
        return {}
    with open(path, "r") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def interpret_slco1b1_from_vcf(
    var_map: Dict[str, Tuple[str, str, str]], base_dir: Optional[Path] = None
) -> Optional[Dict[str, str]]:
    """
    Deterministic SLCO1B1 interpretation based on rs4149056 (c.521T>C).
    var_map: rsid -> (ref, alt, gt). Returns genotype (TT/TC/CC) and phenotype.
    """
    if "rs4149056" not in var_map:
        return None
    ref, alt, gt = var_map["rs4149056"]
    dosage = alt_dosage(gt)
    if dosage == 0:
        geno = f"{ref}{ref}"
    elif dosage == 1:
        geno = f"{ref}{alt}"
    elif dosage == 2:
        geno = f"{alt}{alt}"
    else:
        geno = "Unknown"
    table = load_slco1b1_phenotypes(base_dir=base_dir)
    phenotype = table.get(geno, "Unknown function")
    return {
        "gene": "SLCO1B1",
        "rsid": "rs4149056",
        "genotype": geno,
        "phenotype": phenotype,
    }
