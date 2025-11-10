#!/usr/bin/env python3
"""
Simple rate limiting test

Tests the improved rate limiting functionality by making multiple requests.
Run this after starting the server to verify rate limits work.

Usage:
    python experiments/test_rate_limits.py
"""

import requests
import time
import json
import sys
import os

# Add parent directory to path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger_config import setup_logger
logger = setup_logger(__name__)

BASE_URL = "http://127.0.0.1:8000"

def test_rate_limiting():
    """Test rate limiting with multiple requests"""
    logger.info("Testing Rate Limiting")
    logger.info(f"Server: {BASE_URL}")
    print()
    
    # Use production key with 100 request limit
    api_key = "sk_prod_67890" 
    
    logger.info(f"Testing with API key: {api_key}")
    logger.info("Making multiple requests...")
    print()
    
    success_count = 0
    rate_limited_count = 0
    
    # Make 10 requests to test rate limiting
    for i in range(1, 11):
        try:
            response = requests.get(
                f"{BASE_URL}/",
                headers={"X-Api-Key": api_key},
                timeout=5
            )
            
            print(f"Request {i:2d}: ", end="")
            
            if response.status_code == 200:
                success_count += 1
                print("SUCCESS")
                # Show remaining usage if available
                
            elif response.status_code == 429:
                rate_limited_count += 1
                print("RATE LIMITED")
                try:
                    detail = response.json().get("detail", "Rate limit exceeded")
                    print(f"           {detail}")
                except:
                    pass
                
            else:
                print(f"ERROR ({response.status_code})")
                try:
                    detail = response.json().get("detail", "Unknown error")
                    print(f"           {detail}")
                except:
                    pass
            
        except requests.exceptions.ConnectionError:
            print(f"Request {i:2d}: CONNECTION ERROR")
            print("           Is the server running? Start with:")
            print("           uvicorn app.main:app --reload")
            break
            
        except Exception as e:
            print(f"Request {i:2d}: ERROR - {e}")
        
        # Small delay between requests
        time.sleep(0.2)
    
    print()
    print("Test Results:")
    print(f"   Successful: {success_count}")
    print(f"   Rate limited: {rate_limited_count}")
    
    if rate_limited_count > 0:
        logger.info("Rate limiting is working!")
    elif success_count > 0:
        logger.warning("Rate limit not reached in this test.")
        logger.info("Try making more requests or use a key with lower limit.")
    else:
        logger.error("No successful requests. Check server and database.")

def check_database():
    """Check if database tables exist"""
    logger.info("Checking database setup...")
    
    import sqlite3
    import os
    
    if not os.path.exists("database.db"):
        logger.error("Database not found. Run: python experiments/init_db.py")
        return False
    
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if "api_keys" in tables:
            logger.info("api_keys table exists")
        else:
            logger.error("api_keys table missing")
            
        if "api_key_usage" in tables:
            logger.info("api_key_usage table exists")
        else:
            logger.error("api_key_usage table missing")
        
        # Check API keys
        cursor.execute("SELECT COUNT(*) FROM api_keys")
        key_count = cursor.fetchone()[0]
        logger.info(f"API keys in database: {key_count}")
        
        # Check today's usage
        from datetime import date
        today = date.today().isoformat()
        cursor.execute("SELECT COUNT(*) FROM api_key_usage WHERE usage_date = ?", (today,))
        usage_count = cursor.fetchone()[0]
        logger.info(f"Usage records for today: {usage_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        return False

if __name__ == "__main__":
    logger.info("FileConvertor Rate Limit Tester")
    print("=" * 50)
    
    # Check database first
    if check_database():
        test_rate_limiting()
    
    print()
    logger.info("Next steps:")
    print("   - Reset database: python experiments/init_db.py")
    print("   - Start server: uvicorn app.main:app --reload")
    print("   - View usage: sqlite3 database.db 'SELECT * FROM api_key_usage;'")