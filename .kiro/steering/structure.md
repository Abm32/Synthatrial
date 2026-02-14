# Project Structure

## Directory Organization

```
SynthaTrial/
├── .env                       # Environment variables (create from .env.example)
├── .env.example              # Environment template with competition settings
├── render.yaml               # Render.com deployment configuration
├── vercel.json               # Vercel serverless deployment configuration
├── Procfile                  # Heroku deployment configuration
├── runtime.txt               # Python runtime specification
├── demo.html                 # Competition demo interface
├── COMPETITION_DEPLOYMENT.md # Competition deployment strategy guide
├── QUICK_DEPLOY.md          # 10-minute deployment guide
├── .dockerignore             # Docker ignore file
├── Dockerfile                # Multi-stage Docker build
├── docker-compose.yml        # Docker Compose configuration
├── docker-compose.dev.yml    # Development Docker Compose
├── docker-compose.prod.yml   # Production Docker Compose
├── docker-entrypoint.sh      # Docker entrypoint script
├── Makefile                  # Docker management commands
├── README.md                 # Main project documentation
├── HOW_TO_RUN.md             # Quick start guide with examples
├── requirements.txt          # Python dependencies
├── app.py                    # Streamlit web interface
├── main.py                   # CLI entry point
├── api.py                    # FastAPI REST API wrapper (NEW)
├── test_api.py               # API test suite (NEW)
├── API_README.md             # API documentation (NEW)
├── RENDER_DEPLOYMENT.md      # Render deployment guide (NEW)
├── DEPLOYMENT_CHECKLIST.md   # Deployment checklist (NEW)
├── QUICK_START_API.md        # Quick API deployment guide (NEW)
├── PROJECT_ANALYSIS.md       # Comprehensive project analysis and status (NEW)
├── NEXT_STEPS_ACTION_PLAN.md # Detailed action plan for deployment and scaling (NEW)
├── src/                      # Core application modules
│   ├── __init__.py
│   ├── input_processor.py    # SMILES → Molecular fingerprint conversion
│   ├── vector_search.py      # Pinecone similarity search
│   ├── agent_engine.py       # LLM-based pharmacogenomics simulation
│   ├── vcf_processor.py      # VCF file processing and genetic analysis
│   ├── variant_db.py         # Targeted variant lookup database (PharmVar Tier 1)
│   └── chembl_processor.py   # ChEMBL database integration
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── quick_test.py         # Quick integration tests
│   ├── validation_tests.py   # Comprehensive validation suite
│   ├── test_ssl_manager_properties.py          # SSL certificate property tests (NEW)
│   ├── test_ssl_integration.py                 # SSL integration tests (NEW)
│   ├── test_http_https_redirection_properties.py # HTTP to HTTPS redirection tests (NEW)
│   ├── test_data_initialization_properties.py  # Data initialization property tests (NEW)
│   ├── test_vcf_download_properties.py         # VCF download property tests (NEW)
│   ├── test_vcf_download_integration.py        # VCF download integration tests (NEW)
│   ├── test_chembl_setup_integration.py        # ChEMBL setup integration tests (NEW)
│   ├── test_dev_environment_properties.py      # Development environment property tests (NEW)
│   ├── test_containerized_testing_integration.py # Containerized testing integration (NEW)
│   ├── test_containerized_enhanced_features.py # Enhanced container features tests (NEW)
│   ├── test_security_scanner_properties.py     # Security scanning property tests (NEW)
│   ├── test_security_scanner_integration.py    # Security scanning integration tests (NEW)
│   ├── test_security_monitoring_properties.py  # Security monitoring property tests (NEW)
│   ├── test_cicd_pipeline_properties.py        # CI/CD pipeline property tests (NEW)
│   ├── test_deploy_to_registry_properties.py   # Registry deployment property tests (NEW)
│   ├── test_deploy_to_registry_integration.py  # Registry deployment integration tests (NEW)
│   ├── test_multi_arch_build_integration.py    # Multi-architecture build integration tests (NEW)
│   ├── test_complete_workflow_integration.py   # Complete workflow integration tests (NEW)
│   ├── test_github_actions_integration.py      # GitHub Actions integration tests (NEW)
│   ├── test_docker_environment_integration.py  # Docker environment integration tests (NEW)
│   └── test_integration_runner.py              # Comprehensive integration test runner (NEW)
├── scripts/                  # Utility and setup scripts
│   ├── README.md
│   ├── setup_pinecone_index.py      # Pinecone index creation
│   ├── ingest_chembl_to_pinecone.py # ChEMBL data ingestion
│   ├── list_models.py               # Available LLM models
│   ├── list_models_v2.py            # Enhanced model listing with API queries
│   ├── benchmark_performance.py     # Performance benchmarking (vector retrieval, LLM, end-to-end)
│   ├── test_chromosome10.py         # Big 3 enzymes integration testing
│   ├── check_vcf_integrity.py       # VCF file validation and integrity checking
│   ├── generate_validation_results.py # CPIC guideline validation and accuracy metrics
│   ├── ssl_manager.py               # SSL certificate management (NEW)
│   ├── generate_ssl_certs.sh        # SSL certificate generation script (NEW)
│   ├── data_initializer.py          # Data initialization orchestrator (NEW)
│   ├── download_vcf_files.py        # VCF file download automation (NEW)
│   ├── setup_chembl.py              # ChEMBL database setup automation (NEW)
│   ├── setup_dev_env.py             # Development environment setup (NEW)
│   ├── run_tests_in_container.py    # Containerized testing with reporting (NEW)
│   ├── security_scanner.py          # Container security scanning and vulnerability detection (NEW)
│   ├── production_monitor.py        # Production monitoring and resource tracking (NEW)
│   ├── backup_manager.py            # Automated backup and recovery procedures (NEW)
│   ├── multi_arch_build.py          # Multi-architecture build orchestration (NEW)
│   └── deploy_to_registry.py        # Container registry deployment automation (NEW)
├── notebooks/                # Jupyter notebooks for development and analysis
│   └── README.md            # Notebook usage guide and examples
├── data/                     # Data storage (create directories as needed)
│   ├── chembl/              # ChEMBL database files
│   │   └── chembl_34_sqlite/
│   │       └── chembl_34.db
│   └── genomes/             # VCF genomic data files
│       ├── ALL.chr22.*.vcf.gz  # Chromosome 22 (CYP2D6)
│       └── ALL.chr10.*.vcf.gz  # Chromosome 10 (CYP2C19, CYP2C9)
└── docs/                    # Comprehensive documentation
    ├── README.md            # Documentation index
    ├── setup.md             # Complete setup and installation guide
    ├── usage.md             # Usage examples and CLI reference
    ├── implementation.md    # Technical implementation details
    ├── troubleshooting.md   # Common issues and solutions
    ├── paper-review.md      # Research paper review and validation
    ├── docker.md            # Docker deployment guide
    ├── concepts/            # Conceptual explanations
    │   ├── pharmacogenomics.md
    │   ├── rag_explained.md
    │   ├── run_modes_explained.md  # Three run modes guide
    │   └── vector_databases.md
    └── paper/               # Research paper materials (remaining files)
        ├── FINAL_PAPER_REVIEW.md
        ├── FINAL_RESULTS_ANALYSIS.md
        └── VALIDATION_RESULTS.md
├── docker/                  # Docker configuration files
│   ├── Dockerfile.dev       # Development Dockerfile
│   ├── Dockerfile.dev-enhanced # Enhanced development Dockerfile (NEW)
│   ├── Dockerfile.prod      # Production Dockerfile
│   ├── nginx.conf           # Nginx reverse proxy configuration with SSL
│   ├── nginx-ssl-setup.sh   # SSL certificate setup script (NEW)
│   ├── nginx-entrypoint.sh  # Nginx Docker entrypoint with SSL (NEW)
│   ├── README.md            # Docker SSL configuration documentation (NEW)
│   └── ssl/                 # SSL certificate storage directory (NEW)
├── .pre-commit-config.yaml  # Pre-commit hooks configuration (NEW)
├── pyproject.toml           # Python project configuration with dev dependencies (NEW)
├── pytest.dev.ini           # Development pytest configuration (NEW)
├── docker-compose.dev-enhanced.yml # Enhanced development Docker Compose (NEW)
├── .github/                 # GitHub Actions and repository configuration (NEW)
│   ├── workflows/           # CI/CD workflow definitions
│   │   ├── docker-build.yml     # Main Docker build and test pipeline
│   │   ├── security-scan.yml    # Security scanning workflow
│   │   ├── pr-validation.yml    # Pull request validation
│   │   └── release.yml          # Release and deployment workflow
│   ├── ISSUE_TEMPLATE/      # Issue templates for bug reports, features, security
│   ├── pull_request_template.md # Pull request template
│   └── settings.yml         # Repository settings configuration
├── security_reports/        # Security scanning reports
├── monitoring_reports/      # Production monitoring reports
├── deployment_reports/      # Deployment automation reports
├── build_reports/          # Multi-architecture build reports
└── backups/                # Automated backup storage
```

