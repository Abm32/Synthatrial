# Technology Stack

## Core Technologies

- **Python 3.10+** - Primary language
- **RDKit** - Molecular fingerprinting and cheminformatics
- **Pinecone** - Vector similarity search database
- **Google Gemini** - LLM for pharmacogenomics analysis (default: gemini-2.5-flash, supports gemini-1.5-flash, gemini-2.5-pro, gemini-2.0-flash)
- **LangChain** - LLM integration framework with enhanced RAG capabilities
- **Streamlit** - Modern minimalistic web interface with 3D molecular visualization, Lottie animations, and user-friendly UX
- **SQLite** - ChEMBL database storage
- **Docker** - Containerization for development and production deployment with multi-stage builds
- **Multi-chromosome VCF processing** - Big 3 enzymes support (CYP2D6, CYP2C19, CYP2C9)
- **Targeted Variant Lookup** - Dictionary-based genotyping using Tier 1 Clinical Variants (CPIC Level A) from PharmVar
- **Activity Score method** - CPIC/PharmVar guideline-based metabolizer status inference with structural variant detection

## Key Dependencies

### Core Dependencies
```
rdkit>=2023.9.1
pandas>=2.0.0
scipy>=1.11.0
scikit-learn>=1.3.0
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-google-genai>=0.1.0
pinecone>=5.0.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
streamlit>=1.28.0
plotly>=5.18.0
py3Dmol>=2.0.0
stmol>=0.0.9
streamlit-lottie>=0.0.5
requests>=2.28.0
tenacity>=8.2.0
ipython_genutils>=0.2.0
pytest>=7.0.0
hypothesis>=6.0.0
fastapi>=0.111.0
uvicorn[standard]>=0.30.0
psutil>=5.9.0
docker>=6.0.0
```

### Development Dependencies
```
pre-commit>=3.6.0
black>=23.12.0
isort>=5.13.0
flake8>=7.0.0
mypy>=1.8.0
bandit>=1.7.5
pytest-cov>=4.1.0
pytest-xdist>=3.5.0
pytest-mock>=3.12.0
pytest-benchmark>=4.0.0
pytest-html>=4.1.0
pytest-json-report>=1.5.0
pytest-timeout>=2.2.0
pytest-asyncio>=0.23.0
coverage>=7.4.0
```

### Security and Monitoring Dependencies
```
trivy>=0.50.0          # Container vulnerability scanning
grype>=0.74.0          # Alternative vulnerability scanner
docker>=7.0.0          # Docker SDK for Python
psutil>=5.9.0          # System and process monitoring
cryptography>=41.0.0   # SSL certificate management
pyyaml>=6.0.1          # YAML configuration parsing
requests>=2.31.0       # HTTP requests for health checks
semgrep>=1.45.0        # Static analysis security scanner
safety>=2.3.0          # Python dependency vulnerability scanner
```

## Environment Setup

### Installation
```bash
# Create conda environment (required for RDKit)
conda create -n synthatrial python=3.10
conda activate synthatrial

# Install RDKit via conda (required)
conda install -c conda-forge rdkit pandas scipy scikit-learn

# Install other dependencies via pip
pip install langchain langchain-openai langchain-google-genai pinecone-client python-dotenv streamlit
```

### Environment Variables
Create `.env` file with:
```bash
# Required for LLM simulation (Google Gemini)
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional model selection (defaults to gemini-2.5-flash)
GEMINI_MODEL=gemini-2.5-flash
# Alternative models: gemini-2.5-pro, gemini-2.0-flash, gemini-2.0-flash-exp

# Optional for real drug data (uses mock mode if missing)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX=drug-index

# Optional: Environment settings
ENVIRONMENT=development
DEBUG=true
PORT=8000
```

## Common Commands

