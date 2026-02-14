"""
Agent Engine Module

Handles LLM-based pharmacogenomics simulation using LangChain.
This is the "Brain" that simulates the patient.
"""

import logging
from typing import List

from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.config import config
from src.exceptions import ConfigurationError, LLMError

# Set up logging
logger = logging.getLogger(__name__)

# Lazy initialization - will be created when needed
_llm = None


def _get_llm():
    """Lazy initialization of the LLM to ensure API key is loaded."""
    global _llm
    if _llm is None:
        if not config.GOOGLE_API_KEY:
            raise ConfigurationError(
                "GOOGLE_API_KEY or GEMINI_API_KEY not set. "
                "Please add it to your environment or .env file.",
                missing_keys=["GOOGLE_API_KEY", "GEMINI_API_KEY"],
            )

        logger.info(
            f"Initializing LLM: model={config.GEMINI_MODEL}, "
            f"temperature={config.GEMINI_TEMPERATURE}"
        )

        _llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            temperature=config.GEMINI_TEMPERATURE,
            google_api_key=config.GOOGLE_API_KEY,
        )
    return _llm


def run_simulation(
    drug_name: str,
    similar_drugs: List[str],
    patient_profile: str,
    drug_smiles: str = None,
) -> str:
    """
    Run pharmacogenomics simulation using LLM to predict drug effects.

    Args:
        drug_name: Name of the drug being tested
        similar_drugs: List of formatted drug strings from vector search
        patient_profile: String containing patient information (ID, Age, Genetics, Conditions)

    Returns:
        String containing the AI-generated pharmacogenomics prediction

    Raises:
        ValueError: If Gemini API key is not set
    """
    template = """
    ROLE: You are an advanced Pharmacogenomics AI following CPIC (Clinical Pharmacogenetics Implementation Consortium) guidelines.

    TASK: Predict the physiological reaction of a specific patient to a new drug.

    CONTEXT:
    You have access to the patient's genetic profile for the "Big 3" Metabolic Enzymes:
    1. CYP2D6 (Chromosome 22) - Metabolizes ~25% of drugs: Antidepressants, Antipsychotics, Codeine, Tramadol, Metoprolol
    2. CYP2C19 (Chromosome 10) - Metabolizes Clopidogrel (Plavix), Omeprazole, and other proton pump inhibitors
    3. CYP2C9 (Chromosome 10) - Metabolizes Warfarin (blood thinner), Ibuprofen, Phenytoin, and NSAIDs
    4. UGT1A1 (Chromosome 2) - Phase II enzyme, metabolizes Irinotecan (chemotherapy), Atazanavir
    5. SLCO1B1 (Chromosome 12) - Transporter (OATP1B1), affects Statins (Simvastatin) uptake

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

    3. PATIENT PROFILE: {patient_profile}

    RISK LEVEL DEFINITIONS (CRITICAL - USE THESE EXACTLY):
    - HIGH RISK: Severe consequences requiring alternative drug or contraindication
      * Complete lack of efficacy (e.g., codeine → no conversion to active morphine via CYP2D6)
      * Significant toxicity risk (e.g., metoprolol → bradycardia from accumulation via CYP2D6)
      * Warfarin bleeding risk (CYP2C9 poor metabolizer)
      * CPIC recommendation: "Alternative drug recommended" or "Contraindicated"

    - MEDIUM RISK: Moderate consequences manageable with dose adjustment or monitoring
      * Reduced efficacy but alternative dosing available (e.g., tramadol → dose adjustment via CYP2D6)
      * Moderate accumulation manageable with monitoring
      * Clopidogrel reduced activation (CYP2C19 poor metabolizer) - alternative antiplatelet available
      * CPIC recommendation: "Consider dose adjustment" or "Monitor closely"

    - LOW RISK: Minimal impact, standard dosing appropriate
      * No CYP enzyme dependence (e.g., paracetamol metabolized by CYP1A2/CYP2E1, not Big 3)
      * Minimal genetic impact on drug response
      * CPIC recommendation: "No dose adjustment needed"

    CPIC GUIDELINES REFERENCE (for known substrates):
    CYP2D6:
    - Codeine (poor metabolizer): HIGH RISK - Alternative analgesic recommended (no activation to morphine)
    - Tramadol (poor metabolizer): MEDIUM RISK - Consider dose adjustment or alternative (reduced activation)
    - Metoprolol (poor metabolizer): HIGH RISK - Reduce dose by 50% (toxicity from accumulation)

    CYP2C19:
    - Clopidogrel (poor metabolizer): MEDIUM RISK - Reduced activation, alternative antiplatelet recommended
    - Omeprazole (poor metabolizer): MEDIUM RISK - Reduced efficacy, dose adjustment or alternative PPI

    CYP2C9:
    - Warfarin (poor metabolizer): HIGH RISK - Increased bleeding risk, reduce dose significantly
    - Ibuprofen (poor metabolizer): MEDIUM RISK - Reduced clearance, monitor for GI effects

    REASONING STEPS (follow this logic):
    1. STRUCTURAL ANALYSIS:
       - Compare the SMILES structure of the new drug with similar drugs' SMILES
       - Identify shared functional groups, ring systems, or structural motifs
       - Look for patterns that indicate CYP enzyme metabolism:
         * Aromatic rings + specific substituents → CYP2D6 substrates
         * Thiophene/benzimidazole rings → CYP2C19 substrates
         * Coumarin-like structures → CYP2C9 substrates (warfarin-like)

    2. ENZYME IDENTIFICATION:
       - Use structural similarity to similar drugs to infer CYP enzyme targets
       - Check similar drugs' known targets/metabolism pathways
       - CYP2D6: Antidepressants, opioids, beta-blockers (often have aromatic + basic nitrogen)
       - CYP2C19: Antiplatelets (clopidogrel), PPIs (omeprazole) (often have benzimidazole/thiophene)
       - CYP2C9: Anticoagulants (warfarin), NSAIDs (ibuprofen), anticonvulsants (phenytoin) (often have coumarin/aromatic acid)
       - If structures are very similar to a known CYP substrate, infer the same enzyme pathway

    3. PATIENT GENETIC STATUS:
       - Check patient's metabolizer status for the relevant enzyme(s) from patient profile
       - Identify if patient is poor/intermediate/ultra-rapid metabolizer for the inferred enzyme

    4. IMPACT ASSESSMENT:
       - Activation-dependent (prodrug): Will patient get active metabolite? (Complete failure = HIGH, Reduced = MEDIUM)
       - Clearance-dependent (direct substrate): Will drug accumulate? (Severe accumulation = HIGH, Moderate = MEDIUM)
       - Consider structural similarity: If very similar to a high-risk drug, apply similar risk level

    5. RISK CLASSIFICATION:
       - Consider severity: Can this be managed with dose adjustment? (Yes = MEDIUM, No = HIGH)
       - Classify risk level based on CPIC guidelines, structural similarity, and severity assessment

    OUTPUT FORMAT (MUST FOLLOW EXACTLY):
    - RISK LEVEL: [Low/Medium/High] (choose ONE based on definitions above)
    - PREDICTED REACTION: [Description]
    - BIOLOGICAL MECHANISM: [Which enzyme(s) involved and why it happens]

    IMPORTANT:
    - Always start your response with "RISK LEVEL: " followed by exactly one of: Low, Medium, or High
    - Use the risk level definitions above - do not overestimate risk
    - Identify which CYP enzyme(s) are relevant (CYP2D6, CYP2C19, or CYP2C9)
    - For tramadol-like drugs (reduced activation but manageable), use MEDIUM, not HIGH
    - For codeine-like drugs (complete lack of activation), use HIGH
    - For warfarin-like drugs (severe bleeding risk), use HIGH
    """

    prompt = PromptTemplate(
        input_variables=[
            "drug_name",
            "drug_smiles",
            "similar_drugs",
            "patient_profile",
        ],
        template=template,
    )

    # Get LLM instance (lazy initialization)
    llm = _get_llm()
    chain = prompt | llm

    # Prepare inputs
    inputs = {
        "drug_name": drug_name,
        "drug_smiles": drug_smiles or "Not provided",
        "similar_drugs": "\n".join(similar_drugs),
        "patient_profile": patient_profile,
    }

    logger.info(f"Running simulation for drug: {drug_name}")
    logger.debug(f"Similar drugs: {len(similar_drugs)}")

    # Invoke with retry logic
    try:
        response = _invoke_llm_with_retry(chain, inputs)
        result = response.content if hasattr(response, "content") else str(response)
        logger.info("Simulation completed successfully")
        return result
    except Exception as e:
        logger.error(f"LLM simulation failed: {e}", exc_info=True)
        raise LLMError(
            f"Failed to run pharmacogenomics simulation: {str(e)}",
            model=config.GEMINI_MODEL,
        ) from e


from src.resilience import CircuitBreakerOpenError, circuit_breaker


@circuit_breaker(failure_threshold=3, reset_timeout=60, name="Gemini-LLM")
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((Exception,)),
    reraise=True,
)
def _invoke_llm_with_retry(chain, inputs):
    """
    Invoke LLM chain with retry logic and circuit breaker.
    """
    try:
        return chain.invoke(inputs)
    except Exception as e:
        raise


from typing import Optional


def extract_risk_level(result: str) -> Optional[str]:
    """
    Extract risk level from simulation result

    Args:
        result: AI-generated simulation result

    Returns:
        Risk level string (Low/Medium/High) or None if not found
    """
    lines = result.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("RISK LEVEL:") or line.startswith("- RISK LEVEL:"):
            # Extract the risk level value
            parts = line.split(":")
            if len(parts) >= 2:
                risk = parts[1].strip()
                # Clean up any markdown or extra formatting
                risk = risk.replace("**", "").replace("*", "").strip()
                # Return first word (Low, Medium, or High)
                return risk.split()[0] if risk else None
    return None
