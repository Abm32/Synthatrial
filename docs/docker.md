# Docker Deployment Guide

Complete guide for running SynthaTrial in Docker containers with professional-grade automation, security, and monitoring capabilities.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Docker Buildx for multi-architecture builds (recommended)
- `.env` file with API keys (see [Setup Guide](setup.md))

### Automated Setup (Recommended)
```bash
# Complete development environment setup
make dev-setup

# Enhanced development with all tools
make dev-enhanced

# Production deployment with SSL
make ssl-setup && make run-prod
```

### Manual Setup
```bash
# Development
docker-compose -f docker-compose.dev.yml up -d

# Enhanced development
docker-compose -f docker-compose.dev-enhanced.yml up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

---

## Container Modes

### 1. Development Mode
**File**: `docker-compose.dev.yml`
**Features**:
- Hot reloading for code changes
- Volume mounts for live development
- Jupyter notebook support
- Basic development tools (pytest, black, flake8)

```bash
# Start development container
make run-dev

# With Jupyter notebook
make jupyter

# Access Jupyter at http://localhost:8888
```

### 2. Enhanced Development Mode (NEW)
**File**: `docker-compose.dev-enhanced.yml`
**Features**:
- All development mode features plus:
- Pre-commit hooks and code quality automation
- Advanced debugging tools (gdb, strace, valgrind)
- Performance profiling capabilities
- Comprehensive testing frameworks with coverage
- Hot reload with file watching
- Multiple development servers (Streamlit, Jupyter, Flask)
- Shell enhancements (zsh, fish)
- Documentation tools (pandoc)

```bash
# Start enhanced development environment
make dev-enhanced

# Setup complete development environment
make dev-setup

# Run tests with enhanced reporting
make dev-enhanced-test

# Access services:
# - Streamlit: http://localhost:8501
# - Jupyter Lab: http://localhost:8888
# - Development server: http://localhost:8000
```

### 3. Production Mode
**File**: `docker-compose.prod.yml`
**Features**:
- Optimized for production deployment
- Minimal image size with security hardening
- Health checks and resource limits
- SSL/TLS support with automated certificate management
- Production monitoring and alerting
- Automated backup procedures

```bash
# Start production container
make run-prod

# With SSL and Nginx reverse proxy
make ssl-setup && make run-nginx

# Access application:
# - HTTPS: https://localhost (with SSL)
# - HTTP: http://localhost (redirects to HTTPS)
```

---

## SSL Certificate Management

SynthaTrial includes automated SSL certificate management for secure HTTPS deployments.

### Quick SSL Setup

```bash
# Generate self-signed certificates for development
make ssl-setup

# Test SSL configuration
make ssl-test

# View certificate information
make ssl-info

# Run development with SSL
make ssl-dev
```

### SSL Manager Script

The SSL manager provides comprehensive certificate management:

```bash
# Generate self-signed certificate
python scripts/ssl_manager.py --generate --domain localhost --output-dir docker/ssl

# Validate existing certificates
python scripts/ssl_manager.py --validate --cert docker/ssl/localhost.crt --key docker/ssl/localhost.key

# Check certificate expiration
python scripts/ssl_manager.py --check-expiration --cert docker/ssl/localhost.crt

# Setup renewal cron job
python scripts/ssl_manager.py --setup-renewal --cert docker/ssl/localhost.crt
```

### Production SSL Setup

For production deployments, use proper SSL certificates:

1. **Obtain SSL certificates** from a Certificate Authority (Let's Encrypt, etc.)
2. **Place certificates** in `docker/ssl/` directory:
   ```
   docker/ssl/
   ├── cert.pem      # SSL certificate
   ├── key.pem       # Private key
   └── chain.pem     # Certificate chain (optional)
   ```
3. **Configure Nginx** (automatically detected):
   ```bash
   make run-nginx
   ```

### SSL Configuration Features

- **Automatic HTTP to HTTPS redirection**
- **Certificate validation and integrity checking**
- **Expiration monitoring with alerts**
- **Self-signed certificate generation for development**
- **Production certificate setup guidance**
- **Automated renewal support**

### SSL Troubleshooting

```bash
# Check SSL certificate details
openssl x509 -in docker/ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect localhost:443 -servername localhost

# Verify certificate chain
openssl verify -CAfile docker/ssl/chain.pem docker/ssl/cert.pem

# Check Nginx SSL configuration
docker exec synthatrial-nginx nginx -t
```

---

## Data Initialization Automation

Automated setup and validation of required data files for SynthaTrial.

### Quick Data Setup

```bash
# Initialize all data (VCF + ChEMBL)
python scripts/data_initializer.py --all

# Download only VCF files
python scripts/data_initializer.py --vcf chr22 chr10

# Setup only ChEMBL database
python scripts/data_initializer.py --chembl