### API Deployment Commands
```bash
# Local API testing
python api.py                    # Start FastAPI server locally
python test_api.py              # Run API test suite locally
python test_api.py https://anukriti-ai-competition.onrender.com  # Test deployed API

# API health check
curl http://localhost:8000/     # Local health check
curl https://anukriti-ai-competition.onrender.com/  # Deployed health check

# Competition demo endpoints
curl https://anukriti-ai-competition.onrender.com/demo  # Get demo examples
curl https://anukriti-ai-competition.onrender.com/health  # Detailed health status

# API analysis endpoint
curl -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"drug_name":"Warfarin","patient_profile":"ID: HG00096\nGenetics: CYP2C9 Poor Metabolizer","similar_drugs":[]}'

# Interactive API documentation
# Visit http://localhost:8000/docs for Swagger UI
# Visit http://localhost:8000/redoc for ReDoc
```

### Cloud Deployment Commands
```bash
# Render.com deployment (recommended for competition)
# 1. Push to GitHub: git push origin main
# 2. Create Render web service with:
#    Build: pip install -r requirements.txt
#    Start: uvicorn api:app --host 0.0.0.0 --port 10000
#    Environment: GOOGLE_API_KEY=your_key

# Vercel deployment (serverless alternative)
npm i -g vercel
vercel --prod
vercel env add GOOGLE_API_KEY

# Heroku deployment (with Procfile)
heroku create anukriti-ai-app
heroku config:set GOOGLE_API_KEY=your_key
git push heroku main

# AWS EC2 deployment (production with VCF support - CHEAPEST OPTION)
# See AWS_EC2_DEPLOYMENT.md for complete guide
# Cost: ₹0/month (free tier t2.micro) or ₹400-₹750/month (t3.micro + storage)
# 1. Launch EC2 instance (t2.micro free tier or t3.micro recommended)
# 2. Install Docker
# 3. Clone repository
# 4. Download VCF files to data/genomes/ (stored on EC2 local disk)
# 5. Build and run Docker container with volume mount: -v $(pwd)/data:/app/data
# 6. Enable auto-restart: docker update --restart unless-stopped
# Access: http://<EC2_PUBLIC_IP>:8501

# Test deployed API
curl https://anukriti-ai-competition.onrender.com/
curl https://anukriti-ai-competition.onrender.com/demo
```

### Deployment Cost Comparison
```
Platform Comparison (Monthly Cost):
┌─────────────────┬──────────────┬─────────────┬──────────────┬─────────────────┐
│ Platform        │ Cost         │ VCF Support │ Setup Time   │ Best For        │
├─────────────────┼──────────────┼─────────────┼──────────────┼─────────────────┤
│ Render.com      │ Free-₹500    │ ❌ No       │ 5-10 min     │ Demos, API only │
│ Vercel          │ Free-₹1000   │ ❌ No       │ 5-10 min     │ Serverless      │
│ Heroku          │ ₹500-₹2000   │ ⚠️ Limited  │ 10-15 min    │ Simple apps     │
│ AWS EC2 (FREE)  │ ₹0-₹150      │ ✅ Full     │ 30-45 min    │ Free tier ⭐    │
│ AWS EC2 (PAID)  │ ₹400-₹750    │ ✅ Full     │ 30-45 min    │ Production ⭐   │
│ AWS ECS/Fargate │ ₹1500-₹3000  │ ✅ Full     │ 2-3 hours    │ Enterprise      │
└─────────────────┴──────────────┴─────────────┴──────────────┴─────────────────┘

Cost Optimization Tips:
- Use t2.micro (FREE for 12 months with AWS Free Tier)
- Store VCF files on EC2 local disk (no S3 costs)
- Use Reserved Instances for 40-60% savings (after free tier)
- Stop instance when not needed (no compute charges)
- Download only chr22 initially to save storage costs
```

