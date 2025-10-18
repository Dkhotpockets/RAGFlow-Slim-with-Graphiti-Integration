---
description: Run contract/integration tests that require external services
---

Run the contract tests for RAGFlow Slim. These tests require external services (Graphiti, Supabase, LLM providers) to be running.

First, check if Docker services are running:
```bash
docker-compose ps
```

If services aren't running, start them:
```bash
docker-compose up -d
```

Wait a few seconds for services to be ready, then run the contract tests:
```bash
pytest -q -m contract
```

Show me the results and any failures.
