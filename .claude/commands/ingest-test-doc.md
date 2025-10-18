---
description: Test document ingestion pipeline (Supabase + Graphiti)
---

Test the complete document ingestion pipeline:

1. Create a test document:
```bash
echo "This is a test document about machine learning. Alice works on neural networks at TechCorp. She collaborates with Bob on natural language processing projects." > /tmp/test_doc.txt
```

2. Ingest the document using the API:
```bash
curl -X POST http://localhost:5000/ingest \
  -H "X-API-KEY: changeme" \
  -F "file=@/tmp/test_doc.txt"
```

3. Test retrieval with a query:
```bash
curl -X POST http://localhost:5000/retrieval \
  -H "X-API-KEY: changeme" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who works on neural networks?", "top_k": 3}'
```

4. Test graph search for entities:
```bash
curl -X POST http://localhost:5000/graph/search \
  -H "X-API-KEY: changeme" \
  -H "Content-Type: application/json" \
  -d '{"query": "Alice", "num_results": 5}'
```

Show me:
- Ingestion response (Supabase + Graphiti results)
- Retrieval results (vector + graph)
- Graph search results showing extracted entities and relationships
- Any errors or warnings
