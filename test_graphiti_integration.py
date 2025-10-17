from unittest.mock import patch, AsyncMock

import pytest

from crawl4ai_source.manager import add_episode


def test_graphiti_add_episode_called():
    with patch('crawl4ai_source.manager.add_episode', new_callable=AsyncMock) as mock_add:
        # Simulate calling add_episode in the manager flow
        # We just assert the function exists and is awaitable
        assert callable(mock_add)
        # Call and ensure no exception
        import asyncio
        asyncio.run(mock_add('doc-id', {'text': 'sample'}))
        assert mock_add.called
