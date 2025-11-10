
-- FileConvertor API Database Schema
-- SQLite-compatible schema for API key management and rate limiting

-- Main API keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    hashed_key CHAR(64) NOT NULL UNIQUE,
    permissions TEXT DEFAULT 'convert',
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    has_rate_limit BOOLEAN DEFAULT TRUE, -- enable/disable rate limiting per key
    rate_limit INTEGER DEFAULT 100      -- requests per day
);

-- Usage tracking table for rate limiting
CREATE TABLE IF NOT EXISTS api_key_usage (
    hashed_key CHAR(64) NOT NULL,
    usage_date DATE NOT NULL,
    usage_count INTEGER DEFAULT 0,
    PRIMARY KEY (hashed_key, usage_date)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_usage_date_key 
ON api_key_usage(hashed_key, usage_date);

CREATE INDEX IF NOT EXISTS idx_api_keys_hashed 
ON api_keys(hashed_key);

-- Comments for future reference:
-- 1. hashed_key: SHA256 hash of the actual API key
-- 2. permissions: comma-separated list (e.g., 'convert', 'convert,admin')
-- 3. usage_date: ISO date format (YYYY-MM-DD)
-- 4. Composite primary key ensures one record per key per day
-- 5. ON CONFLICT used in app for atomic increment operations
