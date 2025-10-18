# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RAGFlow Slim with Graphiti and Crawl4AI Integration is a hybrid RAG system that combines web crawling, vector search, and temporal knowledge graphs for enhanced document understanding and retrieval. It integrates:

- **Vector Search**: Supabase for fast similarity-based document retrieval
- **Knowledge Graph**: Neo4j + Graphiti for entity extraction, relationship mapping, and temporal tracking
- **Web Crawling**: Crawl4AI for intelligent web scraping and content extraction
- **Multi-Provider LLM**: Supports Google Gemini, Ollama, and OpenAI

## Common Development Commands

### Running the Application

**Local Development:**
```bash
pip install -r requirements.txt
python app.py
```

**Docker Compose (Recommended):**
```bash
docker-compose up -d
```

**Health Check:**
```bash
curl http://localhost:5000/health
```

### Testing

**Run all tests:**
```bash
python -m pytest
```

**Run contract/integration tests (require external services):**
```bash
pytest -q -m contract
```

**Run specific test file:**
```bash
python test_app.py
```

**Test markers:**
- `@pytest.mark.contract`: Tests that hit external services (Graphiti, Supabase, LLM providers)

### Environment Setup

Copy `.env.example` to `.env` and configure:
- Supabase credentials (SUPABASE_URL, SUPABASE_KEY)
- Neo4j connection (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
- LLM provider (LLM_PROVIDER: auto/ollama/google/openai)
- API keys for chosen LLM provider

## Architecture

### Core Components

**1. Flask API Server (app.py)**
- Main application entry point
- RESTful endpoints for completion, ingestion, retrieval, graph operations, and crawling
- Authentication via X-API-KEY header
- Rate limiting (100 requests/hour/IP)

**2. Hybrid Storage System**

The system uses a dual-storage approach:
- **Supabase (supabase_client.py)**: Vector embeddings for similarity search
- **Neo4j + Graphiti (graphiti_client.py)**: Temporal knowledge graph for entity/relationship extraction

When documents are ingested:
1. Embeddings are stored in Supabase for vector search
2. Content is processed by Graphiti to extract entities/relationships and store in Neo4j
3. Retrieval combines both vector search and graph traversal for richer context

**3. Multi-Provider LLM Support (llm_provider.py)**

Auto-detection logic (priority order):
1. Ollama (local, no API key needed)
2. Google Gemini (if GOOGLE_API_KEY set)
3. OpenAI (if OPENAI_API_KEY set)

**Important for Graphiti:**
- Graphiti requires structured outputs for entity extraction
- When using Ollama as primary provider, the system automatically uses OpenAI for Graphiti's LLM operations (entity extraction) while using Ollama for embeddings to minimize costs
- Google Gemini fully supports Graphiti with GeminiClient and GeminiRerankerClient

**4. Crawl4AI Integration (crawl4ai_source/)**

Provides web crawling capabilities:
- **manager.py**: Job management and orchestration
- **service.py**: Core crawling service using Crawl4AI
- **rate_limiter.py**: Rate limiting for crawl requests
- **deduplicator.py**: Content deduplication using hashing

Crawl jobs are stored in Supabase and support stateful lifecycle (pending → running → completed/failed/cancelled).

### Key Files

- **app.py**: Main Flask application with all API endpoints
- **graphiti_client.py**: Graphiti integration for temporal knowledge graphs
- **supabase_client.py**: Supabase vector operations
- **llm_provider.py**: Multi-provider LLM configuration and auto-detection
- **crawl4ai_source/**: Complete Crawl4AI integration module
- **graphiti_source/**: Embedded Graphiti library (temporal knowledge graph)

### Data Flow

**Document Ingestion:**
```
User uploads file →
  → Supabase: Store embeddings for vector search
  → Graphiti: Extract entities/relationships → Neo4j graph storage
```

**Retrieval:**
```
User query →
  → Vector search in Supabase (similarity-based)
  → Graph search in Graphiti (entity/relationship-based)
  → Combined results returned
```

**Web Crawling:**
```
User creates crawl job →
  → Job stored in Supabase (pending status)
  → Start job → Crawl4AI extracts content
  → Content stored with metadata, links, and content hash
  → Job status updated (completed/failed)
```

## API Endpoints

### Core Endpoints
- `GET /health` - Health check with provider info
- `POST /completion` - Generate text completions
- `POST /ingest` - Ingest documents (TXT/PDF) into both Supabase and Graphiti
- `POST /retrieval` - Retrieve documents (combines vector + graph results)

### Graph Endpoints
- `POST /graph/search` - Search knowledge graph for entities/relationships
- `POST /graph/temporal` - Track entity evolution over time

### Crawl Endpoints
- `POST /crawl` - Create new crawl job
- `GET /crawl/<job_id>` - Get crawl job status and results
- `GET /crawl` - List crawl jobs (with optional status filter)
- `POST /crawl/<job_id>/start` - Start pending crawl job
- `POST /crawl/<job_id>/cancel` - Cancel running/pending crawl job

All endpoints require authentication via `X-API-KEY` header (default: "changeme").

## Development Guidelines

### Adding New Features

1. **New API Endpoints**: Add to `app.py` following existing patterns (authentication, rate limiting, error handling)
2. **LLM Provider Support**: Extend `llm_provider.py` with new provider detection and configuration
3. **Graph Operations**: Add functions to `graphiti_client.py` using async/await pattern with sync wrappers
4. **Vector Operations**: Extend `supabase_client.py` for new Supabase operations

### Testing Considerations

- Contract tests (`@pytest.mark.contract`) require external services to be running:
  - Neo4j for Graphiti tests
  - Supabase for vector store tests
  - LLM provider API keys for integration tests
- In CI, contract tests run conditionally via GitHub Actions workflow_dispatch
- Local testing can use Docker Compose to spin up Neo4j, MySQL, Redis, etc.

### Security and Safety

- All file operations use path sanitization (`_is_safe_path()`)
- API key authentication required for all endpoints
- Rate limiting enforced per IP
- Outputs written to dedicated `outputs/` directory
- Non-root user in Docker container
- Logging to `runtime.log` (configurable via RAGFLOW_LOG_FILE)

### Configuration Files

The system supports loading bootstrap configuration files from `RAGFLOW_CONFIG_DIR` (default: `/data/application`):
- Supports app-specific subdirectories (e.g., `/data/application/myapp/`)
- Can be mounted as Docker volume for external configuration
- Accessible via `/config` endpoint (authenticated)

### Graphiti Schema Initialization

The database schema is initialized on first episode addition (idempotent operation in `add_episode_async()`). This creates necessary Neo4j indices and constraints for:
- Entity nodes with embeddings
- Relationship edges with temporal tracking
- Episode metadata

## Docker Services

When running via `docker-compose.yml`, the following services are available:

- **ragflow-server** (port 5000): Main Flask API
- **ragflow-mysql** (port 3306): MySQL for metadata
- **ragflow-redis** (port 6379): Redis for caching
- **ragflow-minio** (ports 9000, 9001): MinIO for file storage
- **ragflow-es-01** (ports 9200, 9300): Elasticsearch for search indexing
- **ragflow-neo4j** (ports 7474, 7687): Neo4j graph database

The server service uses `host.docker.internal:host-gateway` to access host-based Ollama installations.

## Important Notes

- **Ollama + Graphiti**: When using Ollama as primary provider, OpenAI is required for Graphiti's entity extraction (uses structured outputs). Set both OLLAMA_HOST and OPENAI_API_KEY to use Ollama for embeddings + OpenAI for graph operations.
- **Async Operations**: Graphiti uses async/await. All graphiti_client functions have both async and sync versions (sync versions use `asyncio.new_event_loop()`).
- **Episode Management**: Each document ingested creates a unique "episode" in the knowledge graph with temporal tracking.
- **Crawl Jobs**: Crawl jobs are asynchronous and stateful. Always check job status before retrieving results.
- **Content Deduplication**: Crawl4AI uses SHA256 hashing for content deduplication.
