# Data Model: Crawl4AI Integration

**Date**: October 16, 2025
**Feature**: Crawl4AI Integration
**Status**: Phase 1 - Design Complete

## Overview

This document defines the data structures and schemas for the Crawl4AI integration feature.
The design maintains compatibility with existing RAGFlow architecture.

## Core Data Models

### CrawlJob

Represents a single web crawling operation.

```python
@dataclass
class CrawlJob:
    id: str  # UUID
    url: str  # Target URL to crawl
    status: CrawlStatus  # Enum: pending, running, completed, failed
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    config: CrawlConfig  # Crawling parameters
    result: Optional[CrawlResult]  # Output data
    error_message: Optional[str]  # Failure details
```

### CrawlConfig

Configuration parameters for crawling behavior.

```python
@dataclass
class CrawlConfig:
    max_depth: int = 1  # How deep to crawl (default: single page)
    timeout_seconds: int = 30  # Maximum crawl time
    max_content_size: int = 5 * 1024 * 1024  # 5MB limit
    respect_robots: bool = True  # Honor robots.txt
    user_agent: str = "RAGFlow-Crawler/1.0"
    follow_redirects: bool = True
    extract_metadata: bool = True  # Extract title, description, etc.
```

### CrawlResult

Output data from a successful crawl operation.

```python
@dataclass
class CrawlResult:
    url: str  # Final URL (after redirects)
    title: Optional[str]  # Page title
    content: str  # Main text content
    metadata: Dict[str, Any]  # Additional metadata
    links: List[str]  # Discovered links
    content_hash: str  # SHA256 of content for deduplication
    content_size: int  # Size in bytes
    crawl_time: float  # Time taken in seconds
    extracted_at: datetime  # When content was extracted
```

### CrawlStatus

Enumeration of possible crawl job states.

```python
class CrawlStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

## Database Schema

### crawl_jobs Table

```sql
CREATE TABLE crawl_jobs (
    id VARCHAR(36) PRIMARY KEY,
    url TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    config JSON NOT NULL,
    result JSON NULL,
    error_message TEXT NULL,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_url (url(255))
);
```

### crawl_content Table

```sql
CREATE TABLE crawl_content (
    id VARCHAR(36) PRIMARY KEY,
    job_id VARCHAR(36) NOT NULL,
    url TEXT NOT NULL,
    title VARCHAR(500),
    content_hash VARCHAR(64) NOT NULL,
    content_size INT NOT NULL,
    extracted_at TIMESTAMP NOT NULL,
    FOREIGN KEY (job_id) REFERENCES crawl_jobs(id) ON DELETE CASCADE,
    UNIQUE KEY unique_content_hash (content_hash),
    INDEX idx_job_id (job_id),
    INDEX idx_content_hash (content_hash),
    INDEX idx_extracted_at (extracted_at)
);
```

## API Data Transfer Objects

### CrawlJobRequest

Input for creating a new crawl job.

```python
@dataclass
class CrawlJobRequest:
    url: str
    max_depth: Optional[int] = 1
    timeout_seconds: Optional[int] = 30
    max_content_size: Optional[int] = 5 * 1024 * 1024
    respect_robots: Optional[bool] = True
```

### CrawlJobResponse

API response for crawl job operations.

```python
@dataclass
class CrawlJobResponse:
    id: str
    url: str
    status: str
    created_at: str
    updated_at: str
    completed_at: Optional[str]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
```

## Integration Points

### Graphiti Entity Extraction

Crawl results integrate with existing Graphiti pipeline:

```python
# After successful crawl
crawl_result = await crawl_service.crawl_url(crawl_job.url, crawl_job.config)

# Extract entities using Graphiti
entities = await graphiti.extract_entities(crawl_result.content)

# Store in knowledge graph
await knowledge_graph.store_entities(entities, crawl_result.metadata)
```

### Supabase Vector Storage

Content vectors stored in existing Supabase setup:

```python
# Generate embeddings
embeddings = await embedding_service.generate(crawl_result.content)

# Store in Supabase
await supabase.store_vectors(crawl_result.id, embeddings, crawl_result.metadata)
```

## Data Flow

1. **Input**: CrawlJobRequest → CrawlJob creation
2. **Processing**: CrawlJob → Crawl4AI → CrawlResult
3. **Storage**: CrawlResult → crawl_jobs + crawl_content tables
4. **Integration**: CrawlResult → Graphiti → Neo4j + Supabase
5. **Output**: CrawlJobResponse with status and results

## Validation Rules

- **URL Format**: Must be valid HTTP/HTTPS URL
- **Content Size**: Cannot exceed max_content_size limit
- **Timeout**: Operations must complete within timeout_seconds
- **Robots.txt**: Must be checked when respect_robots=True
- **Deduplication**: Content hash prevents duplicate processing

## Error Handling

- **Network Errors**: Connection timeouts, DNS failures
- **Content Errors**: Invalid HTML, encoding issues
- **Rate Limiting**: Respect server limits, implement backoff
- **Robots.txt**: Honor disallow directives
- **Size Limits**: Truncate or reject oversized content