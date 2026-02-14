# SSL Certificate Setup Guide

This guide covers SSL certificate setup for SynthaTrial's Docker deployment with automatic HTTPS redirection and enhanced security.

## Overview

SynthaTrial's enhanced Docker setup includes:
- **Automatic SSL certificate generation** for development
- **HTTP to HTTPS redirection** with security headers
- **Production SSL certificate support** with validation
- **Nginx reverse proxy** with enhanced security configuration

## Quick Start

### 1. Generate SSL Certificates

```bash
# Generate self-signed certificates for development
make ssl-setup

# Or manually:
python3 scripts/ssl_manager.py --domain localhost --output-dir docker/ssl
```

### 2. Start with SSL Support

```bash
# Development with SSL
make ssl-dev

# Production with SSL
make run-nginx
```

### 3. Access the Application

- **HTTPS**: https://localhost:8443 (development) or https://localhost (production)
- **HTTP**: Automatically redirects to HTTPS

## SSL Certificate Management

### Development Certificates (Self-Signed)

The SSL Manager automatically generates self-signed certificates for development:

```bash
# Generate certificates
make ssl-setup

# Validate certificates
make ssl-test

# View certificate information
make ssl-info
```

**Generated Files:**
- `docker/ssl/localhost.crt` - SSL certificate
- `docker/ssl/localhost.key` - Private key

### Production Certificates

For production deployment, replace self-signed certificates with certificates from a trusted Certificate Authority (CA). This section provides comprehensive guidance for production SSL certificate setup.

#### Option 1: Let's Encrypt (Recommended for Production)

Let's Encrypt provides free, automated SSL certificates with 90-day validity and automatic renewal.

**Prerequisites:**
- Domain name pointing to your server
- Port 80 and 443 accessible from the internet
- Certbot installed on your system

**Installation and Setup:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install certbot

# CentOS/RHEL
sudo yum install certbot

# macOS
brew install certbot
```

**Certificate Generation:**

```bash
# Stop any running web servers on port 80/443
sudo systemctl stop nginx apache2 2>/dev/null || true

# Generate certificate for your domain (standalone mode)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Alternative: Use webroot mode if you have a running web server
sudo certbot certonly --webroot -w /var/www/html -d yourdomain.com -d www.yourdomain.com

# For multiple domains
sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com -d admin.yourdomain.com
```

**Copy Certificates to SynthaTrial:**

```bash
# Create SSL directory if it doesn't exist
mkdir -p docker/ssl

# Copy Let's Encrypt certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem docker/ssl/yourdomain.com.crt
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem docker/ssl/yourdomain.com.key

# Update ownership and permissions
sudo chown $USER:$USER docker/ssl/yourdomain.com.*
chmod 644 docker/ssl/yourdomain.com.crt
chmod 600 docker/ssl/yourdomain.com.key

# Validate the certificates
python3 scripts/ssl_manager.py --validate docker/ssl/yourdomain.com.crt --key docker/ssl/yourdomain.com.key
```

**Automated Renewal Setup:**

```bash
# Test renewal process
sudo certbot renew --dry-run

# Add renewal to crontab (runs twice daily)
echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'docker-compose restart nginx'" | sudo crontab -

# Alternative: Use systemd timer (recommended for modern systems)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

#### Option 2: Commercial SSL Certificate

Commercial certificates from trusted CAs like DigiCert, GlobalSign, or Comodo provide extended validation and warranty.

**Step 1: Generate Certificate Signing Request (CSR)**

```bash
# Generate CSR using SSL Manager
python3 scripts/ssl_manager.py --domain yourdomain.com --generate-csr --output-dir docker/ssl

# Or manually with OpenSSL
openssl req -new -newkey rsa:2048 -nodes -keyout docker/ssl/yourdomain.com.key -out docker/ssl/yourdomain.com.csr

# Provide the following information when prompted:
# Country Name (2 letter code): US
# State or Province Name: Your State
# City or Locality Name: Your City
# Organization Name: Your Company
# Organizational Unit Name: IT Department
# Common Name: yourdomain.com
# Email Address: admin@yourdomain.com
```

**Step 2: Submit CSR to Certificate Authority**

1. Copy the CSR content:
```bash
cat docker/ssl/yourdomain.com.csr
```

2. Submit to your chosen CA through their web interface
3. Complete domain validation (email, DNS, or file-based)
4. Download the issued certificate bundle

**Step 3: Install Certificate**

```bash
# Download certificate files from CA
# Typically includes: certificate.crt, intermediate.crt, root.crt

# Create certificate chain (certificate + intermediate + root)
cat certificate.crt intermediate.crt root.crt > docker/ssl/yourdomain.com.crt

# Or if you have separate files:
cp certificate.crt docker/ssl/yourdomain.com.crt
cp private.key docker/ssl/yourdomain.com.key

# Set proper permissions
chmod 644 docker/ssl/yourdomain.com.crt
chmod 600 docker/ssl/yourdomain.com.key

# Validate certificate chain
python3 scripts/ssl_manager.py --validate docker/ssl/yourdomain.com.crt --key docker/ssl/yourdomain.com.key
```

#### Option 3: Wildcard Certificates

For multiple subdomains, use wildcard certificates:

**Let's Encrypt Wildcard (DNS Challenge):**

