# src/pgx_triggers.py

"""
Drug → Gene trigger map (CPIC-style).

We only surface PGx interpretations when the drug being analyzed
has a guideline-relevant gene.

Example:
- Warfarin → CYP2C9 + VKORC1
- Simvastatin → SLCO1B1
- Clopidogrel → CYP2C19
"""

DRUG_GENE_TRIGGERS = {
    # Statins (SLCO1B1)
    "simvastatin": ["SLCO1B1"],
    "atorvastatin": ["SLCO1B1"],
    "rosuvastatin": ["SLCO1B1"],
    "pravastatin": ["SLCO1B1"],
    "lovastatin": ["SLCO1B1"],
    "fluvastatin": ["SLCO1B1"],
    "pitavastatin": ["SLCO1B1"],
    # Warfarin
    "warfarin": ["CYP2C9", "VKORC1"],
    # Clopidogrel
    "clopidogrel": ["CYP2C19"],
}
