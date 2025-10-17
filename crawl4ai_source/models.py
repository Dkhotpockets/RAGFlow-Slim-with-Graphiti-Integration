"""
Crawl4AI Data Models for RAGFlow Slim

This module defines the core data structures for the Crawl4AI web crawling integration.
All models follow the specification defined in specs/master/data-model.md
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class CrawlStatus(Enum):
    """Enumeration of possible crawl job states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CrawlConfig:
    """
    Configuration parameters for crawling behavior.

    Defines the settings that control how web crawling is performed,
    including depth limits, timeouts, and content constraints.
    """
    max_depth: int = 1
    timeout_seconds: int = 30
    max_content_size: int = 5 * 1024 * 1024  # 5MB default
    respect_robots: bool = True
    user_agent: str = "RAGFlow-Crawler/1.0"
    follow_redirects: bool = True
    extract_metadata: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for JSON serialization."""
        return {
            "max_depth": self.max_depth,
            "timeout_seconds": self.timeout_seconds,
            "max_content_size": self.max_content_size,
            "respect_robots": self.respect_robots,
            "user_agent": self.user_agent,
            "follow_redirects": self.follow_redirects,
            "extract_metadata": self.extract_metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrawlConfig':
        """Create config from dictionary."""
        return cls(
            max_depth=data.get("max_depth", 1),
            timeout_seconds=data.get("timeout_seconds", 30),
            max_content_size=data.get("max_content_size", 5 * 1024 * 1024),
            respect_robots=data.get("respect_robots", True),
            user_agent=data.get("user_agent", "RAGFlow-Crawler/1.0"),
            follow_redirects=data.get("follow_redirects", True),
            extract_metadata=data.get("extract_metadata", True),
        )


@dataclass
class CrawlResult:
    """
    Output data from a successful crawl operation.

    Contains the extracted content, metadata, and processing information
    from a web crawling operation.
    """
    url: str
    title: Optional[str] = None
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)
    content_hash: str = ""
    content_size: int = 0
    crawl_time: float = 0.0
    extracted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "links": self.links,
            "content_hash": self.content_hash,
            "content_size": self.content_size,
            "crawl_time": self.crawl_time,
            "extracted_at": self.extracted_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrawlResult':
        """Create result from dictionary."""
        return cls(
            url=data["url"],
            title=data.get("title"),
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            links=data.get("links", []),
            content_hash=data.get("content_hash", ""),
            content_size=data.get("content_size", 0),
            crawl_time=data.get("crawl_time", 0.0),
            extracted_at=datetime.fromisoformat(data["extracted_at"]) if "extracted_at" in data else datetime.now(timezone.utc),
        )


@dataclass
class CrawlJob:
    """
    Represents a single web crawling operation.

    Tracks the lifecycle of a crawl job from creation through completion,
    including configuration, status, and results.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    url: str = ""
    status: CrawlStatus = CrawlStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    config: CrawlConfig = field(default_factory=CrawlConfig)
    result: Optional[CrawlResult] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "url": self.url,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "config": self.config.to_dict(),
            "result": self.result.to_dict() if self.result else None,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrawlJob':
        """Create job from dictionary."""
        return cls(
            id=data["id"],
            url=data["url"],
            status=CrawlStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            config=CrawlConfig.from_dict(data["config"]),
            result=CrawlResult.from_dict(data["result"]) if data.get("result") else None,
            error_message=data.get("error_message"),
        )

    def mark_running(self) -> None:
        """Mark the job as running."""
        self.status = CrawlStatus.RUNNING
        self.updated_at = datetime.now(timezone.utc)

    def mark_completed(self, result: CrawlResult) -> None:
        """Mark the job as completed with a result."""
        self.status = CrawlStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def mark_failed(self, error_message: str) -> None:
        """Mark the job as failed with an error message."""
        self.status = CrawlStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def mark_cancelled(self) -> None:
        """Mark the job as cancelled."""
        self.status = CrawlStatus.CANCELLED
        self.completed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)


# API Data Transfer Objects

@dataclass
class CrawlJobRequest:
    """
    Input for creating a new crawl job.

    Simplified request object for API endpoints that only includes
    the essential parameters needed to create a crawl job.
    """
    url: str
    max_depth: Optional[int] = 1
    timeout_seconds: Optional[int] = 30
    max_content_size: Optional[int] = 5 * 1024 * 1024
    respect_robots: Optional[bool] = True
    user_agent: Optional[str] = "RAGFlow-Crawler/1.0"
    follow_redirects: Optional[bool] = True
    extract_metadata: Optional[bool] = True

    def to_config(self) -> CrawlConfig:
        """Convert request to a CrawlConfig object."""
        return CrawlConfig(
            max_depth=self.max_depth or 1,
            timeout_seconds=self.timeout_seconds or 30,
            max_content_size=self.max_content_size or 5 * 1024 * 1024,
            respect_robots=self.respect_robots if self.respect_robots is not None else True,
            user_agent=self.user_agent or "RAGFlow-Crawler/1.0",
            follow_redirects=self.follow_redirects if self.follow_redirects is not None else True,
            extract_metadata=self.extract_metadata if self.extract_metadata is not None else True,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrawlJobRequest':
        """Create request from dictionary."""
        from werkzeug.exceptions import BadRequest
        from urllib.parse import urlparse
        
        if not isinstance(data, dict):
            raise BadRequest("Data must be a dictionary")
        
        url = data.get("url")
        if not url:
            raise BadRequest("url is required")
        
        # Basic URL validation
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise BadRequest("Invalid URL format")
        except Exception:
            raise BadRequest("Invalid URL format")
        
        return cls(
            url=url,
            max_depth=data.get("max_depth"),
            timeout_seconds=data.get("timeout_seconds"),
            max_content_size=data.get("max_content_size"),
            respect_robots=data.get("respect_robots"),
            user_agent=data.get("user_agent"),
            follow_redirects=data.get("follow_redirects"),
            extract_metadata=data.get("extract_metadata"),
        )


@dataclass
class CrawlJobResponse:
    """
    API response for crawl job operations.

    Simplified response object that includes job status and results
    in a format suitable for API clients.
    """
    id: str
    url: str
    status: str
    created_at: str
    updated_at: str
    completed_at: Optional[str]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]

    @classmethod
    def from_job(cls, job: CrawlJob) -> 'CrawlJobResponse':
        """Create response from a CrawlJob object."""
        return cls(
            id=job.id,
            url=job.url,
            status=job.status.value,
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat(),
            completed_at=job.completed_at.isoformat() if job.completed_at else None,
            result=job.result.to_dict() if job.result else None,
            error_message=job.error_message,
        )