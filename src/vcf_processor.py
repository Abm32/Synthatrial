"""
VCF Processor Module

Handles parsing of VCF files from 1000 Genomes Project to extract genetic variants.
Focuses on CYP genes (CYP2D6 on chromosome 22, CYP2C19 on chr10, CYP3A4 on chr7).
"""

import gzip
import logging
import os
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from .allele_caller import call_gene_from_variants
from .exceptions import VCFProcessingError
from .variant_db import (
    VARIANT_DB,
    get_allele_interpretation,
    get_phenotype_prediction,
    get_variant_info,
)

# Set up logging
logger = logging.getLogger(__name__)

# CYP gene locations (GRCh37/hg19 coordinates)
# Updated to include CYP2C9 and corrected CYP2C19 coordinates
CYP_GENE_LOCATIONS = {
    "CYP2D6": {
        "chrom": "22",
        "start": 42522500,  # Approximate, CYP2D6 region
        "end": 42530900,
    },
    "CYP2C19": {
        "chrom": "10",
        "start": 96535040,  # Updated coordinates per user specification
        "end": 96625463,
    },
    "CYP2C9": {"chrom": "10", "start": 96698415, "end": 96749147},  # CYP2C9 coordinates
    "CYP3A4": {"chrom": "7", "start": 99376140, "end": 99391055},
    # Phase II Enzymes
    "UGT1A1": {"chrom": "2", "start": 234668875, "end": 234689625},
    # Transporters
    "SLCO1B1": {"chrom": "12", "start": 21288593, "end": 21397223},
}

# Genes included in patient profile (must have VARIANT_DB entry and CYP_GENE_LOCATIONS).
# Order: Big 3 CYPs first, then Phase II / transporters.
PROFILE_GENES = ["CYP2D6", "CYP2C19", "CYP2C9", "UGT1A1", "SLCO1B1"]

# Star Allele to Activity Score Mapping
# Based on CPIC/PharmVar guidelines
# Activity Score (AS) determines metabolizer status:
# - AS = 0: Poor Metabolizer
# - AS = 0.5-1.0: Intermediate Metabolizer
# - AS = 1.5-2.0: Extensive Metabolizer (Normal)
# - AS > 2.0: Ultra-Rapid Metabolizer (requires duplication)

CYP2D6_ACTIVITY_SCORES = {
    "*1": 1.0,  # Wild type (normal function)
    "*2": 1.0,  # Normal function
    "*3": 0.0,  # No function (nonsense mutation)
    "*4": 0.0,  # No function (splicing defect)
    "*5": 0.0,  # No function (gene deletion)
    "*6": 0.0,  # No function (frameshift)
    "*9": 0.5,  # Reduced function
    "*10": 0.5,  # Reduced function
    "*17": 0.5,  # Reduced function
    "*29": 0.5,  # Reduced function
    "*41": 0.5,  # Reduced function
    "*1xN": 1.0,  # Normal function, duplicated (AS multiplied by copy number)
    "*2xN": 1.0,  # Normal function, duplicated
}

CYP2C19_ACTIVITY_SCORES = {
    "*1": 1.0,  # Wild type (normal function)
    "*2": 0.0,  # No function
    "*3": 0.0,  # No function
    "*4": 0.0,  # No function
    "*5": 0.0,  # No function
    "*6": 0.0,  # No function
    "*7": 0.0,  # No function
    "*8": 0.0,  # No function
    "*9": 0.5,  # Reduced function
    "*10": 0.5,  # Reduced function
    "*17": 1.5,  # Increased function (gain-of-function)
    "*1xN": 1.0,  # Normal function, duplicated
    "*17xN": 1.5,  # Increased function, duplicated (ultra-rapid)
}

CYP2C9_ACTIVITY_SCORES = {
    "*1": 1.0,  # Wild type (normal function)
    "*2": 0.5,  # Reduced function
    "*3": 0.0,  # No function
    "*4": 0.0,  # No function
    "*5": 0.0,  # No function
    "*6": 0.0,  # No function
    "*8": 0.0,  # No function
    "*11": 0.0,  # No function
    "*13": 0.5,  # Reduced function
    "*14": 0.5,  # Reduced function
}

