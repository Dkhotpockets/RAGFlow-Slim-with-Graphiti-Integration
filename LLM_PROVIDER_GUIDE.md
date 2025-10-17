# Multi-Provider LLM Configuration Guide

## Overview

RAGFlow Slim with Graphiti Integration now supports **three LLM providers** with automatic detection:

| Provider | Cost | Speed | Privacy | Use Case |
|----------|------|-------|---------|----------|
| **Ollama** | FREE | Fast (local) | 100% Private | Development & Production |
| **Google AI** | $2-10/mo | Fast | Cloud | App Testing |
| **OpenAI** | $5-20/mo | Fast | Cloud | Legacy/Fallback |

## Quick Start

### 1. Set Provider (Auto-Detection)

```powershell
# Let RAGFlow Slim with Graphiti Integration auto-detect (recommended)
$env:LLM_PROVIDER = "auto"

# Or specify explicitly
$env:LLM_PROVIDER = "ollama"    # Local, free
$env:LLM_PROVIDER = "google"    # Google AI
$env:LLM_PROVIDER = "openai"    # OpenAI
```

### 2. Configure API Keys (if needed)

```powershell
# For Google AI
$env:GOOGLE_API_KEY = "AIzaSy...your-key"

# For OpenAI (optional fallback)
$env:OPENAI_API_KEY = "sk-proj-...your-key"

# Ollama needs no API key!
```

### 3. Check Status

```powershell
# Start services
docker-compose up -d

# Check which provider is active
curl http://localhost:5000/health
```

## Provider Details

### Ollama (Recommended for Most Users)

**✅ Pros:**
- Completely FREE - no usage limits
- Fast local processing
- 100% private - no data sent to cloud
- Works offline
- Production-ready

**Setup:**

```powershell
# 1. Install Ollama
winget install Ollama.Ollama

# 2. Pull models (one-time, ~2.3GB total)
ollama pull llama3.2            # LLM
ollama pull nomic-embed-text    # Embeddings

# 3. Configure (auto-detected if running)
$env:LLM_PROVIDER = "ollama"
```

**When to use:**
- Local development
- Cost-sensitive production
- Privacy-critical applications
- Offline environments

---

### Google AI (Gemini)

**✅ Pros:**
- Cheapest cloud option ($2-10/mo)
- Good quality (Gemini 1.5)
- Fast responses
- Easy API key setup

**Setup:**

```powershell
# 1. Get API key from: https://makersuite.google.com/app/apikey

# 2. Configure
$env:LLM_PROVIDER = "google"
$env:GOOGLE_API_KEY = "AIzaSy...your-key"
$env:GOOGLE_MODEL = "gemini-1.5-flash"  # or gemini-1.5-pro
```

**When to use:**
- App testing phase
- Cost-conscious cloud deployment
- When Ollama isn't available
- Gemini-specific features needed

---

### OpenAI

**✅ Pros:**
- Widely supported
- High quality (GPT-4)
- Extensive documentation

**⚠️ Cons:**
- More expensive ($5-20/mo)
- Requires billing setup

**Setup:**

```powershell
# 1. Get API key from: https://platform.openai.com/api-keys

# 2. Add billing: https://platform.openai.com/account/billing

# 3. Configure
$env:LLM_PROVIDER = "openai"
$env:OPENAI_API_KEY = "sk-proj-...your-key"
$env:OPENAI_MODEL = "gpt-4o-mini"  # or gpt-4o
```

**When to use:**
- OpenAI-specific features needed
- Established OpenAI workflows
- Budget allows for premium API

## Auto-Detection Logic

When `LLM_PROVIDER=auto` (default):

```
1. Check if Ollama is running locally
   ├─ Yes → Use Ollama (FREE!)
   └─ No  → Continue...

2. Check if GOOGLE_API_KEY is set
   ├─ Yes → Use Google AI
   └─ No  → Continue...

3. Check if OPENAI_API_KEY is set
   ├─ Yes → Use OpenAI
   └─ No  → Default to Ollama with warning
```

## Configuration for Different Scenarios

### Scenario 1: Local Development (FREE)

```powershell
# .env or PowerShell
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

**Cost: $0/month**

---

### Scenario 2: Multiple Apps Testing

**App 1 & 2 (Testing with Google AI):**
```powershell
LLM_PROVIDER=google
GOOGLE_API_KEY=AIzaSy...your-key
```

**Local RAGFlow Slim with Graphiti Integration (Development with Ollama):**
```powershell
LLM_PROVIDER=ollama
```

**Cost: $2-10/month (just for cloud testing)**

---

### Scenario 3: Production (All Local)

```bash
# Deploy Ollama on dedicated server
# docker-compose.yml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama

  ragflow-server:
    environment:
      - LLM_PROVIDER=ollama
      - OLLAMA_HOST=http://ollama:11434
```

**Cost: $0/month (no API fees, just server hosting)**

---

### Scenario 4: Hybrid (Dev=Ollama, Apps=Google)

```powershell
# Local development
$env:LLM_PROVIDER = "ollama"

# When testing apps
$env:LLM_PROVIDER = "google"
$env:GOOGLE_API_KEY = "..."

