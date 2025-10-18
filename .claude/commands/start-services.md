---
description: Start all Docker Compose services for development
---

Start all RAGFlow Slim services using Docker Compose:

```bash
docker-compose up -d
```

Wait for services to be ready, then check their status:
```bash
docker-compose ps
```

Verify the main application is healthy:
```bash
curl http://localhost:5000/health
```

Show me:
1. Which services are running
2. The health check response with LLM provider and Graphiti status
3. Any services that failed to start
