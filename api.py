#!/usr/bin/env python3
"""
Anukriti AI Pharmacogenomics API
FastAPI wrapper for SynthaTrial backend

Exposes REST API endpoints for pharmacogenomics risk simulation.
"""

import logging
import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.agent_engine import extract_risk_level, run_simulation
from src.config import config
from src.exceptions import ConfigurationError, LLMError
from src.input_processor import get_drug_fingerprint
from src.logging_config import setup_logging
from src.vcf_processor import discover_vcf_paths
from src.vector_search import find_similar_drugs

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Anukriti AI Pharmacogenomics Engine",
    description="AI-powered pharmacogenomics risk simulation using CPIC guidelines",
    version="0.2.0",
)

# Enable CORS for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class AnalyzeRequest(BaseModel):
    """Request model for drug analysis"""

    drug_name: str = Field(..., description="Name of the drug to analyze")
    patient_profile: str = Field(
        ..., description="Patient profile including genetics and conditions"
    )
    drug_smiles: Optional[str] = Field(
        None, description="SMILES string of the drug (optional)"
    )
    similar_drugs: Optional[List[str]] = Field(
        None, description="Pre-computed similar drugs (optional)"
    )


class AnalyzeResponse(BaseModel):
    """Response model for drug analysis"""

    result: str = Field(..., description="AI-generated pharmacogenomics prediction")
    risk_level: Optional[str] = Field(
        None, description="Extracted risk level (Low/Medium/High)"
    )
    drug_name: str = Field(..., description="Name of the analyzed drug")
    status: str = Field(default="success", description="Request status")
    # RAG context (transparent reasoning)
    similar_drugs_used: Optional[List[str]] = Field(
        None, description="Retrieved similar drugs used for prediction"
    )
    genetics_summary: Optional[str] = Field(
        None,
        description="Genetic variants / metabolizer status used (e.g. CYP2D6 poor metabolizer)",
    )
    context_sources: Optional[str] = Field(
        None,
        description="Source of similar drugs (e.g. ChEMBL via Pinecone, Mock data)",
    )


class HealthResponse(BaseModel):
    """Response model for health check"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    model: str = Field(..., description="LLM model being used")


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns service status and configuration
    """
    return HealthResponse(
        status="Anukriti AI Engine Online",
        version="0.2.0",
        model=config.GEMINI_MODEL,
    )


@app.get("/demo")
async def demo_examples():
    """
    Get demo examples for testing and competition presentation
    Returns pre-configured examples that showcase different risk levels
    """
    return {
        "examples": [
            {
                "drug_name": "Warfarin",
                "patient_profile": "ID: DEMO-001\nAge: 45\nGenetics: CYP2C9 Poor Metabolizer\nConditions: Atrial Fibrillation\nLifestyle: Non-smoker",
                "expected_risk": "High",
                "description": "Anticoagulant with genetic contraindication",
            },
            {
                "drug_name": "Codeine",
                "patient_profile": "ID: DEMO-002\nAge: 32\nGenetics: CYP2D6 Poor Metabolizer\nConditions: Chronic Pain\nLifestyle: Non-smoker",
                "expected_risk": "High",
                "description": "Opioid prodrug requiring CYP2D6 activation",
            },
            {
                "drug_name": "Clopidogrel",
                "patient_profile": "ID: DEMO-003\nAge: 58\nGenetics: CYP2C19 Poor Metabolizer\nConditions: Coronary Artery Disease\nLifestyle: Former smoker",
                "expected_risk": "High",
                "description": "Antiplatelet requiring CYP2C19 activation",
            },
            {
                "drug_name": "Ibuprofen",
                "patient_profile": "ID: DEMO-004\nAge: 28\nGenetics: CYP2C9 Normal Metabolizer\nConditions: Headache\nLifestyle: Active, non-smoker",
                "expected_risk": "Low",
                "description": "NSAID with normal metabolism",
            },
            {
                "drug_name": "Metoprolol",
                "patient_profile": "ID: DEMO-005\nAge: 52\nGenetics: CYP2D6 Extensive Metabolizer\nConditions: Hypertension\nLifestyle: Regular exercise",
                "expected_risk": "Low",
                "description": "Beta-blocker with normal CYP2D6 function",
            },
        ],
        "competition_info": {
            "platform": "Anukriti AI Pharmacogenomics Engine",
            "version": "0.2.0",
            "features": [
                "Real-time AI risk assessment",
                "CPIC guideline compliance",
                "Multi-enzyme genetic analysis",
                "Cloud-agnostic deployment",
                "Enterprise-ready API",
            ],
        },
    }


