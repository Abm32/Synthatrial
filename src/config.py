"""
Configuration Management Module

Centralized configuration for SynthaTrial with validation and defaults.
"""

import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Centralized configuration class for SynthaTrial.

    All configuration values are loaded from environment variables with
    sensible defaults. Required values are validated on access.
    """

    # API Keys
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY") or os.getenv(
        "GEMINI_API_KEY"
    )
    PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX: str = os.getenv("PINECONE_INDEX", "drug-index")

    # LLM Configuration
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
    GEMINI_MAX_RETRIES: int = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
    GEMINI_TIMEOUT: int = int(os.getenv("GEMINI_TIMEOUT", "60"))

    # Pinecone Configuration
    PINECONE_MAX_RETRIES: int = int(os.getenv("PINECONE_MAX_RETRIES", "3"))
    PINECONE_TIMEOUT: int = int(os.getenv("PINECONE_TIMEOUT", "30"))
    PINECONE_TOP_K: int = int(os.getenv("PINECONE_TOP_K", "3"))

    # Vector Search Configuration
    FINGERPRINT_BITS: int = 2048
    FINGERPRINT_RADIUS: int = 2

    # VCF Configuration
    VCF_CHR22_PATH: Optional[str] = os.getenv("VCF_CHR22_PATH")
    VCF_CHR10_PATH: Optional[str] = os.getenv("VCF_CHR10_PATH")
    VCF_BATCH_SIZE: int = int(os.getenv("VCF_BATCH_SIZE", "1000"))

    # ChEMBL Configuration
    CHEMBL_DB_PATH: Optional[str] = os.getenv("CHEMBL_DB_PATH")
    CHEMBL_LIMIT: int = int(os.getenv("CHEMBL_LIMIT", "1000"))

    # Caching Configuration
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()

    @classmethod
    def validate_required(cls) -> tuple[bool, list[str]]:
        """
        Validate that required configuration values are set.
        In PRODUCTION, checks are stricter.

        Returns:
            Tuple of (is_valid, list_of_missing_keys)
        """
        missing = []

        # Google API key is required for LLM functionality
        if not cls.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY or GEMINI_API_KEY")

        # In PRODUCTION, Pinecone is required (no mocks allowed)
        if cls.ENVIRONMENT == "production":
            if not cls.PINECONE_API_KEY:
                missing.append("PINECONE_API_KEY (Required in PRODUCTION)")
        else:
            # In Development, it's optional (mock fallback)
            pass

        return len(missing) == 0, missing

    @classmethod
    def is_production(cls) -> bool:
        return cls.ENVIRONMENT == "production"

    @classmethod
    def get_summary(cls) -> dict:
        """
        Get a summary of current configuration (without sensitive values).

        Returns:
            Dictionary with configuration summary
        """
        return {
            "environment": cls.ENVIRONMENT,
            "gemini_model": cls.GEMINI_MODEL,
            "gemini_temperature": cls.GEMINI_TEMPERATURE,
            "pinecone_index": cls.PINECONE_INDEX,
            "fingerprint_bits": cls.FINGERPRINT_BITS,
            "caching_enabled": cls.ENABLE_CACHING,
            "log_level": cls.LOG_LEVEL,
            "has_google_api_key": bool(cls.GOOGLE_API_KEY),
            "has_pinecone_api_key": bool(cls.PINECONE_API_KEY),
        }


# Create a singleton instance
config = Config()
