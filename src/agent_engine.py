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
        _llm = ChatGoogleGenerativeAI(model=_gemini_model, temperature=0.2)
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
    ROLE: You are an advanced Pharmacogenomics AI.
    
    TASK: Predict the physiological reaction of a specific patient to a new drug.
    
    INPUT DATA:
    1. NEW DRUG: {drug_name}
    2. SIMILAR KNOWN DRUGS: {similar_drugs}
    3. PATIENT PROFILE: {patient_profile}
    
    LOGIC:
    - Compare the new drug to the known drugs.
    - Check if the patient's genetic markers (e.g., CYP2D6 status) conflict with the drug's metabolism.
    - Predict specific adverse outcomes.
    
    OUTPUT FORMAT:
    - RISK LEVEL: [Low/Medium/High]
    - PREDICTED REACTION: [Description]
    - BIOLOGICAL MECHANISM: [Why it happens]
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
