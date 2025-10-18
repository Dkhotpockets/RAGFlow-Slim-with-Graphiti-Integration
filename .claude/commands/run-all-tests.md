---
description: Run all tests including unit and contract tests
---

Run the complete test suite for RAGFlow Slim:

1. First run unit tests (no external dependencies):
```bash
pytest -q -m "not contract"
```

2. Then run contract tests (require external services):
```bash
pytest -q -m contract
```

3. Generate a summary of test results

Show me:
- Total tests run
- Passed/failed/skipped counts
- Any test failures with details
- Coverage information if available