@app.get("/health")
async def detailed_health():
    """
    Detailed health check for monitoring and competition demo
    """
    try:
        # Test configuration
        is_valid, missing_keys = config.validate_required()

        return {
            "status": "healthy",
            "timestamp": "2026-02-14T00:00:00Z",
            "version": "0.2.0",
            "environment": "competition",
            "services": {
                "api": "online",
                "llm": "connected" if is_valid else "configuration_error",
                "vector_db": "mock_mode"
                if not config.PINECONE_API_KEY
                else "connected",
            },
            "configuration": {
                "model": config.GEMINI_MODEL,
                "temperature": config.GEMINI_TEMPERATURE,
                "missing_keys": missing_keys if not is_valid else [],
            },
            "endpoints": [
                {"path": "/", "method": "GET", "description": "Basic health check"},
                {
                    "path": "/data-status",
                    "method": "GET",
                    "description": "Pinecone vs mock, VCF chromosomes, ChEMBL presence",
                },
                {
                    "path": "/analyze",
                    "method": "POST",
                    "description": "Drug risk analysis",
                },
                {"path": "/demo", "method": "GET", "description": "Demo examples"},
                {"path": "/docs", "method": "GET", "description": "API documentation"},
            ],
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "timestamp": "2026-02-14T00:00:00Z"}


@app.get("/data-status")
async def data_status():
    """
    Report whether the app is using real data (Pinecone/ChEMBL, VCF) or mock.

    - vector_db: "pinecone" when PINECONE_API_KEY is set and used; "mock" otherwise.
    - vcf_chromosomes: chromosomes found under data/genomes (used for VCF-based profiles).
    - chembl_db_present: True if ChEMBL SQLite exists (used to populate Pinecone; runtime search is via Pinecone).
    """
    app_root = os.path.dirname(os.path.abspath(__file__))
    genomes_dir = os.path.join(app_root, "data", "genomes")
    chembl_paths = [
        os.path.join(app_root, "data", "chembl", "chembl_34_sqlite", "chembl_34.db"),
        os.path.join(app_root, "data", "chembl", "chembl_34.db"),
    ]
    vcf_found = discover_vcf_paths(genomes_dir)
    chembl_present = any(os.path.isfile(p) for p in chembl_paths)
    return {
        "vector_db": "pinecone" if config.PINECONE_API_KEY else "mock",
        "vcf_chromosomes": list(vcf_found.keys()) if vcf_found else [],
        "vcf_paths": vcf_found,
        "chembl_db_present": chembl_present,
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_drug(request: AnalyzeRequest):
    """
    Analyze drug-patient interaction and predict pharmacogenomics risk

    This endpoint:
    1. Processes the drug SMILES (if provided) to generate molecular fingerprint
    2. Finds similar drugs using vector similarity search (if not provided)
    3. Runs AI simulation using patient profile and drug information
    4. Returns risk assessment following CPIC guidelines

    Args:
        request: AnalyzeRequest containing drug info and patient profile

    Returns:
        AnalyzeResponse with AI-generated risk prediction

    Raises:
        HTTPException: If configuration is invalid or simulation fails
    """
    logger.info(f"Received analysis request for drug: {request.drug_name}")

    try:
        # Validate configuration
        is_valid, missing_keys = config.validate_required()
        if not is_valid:
            logger.error(f"Configuration error: Missing keys {missing_keys}")
            raise HTTPException(
                status_code=500,
                detail=f"Server configuration error: Missing {', '.join(missing_keys)}. "
                "Please contact administrator.",
            )

        # Get similar drugs if not provided
        similar_drugs = request.similar_drugs
        used_pinecone = False
        if not similar_drugs:
            logger.info("Computing similar drugs via vector search")
            try:
                drug_smiles = request.drug_smiles or "CC(=O)Nc1ccc(O)cc1"
                vector = get_drug_fingerprint(drug_smiles)
                similar_drugs = find_similar_drugs(vector)
                used_pinecone = bool(config.PINECONE_API_KEY)
                logger.info(f"Found {len(similar_drugs)} similar drugs")
            except Exception as e:
                logger.warning(f"Vector search failed: {e}, using empty list")
                similar_drugs = []
        else:
            used_pinecone = bool(config.PINECONE_API_KEY)

        # Extract genetics summary from patient profile
        genetics_summary = None
        for line in (request.patient_profile or "").splitlines():
            line = line.strip()
            if line.lower().startswith("genetics:"):
                genetics_summary = line.replace("Genetics:", "").strip()
                break

        # Run AI simulation
        logger.info("Running pharmacogenomics simulation")
        result = run_simulation(
            drug_name=request.drug_name,
            similar_drugs=similar_drugs,
            patient_profile=request.patient_profile,
            drug_smiles=request.drug_smiles,
        )

        risk_level = extract_risk_level(result)
        context_sources = (
            "ChEMBL (via Pinecone)" if used_pinecone else "Mock data (no Pinecone key)"
        )
        similar_names = [
            s.split("|")[0].strip() if "|" in s else s for s in similar_drugs
        ]

        logger.info(f"Simulation completed successfully. Risk level: {risk_level}")

        return AnalyzeResponse(
            result=result,
            risk_level=risk_level,
            drug_name=request.drug_name,
            status="success",
            similar_drugs_used=similar_names or similar_drugs,
            genetics_summary=genetics_summary,
            context_sources=context_sources,
        )

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Server configuration error: {str(e)}",
        )

    except LLMError as e:
        logger.error(f"LLM error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"AI simulation service unavailable: {str(e)}",
        )

    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )


# Example usage for testing
class BatchAnalyzeRequest(BaseModel):
    """Request model for batch analysis"""

    requests: List[AnalyzeRequest] = Field(..., description="List of analysis requests")


@app.post("/analyze/batch", response_model=List[AnalyzeResponse])
async def analyze_drug_batch(batch_request: BatchAnalyzeRequest):
    """
    Batch analysis of multiple drug-patient pairs.
    Run simulations in parallel (limited by concurrency).
    """
    logger.info(
        f"Received batch analysis request with {len(batch_request.requests)} items"
    )
    responses = []

    # Process sequentially for MVP
    for request in batch_request.requests:
        try:
            # 1. Get similar drugs
            similar_drugs = request.similar_drugs
            if not similar_drugs:
                try:
                    drug_smiles = request.drug_smiles or "CC(=O)Nc1ccc(O)cc1"
                    vector = get_drug_fingerprint(drug_smiles)
                    similar_drugs = find_similar_drugs(vector)
                except Exception as e:
                    logger.warning(f"Vector search failed for {request.drug_name}: {e}")
                    similar_drugs = []

            # 2. Run simulation
            result = run_simulation(
                drug_name=request.drug_name,
                similar_drugs=similar_drugs,
                patient_profile=request.patient_profile,
                drug_smiles=request.drug_smiles,
            )

            risk_level = extract_risk_level(result)

            responses.append(
                AnalyzeResponse(
                    result=result,
                    risk_level=risk_level,
                    drug_name=request.drug_name,
                    status="success",
                )
            )

        except Exception as e:
            logger.error(f"Error processing batch item {request.drug_name}: {e}")
            responses.append(
                AnalyzeResponse(
                    result=f"Error: {str(e)}",
                    risk_level="Unknown",
                    drug_name=request.drug_name,
                    status="error",
                )
            )

    return responses


if __name__ == "__main__":
    import uvicorn

    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))

    logger.info(f"Starting Anukriti AI API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)  # nosec B104 - bind all for container
