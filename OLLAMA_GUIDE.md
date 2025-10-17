# Using Ollama with RAGFlow Slim with Graphiti Integration

## Why Ollama?

✅ **100% Free** - No API costs, no usage limits  
✅ **Privacy** - All processing happens locally  
✅ **Offline** - Works without internet connection  
✅ **Fast** - Low latency for local models  
✅ **Production Ready** - Can deploy same setup in production  

## Quick Start (5 Minutes)

### 1. Install Ollama

**Windows:**
```powershell
# Download from: https://ollama.ai/download/windows
# Or use winget:
winget install Ollama.Ollama
```

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Pull Required Models

```powershell
# LLM for entity extraction and reasoning (required)
ollama pull llama3.2

# Embedding model for vector search (required)
ollama pull nomic-embed-text

# Optional: Larger model for better quality
ollama pull llama3.1
```

### 3. Start Ollama Service

**Ollama runs automatically in the background after installation.**

Verify it's running:
```powershell
ollama list
```

### 4. Configure RAGFlow Slim with Graphiti Integration to Use Ollama

**Option A: Set environment variable (recommended)**
```powershell
$env:LLM_PROVIDER = "ollama"
```

**Option B: Use auto-detection**
```powershell
# RAGFlow Slim with Graphiti Integration will automatically detect Ollama if running
$env:LLM_PROVIDER = "auto"
```

### 5. Test It!

```powershell
# Start Docker services
docker-compose up -d

# Run tests
python test_graphiti.py
```

## Configuration

### Environment Variables

```bash
# .env file or PowerShell
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_EMBED_MODEL=nomic-embed-text
```

### Available Models

| Model | Size | Use Case | Download Command |
|-------|------|----------|------------------|
| **llama3.2** | 2GB | Fast, efficient, good quality | `ollama pull llama3.2` |
| **llama3.1** | 4.7GB | Better quality, slower | `ollama pull llama3.1` |
| **mistral** | 4.1GB | Alternative LLM | `ollama pull mistral` |
| **phi3** | 2.3GB | Microsoft's efficient model | `ollama pull phi3` |
| **nomic-embed-text** | 274MB | Embeddings (required) | `ollama pull nomic-embed-text` |

### Recommended Setups

**Development (Fast, Low RAM):**
```bash
OLLAMA_MODEL=llama3.2        # 2GB
OLLAMA_EMBED_MODEL=nomic-embed-text  # 274MB
Total: ~2.3GB RAM
```

**Production (Better Quality):**
```bash
OLLAMA_MODEL=llama3.1        # 4.7GB
OLLAMA_EMBED_MODEL=nomic-embed-text  # 274MB
Total: ~5GB RAM
```

## Docker Setup

### Running Ollama Alongside RAGFlow Slim with Graphiti Integration

**Option 1: Ollama on Host (Recommended for Development)**

```yaml
# docker-compose.yml - RAGFlow Slim with Graphiti Integration can access host Ollama
environment:
  - LLM_PROVIDER=ollama
  - OLLAMA_HOST=http://host.docker.internal:11434
```

**Option 2: Ollama in Docker**

```yaml
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

volumes:
  ollama-data:
```

Then pull models:
```powershell
docker exec -it ollama ollama pull llama3.2
docker exec -it ollama ollama pull nomic-embed-text
```

## Performance Comparison

### RAGFlow Slim with Graphiti Integration Operations Cost/Speed

| Operation | OpenAI (Cost) | Google AI (Cost) | Ollama (Speed) |
|-----------|---------------|------------------|----------------|
| Ingest 10 pages | $0.05 | $0.02 | 5-10 sec (FREE) |
| Extract entities | $0.10 | $0.04 | 8-15 sec (FREE) |
| 100 queries | $0.20 | $0.08 | 3-5 min (FREE) |
| **Monthly (moderate use)** | **$5-20** | **$2-10** | **$0** |

### Latency Comparison