# Gene-specific activity score mappings
CYP_ACTIVITY_SCORES = {
    "CYP2D6": CYP2D6_ACTIVITY_SCORES,
    "CYP2C19": CYP2C19_ACTIVITY_SCORES,
    "CYP2C9": CYP2C9_ACTIVITY_SCORES,
}


def validate_vcf(file_content: str) -> Tuple[bool, str]:
    """
    Validate VCF file content.

    Args:
        file_content: Content of the VCF file as string

    Returns:
        Tuple of (is_valid, error_message)
    """
    lines = file_content.strip().split("\n")
    if not lines:
        return False, "Empty file"

    # Check for VCF header
    if not lines[0].startswith("##fileformat=VCF"):
        return False, "Missing VCF fileformat header (##fileformat=VCF...)"

    # Check for column header
    has_header = False
    for line in lines:
        if line.startswith("#CHROM"):
            has_header = True
            fields = line.strip().split("\t")
            required = ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO"]
            if not all(field in fields for field in required):
                return False, f"Missing required columns. Found: {fields}"
            break

    if not has_header:
        return False, "Missing column header line starting with #CHROM"

    return True, "Valid VCF"


def parse_vcf_line(line: str) -> Optional[Dict]:
    """
    Parse a single VCF line (non-header).

    Returns:
        Dictionary with variant information or None if invalid
    """
    if line.startswith("#"):
        return None

    fields = line.strip().split("\t")
    if len(fields) < 10:
        return None

    try:
        chrom = fields[0]
        pos = int(fields[1])
        var_id = fields[2]
        ref = fields[3]
        alt = fields[4]
        qual = fields[5]
        filter_status = fields[6]
        info = fields[7]
        format_field = fields[8]
        genotypes = fields[9:]

        return {
            "chrom": chrom,
            "pos": pos,
            "id": var_id,
            "ref": ref,
            "alt": alt,
            "qual": qual,
            "filter": filter_status,
            "info": info,
            "format": format_field,
            "genotypes": genotypes,
        }
    except (ValueError, IndexError):
        return None


def extract_cyp_variants(
    vcf_path: str, gene: str = "CYP2D6", sample_limit: Optional[int] = None
) -> List[Dict]:
    """
    Extract variants in CYP gene regions from VCF file.

    Args:
        vcf_path: Path to VCF file (can be .gz compressed)
        gene: Gene name (CYP2D6, CYP2C19, CYP3A4)
        sample_limit: Limit number of samples to process (None = all)

    Returns:
        List of variant dictionaries with sample genotypes
    """
    if gene not in CYP_GENE_LOCATIONS:
        raise VCFProcessingError(
            f"Unknown gene: {gene}. Supported: {list(CYP_GENE_LOCATIONS.keys())}",
            vcf_path=vcf_path,
        )

    gene_loc = CYP_GENE_LOCATIONS[gene]
    target_chrom = gene_loc["chrom"]
    start_pos = gene_loc["start"]
    end_pos = gene_loc["end"]

    variants = []

    # Open VCF file (handle gzip)
    open_func = gzip.open if vcf_path.endswith(".gz") else open
    mode = "rt" if vcf_path.endswith(".gz") else "r"

    try:
        with open_func(vcf_path, mode) as f:
            sample_names = None

            for line_num, line in enumerate(f):
                # Parse header to get sample names
                if line.startswith("#CHROM"):
                    header_fields = line.strip().split("\t")
                    if len(header_fields) > 9:
                        sample_names = header_fields[9:]
                        if sample_limit:
                            sample_names = sample_names[:sample_limit]
                    continue

                # Skip other header lines
                if line.startswith("#"):
                    continue

                # Parse variant line
                variant = parse_vcf_line(line)
                if not variant:
                    continue

                # Check if variant is in target region
                if (
                    variant["chrom"] == target_chrom
                    and start_pos <= variant["pos"] <= end_pos
                ):
                    # Add sample information
                    variant["gene"] = gene
                    variant["samples"] = {}

                    if sample_names:
                        for i, sample_name in enumerate(sample_names):
                            if i < len(variant["genotypes"]):
                                variant["samples"][sample_name] = variant["genotypes"][
                                    i
                                ]

                    variants.append(variant)

                    # Progress indicator for large files
                    if len(variants) % 100 == 0:
                        logger.debug(
                            f"Found {len(variants)} variants in {gene} region..."
                        )

        logger.info(f"Total variants found in {gene} region: {len(variants)}")
        return variants

    except FileNotFoundError:
        raise VCFProcessingError(f"VCF file not found: {vcf_path}", vcf_path=vcf_path)
    except Exception as e:
        logger.error(f"Error parsing VCF file: {e}", exc_info=True)
        raise VCFProcessingError(
            f"Error parsing VCF file: {str(e)}", vcf_path=vcf_path
        ) from e


