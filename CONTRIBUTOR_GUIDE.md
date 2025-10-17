# RAGFlow Slim with Graphiti Integration Contributor Guide

## Purpose

RAGFlow Slim with Graphiti Integration is a modular, contributor-safe RAG backend for document ingestion, retrieval, and context-aware LLM responses. It is designed for commercial integration, auditability, and onboarding.

## Getting Started

1. Clone the repository and install dependencies:
   - Activate the Python virtual environment (`.venv`).
   - Install required packages: `pip install -r requirements.txt` (or use auto-install).
2. Set environment variables as needed:
   - `RAGFLOW_API_KEY` (for API authentication)
   - `SUPABASE_URL` and `SUPABASE_KEY` (for Supabase integration)
   - `RAGFLOW_LOG_LEVEL` and `RAGFLOW_LOG_FILE` (for logging)
   - `RAGFLOW_CONFIG_DIR` (optional) - path to a configuration directory that may be mounted
       into the container or host. Default: `/data/application`. The app will scan the
       directory and app-specific subdirectories (e.g., `/data/application/myapp/`) for
       bootstrap files like `init.sql`, `schema.sql`, or `seed.json`.
3. Start the Flask app:
   - `python app.py` or use Docker (`docker build . && docker run ...`).

## API Endpoints

- `/completion`: Generate LLM completions (POST, JSON)
- `/ingest`: Ingest txt or PDF documents (POST, multipart)
- `/retrieval`: Retrieve relevant documents (POST, JSON, supports metadata filtering)

## CLI Usage

- Use `ragflow_cli.py` for ingestion and retrieval from the command line.

## Testing

- Run unit tests with `python test_app.py`.

## Contributor Safety

- All input/output operations are sanitized and path-safe.
- API key authentication and rate limiting are enforced.
- Output folder is consistent for audit and onboarding.
- Logging is configurable via environment variables.

## Extending Ragflow Slim Graphs

- Swap out Supabase for another backend by updating `supabase_client.py`.
- Integrate advanced embedding models via `get_embedding_ollama`.
- Add new endpoints or document types as needed.

## Documentation

- See `openapi.yaml` for full API specification.

## Support

- For onboarding, troubleshooting, or extension, contact the project maintainer or refer to this guide.
