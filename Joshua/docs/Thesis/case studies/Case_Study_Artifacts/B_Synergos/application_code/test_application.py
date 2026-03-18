import unittest
import json
from synthesized_application import app

class SynthesizedAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_process_endpoint_success(self):
        response = self.app.post('/process', json={"key": "value"})
        data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 200)
        self.assertIn("processed", data)

    def test_health_check(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data())
        self.assertEqual(data["status"], "healthy")

if __name__ == '__main__':
    unittest.main()