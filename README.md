# RAGFlow Slim with Graphiti Integration

A lightweight, hybrid RAG (Retrieval-Augmented Generation) system that combines
vector search with temporal knowledge graphs for enhanced document
understanding and retrieval.

## 🎯 Overview

RAGFlow Slim with Graphiti Integration is a streamlined version of RAGFlow that
integrates Graphiti's temporal knowledge graph capabilities. This hybrid system
provides:

- **Vector Search**: Fast similarity-based document retrieval using Supabase
- **Knowledge Graph**: Entity extraction, relationship mapping, and temporal
   tracking using Neo4j + Graphiti
- **Multi-Provider LLM Support**: Google Gemini, Ollama, and other
   providers
- **RESTful API**: Clean endpoints for document ingestion, retrieval, and graph
   queries

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for local development)
- API keys for your preferred LLM providers

### Using Docker Compose

1. **Clone the repository**

   ```bash
   git clone https://github.com/Dkhotpockets/RAGFlow-Slim-with-Graphiti-Integration.git
   cd ragflow-slim-graphs
   ```

2. **Configure environment variables**

   ```bash
   # Copy and edit environment variables
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the services**

   ```bash
   docker-compose up -d
   ```

4. **Verify the setup**

   ```bash
   curl http://localhost:5000/health
   ```

The API will be available at `http://localhost:5000`.

### Local Development

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**

   ```bash
   export SUPABASE_URL="your-supabase-url"
   export SUPABASE_KEY="your-supabase-key"
   export GOOGLE_API_KEY="your-google-api-key"
   # ... other required variables
   ```

3. **Run the application**

   ```bash
   python app.py
   ```

## 🏗️ Architecture

```text
Documents
    ↓
RAGFlow Slim with Graphiti Integration API
    ├─→ Supabase (Vector Store)
    │   └─→ Fast similarity search
    │
    └─→ Neo4j + Graphiti (Graph Store)
        └─→ Entity extraction, relationship mapping, temporal tracking
```

### Services

- **ragflow-server**: Main Flask API server
- **ragflow-mysql**: MySQL database for metadata
- **ragflow-redis**: Redis for caching
- **ragflow-minio**: MinIO for file storage
- **ragflow-es-01**: Elasticsearch for search indexing
- **ragflow-neo4j**: Neo4j graph database for knowledge graph

## 📡 API Endpoints

### Core Endpoints

- `GET /health` - Health check
- `GET /config` - List configuration files
- `POST /completion` - Generate text completions
- `POST /ingest` - Ingest documents (extracts entities and relationships)
- `POST /retrieval` - Retrieve documents (combines vector and graph results)

### Graph Endpoints

- `POST /graph/search` - Search the knowledge graph for entities/relationships
- `POST /graph/temporal` - Track how entities evolved over time

### Example Usage

```python
import requests

# Health check
response = requests.get("http://localhost:5000/health")
print(response.json())

# Ingest a document
data = {
    "content": "Your document content here...",
    "metadata": {"source": "example.txt"}
}
response = requests.post("http://localhost:5000/ingest", json=data)

# Retrieve documents
query = {"query": "What is machine learning?"}
response = requests.post("http://localhost:5000/retrieval", json=query)
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_KEY` | Supabase service role key | Yes |
| `NEO4J_URI` | Neo4j connection URI | Yes |
| `NEO4J_USER` | Neo4j username | Yes |
| `NEO4J_PASSWORD` | Neo4j password | Yes |
| `GOOGLE_API_KEY` | Google Gemini API key | For Gemini provider |
| `OLLAMA_HOST` | Ollama server URL | For Ollama provider |

### LLM Providers

The system supports multiple LLM providers:

- **Google Gemini**: Primary for entity extraction and general completions
- **Ollama**: Local LLM support for embeddings and completions
- **OpenAI**: Compatible with OpenAI API format

Configure the provider using `LLM_PROVIDER` environment variable.

## 🔧 Development

### Project Structure

```text
├── app.py                 # Main Flask application
├── graphiti_client.py     # Graphiti integration
├── supabase_client.py     # Supabase vector operations
├── llm_provider.py        # Multi-provider LLM client
├── docker-compose.yml     # Service orchestration
├── requirements.txt       # Python dependencies
├── graphiti_source/       # Graphiti library
├── docker/               # Docker configuration
└── docs/                 # Documentation
```

### Testing

Run the test suite:

```bash
python -m pytest test_*.py
```

### Running contract/integration tests (CI)

Contract and integration tests that hit external services (Graphiti, Supabase,
LLM providers) are run conditionally in CI.

- Locally: run all tests including contract-marked ones:

```powershell
# Run contract/integration tests locally
pytest -q -m contract
```

- On GitHub Actions: trigger the `CI` workflow with `workflow_dispatch` and set
   the `run_contracts` input to `true` when you want the contract suite.

This avoids running long or environment-dependent tests on every push while
allowing a dedicated contract test run when desired.


### Adding New Features

1. Create a feature branch
2. Add tests for new functionality
3. Update documentation
4. Submit a pull request

## 📚 Documentation

- [Graphiti Integration Guide](GRAPHITI_INTEGRATION.md)
- [Graphiti Quick Start](GRAPHITI_QUICKSTART.md)
- [LLM Provider Setup](LLM_PROVIDER_GUIDE.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [Ollama Integration](OLLAMA_GUIDE.md)
- [Contributor Guide](CONTRIBUTOR_GUIDE.md)

## 🤝 Contributing

We welcome contributions!
See the [Contributor Guide](CONTRIBUTOR_GUIDE.md) for details on:

- Setting up a development environment
- Code standards and practices
- Submitting pull requests
- Reporting issues

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [RAGFlow](https://github.com/infiniflow/ragflow) - Original RAG system
- [Graphiti](https://github.com/getzep/graphiti) - Temporal knowledge graph library
- [Supabase](https://supabase.com) - Vector database and backend services
- [Neo4j](https://neo4j.com) - Graph database
