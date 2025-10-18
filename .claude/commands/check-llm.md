---
description: Verify LLM provider configuration and availability
---

Check the current LLM provider configuration and test connectivity:

1. Check the health endpoint to see which provider is active:
```bash
curl http://localhost:5000/health
```

2. Review the llm_provider.py configuration to see:
   - Which provider is configured (auto, ollama, google, openai)
   - Auto-detection priority order
   - Current model selections

3. Check environment variables:
   - LLM_PROVIDER
   - OLLAMA_HOST (if using Ollama)
   - GOOGLE_API_KEY (if using Google)
   - OPENAI_API_KEY (if using OpenAI)

4. If using Ollama, test connectivity:
```bash
curl http://localhost:11434/api/tags
```

Show me:
- Active LLM provider and models
- Whether the provider is reachable
- Embeddings configuration
- Any configuration warnings or errors
- Important: Note if using Ollama with Graphiti (requires OpenAI for entity extraction)
