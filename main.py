#!/usr/bin/env python3
"""
SynthaTrial - In Silico Pharmacogenomics Platform
Main Entry Point

This script simulates drug effects on synthetic patient cohorts using Agentic AI.
Supports both manual patient profiles and VCF-derived profiles from 1000 Genomes Project.
"""

import argparse

from src.agent_engine import run_simulation
from src.config import config
from src.exceptions import ConfigurationError
from src.input_processor import get_drug_fingerprint
from src.logging_config import setup_logging
from src.vcf_processor import generate_patient_profile_from_vcf, get_sample_ids_from_vcf
from src.vector_search import find_similar_drugs

# Set up logging
setup_logging()


def main():
    parser = argparse.ArgumentParser(
        description="Run pharmacogenomics simulation with support for Big 3 enzymes (CYP2D6, CYP2C19, CYP2C9)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single chromosome (CYP2D6 only):
  python main.py --vcf data/genomes/chr22.vcf.gz --drug-name Codeine

  # Multiple chromosomes (Big 3 enzymes):
  python main.py --vcf data/genomes/chr22.vcf.gz --vcf-chr10 data/genomes/chr10.vcf.gz --drug-name Warfarin

  # Manual profile:
  python main.py --cyp2d6-status poor_metabolizer --drug-name Tramadol
        """,
    )
    parser.add_argument(
        "--drug-smiles", default="CC(=O)Nc1ccc(O)cc1", help="SMILES string of drug"
    )
    parser.add_argument(
        "--drug-name", default="Synthetic-Para-101", help="Name of the drug"
    )
    parser.add_argument("--vcf", help="Path to VCF file for chromosome 22 (CYP2D6)")
    parser.add_argument(
        "--vcf-chr10", help="Path to VCF file for chromosome 10 (CYP2C9 and CYP2C19)"
    )
    parser.add_argument("--sample-id", help="Sample ID from VCF file")
    parser.add_argument(
        "--cyp2d6-status",
        choices=[
            "extensive_metabolizer",
            "intermediate_metabolizer",
            "poor_metabolizer",
            "ultra_rapid_metabolizer",
        ],
        default="poor_metabolizer",
        help="CYP2D6 metabolizer status (if not using VCF)",
    )

    args = parser.parse_args()

    user_drug_smiles = args.drug_smiles
    user_drug_name = args.drug_name

    print(f"--- Starting Simulation for {user_drug_name} ---")

    # 2. Define Patient Profile
    if args.vcf and os.path.exists(args.vcf):
        print(f"\n[VCF Mode] Using patient profile from VCF files")
        print(f"  Chromosome 22: {args.vcf}")
        if args.vcf_chr10:
            print(f"  Chromosome 10: {args.vcf_chr10}")
            print("  ✓ Big 3 enzymes enabled (CYP2D6, CYP2C19, CYP2C9)")
        else:
            print("  ⚠ Only CYP2D6 enabled (add --vcf-chr10 for Big 3 enzymes)")

        try:
            if args.sample_id:
                sample_id = args.sample_id
            else:
                # Get first available sample from chromosome 22
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
                lifestyle={"alcohol": "Moderate", "smoking": "Non-smoker"},
                vcf_path_chr10=args.vcf_chr10,
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
    # Validate configuration
    is_valid, missing_keys = config.validate_required()
    if not is_valid:
        print(
            f"⚠️ Configuration Error: Missing required keys: {', '.join(missing_keys)}"
        )
        print(
            "Please set GOOGLE_API_KEY or GEMINI_API_KEY in your environment or .env file."
        )
        return

    if config.GOOGLE_API_KEY:
        try:
            result = run_simulation(
                user_drug_name,
                similar_drugs,
                patient_profile,
                drug_smiles=user_drug_smiles,
            )
            print("\n" + "=" * 60)
            print("SIMULATION RESULT")
            print("=" * 60)
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
