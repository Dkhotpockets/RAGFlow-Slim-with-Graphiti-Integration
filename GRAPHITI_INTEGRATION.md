# Graphiti Integration Guide

## Overview

This RAGFlow Slim Graphs project now integrates **Graphiti** - a temporal knowledge graph library that automatically extracts entities, relationships, and tracks how they evolve over time. This enhances your RAG system with:

- **Entity & Relationship Extraction**: Automatic extraction from documents
- **Temporal Tracking**: See how information changes over time
- **Graph-based Search**: Query based on relationships, not just vector similarity
- **Hybrid Retrieval**: Combine vector search (Supabase) with graph search (Neo4j)

## Architecture

```text
┌─────────────────┐
│   Documents     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      RAGFlow Slim Graphs API               │
│  ┌──────────────┬────────────────┐  │
│  │   Supabase   │    Graphiti    │  │
│  │ (Vector DB)  │  (Graph DB)    │  │
│  └──────────────┴────────────────┘  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Hybrid Results:                    │
│  - Vector similarity matches        │
│  - Entity/relationship context      │
│  - Temporal evolution               │
└─────────────────────────────────────┘
```

## Setup

### 1. Install Dependencies

First, install the new requirements:

```bash
pip install -r requirements.txt
```

Or compile from requirements.in:

```bash
pip-compile requirements.in
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Set your OpenAI API key (required for Graphiti's LLM-based extraction):

```bash
# PowerShell
$env:OPENAI_API_KEY = "sk-your-key-here"

# Or add to .env file
OPENAI_API_KEY=sk-your-key-here
```

### 3. Start Services with Docker Compose

The docker-compose.yml now includes Neo4j:

```bash
docker-compose up -d
```

This will start:

- **ragflow-server** (Flask API on port 5000)
- **ragflow-neo4j** (Neo4j on ports 7474/7687)
- **ragflow-mysql**, **ragflow-redis**, **ragflow-minio**, **ragflow-es-01**

### 4. Verify Neo4j is Running

Access Neo4j Browser at: <http://localhost:7474>

- Username: `neo4j`
- Password: `graphiti_password`

## API Endpoints

### Enhanced Endpoints

#### POST `/ingest`

Now stores documents in **both** Supabase (vector) and Graphiti (graph).

**Request:**

```bash
curl -X POST http://localhost:5000/ingest \
  -H "X-API-KEY: changeme" \
  -F "file=@document.pdf"
```

**Response:**

```json
{
  "status": "success",
  "supabase_response": { ... },
  "graph_response": {
    "status": "success",
    "episode_name": "document.pdf_a1b2c3d4",
    "timestamp": "2025-10-16T10:30:00"
  }
}
```

#### POST `/retrieval`

Now returns **both** vector results and graph results.

**Request:**

```bash
curl -X POST http://localhost:5000/retrieval \
  -H "X-API-KEY: changeme" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What did the CEO announce about Q4?",
    "top_k": 5
  }'
```

**Response:**

```json
{
  "vector_results": [
    {
      "doc_id": "123",
      "filename": "earnings_report.pdf",
      "snippet": "CEO announced strong Q4 performance..."
    }
  ],
  "graph_results": [
    {
      "entity": "CEO",
      "relationship": "ANNOUNCED",
      "target": "Q4 Performance",
      "timestamp": "2025-10-16T10:00:00"
    }
  ]
}
```

### New Graph-Specific Endpoints

#### POST `/graph/search`
Search the knowledge graph for entities and relationships.

**Request:**
```bash
curl -X POST http://localhost:5000/graph/search \
  -H "X-API-KEY: changeme" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who are the executives mentioned?",
    "num_results": 10
  }'
```

**Response:**
```json
{
  "results": [
    {
      "entity_name": "John Smith",
      "entity_type": "Person",
      "relationships": [
        {
          "type": "WORKS_FOR",
          "target": "Acme Corp"
        }
      ]
    }
  ],
  "count": 10
}
```

#### POST `/graph/temporal`
Get temporal context showing how an entity evolved over time.

**Request:**
```bash
curl -X POST http://localhost:5000/graph/temporal \
  -H "X-API-KEY: changeme" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_name": "Project Alpha",
    "start_time": "2025-01-01T00:00:00",
    "end_time": "2025-10-16T23:59:59"
  }'
```

**Response:**
```json
{
  "entity": "Project Alpha",
  "time_range": {
    "start": "2025-01-01T00:00:00",
    "end": "2025-10-16T23:59:59"
  },
  "results": [
    {
      "timestamp": "2025-01-15T10:00:00",
      "event": "Project Alpha initiated",
      "relationships": [...]
    },
    {
      "timestamp": "2025-06-01T14:30:00",
      "event": "Project Alpha milestone reached",
      "relationships": [...]
    }
  ]
}
```

## Python Client Examples

### Example 1: Ingest with Graph Extraction

```python
import requests

