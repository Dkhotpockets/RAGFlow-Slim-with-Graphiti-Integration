# API Contracts: Crawl4AI Integration

**Date**: October 16, 2025
**Feature**: Crawl4AI Integration
**Status**: Phase 1 - Design Complete

## Overview

This document defines the REST API contracts for the Crawl4AI integration feature.
All endpoints follow RESTful conventions and integrate with existing RAGFlow API.

## Base URL

```
/api/v1/crawl
```

## Endpoints

### POST /api/v1/crawl/jobs

Create a new crawl job.

**Request Body:**
```json
{
  "url": "https://example.com",
  "max_depth": 1,
  "timeout_seconds": 30,
  "max_content_size": 5242880,
  "respect_robots": true
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://example.com",
  "status": "pending",
  "created_at": "2025-10-16T10:30:00Z",
  "updated_at": "2025-10-16T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid URL or parameters
- `429 Too Many Requests`: Rate limit exceeded

### GET /api/v1/crawl/jobs/{job_id}

Get crawl job status and results.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://example.com",
  "status": "completed",
  "created_at": "2025-10-16T10:30:00Z",
  "updated_at": "2025-10-16T10:32:15Z",
  "completed_at": "2025-10-16T10:32:15Z",
  "result": {
    "url": "https://example.com",
    "title": "Example Domain",
    "content": "This domain is for use in illustrative examples...",
    "metadata": {
      "description": "Example domain for testing",
      "keywords": ["example", "test"]
    },
    "links": [
      "https://example.com/page1",
      "https://example.com/page2"
    ],
    "content_hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
    "content_size": 1234,
    "crawl_time": 2.5
  }
}
```

**Response (202 Accepted) - Still Processing:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://example.com",
  "status": "running",
  "created_at": "2025-10-16T10:30:00Z",
  "updated_at": "2025-10-16T10:31:00Z"
}
```

**Error Responses:**
- `404 Not Found`: Job not found
- `500 Internal Server Error`: Processing failed

### GET /api/v1/crawl/jobs

List crawl jobs with pagination.

**Query Parameters:**
- `status` (optional): Filter by status (pending, running, completed, failed)
- `limit` (optional): Number of results (default: 20, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response (200 OK):**
```json
{
  "jobs": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "url": "https://example.com",
      "status": "completed",
      "created_at": "2025-10-16T10:30:00Z",
      "updated_at": "2025-10-16T10:32:15Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

### DELETE /api/v1/crawl/jobs/{job_id}

Cancel a pending or running crawl job.

**Response (204 No Content):** Job cancelled successfully

**Error Responses:**
- `404 Not Found`: Job not found
- `409 Conflict`: Job already completed or failed

### GET /api/v1/crawl/stats

Get crawling statistics.

**Response (200 OK):**
```json
{
  "total_jobs": 150,
  "completed_jobs": 142,
  "failed_jobs": 8,
  "running_jobs": 0,
  "avg_crawl_time": 3.2,
  "total_content_size": 157286400,
  "unique_urls": 128
}
```

## Request/Response Schemas

### CrawlJobRequest
```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "format": "uri",
      "description": "Target URL to crawl"
    },
    "max_depth": {
      "type": "integer",
      "minimum": 1,
      "maximum": 3,
      "default": 1,
      "description": "Crawl depth"
    },
    "timeout_seconds": {
      "type": "integer",
      "minimum": 5,
      "maximum": 300,
      "default": 30,
      "description": "Timeout in seconds"
    },
    "max_content_size": {
      "type": "integer",
      "minimum": 1024,
      "maximum": 10485760,
      "default": 5242880,
      "description": "Max content size in bytes"
    },
    "respect_robots": {
      "type": "boolean",
      "default": true,
      "description": "Respect robots.txt"
    }
  },
  "required": ["url"]
}
```

### CrawlJobResponse
```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid",
      "description": "Job ID"
    },
    "url": {
      "type": "string",
      "format": "uri",
      "description": "Target URL"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "running", "completed", "failed", "cancelled"],
      "description": "Job status"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Creation timestamp"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Last update timestamp"
    },
    "completed_at": {
      "type": "string",
      "format": "date-time",
      "description": "Completion timestamp"
    },
    "result": {
      "$ref": "#/definitions/CrawlResult"
    },
    "error_message": {
      "type": "string",
      "description": "Error details if failed"
    }
  },
  "required": ["id", "url", "status", "created_at", "updated_at"]
}
```

### CrawlResult
```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "format": "uri",
      "description": "Final URL"
    },
    "title": {
      "type": "string",
      "description": "Page title"
    },
    "content": {
      "type": "string",
      "description": "Extracted text content"
    },
    "metadata": {
      "type": "object",
      "description": "Additional metadata"
    },
    "links": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "uri"
      },
      "description": "Discovered links"
    },
    "content_hash": {
      "type": "string",
      "description": "SHA256 content hash"
    },
    "content_size": {
      "type": "integer",
      "description": "Content size in bytes"
    },
    "crawl_time": {
      "type": "number",
      "description": "Crawl duration in seconds"
    }
  },
  "required": ["url", "content", "content_hash", "content_size", "crawl_time"]
}
```

## Error Response Format

All error responses follow this format:

```json
{
  "error": {
    "code": "INVALID_URL",
    "message": "The provided URL is not valid",
    "details": {
      "url": "not-a-url"
    }
  }
}
```

## Rate Limiting

- **Create Job**: 10 requests per minute per IP
- **Get Job**: 60 requests per minute per IP
- **List Jobs**: 30 requests per minute per IP

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets (Unix timestamp)

## Authentication

All endpoints require authentication via existing RAGFlow auth (API key or JWT).

## Content Types

- **Request**: `application/json`
- **Response**: `application/json`

## Versioning

API version is included in URL path (`/api/v1/crawl`). Future versions use `/api/v2/crawl`.