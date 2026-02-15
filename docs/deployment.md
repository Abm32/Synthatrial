# Deployment Automation Documentation

This document provides comprehensive information about SynthaTrial's deployment automation system for container registries and environment-specific deployments.

> **Note:** SynthaTrial is a research prototype; outputs must not be used for clinical decision-making. For VCF/ChEMBL data at deploy time, see [Deployment data](DEPLOYMENT_DATA.md).

## Overview

The deployment automation system provides:
- Multi-registry support (GitHub Container Registry, Docker Hub, AWS ECR, etc.)
- Environment-specific deployment (development, staging, production)
- Multi-architecture image deployment (AMD64, ARM64)
- Deployment validation and health checks
- Rollback capabilities
- Comprehensive logging and monitoring
- Integration with existing CI/CD infrastructure

## Quick Start

### Basic Deployment Commands

```bash
# Deploy to staging
make deploy-staging REGISTRY=ghcr.io/your-org/synthatrial

# Deploy to production (requires approval)
make deploy-production REGISTRY=ghcr.io/your-org/synthatrial TAG=v1.0.0

# Deploy to development environment
make deploy-development REGISTRY=docker.io/your-org/synthatrial

# List supported registries
make deploy-list-registries

# Validate deployment
make deploy-validate REGISTRY=ghcr.io/your-org/synthatrial ENV=staging
```

### Direct Script Usage

```bash
# Deploy with custom configuration
python scripts/deploy_to_registry.py \
  --registry ghcr.io/your-org/synthatrial \
  --environment production \
  --tag v1.0.0 \
  --images synthatrial,synthatrial-dev \
  --platforms linux/amd64,linux/arm64 \
  --health-check-url https://your-app.com/health \
  --verbose

# Validate deployment status
python scripts/deploy_to_registry.py \
  --validate-deployment \
  --registry ghcr.io/your-org/synthatrial \
  --environment production

# Cleanup old deployments
python scripts/deploy_to_registry.py \
  --cleanup \
  --registry ghcr.io/your-org/synthatrial \
  --keep-count 10
```

## Supported Container Registries

### GitHub Container Registry (GHCR)
- **URL Pattern**: `ghcr.io/{org}/{repo}`
- **Authentication**: Token-based (GitHub token)
- **Environment Variables**: `GITHUB_TOKEN` or `REGISTRY_TOKEN`
- **Example**: `ghcr.io/your-org/synthatrial`

### Docker Hub
- **URL Pattern**: `docker.io/{org}/{repo}` or `{org}/{repo}`
- **Authentication**: Username/password
- **Environment Variables**: `REGISTRY_USERNAME`, `REGISTRY_PASSWORD`
- **Example**: `docker.io/your-org/synthatrial`

### AWS Elastic Container Registry (ECR)
- **URL Pattern**: `{account}.dkr.ecr.{region}.amazonaws.com/{repo}`
- **Authentication**: AWS CLI integration
- **Prerequisites**: AWS CLI configured with proper credentials
- **Example**: `123456789012.dkr.ecr.us-west-2.amazonaws.com/synthatrial`

### Google Container Registry (GCR)
- **URL Pattern**: `gcr.io/{project}/{repo}`
- **Authentication**: Token-based (service account key)
- **Environment Variables**: `REGISTRY_TOKEN`
- **Example**: `gcr.io/your-project/synthatrial`

### Azure Container Registry (ACR)
- **URL Pattern**: `{registry}.azurecr.io/{repo}`
- **Authentication**: Username/password or token
- **Environment Variables**: `REGISTRY_USERNAME`, `REGISTRY_PASSWORD`
- **Example**: `yourregistry.azurecr.io/synthatrial`

## Environment-Specific Deployments

### Development Environment
- **Purpose**: Development and testing
- **Approval Required**: No
- **Health Check**: Optional (60s timeout)
- **Rollback**: Enabled
- **Default Images**: `synthatrial-dev`, `synthatrial-dev-enhanced`
- **Default Tag**: `dev`