## Module Responsibilities

### Core Modules (`src/`)

- **`input_processor.py`**: Validates SMILES strings and converts to 2048-bit Morgan fingerprints using RDKit
- **`vector_search.py`**: Handles Pinecone vector database operations with mock mode fallback and enhanced metadata (SMILES, targets, side effects)
- **`agent_engine.py`**: LLM integration using LangChain and Google Gemini for pharmacogenomics analysis with enhanced CPIC guideline-based prompting, structural analysis using SMILES strings, comprehensive drug interaction predictions, and support for multiple Gemini models (default: gemini-2.5-flash)
- **`vcf_processor.py`**: Processes VCF files to extract CYP enzyme variants and generate patient profiles. Supports multi-chromosome analysis (chromosomes 10 and 22) for Big 3 enzymes (CYP2D6, CYP2C19, CYP2C9) with targeted variant lookup and Activity Score method for CPIC-compliant metabolizer status inference
- **`variant_db.py`**: Targeted variant lookup database containing Tier 1 Clinical Variants (CPIC Level A) from PharmVar with activity scores and structural variant detection
- **`chembl_processor.py`**: Extracts drug information from ChEMBL SQLite database

### Entry Points

- **`app.py`**: Minimalistic Streamlit web interface with clean styling, streamlined user experience, curated drug database, real-time system monitoring, and competition-ready features. Features a simplified 3-tab interface (Analysis, Platform, About) with collapsed sidebar for cleaner main interface
- **`main.py`**: Command-line interface supporting both VCF and manual patient profiles. Supports single-chromosome (CYP2D6 only) and multi-chromosome (Big 3 enzymes) analysis with `--vcf-chr10` parameter for chromosome 10 data
- **`api.py`**: FastAPI REST API wrapper providing health check, analysis, and demo endpoints for programmatic access and cloud deployment

