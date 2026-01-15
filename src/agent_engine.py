"""
Agent Engine Module

Handles LLM-based pharmacogenomics simulation using LangChain.
This is the "Brain" that simulates the patient.
"""

from typing import List
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Load environment variables from .env file
load_dotenv()

# Lazy initialization - will be created when needed
_llm = None
# Default to gemini-2.5-flash (newest, fastest model)
# Other available models: gemini-2.5-pro, gemini-2.0-flash, gemini-2.0-flash-exp
# User can override with GEMINI_MODEL env var
_gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _get_llm():
    """Lazy initialization of the LLM to ensure API key is loaded."""
    global _llm
    if _llm is None:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY or GEMINI_API_KEY not set. "
                "Please add it to your environment or .env file."
            )
        # Lower temperature for more consistent, deterministic outputs
        _llm = ChatGoogleGenerativeAI(model=_gemini_model, temperature=0.1)
    return _llm


def run_simulation(drug_name: str, similar_drugs: List[str], patient_profile: str) -> str:
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
    
    INPUT DATA:
    1. NEW DRUG: {drug_name}
    2. SIMILAR KNOWN DRUGS: {similar_drugs}
    3. PATIENT PROFILE: {patient_profile}
    
    RISK LEVEL DEFINITIONS (CRITICAL - USE THESE EXACTLY):
    - HIGH RISK: Severe consequences requiring alternative drug or contraindication
      * Complete lack of efficacy (e.g., codeine → no conversion to active morphine)
      * Significant toxicity risk (e.g., metoprolol → bradycardia from accumulation)
      * CPIC recommendation: "Alternative drug recommended" or "Contraindicated"
    
    - MEDIUM RISK: Moderate consequences manageable with dose adjustment or monitoring
      * Reduced efficacy but alternative dosing available (e.g., tramadol → dose adjustment)
      * Moderate accumulation manageable with monitoring
      * CPIC recommendation: "Consider dose adjustment" or "Monitor closely"
    
    - LOW RISK: Minimal impact, standard dosing appropriate
      * No CYP2D6 dependence (e.g., paracetamol metabolized by CYP1A2/CYP2E1)
      * Minimal genetic impact on drug response
      * CPIC recommendation: "No dose adjustment needed"
    
    CPIC GUIDELINES REFERENCE (for known CYP2D6 substrates):
    - Codeine (poor metabolizer): HIGH RISK - Alternative analgesic recommended (no activation to morphine)
    - Tramadol (poor metabolizer): MEDIUM RISK - Consider dose adjustment or alternative (reduced activation)
    - Metoprolol (poor metabolizer): HIGH RISK - Reduce dose by 50% (toxicity from accumulation)
    
    REASONING STEPS (follow this logic):
    1. Identify if drug requires CYP2D6 for activation (prodrug) or clearance (direct substrate)
    2. Assess impact of poor metabolizer status:
       - Activation-dependent: Will patient get active metabolite? (Complete failure = HIGH, Reduced = MEDIUM)
       - Clearance-dependent: Will drug accumulate? (Severe accumulation = HIGH, Moderate = MEDIUM)
    3. Consider severity: Can this be managed with dose adjustment? (Yes = MEDIUM, No = HIGH)
    4. Classify risk level based on CPIC guidelines and severity assessment
    
    OUTPUT FORMAT (MUST FOLLOW EXACTLY):
    - RISK LEVEL: [Low/Medium/High] (choose ONE based on definitions above)
    - PREDICTED REACTION: [Description]
    - BIOLOGICAL MECHANISM: [Why it happens]
    
    IMPORTANT: 
    - Always start your response with "RISK LEVEL: " followed by exactly one of: Low, Medium, or High
    - Use the risk level definitions above - do not overestimate risk
    - For tramadol-like drugs (reduced activation but manageable), use MEDIUM, not HIGH
    - For codeine-like drugs (complete lack of activation), use HIGH
    """
    
    prompt = PromptTemplate(
        input_variables=["drug_name", "similar_drugs", "patient_profile"],
        template=template
    )
    
    # Get LLM instance (lazy initialization)
    llm = _get_llm()
    chain = prompt | llm
    response = chain.invoke({
        "drug_name": drug_name,
        "similar_drugs": "\n".join(similar_drugs),
        "patient_profile": patient_profile
    })
    
    # ChatGoogleGenerativeAI returns an object with .content in Generation
    return response.content if hasattr(response, "content") else str(response)
