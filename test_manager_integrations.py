import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from crawl4ai_source.manager import CrawlJobManager, add_episode, add_document_to_supabase
from crawl4ai_source.models import CrawlJob, CrawlResult, CrawlConfig, CrawlStatus


@pytest.mark.asyncio
async def test_integrate_with_graphiti_calls_add_episode():
    manager = CrawlJobManager.__new__(CrawlJobManager)
    manager.supabase = None

    job = CrawlJob(id='job-1', url='https://example.com')
    result = CrawlResult(url='https://example.com', content='hello world')

    with patch('crawl4ai_source.manager.add_episode', new_callable=AsyncMock) as mock_add:
        # Graphiti available mock - ensure function returns a success dict
        mock_add.return_value = {'status': 'success'}
        with patch('crawl4ai_source.manager.GRAPHITI_AVAILABLE', True):
            await manager._integrate_with_graphiti(job, result)
            # Even if content is small, add_episode should be called
            assert mock_add.called


@pytest.mark.asyncio
async def test_store_result_in_supabase_calls_client():
    manager = CrawlJobManager.__new__(CrawlJobManager)
    manager.supabase = None

    job = CrawlJob(id='job-2', url='https://example.com')
    result = CrawlResult(url='https://example.com', content='hello world')

    # Patch supabase availability and embedding
    with (
        patch('crawl4ai_source.manager.SUPABASE_AVAILABLE', True),
        patch('crawl4ai_source.manager.EMBEDDING_AVAILABLE', True),
        patch('crawl4ai_source.manager.get_embedding_ollama') as mock_emb,
        patch('crawl4ai_source.manager.add_document_to_supabase') as mock_add,
    ):
        mock_emb.return_value = [0.1, 0.2, 0.3]
        mock_add.return_value = {'id': 'doc-1'}
        # Call the supabase integration method
        await manager._integrate_with_supabase(job, result)
        assert mock_add.called