### Staging Environment
- **Purpose**: Pre-production testing
- **Approval Required**: No
- **Health Check**: Required (120s timeout)
- **Rollback**: Enabled
- **Validation**: Required
- **Default Images**: All images
- **Default Tag**: `staging`

### Production Environment
- **Purpose**: Live production deployment
- **Approval Required**: Yes (manual or `DEPLOYMENT_APPROVED=true`)
- **Health Check**: Required (300s timeout)
- **Rollback**: Enabled
- **Validation**: Required
- **Default Images**: `synthatrial`
- **Default Tag**: `latest`

## Authentication Methods

### Token-Based Authentication
Used for GitHub Container Registry, Google Container Registry, and some custom registries.

```bash
# Set environment variable
export REGISTRY_TOKEN="your_token_here"

# Or pass directly
python scripts/deploy_to_registry.py \
  --registry ghcr.io/org/repo \
  --token "your_token_here" \
  --environment staging
```

### Username/Password Authentication
Used for Docker Hub, Azure Container Registry, and some custom registries.

```bash
# Set environment variables
export REGISTRY_USERNAME="your_username"
export REGISTRY_PASSWORD="your_password"

# Or pass directly
python scripts/deploy_to_registry.py \
  --registry docker.io/org/repo \
  --username "your_username" \
  --password "your_password" \
  --environment staging
```

### AWS ECR Authentication
Automatically handled through AWS CLI integration.

```bash
# Ensure AWS CLI is configured
aws configure

# Deploy to ECR
python scripts/deploy_to_registry.py \
  --registry 123456789012.dkr.ecr.us-west-2.amazonaws.com/synthatrial \
  --environment production
```

## Deployment Hooks

### Pre-Deployment Hooks
Execute before deployment begins. Useful for:
- Database migrations
- Service health checks
- Backup creation
- Notification sending

```bash
python scripts/deploy_to_registry.py \
  --registry ghcr.io/org/repo \
  --environment production \
  --pre-deploy-hook "script:scripts/backup_database.sh" \
  --pre-deploy-hook "command:echo 'Starting deployment'" \
  --pre-deploy-hook "curl -X POST https://api.slack.com/webhook"
```

### Post-Deployment Hooks
Execute after deployment completes. Useful for:
- Cache warming
- Monitoring setup
- Notification sending
- Cleanup tasks

```bash
python scripts/deploy_to_registry.py \
  --registry ghcr.io/org/repo \
  --environment production \
  --post-deploy-hook "script:scripts/warm_cache.sh" \
  --post-deploy-hook "command:echo 'Deployment completed'"
```

## Health Checks

Health checks validate that deployed applications are running correctly.

### Configuration
```bash
python scripts/deploy_to_registry.py \
  --registry ghcr.io/org/repo \
  --environment production \
  --health-check-url "https://your-app.com/health"
```

### Health Check Behavior
- **Development**: 60-second timeout, optional
- **Staging**: 120-second timeout, required
- **Production**: 300-second timeout, required
- **Retry Logic**: Checks every 10 seconds until timeout
- **Success Criteria**: HTTP 200 response
- **Failure Handling**: Triggers rollback if enabled

## Rollback Capabilities

Automatic rollback on deployment failure (when enabled).

### Rollback Triggers
- Health check failure
- Deployment script failure
- Manual rollback request

### Rollback Process
1. Detect deployment failure
2. Identify previous stable version
3. Deploy previous version
4. Validate rollback success
5. Update deployment status

### Rollback Configuration
```bash
# Enable rollback (default)
python scripts/deploy_to_registry.py \
  --registry ghcr.io/org/repo \
  --environment production

# Disable rollback
python scripts/deploy_to_registry.py \
  --registry ghcr.io/org/repo \
  --environment production \
  --no-rollback
```

## Multi-Architecture Support

Deploy images for multiple CPU architectures simultaneously.

### Supported Platforms
- `linux/amd64` (Intel/AMD 64-bit)
- `linux/arm64` (ARM 64-bit)
- `linux/arm/v7` (ARM 32-bit)
- `linux/386` (Intel/AMD 32-bit)

