"""
Crawl4AI Integration for RAGFlow Slim

This package provides web crawling capabilities for the RAGFlow Slim system,
enabling automated content extraction and knowledge graph integration.
"""

from .models import (
    CrawlConfig,
    CrawlJob,
    CrawlJobRequest,
    CrawlJobResponse,
    CrawlResult,
    CrawlStatus,
)
from .service import CrawlService
from .manager import CrawlJobManager
from .deduplicator import ContentDeduplicator, ContentFingerprint
from .rate_limiter import RateLimiter, RateLimitRule

__all__ = [
    "CrawlConfig",
    "CrawlJob",
    "CrawlJobRequest",
    "CrawlJobResponse",
    "CrawlResult",
    "CrawlStatus",
    "CrawlService",
    "CrawlJobManager",
    "ContentDeduplicator",
    "ContentFingerprint",
    "RateLimiter",
    "RateLimitRule",
]