### Setup Commands
```bash
# Setup Pinecone index
python scripts/setup_pinecone_index.py

# Ingest ChEMBL data to Pinecone
python scripts/ingest_chembl_to_pinecone.py

# Automated data initialization (NEW)
python scripts/data_initializer.py --all  # Initialize all data (VCF + ChEMBL)
python scripts/data_initializer.py --vcf chr22 chr10  # Download only VCF files
python scripts/data_initializer.py --chembl  # Setup only ChEMBL database
python scripts/data_initializer.py --status  # Check current data status

# SSL certificate management (NEW)
python scripts/ssl_manager.py --domain localhost  # Generate self-signed certificates
python scripts/ssl_manager.py --validate docker/ssl/localhost.crt --key docker/ssl/localhost.key
bash scripts/generate_ssl_certs.sh  # Alternative certificate generation

# Development environment setup (NEW)
python scripts/setup_dev_env.py  # Full development environment setup
python scripts/setup_dev_env.py --validate-only  # Validation only
python scripts/setup_dev_env.py --skip-hooks  # Skip pre-commit setup

# Download VCF data (chromosome 22 - CYP2D6)
curl -L https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz -o data/genomes/chr22.vcf.gz

# Download VCF data (chromosome 10 - CYP2C19, CYP2C9) - NEW
curl -L https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz -o data/genomes/chr10.vcf.gz

# Download ChEMBL database (optional)
curl -L https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_34/chembl_34_sqlite.tar.gz -o data/chembl/chembl_34_sqlite.tar.gz
tar -xvzf data/chembl/chembl_34_sqlite.tar.gz -C data/chembl/

# Verify VCF file integrity (optional)
python scripts/check_vcf_integrity.py data/genomes/chr10.vcf.gz
python scripts/check_vcf_integrity.py data/genomes/chr22.vcf.gz
```

### Enhanced Streamlit UI Features
```bash
# Modern minimalistic web interface with 3D visualization
streamlit run app.py

# Features include:
# - Clean, user-friendly design with minimalistic Inter font styling
# - 3D molecular structure visualization with py3Dmol and stmol
# - Lottie animations for enhanced user experience (DNA, loading, success)
# - 4-tab interface: Simulation Lab, Batch Processing, Analytics, About
# - Streamlined drug analysis workflow with curated database (7 drugs)
# - Real-time system health monitoring with API status
# - Multi-enzyme patient profiling (CYP2D6, CYP2C19, CYP2C9, UGT1A1, SLCO1B1)
# - 3-stage pipeline visualization: Genetics → Similar Drugs → Predicted Response
# - Batch processing capabilities for cohort analysis
# - Competition-ready demo interface with professional styling
# - Performance metrics and analytics dashboard
# - Cloud deployment integration status
# - Analysis history tracking and report downloads
# - Configurable API URL for flexible deployment
# - Collapsed sidebar by default for cleaner main interface
```

# REST API (production deployment)
python api.py                    # Start FastAPI server
uvicorn api:app --host 0.0.0.0 --port 8000  # Alternative start command

# Docker (recommended for production)
make quick-start  # Development mode
make run-prod     # Production mode

# Command line interface - Single chromosome (CYP2D6 only)
python main.py --vcf data/genomes/chr22.vcf.gz --sample-id HG00096

# Command line interface - Multi-chromosome (Big 3 enzymes: CYP2D6, CYP2C19, CYP2C9)
python main.py --vcf data/genomes/chr22.vcf.gz --vcf-chr10 data/genomes/chr10.vcf.gz --sample-id HG00096

# Docker CLI mode
docker run synthatrial cli --drug-name Warfarin --cyp2d6-status poor_metabolizer

# CYP2D6 status override (single enzyme)
python main.py --cyp2d6-status poor_metabolizer

# Test specific drug interactions
python main.py --vcf data/genomes/chr22.vcf.gz --vcf-chr10 data/genomes/chr10.vcf.gz --drug-name Warfarin --sample-id HG00096
python main.py --vcf data/genomes/chr22.vcf.gz --vcf-chr10 data/genomes/chr10.vcf.gz --drug-name Clopidogrel --sample-id HG00096
```

### Docker Commands (Enhanced)
```bash
# Quick development setup
make quick-start

# Development with enhanced features (NEW)
make dev-enhanced  # Enhanced development container with additional tools

