"""
VCF Processor Module

Handles parsing of VCF files from 1000 Genomes Project to extract genetic variants.
Focuses on CYP genes (CYP2D6 on chromosome 22, CYP2C19 on chr10, CYP3A4 on chr7).
"""

import gzip
import os
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from .variant_db import VARIANT_DB, get_phenotype_prediction, get_variant_info

# CYP gene locations (GRCh37/hg19 coordinates)
# Updated to include CYP2C9 and corrected CYP2C19 coordinates
CYP_GENE_LOCATIONS = {
    'CYP2D6': {
        'chrom': '22',
        'start': 42522500,  # Approximate, CYP2D6 region
        'end': 42530900
    },
    'CYP2C19': {
        'chrom': '10',
        'start': 96535040,  # Updated coordinates per user specification
        'end': 96625463
    },
    'CYP2C9': {
        'chrom': '10',
        'start': 96698415,  # CYP2C9 coordinates
        'end': 96749147
    },
    'CYP3A4': {
        'chrom': '7',
        'start': 99376140,
        'end': 99391055
    }
}

# Star Allele to Activity Score Mapping
# Based on CPIC/PharmVar guidelines
# Activity Score (AS) determines metabolizer status:
# - AS = 0: Poor Metabolizer
# - AS = 0.5-1.0: Intermediate Metabolizer  
# - AS = 1.5-2.0: Extensive Metabolizer (Normal)
# - AS > 2.0: Ultra-Rapid Metabolizer (requires duplication)

CYP2D6_ACTIVITY_SCORES = {
    '*1': 1.0,      # Wild type (normal function)
    '*2': 1.0,      # Normal function
    '*3': 0.0,      # No function (nonsense mutation)
    '*4': 0.0,      # No function (splicing defect)
    '*5': 0.0,      # No function (gene deletion)
    '*6': 0.0,      # No function (frameshift)
    '*9': 0.5,      # Reduced function
    '*10': 0.5,     # Reduced function
    '*17': 0.5,     # Reduced function
    '*29': 0.5,     # Reduced function
    '*41': 0.5,     # Reduced function
    '*1xN': 1.0,    # Normal function, duplicated (AS multiplied by copy number)
    '*2xN': 1.0,    # Normal function, duplicated
}

CYP2C19_ACTIVITY_SCORES = {
    '*1': 1.0,      # Wild type (normal function)
    '*2': 0.0,      # No function
    '*3': 0.0,      # No function
    '*4': 0.0,      # No function
    '*5': 0.0,      # No function
    '*6': 0.0,      # No function
    '*7': 0.0,      # No function
    '*8': 0.0,      # No function
    '*9': 0.5,      # Reduced function
    '*10': 0.5,     # Reduced function
    '*17': 1.5,     # Increased function (gain-of-function)
    '*1xN': 1.0,    # Normal function, duplicated
    '*17xN': 1.5,   # Increased function, duplicated (ultra-rapid)
}

CYP2C9_ACTIVITY_SCORES = {
    '*1': 1.0,      # Wild type (normal function)
    '*2': 0.5,      # Reduced function
    '*3': 0.0,      # No function
    '*4': 0.0,      # No function
    '*5': 0.0,      # No function
    '*6': 0.0,      # No function
    '*8': 0.0,      # No function
    '*11': 0.0,     # No function
    '*13': 0.5,     # Reduced function
    '*14': 0.5,     # Reduced function
}

# Gene-specific activity score mappings
CYP_ACTIVITY_SCORES = {
    'CYP2D6': CYP2D6_ACTIVITY_SCORES,
    'CYP2C19': CYP2C19_ACTIVITY_SCORES,
    'CYP2C9': CYP2C9_ACTIVITY_SCORES,
}


def parse_vcf_line(line: str) -> Optional[Dict]:
    """
    Parse a single VCF line (non-header).
    
    Returns:
        Dictionary with variant information or None if invalid
    """
    if line.startswith('#'):
        return None
    
    fields = line.strip().split('\t')
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
            'chrom': chrom,
            'pos': pos,
            'id': var_id,
            'ref': ref,
            'alt': alt,
            'qual': qual,
            'filter': filter_status,
            'info': info,
            'format': format_field,
            'genotypes': genotypes
        }
    except (ValueError, IndexError):
        return None