# Check data status
python scripts/data_initializer.py --status
```

### VCF File Management

Automated download and validation of 1000 Genomes Project VCF files:

```bash
# Download specific chromosomes
python scripts/download_vcf_files.py --chromosomes chr22,chr10 --output-dir data/genomes

# Validate VCF file integrity
python scripts/check_vcf_integrity.py data/genomes/chr22.vcf.gz

# Download with progress tracking
python scripts/download_vcf_files.py --chromosomes chr22 --progress --validate
```

### ChEMBL Database Setup

Automated ChEMBL database download and configuration:

```bash
# Setup ChEMBL database
python scripts/setup_chembl.py --output-dir data/chembl

# Validate ChEMBL database
python scripts/setup_chembl.py --validate --database-path data/chembl/chembl_34.db

# Setup with integrity checking
python scripts/setup_chembl.py --output-dir data/chembl --validate-integrity
```

### Data Validation Features

- **Checksum verification** for downloaded files
- **Corruption detection** and automatic re-download
- **Progress tracking** for large file downloads
- **Integrity validation** on container startup
- **Comprehensive error reporting** with remediation guidance

### Data Status Monitoring

```bash
# Check overall data status
python scripts/data_initializer.py --status

# Detailed validation report
python scripts/data_initializer.py --validate-all

# Container startup validation
docker logs synthatrial | grep "Data validation"
```

---

## Security Scanning and Monitoring

Comprehensive security scanning and vulnerability management for container images.

### Container Security Scanning

```bash
# Scan all local Docker images
make container-security-scan

# Scan specific image
make container-security-scan-image IMAGE=synthatrial:latest

# Scan for critical vulnerabilities only
make container-security-scan-critical

# Generate comprehensive security reports
make container-security-report
```

### Security Scanner Script

Advanced vulnerability scanning with multiple tools:

```bash
# Scan with Trivy (default)
python scripts/security_scanner.py --image synthatrial:latest

# Scan with Grype
python scripts/security_scanner.py --image synthatrial:latest --scanner grype

# Filter by severity
python scripts/security_scanner.py --image synthatrial:latest --severity high,critical

# Generate JSON report
python scripts/security_scanner.py --image synthatrial:latest --output-format json --output security-report.json

# Scan all images
python scripts/security_scanner.py --scan-all-images
```

### Security Features

- **Multi-tool scanning** (Trivy, Grype)
- **Severity-based filtering** and alerting
- **Detailed vulnerability reports** with remediation guidance
- **CI/CD integration** with build blocking
- **Comprehensive error handling** and logging
- **Support for local and remote images**

---

## Production Monitoring and Backup

Real-time monitoring, alerting, and backup management for production deployments.

### Production Monitoring

```bash
# Start production monitoring
make monitor-start

# Perform health check
make monitor-health

# Generate monitoring report
make monitor-report

# Create backup
make monitor-backup PATHS=/app/data,/app/logs

# Setup alert configuration
make monitor-config
```

### Production Monitor Script

Comprehensive monitoring and alerting system:

```bash
# Start monitoring with default configuration
python scripts/production_monitor.py --monitor

# Monitor with custom alert configuration
python scripts/production_monitor.py --monitor --alert-config alerts.json

# Perform health check
python scripts/production_monitor.py --health-check

# Create backup of specific paths
python scripts/production_monitor.py --backup --backup-paths /app/data,/app/logs

# Generate detailed monitoring report
python scripts/production_monitor.py --generate-report --output monitoring-report.json
```

### Monitoring Features

- **Real-time resource monitoring** (CPU, memory, disk, network)
- **Container health status tracking**
- **Performance metrics collection** and analysis
- **Configurable alerting system** with thresholds
- **Automated backup procedures** with compression
- **System recovery recommendations**
- **Integration with Docker** and container orchestration
- **Comprehensive logging** and reporting

### Alert Configuration

Create `alerts.json` for custom alerting:

```json
{
  "cpu_threshold": 80.0,
  "memory_threshold": 85.0,
  "disk_threshold": 90.0,
  "email_alerts": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "recipients": ["admin@example.com"]
  },
  "webhook_alerts": {
    "enabled": true,
    "url": "https://hooks.slack.com/services/..."
  }
}
```

### Backup Management

```bash
# Create compressed backup
python scripts/production_monitor.py --backup \
  --backup-paths /app/data,/app/logs \
  --backup-name "synthatrial-$(date +%Y%m%d)" \
  --compress

# Automated backup with retention
python scripts/production_monitor.py --backup \
  --backup-paths /app/data \
  --retention-days 30 \
  --cleanup-old
```

---

## Available Commands

### Docker Entrypoint Commands

The container supports multiple run modes via the entrypoint script:

```bash
# Web interface (default)
docker run synthatrial streamlit

# CLI mode
docker run synthatrial cli --drug-name Codeine --cyp2d6-status poor_metabolizer

# Run tests
docker run synthatrial test

# Setup tasks (Pinecone index, ChEMBL ingestion)
docker run synthatrial setup

