# Migration Guide: Adding Graphiti to Existing RAGFlow Slim Graphs

If you have an existing RAGFlow Slim Graphs installation, follow these steps to add Graphiti support.

## Prerequisites

- Existing RAGFlow Slim Graphs installation
- Docker and Docker Compose
- OpenAI API key (for entity extraction)

## Step-by-Step Migration

### Step 1: Backup Your Data (Recommended)

```powershell
# Backup Supabase data (if needed)
# Backup outputs folder
Copy-Item -Path ".\outputs" -Destination ".\outputs.backup" -Recurse
```

### Step 2: Update Requirements

Add these lines to your `requirements.in`:
```
graphiti-core
neo4j
flask-cors
```

Then regenerate and install:
```bash
pip-compile requirements.in
pip install -r requirements.txt
```

### Step 3: Add Neo4j to Docker Compose

Add to your `docker-compose.yml` services section:

```yaml
  ragflow-slim-graphs-neo4j:
    image: neo4j:5.15.0
    container_name: ragflow-slim-graphs-neo4j
    restart: unless-stopped
    environment:
      - NEO4J_AUTH=neo4j/graphiti_password
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
      - NEO4J_dbms_memory_heap_max__size=2G
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    volumes:
      - neo4j-data:/data
      - neo4j-logs:/logs
```

Add volumes at the end:
```yaml
volumes:
  neo4j-data:
  neo4j-logs:
```

Update `ragflow-slim-graphs-server` service to depend on Neo4j:
```yaml
  ragflow-slim-graphs-server:
    # ... existing config ...
    depends_on:
      # ... existing dependencies ...
      - ragflow-slim-graphs-neo4j
    environment:
      # ... existing env vars ...
      - NEO4J_URI=bolt://ragflow-slim-graphs-neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=graphiti_password
      - GRAPHITI_LLM_PROVIDER=openai
      - OPENAI_API_KEY=${OPENAI_API_KEY:-your_openai_key_here}
```

### Step 4: Add Graphiti Client Module

Copy the `graphiti_client.py` file to your project root.

### Step 5: Update app.py

Add import at the top of `app.py`:
```python
from graphiti_client import (
    add_episode, 
    search_graph, 
    get_temporal_context,
    GRAPHITI_AVAILABLE
)
```

Update the `/ingest` endpoint to add graph extraction:
```python
# After the line: response = add_document_to_supabase(...)
# Add:
graph_result = {}
if GRAPHITI_AVAILABLE:
    episode_name = f"{filename}_{uuid.uuid4().hex[:8]}"
    graph_result = add_episode(
        name=episode_name,
        episode_body=text[:10000],
        source_description=f"Document: {filename}",
        episode_type="text"
    )
    logging.info(f"Added document to knowledge graph: {graph_result}")

# Update return to include graph_result:
return jsonify({
    "status": "success",
    "supabase_response": response,
    "graph_response": graph_result
})
```

Update the `/retrieval` endpoint:
```python
# After: docs = search_documents_supabase(...)
# Add:
graph_results = []
if GRAPHITI_AVAILABLE:
    graph_results = search_graph(query, num_results=5)
    logging.info(f"Graph search returned {len(graph_results)} results")

# Update return:
return jsonify({
    "vector_results": results,
    "graph_results": graph_results
})
```

Add new graph endpoints before `if __name__ == "__main__"`:
```python
@app.route("/graph/search", methods=["POST"])
def graph_search():
    # See full implementation in updated app.py
    pass

@app.route("/graph/temporal", methods=["POST"])
def graph_temporal():
    # See full implementation in updated app.py
    pass
```

### Step 6: Set Environment Variables

```powershell
# PowerShell
$env:OPENAI_API_KEY = "sk-your-key-here"

# Or add to .env file
echo 'OPENAI_API_KEY=sk-your-key-here' >> .env
```

### Step 7: Restart Services

```bash
# Stop existing services
docker-compose down

# Start with new configuration
docker-compose up -d

# Check logs
docker-compose logs -f ragflow-slim-graphs-neo4j
docker-compose logs -f ragflow-slim-graphs-server
```