# When going live
$env:LLM_PROVIDER = "ollama"  # Switch back to free
```

## Docker Configuration

### Environment Variables in docker-compose.yml

```yaml
services:
  ragflow-server:
    environment:
      # Auto-detect (recommended)
      - LLM_PROVIDER=auto
      
      # OpenAI (optional)
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - OPENAI_MODEL=gpt-4o-mini
      
      # Google AI (optional)
      - GOOGLE_API_KEY=${GOOGLE_API_KEY:-}
      - GOOGLE_MODEL=gemini-1.5-flash
      
      # Ollama (access host Ollama)
      - OLLAMA_HOST=http://host.docker.internal:11434
      - OLLAMA_MODEL=llama3.2
      - OLLAMA_EMBED_MODEL=nomic-embed-text
    
    extra_hosts:
      - "host.docker.internal:host-gateway"  # Linux support
```

### Start with Specific Provider

```powershell
# Use Ollama
$env:LLM_PROVIDER = "ollama"
docker-compose up -d

# Use Google AI
$env:LLM_PROVIDER = "google"
$env:GOOGLE_API_KEY = "..."
docker-compose up -d

# Use OpenAI
$env:LLM_PROVIDER = "openai"
$env:OPENAI_API_KEY = "..."
docker-compose up -d
```

## API Endpoint

### Check Active Provider

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "graphiti_available": true,
  "llm_provider": "ollama",
  "llm_model": "llama3.2",
  "embeddings_model": "nomic-embed-text",
  "neo4j_uri": "bolt://ragflow-neo4j:7687",
  "supabase_configured": true,
  "timestamp": "2025-10-16T18:30:00"
}
```

## Cost Comparison

### Monthly Usage Estimate (Moderate Use)

| Operation | OpenAI | Google AI | Ollama |
|-----------|--------|-----------|--------|
| Ingest 100 docs | $0.50 | $0.20 | **FREE** |
| 1000 queries | $2.00 | $0.80 | **FREE** |
| Entity extraction | $10.00 | $4.00 | **FREE** |
| Embeddings | $0.20 | $0.10 | **FREE** |
| **TOTAL/month** | **$12.70** | **$5.10** | **$0.00** |

### Break-Even Analysis

- **OpenAI**: Avoid if possible (3x more expensive than Google)
- **Google AI**: Good for testing, $2-10/mo
- **Ollama**: Always free, one-time 2GB download

**Recommendation:** Use Ollama everywhere except when you specifically need cloud features.

## Troubleshooting

### Provider Not Detected

```powershell
# Check health endpoint
curl http://localhost:5000/health

# Verify Ollama is running
curl http://localhost:11434/api/tags

# Check environment variables
Get-ChildItem Env: | Where-Object {$_.Name -like "*LLM*" -or $_.Name -like "*OLLAMA*" -or $_.Name -like "*GOOGLE*"}
```

### Ollama Models Not Found

```powershell
# List installed models
ollama list

# Pull if missing
ollama pull llama3.2
ollama pull nomic-embed-text
```

### Docker Can't Access Host Ollama

```yaml
# Add to docker-compose.yml
services:
  ragflow-server:
    environment:
      - OLLAMA_HOST=http://host.docker.internal:11434
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

### Google AI Quota Error

```
Error: "Quota exceeded" or "API key invalid"

Solutions:
1. Check API key: https://makersuite.google.com/app/apikey
2. Enable billing: https://console.cloud.google.com/billing
3. Or switch to Ollama: $env:LLM_PROVIDER = "ollama"
```

## Migration Path

### From OpenAI to Ollama

```powershell
# 1. Install Ollama and pull models
ollama pull llama3.2
ollama pull nomic-embed-text

# 2. Switch provider
$env:LLM_PROVIDER = "ollama"

# 3. Restart Docker
docker-compose restart

# 4. Remove OpenAI key (optional)
Remove-Item Env:OPENAI_API_KEY
```

**Savings: $5-20/month → $0/month**

### From Google AI to Ollama

```powershell
# Same as above - Ollama replaces any cloud provider
$env:LLM_PROVIDER = "ollama"
```

**Savings: $2-10/month → $0/month**

## Best Practices

1. **Default to auto-detection**
   ```powershell
   LLM_PROVIDER=auto
   ```

2. **Use Ollama for development**
   - Free, fast, private
   - Install once, use forever

3. **Use Google AI for testing**
   - Cheaper than OpenAI
   - Good quality

4. **Use Ollama for production**
   - Zero API costs
   - Predictable performance
   - No rate limits

5. **Keep API keys as fallback**
   ```powershell
   # Even if using Ollama, keep keys for flexibility
   GOOGLE_API_KEY=...  # Fallback if Ollama issues
   ```

## Next Steps

1. **Setup Ollama**: Run `./setup_ollama.ps1`
2. **Test**: `python test_graphiti.py`
3. **Deploy**: Use same Ollama setup in production
4. **Save money**: Cancel OpenAI subscription 💰

## Resources

- **Ollama Setup**: `OLLAMA_GUIDE.md`
- **Google AI**: https://makersuite.google.com/
- **OpenAI**: https://platform.openai.com/
- **RAGFlow Slim with Graphiti Integration Docs**: `GRAPHITI_INTEGRATION.md`
