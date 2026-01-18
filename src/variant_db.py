"""
Critical Pharmacogenomic Variants Database

Contains Tier 1 Clinical Variants (CPIC Level A) for CYP enzymes.
Source: PharmVar and CPIC Guidelines

This replaces naive variant counting with targeted allele lookup based on
specific rsIDs (Reference SNP IDs) that are known to affect enzyme function.
"""

# Critical Pharmacogenomic Variants (The "Famous" Ones)
# Source: PharmVar and CPIC Guidelines

VARIANT_DB = {
    "CYP2D6": {
        "rs3892097": {
            "allele": "*4",
            "impact": "Null",
            "name": "Splicing Defect (1846G>A)",
            "activity_score": 0.0
        },
        "rs1065852": {
            "allele": "*10",
            "impact": "Reduced",
            "name": "100C>T",
            "activity_score": 0.5
        },
        "rs16947": {
            "allele": "*2",
            "impact": "Normal",
            "name": "2850C>T (Common)",
            "activity_score": 1.0
        },
        "rs28371725": {
            "allele": "*41",
            "impact": "Reduced",
            "name": "2988G>A",
            "activity_score": 0.5
        },
        "rs35742686": {
            "allele": "*3",
            "impact": "Null",
            "name": "2549delA",
            "activity_score": 0.0
        },
        "rs5030655": {
            "allele": "*6",
            "impact": "Null",
            "name": "1707delT",
            "activity_score": 0.0
        },
        "rs5030865": {
            "allele": "*9",
            "impact": "Reduced",
            "name": "2613_2615delAAG",
            "activity_score": 0.5
        },
        "rs28371706": {
            "allele": "*17",
            "impact": "Reduced",
            "name": "1023C>T",
            "activity_score": 0.5
        },
        # Gene deletion (structural variant)
        "CYP2D6_DEL": {
            "allele": "*5",
            "impact": "Null",
            "name": "Gene Deletion",
            "activity_score": 0.0
        },
        # Gene duplication (structural variant)
        "CYP2D6_DUP": {
            "allele": "*1xN",
            "impact": "Increased",
            "name": "Gene Duplication",
            "activity_score": 1.0  # Multiplied by copy number
        }
    },
    "CYP2C19": {
        "rs4244285": {
            "allele": "*2",
            "impact": "Null",
            "name": "Splicing Defect (681G>A)",
            "activity_score": 0.0
        },
        "rs4986893": {
            "allele": "*3",
            "impact": "Null",
            "name": "Stop Codon (636G>A)",
            "activity_score": 0.0
        },
        "rs12248560": {
            "allele": "*17",
            "impact": "Increased",
            "name": "Promoter Variant (-806C>T)",
            "activity_score": 1.0
        },
        "rs28399504": {
            "allele": "*4",
            "impact": "Null",
            "name": "1A>G",
            "activity_score": 0.0
        },
        "rs56337013": {
            "allele": "*8",
            "impact": "Null",
            "name": "358T>C",
            "activity_score": 0.0
        },
        "rs72552267": {
            "allele": "*9",
            "impact": "Reduced",
            "name": "431G>A",
            "activity_score": 0.5
        },
        # Gene deletion
        "CYP2C19_DEL": {
            "allele": "*5",
            "impact": "Null",
            "name": "Gene Deletion",
            "activity_score": 0.0
        }
    },
    "CYP2C9": {
        "rs1799853": {
            "allele": "*2",
            "impact": "Reduced",
            "name": "Arg144Cys (430C>T)",
            "activity_score": 0.5
        },
        "rs1057910": {
            "allele": "*3",
            "impact": "Reduced",
            "name": "Ile359Leu (1075A>C)",
            "activity_score": 0.5
        },
        "rs28371686": {
            "allele": "*5",
            "impact": "Reduced",
            "name": "Asp360Glu",
            "activity_score": 0.5
        },
        "rs9332131": {
            "allele": "*6",
            "impact": "Null",
            "name": "818delA",
            "activity_score": 0.0
        },
        "rs28371685": {
            "allele": "*8",
            "impact": "Reduced",
            "name": "449G>A",
            "activity_score": 0.5
        },
        "rs7900194": {
            "allele": "*11",
            "impact": "Reduced",
            "name": "1003C>T",
            "activity_score": 0.5
        },
        # Gene deletion
        "CYP2C9_DEL": {
            "allele": "*5",
            "impact": "Null",
            "name": "Gene Deletion",
            "activity_score": 0.0
        }
    }
}