def infer_metabolizer_status(
    variants: List[Dict], sample_id: str, gene: str = "CYP2D6"
) -> str:
    """
    Infer CYP metabolizer status using Targeted Variant Lookup (Dictionary-Based Genotyping).

    This method replaces naive variant counting with targeted lookup of Tier 1 Clinical Variants
    (CPIC Level A) based on specific rsIDs. Only variants known to affect enzyme function are
    considered, filtering out synonymous mutations and intronic variants.

    Based on CPIC/PharmVar guidelines:
    - AS = 0: Poor Metabolizer
    - AS = 0.5-1.0: Intermediate Metabolizer
    - AS = 1.5-2.0: Extensive Metabolizer (Normal)
    - AS > 2.0: Ultra-Rapid Metabolizer

    Args:
        variants: List of variant dictionaries from VCF
        sample_id: Sample ID to analyze
        gene: Gene name (CYP2D6, CYP2C19, CYP2C9)

    Returns:
        Metabolizer status: 'extensive_metabolizer', 'intermediate_metabolizer',
                           'poor_metabolizer', or 'ultra_rapid_metabolizer'
    """
    if not variants:
        return "extensive_metabolizer"  # Default: wild-type (*1/*1)

    # Get critical variants database for this gene
    gene_db = VARIANT_DB.get(gene, {})
    if not gene_db:
        # Fallback: if gene not in database, assume normal
        return "extensive_metabolizer"

    # Track found alleles and structural variants
    found_alleles = []
    copy_number = 2  # Default diploid
    has_deletion = False

    # Scan variants for critical rsIDs
    for variant in variants:
        if sample_id not in variant.get("samples", {}):
            continue

        genotype = variant["samples"][sample_id]
        rsid = variant.get("id", "")

        # Skip if genotype is homozygous reference (0/0) or missing
        if genotype in ["0/0", "0|0", ".", "./.", ".|."]:
            continue

        # Check for structural variants (deletions/duplications)
        alt = str(variant.get("alt", ""))
        info = str(variant.get("info", ""))

        if "<DEL>" in alt or "DEL" in info.upper():
            has_deletion = True
            found_alleles.append(f"{gene}_DEL")
            copy_number = 0
            continue

        if "DUP" in alt.upper() or "DUP" in info.upper() or "MULTI" in info.upper():
            # Duplication detected - increase copy number
            copy_number = 3  # At least one extra copy
            found_alleles.append(f"{gene}_DUP")
            continue

        # Check if this variant is in our critical variants database
        if rsid in gene_db:
            variant_info = gene_db[rsid]
            allele = variant_info["allele"]

            # Check if patient actually has this variant (not homozygous reference)
            # Parse genotype to determine zygosity
            is_variant = False
            is_homozygous = False

            if "/" in genotype:
                alleles = genotype.split("/")
                if len(alleles) == 2:
                    if alleles[0] != "0" and alleles[1] != "0":
                        is_variant = True
                        is_homozygous = alleles[0] == alleles[1]
                    elif alleles[0] != "0" or alleles[1] != "0":
                        is_variant = True
            elif "|" in genotype:
                alleles = genotype.split("|")
                if len(alleles) == 2:
                    if alleles[0] != "0" and alleles[1] != "0":
                        is_variant = True
                        is_homozygous = alleles[0] == alleles[1]
                    elif alleles[0] != "0" or alleles[1] != "0":
                        is_variant = True

            if is_variant:
                found_alleles.append(allele)
                logger.debug(
                    f"Found Critical Variant: {rsid} ({allele}) - {variant_info['impact']} - {variant_info['name']}"
                )

    # Use variant_db function to predict phenotype based on found alleles
    phenotype = get_phenotype_prediction(gene, found_alleles, copy_number)

    return phenotype