### Step 8: Verify Installation

```bash
# Run test suite
python test_graphiti.py

# Or manually test
curl -X POST http://localhost:5000/graph/search \
  -H "X-API-KEY: changeme" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

## Backward Compatibility

✅ **Your existing functionality remains unchanged:**

- `/completion` endpoint - unchanged
- `/ingest` endpoint - enhanced but backward compatible
- `/retrieval` endpoint - enhanced but backward compatible
- All existing data in Supabase - untouched

The system gracefully degrades if Graphiti is unavailable - vector search continues to work independently.

## Rolling Back

If you need to revert:

```bash
# Stop services
docker-compose down

# Restore old docker-compose.yml (remove Neo4j service)
git checkout docker-compose.yml  # if using git

# Restore old app.py
git checkout app.py  # if using git

# Restart
docker-compose up -d
```

## Common Issues

### Issue: "Graphiti is not available"

**Solution:**
```bash
pip install graphiti-core neo4j
```

### Issue: Neo4j container won't start

**Solution:**
```bash
# Check logs
docker logs ragflow-slim-graphs-neo4j

# Common fix: Remove existing data
docker-compose down -v
docker-compose up -d
```

### Issue: OpenAI API errors

**Solution:**
```bash
# Verify key is set
echo $env:OPENAI_API_KEY

# Check API key validity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $env:OPENAI_API_KEY"
```

### Issue: Import errors in Python

**Solution:**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt --force-reinstall
```

## Performance Considerations

### Before Migration
- Ingestion: ~1 second per document
- Retrieval: ~100ms

### After Migration
- Ingestion: ~5-10 seconds per document (due to LLM extraction)
- Retrieval: ~200ms (vector + graph search)

**Tip:** Process large document batches during off-hours.

## Data Migration

Existing documents in Supabase are NOT automatically added to the graph. To add them:

1. **Option A - Re-ingest**: Upload documents again via `/ingest`
2. **Option B - Bulk migration**: Create a script to fetch from Supabase and call `add_episode`

Example bulk migration script:
```python
from supabase_client import supabase
from graphiti_client import add_episode
import uuid

# Fetch all documents
docs = supabase.table("documents").select("*").execute()

for doc in docs.data:
    episode_name = f"migration_{doc['id']}_{uuid.uuid4().hex[:8]}"
    result = add_episode(
        name=episode_name,
        episode_body=doc['text'][:10000],
        source_description=f"Migrated: {doc.get('metadata', {}).get('filename', 'unknown')}",
        episode_type="text"
    )
    print(f"Migrated doc {doc['id']}: {result}")
```

## Monitoring

### Check Neo4j Status
```cypher
# In Neo4j Browser (http://localhost:7474)
CALL dbms.components()
MATCH (n) RETURN count(n) as node_count
```

### Check API Health
```bash
# Test vector search (should work)
curl -X POST http://localhost:5000/retrieval \
  -H "X-API-KEY: changeme" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 1}'

# Test graph search (new feature)
curl -X POST http://localhost:5000/graph/search \
  -H "X-API-KEY: changeme" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "num_results": 1}'
```

## Support

- Check [GRAPHITI_INTEGRATION.md](./GRAPHITI_INTEGRATION.md) for detailed docs
- See [GRAPHITI_QUICKSTART.md](./GRAPHITI_QUICKSTART.md) for quick reference
- Review [test_graphiti.py](./test_graphiti.py) for working examples

## Summary Checklist

- [ ] Backup existing data
- [ ] Update requirements.in and install
- [ ] Add Neo4j to docker-compose.yml
- [ ] Copy graphiti_client.py
- [ ] Update app.py imports and endpoints
- [ ] Set OPENAI_API_KEY environment variable
- [ ] Restart services with `docker-compose up -d`
- [ ] Run `python test_graphiti.py`
- [ ] Verify Neo4j Browser access
- [ ] Test ingestion and retrieval

Once all steps are complete, you'll have a powerful hybrid RAG system! 🎉
