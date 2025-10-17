from unittest.mock import patch

import pytest

from crawl4ai_source.manager import add_document_to_supabase


def test_supabase_add_document_called():
    with patch('crawl4ai_source.manager.add_document_to_supabase') as mock_add:
        mock_add.return_value = {'id': 'doc-123'}
        result = mock_add('doc-text', {'meta': 'value'})
        assert mock_add.called
        assert result['id'] == 'doc-123'