def extract_cyp_variants(vcf_path: str, gene: str = 'CYP2D6', sample_limit: Optional[int] = None) -> List[Dict]:
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
        raise ValueError(f"Unknown gene: {gene}. Supported: {list(CYP_GENE_LOCATIONS.keys())}")
    
    gene_loc = CYP_GENE_LOCATIONS[gene]
    target_chrom = gene_loc['chrom']
    start_pos = gene_loc['start']
    end_pos = gene_loc['end']
    
    variants = []
    
    # Open VCF file (handle gzip)
    open_func = gzip.open if vcf_path.endswith('.gz') else open
    mode = 'rt' if vcf_path.endswith('.gz') else 'r'
    
    try:
        with open_func(vcf_path, mode) as f:
            sample_names = None
            
            for line_num, line in enumerate(f):
                # Parse header to get sample names
                if line.startswith('#CHROM'):
                    header_fields = line.strip().split('\t')
                    if len(header_fields) > 9:
                        sample_names = header_fields[9:]
                        if sample_limit:
                            sample_names = sample_names[:sample_limit]
                    continue
                
                # Skip other header lines
                if line.startswith('#'):
                    continue
                
                # Parse variant line
                variant = parse_vcf_line(line)
                if not variant:
                    continue
                
                # Check if variant is in target region
                if (variant['chrom'] == target_chrom and 
                    start_pos <= variant['pos'] <= end_pos):
                    
                    # Add sample information
                    variant['gene'] = gene
                    variant['samples'] = {}
                    
                    if sample_names:
                        for i, sample_name in enumerate(sample_names):
                            if i < len(variant['genotypes']):
                                variant['samples'][sample_name] = variant['genotypes'][i]
                    
                    variants.append(variant)
                    
                    # Progress indicator for large files
                    if len(variants) % 100 == 0:
                        print(f"Found {len(variants)} variants in {gene} region...")
        
        print(f"Total variants found in {gene} region: {len(variants)}")
        return variants
        
    except FileNotFoundError:
        raise FileNotFoundError(f"VCF file not found: {vcf_path}")
    except Exception as e:
        raise RuntimeError(f"Error parsing VCF file: {e}")


def infer_metabolizer_status(variants: List[Dict], sample_id: str, gene: str = 'CYP2D6') -> str:
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
        return 'extensive_metabolizer'  # Default: wild-type (*1/*1)
    
    # Get critical variants database for this gene
    gene_db = VARIANT_DB.get(gene, {})
    if not gene_db:
        # Fallback: if gene not in database, assume normal
        return 'extensive_metabolizer'
    
    # Track found alleles and structural variants
    found_alleles = []
    copy_number = 2  # Default diploid
    has_deletion = False
    
    # Scan variants for critical rsIDs
    for variant in variants:
        if sample_id not in variant.get('samples', {}):
            continue
        
        genotype = variant['samples'][sample_id]
        rsid = variant.get('id', '')
        
        # Skip if genotype is homozygous reference (0/0) or missing
        if genotype in ['0/0', '0|0', '.', './.', '.|.']:
            continue
        
        # Check for structural variants (deletions/duplications)
        alt = str(variant.get('alt', ''))
        info = str(variant.get('info', ''))
        
        if '<DEL>' in alt or 'DEL' in info.upper():
            has_deletion = True
            found_alleles.append(f"{gene}_DEL")
            copy_number = 0
            continue
        
        if 'DUP' in alt.upper() or 'DUP' in info.upper() or 'MULTI' in info.upper():
            # Duplication detected - increase copy number
            copy_number = 3  # At least one extra copy
            found_alleles.append(f"{gene}_DUP")
            continue
        
        # Check if this variant is in our critical variants database
        if rsid in gene_db:
            variant_info = gene_db[rsid]
            allele = variant_info['allele']
            
            # Check if patient actually has this variant (not homozygous reference)
            # Parse genotype to determine zygosity
            is_variant = False
            is_homozygous = False
            
            if '/' in genotype:
                alleles = genotype.split('/')
                if len(alleles) == 2:
                    if alleles[0] != '0' and alleles[1] != '0':
                        is_variant = True
                        is_homozygous = (alleles[0] == alleles[1])
                    elif alleles[0] != '0' or alleles[1] != '0':
                        is_variant = True
            elif '|' in genotype:
                alleles = genotype.split('|')
                if len(alleles) == 2:
                    if alleles[0] != '0' and alleles[1] != '0':
                        is_variant = True
                        is_homozygous = (alleles[0] == alleles[1])
                    elif alleles[0] != '0' or alleles[1] != '0':
                        is_variant = True
            
            if is_variant:
                found_alleles.append(allele)
                print(f"  -> Found Critical Variant: {rsid} ({allele}) - {variant_info['impact']} - {variant_info['name']}")
    
    # Use variant_db function to predict phenotype based on found alleles
    phenotype = get_phenotype_prediction(gene, found_alleles, copy_number)
    
    return phenotype