### Configuration
```bash
python scripts/deploy_to_registry.py \
  --registry ghcr.io/org/repo \
  --environment production \
  --platforms linux/amd64,linux/arm64
```

## CI/CD Integration

### GitHub Actions Integration
The deployment system integrates with GitHub Actions workflows:

```yaml
- name: Deploy to staging
  env:
    REGISTRY_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python3 scripts/deploy_to_registry.py \
      --registry ghcr.io/${{ github.repository }} \
      --environment staging \
      --tag staging \
      --verbose
```

### Environment Variables for CI/CD
```bash
# Required for authentication
REGISTRY_TOKEN=your_token
GITHUB_TOKEN=your_github_token

# Optional for production approval
DEPLOYMENT_APPROVED=true

# Optional for custom configuration
HEALTH_CHECK_URL=https://your-app.com/health
```

## Monitoring and Reporting

### Deployment Reports
Comprehensive reports generated for each deployment:

```json
{
  "deployment_info": {
    "timestamp": "2024-01-15T10:30:00Z",
    "deployment_id": "deploy-1705312200",
    "environment": "production",
    "registry": "ghcr.io/org/synthatrial",
    "success": true,
    "deployment_time_seconds": 245.7
  },
  "config": {
    "images": ["synthatrial"],
    "tags": ["v1.0.0", "latest"],
    "platforms": ["linux/amd64", "linux/arm64"]
  },
  "result": {
    "deployed_images": [
      "ghcr.io/org/synthatrial:v1.0.0",
      "ghcr.io/org/synthatrial:latest"
    ],
    "health_check_passed": true
  }
}
```

### Deployment Validation
Validate deployment status and image availability:

```bash
# Validate specific environment
make deploy-validate REGISTRY=ghcr.io/org/synthatrial ENV=production

# Output example
Deployment Validation Results:
Environment: production
Registry: ghcr.io/org/synthatrial
Status: SUCCESS

Images:
  ✅ ghcr.io/org/synthatrial/synthatrial:latest (exists)
  ✅ ghcr.io/org/synthatrial/synthatrial-dev:latest (exists)
  ❌ ghcr.io/org/synthatrial/synthatrial-dev-enhanced:latest (missing)
```

## Troubleshooting

### Common Issues

#### Authentication Failures
```bash
# Check token validity
echo $REGISTRY_TOKEN | docker login ghcr.io --username token --password-stdin

# Verify AWS CLI configuration
aws ecr get-login-password --region us-west-2
```

#### Build Failures
```bash
# Check multi-arch build script
python scripts/multi_arch_build.py --list-builders

# Test local build
make build-multi-arch
```

#### Health Check Failures
```bash
# Test health endpoint manually
curl -f https://your-app.com/health

# Check application logs
docker logs container_name
```

#### Registry Push Failures
```bash
# Verify registry URL
docker manifest inspect ghcr.io/org/synthatrial:latest

# Check network connectivity
ping ghcr.io
```

### Debug Mode
Enable verbose logging for detailed troubleshooting:

```bash
python scripts/deploy_to_registry.py \
  --registry ghcr.io/org/repo \
  --environment staging \
  --verbose
```

### Log Analysis
Deployment logs include:
- Authentication attempts
- Build progress
- Push operations
- Health check results
- Error details with stack traces

## Best Practices

### Security
1. **Use tokens instead of passwords** when possible
2. **Rotate credentials regularly**
3. **Use environment-specific credentials**
4. **Enable approval for production deployments**
5. **Validate deployments before promoting**

### Reliability
1. **Enable health checks** for all environments
2. **Use rollback capabilities** for critical deployments
3. **Test deployments in staging** before production
4. **Monitor deployment metrics** and success rates
5. **Implement proper error handling** in hooks

### Performance
1. **Use multi-architecture builds** for broader compatibility
2. **Leverage build caching** for faster deployments
3. **Optimize image sizes** for faster transfers
4. **Use parallel deployments** when possible
5. **Monitor deployment times** and optimize bottlenecks

### Maintenance
1. **Clean up old deployments** regularly
2. **Monitor registry storage usage**
3. **Update deployment scripts** with new features
4. **Review and update** environment configurations
5. **Document custom configurations** and procedures

