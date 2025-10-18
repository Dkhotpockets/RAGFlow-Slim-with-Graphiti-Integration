---
description: Set up development environment from scratch
---

Set up the RAGFlow Slim development environment:

1. Check if .env file exists, if not copy from .env.example:
```bash
if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file - please configure it"; else echo ".env already exists"; fi
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start Docker services:
```bash
docker-compose up -d
```

4. Wait for services to be ready (10 seconds):
```bash
sleep 10
```

5. Check service health:
```bash
docker-compose ps
curl http://localhost:5000/health
```

Show me:
- Whether .env was created (and remind to configure API keys)
- Python package installation results
- Docker service status
- Application health check results
- Next steps for configuration