def get_activity_score_for_allele(gene: str, rsid: str) -> float:
    """
    Get the activity score for a specific variant.
    
    Args:
        gene: Gene name (CYP2D6, CYP2C19, CYP2C9)
        rsid: Variant rsID or structural variant identifier
        
    Returns:
        Activity score (0.0 to 1.0), or None if variant not found
    """
    gene_db = VARIANT_DB.get(gene, {})
    variant_info = gene_db.get(rsid)
    if variant_info:
        return variant_info.get("activity_score", 0.0)
    return None


def get_phenotype_prediction(gene: str, alleles_found: list, copy_number: int = 2) -> str:
    """
    Predicts metabolizer status based on found alleles using Activity Score method.
    
    Based on CPIC/PharmVar guidelines:
    - AS = 0: Poor Metabolizer
    - AS = 0.5-1.0: Intermediate Metabolizer
    - AS = 1.5-2.0: Extensive Metabolizer (Normal)
    - AS > 2.0: Ultra-Rapid Metabolizer (requires duplication)
    
    Args:
        gene: Gene name (CYP2D6, CYP2C19, CYP2C9)
        alleles_found: List of allele identifiers found (e.g., ['*4', '*10'])
        copy_number: Gene copy number (default 2, can be 0, 1, 2, 3+ for duplications)
        
    Returns:
        Metabolizer status string
    """
    if not alleles_found:
        # No variants found = wild-type (*1/*1)
        # Default: Extensive Metabolizer (Normal)
        base_score = 1.0
        total_score = base_score * copy_number
    else:
        # Calculate Activity Score from found alleles
        gene_db = VARIANT_DB.get(gene, {})
        total_score = 0.0
        
        # Sum activity scores from alleles
        for allele in alleles_found:
            # Find variant info by allele name
            for rsid, variant_info in gene_db.items():
                if variant_info["allele"] == allele:
                    total_score += variant_info.get("activity_score", 0.0)
                    break
        
        # If no specific alleles matched, assume wild-type
        if total_score == 0.0 and alleles_found:
            # Found variants but couldn't match - conservative assumption
            total_score = 1.0
        
        # Adjust for copy number (duplications)
        if copy_number > 2:
            # Duplication detected - multiply activity score
            total_score = total_score * (copy_number / 2.0)
        elif copy_number == 0:
            # Gene deletion
            total_score = 0.0
        elif copy_number == 1:
            # Single copy (hemizygous)
            total_score = total_score / 2.0
    
    # Classify based on Activity Score
    if total_score > 2.0:
        return "ultra_rapid_metabolizer"
    elif total_score >= 1.5:
        return "extensive_metabolizer"
    elif total_score >= 0.5:
        return "intermediate_metabolizer"
    else:
        return "poor_metabolizer"


def get_variant_info(gene: str, rsid: str) -> dict:
    """
    Get detailed information about a specific variant.
    
    Args:
        gene: Gene name
        rsid: Variant rsID
        
    Returns:
        Dictionary with variant information, or None if not found
    """
    gene_db = VARIANT_DB.get(gene, {})
    return gene_db.get(rsid)


def list_critical_variants(gene: str) -> list:
    """
    List all critical variants for a given gene.
    
    Args:
        gene: Gene name
        
    Returns:
        List of rsIDs for that gene
    """
    gene_db = VARIANT_DB.get(gene, {})
    return list(gene_db.keys())