def infer_metabolizer_status_with_alleles(
    variants: List[Dict], sample_id: str, gene: str = "CYP2D6"
) -> Dict:
    """
    Infer metabolizer status and return allele-level interpretation for transparency.
    Returns phenotype, called alleles, allele call string (e.g. *1/*4), and PharmVar-style interpretations.
    """
    result = {
        "phenotype": "extensive_metabolizer",
        "alleles": [],
        "allele_call": "",
        "interpretation": [],
    }
    if not variants:
        result["allele_call"] = "*1/*1"
        result["interpretation"] = [f"{gene}*1: Normal function (wild-type)"]
        return result

    gene_db = VARIANT_DB.get(gene, {})
    if not gene_db:
        return result

    found_alleles: List[str] = []
    copy_number = 2
    has_deletion = False

    for variant in variants:
        if sample_id not in variant.get("samples", {}):
            continue
        genotype = variant["samples"][sample_id]
        rsid = variant.get("id", "")
        if genotype in ["0/0", "0|0", ".", "./.", ".|."]:
            continue
        alt = str(variant.get("alt", ""))
        info = str(variant.get("info", ""))
        if "<DEL>" in alt or "DEL" in info.upper():
            has_deletion = True
            found_alleles.append(f"{gene}_DEL")
            copy_number = 0
            continue
        if "DUP" in alt.upper() or "DUP" in info.upper() or "MULTI" in info.upper():
            copy_number = 3
            found_alleles.append(f"{gene}_DUP")
            continue
        if rsid in gene_db:
            variant_info = gene_db[rsid]
            allele = variant_info["allele"]
            is_variant = False
            if "/" in genotype:
                alleles = genotype.split("/")
                if len(alleles) == 2 and (alleles[0] != "0" or alleles[1] != "0"):
                    is_variant = True
            elif "|" in genotype:
                alleles = genotype.split("|")
                if len(alleles) == 2 and (alleles[0] != "0" or alleles[1] != "0"):
                    is_variant = True
            if is_variant:
                found_alleles.append(allele)

    result["phenotype"] = get_phenotype_prediction(gene, found_alleles, copy_number)
    result["alleles"] = found_alleles
    if not found_alleles:
        result["allele_call"] = "*1/*1"
        result["interpretation"] = [f"{gene}*1: Normal function (wild-type)"]
    else:
        result["allele_call"] = "/".join(sorted(set(found_alleles)))
        result["interpretation"] = get_allele_interpretation(gene, found_alleles)
    return result


def _variants_to_genotype_map(
    variants: List[Dict], sample_id: str
) -> Dict[str, Tuple[str, str, str]]:
    """Build rsid -> (ref, alt, gt) from VCF variant list for one sample."""
    out: Dict[str, Tuple[str, str, str]] = {}
    for v in variants:
        rsid = v.get("id") or v.get("rsid", "")
        if (
            not rsid
            or rsid.startswith("CYP")
            or "DEL" in str(rsid)
            or "DUP" in str(rsid)
        ):
            continue
        ref = str(v.get("ref", ""))
        alt = str(v.get("alt", ""))
        if not ref:
            continue
        if "," in alt:
            alt = alt.split(",")[0]
        samples = v.get("samples", {})
        gt = samples.get(sample_id, "0/0")
        if not gt or gt in (".", "./.", ".|."):
            continue
        out[rsid] = (ref, alt, gt)
    return out


def _chrom_key_for_gene(gene: str) -> Optional[str]:
    """Return VCF chromosome key for a gene (e.g. CYP2D6 -> chr22)."""
    loc = CYP_GENE_LOCATIONS.get(gene)
    if not loc:
        return None
    c = loc["chrom"].upper()
    if c == "X" or c == "Y":
        return f"chr{c}"
    try:
        return f"chr{int(c)}"
    except (TypeError, ValueError):
        return None


