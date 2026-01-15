"""
VCF Processor Module

Handles parsing of VCF files from 1000 Genomes Project to extract genetic variants.
Focuses on CYP genes (CYP2D6 on chromosome 22, CYP2C19 on chr10, CYP3A4 on chr7).
"""

import gzip
import os
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# CYP gene locations (GRCh37/hg19 coordinates)
CYP_GENE_LOCATIONS = {
    'CYP2D6': {
        'chrom': '22',
        'start': 42522500,  # Approximate, CYP2D6 region
        'end': 42530900
    },
    'CYP2C19': {
        'chrom': '10',
        'start': 96541615,
        'end': 96561468
    },
    'CYP3A4': {
        'chrom': '7',
        'start': 99376140,
        'end': 99391055
    }
}

# Known CYP2D6 star alleles and their functional status
# Simplified mapping - in reality, this requires haplotype phasing
CYP2D6_ALLELES = {
    '*1': 'extensive_metabolizer',  # Wild type
    '*2': 'extensive_metabolizer',  # Increased function
    '*3': 'poor_metabolizer',       # Nonsense mutation
    '*4': 'poor_metabolizer',       # Splicing defect
    '*5': 'poor_metabolizer',       # Gene deletion
    '*6': 'poor_metabolizer',       # Frameshift
    '*9': 'intermediate_metabolizer',
    '*10': 'intermediate_metabolizer',
    '*17': 'intermediate_metabolizer',
    '*29': 'intermediate_metabolizer',
    '*41': 'intermediate_metabolizer',
    '*1xN': 'ultra_rapid_metabolizer',  # Gene duplication
    '*2xN': 'ultra_rapid_metabolizer',
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


def infer_metabolizer_status(variants: List[Dict], sample_id: str) -> str:
    """
    Infer CYP metabolizer status from variants for a specific sample.
    
    This is a simplified inference - real pharmacogenomics requires
    haplotype phasing and star allele calling.
    
    Args:
        variants: List of variant dictionaries
        sample_id: Sample ID to analyze
        
    Returns:
        Metabolizer status: 'extensive_metabolizer', 'intermediate_metabolizer',
                           'poor_metabolizer', or 'ultra_rapid_metabolizer'
    """
    if not variants:
        return 'extensive_metabolizer'  # Default assumption
    
    # Count non-reference alleles for this sample
    non_ref_count = 0
    has_deletion = False
    
    for variant in variants:
        if sample_id not in variant.get('samples', {}):
            continue
        
        genotype = variant['samples'][sample_id]
        
        # Parse genotype (format: 0/0, 0/1, 1/1, etc.)
        # 0 = reference allele, 1+ = alternate allele
        if '/' in genotype:
            alleles = genotype.split('/')
            for allele in alleles:
                if allele != '0' and allele != '.':
                    non_ref_count += 1
                    if variant['alt'] == '<DEL>':
                        has_deletion = True
        
        elif '|' in genotype:  # Phased
            alleles = genotype.split('|')
            for allele in alleles:
                if allele != '0' and allele != '.':
                    non_ref_count += 1
    
    # Simplified inference based on variant count
    # In reality, this requires star allele calling
    if has_deletion:
        return 'poor_metabolizer'
    elif non_ref_count >= 4:
        return 'ultra_rapid_metabolizer'  # Possible duplication
    elif non_ref_count >= 2:
        return 'poor_metabolizer'
    elif non_ref_count == 1:
        return 'intermediate_metabolizer'
    else:
        return 'extensive_metabolizer'


def generate_patient_profile_from_vcf(
    vcf_path: str,
    sample_id: str,
    age: Optional[int] = None,
    conditions: Optional[List[str]] = None,
    lifestyle: Optional[Dict[str, str]] = None
) -> str:
    """
    Generate a synthetic patient profile from VCF data.
    
    Args:
        vcf_path: Path to VCF file
        sample_id: Sample ID from VCF file
        age: Patient age (random if not provided)
        conditions: List of medical conditions
        lifestyle: Dictionary with 'alcohol' and 'smoking' keys
        
    Returns:
        Formatted patient profile string
    """
    import random
    
    # Extract CYP variants (focus on CYP2D6 for chromosome 22)
    cyp2d6_variants = []
    cyp2c19_variants = []
    cyp3a4_variants = []
    
    chrom = vcf_path.split('/')[-1]
    
    # Check which chromosome this VCF file contains
    if 'chr22' in chrom.lower() or '22' in chrom:
        try:
            cyp2d6_variants = extract_cyp_variants(vcf_path, 'CYP2D6', sample_limit=1)
        except Exception as e:
            print(f"Warning: Could not extract CYP2D6 variants: {e}")
    
    # Infer metabolizer statuses
    cyp2d6_status = infer_metabolizer_status(cyp2d6_variants, sample_id) if cyp2d6_variants else 'extensive_metabolizer'
    cyp2c19_status = infer_metabolizer_status(cyp2c19_variants, sample_id) if cyp2c19_variants else 'extensive_metabolizer'
    cyp3a4_status = infer_metabolizer_status(cyp3a4_variants, sample_id) if cyp3a4_variants else 'extensive_metabolizer'
    
    # Build genetics text
    genetics_parts = []
    if cyp2d6_status != 'extensive_metabolizer':
        genetics_parts.append(f"CYP2D6 {cyp2d6_status.replace('_', ' ').title()}")
    if cyp2c19_status != 'extensive_metabolizer':
        genetics_parts.append(f"CYP2C19 {cyp2c19_status.replace('_', ' ').title()}")
    if cyp3a4_status != 'extensive_metabolizer':
        genetics_parts.append(f"CYP3A4 {cyp3a4_status.replace('_', ' ').title()}")
    
    genetics_text = ", ".join(genetics_parts) if genetics_parts else "CYP2D6 Extensive Metabolizer"
    
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