### Testing (`tests/`)

- **`quick_test.py`**: Fast integration tests for imports, file existence, and basic functionality
- **`validation_tests.py`**: Comprehensive test suite with known CYP2D6 substrates and expected outcomes
- **`test_api.py`**: Automated test suite for FastAPI endpoints with local and deployed testing capabilities (NEW)

### Scripts (`scripts/`)

- **`setup_pinecone_index.py`**: Creates Pinecone index with correct configuration (2048 dimensions, cosine metric)
- **`ingest_chembl_to_pinecone.py`**: Batch ingestion of ChEMBL drugs into Pinecone vector database
- **`list_models.py`**: Lists available Gemini models for testing different LLM versions
- **`list_models_v2.py`**: Enhanced model listing with direct API queries and detailed model information including capabilities and performance metrics
- **`test_chromosome10.py`**: Comprehensive testing suite for Big 3 enzymes integration and multi-chromosome functionality
- **`check_vcf_integrity.py`**: Validates VCF file integrity, checks for corruption, and verifies download completeness with detailed reporting
- **`generate_validation_results.py`**: Generates comprehensive validation results for research and paper documentation with CPIC compliance metrics
- **`benchmark_performance.py`**: Performance benchmarking for single and multi-chromosome processing with detailed timing analysis
- **`ssl_manager.py`**: SSL certificate management with generation, validation, expiration checking, and renewal (NEW)
- **`generate_ssl_certs.sh`**: Shell script for automated SSL certificate generation (NEW)
- **`data_initializer.py`**: Data initialization orchestrator for automated VCF and ChEMBL setup (NEW)
- **`download_vcf_files.py`**: Automated VCF file downloads with integrity validation (NEW)
- **`setup_chembl.py`**: Automated ChEMBL database download and setup (NEW)
- **`setup_dev_env.py`**: Development environment setup with pre-commit hooks and code quality tools (NEW)
- **`security_scanner.py`**: Container security scanning with vulnerability detection, compliance checking, and security reporting using Trivy/Grype integration (NEW)
- **`production_monitor.py`**: Production monitoring with resource tracking, health monitoring, alerting, and performance metrics collection (NEW)
- **`backup_manager.py`**: Automated backup and recovery procedures with data integrity validation and disaster recovery capabilities (NEW)
- **`multi_arch_build.py`**: Multi-architecture build orchestration for AMD64/ARM64 platforms with build optimization and artifact management (NEW)
- **`deploy_to_registry.py`**: Container registry deployment automation with environment-specific deployment, health checks, and rollback capabilities (NEW)