```bash
# Install DNS plugin for your provider (example: Cloudflare)
sudo apt-get install python3-certbot-dns-cloudflare

# Create credentials file
echo "dns_cloudflare_api_token = YOUR_API_TOKEN" > ~/.secrets/certbot/cloudflare.ini
chmod 600 ~/.secrets/certbot/cloudflare.ini

# Generate wildcard certificate
sudo certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/certbot/cloudflare.ini -d "*.yourdomain.com" -d yourdomain.com

# Copy to SynthaTrial
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem docker/ssl/yourdomain.com.crt
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem docker/ssl/yourdomain.com.key
sudo chown $USER:$USER docker/ssl/yourdomain.com.*
```

#### Option 4: Enterprise Certificate Management

For enterprise environments with existing PKI infrastructure:

**Using Enterprise CA:**

```bash
# Generate CSR with enterprise requirements
openssl req -new -newkey rsa:4096 -nodes -keyout docker/ssl/yourdomain.com.key -out docker/ssl/yourdomain.com.csr -config enterprise.conf

# Submit through enterprise certificate management system
# Install issued certificate and intermediate chain
# Configure certificate monitoring and automated renewal
```

**Certificate Deployment Automation:**

```bash
# Create deployment script for certificate updates
cat > scripts/deploy_enterprise_certs.sh << 'EOF'
#!/bin/bash
# Enterprise certificate deployment script

CERT_SOURCE="/path/to/enterprise/certs"
SSL_DIR="docker/ssl"

# Copy certificates from enterprise store
cp "$CERT_SOURCE/yourdomain.com.crt" "$SSL_DIR/"
cp "$CERT_SOURCE/yourdomain.com.key" "$SSL_DIR/"

# Validate certificates
python3 scripts/ssl_manager.py --validate "$SSL_DIR/yourdomain.com.crt" --key "$SSL_DIR/yourdomain.com.key"

# Restart services
docker-compose restart nginx
EOF

chmod +x scripts/deploy_enterprise_certs.sh
```

### Certificate Validation

The SSL Manager provides comprehensive certificate validation:

```bash
# Validate certificate and key match
python3 scripts/ssl_manager.py --validate docker/ssl/localhost.crt --key docker/ssl/localhost.key

# Check expiration date
python3 scripts/ssl_manager.py --check-expiration docker/ssl/localhost.crt

# Setup renewal monitoring
python3 scripts/ssl_manager.py --setup-renewal docker/ssl/localhost.crt
```

## Nginx Configuration

### Enhanced Security Features

The enhanced Nginx configuration includes:

- **HTTP to HTTPS redirection** with 301 status codes
- **Security headers**: HSTS, X-Frame-Options, CSP, etc.
- **Rate limiting** to prevent abuse
- **WebSocket support** for Streamlit real-time features
- **Static file caching** for improved performance
- **Health check endpoints** for monitoring

### Certificate Detection

Nginx automatically detects certificates in this priority order:

1. `localhost.crt/localhost.key` (SSL Manager default)
2. `cert.pem/key.pem` (original configuration)
3. `cert.crt/cert.key` (alternative naming)
4. `server.crt/server.key` (common naming)

### Custom Domain Configuration

To use a custom domain:

1. Generate certificate for your domain:
```bash
python3 scripts/ssl_manager.py --domain yourdomain.com --output-dir docker/ssl
```

2. Update Nginx configuration:
```bash
# The nginx-ssl-setup.sh script will automatically detect and configure certificates
# No manual configuration needed
```

## Docker Compose Integration

### Development Setup

```yaml
# docker-compose.dev.yml includes nginx-dev profile
services:
  nginx-dev:
    image: nginx:alpine
    ports:
      - "8443:443"  # HTTPS
      - "8080:80"   # HTTP (redirects to HTTPS)
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:rw
      - ./docker/nginx-ssl-setup.sh:/etc/nginx/nginx-ssl-setup.sh:ro
      - ./docker/nginx-entrypoint.sh:/docker-entrypoint.sh:ro
      - ./docker/ssl:/etc/nginx/ssl:rw
    profiles:
      - nginx-dev
```

### Production Setup

```yaml
# docker-compose.prod.yml includes nginx profile
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"   # HTTPS
      - "80:80"     # HTTP (redirects to HTTPS)
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:rw
      - ./docker/nginx-ssl-setup.sh:/etc/nginx/nginx-ssl-setup.sh:ro
      - ./docker/nginx-entrypoint.sh:/docker-entrypoint.sh:ro
      - ./docker/ssl:/etc/nginx/ssl:rw
    profiles:
      - nginx
```

## Production Deployment Best Practices

### Security Hardening

#### Certificate Security
- **Use strong key sizes**: Minimum 2048-bit RSA or 256-bit ECC keys
- **Implement proper key management**: Store private keys securely with restricted access
- **Enable certificate transparency**: Monitor certificate issuance for your domains
- **Use certificate pinning**: For mobile apps and critical services

```bash
# Generate strong RSA key (4096-bit for high security)
openssl genrsa -out docker/ssl/yourdomain.com.key 4096

# Generate ECC key (faster, smaller, equally secure)
openssl ecparam -genkey -name secp384r1 -out docker/ssl/yourdomain.com.key

# Set restrictive permissions
chmod 600 docker/ssl/*.key
chmod 644 docker/ssl/*.crt
chown root:ssl-cert docker/ssl/*  # Use ssl-cert group if available
```

