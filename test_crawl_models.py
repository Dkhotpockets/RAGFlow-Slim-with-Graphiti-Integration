"""
Tests for Crawl4AI data models.

This module contains unit tests for the data models defined in crawl4ai_source/models.py.
Tests cover serialization, deserialization, and business logic methods.
"""

import pytest
from datetime import datetime
from crawl4ai_source.models import (
    CrawlStatus,
    CrawlConfig,
    CrawlResult,
    CrawlJob,
    CrawlJobRequest,
    CrawlJobResponse
)


class TestCrawlStatus:
    """Test CrawlStatus enum."""

    def test_enum_values(self):
        """Test that all expected status values are present."""
        assert CrawlStatus.PENDING.value == "pending"
        assert CrawlStatus.RUNNING.value == "running"
        assert CrawlStatus.COMPLETED.value == "completed"
        assert CrawlStatus.FAILED.value == "failed"
        assert CrawlStatus.CANCELLED.value == "cancelled"

    def test_enum_membership(self):
        """Test that all expected statuses are in the enum."""
        statuses = {status.value for status in CrawlStatus}
        expected = {"pending", "running", "completed", "failed", "cancelled"}
        assert statuses == expected


class TestCrawlConfig:
    """Test CrawlConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = CrawlConfig()
        assert config.max_depth == 1
        assert config.timeout_seconds == 30
        assert config.max_content_size == 5 * 1024 * 1024  # 5MB
        assert config.respect_robots is True
        assert config.user_agent == "RAGFlow-Crawler/1.0"
        assert config.follow_redirects is True
        assert config.extract_metadata is True

    def test_custom_values(self):
        """Test configuration with custom values."""
        config = CrawlConfig(
            max_depth=3,
            timeout_seconds=60,
            max_content_size=10 * 1024 * 1024,
            respect_robots=False,
            user_agent="Custom-Agent/1.0",
            follow_redirects=False,
            extract_metadata=False
        )
        assert config.max_depth == 3
        assert config.timeout_seconds == 60
        assert config.max_content_size == 10 * 1024 * 1024
        assert config.respect_robots is False
        assert config.user_agent == "Custom-Agent/1.0"
        assert config.follow_redirects is False
        assert config.extract_metadata is False

    def test_to_dict(self):
        """Test serialization to dictionary."""
        config = CrawlConfig(max_depth=2, timeout_seconds=45)
        data = config.to_dict()
        expected = {
            "max_depth": 2,
            "timeout_seconds": 45,
            "max_content_size": 5 * 1024 * 1024,
            "respect_robots": True,
            "user_agent": "RAGFlow-Crawler/1.0",
            "follow_redirects": True,
            "extract_metadata": True,
        }
        assert data == expected

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "max_depth": 3,
            "timeout_seconds": 60,
            "max_content_size": 10 * 1024 * 1024,
            "respect_robots": False,
            "user_agent": "Test-Agent/1.0",
            "follow_redirects": False,
            "extract_metadata": False,
        }
        config = CrawlConfig.from_dict(data)
        assert config.max_depth == 3
        assert config.timeout_seconds == 60
        assert config.max_content_size == 10 * 1024 * 1024
        assert config.respect_robots is False
        assert config.user_agent == "Test-Agent/1.0"
        assert config.follow_redirects is False
        assert config.extract_metadata is False

    def test_from_dict_defaults(self):
        """Test deserialization with missing fields uses defaults."""
        data = {"max_depth": 2}
        config = CrawlConfig.from_dict(data)
        assert config.max_depth == 2
        assert config.timeout_seconds == 30  # default
        assert config.respect_robots is True  # default


class TestCrawlResult:
    """Test CrawlResult dataclass."""

    def test_default_values(self):
        """Test default result values."""
        result = CrawlResult(url="https://example.com")
        assert result.url == "https://example.com"
        assert result.title is None
        assert result.content == ""
        assert result.metadata == {}
        assert result.links == []
        assert result.content_hash == ""
        assert result.content_size == 0
        assert result.crawl_time == 0.0
        assert isinstance(result.extracted_at, datetime)

    def test_custom_values(self):
        """Test result with custom values."""
        extracted_at = datetime(2024, 1, 1, 12, 0, 0)
        result = CrawlResult(
            url="https://example.com",
            title="Test Page",
            content="Test content",
            metadata={"author": "Test"},
            links=["https://link1.com", "https://link2.com"],
            content_hash="abc123",
            content_size=1000,
            crawl_time=2.5,
            extracted_at=extracted_at
        )
        assert result.url == "https://example.com"
        assert result.title == "Test Page"
        assert result.content == "Test content"
        assert result.metadata == {"author": "Test"}
        assert result.links == ["https://link1.com", "https://link2.com"]
        assert result.content_hash == "abc123"
        assert result.content_size == 1000
        assert result.crawl_time == 2.5
        assert result.extracted_at == extracted_at

    def test_to_dict(self):
        """Test serialization to dictionary."""
        extracted_at = datetime(2024, 1, 1, 12, 0, 0)
        result = CrawlResult(
            url="https://example.com",
            title="Test Page",
            content="Test content",
            extracted_at=extracted_at
        )
        data = result.to_dict()
        assert data["url"] == "https://example.com"
        assert data["title"] == "Test Page"
        assert data["content"] == "Test content"
        assert data["metadata"] == {}
        assert data["links"] == []
        assert data["content_hash"] == ""
        assert data["content_size"] == 0
        assert data["crawl_time"] == 0.0
        assert data["extracted_at"] == extracted_at.isoformat()

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "url": "https://example.com",
            "title": "Test Page",
            "content": "Test content",
            "metadata": {"author": "Test"},
            "links": ["https://link1.com"],
            "content_hash": "abc123",
            "content_size": 1000,
            "crawl_time": 2.5,
            "extracted_at": "2024-01-01T12:00:00",
        }
        result = CrawlResult.from_dict(data)
        assert result.url == "https://example.com"
        assert result.title == "Test Page"
        assert result.content == "Test content"
        assert result.metadata == {"author": "Test"}
        assert result.links == ["https://link1.com"]
        assert result.content_hash == "abc123"
        assert result.content_size == 1000
        assert result.crawl_time == 2.5
        assert result.extracted_at == datetime(2024, 1, 1, 12, 0, 0)

    def test_from_dict_defaults(self):
        """Test deserialization with missing fields uses defaults."""
        data = {"url": "https://example.com"}
        result = CrawlResult.from_dict(data)
        assert result.url == "https://example.com"
        assert result.title is None
        assert result.content == ""
        assert result.metadata == {}
        assert result.links == []
        assert result.content_hash == ""
        assert result.content_size == 0
        assert result.crawl_time == 0.0
        assert isinstance(result.extracted_at, datetime)


class TestCrawlJob:
    """Test CrawlJob dataclass."""

    def test_default_values(self):
        """Test default job values."""
        job = CrawlJob(url="https://example.com")
        assert job.url == "https://example.com"
        assert isinstance(job.id, str)
        assert len(job.id) > 0
        assert job.status == CrawlStatus.PENDING
        assert isinstance(job.created_at, datetime)
        assert isinstance(job.updated_at, datetime)
        assert job.completed_at is None
        assert isinstance(job.config, CrawlConfig)
        assert job.result is None
        assert job.error_message is None

    def test_custom_values(self):
        """Test job with custom values."""
        config = CrawlConfig(max_depth=2)
        result = CrawlResult(url="https://example.com", content="Test")
        created_at = datetime(2024, 1, 1, 10, 0, 0)
        updated_at = datetime(2024, 1, 1, 10, 5, 0)
        completed_at = datetime(2024, 1, 1, 10, 5, 0)

        job = CrawlJob(
            id="test-job-123",
            url="https://example.com",
            status=CrawlStatus.COMPLETED,
            created_at=created_at,
            updated_at=updated_at,
            completed_at=completed_at,
            config=config,
            result=result,
            error_message="Test error"
        )
        assert job.id == "test-job-123"
        assert job.url == "https://example.com"
        assert job.status == CrawlStatus.COMPLETED
        assert job.created_at == created_at
        assert job.updated_at == updated_at
        assert job.completed_at == completed_at
        assert job.config == config
        assert job.result == result
        assert job.error_message == "Test error"

    def test_mark_running(self):
        """Test marking job as running."""
        job = CrawlJob(url="https://example.com")
        initial_updated_at = job.updated_at

        job.mark_running()

        assert job.status == CrawlStatus.RUNNING
        assert job.updated_at >= initial_updated_at

    def test_mark_completed(self):
        """Test marking job as completed."""
        job = CrawlJob(url="https://example.com")
        result = CrawlResult(url="https://example.com", content="Test content")
        initial_updated_at = job.updated_at

        job.mark_completed(result)

        assert job.status == CrawlStatus.COMPLETED
        assert job.result == result
        assert job.completed_at is not None
        assert job.updated_at >= initial_updated_at

    def test_mark_failed(self):
        """Test marking job as failed."""
        job = CrawlJob(url="https://example.com")
        initial_updated_at = job.updated_at

        job.mark_failed("Test error message")

        assert job.status == CrawlStatus.FAILED
        assert job.error_message == "Test error message"
        assert job.completed_at is not None
        assert job.updated_at >= initial_updated_at

    def test_mark_cancelled(self):
        """Test marking job as cancelled."""
        job = CrawlJob(url="https://example.com")
        initial_updated_at = job.updated_at

        job.mark_cancelled()

        assert job.status == CrawlStatus.CANCELLED
        assert job.completed_at is not None
        assert job.updated_at >= initial_updated_at

    def test_to_dict(self):
        """Test serialization to dictionary."""
        config = CrawlConfig(max_depth=2)
        result = CrawlResult(url="https://example.com", content="Test")
        created_at = datetime(2024, 1, 1, 10, 0, 0)
        updated_at = datetime(2024, 1, 1, 10, 5, 0)
        completed_at = datetime(2024, 1, 1, 10, 5, 0)

        job = CrawlJob(
            id="test-job-123",
            url="https://example.com",
            status=CrawlStatus.COMPLETED,
            created_at=created_at,
            updated_at=updated_at,
            completed_at=completed_at,
            config=config,
            result=result,
            error_message="Test error"
        )

        data = job.to_dict()
        assert data["id"] == "test-job-123"
        assert data["url"] == "https://example.com"
        assert data["status"] == "completed"
        assert data["created_at"] == created_at.isoformat()
        assert data["updated_at"] == updated_at.isoformat()
        assert data["completed_at"] == completed_at.isoformat()
        assert data["config"]["max_depth"] == 2
        assert data["result"]["content"] == "Test"
        assert data["error_message"] == "Test error"

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "id": "test-job-123",
            "url": "https://example.com",
            "status": "completed",
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-01T10:05:00",
            "completed_at": "2024-01-01T10:05:00",
            "config": {"max_depth": 2},
            "result": {"url": "https://example.com", "content": "Test"},
            "error_message": "Test error"
        }

        job = CrawlJob.from_dict(data)
        assert job.id == "test-job-123"
        assert job.url == "https://example.com"
        assert job.status == CrawlStatus.COMPLETED
        assert job.created_at == datetime(2024, 1, 1, 10, 0, 0)
        assert job.updated_at == datetime(2024, 1, 1, 10, 5, 0)
        assert job.completed_at == datetime(2024, 1, 1, 10, 5, 0)
        assert job.config.max_depth == 2
        assert job.result.content == "Test"
        assert job.error_message == "Test error"


class TestCrawlJobRequest:
    """Test CrawlJobRequest dataclass."""

    def test_default_values(self):
        """Test default request values."""
        request = CrawlJobRequest(url="https://example.com")
        assert request.url == "https://example.com"
        assert request.max_depth == 1
        assert request.timeout_seconds == 30
        assert request.max_content_size == 5 * 1024 * 1024
        assert request.respect_robots is True

    def test_custom_values(self):
        """Test request with custom values."""
        request = CrawlJobRequest(
            url="https://example.com",
            max_depth=3,
            timeout_seconds=60,
            max_content_size=10 * 1024 * 1024,
            respect_robots=False
        )
        assert request.url == "https://example.com"
        assert request.max_depth == 3
        assert request.timeout_seconds == 60
        assert request.max_content_size == 10 * 1024 * 1024
        assert request.respect_robots is False

    def test_to_config(self):
        """Test conversion to CrawlConfig."""
        request = CrawlJobRequest(
            url="https://example.com",
            max_depth=3,
            timeout_seconds=60,
            max_content_size=10 * 1024 * 1024,
            respect_robots=False
        )
        config = request.to_config()
        assert config.max_depth == 3
        assert config.timeout_seconds == 60
        assert config.max_content_size == 10 * 1024 * 1024
        assert config.respect_robots is False
        # Check defaults are applied for other fields
        assert config.user_agent == "RAGFlow-Crawler/1.0"
        assert config.follow_redirects is True
        assert config.extract_metadata is True


class TestCrawlJobResponse:
    """Test CrawlJobResponse dataclass."""

    def test_from_job(self):
        """Test creation from CrawlJob."""
        config = CrawlConfig(max_depth=2)
        result = CrawlResult(url="https://example.com", content="Test content")
        created_at = datetime(2024, 1, 1, 10, 0, 0)
        updated_at = datetime(2024, 1, 1, 10, 5, 0)
        completed_at = datetime(2024, 1, 1, 10, 5, 0)

        job = CrawlJob(
            id="test-job-123",
            url="https://example.com",
            status=CrawlStatus.COMPLETED,
            created_at=created_at,
            updated_at=updated_at,
            completed_at=completed_at,
            config=config,
            result=result,
            error_message=None
        )

        response = CrawlJobResponse.from_job(job)
        assert response.id == "test-job-123"
        assert response.url == "https://example.com"
        assert response.status == "completed"
        assert response.created_at == created_at.isoformat()
        assert response.updated_at == updated_at.isoformat()
        assert response.completed_at == completed_at.isoformat()
        assert response.result["content"] == "Test content"
        assert response.error_message is None

    def test_from_job_without_result(self):
        """Test creation from job without result."""
        job = CrawlJob(
            id="test-job-123",
            url="https://example.com",
            status=CrawlStatus.PENDING
        )

        response = CrawlJobResponse.from_job(job)
        assert response.id == "test-job-123"
        assert response.url == "https://example.com"
        assert response.status == "pending"
        assert response.result is None
        assert response.completed_at is None
        assert response.error_message is None