# Development with Jupyter notebooks
make jupyter  # Access at http://localhost:8888

# Production deployment
make run-prod

# Production with SSL/Nginx
make run-nginx

# SSL certificate management (NEW)
make ssl-setup  # Generate SSL certificates
make ssl-validate  # Validate existing certificates

# Data initialization (NEW)
make data-init  # Initialize all data (VCF + ChEMBL)
make data-status  # Check data status

# Container management
make stop     # Stop all containers
make clean    # Remove containers and images
make logs     # Show container logs
make shell    # Open shell in container

# Testing and validation (ENHANCED)
make test     # Run validation tests
make test-properties  # Run property-based tests
make test-containerized  # Run tests in containers
make setup    # Run setup tasks (Pinecone, ChEMBL)
make benchmark # Run performance benchmarks

# Development environment (NEW)
make dev-setup  # Setup development environment
make pre-commit-install  # Install pre-commit hooks
make code-quality  # Run code quality checks

# Security scanning and monitoring (NEW)
make security-audit         # Comprehensive security audit
make vulnerability-check     # Check dependency vulnerabilities
make container-security-scan # Scan Docker images for vulnerabilities
make monitor-start          # Start production monitoring
make monitor-health         # Perform health check
make backup-all            # Create comprehensive backup
make system-status         # Complete system status overview

# Multi-architecture builds and deployment
make build-multi-arch       # Build for AMD64+ARM64 platforms
make build-and-push         # Build and push to registry (REGISTRY=url)
make deploy-staging         # Deploy to staging environment
make deploy-production      # Deploy to production environment
make ci-setup              # Setup CI/CD environment
make ci-test-local         # Run local CI/CD simulation

# Integration testing
make test-integration      # Run integration test suite
make test-all             # Run comprehensive test suite
python tests/test_integration_runner.py  # Run complete workflow integration tests

# GitHub Actions workflows
make ci-validate           # Validate GitHub Actions workflows
make ci-status            # Check CI/CD pipeline status
```

### Testing
```bash
# Quick integration test
python tests/quick_test.py

# Full validation suite
python tests/validation_tests.py

# Property-based testing (NEW)
python -m pytest tests/test_*_properties.py  # Run all property tests
python -m pytest tests/test_ssl_manager_properties.py  # SSL certificate tests
python -m pytest tests/test_data_initialization_properties.py  # Data initialization tests
python -m pytest tests/test_dev_environment_properties.py  # Development environment tests

# Containerized testing (NEW)
python scripts/run_tests_in_container.py --containers enhanced-dev  # Run tests in enhanced container
python scripts/run_tests_in_container.py --coverage-threshold 80  # Coverage requirements
python scripts/run_tests_in_container.py --ci-mode  # CI integration mode

# Test chromosome 10 integration (Big 3 enzymes)
python scripts/test_chromosome10.py

# Check VCF file integrity
python scripts/check_vcf_integrity.py data/genomes/chr10.vcf.gz

# Generate CPIC guideline validation results
python scripts/generate_validation_results.py

# Benchmark performance metrics
python scripts/benchmark_performance.py

# Comprehensive integration testing
python tests/test_integration_runner.py  # Run all integration test suites
python tests/test_complete_workflow_integration.py  # End-to-end workflow tests
python tests/test_github_actions_integration.py     # CI/CD pipeline integration tests
python tests/test_docker_environment_integration.py # Docker component integration tests

# Security scanning and monitoring
python scripts/security_scanner.py --scan-all-images  # Scan all Docker images
python scripts/production_monitor.py --start-monitoring  # Start production monitoring
python scripts/backup_manager.py --create-backup  # Create automated backup
python scripts/multi_arch_build.py --target prod --platforms linux/amd64,linux/arm64  # Multi-arch builds
python scripts/deploy_to_registry.py --environment production  # Deploy to production

