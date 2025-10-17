"""
Tests for Crawl4AI service implementation.

This module contains unit tests for the CrawlService class in crawl4ai_source/service.py.
Tests cover service lifecycle, crawling operations, and content extraction.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from crawl4ai_source.service import CrawlService
from crawl4ai_source.models import CrawlConfig, CrawlResult


class TestCrawlService:
    """Test CrawlService class."""

    @pytest.fixture
    def crawl_service(self):
        """Create a CrawlService instance for testing."""
        return CrawlService()

    @pytest.fixture
    def sample_config(self):
        """Create a sample CrawlConfig for testing."""
        return CrawlConfig(
            max_depth=2,
            timeout_seconds=30,
            max_content_size=5 * 1024 * 1024,
            respect_robots=True,
            user_agent="Test-Agent/1.0",
            follow_redirects=True,
            extract_metadata=True
        )

    @pytest.mark.asyncio
    async def test_context_manager(self, crawl_service):
        """Test async context manager functionality."""
        # Test entering context
        async with crawl_service:
            assert crawl_service._crawler is not None

        # Test exiting context
        assert crawl_service._crawler is None

    @pytest.mark.asyncio
    async def test_start_stop(self, crawl_service):
        """Test manual start/stop functionality."""
        # Initially not started
        assert crawl_service._crawler is None

        # Start service
        await crawl_service.start()
        assert crawl_service._crawler is not None

        # Stop service
        await crawl_service.stop()
        assert crawl_service._crawler is None

    @pytest.mark.asyncio
    async def test_crawl_url_without_start_raises_error(self, crawl_service, sample_config):
        """Test that crawling without starting service raises error."""
        with pytest.raises(RuntimeError, match="Crawler service not started"):
            await crawl_service.crawl_url("https://example.com", sample_config)

    @pytest.mark.asyncio
    async def test_crawl_url_success(self, crawl_service, sample_config):
        """Test successful URL crawling."""
        # Mock the markdown result
        mock_markdown = MagicMock()
        mock_markdown.raw_markdown = "Test content"

        # Mock the crawler result
        mock_result = MagicMock()
        mock_result.url = "https://example.com"
        mock_result.markdown = mock_markdown
        mock_result.markdown_v2 = None
        mock_result.metadata = {
            'title': 'Test Page',
            'description': 'Test description',
            'keywords': 'test, page',
            'author': 'Test Author',
            'language': 'en',
            'content_type': 'text/html'
        }
        mock_result.links = ['https://link1.com', 'https://link2.com']
        mock_result.html = '<html><head><title>Test Page</title></head><body>Test content</body></html>'

        # Mock the crawler directly
        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result
        crawl_service._crawler = mock_crawler

        result = await crawl_service.crawl_url("https://example.com", sample_config)

        # Verify result structure
        assert isinstance(result, CrawlResult)
        assert result.url == "https://example.com"
        assert result.title == "Test Page"
        assert result.content == "Test content"
        # Hash of "Test content"
        expected_hash = "9d9595c5d94fb65b824f56e9999527dba9542481580d69feb89056aabaa0aa87"
        assert result.content_hash == expected_hash
        assert result.content_size == len("Test content".encode('utf-8'))
        assert result.crawl_time >= 0
        assert len(result.links) == 2
        assert 'title' in result.metadata
        assert 'crawl_config' in result.metadata

    @pytest.mark.asyncio
    async def test_crawl_url_with_redirect(self, crawl_service, sample_config):
        """Test crawling with URL redirect."""
        # Mock the markdown result
        mock_markdown = MagicMock()
        mock_markdown.raw_markdown = "Redirected content"

        # Mock the crawler with redirected URL
        mock_result = MagicMock()
        mock_result.url = "https://example.com/redirected"
        mock_result.markdown = mock_markdown
        mock_result.metadata = {'title': 'Redirected Page'}
        mock_result.links = []
        mock_result.html = '<html><head><title>Redirected Page</title></head><body>Redirected content</body></html>'

        # Mock the crawler directly
        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result
        crawl_service._crawler = mock_crawler

        result = await crawl_service.crawl_url("https://example.com", sample_config)

        # Should use the final redirected URL
        assert result.url == "https://example.com/redirected"

    @pytest.mark.asyncio
    async def test_crawl_url_failure(self, crawl_service, sample_config):
        """Test crawling failure handling."""
        # Mock the crawler to raise an exception
        mock_crawler = AsyncMock()
        mock_crawler.arun.side_effect = Exception("Network error")
        crawl_service._crawler = mock_crawler

        with pytest.raises(Exception, match="Network error"):
            await crawl_service.crawl_url("https://example.com", sample_config)

    @pytest.mark.asyncio
    async def test_crawl_url_no_markdown(self, crawl_service, sample_config):
        """Test crawling when markdown extraction fails."""
        # Mock result with no markdown
        mock_result = MagicMock()
        mock_result.url = "https://example.com"
        mock_result.markdown = None
        mock_result.markdown_v2 = None
        mock_result.metadata = {'title': 'Test Page'}
        mock_result.links = []
        mock_result.html = '<html><head><title>Test Page</title></head><body>Test content</body></html>'

        # Mock the crawler directly
        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result
        crawl_service._crawler = mock_crawler

        result = await crawl_service.crawl_url("https://example.com", sample_config)

        assert result.content == '<html><head><title>Test Page</title></head><body>Test content</body></html>'  # HTML fallback
        assert result.title == "Test Page"  # Title from metadata

    def test_extract_title_from_metadata(self, crawl_service):
        """Test title extraction from metadata."""
        mock_result = MagicMock()
        mock_result.metadata = {'title': 'Metadata Title'}

        title = crawl_service._extract_title(mock_result)
        assert title == "Metadata Title"

    def test_extract_title_from_html(self, crawl_service):
        """Test title extraction from HTML."""
        mock_result = MagicMock()
        mock_result.metadata = None
        mock_result.html = '<html><head><title>HTML Title</title></head><body>Content</body></html>'

        title = crawl_service._extract_title(mock_result)
        assert title == "HTML Title"

    def test_extract_title_failure(self, crawl_service):
        """Test title extraction failure handling."""
        mock_result = MagicMock()
        mock_result.metadata = None
        mock_result.html = None

        title = crawl_service._extract_title(mock_result)
        assert title is None

    def test_extract_metadata(self, crawl_service, sample_config):
        """Test metadata extraction."""
        mock_result = MagicMock()
        mock_result.url = "https://example.com/page"
        mock_result.metadata = {
            'title': 'Test Page',
            'description': 'Test description',
            'keywords': 'test, page',
            'author': 'Test Author',
            'language': 'en',
            'content_type': 'text/html'
        }

        metadata = crawl_service._extract_metadata(mock_result, sample_config)

        assert metadata['title'] == 'Test Page'
        assert metadata['description'] == 'Test description'
        assert metadata['keywords'] == 'test, page'
        assert metadata['author'] == 'Test Author'
        assert metadata['language'] == 'en'
        assert metadata['content_type'] == 'text/html'
        assert metadata['domain'] == 'example.com'
        assert metadata['scheme'] == 'https'
        assert 'crawl_config' in metadata

    def test_extract_metadata_disabled(self, crawl_service):
        """Test metadata extraction when disabled in config."""
        config = CrawlConfig(extract_metadata=False)
        mock_result = MagicMock()
        mock_result.url = "https://example.com"
        mock_result.metadata = {'title': 'Test'}

        metadata = crawl_service._extract_metadata(mock_result, config)

        # Should not include metadata fields when disabled
        assert 'title' not in metadata
        assert 'domain' in metadata  # URL info still included
        assert 'crawl_config' in metadata

    def test_extract_links_from_list(self, crawl_service):
        """Test link extraction from list of strings."""
        mock_result = MagicMock()
        mock_result.links = ['https://link1.com', 'https://link2.com', 'https://link1.com']  # Duplicate

        links = crawl_service._extract_links(mock_result)
        assert len(links) == 2  # Duplicates removed
        assert 'https://link1.com' in links
        assert 'https://link2.com' in links

    def test_extract_links_from_dicts(self, crawl_service):
        """Test link extraction from list of dicts."""
        mock_result = MagicMock()
        mock_result.links = [
            {'href': 'https://link1.com'},
            {'href': 'https://link2.com'},
            {'other': 'not-a-link'}
        ]

        links = crawl_service._extract_links(mock_result)
        assert len(links) == 2
        assert 'https://link1.com' in links
        assert 'https://link2.com' in links

    def test_extract_links_failure(self, crawl_service):
        """Test link extraction failure handling."""
        mock_result = MagicMock()
        mock_result.links = None

        links = crawl_service._extract_links(mock_result)
        assert links == []

    def test_generate_content_hash(self, crawl_service):
        """Test content hash generation."""
        content = "Test content for hashing"
        hash1 = crawl_service._generate_content_hash(content)
        hash2 = crawl_service._generate_content_hash(content)

        assert len(hash1) == 64  # SHA256 hex length
        assert hash1 == hash2  # Same content produces same hash

        # Different content produces different hash
        hash3 = crawl_service._generate_content_hash("Different content")
        assert hash1 != hash3

    @pytest.mark.asyncio
    async def test_health_check_not_started(self, crawl_service):
        """Test health check when service not started."""
        assert await crawl_service.health_check() is False

    @pytest.mark.asyncio
    async def test_health_check_started(self, crawl_service):
        """Test health check when service is started."""
        async with crawl_service:
            assert await crawl_service.health_check() is True