### Documentation (`docs/`)

- **`README.md`**: Documentation index and navigation guide
- **`setup.md`**: Complete setup and installation guide (consolidated from multiple setup files)
- **`usage.md`**: Usage examples and CLI reference with comprehensive test cases
- **`implementation.md`**: Technical implementation details and architecture (consolidated from multiple implementation files)
- **`troubleshooting.md`**: Common issues and solutions (consolidated from multiple troubleshooting files)
- **`paper-review.md`**: Research paper review and validation results (consolidated from multiple paper files)
- **`docker.md`**: Complete Docker deployment guide with development and production configurations
- **`docs/cicd.md`**: CI/CD pipeline documentation with GitHub Actions workflows and deployment automation (NEW)
- **`docs/deployment.md`**: Deployment automation guide with multi-environment deployment strategies (NEW)

### API and Deployment Documentation (Root Level)

- **`API_README.md`**: Complete FastAPI documentation with usage examples, endpoint specifications, and integration guides
- **`RENDER_DEPLOYMENT.md`**: Step-by-step guide for deploying FastAPI to Render cloud platform with configuration details
- **`COMPETITION_DEPLOYMENT.md`**: Competition deployment strategy with cloud platform options and demo setup
- **`QUICK_DEPLOY.md`**: 10-minute deployment guide for rapid competition setup
- **`DEPLOYMENT_CHECKLIST.md`**: Comprehensive deployment checklist with expected results and troubleshooting
- **`QUICK_START_API.md`**: Quick start guide for API deployment in 3 simple steps
- **`PROJECT_ANALYSIS.md`**: Comprehensive project analysis with architecture overview, current status, and technical metrics
- **`NEXT_STEPS_ACTION_PLAN.md`**: Detailed action plan for production deployment, user onboarding, and strategic roadmap

### Competition and Demo Files

- **`demo.html`**: Professional competition demo interface with gradient design and real-time API integration
- **`render.yaml`**: One-click Render.com deployment configuration
- **`vercel.json`**: Vercel serverless deployment configuration
- **`Procfile`**: Heroku deployment configuration
- **`runtime.txt`**: Python runtime specification for cloud platforms
- **`.env.example`**: Environment template with competition and cloud deployment settings

### Examples (`examples/`) (NEW)

- **`deployment_example.py`**: Deployment automation example scripts
- **`anukriti_frontend_example.html`**: Beautiful dark-themed frontend UI for FastAPI with neon cyan accents, pre-loaded drug examples, and color-coded risk levels

### Docker Configuration (`docker/`)

- **`Dockerfile.dev`**: Development-optimized Docker image with debugging tools, hot reloading, and Jupyter notebook support
- **`Dockerfile.dev-enhanced`**: Enhanced development Docker image with additional development tools, code quality tools, and testing frameworks (NEW)
- **`Dockerfile.prod`**: Production-optimized Docker image with minimal size, security hardening, and SSL support
- **`nginx.conf`**: Nginx reverse proxy configuration with SSL support, WebSocket handling, and security headers
- **`nginx-ssl-setup.sh`**: Automated SSL certificate detection and setup script (NEW)
- **`nginx-entrypoint.sh`**: Docker entrypoint script with SSL initialization (NEW)
- **`README.md`**: Docker SSL configuration documentation and usage guide (NEW)
- **`ssl/`**: SSL certificate storage directory for development and production certificates (NEW)

### GitHub Actions and CI/CD (`/.github/`)

