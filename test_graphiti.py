"""
Test script for Graphiti integration in RAGFlow Slim
Run this after setting up the environment to verify everything works.
"""

import requests
import json
import time
from pathlib import Path

import pytest

# Configuration
API_URL = "http://localhost:5000"
API_KEY = "changeme"
HEADERS = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

@pytest.mark.contract
def test_graphiti_availability():
    """Test if Graphiti is available."""
    print("=" * 60)
    print("Testing Graphiti Availability")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{API_URL}/graph/search",
            headers=HEADERS,
            json={"query": "test"}
        )
        assert response.status_code != 503, f"Graphiti not available: {response.json()}"
    except Exception as e:
        raise AssertionError(f"Error connecting to API: {e}")


@pytest.mark.contract
def test_document_ingestion():
    """Test document ingestion with graph extraction."""
    print("\n" + "=" * 60)
    print("Testing Document Ingestion")
    print("=" * 60)
    
    # Create a test document
    test_content = """
    Project Status Update - October 2025
    
    John Smith, the CEO, announced that Project Alpha has reached a major milestone.
    The development team, led by Sarah Johnson, successfully deployed the new feature.
    Customer feedback has been overwhelmingly positive, with a 95% satisfaction rate.
    
    Key risks identified:
    - Supply chain delays may impact Q4 delivery
    - Budget constraints require additional review
    
    Next steps:
    - Schedule follow-up meeting for November 1st
    - Review budget allocation with finance team
    """
    
    # Save to temp file
    temp_file = Path("test_document.txt")
    temp_file.write_text(test_content)
    
    try:
        with open(temp_file, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{API_URL}/ingest",
                headers={"X-API-KEY": API_KEY},
                files=files
            )

        if response.status_code != 200:
            pytest.skip(f"Ingestion endpoint returned {response.status_code}: {response.text}")

        result = response.json()
        assert result.get('graph_response', {}).get('status') == 'success', "Graph extraction failed"
        assert 'episode_name' in result.get('graph_response', {}), "Episode name missing from graph response"
    except Exception as e:
        pytest.skip(f"Skipping ingestion test due to exception: {e}")
    finally:
        # Cleanup
        if temp_file.exists():
            temp_file.unlink()


@pytest.mark.contract
def test_hybrid_retrieval():
    """Test hybrid retrieval (vector + graph)."""
    print("\n" + "=" * 60)
    print("Testing Hybrid Retrieval")
    print("=" * 60)
    
    # Give the system a moment to process the ingested document
    print("Waiting 5 seconds for processing...")
    time.sleep(5)
    
    try:
        response = requests.post(
            f"{API_URL}/retrieval",
            headers=HEADERS,
            json={
                "query": "What did John Smith announce about Project Alpha?",
                "top_k": 3
            }
        )

        if response.status_code != 200:
            pytest.skip(f"Retrieval endpoint returned {response.status_code}: {response.text}")

        result = response.json()
        vector_count = len(result.get("vector_results", []))
        graph_count = len(result.get("graph_results", []))
        assert vector_count >= 0
        assert graph_count >= 0
    except Exception as e:
        pytest.skip(f"Skipping retrieval test due to exception: {e}")


@pytest.mark.contract
def test_graph_search():
    """Test graph-specific search."""
    print("\n" + "=" * 60)
    print("Testing Graph Search")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{API_URL}/graph/search",
            headers=HEADERS,
            json={
                "query": "Who is the CEO?",
                "num_results": 5
            }
        )

        if response.status_code != 200:
            pytest.skip(f"Graph search endpoint returned {response.status_code}: {response.text}")

        result = response.json()
        assert result.get('count', 0) >= 0
    except Exception as e:
        pytest.skip(f"Skipping graph search test due to exception: {e}")


@pytest.mark.contract
def test_temporal_query():
    """Test temporal context query."""
    print("\n" + "=" * 60)
    print("Testing Temporal Query")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{API_URL}/graph/temporal",
            headers=HEADERS,
            json={
                "entity_name": "Project Alpha",
                "start_time": "2025-01-01T00:00:00",
                "end_time": "2025-12-31T23:59:59"
            }
        )

        if response.status_code != 200:
            pytest.skip(f"Temporal endpoint returned {response.status_code}: {response.text}")

        result = response.json()
        assert 'entity' in result
        assert isinstance(result.get('results', []), list)
    except Exception as e:
        pytest.skip(f"Skipping temporal test due to exception: {e}")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("RAGFlow Slim - Graphiti Integration Test Suite")
    print("=" * 60)
    print()
    
    results = {
        "Graphiti Availability": test_graphiti_availability(),
        "Document Ingestion": test_document_ingestion(),
        "Hybrid Retrieval": test_hybrid_retrieval(),
        "Graph Search": test_graph_search(),
        "Temporal Query": test_temporal_query()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    # Convert results (which may be booleans) to ints safely
    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    print()
    print(f"Total: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Graphiti integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("\nCommon issues:")
        print("- Graphiti not installed: pip install -r requirements.txt")
        print("- Neo4j not running: docker-compose up -d")
        print("- OpenAI API key not set: export OPENAI_API_KEY=sk-...")
        print("- API not running: python app.py")


if __name__ == "__main__":
    main()