def generate_patient_profile_from_vcf(
    vcf_path: str,
    sample_id: str,
    age: Optional[int] = None,
    conditions: Optional[List[str]] = None,
    lifestyle: Optional[Dict[str, str]] = None,
    vcf_path_chr10: Optional[str] = None,
    vcf_paths_by_chrom: Optional[Dict[str, str]] = None,
) -> str:
    """
    Generate a synthetic patient profile from VCF data.
    Uses chr22 (CYP2D6), chr10 (CYP2C19, CYP2C9), chr2 (UGT1A1), chr12 (SLCO1B1)
    when the corresponding VCF files are provided via vcf_paths_by_chrom or legacy args.

    Args:
        vcf_path: Path to primary VCF (chr22 for CYP2D6); used if vcf_paths_by_chrom not set.
        sample_id: Sample ID from VCF file
        age: Patient age (random if not provided)
        conditions: List of medical conditions
        lifestyle: Dictionary with 'alcohol' and 'smoking' keys
        vcf_path_chr10: Optional path to chr10 (CYP2C9/CYP2C19); used if vcf_paths_by_chrom not set.
        vcf_paths_by_chrom: Optional dict chromosome -> path (e.g. {"chr22": path, "chr10": path,
            "chr2": path, "chr12": path}). When set, overrides vcf_path/vcf_path_chr10 for lookups.
    Returns:
        Formatted patient profile string
    """
    import random

    # Build chromosome -> path map: prefer vcf_paths_by_chrom, else legacy args
    if vcf_paths_by_chrom:
        paths = {k: p for k, p in vcf_paths_by_chrom.items() if p and os.path.exists(p)}
    else:
        paths = {}
        if vcf_path and os.path.exists(vcf_path):
            paths["chr22"] = vcf_path
        if vcf_path_chr10 and os.path.exists(vcf_path_chr10):
            paths["chr10"] = vcf_path_chr10

    # Extract variants and infer status for each profile gene from the correct chromosome VCF
    gene_variants: Dict[str, List] = {g: [] for g in PROFILE_GENES}
    for gene in PROFILE_GENES:
        chr_key = _chrom_key_for_gene(gene)
        if not chr_key:
            continue
        vcf_file = paths.get(chr_key)
        if not vcf_file:
            continue
        try:
            gene_variants[gene] = extract_cyp_variants(vcf_file, gene, sample_limit=1)
            if gene_variants[gene]:
                logger.info(
                    f"Extracted {len(gene_variants[gene])} {gene} variants from {chr_key}"
                )
        except Exception as e:
            logger.warning(f"Could not extract {gene} variants from {chr_key}: {e}")

    # Infer status and allele-level interpretation per gene (for transparency)
    # CYP2C19: use curated PharmVar/CPIC data when present (deterministic, guideline-derived)
    def _status_and_alleles(
        gene: str, default: str = "extensive_metabolizer"
    ) -> Tuple[str, Optional[str], List[str]]:
        if gene == "SLCO1B1":
            default = "average_function"
        if not gene_variants[gene]:
            return default, None, []
        # Try CPIC/PharmVar path first for genes with data/pgx files (e.g. CYP2C19)
        try:
            var_map = _variants_to_genotype_map(gene_variants[gene], sample_id)
            if var_map:
                cpic_result = call_gene_from_variants(gene, var_map)
                if cpic_result:
                    phen = cpic_result["phenotype_normalized"]
                    diplo = cpic_result["diplotype"]
                    interp = [
                        f"{gene} {diplo} → {cpic_result['phenotype_display']} (CPIC)"
                    ]
                    return phen, diplo, interp
        except Exception as e:
            logger.debug(f"CPIC/PharmVar path skipped for {gene}: {e}")
        info = infer_metabolizer_status_with_alleles(
            gene_variants[gene], sample_id, gene=gene
        )
        return (
            info["phenotype"],
            info.get("allele_call"),
            info.get("interpretation", []),
        )

    genetics_parts = []
    for gene in PROFILE_GENES:
        status, allele_call, interpretation = _status_and_alleles(gene)
        s = status
        if s == "extensive_metabolizer" and gene != "SLCO1B1":
            continue
        if gene == "SLCO1B1" and s == "average_function":
            continue
        term = s.replace("_", " ").title()
        if gene == "SLCO1B1":
            term = term.replace("Metabolizer", "Function")
        # Include allele call when available (e.g. "CYP2D6 *1/*4 (Poor Metabolizer)")
        if allele_call and allele_call != "*1/*1":
            genetics_parts.append(f"{gene} {allele_call} ({term})")
        else:
            genetics_parts.append(f"{gene} {term}")

    if not genetics_parts:
        genetics_text = "CYP2D6 Extensive Metabolizer (Normal)"
    else:
        genetics_text = ", ".join(genetics_parts)

    # Default values
    if age is None:
        age = random.randint(25, 75)
    if conditions is None:
        conditions = []
    if lifestyle is None:
        lifestyle = {"alcohol": "Moderate", "smoking": "Non-smoker"}

    conditions_text = ", ".join(conditions) if conditions else "None"
    lifestyle_text = f"Alcohol: {lifestyle.get('alcohol', 'Moderate')}, Smoking: {lifestyle.get('smoking', 'Non-smoker')}"

    profile = f"""ID: {sample_id}
Age: {age}
Genetics: {genetics_text}
Conditions: {conditions_text}
Lifestyle: {lifestyle_text}
Source: 1000 Genomes Project VCF"""

    return profile


