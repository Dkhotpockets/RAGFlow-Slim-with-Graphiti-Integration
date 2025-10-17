#!/usr/bin/env python3
import os
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

print("=" * 60)
print("Testing full Graphiti + Gemini workflow")
print("=" * 60)

try:
    print("\n1. Importing graphiti_client module...")
    from graphiti_client import add_episode
    print("   ✅ graphiti_client imported")
    
    print("\n2. Testing add_episode() with Gemini backend...")
    result = add_episode(
        name="Test Episode with Gemini",
        episode_body="Machine learning and artificial intelligence are transforming industries. Gemini models from Google provide cost-effective entity extraction.",
        source_description="gemini-test"
    )
    print(f"   Result: {result}")
    print("   ✅ SUCCESS!")
    
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}")
    print(f"   Message: {e}")
    import traceback
    print("\n   Full traceback:")
    traceback.print_exc()
    sys.exit(1)
