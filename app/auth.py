from fastapi import HTTPException, Header
import hashlib, sqlite3, logging
from datetime import date

DB_PATH = "database.db"
logger = logging.getLogger(__name__)

def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key and enforce daily rate limits"""
    hashed_key = hashlib.sha256(x_api_key.encode()).hexdigest()
    usage_count = 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT revoked, has_rate_limit, rate_limit, permissions 
        FROM api_keys WHERE hashed_key = ?
    """, (hashed_key,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid API key")

    revoked, has_rate_limit, rate_limit, permissions = row
    if revoked:
        conn.close()
        raise HTTPException(status_code=401, detail="API key revoked")

    if has_rate_limit and rate_limit:
        usage_count = get_daily_usage(cursor, hashed_key)
        if usage_count >= rate_limit:
            conn.close()
            logger.warning(f"Rate limit exceeded ({usage_count}/{rate_limit}) for key {hashed_key[:8]}...")
            raise HTTPException(status_code=429, detail="Daily rate limit reached")
        increment_usage(cursor, hashed_key)
        conn.commit()

    conn.close()

    return {
        "permissions": permissions,
        "usage_remaining": (rate_limit - usage_count - 1) if has_rate_limit else None
    }


def get_daily_usage(cursor, hashed_key):
    today = date.today().isoformat()
    cursor.execute("""
        SELECT usage_count FROM api_key_usage
        WHERE hashed_key = ? AND usage_date = ?
    """, (hashed_key, today))
    row = cursor.fetchone()
    return row[0] if row else 0


def increment_usage(cursor, hashed_key):
    today = date.today().isoformat()
    cursor.execute("""
        INSERT INTO api_key_usage (hashed_key, usage_date, usage_count)
        VALUES (?, ?, 1)
        ON CONFLICT(hashed_key, usage_date)
        DO UPDATE SET usage_count = usage_count + 1
    """, (hashed_key, today))


def reset_daily_usage():
    """Clean up old usage records (run daily via cron or scheduler)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM api_key_usage WHERE usage_date < date('now', '-7 days')")
    conn.commit()
    conn.close()