| Provider | Average Response Time |
|----------|----------------------|
| **Ollama (local)** | 0.5-2 seconds |
| **OpenAI** | 1-3 seconds + network |
| **Google AI** | 1-3 seconds + network |

## Multi-App Deployment Strategy

### Scenario: Multiple Apps Using RAGFlow Slim with Graphiti Integration

```
┌─────────────────────────────────────────────────────┐
│                  Your Architecture                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐     ┌──────────────┐             │
│  │  App 1       │     │  App 2       │             │
│  │  (Testing)   │     │  (Testing)   │             │
│  └──────┬───────┘     └──────┬───────┘             │
│         │ LLM_PROVIDER=google │                     │
│         └─────────┬───────────┘                     │
│                   │                                  │
│         ┌─────────▼──────────┐                      │
│         │   RAGFlow Slim with Graphiti Integration     │                      │
│         │   (Multi-Provider) │                      │
│         └─────────┬──────────┘                      │
│                   │                                  │
│    ┌──────────────┼──────────────┐                 │
│    │              │               │                 │
│    ▼              ▼               ▼                 │
│ ┌────────┐  ┌─────────┐    ┌─────────┐            │
│ │ Ollama │  │Google AI│    │ OpenAI  │            │
│ │ (Local)│  │ (Cloud) │    │ (Cloud) │            │
│ │  FREE  │  │  $2-10  │    │ $5-20   │            │
│ └────────┘  └─────────┘    └─────────┘            │
│                                                      │
│  Production: All apps → Ollama (FREE)               │
└─────────────────────────────────────────────────────┘
```

### Configuration Per Environment

**Development (Local):**
```bash
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
```

**Testing Apps (Google AI):**
```bash
LLM_PROVIDER=google
GOOGLE_API_KEY=AIzaSy...your-key
```

**Production (All Local):**
```bash
LLM_PROVIDER=ollama
OLLAMA_HOST=http://ollama-server:11434
# Deploy Ollama on dedicated server for all apps to share
```

## Troubleshooting

### Ollama Not Detected

```powershell
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

### "Model not found" Error

```powershell
# List installed models
ollama list

# Pull missing model
ollama pull llama3.2
ollama pull nomic-embed-text
```

### Slow Performance

```bash
# Use smaller model
OLLAMA_MODEL=llama3.2  # Instead of llama3.1

# Or reduce context window
OLLAMA_MAX_TOKENS=4096  # Default is 8192
```

### Docker Can't Access Ollama

```bash
# Use host.docker.internal instead of localhost
OLLAMA_HOST=http://host.docker.internal:11434

# On Linux, add to docker-compose.yml:
extra_hosts:
  - "host.docker.internal:host-gateway"
```

## Best Practices

### 1. **Use Ollama for Development**
- Zero cost
- Fast iteration
- No API key management

### 2. **Use Google AI for App Testing**
- Cheaper than OpenAI ($2-10/mo vs $5-20/mo)
- Good quality
- Easy to switch to Ollama later

### 3. **Use Ollama for Production**
- Deploy once, serve all apps
- No per-request costs
- Better privacy
- Predictable performance

### 4. **Keep Auto-Detection Enabled**
```bash
LLM_PROVIDER=auto
# Set API keys you have, Ollama will be used if available
```

## Next Steps

1. **Install Ollama**: https://ollama.ai
2. **Pull models**: `ollama pull llama3.2 && ollama pull nomic-embed-text`
3. **Set env var**: `$env:LLM_PROVIDER = "ollama"`
4. **Test**: `python test_graphiti.py`
5. **Deploy**: Use same Ollama setup in production

## Resources

- **Ollama Website**: https://ollama.ai
- **Model Library**: https://ollama.ai/library
- **Ollama GitHub**: https://github.com/ollama/ollama
- **RAGFlow Slim with Graphiti Integration Docs**: See `GRAPHITI_INTEGRATION.md`
