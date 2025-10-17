<!--
Sync Impact Report:
- Version change: N/A → 1.0.0 (initial constitution)
- Added sections: Core Principles (5), Technology Standards, Development Workflow, Governance
- Templates requiring updates: plan-template.md (constitution check alignment) ✅ updated
- Follow-up TODOs: None - all placeholders filled
-->
# RAGFlow Slim Constitution

## Core Principles

### I. Test-First (NON-NEGOTIABLE)
All features must be developed using Test-Driven Development. Tests are written before
implementation, ensuring red-green-refactor cycle. Unit tests cover core logic,
integration tests validate service interactions. CI pipeline enforces test execution
and coverage requirements.

### II. API-First Design
Every feature exposes functionality through RESTful APIs. OpenAPI specifications
must be maintained and validated. API contracts are defined before implementation,
ensuring consistent interfaces and proper error handling.

### III. Integration Testing
Focus on testing complete workflows rather than isolated units. Integration tests
validate data flow from ingestion through vector storage and graph operations.
Docker Compose environment ensures consistent test execution.

### IV. Observability
All services must provide health endpoints, structured logging, and metrics.
Runtime logs are collected for debugging and monitoring. Error conditions are
logged with sufficient context for troubleshooting.

### V. Simplicity
Start with minimal viable solutions. Avoid over-engineering and unnecessary
complexity. The "Slim" designation requires focusing on core RAG functionality
without feature bloat.

## Technology Standards

**Runtime Environment**: Python 3.8+ required for all components
**Containerization**: Docker required for deployment and testing
**Database Stack**: Supabase (vectors), Neo4j (graphs), MySQL/Redis (operational)
**LLM Providers**: Support for Google Gemini, Ollama, and extensible provider interface
**API Framework**: Flask/FastAPI with OpenAPI documentation

## Development Workflow

**Version Control**: Git with protected master branch
**Code Review**: All changes require pull request review
**CI/CD**: Automated testing, building, and deployment via GitHub Actions
**Documentation**: README, API docs, and integration guides must be current
**Security**: Dependencies scanned, secrets managed via environment variables

## Governance

Constitution supersedes all other practices and guides development decisions.
Amendments require:
1. Clear rationale for changes
2. Impact assessment on existing features
3. Migration plan for implementation
4. Review and approval by maintainers

All pull requests must verify compliance with these principles. Complexity additions
require explicit justification. Use CONTRIBUTOR_GUIDE.md for runtime development
guidance.

**Version**: 1.0.0 | **Ratified**: 2025-10-16 | **Last Amended**: 2025-10-16