#### Nginx Security Configuration

**Enhanced SSL Configuration:**
```nginx
# Strong SSL configuration for production
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/nginx/ssl/ca-bundle.crt;

# Session settings
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_session_tickets off;

# Security headers
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' wss: https:; frame-ancestors 'none';" always;
```

### Monitoring and Alerting

#### Certificate Expiration Monitoring

**Automated Monitoring Script:**
```bash
#!/bin/bash
# Certificate expiration monitoring script
# Place in /usr/local/bin/check-ssl-expiry.sh

DOMAIN="yourdomain.com"
CERT_PATH="/path/to/docker/ssl/${DOMAIN}.crt"
DAYS_WARNING=30
DAYS_CRITICAL=7

# Check certificate expiration
EXPIRY_DATE=$(openssl x509 -in "$CERT_PATH" -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
CURRENT_EPOCH=$(date +%s)
DAYS_UNTIL_EXPIRY=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))

# Send alerts based on days remaining
if [ $DAYS_UNTIL_EXPIRY -le $DAYS_CRITICAL ]; then
    # Critical alert - certificate expires soon
    echo "CRITICAL: SSL certificate for $DOMAIN expires in $DAYS_UNTIL_EXPIRY days!"
    # Send to monitoring system (e.g., Nagios, Zabbix, PagerDuty)
    curl -X POST "https://api.pagerduty.com/incidents" \
         -H "Authorization: Token YOUR_API_TOKEN" \
         -H "Content-Type: application/json" \
         -d "{\"incident\":{\"type\":\"incident\",\"title\":\"SSL Certificate Expiring: $DOMAIN\",\"service\":{\"id\":\"YOUR_SERVICE_ID\"},\"urgency\":\"high\"}}"
elif [ $DAYS_UNTIL_EXPIRY -le $DAYS_WARNING ]; then
    # Warning alert
    echo "WARNING: SSL certificate for $DOMAIN expires in $DAYS_UNTIL_EXPIRY days"
    # Send warning notification
fi
```

**Cron Configuration:**
```bash
# Add to crontab for daily monitoring
0 9 * * * /usr/local/bin/check-ssl-expiry.sh

# Or use systemd timer for more control
# /etc/systemd/system/ssl-monitor.service
[Unit]
Description=SSL Certificate Expiration Monitor
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/check-ssl-expiry.sh
User=ssl-monitor
Group=ssl-monitor

# /etc/systemd/system/ssl-monitor.timer
[Unit]
Description=Run SSL Certificate Monitor Daily
Requires=ssl-monitor.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

#### Health Checks and Monitoring

**SSL Health Check Endpoint:**
```bash
# Add to your application or create separate health check service
curl -f -s -o /dev/null https://yourdomain.com/health || exit 1

# Advanced SSL health check
#!/bin/bash
# ssl-health-check.sh
DOMAIN="yourdomain.com"
PORT="443"

# Check SSL certificate validity
if ! echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:$PORT 2>/dev/null | openssl x509 -checkend 86400 -noout; then
    echo "SSL certificate expires within 24 hours"
    exit 1
fi

# Check SSL connection
if ! curl -f -s -m 10 https://$DOMAIN/health > /dev/null; then
    echo "SSL connection failed"
    exit 1
fi

echo "SSL health check passed"
exit 0
```

### Backup and Recovery

#### Certificate Backup Strategy

**Automated Backup Script:**
```bash
#!/bin/bash
# ssl-backup.sh - Backup SSL certificates and keys