- **`workflows/docker-build.yml`**: Main CI/CD pipeline with multi-architecture builds, testing, and deployment automation
- **`workflows/security-scan.yml`**: Security scanning workflow with vulnerability detection and compliance reporting
- **`workflows/pr-validation.yml`**: Pull request validation with automated testing and code quality checks
- **`workflows/release.yml`**: Release and deployment workflow with automated registry deployment
- **`ISSUE_TEMPLATE/`**: Issue templates for bug reports, feature requests, and security issues
- **`pull_request_template.md`**: Standardized pull request template with checklist and guidelines
- **`settings.yml`**: Repository settings configuration for automated repository management

### Security and Monitoring (`/security_reports/`, `/monitoring_reports/`)

- **Security Reports**: Automated vulnerability scanning reports, compliance assessments, and security metrics
- **Monitoring Reports**: Production monitoring data, performance metrics, resource utilization, and health status
- **Deployment Reports**: Deployment automation logs, success/failure tracking, and rollback procedures
- **Build Reports**: Multi-architecture build logs, platform-specific metrics, and build artifact tracking
- **Backup Reports**: Automated backup status, integrity validation, and recovery procedures

### Jupyter Notebooks (`notebooks/`)

- **Development and Analysis**: Interactive notebooks for data exploration, model testing, and performance analysis
- **Environment Integration**: Full access to SynthaTrial modules and dependencies within containerized Jupyter environment
- **Use Cases**: VCF data exploration, ChEMBL analysis, model validation, and performance benchmarking

### Integration Testing (`tests/test_*_integration.py`)

- **Complete Workflow Integration**: End-to-end testing of SSL + Data + Deployment workflows
- **GitHub Actions Integration**: CI/CD pipeline testing and workflow validation
- **Docker Environment Integration**: Container orchestration and environment consistency testing
- **Security and Monitoring Integration**: Security scanning and production monitoring validation
## File Naming Conventions

- **Python modules**: Snake case (e.g., `input_processor.py`)
- **Classes**: Pascal case (e.g., `DrugProcessor`)
- **Functions**: Snake case (e.g., `get_drug_fingerprint`)
- **Constants**: Upper snake case (e.g., `VALIDATION_CASES`)
- **Data files**: Descriptive names with appropriate extensions (e.g., `chembl_34.db`, `chr22.vcf.gz`, `chr10.vcf.gz`)

## Import Patterns

```python
# Standard library imports first
import os
import sys
from typing import List

# Third-party imports
import pandas as pd
from rdkit import Chem
from langchain_google_genai import ChatGoogleGenerativeAI

# Local imports last
from src.input_processor import get_drug_fingerprint
from src.vector_search import find_similar_drugs
```

## Configuration Management

- **Environment variables**: Stored in `.env` file, loaded via `python-dotenv`
- **Environment template**: `.env.example` includes competition deployment settings and cloud platform configurations
- **Default values**: Provided for optional configurations (e.g., `GEMINI_MODEL`, `ENVIRONMENT`, `DEBUG`)
- **Graceful fallbacks**: Mock modes when API keys are missing
- **Validation**: Check for required files and configurations at runtime
- **Cloud deployment configuration**: Platform-specific deployment files (render.yaml, vercel.json, Procfile)
- **Competition settings**: Optimized environment variables for demo and competition deployment
- **Docker environment**: Automated environment setup and validation in containerized deployments
- **Development configuration**: `.env.dev` and `pytest.dev.ini` for development-specific settings
- **Pre-commit configuration**: `.pre-commit-config.yaml` for automated code quality checks
- **Python project configuration**: `pyproject.toml` with development dependencies and tool configurations
- **Security scanning configuration**: Automated vulnerability scanning with Trivy/Grype integration and security reporting
- **Production monitoring configuration**: Resource tracking, health monitoring, alerting, and performance metrics collection
- **CI/CD pipeline configuration**: GitHub Actions workflows for automated builds, testing, and deployment
- **Multi-architecture build configuration**: AMD64/ARM64 platform support with build optimization
- **Backup and recovery configuration**: Automated backup procedures with integrity validation and disaster recovery

## Error Handling Patterns

- **Descriptive error messages**: Include specific guidance for resolution
- **Graceful degradation**: Continue with reduced functionality when possible
- **User-friendly output**: Clear status messages and progress indicators
- **Exception chaining**: Preserve original error context while providing user guidance