# Project and deployment: see root README.md
```

## Architecture Notes

- **Modular design**: Separate processors for input, vector search, VCF, ChEMBL, and AI engine
- **Dual interface architecture**: Streamlit web UI and FastAPI REST API for flexible deployment options
- **RESTful API**: Production-ready FastAPI wrapper with health check and analysis endpoints
- **Cloud deployment ready**: Optimized for Render, Vercel, Heroku, AWS EC2, and other cloud platforms
- **AWS EC2 deployment**: Complete production deployment with Docker and VCF files stored on EC2 local storage for cost-effective full-featured deployment. Most economical option at ₹0/month (free tier) or ₹400-₹750/month (paid tier) with full VCF support. Avoids expensive managed services like ECS/Fargate (₹1500-₹3000/month) and S3 storage costs by using EC2 local disk.
- **Competition-ready deployment**: One-click deployment configurations for Render.com and Vercel with demo endpoints
- **Interactive API documentation**: Auto-generated Swagger UI and ReDoc for API exploration
- **Professional-grade containerization**: Multi-stage Docker builds with development, enhanced development, production, and CI/CD configurations
- **Enterprise security and monitoring**: Automated SSL certificate management, vulnerability scanning, production monitoring, and comprehensive security headers
- **Enhanced development environment**: Pre-commit hooks, code quality tools, property-based testing, containerized testing, and Jupyter notebook integration
- **SSL certificate management**: Automated SSL certificate generation, validation, expiration checking, and renewal for secure deployments
- **Data initialization automation**: Automated VCF file downloads, ChEMBL database setup, integrity validation, and progress tracking
- **Security scanning and compliance**: Container vulnerability scanning, dependency checking, and security reporting with Trivy/Grype integration
- **Production monitoring and alerting**: Resource tracking, health monitoring, automated backup procedures, and performance metrics collection
- **CI/CD pipeline integration**: Multi-architecture builds, automated testing pipelines, GitHub Actions workflows, and container registry deployment
- **Comprehensive integration testing**: End-to-end workflow validation, cross-component testing, and automated test orchestration
- **Multi-chromosome support**: Processes chromosome 22 (CYP2D6) and chromosome 10 (CYP2C19, CYP2C9) for Big 3 enzyme coverage
- **Targeted Variant Lookup**: Dictionary-based genotyping using specific rsIDs from PharmVar database instead of naive variant counting
- **Activity Score method**: CPIC/PharmVar guideline-based metabolizer status inference with structural variant detection (CNVs)
- **Enhanced LLM prompting**: CPIC guideline-based prompting with structural analysis using SMILES strings and multi-model support
- **Container orchestration**: Docker Compose with environment-specific configurations, health checks, and resource limits
- **Automated deployment**: SSL certificate management, data initialization, and security scanning
- **Production readiness**: Nginx reverse proxy, SSL/TLS support, monitoring, and backup automation
- **CI/CD integration**: Multi-architecture builds, automated testing, and registry deployment
- **Property-based testing**: Comprehensive testing using Hypothesis for SSL, data initialization, and development environment validation
- **Code quality automation**: Pre-commit hooks with Black, isort, flake8, mypy, bandit, and security scanning
- **Containerized testing**: Multi-container test execution with coverage reporting and CI integration
- **Lazy initialization**: LLM and database connections initialized when needed
- **Mock mode support**: Graceful fallback when API keys are missing with realistic example data
- **Error handling**: Comprehensive error handling with user-friendly messages
- **Batch processing**: Efficient batch operations for large datasets
- **Backward compatibility**: Single-chromosome mode maintained for existing workflows
- **Performance benchmarking**: Built-in tools for measuring vector retrieval, LLM simulation, and end-to-end timing
- **CPIC compliance**: Validation against Clinical Pharmacogenetics Implementation Consortium guidelines
- **Version consistency**: Maintained across all components (currently v0.2 Beta)
- **Docker enhancements complete**: All SSL certificate management, data initialization automation, security scanning, production monitoring, and CI/CD pipeline integration features are fully implemented and production-ready

## Development Guidelines

- Use conda for RDKit installation (pip installation often fails)
- Always check for API keys before making external calls
- Implement mock modes for testing without credentials
- Follow CPIC guidelines for pharmacogenomics predictions
- Use descriptive error messages for user guidance
- **Documentation**: All in root README.md; docs/README.md points to it
- **Testing**: Run validation tests after changes (`python tests/validation_tests.py`)
- **Property-based testing**: Use Hypothesis for comprehensive testing of SSL, data initialization, and development environment functionality
- **Code quality**: Use pre-commit hooks for automated code formatting, linting, and security checks
- **SSL management**: Use automated SSL certificate generation and validation for secure deployments
- **Data automation**: Use automated data initialization scripts for VCF files and ChEMBL database setup
- **Performance**: Use benchmarking tools to measure system performance (`python scripts/benchmark_performance.py`)
- **Variant Lookup**: Use targeted variant lookup from `src/variant_db.py` instead of naive variant counting
- **Multi-chromosome**: Test with both single chromosome and Big 3 enzymes modes for comprehensive coverage
- **VCF Integrity**: Always verify VCF file integrity using `python scripts/check_vcf_integrity.py`
- **Docker Development**: Use `make quick-start` for development, `make dev-enhanced` for enhanced development, `make run-prod` for production testing
- **API Development**: Use `python api.py` for local API testing, `python test_api.py` for automated API testing
- **Cloud Deployment**: Deploy FastAPI to Render, Vercel, Heroku, AWS EC2, or other cloud platforms
- **AWS EC2 Deployment**: Use `AWS_EC2_DEPLOYMENT.md` for complete production deployment with VCF support
- **Cost Optimization**: Use t2.micro (free tier) or t3.micro (₹400-₹750/month) for cheapest deployment. Avoid ECS/Fargate (₹1500-₹3000/month) and S3 storage (₹200-₹400/month extra) by using EC2 local disk for VCF files.
- **Competition Deployment**: See root README (Deployment section and render.yaml)
- **Demo Interface**: Use `demo.html` for professional competition presentations
- **API Documentation**: Use `/docs` endpoint for interactive Swagger UI, `/redoc` for alternative documentation
- **Jupyter Development**: Use `make jupyter` for notebook-based development and analysis
- **Container Management**: Use Docker health checks, resource limits, and automated SSL setup for production deployments
- **Environment Configuration**: Use corrected `.env.example` template with `GOOGLE_API_KEY` (not `OPENAI_API_KEY`)
- **Multi-mode Deployment**: Support for development (hot reload), enhanced development (additional tools), production (optimized), and CI/CD (automated) configurations
- **Security Best Practices**: Automated vulnerability scanning, SSL certificate management, container hardening, and comprehensive security monitoring
- **Performance Monitoring**: Built-in container resource monitoring, performance benchmarking tools, and automated alerting systems
- **CI/CD Integration**: Multi-architecture builds, automated testing pipelines, GitHub Actions workflows, and registry deployment automation
- **Enterprise Deployment**: Production-ready containerization with SSL/TLS, monitoring, backup automation, and disaster recovery procedures
- **Integration Testing**: Comprehensive end-to-end workflow validation, cross-component testing, and automated test orchestration
- **Model Selection**: Default to gemini-2.5-flash for speed, use gemini-2.5-pro for complex analysis
- **Project and deployment**: See root README.md for overview and deployment
- **Production Readiness**: Use `make production-ready` to validate complete system readiness for deployment
- **System Status**: Use `make system-status` and `make automation-status` for comprehensive status overview
- **Version Consistency**: Maintain consistent version numbers across all files (currently v0.2 Beta)
- **Docker Enhancements**: All Docker enhancement features are now complete and production-ready, including SSL certificate management, data initialization automation, security scanning, production monitoring, and CI/CD pipeline integration
- **Competition Ready**: Platform optimized for competition deployment with Render.com, Vercel, and demo interfaces
- **UI Design**: Use minimalistic, clean design principles for user interfaces - prioritize user-friendliness and simplicity over complex enterprise dashboards