url = "http://localhost:5000/ingest"
headers = {"X-API-KEY": "changeme"}

with open("meeting_notes.txt", "rb") as f:
    files = {"file": f}
    response = requests.post(url, headers=headers, files=files)
    print(response.json())
```

### Example 2: Hybrid Search

```python
import requests

url = "http://localhost:5000/retrieval"
headers = {
    "X-API-KEY": "changeme",
    "Content-Type": "application/json"
}
data = {
    "query": "What are the risks mentioned in the financial report?",
    "top_k": 5
}

response = requests.post(url, headers=headers, json=data)
results = response.json()

print("Vector Results:", results["vector_results"])
print("Graph Results:", results["graph_results"])
```

### Example 3: Track Entity Over Time

```python
import requests
from datetime import datetime, timedelta

url = "http://localhost:5000/graph/temporal"
headers = {
    "X-API-KEY": "changeme",
    "Content-Type": "application/json"
}

# Track "Customer Satisfaction" over last 6 months
end_time = datetime.now()
start_time = end_time - timedelta(days=180)

data = {
    "entity_name": "Customer Satisfaction",
    "start_time": start_time.isoformat(),
    "end_time": end_time.isoformat()
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

## Use Cases

### 1. Financial Analysis
Track how financial metrics, risks, and strategies evolve across quarterly reports:

```python
# Ingest Q1, Q2, Q3, Q4 reports
# Query: "How has the company's debt position changed?"
# -> Graph shows temporal progression of debt-related entities
```

### 2. Project Management
Track project entities, milestones, and team members across meeting notes:

```python
# Ingest weekly meeting notes
# Query: "What were the blockers for Project X?"
# -> Graph shows relationships between project, blockers, and team members
```

### 3. Customer Intelligence
Track customer mentions, feedback, and relationships across communications:

```python
# Ingest customer emails, support tickets
# Query: "What are the main complaints from Enterprise customers?"
# -> Graph shows customer entities, their complaints, and product features
```

### 4. Legal/Compliance
Track entities, clauses, and relationships in legal documents:

```python
# Ingest contracts, policies
# Query: "Which contracts mention data retention?"
# -> Graph shows contracts, data retention clauses, and related entities
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `password` |
| `GRAPHITI_LLM_PROVIDER` | LLM provider for extraction | `openai` |
| `OPENAI_API_KEY` | OpenAI API key | (required) |

### Docker Override

To use custom Neo4j settings, create `docker-compose.override.yml`:

```yaml
version: '3.8'
services:
  ragflow-slim-graphs-neo4j:
    environment:
      - NEO4J_AUTH=neo4j/my_custom_password
      - NEO4J_dbms_memory_heap_max__size=4G
```

## Troubleshooting

### Graphiti Not Available
If you see "Graphiti is not available" errors:

1. Check if graphiti-core is installed:
   ```bash
   pip list | grep graphiti
   ```

2. Verify Neo4j is running:
   ```bash
   docker ps | grep neo4j
   ```

3. Check logs:
   ```bash
   docker logs ragflow-slim-graphs-neo4j
   ```

### OpenAI API Issues
Graphiti uses OpenAI for entity extraction. Ensure:

1. `OPENAI_API_KEY` is set
2. API key has credits available
3. Check rate limits if processing large documents

### Neo4j Connection Issues
If connection fails:

1. Verify Neo4j is running on port 7687
2. Check credentials match environment variables
3. Ensure Docker network connectivity

## Performance Considerations

### Document Size Limits
- Graphiti processes are limited to 10,000 characters per document
- For larger documents, consider chunking before ingestion

### Processing Time
- Graph extraction is LLM-powered and takes longer than vector embedding
- Expect 3-10 seconds per document depending on size
- Consider async processing for production workloads

### Neo4j Resources
- Default heap size: 2GB (adjust via `NEO4J_dbms_memory_heap_max__size`)
- Consider increasing for large knowledge graphs (>100k nodes)

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set OpenAI API key**: `export OPENAI_API_KEY=sk-...`
3. **Start services**: `docker-compose up -d`
4. **Test ingestion**: Upload a document via `/ingest`
5. **Test retrieval**: Query via `/retrieval` and see hybrid results
6. **Explore graph**: Use `/graph/search` and `/graph/temporal`

## Additional Resources

- [Graphiti Documentation](https://github.com/getzep/graphiti)
- [Neo4j Browser Guide](https://neo4j.com/docs/browser-manual/current/)
- [RAGFlow Slim Graphs API Docs](./openapi.yaml)