# Performance benchmarks
docker run synthatrial benchmark

# Validation tests
docker run synthatrial validate

# Interactive shell
docker run synthatrial bash
```

### Enhanced Make Commands

#### Development Environment
```bash
# Enhanced development environment
make dev-enhanced           # Build and run enhanced development environment
make dev-enhanced-build     # Build enhanced development image
make dev-enhanced-run       # Run enhanced development container
make dev-enhanced-shell     # Open shell in enhanced development container
make dev-enhanced-test      # Run tests with enhanced reporting
make dev-enhanced-stop      # Stop enhanced development environment

# Development environment setup
make dev-setup              # Setup complete development environment
make dev-validate           # Validate development environment
make pre-commit-install     # Install pre-commit hooks
make pre-commit-run         # Run pre-commit on all files

# Basic development
make build-dev              # Build development image
make run-dev                # Run development container
make jupyter                # Run with Jupyter notebook
make ssl-dev                # Run development with SSL (Nginx)
```

#### Production Deployment
```bash
# Production builds and deployment
make build-prod             # Build production image
make run-prod               # Run production container
make run-nginx              # Run with Nginx reverse proxy

# SSL certificate management
make ssl-setup              # Generate SSL certificates
make ssl-test               # Test SSL configuration
make ssl-info               # Show SSL certificate information
```

#### Security and Monitoring
```bash
# Security scanning
make container-security-scan        # Scan all local Docker images
make container-security-scan-image  # Scan specific image (IMAGE=name:tag)
make container-security-scan-critical  # Scan for critical vulnerabilities only
make container-security-report      # Generate comprehensive security reports

# Production monitoring
make monitor-start          # Start production monitoring
make monitor-health         # Perform health check
make monitor-report         # Generate monitoring report
make monitor-backup         # Create backup (PATHS=path1,path2)
make monitor-config         # Create example alert configuration
```

#### CI/CD Integration
```bash
# CI/CD setup and validation
make ci-setup               # Setup and validate CI/CD configuration
make ci-validate            # Validate GitHub Actions workflows
make ci-test-local          # Run local CI/CD simulation
make ci-status              # Show CI/CD configuration status

# GitHub CLI integration
make gh-workflow-run        # Trigger GitHub workflow (WORKFLOW=name)
make gh-workflow-status     # Show workflow run status
make gh-workflow-logs       # Show workflow logs (RUN_ID=id)
```

#### Multi-Architecture Builds
```bash
# Multi-architecture builds
make build-multi-arch       # Build production images for AMD64+ARM64
make build-multi-arch-dev   # Build development images for AMD64+ARM64
make build-multi-arch-enhanced  # Build enhanced dev images for AMD64+ARM64
make build-and-push         # Build and push to registry (REGISTRY=url TARGET=prod)
make build-and-push-all     # Build and push all targets (REGISTRY=url)
make build-amd64            # Build for AMD64 platform only
make build-arm64            # Build for ARM64 platform only

# Build management
make multi-arch-list-builders    # List available Docker Buildx builders
make multi-arch-cleanup          # Clean up build artifacts
make multi-arch-cleanup-builder  # Clean up multi-arch builder
```

#### Registry Deployment
```bash
# Automated deployment
make deploy-staging         # Deploy to staging environment (REGISTRY=url)
make deploy-production      # Deploy to production environment (REGISTRY=url)
make deploy-development     # Deploy to development environment (REGISTRY=url)
make deploy-custom          # Custom deployment (REGISTRY=url ENV=env TAG=tag)
make deploy-list-registries # List supported container registries
make deploy-validate        # Validate deployment (REGISTRY=url ENV=env)
make deploy-cleanup         # Cleanup old deployments (REGISTRY=url)
```

#### Code Quality
```bash
# Code quality and testing
make format                 # Format code with Black and isort
make lint                   # Run linting checks
make security-scan          # Run security analysis
make test-coverage          # Run tests with coverage
```

#### General Commands
```bash
# General container management
make build                  # Build default image
make run                    # Run default container
make stop                   # Stop all containers
make clean                  # Remove containers and images
make test                   # Run tests in container
make setup                  # Run setup tasks
make logs                   # Show container logs
make shell                  # Open shell in container
```

---

## CI/CD Pipeline Integration

Automated continuous integration and deployment with GitHub Actions.

### GitHub Actions Workflows

SynthaTrial includes comprehensive CI/CD workflows:

#### 1. Docker Build and Deploy (`.github/workflows/docker-build.yml`)
- **Triggers**: Push to main/develop, tags, pull requests
- **Features**:
  - Multi-architecture builds (AMD64, ARM64)
  - Code quality checks and security scanning
  - Automated testing with coverage reporting
  - Container registry deployment
  - Environment-specific deployments

#### 2. Security Scanning (`.github/workflows/security-scan.yml`)
- **Triggers**: Daily schedule, code changes, manual dispatch
- **Features**:
  - Comprehensive vulnerability scanning
  - Dependency security analysis
  - Container image security assessment
  - Infrastructure security validation
  - Severity-based build blocking

#### 3. Release and Deploy (`.github/workflows/release.yml`)
- **Triggers**: Release publication, manual dispatch
- **Features**:
  - Automated release validation
  - Multi-environment deployment
  - Production deployment with approval gates
  - Rollback capabilities

### CI/CD Setup and Validation

```bash
# Setup CI/CD configuration
make ci-setup

