# Update: Structure Comparison in LLM Prompt

**Date:** Implementation update  
**Action Item:** Ensure agent_engine.py prompt includes drug structures (SMILES) for comparison

---

## ✅ Changes Implemented

### 1. Vector Search Enhancement (`src/vector_search.py`)

**Before:**
```python
found_drugs.append(f"{drug_name} (Side Effects: {side_effects})")
```

**After:**
```python
drug_info = f"{drug_name} | SMILES: {smiles} | Side Effects: {side_effects} | Targets: {targets}"
found_drugs.append(drug_info)
```

**Result:**
- ✅ Similar drugs now include SMILES structures
- ✅ Includes targets (enzymes/proteins) for better context
- ✅ Mock data also includes SMILES for testing

### 2. Agent Engine Prompt Update (`src/agent_engine.py`)

#### Added Drug SMILES Parameter
```python
def run_simulation(drug_name: str, similar_drugs: List[str], patient_profile: str, drug_smiles: str = None) -> str:
```

#### Enhanced Prompt Template

**New Input Section:**
```
INPUT DATA:
1. NEW DRUG: {drug_name}
   SMILES Structure: {drug_smiles}
   (Use the SMILES structure to understand the molecular structure and compare with similar drugs)

2. SIMILAR KNOWN DRUGS (with structures):
   {similar_drugs}
   
   IMPORTANT: Each similar drug entry includes:
   - Drug Name
   - SMILES structure (molecular formula)
   - Known Side Effects
   - Known Targets (enzymes/proteins)
   
   Use the SMILES structures to:
   - Compare molecular similarity between the new drug and similar drugs
   - Identify shared functional groups that might indicate CYP enzyme metabolism
   - Recognize structural patterns that correlate with known CYP substrates
   - Infer which CYP enzyme(s) likely metabolize the new drug based on structural similarity
```

#### Enhanced Reasoning Steps

**New Step 1: STRUCTURAL ANALYSIS**
```
1. STRUCTURAL ANALYSIS:
   - Compare the SMILES structure of the new drug with similar drugs' SMILES
   - Identify shared functional groups, ring systems, or structural motifs
   - Look for patterns that indicate CYP enzyme metabolism:
     * Aromatic rings + specific substituents → CYP2D6 substrates
     * Thiophene/benzimidazole rings → CYP2C19 substrates
     * Coumarin-like structures → CYP2C9 substrates (warfarin-like)
```

**Updated Step 2: ENZYME IDENTIFICATION**
```
2. ENZYME IDENTIFICATION:
   - Use structural similarity to similar drugs to infer CYP enzyme targets
   - Check similar drugs' known targets/metabolism pathways
   - If structures are very similar to a known CYP substrate, infer the same enzyme pathway
```

### 3. Main Script Update (`main.py`)

**Before:**
```python
result = run_simulation(user_drug_name, similar_drugs, patient_profile)
```

**After:**
```python
result = run_simulation(user_drug_name, similar_drugs, patient_profile, drug_smiles=user_drug_smiles)
```

---

## 📊 Expected Impact

### Before Update
- ❌ LLM only saw drug names: "Paracetamol", "Ibuprofen"
- ❌ No structural information for comparison
- ❌ Limited ability to infer CYP enzyme pathways from structure

### After Update
- ✅ LLM sees full structures: "Paracetamol | SMILES: CC(=O)Nc1ccc(O)cc1 | ..."
- ✅ Can compare molecular structures directly
- ✅ Can identify shared functional groups
- ✅ Better inference of CYP enzyme pathways based on structural similarity

---

## 🧪 Example Output Format

### Similar Drugs Format
```
Paracetamol | SMILES: CC(=O)Nc1ccc(O)cc1 | Side Effects: Liver toxicity (rare) | Targets: COX-1, COX-2
Ibuprofen | SMILES: CC(C)CC1=CC=C(C=C1)C(C)C(=O)O | Side Effects: GI irritation | Targets: COX-1, COX-2
Aspirin | SMILES: CC(=O)OC1=CC=CC=C1C(=O)O | Side Effects: GI bleeding | Targets: COX-1, COX-2
```

### LLM Prompt Includes
```
INPUT DATA:
1. NEW DRUG: New-Analgesic-123
   SMILES Structure: CC(=O)Nc1ccc(OC)cc1

2. SIMILAR KNOWN DRUGS (with structures):
   Paracetamol | SMILES: CC(=O)Nc1ccc(O)cc1 | Side Effects: Liver toxicity (rare) | Targets: COX-1, COX-2
   Ibuprofen | SMILES: CC(C)CC1=CC=C(C=C1)C(C)C(=O)O | Side Effects: GI irritation | Targets: COX-1, COX-2
   ...
```

---

## 🔍 How LLM Uses Structures

The enhanced prompt instructs the LLM to:

1. **Compare Structures:**
   - Identify shared functional groups (e.g., aromatic rings, hydroxyl groups)
   - Recognize structural motifs (e.g., coumarin-like, benzimidazole-like)

2. **Infer CYP Pathways:**
   - If new drug has similar structure to warfarin (coumarin) → likely CYP2C9 substrate
   - If similar to clopidogrel (thiophene) → likely CYP2C19 substrate
   - If similar to codeine (aromatic + basic N) → likely CYP2D6 substrate

3. **Better Risk Assessment:**
   - Structural similarity to high-risk drugs → apply similar risk level
   - Shared functional groups → infer similar metabolism pathways

---

## ✅ Backward Compatibility

- ✅ `drug_smiles` parameter is optional (defaults to `None`)
- ✅ Existing code that doesn't pass SMILES still works
- ✅ Prompt handles missing SMILES gracefully ("Not provided")

---

## 📝 Files Modified

1. **`src/vector_search.py`**
   - Updated `find_similar_drugs()` to include SMILES and targets in output
   - Updated mock data to include SMILES

2. **`src/agent_engine.py`**
   - Added `drug_smiles` parameter to `run_simulation()`
   - Enhanced prompt template with structural comparison instructions
   - Added STRUCTURAL ANALYSIS reasoning step

3. **`main.py`**
   - Updated `run_simulation()` call to pass `drug_smiles`

---

## ✅ Status

**Implementation:** ✅ Complete  
**Testing:** Ready for testing  
**Documentation:** This file

---

*Update Date: Based on user action item*
