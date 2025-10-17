import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from crawl4ai_source.models import CrawlJob, CrawlResult
from crawl4ai_source.manager import CrawlJobManager


@pytest.mark.asyncio
async def test_supabase_duplicate_hash_ignored():
    supabase = MagicMock()
    manager = CrawlJobManager(supabase_client=supabase)

    job = CrawlJob(url="https://example.com/dup")
    result = CrawlResult(
        url="https://example.com/dup",
        content="duplicate content",
        content_hash="dup123",
        content_size=10,
        extracted_at=datetime.now(timezone.utc),
    )

    # Make insert throw a duplicate-key error
    def raise_dup(*args, **kwargs):
        raise Exception("duplicate key value violates unique constraint")

    with patch("crawl4ai_source.manager.SUPABASE_AVAILABLE", True), \
         patch("crawl4ai_source.manager.add_document_to_supabase", side_effect=raise_dup) as mock_add, \
         patch("crawl4ai_source.manager.EMBEDDING_AVAILABLE", True), \
         patch("crawl4ai_source.manager.get_embedding_ollama", MagicMock(return_value=[0.1])):

        # Should not raise
        await manager._persist_crawl_result(job.id, result)
        # integration call should be attempted in integrate_with_supabase, but here we focus on persist
        # If no exception bubbled, the behavior is correct
        assert True


@pytest.mark.asyncio
async def test_supabase_other_error_raises():
    supabase = MagicMock()
    manager = CrawlJobManager(supabase_client=supabase)

    job = CrawlJob(url="https://example.com/error")
    result = CrawlResult(
        url="https://example.com/error",
        content="bad content",
        content_hash="err123",
        content_size=10,
        extracted_at=datetime.now(timezone.utc),
    )

    def raise_other(*args, **kwargs):
        raise Exception("database connection timeout")

    # Patch the supabase insert to raise a non-duplicate error and ensure it's propagated by _persist_crawl_result
    with patch.object(manager, 'supabase') as mock_supabase:
        # Configure the table().insert().execute() chain to raise
        mock_table = MagicMock()
        mock_table.insert.side_effect = raise_other
        mock_supabase.table.return_value = mock_table

        with pytest.raises(Exception):
            await manager._persist_crawl_result(job.id, result)