# Validate GitHub Actions workflows
make ci-validate

# Run local CI/CD simulation
make ci-test-local

# Check CI/CD status
make ci-status
```

### Multi-Architecture Build Pipeline

The CI/CD system supports building for multiple architectures:

```yaml
# Example workflow configuration
strategy:
  matrix:
    platform:
      - linux/amd64
      - linux/arm64
```

### Environment-Specific Deployments

```bash
# Deploy to different environments
make deploy-staging REGISTRY=ghcr.io/your-org
make deploy-production REGISTRY=ghcr.io/your-org
make deploy-development REGISTRY=ghcr.io/your-org

# Custom deployment
make deploy-custom REGISTRY=ghcr.io/your-org ENV=testing TAG=v1.0.0
```

### Registry Integration

Supported container registries:
- **GitHub Container Registry** (ghcr.io)
- **Docker Hub**
- **Amazon ECR**
- **Google Container Registry**
- **Azure Container Registry**

```bash
# List supported registries
make deploy-list-registries

# Validate deployment configuration
make deploy-validate REGISTRY=ghcr.io/your-org ENV=production
```

### CI/CD Features

- **Automated builds** on code changes
- **Multi-architecture support** (AMD64, ARM64)
- **Comprehensive testing** (unit, integration, security)
- **Security scanning** with vulnerability assessment
- **Environment-specific deployments** with approval gates
- **Rollback capabilities** for failed deployments
- **Performance benchmarking** in CI pipeline
- **Automated documentation** updates

---

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root:

```bash
# Required for LLM simulation (Google Gemini)
GOOGLE_API_KEY=your_google_api_key

# Optional for real drug data (uses mock data if not set)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX=drug-index

# Optional model selection (defaults to gemini-2.5-flash)
GEMINI_MODEL=gemini-2.5-flash
# Alternative models: gemini-2.5-pro, gemini-2.0-flash, gemini-2.0-flash-exp

# Development environment settings
DEVELOPMENT_MODE=1                    # Enable development features
PYTHONUNBUFFERED=1                   # Real-time logging
PYTHONDONTWRITEBYTECODE=1            # Prevent .pyc files

# Streamlit configuration
STREAMLIT_SERVER_HEADLESS=true       # Headless mode for containers
STREAMLIT_SERVER_ENABLE_CORS=false   # Disable CORS for development
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false  # Disable XSRF for development
```

### Enhanced Volume Mounts

The containers use comprehensive volume mounts for different environments:

#### Development Environment
```yaml
volumes:
  # Source code (hot reload)
  - .:/app
  - /app/.pytest_cache      # Exclude cache directories
  - /app/.mypy_cache
  - /app/.hypothesis

  # Data directories (persistent)
  - ./data:/app/data:rw
  - ./logs:/app/logs:rw

  # Configuration
  - ./.env:/app/.env:ro

  # Development tools
  - ./notebooks:/app/notebooks:rw
  - ~/.ssh:/root/.ssh:ro    # SSH keys for git operations
  - ~/.gitconfig:/root/.gitconfig:ro  # Git configuration
```

#### Production Environment
```yaml
volumes:
  # Data directories (persistent)
  - ./data:/app/data:ro     # Read-only data
  - ./logs:/app/logs:rw     # Writable logs

  # Configuration (read-only)
  - ./.env:/app/.env:ro

  # SSL certificates
  - ./docker/ssl:/app/ssl:ro

  # Backup storage
  - ./backups:/app/backups:rw
```

### Environment-Specific Configuration

#### Development Configuration (`.env.dev`)
```bash
# Development-specific settings
DEVELOPMENT_MODE=1
DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_HOT_RELOAD=true
ENABLE_PROFILING=true
JUPYTER_ENABLE_LAB=true
```

#### Production Configuration (`.env.prod`)
```bash
# Production-specific settings
DEVELOPMENT_MODE=0
DEBUG=false
LOG_LEVEL=INFO
ENABLE_SSL=true
ENABLE_MONITORING=true
BACKUP_ENABLED=true
```

---

## Data Setup and Management

### Automated Data Initialization

The recommended approach is to use the automated data initialization system:

```bash
# Initialize all required data
python scripts/data_initializer.py --all

# Check current data status
python scripts/data_initializer.py --status

# Initialize specific components
python scripts/data_initializer.py --vcf chr22 chr10  # VCF files only
python scripts/data_initializer.py --chembl          # ChEMBL database only
```

### Manual VCF File Setup

If you prefer manual setup, download VCF files to the data directory:

```bash
# Create data directories
mkdir -p data/genomes
cd data/genomes