## Advanced Configuration

### Custom Registry Support
Add support for custom container registries:

```python
# In scripts/deploy_to_registry.py
custom_registry = RegistryConfig(
    name="Custom Registry",
    url="custom.registry.com/org/repo",
    auth_method="token",  # or "password"
    username="your_username",  # if using password auth
    token="your_token"  # if using token auth
)
```

### Environment-Specific Hooks
Configure different hooks for different environments:

```bash
# Development hooks
--pre-deploy-hook "echo 'Dev deployment starting'"

# Staging hooks
--pre-deploy-hook "script:scripts/staging_backup.sh"
--post-deploy-hook "script:scripts/run_integration_tests.sh"

# Production hooks
--pre-deploy-hook "script:scripts/production_backup.sh"
--pre-deploy-hook "script:scripts/notify_team.sh"
--post-deploy-hook "script:scripts/warm_cache.sh"
--post-deploy-hook "script:scripts/update_monitoring.sh"
```

### Custom Health Checks
Implement custom health check logic:

```bash
# Custom health check script
#!/bin/bash
# scripts/custom_health_check.sh

echo "Performing custom health checks..."

# Check application endpoint
curl -f https://your-app.com/api/health || exit 1

# Check database connectivity
python scripts/check_database.py || exit 1

# Check external dependencies
curl -f https://external-api.com/status || exit 1

echo "All health checks passed!"
```

Use in deployment:
```bash
--post-deploy-hook "script:scripts/custom_health_check.sh"
```

## Integration Examples

### Complete Production Deployment
```bash
#!/bin/bash
# scripts/deploy_production.sh

set -e

echo "🚀 Starting production deployment..."

# Pre-deployment checks
echo "📋 Running pre-deployment checks..."
python scripts/check_prerequisites.py

# Deploy to production
echo "🏗️  Deploying to production registry..."
python scripts/deploy_to_registry.py \
  --registry ghcr.io/your-org/synthatrial \
  --environment production \
  --tag "v$(cat VERSION)" \
  --images synthatrial \
  --platforms linux/amd64,linux/arm64 \
  --health-check-url "https://synthatrial.your-org.com/health" \
  --pre-deploy-hook "script:scripts/backup_production.sh" \
  --pre-deploy-hook "script:scripts/notify_deployment_start.sh" \
  --post-deploy-hook "script:scripts/warm_cache.sh" \
  --post-deploy-hook "script:scripts/notify_deployment_complete.sh" \
  --verbose

# Validate deployment
echo "🔍 Validating production deployment..."
python scripts/deploy_to_registry.py \
  --validate-deployment \
  --registry ghcr.io/your-org/synthatrial \
  --environment production \
  --verbose

echo "✅ Production deployment completed successfully!"
```

### Staging to Production Promotion
```bash
#!/bin/bash
# scripts/promote_to_production.sh

STAGING_TAG="staging-$(date +%Y%m%d)"
PRODUCTION_TAG="v$(cat VERSION)"

echo "🔄 Promoting staging to production..."

# Validate staging deployment
echo "🔍 Validating staging deployment..."
python scripts/deploy_to_registry.py \
  --validate-deployment \
  --registry ghcr.io/your-org/synthatrial \
  --environment staging

# Tag staging images for production
echo "🏷️  Tagging images for production..."
docker pull ghcr.io/your-org/synthatrial:$STAGING_TAG
docker tag ghcr.io/your-org/synthatrial:$STAGING_TAG ghcr.io/your-org/synthatrial:$PRODUCTION_TAG
docker push ghcr.io/your-org/synthatrial:$PRODUCTION_TAG

# Deploy to production
echo "🚀 Deploying to production..."
python scripts/deploy_to_registry.py \
  --registry ghcr.io/your-org/synthatrial \
  --environment production \
  --tag $PRODUCTION_TAG \
  --verbose

echo "✅ Promotion completed successfully!"
```

This deployment automation system provides comprehensive support for container registry management and environment-specific deployments, ensuring reliable and secure deployment workflows for SynthaTrial.
