import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from crawl4ai_source.models import CrawlJob, CrawlResult
from crawl4ai_source.manager import CrawlJobManager


@pytest.mark.asyncio
async def test_integrate_with_supabase_calls_add_document():
    supabase = MagicMock()
    manager = CrawlJobManager(supabase_client=supabase)

    job = CrawlJob(url="https://example.com/vec")
    result = CrawlResult(
        url="https://example.com/vec",
        title="Vector Page",
        content="This is vector content",
        content_hash="vh123",
        content_size=123,
        crawl_time=0.5,
        extracted_at=datetime.now(timezone.utc),
    )

    # Prepare mocks
    embedding = [0.1, 0.2, 0.3]
    mock_get_embedding = MagicMock(return_value=embedding)
    mock_add_doc = MagicMock(return_value={"id": "vh123"})

    with patch("crawl4ai_source.manager.SUPABASE_AVAILABLE", True), \
         patch("crawl4ai_source.manager.EMBEDDING_AVAILABLE", True), \
         patch("crawl4ai_source.manager.get_embedding_ollama", mock_get_embedding), \
         patch("crawl4ai_source.manager.add_document_to_supabase", mock_add_doc):

        # Act
        await manager._integrate_with_supabase(job, result)

        # Assert embedding and add_document called
        mock_get_embedding.assert_called_once_with(result.content)
        mock_add_doc.assert_called_once()
        called_args, called_kwargs = mock_add_doc.call_args
        # content should be passed as first positional arg
        assert called_args[0] == result.content
        metadata = called_kwargs.get("metadata")
        assert metadata["source_url"] == result.url
        assert metadata["crawl_job_id"] == job.id
        assert metadata["content_hash"] == result.content_hash


@pytest.mark.asyncio
async def test_integrate_with_supabase_handles_exception():
    supabase = MagicMock()
    manager = CrawlJobManager(supabase_client=supabase)

    job = CrawlJob(url="https://example.com/vec")
    result = CrawlResult(
        url="https://example.com/vec",
        content="This will fail",
        content_hash="vh_fail",
        content_size=10,
        extracted_at=datetime.now(timezone.utc),
    )

    mock_get_embedding = MagicMock(return_value=[0.0])

    def raise_on_add(*args, **kwargs):
        raise RuntimeError("Supabase write failure")

    with patch("crawl4ai_source.manager.SUPABASE_AVAILABLE", True), \
         patch("crawl4ai_source.manager.EMBEDDING_AVAILABLE", True), \
         patch("crawl4ai_source.manager.get_embedding_ollama", mock_get_embedding), \
         patch("crawl4ai_source.manager.add_document_to_supabase", side_effect=raise_on_add) as mock_add:

        # Should not raise despite underlying client error
        await manager._integrate_with_supabase(job, result)

        mock_get_embedding.assert_called_once()
        assert mock_add.called