# Chromosome 22 (CYP2D6) - Required
curl -L https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz -o chr22.vcf.gz

# Chromosome 10 (CYP2C19, CYP2C9) - Required for Big 3 enzymes
curl -L https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz -o chr10.vcf.gz

# Validate file integrity
python scripts/check_vcf_integrity.py data/genomes/chr22.vcf.gz
python scripts/check_vcf_integrity.py data/genomes/chr10.vcf.gz
```

### Manual ChEMBL Database Setup

Download and extract the ChEMBL database:

```bash
# Create ChEMBL directory
mkdir -p data/chembl
cd data/chembl

# Download ChEMBL database
curl -L https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_34/chembl_34_sqlite.tar.gz -o chembl_34_sqlite.tar.gz

# Extract database
tar -xvzf chembl_34_sqlite.tar.gz

# Validate database
python scripts/setup_chembl.py --validate --database-path data/chembl/chembl_34_sqlite/chembl_34.db
```

### Data Validation and Integrity

The system includes comprehensive data validation:

```bash
# Validate all data files
python scripts/data_initializer.py --validate-all

# Check specific file integrity
python scripts/check_vcf_integrity.py data/genomes/chr22.vcf.gz

# Validate ChEMBL database
python scripts/setup_chembl.py --validate --database-path data/chembl/chembl_34.db

# Container startup validation (automatic)
docker logs synthatrial | grep "Data validation"
```

---

## Production Deployment

### Complete Production Setup

1. **Prepare Environment**:
   ```bash
   # Create production environment file
   cp .env.example .env.prod
   # Edit .env.prod with production values

   # Setup SSL certificates
   make ssl-setup
   ```

2. **Initialize Data**:
   ```bash
   # Download and validate all required data
   python scripts/data_initializer.py --all --validate
   ```

3. **Build Production Images**:
   ```bash
   # Build production image
   make build-prod

   # Or build multi-architecture images
   make build-multi-arch
   ```

4. **Deploy with Monitoring**:
   ```bash
   # Start production deployment with SSL and monitoring
   make run-prod
   make monitor-start
   ```

### Production with SSL and Nginx

For secure production deployment with reverse proxy:

1. **SSL Certificate Setup**:
   ```bash
   # For development/testing (self-signed)
   make ssl-setup

   # For production (place your certificates)
   cp your-cert.pem docker/ssl/cert.pem
   cp your-key.pem docker/ssl/key.pem
   ```

2. **Deploy with Nginx**:
   ```bash
   # Start with Nginx reverse proxy
   make run-nginx

   # Verify SSL configuration
   make ssl-test
   ```

3. **Access Application**:
   - **HTTPS**: https://your-domain.com
   - **HTTP**: Automatically redirects to HTTPS

### Production Security Configuration

#### Resource Limits and Security

Production containers include comprehensive security measures:

```yaml
# Resource limits
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
    reservations:
      memory: 2G
      cpus: '1.0'

# Security context
security_opt:
  - no-new-privileges:true
user: "1000:1000"  # Non-root user
read_only: true     # Read-only filesystem
tmpfs:
  - /tmp
  - /var/tmp
```

#### Security Scanning

Regular security scanning is essential for production:

```bash
# Scan production images
make container-security-scan-image IMAGE=synthatrial:prod

# Generate security report
make container-security-report

# Automated scanning in CI/CD
# See .github/workflows/security-scan.yml
```

### Production Monitoring Setup

#### Health Checks and Monitoring

```bash
# Setup production monitoring
make monitor-start

# Configure custom alerts
make monitor-config

# Check system health
make monitor-health

# Generate monitoring reports
make monitor-report
```

#### Backup Configuration

```bash
# Setup automated backups
make monitor-backup PATHS=/app/data,/app/logs

# Configure backup retention
python scripts/production_monitor.py --backup \
  --backup-paths /app/data \
  --retention-days 30 \
  --cleanup-old
```

### High Availability Deployment

For high availability, use Docker Swarm or Kubernetes:

#### Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml synthatrial

# Scale services
docker service scale synthatrial_synthatrial=3
```

#### Load Balancing
```bash
# Scale containers for load balancing
docker-compose -f docker-compose.prod.yml up -d --scale synthatrial=3

# Use Nginx for load balancing (configured automatically)
make run-nginx
```

---

## Health Checks and Container Management

### Container Health Monitoring

All containers include comprehensive health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Health Check Commands

```bash
# Check container health status
docker ps  # Shows health status in STATUS column

# Detailed health information
docker inspect <container_id> | grep Health

# Health check logs
docker logs <container_id> | grep health

# Manual health check
curl -f http://localhost:8501/_stcore/health
```

### Container Resource Monitoring

