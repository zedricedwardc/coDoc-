import unittest
import json
from app import app

class AnalyzeEndpointTestCase(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_short_code(self):
        short_code = "def add(a, b): return a + b"
        response = self.client.post("/api/analyze", json={"code": short_code})
        
        # Check if status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Extract JSON data
        data = response.get_json()
        
        # Check for necessary fields
        self.assertIn("native_analysis", data, "Missing native analysis in response.")
        self.assertIn("ai_insights", data, "Missing AI insights in response.")

    def test_medium_code(self):
        medium_code = """
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            return False
    return True

primes = [i for i in range(100) if is_prime(i)]
print(primes)
"""
        response = self.client.post("/api/analyze", json={"code": medium_code})
        
        # Check if status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Extract JSON data
        data = response.get_json()

        # Check for necessary fields and conditions
        self.assertIn("native_analysis", data, "Missing native analysis in response.")
        self.assertIn("ai_insights", data, "Missing AI insights in response.")
        self.assertIn("functions", data["native_analysis"], "Missing functions analysis in native analysis.")

    def test_long_code(self):
        long_code = "\n".join([
            "def fib(n):",
            "    if n <= 1: return n",
            "    return fib(n-1) + fib(n-2)",
        ] * 20)  # Repeat the code to make it long

        response = self.client.post("/api/analyze", json={"code": long_code})
        
        # Check if status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Extract JSON data
        data = response.get_json()

        # Check for necessary fields and conditions
        self.assertIn("native_analysis", data, "Missing native analysis in response.")
        self.assertIn("ai_insights", data, "Missing AI insights in response.")
        self.assertIn("time_complexity", data["native_analysis"], "Missing time complexity analysis in native analysis.")

if __name__ == "__main__":
    unittest.main()
