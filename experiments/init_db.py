#!/usr/bin/env python3
"""
Database initialization script for FileConvertor API testing

This script creates the SQLite database and populates it with test API keys.
Run this before starting the API server for the first time.

Usage:
    python experiments/init_db.py
"""

import sqlite3
import hashlib
import os
import sys
from datetime import datetime

# Add parent directory to path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger_config import setup_logger
logger = setup_logger(__name__)

DB_PATH = "database.db"

def create_database():
    """Create the database and tables"""
    logger.info("Creating database...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create api_keys table (from schema.sql)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            hashed_key TEXT NOT NULL UNIQUE,
            permissions TEXT DEFAULT 'convert',
            revoked BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            has_rate_limit BOOLEAN DEFAULT TRUE,
            rate_limit INTEGER DEFAULT 100
        )
    """)
    
    # Create usage tracking table with proper PRIMARY KEY
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_key_usage (
            hashed_key CHAR(64) NOT NULL,
            usage_date DATE NOT NULL,
            usage_count INTEGER DEFAULT 0,
            PRIMARY KEY (hashed_key, usage_date)
        )
    """)
    
    # Create index for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_usage_date_key 
        ON api_key_usage(hashed_key, usage_date)
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database created successfully")

def add_test_api_keys():
    """Add test API keys to the database"""
    logger.info("Adding test API keys...")
    
    test_keys = [
        {
            "key": "sk_test_12345",
            "permissions": "convert",
            "rate_limit": 1000,
            "description": "Test key for development"
        },
        {
            "key": "sk_prod_67890", 
            "permissions": "convert",
            "rate_limit": 1,
            "description": "Production-like key with limits"
        },
        {
            "key": "sk_admin_99999",
            "permissions": "convert,admin",
            "rate_limit": 10000,
            "description": "Admin key with high limits"
        }
    ]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for key_info in test_keys:
        # Hash the API key
        hashed_key = hashlib.sha256(key_info["key"].encode()).hexdigest()
        
        try:
            cursor.execute("""
                INSERT INTO api_keys (hashed_key, permissions, rate_limit)
                VALUES (?, ?, ?)
            """, (hashed_key, key_info["permissions"], key_info["rate_limit"]))
            
            logger.info(f"Added: {key_info['key']} - {key_info['description']}")
            
        except sqlite3.IntegrityError:
            logger.warning(f"Key already exists: {key_info['key']}")
    
    conn.commit()
    conn.close()

def list_api_keys():
    """List all API keys in the database (for verification)"""
    logger.info("Current API keys in database:")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, hashed_key, permissions, revoked, rate_limit, created_at
        FROM api_keys
        ORDER BY id
    """)
    
    rows = cursor.fetchall()
    
    if not rows:
        logger.info("No API keys found")
        conn.close()
        return
    
    print(f"{'ID':<4} {'Hash (first 12)':<15} {'Permissions':<15} {'Revoked':<8} {'Rate Limit':<12} {'Created'}")
    print("-" * 80)
    
    for row in rows:
        id_, hashed_key, permissions, revoked, rate_limit, created_at = row
        hash_preview = hashed_key[:12] + "..."
        revoked_status = "Yes" if revoked else "No"
        created_short = created_at[:16] if created_at else "N/A"
        
        print(f"{id_:<4} {hash_preview:<15} {permissions:<15} {revoked_status:<8} {rate_limit:<12} {created_short}")
    
    # Show usage stats for today
    today = datetime.now().date().isoformat()
    cursor.execute("""
        SELECT ak.hashed_key, aku.usage_count 
        FROM api_keys ak
        LEFT JOIN api_key_usage aku ON ak.hashed_key = aku.hashed_key AND aku.usage_date = ?
        ORDER BY ak.id
    """, (today,))
    
    usage_rows = cursor.fetchall()
    
    if usage_rows:
        print(f"\nToday's Usage ({today}):")
        print(f"{'Hash (first 12)':<15} {'Usage Count':<12}")
        print("-" * 30)
        for hashed_key, usage_count in usage_rows:
            hash_preview = hashed_key[:12] + "..."
            usage_display = usage_count if usage_count else 0
            print(f"{hash_preview:<15} {usage_display:<12}")
    
    conn.close()

def reset_database():
    """Delete and recreate the database"""
    if os.path.exists(DB_PATH):
        logger.info(f"Removing existing database: {DB_PATH}")
        os.remove(DB_PATH)
    
    create_database()
    add_test_api_keys()

def main():
    """Main initialization function"""
    logger.info("FileConvertor Database Initialization")
    logger.info(f"Database path: {os.path.abspath(DB_PATH)}")
    print()
    
    if os.path.exists(DB_PATH):
        response = input("Database already exists. Reset it? (y/N): ").lower().strip()
        if response in ['y', 'yes']:
            reset_database()
        else:
            logger.info("Using existing database...")
    else:
        create_database()
        add_test_api_keys()
    
    print()
    list_api_keys()
    
    print()
    print("Test API Keys:")
    print("  Development: sk_test_12345")
    print("  Production:  sk_prod_67890") 
    print("  Admin:       sk_admin_99999")
    print()
    print("Usage examples:")
    print("  curl -H 'X-Api-Key: sk_test_12345' http://127.0.0.1:8000/convert")
    print("  Or use the /docs interface with 'X-Api-Key' header")
    print()
    logger.info("Database initialization complete!")

if __name__ == "__main__":
    main()