```bash
# Real-time resource usage
docker stats

# Detailed container information
docker inspect synthatrial

# Process monitoring inside container
make shell
htop  # Available in enhanced development environment
```

---

## Comprehensive Troubleshooting

### Container Startup Issues

#### Container Won't Start

1. **Check container logs**:
   ```bash
   make logs
   # or
   docker-compose logs synthatrial
   # or for specific container
   docker logs synthatrial-dev-enhanced
   ```

2. **Verify environment variables**:
   ```bash
   make shell
   env | grep -E "(GOOGLE|PINECONE|GEMINI)"

   # Check .env file
   cat /app/.env
   ```

3. **Check data mounts and permissions**:
   ```bash
   make shell
   ls -la /app/data/genomes/
   ls -la /app/data/chembl/

   # Check mount permissions
   ls -la /app/data/
   ```

4. **Validate Docker Compose configuration**:
   ```bash
   # Validate compose file syntax
   docker-compose -f docker-compose.dev.yml config
   docker-compose -f docker-compose.prod.yml config
   ```

#### Port Conflicts

```bash
# Check port usage
netstat -tulpn | grep :8501
lsof -i :8501

# Use different ports
docker-compose -f docker-compose.dev.yml up -d --scale synthatrial=1 -p 8502:8501
```

### API and Connectivity Issues

#### API Key Problems

1. **Verify API keys are properly set**:
   ```bash
   make shell
   python -c "import os; print('GOOGLE_API_KEY:', 'SET' if os.getenv('GOOGLE_API_KEY') else 'NOT SET')"
   ```

2. **Test API connectivity**:
   ```bash
   make test
   # or
   python scripts/list_models.py  # Test Gemini API
   ```

3. **Check API key format**:
   ```bash
   # Google API key should start with 'AIza'
   echo $GOOGLE_API_KEY | head -c 10
   ```

#### Network Connectivity

```bash
# Test external connectivity
make shell
curl -I https://api.gemini.google.com
curl -I https://www.ebi.ac.uk

# Test DNS resolution
nslookup api.gemini.google.com
```

### Data and File Issues

#### VCF File Problems

1. **Check VCF file integrity**:
   ```bash
   python scripts/check_vcf_integrity.py data/genomes/chr22.vcf.gz
   python scripts/check_vcf_integrity.py data/genomes/chr10.vcf.gz
   ```

2. **Validate VCF file format**:
   ```bash
   make shell
   zcat /app/data/genomes/chr22.vcf.gz | head -20
   ```

3. **Re-download corrupted files**:
   ```bash
   python scripts/download_vcf_files.py --chromosomes chr22 --force-redownload
   ```

#### ChEMBL Database Issues

1. **Verify ChEMBL database**:
   ```bash
   python scripts/setup_chembl.py --validate --database-path data/chembl/chembl_34_sqlite/chembl_34.db
   ```

2. **Check database file**:
   ```bash
   make shell
   ls -la /app/data/chembl/chembl_34_sqlite/chembl_34.db
   sqlite3 /app/data/chembl/chembl_34_sqlite/chembl_34.db ".tables"
   ```

3. **Re-setup ChEMBL database**:
   ```bash
   python scripts/setup_chembl.py --output-dir data/chembl --force-redownload
   ```

### Performance Issues

#### High Resource Usage

1. **Monitor resource consumption**:
   ```bash
   docker stats
   make monitor-health
   ```

2. **Optimize container resources**:
   ```bash
   # Increase memory limits in docker-compose files
   # Edit docker-compose.prod.yml:
   deploy:
     resources:
       limits:
         memory: 8G  # Increase from 4G
         cpus: '4.0'  # Increase from 2.0
   ```

3. **Performance benchmarking**:
   ```bash
   make benchmark
   python scripts/benchmark_performance.py
   ```

#### Slow Application Response

1. **Check application logs**:
   ```bash
   make logs | grep -E "(ERROR|WARNING|SLOW)"
   ```

2. **Profile application performance**:
   ```bash
   # Enable profiling in development
   make dev-enhanced
   # Profiling tools available in enhanced environment
   ```

3. **Optimize model selection**:
   ```bash
   # Use faster model for development
   export GEMINI_MODEL=gemini-2.5-flash  # Fastest
   # vs gemini-2.5-pro  # More accurate but slower
   ```

### SSL and Security Issues

#### SSL Certificate Problems

1. **Validate SSL certificates**:
   ```bash
   make ssl-test
   python scripts/ssl_manager.py --validate --cert docker/ssl/localhost.crt --key docker/ssl/localhost.key
   ```

2. **Check certificate expiration**:
   ```bash
   python scripts/ssl_manager.py --check-expiration --cert docker/ssl/localhost.crt
   ```

3. **Regenerate certificates**:
   ```bash
   make ssl-setup  # Regenerate self-signed certificates
   ```

#### Security Scanning Issues

1. **Run security scans**:
   ```bash
   make container-security-scan
   python scripts/security_scanner.py --image synthatrial:latest
   ```

