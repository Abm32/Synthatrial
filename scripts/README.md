# Scripts Directory

This directory contains utility scripts for setting up and managing SynthaTrial.

## Available Scripts

### Setup Scripts

- **`setup_pinecone_index.py`**
  - Creates and configures Pinecone index
  - Verifies index settings (2048 dimensions, cosine metric)
  - Usage: `python scripts/setup_pinecone_index.py`

### Data Ingestion Scripts

- **`ingest_chembl_to_pinecone.py`**
  - Extracts drugs from ChEMBL database
  - Generates molecular fingerprints
  - Ingests into Pinecone vector database
  - Usage: `python scripts/ingest_chembl_to_pinecone.py`
  - Configuration: Set `CHEMBL_LIMIT` environment variable to control number of drugs

### Utility Scripts

- **`list_models.py`** / **`list_models_v2.py`**
  - Lists available LLM models
  - Useful for checking API access
  - Usage: `python scripts/list_models.py`

## Running Scripts

All scripts should be run from the project root directory:

```bash
# From project root
python scripts/setup_pinecone_index.py
python scripts/ingest_chembl_to_pinecone.py
```

## Prerequisites

- Conda environment activated: `conda activate synthatrial`
- API keys configured in `.env` file
- Required data files downloaded (see main README)

## Notes

- Scripts are executable (`chmod +x`) but can also be run with `python`
- Check individual script help: `python scripts/script_name.py --help` (if supported)
- See main README for detailed setup instructions