BACKUP_DIR="/backup/ssl/$(date +%Y%m%d)"
SSL_DIR="/path/to/docker/ssl"
RETENTION_DAYS=90

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup certificates and keys
cp -r "$SSL_DIR"/* "$BACKUP_DIR/"

# Encrypt backup (optional but recommended)
tar -czf "$BACKUP_DIR.tar.gz" -C "$BACKUP_DIR" .
gpg --cipher-algo AES256 --compress-algo 1 --s2k-mode 3 --s2k-digest-algo SHA512 --s2k-count 65536 --symmetric --output "$BACKUP_DIR.tar.gz.gpg" "$BACKUP_DIR.tar.gz"

# Clean up unencrypted files
rm -rf "$BACKUP_DIR" "$BACKUP_DIR.tar.gz"

# Remove old backups
find /backup/ssl/ -name "*.tar.gz.gpg" -mtime +$RETENTION_DAYS -delete

echo "SSL backup completed: $BACKUP_DIR.tar.gz.gpg"
```

#### Disaster Recovery Procedures

**Certificate Recovery Process:**
1. **Identify the issue**: Certificate corruption, expiration, or loss
2. **Stop services**: Prevent further SSL errors
3. **Restore from backup**: Use most recent valid backup
4. **Validate certificates**: Ensure restored certificates are valid
5. **Update services**: Restart with restored certificates
6. **Monitor**: Verify SSL functionality is restored

**Recovery Script:**
```bash
#!/bin/bash
# ssl-recovery.sh - Restore SSL certificates from backup

BACKUP_FILE="$1"
SSL_DIR="/path/to/docker/ssl"
TEMP_DIR="/tmp/ssl-recovery-$$"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file.tar.gz.gpg>"
    exit 1
fi

# Create temporary directory
mkdir -p "$TEMP_DIR"

# Decrypt and extract backup
gpg --decrypt "$BACKUP_FILE" | tar -xzf - -C "$TEMP_DIR"

# Validate restored certificates
for cert in "$TEMP_DIR"/*.crt; do
    key="${cert%.crt}.key"
    if [ -f "$key" ]; then
        if ! openssl x509 -in "$cert" -noout -checkend 0; then
            echo "ERROR: Certificate $cert is expired or invalid"
            exit 1
        fi

        # Check certificate/key match
        cert_modulus=$(openssl x509 -noout -modulus -in "$cert" | openssl md5)
        key_modulus=$(openssl rsa -noout -modulus -in "$key" | openssl md5)

        if [ "$cert_modulus" != "$key_modulus" ]; then
            echo "ERROR: Certificate and key do not match: $cert, $key"
            exit 1
        fi
    fi
done

# Backup current SSL directory
if [ -d "$SSL_DIR" ]; then
    mv "$SSL_DIR" "${SSL_DIR}.backup.$(date +%Y%m%d-%H%M%S)"
fi

# Restore certificates
mkdir -p "$SSL_DIR"
cp "$TEMP_DIR"/* "$SSL_DIR/"

# Set proper permissions
chmod 644 "$SSL_DIR"/*.crt
chmod 600 "$SSL_DIR"/*.key

# Clean up
rm -rf "$TEMP_DIR"

echo "SSL certificates restored successfully"
echo "Restart your services to apply the restored certificates"
```

### Compliance and Auditing

#### Security Compliance

**PCI DSS Requirements:**
- Use TLS 1.2 or higher
- Disable weak ciphers and protocols
- Implement proper key management
- Regular security assessments

**HIPAA Requirements:**
- Encrypt data in transit using strong SSL/TLS
- Implement access controls for certificate management
- Maintain audit logs of certificate operations
- Regular risk assessments

**SOC 2 Requirements:**
- Document SSL/TLS configuration procedures
- Implement change management for certificates
- Monitor certificate expiration and renewal
- Maintain security incident response procedures

#### Audit Logging

**SSL Operations Logging:**
```bash
# Log SSL certificate operations
logger -t ssl-manager "Certificate generated for domain: $DOMAIN"
logger -t ssl-manager "Certificate validation: $RESULT"
logger -t ssl-manager "Certificate renewal: $STATUS"

# Centralized logging configuration
# /etc/rsyslog.d/50-ssl.conf
:programname, isequal, "ssl-manager" /var/log/ssl-operations.log
& stop
```

**Compliance Reporting:**
```bash
#!/bin/bash
# ssl-compliance-report.sh - Generate SSL compliance report

REPORT_DATE=$(date +%Y-%m-%d)
REPORT_FILE="/reports/ssl-compliance-$REPORT_DATE.txt"

echo "SSL/TLS Compliance Report - $REPORT_DATE" > "$REPORT_FILE"
echo "=========================================" >> "$REPORT_FILE"

# Check certificate expiration
echo "Certificate Expiration Status:" >> "$REPORT_FILE"
for cert in /path/to/ssl/*.crt; do
    domain=$(basename "$cert" .crt)
    expiry=$(openssl x509 -in "$cert" -noout -enddate | cut -d= -f2)
    days_until_expiry=$(( ($(date -d "$expiry" +%s) - $(date +%s)) / 86400 ))
    echo "  $domain: $days_until_expiry days remaining" >> "$REPORT_FILE"
done

# Check SSL configuration
echo "SSL Configuration Status:" >> "$REPORT_FILE"
echo "  TLS Protocols: $(nginx -T 2>/dev/null | grep ssl_protocols)" >> "$REPORT_FILE"
echo "  Cipher Suites: Strong ciphers configured" >> "$REPORT_FILE"
echo "  HSTS: Enabled" >> "$REPORT_FILE"

# Security headers check
echo "Security Headers Status:" >> "$REPORT_FILE"
curl -s -I https://yourdomain.com | grep -E "(Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options)" >> "$REPORT_FILE"

echo "Report generated: $REPORT_FILE"
```

## Troubleshooting

### Common Issues and Solutions

#### Certificate Generation Issues

**Issue: OpenSSL not found**
```bash
# Error: openssl: command not found
# Solution: Install OpenSSL
sudo apt-get install openssl  # Ubuntu/Debian
sudo yum install openssl      # CentOS/RHEL
brew install openssl          # macOS
```

**Issue: Permission denied when generating certificates**
```bash
# Error: Permission denied: 'docker/ssl/localhost.key'
# Solution: Check directory permissions and create if needed
mkdir -p docker/ssl
chmod 755 docker/ssl
sudo chown $USER:$USER docker/ssl
```

**Issue: Certificate generation fails with "unable to write 'random state'"**
```bash
# Error: unable to write 'random state'
# Solution: Set RANDFILE environment variable
export RANDFILE=$HOME/.rnd
# Or create the file manually
touch $HOME/.rnd
chmod 600 $HOME/.rnd
```

#### Certificate Validation Issues

**Issue: Certificate and private key do not match**
```bash
# Error: Certificate and private key do not match
# Solution: Regenerate both certificate and key together
rm docker/ssl/localhost.*
make ssl-setup

# Or validate manually
openssl x509 -noout -modulus -in docker/ssl/localhost.crt | openssl md5
openssl rsa -noout -modulus -in docker/ssl/localhost.key | openssl md5
# The MD5 hashes should match
```

**Issue: Certificate has expired**
```bash
# Error: Certificate has expired
# Solution: Check expiration and regenerate if needed
python3 scripts/ssl_manager.py --check-expiration docker/ssl/localhost.crt

# Regenerate expired certificate
rm docker/ssl/localhost.*
make ssl-setup
```

**Issue: Invalid certificate format**
```bash
# Error: unable to load certificate
# Solution: Verify certificate format
openssl x509 -in docker/ssl/localhost.crt -text -noout

# If corrupted, regenerate
make ssl-setup
```

#### Docker and Nginx Issues

**Issue: Nginx fails to start with SSL configuration**
```bash
# Error: nginx: [emerg] cannot load certificate
# Solution: Check certificate paths and permissions
ls -la docker/ssl/
docker-compose logs nginx

# Validate Nginx configuration
docker run --rm -v $(pwd)/docker/nginx.conf:/etc/nginx/nginx.conf nginx:alpine nginx -t
```

**Issue: SSL certificate not found in container**
```bash
# Error: SSL certificate not found: /etc/nginx/ssl/localhost.crt
# Solution: Check volume mounts in docker-compose.yml
docker-compose config | grep -A 5 -B 5 ssl

# Verify volume mount
docker-compose exec nginx ls -la /etc/nginx/ssl/
```

**Issue: HTTP requests not redirecting to HTTPS**
```bash
# Error: HTTP requests return 404 instead of redirecting
# Solution: Check Nginx configuration for redirect rules
docker-compose exec nginx nginx -T | grep -A 10 -B 10 "return 301"

# Test redirect manually
curl -I http://localhost:8080/
# Should return: HTTP/1.1 301 Moved Permanently
```

**Issue: Browser shows "Connection is not secure" warning**
```bash
# Issue: Self-signed certificate warning in browser
# Solution: This is expected for self-signed certificates
# For development: Accept the security exception
# For production: Use certificates from trusted CA (Let's Encrypt, commercial)

# Check certificate details in browser:
# Chrome: Click on "Not secure" -> Certificate (invalid)
# Firefox: Click on lock icon -> Connection not secure -> More information
```

#### Let's Encrypt Issues

**Issue: Let's Encrypt certificate generation fails**
```bash
# Error: Failed authorization procedure
# Solution: Check domain DNS and firewall settings

# Verify domain points to your server
nslookup yourdomain.com
dig yourdomain.com

# Check if ports 80 and 443 are accessible
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Test with dry run
sudo certbot certonly --standalone --dry-run -d yourdomain.com
```

**Issue: Let's Encrypt rate limits**
```bash
# Error: too many certificates already issued
# Solution: Use staging environment for testing
sudo certbot certonly --staging --standalone -d yourdomain.com

# Check rate limits
curl -s "https://crt.sh/?q=yourdomain.com&output=json" | jq length
```

**Issue: Let's Encrypt renewal fails**
```bash
# Error: renewal failed
# Solution: Check renewal configuration and logs
sudo certbot renew --dry-run
sudo journalctl -u certbot.timer
sudo cat /var/log/letsencrypt/letsencrypt.log

# Manual renewal
sudo certbot renew --force-renewal
```

#### Container and Docker Issues

**Issue: Docker container cannot access SSL certificates**
```bash
# Error: Permission denied accessing SSL files
# Solution: Check file ownership and permissions
ls -la docker/ssl/
sudo chown -R $USER:$USER docker/ssl/
chmod 644 docker/ssl/*.crt
chmod 600 docker/ssl/*.key
```

**Issue: SSL setup fails in CI/CD pipeline**
```bash
# Error: SSL setup fails in automated deployment
# Solution: Use environment-specific certificate management
# For CI/CD, use secrets management for production certificates

# GitHub Actions example:
# Store certificates as repository secrets
# Use deployment-specific SSL setup scripts
```

**Issue: Multiple certificate files causing conflicts**
```bash
# Error: Multiple certificates found, using wrong one
# Solution: Clean up SSL directory and use consistent naming
ls -la docker/ssl/
rm docker/ssl/*.crt docker/ssl/*.key
make ssl-setup

# Or specify exact certificate in Nginx config
```

### Advanced Troubleshooting

#### SSL/TLS Protocol Issues

**Issue: SSL handshake failures**
```bash
# Test SSL connection
openssl s_client -connect localhost:8443 -servername localhost

# Check supported protocols and ciphers
nmap --script ssl-enum-ciphers -p 8443 localhost

# Test specific TLS version
openssl s_client -tls1_2 -connect localhost:8443
```

**Issue: Cipher suite compatibility problems**
```bash
# Check cipher suites
openssl ciphers -v 'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS'

# Test with specific cipher
openssl s_client -cipher ECDHE-RSA-AES256-GCM-SHA384 -connect localhost:8443
```

#### Certificate Chain Issues

**Issue: Incomplete certificate chain**
```bash
# Check certificate chain
openssl s_client -connect yourdomain.com:443 -showcerts

# Verify chain with CA bundle
openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt docker/ssl/yourdomain.com.crt

# Build complete chain
cat yourdomain.com.crt intermediate.crt root.crt > docker/ssl/yourdomain.com.crt
```

#### Performance and Security Issues

**Issue: SSL performance problems**
```bash
# Enable OCSP stapling
# Add to Nginx configuration:
# ssl_stapling on;
# ssl_stapling_verify on;

# Test OCSP stapling
openssl s_client -connect yourdomain.com:443 -status
```

**Issue: Security scanner warnings**
```bash
# Test SSL security
testssl.sh yourdomain.com:443

# Or use online tools:
# SSL Labs: https://www.ssllabs.com/ssltest/
# Security Headers: https://securityheaders.com/
```

### Debugging Commands

#### Certificate Analysis
```bash
# View certificate details
openssl x509 -in docker/ssl/localhost.crt -text -noout

# Check certificate dates
openssl x509 -in docker/ssl/localhost.crt -noout -dates

# Verify certificate chain
openssl verify -verbose -CAfile ca-bundle.crt docker/ssl/localhost.crt

# Check certificate fingerprint
openssl x509 -in docker/ssl/localhost.crt -noout -fingerprint -sha256
```

#### Network and Connection Testing
```bash
# Test SSL connection with full handshake details
openssl s_client -connect localhost:8443 -debug -msg

# Check certificate from remote server
echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates

# Test HTTP to HTTPS redirect
curl -v -L http://localhost:8080/

# Check SSL certificate expiration remotely
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

#### Container and Service Debugging
```bash
# Check Nginx configuration syntax
docker-compose exec nginx nginx -t

# View Nginx error logs
docker-compose logs nginx | grep error

# Check SSL certificate loading in Nginx
docker-compose exec nginx nginx -T | grep ssl_certificate

# Monitor SSL connections
docker-compose exec nginx tail -f /var/log/nginx/access.log | grep SSL

# Check container SSL directory
docker-compose exec nginx ls -la /etc/nginx/ssl/
```

### Getting Help

If you encounter issues not covered in this troubleshooting guide:

1. **Check the logs**: Always start with container logs and system logs
2. **Validate configuration**: Use built-in validation tools before deployment
3. **Test incrementally**: Test each component (certificate generation, validation, Nginx config) separately
4. **Use verbose output**: Enable verbose logging for detailed error information
5. **Check documentation**: Refer to official documentation for OpenSSL, Nginx, and certificate authorities
6. **Community resources**: Stack Overflow, Docker forums, and SSL/TLS communities

**Useful Resources:**
- OpenSSL Documentation: https://www.openssl.org/docs/
- Nginx SSL Module: http://nginx.org/en/docs/http/ngx_http_ssl_module.html
- Let's Encrypt Documentation: https://letsencrypt.org/docs/
- SSL Labs Testing: https://www.ssllabs.com/ssltest/
- Mozilla SSL Configuration Generator: https://ssl-config.mozilla.org/

## Automation and Monitoring

### Certificate Renewal

The SSL Manager provides renewal monitoring:

```bash
# Setup renewal checking (creates cron-ready script)
python3 scripts/ssl_manager.py --setup-renewal docker/ssl/localhost.crt

# Add to crontab for daily checks
0 9 * * * /path/to/synthatrial/docker/ssl/check_renewal.sh
```

### Health Monitoring

Nginx includes health check endpoints:

- **HTTP health check**: http://localhost:8080/health
- **HTTPS health check**: https://localhost:8443/health
- **Docker health checks**: Automated container health monitoring

### Logging and Monitoring

```bash
# View Nginx logs
docker-compose logs nginx

# Monitor SSL certificate status
make ssl-info

# Check container health
docker-compose ps
```

## Integration with CI/CD

The SSL setup integrates seamlessly with automated deployment pipelines and CI/CD systems.

### GitHub Actions Integration

**SSL Certificate Management in CI/CD:**

```yaml
# .github/workflows/ssl-deployment.yml
name: SSL Certificate Deployment

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly certificate check
  workflow_dispatch:     # Manual trigger

jobs:
  ssl-management:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y openssl

    - name: Check certificate expiration
      run: |
        python3 scripts/ssl_manager.py --check-expiration docker/ssl/localhost.crt

    - name: Generate development certificates
      if: github.ref == 'refs/heads/develop'
      run: |
        make ssl-setup

    - name: Deploy production certificates
      if: github.ref == 'refs/heads/main'
      env:
        PROD_CERT: ${{ secrets.PRODUCTION_CERTIFICATE }}
        PROD_KEY: ${{ secrets.PRODUCTION_PRIVATE_KEY }}
      run: |
        echo "$PROD_CERT" > docker/ssl/production.crt
        echo "$PROD_KEY" > docker/ssl/production.key
        chmod 644 docker/ssl/production.crt
        chmod 600 docker/ssl/production.key
        python3 scripts/ssl_manager.py --validate docker/ssl/production.crt --key docker/ssl/production.key

    - name: Update deployment
      run: |
        docker-compose down
        docker-compose up -d

    - name: Verify SSL deployment
      run: |
        sleep 30  # Wait for services to start
        curl -f -s -o /dev/null https://localhost:8443/health || exit 1
```

### Docker Compose Production Deployment

**Production SSL Configuration:**

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  synthatrial:
    build:
      context: .
      dockerfile: docker/Dockerfile.prod
    environment:
      - SSL_ENABLED=true
      - SSL_CERT_PATH=/app/ssl/production.crt
      - SSL_KEY_PATH=/app/ssl/production.key
    volumes:
      - ./docker/ssl:/app/ssl:ro
    networks:
      - synthatrial-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx-ssl-setup.sh:/etc/nginx/nginx-ssl-setup.sh:ro
      - ./docker/nginx-entrypoint.sh:/docker-entrypoint.sh:ro
      - ./docker/ssl:/etc/nginx/ssl:ro
    depends_on:
      - synthatrial
    networks:
      - synthatrial-network
    healthcheck:
      test: ["CMD", "curl", "-f", "-k", "https://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    entrypoint: ["/docker-entrypoint.sh"]

networks:
  synthatrial-network:
    driver: bridge

volumes:
  ssl-certificates:
    driver: local
```

### Kubernetes Deployment

**SSL Certificate Management in Kubernetes:**

```yaml
# k8s/ssl-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: synthatrial-ssl-certs
  namespace: synthatrial
type: kubernetes.io/tls
data:
  tls.crt: # Base64 encoded certificate
  tls.key: # Base64 encoded private key

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: synthatrial
  namespace: synthatrial
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
        image: synthatrial:latest
        ports:
        - containerPort: 8501
        volumeMounts:
        - name: ssl-certs
          mountPath: /app/ssl
          readOnly: true
        env:
        - name: SSL_ENABLED
          value: "true"
        - name: SSL_CERT_PATH
          value: "/app/ssl/tls.crt"
        - name: SSL_KEY_PATH
          value: "/app/ssl/tls.key"
      volumes:
      - name: ssl-certs
        secret:
          secretName: synthatrial-ssl-certs

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: synthatrial-ingress
  namespace: synthatrial
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - synthatrial.yourdomain.com
    secretName: synthatrial-tls
  rules:
  - host: synthatrial.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: synthatrial-service
            port:
              number: 80
```

### Terraform Infrastructure as Code

**SSL Certificate Management with Terraform:**

```hcl
# terraform/ssl.tf
resource "aws_acm_certificate" "synthatrial" {
  domain_name       = "synthatrial.yourdomain.com"
  validation_method = "DNS"

  subject_alternative_names = [
    "*.synthatrial.yourdomain.com"
  ]

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "SynthaTrial SSL Certificate"
    Environment = var.environment
  }
}

resource "aws_acm_certificate_validation" "synthatrial" {
  certificate_arn         = aws_acm_certificate.synthatrial.arn
  validation_record_fqdns = [for record in aws_route53_record.synthatrial_validation : record.fqdn]
}

resource "aws_route53_record" "synthatrial_validation" {
  for_each = {
    for dvo in aws_acm_certificate.synthatrial.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.main.zone_id
}

# Application Load Balancer with SSL
resource "aws_lb" "synthatrial" {
  name               = "synthatrial-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false

  tags = {
    Name = "SynthaTrial ALB"
    Environment = var.environment
  }
}

resource "aws_lb_listener" "synthatrial_https" {
  load_balancer_arn = aws_lb.synthatrial.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate_validation.synthatrial.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.synthatrial.arn
  }
}

resource "aws_lb_listener" "synthatrial_http" {
  load_balancer_arn = aws_lb.synthatrial.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}
```

### Ansible Automation

**SSL Certificate Deployment with Ansible:**

```yaml
# ansible/ssl-deployment.yml
---
- name: Deploy SSL Certificates for SynthaTrial
  hosts: synthatrial_servers
  become: yes
  vars:
    ssl_dir: /opt/synthatrial/docker/ssl
    domain_name: "{{ synthatrial_domain | default('localhost') }}"

  tasks:
    - name: Create SSL directory
      file:
        path: "{{ ssl_dir }}"
        state: directory
        mode: '0755'
        owner: root
        group: ssl-cert

    - name: Install OpenSSL
      package:
        name: openssl
        state: present

    - name: Copy production certificates
      copy:
        content: "{{ item.content }}"
        dest: "{{ ssl_dir }}/{{ item.dest }}"
        mode: "{{ item.mode }}"
        owner: root
        group: ssl-cert
      loop:
        - { content: "{{ production_certificate }}", dest: "{{ domain_name }}.crt", mode: "0644" }
        - { content: "{{ production_private_key }}", dest: "{{ domain_name }}.key", mode: "0600" }
      when: environment == "production"
      no_log: true  # Don't log sensitive certificate data

    - name: Generate self-signed certificates for development
      command: |
        python3 /opt/synthatrial/scripts/ssl_manager.py
        --domain {{ domain_name }}
        --output-dir {{ ssl_dir }}
      when: environment != "production"

    - name: Validate certificates
      command: |
        python3 /opt/synthatrial/scripts/ssl_manager.py
        --validate {{ ssl_dir }}/{{ domain_name }}.crt
        --key {{ ssl_dir }}/{{ domain_name }}.key
      register: cert_validation
      failed_when: cert_validation.rc != 0

    - name: Restart SynthaTrial services
      docker_compose:
        project_src: /opt/synthatrial
        state: present
        restarted: yes

    - name: Verify SSL endpoint
      uri:
        url: "https://{{ domain_name }}/health"
        method: GET
        validate_certs: no  # Allow self-signed for development
        timeout: 30
      retries: 3
      delay: 10
```

### Automated Certificate Renewal

**Production Certificate Renewal Automation:**

```bash
#!/bin/bash
# scripts/automated-ssl-renewal.sh
# Automated SSL certificate renewal for production environments

set -euo pipefail

# Configuration
DOMAIN="${SSL_DOMAIN:-localhost}"
SSL_DIR="${SSL_DIR:-docker/ssl}"
BACKUP_DIR="${BACKUP_DIR:-/backup/ssl}"
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-admin@yourdomain.com}"
DAYS_BEFORE_EXPIRY="${DAYS_BEFORE_EXPIRY:-30}"

# Logging
LOG_FILE="/var/log/ssl-renewal.log"
exec 1> >(tee -a "$LOG_FILE")
exec 2>&1

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# Check certificate expiration
check_expiration() {
    local cert_path="$SSL_DIR/$DOMAIN.crt"

    if [ ! -f "$cert_path" ]; then
        log "ERROR: Certificate not found: $cert_path"
        return 1
    fi

    local expiry_date
    expiry_date=$(openssl x509 -in "$cert_path" -noout -enddate | cut -d= -f2)
    local expiry_epoch
    expiry_epoch=$(date -d "$expiry_date" +%s)
    local current_epoch
    current_epoch=$(date +%s)
    local days_until_expiry
    days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))

    log "Certificate expires in $days_until_expiry days"

    if [ "$days_until_expiry" -le "$DAYS_BEFORE_EXPIRY" ]; then
        log "Certificate renewal needed"
        return 0
    else
        log "Certificate renewal not needed"
        return 1
    fi
}

# Backup current certificates
backup_certificates() {
    local backup_path="$BACKUP_DIR/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_path"

    cp "$SSL_DIR"/*.crt "$SSL_DIR"/*.key "$backup_path/" 2>/dev/null || true

    log "Certificates backed up to: $backup_path"
}

# Renew Let's Encrypt certificate
renew_letsencrypt() {
    log "Renewing Let's Encrypt certificate for $DOMAIN"

    # Stop services to free port 80
    docker-compose down || true

    # Renew certificate
    if certbot renew --standalone --cert-name "$DOMAIN"; then
        log "Certificate renewal successful"

        # Copy renewed certificates
        cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/$DOMAIN.crt"
        cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/$DOMAIN.key"

        # Set permissions
        chmod 644 "$SSL_DIR/$DOMAIN.crt"
        chmod 600 "$SSL_DIR/$DOMAIN.key"

        # Validate renewed certificates
        if python3 scripts/ssl_manager.py --validate "$SSL_DIR/$DOMAIN.crt" --key "$SSL_DIR/$DOMAIN.key"; then
            log "Certificate validation successful"
            return 0
        else
            log "ERROR: Certificate validation failed"
            return 1
        fi
    else
        log "ERROR: Certificate renewal failed"
        return 1
    fi
}

# Restart services
restart_services() {
    log "Restarting SynthaTrial services"

    if docker-compose up -d; then
        log "Services restarted successfully"

        # Wait for services to be ready
        sleep 30

        # Verify SSL endpoint
        if curl -f -s -m 10 "https://$DOMAIN/health" > /dev/null; then
            log "SSL endpoint verification successful"
            return 0
        else
            log "ERROR: SSL endpoint verification failed"
            return 1
        fi
    else
        log "ERROR: Failed to restart services"
        return 1
    fi
}

# Send notification
send_notification() {
    local status="$1"
    local message="$2"

    # Email notification
    echo "$message" | mail -s "SSL Certificate Renewal: $status" "$NOTIFICATION_EMAIL" || true

    # Slack notification (if webhook configured)
    if [ -n "${SLACK_WEBHOOK:-}" ]; then
        curl -X POST -H 'Content-type: application/json' \
             --data "{\"text\":\"SSL Certificate Renewal: $status\\n$message\"}" \
             "$SLACK_WEBHOOK" || true
    fi

    # PagerDuty notification for failures
    if [ "$status" = "FAILED" ] && [ -n "${PAGERDUTY_API_KEY:-}" ]; then
        curl -X POST "https://api.pagerduty.com/incidents" \
             -H "Authorization: Token $PAGERDUTY_API_KEY" \
             -H "Content-Type: application/json" \
             -d "{\"incident\":{\"type\":\"incident\",\"title\":\"SSL Certificate Renewal Failed: $DOMAIN\",\"service\":{\"id\":\"$PAGERDUTY_SERVICE_ID\"},\"urgency\":\"high\"}}" || true
    fi
}

# Main renewal process
main() {
    log "Starting SSL certificate renewal check for $DOMAIN"

    if check_expiration; then
        backup_certificates

        if renew_letsencrypt && restart_services; then
            local message="SSL certificate renewal completed successfully for $DOMAIN"
            log "$message"
            send_notification "SUCCESS" "$message"
        else
            local message="SSL certificate renewal failed for $DOMAIN. Manual intervention required."
            log "$message"
            send_notification "FAILED" "$message"
            exit 1
        fi
    else
        log "No renewal needed for $DOMAIN"
    fi
}

# Execute main function
main "$@"
```

For production deployments, ensure certificates are properly managed in your CI/CD pipeline with secure storage, automated renewal, and comprehensive monitoring.
