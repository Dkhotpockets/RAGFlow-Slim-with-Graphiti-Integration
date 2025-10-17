# Graphiti Integration - Quick Start

## What's New?

Your RAGFlow Slim Graphs project now has **temporal knowledge graph** capabilities powered by [Graphiti](https://github.com/getzep/graphiti)! 🎉

### Before (Vector-only RAG):

```
### Before (Vector-only RAG):

```text
Documents → Vector Embeddings → Similarity Search
```
```

### After (Hybrid RAG with Knowledge Graphs)

```text
Documents → Vector Embeddings + Entity/Relationship Extraction
          ↓                    ↓
    Similarity Search    Knowledge Graph Search
          ↓                    ↓
        Combined Results with Temporal Context
```

## Quick Setup (5 minutes)

### 1. Set Your OpenAI API Key

```powershell
# PowerShell (Windows)
$env:OPENAI_API_KEY = "sk-your-key-here"

# Or add to .env file
echo 'OPENAI_API_KEY=sk-your-key-here' >> .env
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start All Services

```bash
docker-compose up -d
```

This starts:
- Flask API (port 5000)
- Neo4j Graph DB (ports 7474, 7687)
- MySQL, Redis, MinIO, Elasticsearch

### 4. Run Tests

```bash
python test_graphiti.py
```

If all tests pass ✅, you're ready to go!

## Usage Examples

### Example 1: Ingest a Document

```bash
curl -X POST http://localhost:5000/ingest \
  -H "X-API-KEY: changeme" \
  -F "file=@quarterly_report.pdf"
```

**What happens:**
- PDF is parsed and stored in Supabase (vector DB)
- Entities & relationships are extracted and stored in Neo4j (graph DB)
- You can now search using both vector similarity AND graph relationships

### Example 2: Hybrid Search

```bash
curl -X POST http://localhost:5000/retrieval \
  -H "X-API-KEY: changeme" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main risks mentioned?",
    "top_k": 5
  }'
```

**Returns:**
```json
{
  "vector_results": [
    {"filename": "risk_report.pdf", "snippet": "Key risks include..."}
  ],
  "graph_results": [
    {
      "entity": "Financial Risk",
      "relationships": [
        {"type": "MENTIONED_IN", "target": "Q3 Report"},
        {"type": "RELATED_TO", "target": "Market Volatility"}
      ]
    }
  ]
}
```

### Example 3: Track Entity Over Time

```bash
curl -X POST http://localhost:5000/graph/temporal \
  -H "X-API-KEY: changeme" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_name": "Customer Satisfaction",
    "start_time": "2025-01-01T00:00:00",
    "end_time": "2025-10-16T23:59:59"
  }'
```

**Shows:** How "Customer Satisfaction" evolved across all your documents over time!

## New API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /ingest` | ⚡ Enhanced with graph extraction |
| `POST /retrieval` | ⚡ Now returns vector + graph results |
| `POST /graph/search` | 🆕 Search entities & relationships |
| `POST /graph/temporal` | 🆕 Track entities over time |

## Real-World Use Cases

### 1. 📊 Financial Analysis
Track how metrics, risks, and strategies evolve across quarterly reports.

### 2. 🚀 Project Management
See relationships between projects, team members, and milestones.

### 3. 👥 Customer Intelligence
Understand customer entities, feedback, and product relationships.

### 4. ⚖️ Legal/Compliance
Track clauses, regulations, and their relationships across documents.

## View Your Knowledge Graph

Open Neo4j Browser: http://localhost:7474
- Username: `neo4j`
- Password: `graphiti_password`

Run queries like:
```cypher
MATCH (n) RETURN n LIMIT 25
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│              RAGFlow Slim Graphs API                   │
│  ┌──────────────────┬──────────────────────┐   │
│  │   Supabase       │      Graphiti        │   │
│  │  (Vector Store)  │   (Knowledge Graph)  │   │
│  │                  │                      │   │
│  │  • Embeddings    │  • Entities          │   │
│  │  • Similarity    │  • Relationships     │   │
│  │  • Fast lookup   │  • Temporal tracking │   │
│  └──────────────────┴──────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## Troubleshooting

### "Graphiti is not available" error
```bash
# Install dependencies
pip install graphiti-core neo4j

# Verify Neo4j is running
docker ps | grep neo4j
```

### OpenAI API errors
```bash
# Check if key is set
echo $env:OPENAI_API_KEY  # PowerShell

# Set it if missing
$env:OPENAI_API_KEY = "sk-your-key-here"
```

### Neo4j connection issues
```bash
# Check Neo4j logs
docker logs ragflow-slim-graphs-neo4j

# Restart Neo4j
docker-compose restart ragflow-slim-graphs-neo4j
```

## Performance Tips

- **Document size**: Limited to 10k characters for graph extraction (adjustable)
- **Processing time**: 3-10 seconds per document (LLM-powered extraction)
- **Neo4j memory**: Default 2GB, increase for large graphs (100k+ nodes)

## Full Documentation

See [GRAPHITI_INTEGRATION.md](./GRAPHITI_INTEGRATION.md) for:
- Detailed API documentation
- Python client examples
- Configuration options
- Advanced use cases

## Next Steps

1. ✅ Run `python test_graphiti.py` to verify setup
2. 📄 Ingest some test documents
3. 🔍 Try hybrid search with `/retrieval`
4. 📊 Explore the graph in Neo4j Browser
5. 🚀 Build amazing RAG applications!

---

**Questions?** Check out:
- [Graphiti GitHub](https://github.com/getzep/graphiti)
- [Neo4j Docs](https://neo4j.com/docs/)
- [RAGFlow Slim Graphs Issues](./CONTRIBUTOR_GUIDE.md)
