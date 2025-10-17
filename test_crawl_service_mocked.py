import asyncio
import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from crawl4ai_source.service import CrawlService
from crawl4ai_source.models import CrawlConfig


class FakeResult:
    def __init__(self, url='https://example.com', html='<html><title>Test</title><body>Hi</body></html>'):
        self.url = url
        self.html = html
        self.metadata = {'title': 'Test', 'description': 'desc'}
        self.links = ['https://example.com/page1']
        self.markdown = None


@pytest.mark.asyncio
async def test_crawl_url_extracts_content():
    service = CrawlService()

    fake_crawler = MagicMock()
    fake_crawler.arun = AsyncMock(return_value=FakeResult())

    service._crawler = fake_crawler

    config = CrawlConfig(max_depth=1)

    result = await service.crawl_url('https://example.com', config)

    assert result.url == 'https://example.com'
    assert 'Test' in result.title
    assert 'Hi' in result.content
    assert isinstance(result.links, list)
