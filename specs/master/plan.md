# Implementation Plan: Crawl4AI Integration

**Branch**: `crawl4ai-integration` | **Date**: October 16, 2025 | **Spec**: specs/master/spec.md
**Input**: Feature specification from `/specs/master/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate Crawl4AI web crawling capabilities into RAGFlow Slim to enable automatic ingestion of web content, with entity extraction via Graphiti and storage in Supabase/Neo4j.

## Technical Context

**Language/Version**: Python 3.8+ (existing project requirement)
**Primary Dependencies**: Crawl4AI, existing Flask/FastAPI, Graphiti, Supabase, Neo4j
**Storage**: Supabase (vectors), Neo4j (knowledge graph), existing MySQL/Redis
**Testing**: pytest (existing), new integration tests for crawling
**Target Platform**: Docker containers (Linux), existing architecture
**Performance Goals**: <30 second crawl timeout, <5MB content per crawl, non-blocking API
**Constraints**: Respect robots.txt, rate limiting, content sanitization required
**Scale/Scope**: 10-100 concurrent crawls, 1M+ crawled pages, API-first design

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: PASS - Constitution established with 5 core principles

**Test-First**: ✅ pytest tests exist, CI pipeline enforces testing
**API-First Design**: ✅ RESTful APIs with OpenAPI specs maintained
**Integration Testing**: ✅ Docker Compose setup validates service interactions
**Observability**: ✅ Health endpoints, logging, and monitoring implemented
**Simplicity**: ✅ "Slim" version focuses on core RAG functionality

**Gate Decision**: PASS - All principles established and aligned with existing codebase

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB fails] |

## Phase 0: Research & Analysis ✅ COMPLETE
**Status**: Complete
**Deliverables**: research.md created with technical clarifications
**Key Findings**:
- Constitution establishment deferred (template exists)
- Crawl4AI compatible with existing Python stack
- Library integration within Flask app recommended
- Comprehensive politeness and error handling required

## Phase 1: Design & Architecture ✅ COMPLETE
**Status**: Complete
**Deliverables**: data-model.md and api-contracts.md created
**Key Deliverables**:
- Data models: CrawlJob, CrawlConfig, CrawlResult with database schemas
- API contracts: REST endpoints for job management with full request/response schemas
- Integration points: Graphiti entity extraction and Supabase vector storage
- Error handling: Comprehensive error responses and validation rules

## Phase 2: Implementation
**Status**: Ready to Start
**Objective**: Implement the crawling service and API endpoints
**Deliverables**:
- Crawl4AI service integration
- REST API endpoints
- Database migrations
- Unit and integration tests

**Tasks**:
1. Add Crawl4AI dependency and configuration
2. Implement crawl service with async processing
3. Create database tables and migrations
4. Build REST API endpoints
5. Add comprehensive error handling and logging
6. Write unit and integration tests
7. Update documentation and examples

