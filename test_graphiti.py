"""
Test script for Graphiti integration in RAGFlow Slim
Run this after setting up the environment to verify everything works.
"""

import requests
import json
import time
from pathlib import Path

# Configuration
API_URL = "http://localhost:5000"
API_KEY = "changeme"
HEADERS = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

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
        
        if response.status_code == 503:
            print("❌ Graphiti is NOT available")
            print(f"   Response: {response.json()}")
            return False
        else:
            print("✅ Graphiti is available")
            return True
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return False


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
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document ingested successfully")
            print(f"   Supabase: {result.get('supabase_response', {}).get('status', 'N/A')}")
            print(f"   Graph: {result.get('graph_response', {}).get('status', 'N/A')}")
            
            if result.get('graph_response', {}).get('status') == 'success':
                print(f"   Episode name: {result['graph_response']['episode_name']}")
                return True
            else:
                print("   ⚠️  Graph extraction may have failed")
                return False
        else:
            print(f"❌ Ingestion failed: {response.status_code}")
            print(f"   Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        return False
    finally:
        # Cleanup
        if temp_file.exists():
            temp_file.unlink()


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
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Hybrid retrieval successful")
            
            vector_count = len(result.get("vector_results", []))
            graph_count = len(result.get("graph_results", []))
            
            print(f"   Vector results: {vector_count}")
            print(f"   Graph results: {graph_count}")
            
            if graph_count > 0:
                print("\n   Sample graph result:")
                print(json.dumps(result["graph_results"][0], indent=4))
            
            return True
        else:
            print(f"❌ Retrieval failed: {response.status_code}")
            print(f"   Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error during retrieval: {e}")
        return False


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
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Graph search successful")
            print(f"   Results count: {result.get('count', 0)}")
            
            if result.get('count', 0) > 0:
                print("\n   Sample result:")
                print(json.dumps(result["results"][0], indent=4))
            
            return True
        else:
            print(f"❌ Graph search failed: {response.status_code}")
            print(f"   Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error during graph search: {e}")
        return False


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
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Temporal query successful")
            print(f"   Entity: {result.get('entity', 'N/A')}")
            print(f"   Results: {len(result.get('results', []))}")
            return True
        else:
            print(f"❌ Temporal query failed: {response.status_code}")
            print(f"   Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error during temporal query: {e}")
        return False


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
    
    total_passed = sum(results.values())
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