2. **Address vulnerabilities**:
   ```bash
   # Update base images
   make build-prod --no-cache

   # Check for updates
   docker pull continuumio/miniconda3:latest
   ```

### Development Environment Issues

#### Pre-commit Hook Problems

1. **Install pre-commit hooks**:
   ```bash
   make pre-commit-install
   ```

2. **Run pre-commit manually**:
   ```bash
   make pre-commit-run
   ```

3. **Fix pre-commit issues**:
   ```bash
   # Format code
   make format

   # Run linting
   make lint
   ```

#### Hot Reload Not Working

1. **Check volume mounts**:
   ```bash
   docker inspect synthatrial-dev-enhanced | grep -A 10 Mounts
   ```

2. **Restart development container**:
   ```bash
   make dev-enhanced-stop
   make dev-enhanced
   ```

3. **Check file watching**:
   ```bash
   make shell
   # Check if inotify-tools is installed
   which inotifywait
   ```

### CI/CD and Build Issues

#### Multi-Architecture Build Problems

1. **Check buildx availability**:
   ```bash
   docker buildx version
   docker buildx ls
   ```

2. **Setup buildx builder**:
   ```bash
   docker buildx create --name multiarch --use
   docker buildx inspect --bootstrap
   ```

3. **Install QEMU emulation**:
   ```bash
   docker run --privileged --rm tonistiigi/binfmt --install all
   ```

#### Registry Push Failures

1. **Check registry authentication**:
   ```bash
   docker login ghcr.io
   ```

2. **Verify registry permissions**:
   ```bash
   # Check if you have push permissions to the repository
   ```

3. **Test registry connectivity**:
   ```bash
   docker pull ghcr.io/your-org/test-image || echo "Registry access test"
   ```

### Advanced Debugging

#### Container Debugging

```bash
# Access container with debugging tools
make dev-enhanced-shell

# Debug with strace (enhanced environment)
strace -p <pid>

# Memory debugging with valgrind (enhanced environment)
valgrind --tool=memcheck python app.py

# Network debugging
netstat -tulpn
ss -tulpn
```

#### Application Debugging

```bash
# Python debugging
make shell
python -c "
import sys
print('Python version:', sys.version)
print('Python path:', sys.path)
"

# Check imports
python -c "
try:
    from src.input_processor import get_drug_fingerprint
    print('✅ Input processor OK')
except Exception as e:
    print('❌ Input processor error:', e)
"

# Test core functionality
python tests/quick_test.py
```

#### Log Analysis

```bash
# Comprehensive log analysis
make logs | grep -E "(ERROR|CRITICAL|FATAL)"

# Application-specific logs
docker logs synthatrial 2>&1 | grep -E "(Streamlit|RDKit|Pinecone)"

# System logs
journalctl -u docker.service | tail -50
```

---

## Advanced Configuration and Customization

### Custom Docker Images

#### Extending Base Images

Create custom Dockerfile for specific needs:

```dockerfile
# custom/Dockerfile.research
FROM synthatrial:dev-enhanced

# Add research-specific tools
RUN conda install -c conda-forge \
    jupyter-lab \
    plotly \
    seaborn \
    biopython

# Add custom Python packages
RUN pip install \
    rdkit-pypi \
    chembl-webresource-client \
    pubchempy

# Custom configuration
COPY custom/research_config.py /app/config/
ENV RESEARCH_MODE=1
```

Build and use custom image:
```bash
docker build -f custom/Dockerfile.research -t synthatrial:research .
docker run -p 8501:8501 synthatrial:research
```

#### Multi-Stage Custom Builds

```dockerfile
# custom/Dockerfile.optimized
# Stage 1: Build dependencies
FROM continuumio/miniconda3:latest AS builder
RUN conda install -c conda-forge rdkit pandas scipy
RUN pip install --no-deps custom-package

# Stage 2: Runtime
FROM synthatrial:prod
COPY --from=builder /opt/conda /opt/conda
```

### Environment-Specific Configurations

#### Staging Environment

```yaml
# docker-compose.staging.yml
version: '3.8'
services:
  synthatrial:
    extends:
      file: docker-compose.prod.yml
      service: synthatrial
    environment:
      - GEMINI_MODEL=gemini-1.5-flash  # Different model for staging
      - LOG_LEVEL=DEBUG
      - ENABLE_PROFILING=true
    deploy:
      resources:
        limits:
          memory: 2G  # Reduced resources for staging
          cpus: '1.0'
```

#### Testing Environment

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  synthatrial:
    extends:
      file: docker-compose.dev.yml
      service: synthatrial
    environment:
      - TESTING_MODE=1
      - MOCK_API_CALLS=true
      - SKIP_DATA_VALIDATION=true
    command: ["python", "-m", "pytest", "tests/", "-v"]
```

### Container Orchestration

#### Docker Swarm Deployment

```bash
# Initialize Docker Swarm
docker swarm init

