from fastapi import HTTPException, Header, Depends
import hashlib
import sqlite3

DB_PATH = "database.db"

def verify_api_key(x_api_key: str = Header(...)):
    hashed_key = hashlib.sha256(x_api_key.encode()).hexdigest()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT revoked FROM api_keys WHERE hashed_key = ?", (hashed_key,))
    row = cursor.fetchone()
    conn.close()

    if not row or row[0]:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key")

    return True
