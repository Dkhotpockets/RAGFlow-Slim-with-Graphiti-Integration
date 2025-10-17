import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from crawl4ai_source.manager import CrawlJobManager
from crawl4ai_source.models import CrawlJob, CrawlResult, CrawlStatus


@pytest.mark.asyncio
async def test_graphiti_failure_does_not_fail_job():
    manager = CrawlJobManager.__new__(CrawlJobManager)
    manager.supabase = None

    job = CrawlJob(id='job-1', url='https://example.com')
    result = CrawlResult(url='https://example.com', content='hello world')

    with patch('crawl4ai_source.manager.add_episode', new_callable=AsyncMock) as mock_add:
        mock_add.side_effect = Exception('Graphiti error')
        with patch('crawl4ai_source.manager.GRAPHITI_AVAILABLE', True):
            # Should not raise
            await manager._integrate_with_graphiti(job, result)


@pytest.mark.asyncio
async def test_supabase_failure_does_not_fail_job():
    manager = CrawlJobManager.__new__(CrawlJobManager)
    manager.supabase = None

    job = CrawlJob(id='job-2', url='https://example.com')
    result = CrawlResult(url='https://example.com', content='hello world')

    with patch('crawl4ai_source.manager.SUPABASE_AVAILABLE', True), \
         patch('crawl4ai_source.manager.EMBEDDING_AVAILABLE', True), \
         patch('crawl4ai_source.manager.get_embedding_ollama') as mock_emb, \
         patch('crawl4ai_source.manager.add_document_to_supabase') as mock_add:
        mock_emb.return_value = [0.1, 0.2]
        mock_add.side_effect = Exception('Supabase error')
        # Should not raise
        await manager._integrate_with_supabase(job, result)
