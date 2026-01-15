#!/usr/bin/env python3
"""
SynthaTrial - In Silico Pharmacogenomics Platform
Main Entry Point

This script simulates drug effects on synthetic patient cohorts using Agentic AI.
Supports both manual patient profiles and VCF-derived profiles from 1000 Genomes Project.
"""

from src.input_processor import get_drug_fingerprint
from src.vector_search import find_similar_drugs
from src.agent_engine import run_simulation
from src.vcf_processor import generate_patient_profile_from_vcf, get_sample_ids_from_vcf
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='Run pharmacogenomics simulation')
    parser.add_argument('--drug-smiles', default='CC(=O)Nc1ccc(O)cc1', help='SMILES string of drug')
    parser.add_argument('--drug-name', default='Synthetic-Para-101', help='Name of the drug')
    parser.add_argument('--vcf', help='Path to VCF file (optional, uses VCF-derived patient if provided)')
    parser.add_argument('--sample-id', help='Sample ID from VCF file')
    parser.add_argument('--cyp2d6-status', 
                       choices=['extensive_metabolizer', 'intermediate_metabolizer', 
                               'poor_metabolizer', 'ultra_rapid_metabolizer'],
                       default='poor_metabolizer',
                       help='CYP2D6 metabolizer status (if not using VCF)')
    
    args = parser.parse_args()
    
    user_drug_smiles = args.drug_smiles
    user_drug_name = args.drug_name
    
    print(f"--- Starting Simulation for {user_drug_name} ---")
    
    # 2. Define Patient Profile
    if args.vcf and os.path.exists(args.vcf):
        print(f"\n[VCF Mode] Using patient profile from VCF: {args.vcf}")
        try:
            if args.sample_id:
                sample_id = args.sample_id
            else:
                # Get first available sample
                sample_ids = get_sample_ids_from_vcf(args.vcf, limit=1)
                if sample_ids:
                    sample_id = sample_ids[0]
                else:
                    raise ValueError("No samples found in VCF file")
            
            print(f"  Sample ID: {sample_id}")
            patient_profile = generate_patient_profile_from_vcf(
                args.vcf, 
                sample_id,
                age=45,
                conditions=["Chronic Liver Disease (Mild)"],
                lifestyle={'alcohol': 'Moderate', 'smoking': 'Non-smoker'}
            )
            print("  ✓ Generated patient profile from VCF")
        except Exception as e:
            print(f"  ⚠ Error processing VCF: {e}")
            print("  Falling back to manual profile...")
            patient_profile = create_manual_profile(args.cyp2d6_status)
    else:
        print("\n[Manual Mode] Using manually defined patient profile")
        patient_profile = create_manual_profile(args.cyp2d6_status)
    
    print(f"\nPatient Profile:")
    print(patient_profile)
    
    # 3. Process Drug
    print("\n--- Step 1: Processing Drug ---")
    try:
        vector = get_drug_fingerprint(user_drug_smiles)
        print(f"✓ Drug digitized: {len(vector)}-bit fingerprint")
    except Exception as e:
        print(f"✗ Error processing drug: {e}")
        return
    
    # 4. Search for Similar Drugs
    print("\n--- Step 2: Vector Similarity Search ---")
    similar_drugs = find_similar_drugs(vector)
    print(f"✓ Found {len(similar_drugs)} similar drugs:")
    for i, drug in enumerate(similar_drugs, 1):
        print(f"  {i}. {drug}")
    
    # 5. Run AI Simulation
    print("\n--- Step 3: AI Simulation ---")
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            result = run_simulation(user_drug_name, similar_drugs, patient_profile)
            print("\n" + "="*60)
            print("SIMULATION RESULT")
            print("="*60)
            print(result)
        except Exception as e:
            print(f"✗ Error running simulation: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠ GOOGLE_API_KEY not found. Skipping LLM simulation.")
        print("\nExpected Input for LLM:")
        print(f"  Drug: {user_drug_name}")
        print(f"  Similar Drugs: {', '.join(similar_drugs)}")
        print(f"  Patient Profile:\n{patient_profile}")


def create_manual_profile(cyp2d6_status: str) -> str:
    """Create a manual patient profile."""
    return f"""ID: SP-01
Age: 45
Genetics: CYP2D6 {cyp2d6_status.replace('_', ' ').title()}
Conditions: Chronic Liver Disease (Mild)
Lifestyle: Alcohol consumer (Moderate)"""


if __name__ == "__main__":
    main()
