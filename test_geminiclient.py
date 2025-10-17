#!/usr/bin/env python3
import os
import sys
import logging
import pytest

logging.basicConfig(level=logging.DEBUG)

print("=" * 60)
print("Testing GeminiClient initialization")
print("=" * 60)

print(f"\n1. Environment variables:")
print(f"  GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY', 'NOT SET')[:20] if os.getenv('GOOGLE_API_KEY') else 'NOT SET'}...")
print(f"  OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', 'NOT SET')}")

try:
    print(f"\n2. Importing GeminiClient...")
    from graphiti_core.llm_client.gemini_client import GeminiClient
    print("   ✅ GeminiClient imported")
    
    print(f"\n3. Importing LLMConfig...")
    from graphiti_core.llm_client import LLMConfig
    print("   ✅ LLMConfig imported")
    
    print(f"\n4. Creating LLMConfig...")
    llm_config = LLMConfig(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="gemini-1.5-flash"
    )
    print(f"   ✅ LLMConfig created: {llm_config}")
    
    print(f"\n5. Creating GeminiClient...")
    client = GeminiClient(config=llm_config)
    print(f"   ✅ GeminiClient created: {client}")
    print("   SUCCESS!")
    
except ModuleNotFoundError as e:
    # Optional dependency missing; instruct pytest to skip module collection
    print(f"   ⚠️ Optional dependency missing: {e}. Skipping GeminiClient initialization tests.")
    pytest.skip(f"Optional dependency missing: {e}", allow_module_level=True)

except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}")
    print(f"   Message: {e}")
    import traceback
    print("\n   Full traceback:")
    traceback.print_exc()
    # Non-module errors are still fatal for this script
    pytest.fail(f"GeminiClient initialization failed with exception: {e}")
