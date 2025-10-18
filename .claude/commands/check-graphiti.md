---
description: Verify Graphiti and Neo4j connection and configuration
---

Check the Graphiti integration and Neo4j connection:

1. First, verify Neo4j is running:
```bash
docker-compose ps ragflow-neo4j
```

2. Check the health endpoint to see Graphiti status:
```bash
curl http://localhost:5000/health
```

3. Review the Graphiti client configuration in graphiti_client.py to verify:
   - Neo4j connection settings
   - LLM provider configuration for entity extraction
   - Embedder configuration

4. If Neo4j is running, try to connect using the configured credentials:
   - URI: bolt://localhost:7687 (or bolt://ragflow-neo4j:7687 in Docker)
   - User: neo4j
   - Password: graphiti_password

Show me:
- Whether Neo4j is accessible
- Current Graphiti configuration
- Any connection errors or warnings
- Which LLM provider is configured for Graphiti operations
