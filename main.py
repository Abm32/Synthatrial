#!/usr/bin/env python3
"""
SynthaTrial - In Silico Pharmacogenomics Platform
Main Entry Point

This script simulates drug effects on synthetic patient cohorts using Agentic AI.
"""

from src.input_processor import get_drug_fingerprint
from src.vector_search import find_similar_drugs
from src.agent_engine import run_simulation
import os

# 1. User Input (Simulated)
user_drug_smiles = "CC(=O)Nc1ccc(O)cc1"  # Paracetamol
user_drug_name = "Synthetic-Para-101"

# 2. Define a Synthetic Patient (Hardcoded for MVP)
patient_sp_01 = """
ID: SP-01
Age: 45
Genetics: CYP2D6 Poor Metabolizer (Allele *4/*4)
Conditions: Chronic Liver Disease (Mild)
Lifestyle: Alcohol consumer (Moderate)
"""

print(f"--- Starting Simulation for {user_drug_name} ---")

# 3. Process
try:
    vector = get_drug_fingerprint(user_drug_smiles)
    print("-> Drug digitized.")
except Exception as e:
    print(f"Error processing drug: {e}")
    exit()

# 4. Search
similar_drugs = find_similar_drugs(vector)
print(f"-> Found {len(similar_drugs)} similar biological anchors.")

# 5. Simulate
# Check for API Key before running LLM (Gemini)
if os.environ.get("GOOGLE_API_KEY"):
    result = run_simulation(user_drug_name, similar_drugs, patient_sp_01)
    print("\n--- SIMULATION RESULT ---")
    print(result)
else:
    print("\n[!] GOOGLE_API_KEY not found. Skipping LLM simulation.")
    print("Expected Input for LLM would be:")
    print(f"Drug: {user_drug_name}")
    print(f"Anchors: {similar_drugs}")
