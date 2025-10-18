# Security Setup Guide

## Critical Security Improvements Applied

This document outlines the security improvements made to RAGFlow Slim and provides setup instructions.

### 1. API Key and Secrets Management

**BEFORE (INSECURE):**
- Hardcoded API keys in `docker-compose.yml`
- Default passwords in configuration files
- Weak default API key fallback ("changeme")

**AFTER (SECURE):**
- All sensitive credentials moved to environment variables
- Production mode requires `RAGFLOW_API_KEY` to be set
- Strong password requirements documented in `.env.example`

### Required Environment Variables

Create a `.env` file with the following (NEVER commit this file):

```bash
# API Authentication (REQUIRED in production)
RAGFLOW_API_KEY=<generate-strong-random-key-32-chars-min>

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=<your-supabase-service-role-key>

# Neo4j Configuration
NEO4J_PASSWORD=<strong-password-16-chars-min>

# MySQL Configuration
MYSQL_ROOT_PASSWORD=<strong-password-16-chars-min>
MYSQL_PASSWORD=<strong-password-16-chars-min>

# MinIO Configuration
MINIO_ROOT_PASSWORD=<strong-password-16-chars-min>

# LLM Provider (choose one)
GOOGLE_API_KEY=<your-google-api-key>
# or
OPENAI_API_KEY=<your-openai-api-key>
# or configure Ollama
OLLAMA_HOST=http://localhost:11434
```

### 2. Generating Strong Credentials

```bash
# Generate a strong API key (32 characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate strong passwords (16 characters)
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

### 3. Supabase Database Setup

Run the SQL setup script in your Supabase SQL Editor:

```bash
# The script is located at: setup_supabase.sql
# It will:
# - Enable pgvector extension
# - Create documents table with vector embeddings
# - Create vector similarity search function
# - Create indexes for performance
# - Set up crawl_jobs table
```

**Important:** Update the vector dimension in `setup_supabase.sql` if using a different embedding model:
- OpenAI text-embedding-3-small: 1536 dimensions
- Nomic embed-text (Ollama): 768 dimensions

### 4. Docker Compose Configuration

The `docker-compose.yml` now uses environment variable substitution:

```yaml
environment:
  - SUPABASE_KEY=${SUPABASE_KEY}  # Reads from .env file
  - GOOGLE_API_KEY=${GOOGLE_API_KEY}
  - NEO4J_PASSWORD=${NEO4J_PASSWORD}
```

**Never commit the actual `.env` file to version control!**

### 5. GitHub Secrets Setup

For CI/CD pipelines, add these secrets to your GitHub repository:

1. Go to repository Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `GOOGLE_API_KEY` (or `OPENAI_API_KEY`)

### 6. Security Best Practices

#### Password Requirements
- **Minimum length**: 16 characters
- **Complexity**: Mix of uppercase, lowercase, numbers, symbols
- **Uniqueness**: Different passwords for each service
- **Rotation**: Change passwords every 90 days

#### API Key Management
- Store keys in environment variables only
- Never hardcode keys in source code
- Use different keys for development/staging/production
- Rotate keys if compromised
- Monitor API usage for anomalies

#### Access Control
- Use principle of least privilege
- Separate service accounts for each component
- Enable 2FA for all admin accounts
- Regular security audits

### 7. Deployment Checklist

Before deploying to production:

- [ ] Generated strong, unique credentials for all services
- [ ] Created `.env` file with all required variables
- [ ] Verified `.env` is in `.gitignore`
- [ ] Ran `setup_supabase.sql` in Supabase
- [ ] Tested application with new credentials
- [ ] Configured GitHub secrets for CI/CD
- [ ] Enabled HTTPS/TLS for all external connections
- [ ] Configured firewall rules
- [ ] Set up monitoring and alerting
- [ ] Documented credential storage location (secure vault)

### 8. Security Monitoring

The project includes a security check workflow (`.github/workflows/security-check.yml`) that:
- Scans dependencies for known vulnerabilities (Safety)
- Analyzes code for security issues (Bandit)
- Checks for hardcoded secrets
- Runs weekly automatically

### 9. Incident Response

If credentials are compromised:

1. **Immediate Actions**:
   - Rotate all affected API keys immediately
   - Change all passwords
   - Review access logs for unauthorized activity
   - Lock down affected services

2. **Investigation**:
   - Identify how credentials were exposed
   - Check git history for leaked secrets
   - Review recent deployments and changes

3. **Prevention**:
   - Update `.gitignore` if needed
   - Add pre-commit hooks to prevent secret commits
   - Train team on security best practices
   - Consider using a secrets manager (AWS Secrets Manager, HashiCorp Vault)

### 10. Unicode/Encoding Fixes

**Issue**: Emoji characters in `graphiti_client.py` caused `UnicodeEncodeError` on Windows

**Fix**: Replaced all emoji print statements with proper logging:
- `print("📦 module loaded")` → `logging.debug("module loaded")`
- All emojis removed from production code
- Proper logging levels used throughout

### 11. Vector Search Implementation

**Issue**: Supabase vector search was placeholder (returned latest documents)

**Fix**: Implemented proper pgvector similarity search:
- Created `match_documents` RPC function in Supabase
- Uses cosine distance for semantic similarity
- Falls back gracefully if vector search unavailable
- Includes SQL setup script with proper indexes

### 12. Production Readiness

The application now enforces security in production mode:

```python
# In app.py
if FLASK_ENV == "production":
    if API_KEY is None:
        raise RuntimeError("RAGFLOW_API_KEY must be set in production")
```

This prevents accidental deployment with default/missing credentials.

### 13. Next Steps

1. **Secrets Manager Integration** (recommended for production):
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault

2. **Enhanced Monitoring**:
   - Set up Sentry or similar for error tracking
   - Configure Prometheus/Grafana for metrics
   - Enable audit logging

3. **Security Hardening**:
   - Enable rate limiting per user (not just per IP)
   - Implement request signing
   - Add CORS restrictions
   - Enable security headers (CSP, HSTS, etc.)

## Support

For security issues, please email security@your-domain.com (configure this).

For general support, see the main README.md.

---

**Last Updated**: 2025-10-17
**Security Review**: Critical issues resolved, production-ready with proper configuration
