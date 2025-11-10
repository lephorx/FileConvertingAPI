# Experiments

This folder contains scripts and utilities for testing and development of the FileConvertor API.

## Database Initialization

### `init_db.py`

Script to initialize the SQLite database with test API keys.

**Usage:**
```powershell
# PowerShell
python experiments/init_db.py

# Or from experiments folder
cd experiments
python init_db.py
```

```bash
# Bash
python experiments/init_db.py
```

**What it does:**
- Creates `database.db` in the project root
- Sets up the `api_keys` table according to `schema.sql`
- Adds three test API keys:
  - `sk_test_12345` - Development key (1000 requests/day)
  - `sk_prod_67890` - Production-like key (100 requests/day)
  - `sk_admin_99999` - Admin key (10000 requests/day)

**Test the API keys:**
```bash
# Using curl
curl -H "X-Api-Key: sk_test_12345" -X POST -F "file=@test.mp4" http://127.0.0.1:8000/convert

# Using the interactive docs
# Go to http://127.0.0.1:8000/docs
# Click the lock icon and enter: sk_test_12345
```

## Database Schema

The database uses the schema defined in `../schema.sql`. Key features:

- **Hashed API keys** - Keys are stored as SHA256 hashes
- **Permissions** - Control what endpoints each key can access
- **Rate limiting** - Configurable request limits per key
- **Revocation** - Keys can be disabled without deletion

## Development Workflow

1. **Initialize database:**
   ```powershell
   python experiments/init_db.py
   ```

2. **Start API server:**
   ```powershell
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

3. **Test API:**
   ```powershell
   curl -H "X-Api-Key: sk_test_12345" http://127.0.0.1:8000/
   ```

## Security Notes

- **WARNING:** Test keys only - The keys in this script are for development
- **Production keys** - Generate secure keys for production deployment
- **Database reset** - The script can reset the database if needed
- **Logging** - All API key usage should be logged in production