def generate_patient_profile_from_vcf(
    vcf_path: str,
    sample_id: str,
    age: Optional[int] = None,
    conditions: Optional[List[str]] = None,
    lifestyle: Optional[Dict[str, str]] = None,
    vcf_path_chr10: Optional[str] = None
) -> str:
    """
    Generate a synthetic patient profile from VCF data.
    Supports both single VCF file (chromosome 22) and multiple VCF files (chr22 + chr10).
    
    Args:
        vcf_path: Path to VCF file (typically chromosome 22 for CYP2D6)
        sample_id: Sample ID from VCF file
        age: Patient age (random if not provided)
        conditions: List of medical conditions
        lifestyle: Dictionary with 'alcohol' and 'smoking' keys
        vcf_path_chr10: Optional path to chromosome 10 VCF file (for CYP2C9 and CYP2C19)
        
    Returns:
        Formatted patient profile string
    """
    import random
    
    # Extract CYP variants from chromosome 22 (CYP2D6)
    cyp2d6_variants = []
    chrom = vcf_path.split('/')[-1]
    
    if 'chr22' in chrom.lower() or '22' in chrom:
        try:
            cyp2d6_variants = extract_cyp_variants(vcf_path, 'CYP2D6', sample_limit=1)
        except Exception as e:
            print(f"Warning: Could not extract CYP2D6 variants: {e}")
    
    # Extract CYP variants from chromosome 10 (CYP2C9 and CYP2C19)
    cyp2c19_variants = []
    cyp2c9_variants = []
    
    if vcf_path_chr10 and os.path.exists(vcf_path_chr10):
        try:
            cyp2c19_variants = extract_cyp_variants(vcf_path_chr10, 'CYP2C19', sample_limit=1)
            print(f"✓ Extracted {len(cyp2c19_variants)} CYP2C19 variants from chromosome 10")
        except Exception as e:
            print(f"Warning: Could not extract CYP2C19 variants: {e}")
        
        try:
            cyp2c9_variants = extract_cyp_variants(vcf_path_chr10, 'CYP2C9', sample_limit=1)
            print(f"✓ Extracted {len(cyp2c9_variants)} CYP2C9 variants from chromosome 10")
        except Exception as e:
            print(f"Warning: Could not extract CYP2C9 variants: {e}")
    
    # Infer metabolizer statuses using improved Activity Score method
    cyp2d6_status = infer_metabolizer_status(cyp2d6_variants, sample_id, gene='CYP2D6') if cyp2d6_variants else 'extensive_metabolizer'
    cyp2c19_status = infer_metabolizer_status(cyp2c19_variants, sample_id, gene='CYP2C19') if cyp2c19_variants else 'extensive_metabolizer'
    cyp2c9_status = infer_metabolizer_status(cyp2c9_variants, sample_id, gene='CYP2C9') if cyp2c9_variants else 'extensive_metabolizer'
    
    # Build genetics text (include all detected enzymes)
    genetics_parts = []
    if cyp2d6_status != 'extensive_metabolizer':
        genetics_parts.append(f"CYP2D6 {cyp2d6_status.replace('_', ' ').title()}")
    if cyp2c19_status != 'extensive_metabolizer':
        genetics_parts.append(f"CYP2C19 {cyp2c19_status.replace('_', ' ').title()}")
    if cyp2c9_status != 'extensive_metabolizer':
        genetics_parts.append(f"CYP2C9 {cyp2c9_status.replace('_', ' ').title()}")
    
    # Default to extensive metabolizer if no variants found
    if not genetics_parts:
        genetics_text = "CYP2D6 Extensive Metabolizer"
    else:
        genetics_text = ", ".join(genetics_parts)
    
    # Default values
    if age is None:
        age = random.randint(25, 75)
    if conditions is None:
        conditions = []
    if lifestyle is None:
        lifestyle = {'alcohol': 'Moderate', 'smoking': 'Non-smoker'}
    
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
    lifestyle: Optional[Dict[str, str]] = None
) -> str:
    """
    Generate patient profile from multiple VCF files (chromosomes 22 and 10).
    This function extracts variants for all "Big 3" enzymes: CYP2D6, CYP2C19, CYP2C9.
    
    Args:
        vcf_path_chr22: Path to chromosome 22 VCF file (for CYP2D6)
        vcf_path_chr10: Path to chromosome 10 VCF file (for CYP2C9 and CYP2C19)
        sample_id: Sample ID from VCF file
        age: Patient age (random if not provided)
        conditions: List of medical conditions
        lifestyle: Dictionary with 'alcohol' and 'smoking' keys
        
    Returns:
        Formatted patient profile string with all CYP enzyme statuses
    """
    return generate_patient_profile_from_vcf(
        vcf_path_chr22,
        sample_id,
        age=age,
        conditions=conditions,
        lifestyle=lifestyle,
        vcf_path_chr10=vcf_path_chr10
    )


def get_sample_ids_from_vcf(vcf_path: str, limit: Optional[int] = 10) -> List[str]:
    """
    Get list of sample IDs from VCF file header.
    
    Args:
        vcf_path: Path to VCF file
        limit: Maximum number of samples to return (None = all)
        
    Returns:
        List of sample IDs
    """
    open_func = gzip.open if vcf_path.endswith('.gz') else open
    mode = 'rt' if vcf_path.endswith('.gz') else 'r'
    
    try:
        with open_func(vcf_path, mode) as f:
            for line in f:
                if line.startswith('#CHROM'):
                    header_fields = line.strip().split('\t')
                    if len(header_fields) > 9:
                        samples = header_fields[9:]
                        if limit:
                            return samples[:limit]
                        return samples
        return []
    except Exception as e:
        print(f"Error reading VCF header: {e}")
        return []
