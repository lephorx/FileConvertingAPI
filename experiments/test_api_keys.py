#!/usr/bin/env python3
"""
Test script to verify API key authentication works

This script tests the API endpoints with different API keys.
Make sure to run init_db.py first and start the server.

Usage:
    python experiments/test_api_keys.py
"""

import requests
import json
import time
import sys
import os

# Add parent directory to path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger_config import setup_logger
logger = setup_logger(__name__)

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(endpoint, api_key=None, method="GET", **kwargs):
    """Test an endpoint with optional API key"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if api_key:
        headers["X-Api-Key"] = api_key
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, **kwargs)
        elif method == "POST":
            response = requests.post(url, headers=headers, **kwargs)
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else "Non-JSON response",
            "success": response.status_code < 400
        }
        
    except requests.exceptions.ConnectionError:
        return {
            "status_code": None,
            "response": "Connection failed - is the server running?",
            "success": False
        }
    except Exception as e:
        return {
            "status_code": None,
            "response": f"Error: {e}",
            "success": False
        }

def main():
    """Test API key authentication"""
    logger.info("Testing FileConvertor API Key Authentication")
    logger.info(f"Base URL: {BASE_URL}")
    print()
    
    # Test cases
    tests = [
        {
            "name": "Root endpoint without API key",
            "endpoint": "/",
            "api_key": None,
            "expected_status": 200  # Root might not require auth
        },
        {
            "name": "Root endpoint with valid API key",
            "endpoint": "/", 
            "api_key": "sk_test_12345",
            "expected_status": 200
        },
        {
            "name": "Convert endpoint without API key",
            "endpoint": "/convert",
            "api_key": None,
            "method": "POST",
            "expected_status": 401  # Should require auth
        },
        {
            "name": "Convert endpoint with valid API key",
            "endpoint": "/convert",
            "api_key": "sk_test_12345", 
            "method": "POST",
            "expected_status": 422  # No file provided, but auth should pass
        },
        {
            "name": "Convert endpoint with invalid API key",
            "endpoint": "/convert",
            "api_key": "invalid_key_123",
            "method": "POST", 
            "expected_status": 401
        },
        {
            "name": "Convert endpoint with production API key",
            "endpoint": "/convert",
            "api_key": "sk_prod_67890",
            "method": "POST",
            "expected_status": 422  # No file provided, but auth should pass
        }
    ]
    
    # Run tests
    results = []
    for test in tests:
        logger.info(f"Testing: {test['name']}")
        
        result = test_endpoint(
            test["endpoint"],
            test.get("api_key"),
            test.get("method", "GET")
        )
        
        # Check if result matches expectation
        expected = test.get("expected_status")
        actual = result["status_code"]
        
        if actual == expected:
            print(f"  PASS: {actual} (expected {expected})")
        else:
            print(f"  FAIL: {actual} (expected {expected})")
            print(f"     Response: {result['response']}")
        
        results.append({**test, **result})
        print()
        
        # Small delay between requests
        time.sleep(0.1)
    
    # Summary
    passed = sum(1 for r in results if r["status_code"] == r.get("expected_status"))
    total = len(results)
    
    logger.info(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("All tests passed! API key authentication is working correctly.")
    else:
        logger.warning("Some tests failed. Check the server logs for details.")
        
    print()
    logger.info("Next steps:")
    print("  1. Start the server: uvicorn app.main:app --reload")
    print("  2. Test manually: curl -H 'X-Api-Key: sk_test_12345' http://127.0.0.1:8000/")
    print("  3. Use interactive docs: http://127.0.0.1:8000/docs")

if __name__ == "__main__":
    main()