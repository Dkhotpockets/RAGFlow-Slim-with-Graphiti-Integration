import unittest
from app import app

class RagflowSlimTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.api_key = "changeme"  # Set to match RAGFLOW_API_KEY

    def test_completion_unauthorized(self):
        resp = self.client.post("/completion", json={"prompt": "test"})
        self.assertEqual(resp.status_code, 401)

    def test_completion_authorized(self):
        resp = self.client.post("/completion", json={"prompt": "test"}, headers={"X-API-KEY": self.api_key})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("response", resp.get_json())

    def test_ingest_missing_file(self):
        resp = self.client.post("/ingest", headers={"X-API-KEY": self.api_key})
        self.assertEqual(resp.status_code, 400)

    def test_retrieval_missing_query(self):
        resp = self.client.post("/retrieval", json={}, headers={"X-API-KEY": self.api_key})
        self.assertEqual(resp.status_code, 400)

if __name__ == "__main__":
    unittest.main()
