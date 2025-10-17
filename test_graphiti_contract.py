import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

import pytest

from crawl4ai_source.models import CrawlJob, CrawlResult, CrawlConfig
from crawl4ai_source.manager import CrawlJobManager


@pytest.mark.asyncio
async def test_integrate_with_graphiti_calls_add_episode():
    # Arrange: create manager with a fake supabase client
    supabase = MagicMock()
    manager = CrawlJobManager(supabase_client=supabase)

    # Create a job and a crawl result
    job = CrawlJob(url="https://example.com/test")
    result = CrawlResult(
        url="https://example.com/test",
        title="Test Page",
        content="<html><body>Hello Graphiti</body></html>",
        content_hash="hash123",
        content_size=42,
        crawl_time=0.12,
        extracted_at=datetime.now(timezone.utc),
    )

    # Patch the module-level GRAPHITI_AVAILABLE flag and add_episode function
    async_mock = AsyncMock(return_value={"status": "success"})
    with patch("crawl4ai_source.manager.GRAPHITI_AVAILABLE", True), \
         patch("crawl4ai_source.manager.add_episode", async_mock):

        # Act: call the integration method
        await manager._integrate_with_graphiti(job, result)

    # Assert: add_episode was awaited once with expected arguments
    async_mock.assert_awaited_once()
    # Inspect the awaited call kwargs
    call = async_mock.call_args
    called_kwargs = call.kwargs if call else {}
    assert "name" in called_kwargs
    assert called_kwargs.get("episode_body", "").startswith("<html>")
    assert called_kwargs.get("source_description", "").startswith("Crawled content from")
    assert called_kwargs.get("reference_time") == result.extracted_at