def generate_patient_profile_multi_chromosome(
    vcf_path_chr22: str,
    vcf_path_chr10: Optional[str],
    sample_id: str,
    age: Optional[int] = None,
    conditions: Optional[List[str]] = None,
    lifestyle: Optional[Dict[str, str]] = None,
    vcf_paths_by_chrom: Optional[Dict[str, str]] = None,
) -> str:
    """
    Generate patient profile from multiple VCF files.
    When vcf_paths_by_chrom is provided, uses it for all chromosomes (chr2, chr10, chr12, chr22, etc.).
    """
    return generate_patient_profile_from_vcf(
        vcf_path_chr22,
        sample_id,
        age=age,
        conditions=conditions,
        lifestyle=lifestyle,
        vcf_path_chr10=vcf_path_chr10,
        vcf_paths_by_chrom=vcf_paths_by_chrom,
    )


def get_sample_ids_from_vcf(vcf_path: str, limit: Optional[int] = 10) -> List[str]:
    """
    Get list of sample IDs from VCF file header.
    """
    open_func = gzip.open if vcf_path.endswith(".gz") else open
    mode = "rt" if vcf_path.endswith(".gz") else "r"

    try:
        with open_func(vcf_path, mode) as f:
            for line in f:
                if line.startswith("#CHROM"):
                    header_fields = line.strip().split("\t")
                    if len(header_fields) > 9:
                        samples = header_fields[9:]
                        if limit:
                            return samples[:limit]
                        return samples
        return []
    except Exception as e:
        print(f"Error reading VCF header: {e}")
        return []


# Chromosomes supported for discovery (autosomes 1-22, X, Y).
# Order: longest token first so "chr22" matches before "chr2".
SUPPORTED_CHROMOSOMES_ORDER: Tuple[str, ...] = tuple(
    sorted(
        [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY"],
        key=lambda x: -len(x),
    )
)


def discover_vcf_paths(genomes_dir: str = "data/genomes") -> Dict[str, str]:
    """
    Discover VCF files in data/genomes and map them to chromosomes.

    Accepts both short names (chr22.vcf.gz, chr10.vcf.gz) and long 1000 Genomes
    names (e.g. ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz).
    Returns a dict mapping chromosome key to absolute path, e.g. {"chr22": path, "chr10": path}.
    Any chr1–chr22, chrX, chrY present in the filename is detected.
    """
    if not os.path.isdir(genomes_dir):
        return {}
    found: Dict[str, str] = {}
    try:
        for name in os.listdir(genomes_dir):
            if not name.endswith(".vcf.gz"):
                continue
            path = os.path.join(genomes_dir, name)
            if not os.path.isfile(path):
                continue
            # Match all chrN/chrX/chrY in filename; take first that we support (longest-first)
            for c in SUPPORTED_CHROMOSOMES_ORDER:
                if c not in name:
                    continue
                idx = name.find(c)
                next_char = name[idx + len(c) : idx + len(c) + 1]
                if next_char and next_char.isdigit():
                    continue
                if c not in found:
                    found[c] = os.path.abspath(path)
                break
    except OSError as e:
        logger.warning(f"Could not list genomes dir {genomes_dir}: {e}")
    return found
