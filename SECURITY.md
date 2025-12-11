# Security Guidelines

This document outlines security best practices and hardening recommendations for deploying the Real-Time RTSP Camera Grid Viewer in production environments.

## Table of Contents

1. [Overview](#overview)
2. [Security Architecture](#security-architecture)
3. [Configuration Security](#configuration-security)
4. [Network Security](#network-security)
5. [WebRTC Security](#webrtc-security)
6. [Authentication & Authorization](#authentication--authorization)
7. [Monitoring & Incident Response](#monitoring--incident-response)
8. [Security Checklist](#security-checklist)

---

## Overview

### Security Model

The application follows a defense-in-depth approach with multiple security layers:

1. **Network Layer**: Firewall rules, port restrictions, reverse proxy
2. **Transport Layer**: TLS/SSL encryption, secure WebRTC connections
3. **Application Layer**: CORS policies, input validation, secure configuration
4. **Data Layer**: Credential management, secrets protection

### Threat Model

Primary threats to consider:

- **Unauthorized Access**: Malicious actors accessing camera feeds
- **CORS Misconfiguration**: Cross-origin attacks from untrusted domains
- **Credential Exposure**: Camera passwords leaked through configuration files
- **Man-in-the-Middle**: Unencrypted traffic interception
- **Denial of Service**: Resource exhaustion through excessive connections
- **TURN Server Abuse**: Bandwidth theft through public TURN credentials

---

## Security Architecture

### Production Architecture Diagram

```
Internet
    |
    v
[Firewall: 443 only]
    |
    v
[nginx/Caddy Reverse Proxy]
    |  (TLS Termination)
    |  (Basic Auth)
    |
    v
[Internal Network]
    |
    +-- [FastAPI :8000] (internal)
    |
    +-- [go2rtc API :1984] (internal)
    |
    +-- [go2rtc WebRTC :8555] (public - required)
    |
    +-- [RTSP Cameras] (internal)
```

### Key Principles

1. **Minimal Exposure**: Only expose WebRTC media port (8555) to public internet
2. **TLS Everywhere**: Use HTTPS for all web traffic
3. **Authentication**: Protect endpoints with basic auth or OAuth
4. **Least Privilege**: Run containers with minimal permissions

---

## Configuration Security

### Environment Variables

**Critical**: Never commit `.env` files to version control.

#### Required Production Settings

```bash
# ============================================================================
# SECURITY: MUST be configured for production
# ============================================================================

# CORS Configuration - CRITICAL
# Default "*" allows ANY website to connect. MUST restrict in production.
ALLOWED_ORIGINS=https://yourdomain.com

# TURN Server - CRITICAL
# Default uses public server. MUST use private infrastructure in production.
TURN_URL=turn:turn.yourdomain.com:3478
TURN_USERNAME=production_username_$(openssl rand -hex 8)
TURN_PASSWORD=$(openssl rand -base64 32)

# Camera Credentials - CRITICAL
# Use strong, unique passwords
CAM_PASS=$(openssl rand -base64 32)
```

### CORS Policy Best Practices

#### Development (Permissive)
```bash
ALLOWED_ORIGINS=*
```

#### Staging (Restricted)
```bash
ALLOWED_ORIGINS=https://staging.yourdomain.com
```

#### Production (Strict)
```bash
# Single domain
ALLOWED_ORIGINS=https://yourdomain.com

# Multiple trusted domains
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com,https://mobile.yourdomain.com
```

### Secrets Management

**Option 1: Docker Secrets** (Recommended for Docker Swarm)
```yaml
# docker-compose.yml
services:
  camera-viewer:
    secrets:
      - cam_password
      - turn_credentials

secrets:
  cam_password:
    external: true
  turn_credentials:
    external: true
```

**Option 2: HashiCorp Vault** (Enterprise)
```bash
export CAM_PASS=$(vault kv get -field=password secret/camera)
export TURN_PASSWORD=$(vault kv get -field=password secret/turn)
```

**Option 3: AWS Secrets Manager** (Cloud)
```bash
export CAM_PASS=$(aws secretsmanager get-secret-value \
  --secret-id camera/password --query SecretString --output text)
```

---

## Network Security

### Firewall Configuration

#### Ubuntu/Debian (ufw)

```bash
# Reset firewall (careful!)
sudo ufw --force reset

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (adjust port if changed)
sudo ufw allow 22/tcp

# Allow HTTPS (reverse proxy)
sudo ufw allow 443/tcp

# Allow WebRTC media (REQUIRED for WebRTC)
sudo ufw allow 8555/tcp
sudo ufw allow 8555/udp

# DENY direct access to backend services
sudo ufw deny 8000/tcp  # FastAPI
sudo ufw deny 1984/tcp  # go2rtc API
sudo ufw deny 8554/tcp  # RTSP

# Enable firewall
sudo ufw enable

# Verify rules
sudo ufw status verbose
```

#### CentOS/RHEL (firewalld)

```bash
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8555/tcp
sudo firewall-cmd --permanent --add-port=8555/udp
sudo firewall-cmd --reload
```

### Reverse Proxy (nginx with TLS)

#### Installation

```bash
sudo apt-get install nginx certbot python3-certbot-nginx
```

#### Configuration

```nginx
# /etc/nginx/sites-available/camera-viewer

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # TLS Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Basic Authentication (optional but recommended)
    auth_basic "Camera Viewer Access";
    auth_basic_user_file /etc/nginx/.htpasswd;

    # Proxy to FastAPI
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for long-lived connections
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://localhost:8000;
    }
}
```

#### Create Basic Auth

```bash
# Install htpasswd utility
sudo apt-get install apache2-utils

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Add more users
sudo htpasswd /etc/nginx/.htpasswd viewer
```

#### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/camera-viewer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Obtain SSL Certificate

```bash
sudo certbot --nginx -d yourdomain.com
sudo certbot renew --dry-run  # Test auto-renewal
```

---

## WebRTC Security

### TURN Server Setup

Public TURN servers (like openrelay) are **NOT suitable for production**. Set up your own:

#### Option 1: coturn (Self-Hosted)

**Installation:**
```bash
sudo apt-get install coturn
```

**Configuration** (`/etc/turnserver.conf`):
```ini
# Listener port
listening-port=3478
tls-listening-port=5349

# External IP (your server's public IP)
external-ip=YOUR_PUBLIC_IP

# Realm
realm=yourdomain.com

# Authentication
lt-cred-mech
user=username:password

# Logging
log-file=/var/log/turnserver.log
verbose

# Security
fingerprint
no-multicast-peers
no-tlsv1
no-tlsv1_1

# Performance
max-bps=1000000
bps-capacity=0
```

**Enable and start:**
```bash
sudo systemctl enable coturn
sudo systemctl start coturn
```

**Update .env:**
```bash
TURN_URL=turn:yourdomain.com:3478
TURN_USERNAME=username
TURN_PASSWORD=password
```

#### Option 2: Managed Services

**Twilio Network Traversal Service:**
- Sign up at https://www.twilio.com/stun-turn
- Get credentials from dashboard
- Pricing: Pay-as-you-go

**Cloudflare Calls:**
- Part of Cloudflare Calls product
- Integrated with Cloudflare CDN

### ICE Configuration Security

**Best Practices:**

1. **Use TLS for TURN** (port 5349):
   ```bash
   TURN_URL=turns:turn.yourdomain.com:5349
   ```

2. **Rotate TURN credentials regularly** (monthly):
   ```bash
   # Generate new credentials
   NEW_PASS=$(openssl rand -base64 32)

   # Update coturn config
   sudo sed -i "s/user=.*/user=username:$NEW_PASS/" /etc/turnserver.conf
   sudo systemctl restart coturn

   # Update application .env
   echo "TURN_PASSWORD=$NEW_PASS" >> .env
   ```

3. **Monitor TURN usage**:
   ```bash
   # Check coturn logs for abuse
   sudo tail -f /var/log/turnserver.log | grep "allocation"
   ```

4. **Implement rate limiting** in coturn config:
   ```ini
   max-allocate-lifetime=600  # 10 minutes max
   total-quota=100            # Max 100 concurrent allocations
   user-quota=10              # Max 10 per user
   ```

---

## Authentication & Authorization

### Basic Authentication (Quick Start)

Already configured in nginx example above. For API-level auth:

#### FastAPI Dependency

```python
# Add to main.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "secure_password")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Protect endpoints
@app.get("/", dependencies=[Depends(verify_credentials)])
async def get_frontend():
    ...
```

### OAuth 2.0 / JWT (Production)

For enterprise deployments, implement JWT-based authentication:

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401)
        return username
    except JWTError:
        raise HTTPException(status_code=401)
```

---

## Monitoring & Incident Response

### Logging

**Enable comprehensive logging:**

```python
# main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/camera-viewer/app.log'),
        logging.StreamHandler()
    ]
)

# Log security events
logger.info(f"Connection from {client_ip} - User: {username}")
logger.warning(f"Failed auth attempt from {client_ip}")
```

### Monitoring Tools

**Prometheus + Grafana:**

```yaml
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

**Key Metrics to Monitor:**

- Active WebRTC connections
- Failed authentication attempts
- FFmpeg process health
- Bandwidth usage
- CPU/Memory utilization
- TURN server allocation count

### Alerting

**Example Prometheus Alert Rules:**

```yaml
# /etc/prometheus/alerts.yml
groups:
  - name: camera_viewer
    rules:
      - alert: HighFailedAuthRate
        expr: rate(failed_auth_total[5m]) > 10
        annotations:
          summary: "High failed authentication rate detected"

      - alert: WebRTCConnectionFailure
        expr: webrtc_connection_failures > 50
        annotations:
          summary: "High WebRTC connection failure rate"
```

### Incident Response Plan

1. **Detection**: Automated alerts via Prometheus/Grafana
2. **Analysis**: Check logs in `/var/log/camera-viewer/`
3. **Containment**:
   - Block malicious IPs: `sudo ufw deny from <IP>`
   - Disable compromised accounts
   - Rotate credentials if exposed
4. **Recovery**:
   - Restart affected services
   - Restore from backup if needed
5. **Post-Incident**: Review and update security policies

---

## Security Checklist

### Pre-Deployment

- [ ] **Configuration**
  - [ ] ALLOWED_ORIGINS set to production domain(s)
  - [ ] Private TURN server configured
  - [ ] Strong passwords for CAM_PASS (min 32 characters)
  - [ ] .env excluded from version control
  - [ ] Secrets stored in secure vault (not plain .env)

- [ ] **Network**
  - [ ] Firewall configured (only 443 and 8555 exposed)
  - [ ] Reverse proxy with TLS enabled
  - [ ] SSL certificate valid and auto-renewing
  - [ ] HTTP redirects to HTTPS

- [ ] **Application**
  - [ ] Authentication enabled (Basic Auth or OAuth)
  - [ ] Rate limiting configured
  - [ ] Security headers set (HSTS, X-Frame-Options, etc.)
  - [ ] Logging enabled for security events

- [ ] **Infrastructure**
  - [ ] Docker containers run as non-root user
  - [ ] Regular security updates scheduled
  - [ ] Backup and recovery plan documented
  - [ ] Monitoring and alerting configured

### Post-Deployment

- [ ] **Testing**
  - [ ] Penetration testing completed
  - [ ] WebRTC connectivity verified from target networks
  - [ ] CORS policy tested (should block unauthorized origins)
  - [ ] Authentication tested (should deny invalid credentials)

- [ ] **Monitoring**
  - [ ] Logs reviewed daily
  - [ ] Alerts configured and tested
  - [ ] Metrics dashboard accessible
  - [ ] Incident response plan tested

- [ ] **Maintenance**
  - [ ] Security patches applied monthly
  - [ ] Credentials rotated quarterly
  - [ ] SSL certificate renewal automated
  - [ ] Access logs archived for compliance

---

## Vulnerability Reporting

If you discover a security vulnerability, please email security@yourdomain.com with:

1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if available)

**Please do not** open a public GitHub issue for security vulnerabilities.

---

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [WebRTC Security](https://webrtc-security.github.io/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [nginx Security Tips](https://docs.nginx.com/nginx/admin-guide/security-controls/)

---

**Last Updated**: December 2025
**Version**: 1.0
**Review Cycle**: Quarterly