# Create overlay network
docker network create --driver overlay synthatrial-network

# Deploy stack
docker stack deploy -c docker-compose.swarm.yml synthatrial

# Scale services
docker service scale synthatrial_synthatrial=3
docker service scale synthatrial_nginx=2
```

#### Kubernetes Deployment

```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: synthatrial
spec:
  replicas: 3
  selector:
    matchLabels:
      app: synthatrial
  template:
    metadata:
      labels:
        app: synthatrial
    spec:
      containers:
      - name: synthatrial
        image: synthatrial:prod
        ports:
        - containerPort: 8501
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: synthatrial-secrets
              key: google-api-key
```

### Performance Optimization

#### Resource Tuning

```yaml
# docker-compose.performance.yml
version: '3.8'
services:
  synthatrial:
    image: synthatrial:prod
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 4G
          cpus: '2.0'
    environment:
      - PYTHONOPTIMIZE=2  # Enable Python optimizations
      - OMP_NUM_THREADS=4  # Optimize NumPy/SciPy
    ulimits:
      memlock:
        soft: -1
        hard: -1
```

#### Caching Strategies

```bash
# Enable Docker BuildKit for better caching
export DOCKER_BUILDKIT=1

# Use cache mounts in Dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Multi-stage builds with caching
FROM synthatrial:base AS dependencies
RUN --mount=type=cache,target=/opt/conda/pkgs \
    conda install -c conda-forge rdkit
```

### Security Hardening

#### Production Security Configuration

```yaml
# docker-compose.secure.yml
version: '3.8'
services:
  synthatrial:
    image: synthatrial:prod
    security_opt:
      - no-new-privileges:true
      - apparmor:docker-default
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
      - /var/tmp:noexec,nosuid,size=50m
    user: "1000:1000"
```

#### Secrets Management

```bash
# Create Docker secrets
echo "your-google-api-key" | docker secret create google_api_key -
echo "your-pinecone-key" | docker secret create pinecone_api_key -

# Use secrets in compose file
secrets:
  google_api_key:
    external: true
  pinecone_api_key:
    external: true

services:
  synthatrial:
    secrets:
      - google_api_key
      - pinecone_api_key
```

---

## Integration Examples

### CI/CD Pipeline Integration

#### GitHub Actions Integration

```yaml
# .github/workflows/custom-deploy.yml
name: Custom Deployment

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - development
          - staging
          - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and deploy
        run: |
          make build-multi-arch
          make deploy-${{ github.event.inputs.environment }}
```

#### Jenkins Integration

```groovy
// Jenkinsfile
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'make build-multi-arch'
            }
        }

        stage('Test') {
            steps {
                sh 'make test'
                sh 'make container-security-scan'
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'make deploy-production'
            }
        }
    }
}
```

### Monitoring Integration

#### Prometheus Integration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'synthatrial'
    static_configs:
      - targets: ['synthatrial:8501']
    metrics_path: '/metrics'
```

#### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "SynthaTrial Monitoring",
    "panels": [
      {
        "title": "Container CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total[5m])"
          }
        ]
      }
    ]
  }
}
```

---

## Best Practices and Recommendations

### Development Best Practices

1. **Use Enhanced Development Environment**:
   ```bash
   make dev-enhanced  # Comprehensive tooling
   ```

2. **Enable Pre-commit Hooks**:
   ```bash
   make pre-commit-install
   ```

3. **Regular Security Scanning**:
   ```bash
   make container-security-scan
   ```

4. **Data Validation**:
   ```bash
   python scripts/data_initializer.py --validate-all
   ```

### Production Best Practices

1. **Use Multi-Architecture Builds**:
   ```bash
   make build-multi-arch
   ```

2. **Enable SSL/TLS**:
   ```bash
   make ssl-setup && make run-nginx
   ```

3. **Setup Monitoring**:
   ```bash
   make monitor-start
   ```

4. **Regular Backups**:
   ```bash
   make monitor-backup PATHS=/app/data,/app/logs
   ```

5. **Security Hardening**:
   ```bash
   # Use production security configuration
   docker-compose -f docker-compose.secure.yml up -d
   ```

### Performance Best Practices

1. **Resource Optimization**:
   - Use appropriate resource limits
   - Enable caching strategies
   - Optimize model selection

2. **Network Optimization**:
   - Use CDN for static assets
   - Enable compression
   - Optimize API calls

3. **Storage Optimization**:
   - Use volume mounts for persistent data
   - Implement backup strategies
   - Monitor disk usage

---

For more information, see:
- [Setup Guide](setup.md) - Initial configuration and installation
- [Usage Guide](usage.md) - How to use the application
- [Implementation Guide](implementation.md) - Technical implementation details
- [Troubleshooting Guide](troubleshooting.md) - Common issues and solutions
- [CI/CD Guide](cicd.md) - Continuous integration and deployment
- [SSL Setup Guide](ssl_setup.md) - SSL certificate management
