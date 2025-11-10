
-- Schema for API keys 
-- You can expand / modify as needed
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    hashed_key CHAR(64) NOT NULL,
    permissions TEXT DEFAULT 'convert',
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    has_rate_limit BOOLEAN DEFAULT TRUE, -- enable/disable if user has rate limit
    rate_limit INTEGER DEFAULT 100 -- requests per day

);
