# FileConvertor

A small file conversion application with a Python backend and an optional Next.js (React) frontend. The backend exposes a simple REST API to upload media files and convert them using FFmpeg; the frontend is intended as a user-friendly upload UI.

This README explains the repository layout, how to run the backend and frontend for development on Windows (PowerShell), and additional notes for Docker-based local development.

## Table of contents

- [Features](#features)
- [Repository layout](#repository-layout)
- [Assumptions](#assumptions)
- [Prerequisites](#prerequisites)
- [Quick start — Backend (development)](#quick-start---backend-development)
- [Quick start — Frontend (development)](#quick-start---frontend-development)
- [Run both services (recommended for dev)](#run-both-services-recommended-for-dev)
- [Testing](#testing)
- [Contribution & notes](#contribution--notes)
- [License](#license)

## Features

- Convert common audio/video formats supported by FFmpeg (mp4, mkv, avi, wav, mp3, etc.)
- Simple REST API with automatic docs (if using FastAPI)
- Clean logging configured via `logger_config.py`
- Designed to offload heavy work to workers (future improvement)

## Repository layout

Top-level files and directories in this repository (as of now):

```
FileConvertor/
├── README.md
├── requirements.txt      # Python dependencies for the backend
├── app/                  # Python backend source (entry: app/main.py)
│   ├── main.py
│   └── ...
├── utlis/                # (typo preserved) logging/config helpers
│   └── logger_config.py
└── frontend/             # (optional) Next.js frontend (may not exist yet)
```

Update: If you migrate to a monorepo layout later, a recommended structure is `backend/` and `frontend/` top-level folders.

## Assumptions

- The backend is implemented in Python and exposes an ASGI app (commonly FastAPI) at `app/main.py` as `app`.
- FFmpeg is used for conversions and must be installed on the host system.
- The frontend (optional) will be a Next.js TypeScript app living in `frontend/`.

If any of these assumptions are incorrect for your project, tell me which parts differ and I will adapt the instructions.

## Prerequisites

- Python 3.8+ installed and available on PATH
- Node.js + npm or pnpm (if you plan to run the frontend)
- FFmpeg installed and available on PATH

On Windows you can install FFmpeg via winget or a package manager of your choice. Example (PowerShell):

```powershell
# Install via winget (if available)
winget install --id=Gyan.FFmpeg -e --source=winget
# or download a static build from https://ffmpeg.org/
```

## Quick start — Backend (development)

These instructions include both PowerShell (Windows) and Bash (Linux/macOS). Run the commands appropriate for your shell.

PowerShell (Windows)

```powershell
# 1) Create and activate a venv
python -m venv .venv
.\.venv\Scripts\Activate

# 2) Install dependencies (uses top-level requirements.txt)
pip install -r requirements.txt

# 3) Run the backend (assumes FastAPI + uvicorn and that app/main.py exposes `app`)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# After this, API docs (if FastAPI) are available at http://127.0.0.1:8000/docs
```

Bash (Linux / macOS)

```bash
# 1) Create and activate a venv
python3 -m venv .venv
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run the backend (assumes FastAPI + uvicorn and that app/main.py exposes `app`)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# After this, API docs (if FastAPI) are available at http://127.0.0.1:8000/docs
```

Notes:
- If your entrypoint is `main.py` in the repository root, run `uvicorn main:app --reload` instead.
- If you don't use FastAPI, substitute the appropriate run command for your framework.

## Quick start — Frontend (development)

If you add or have a Next.js frontend in `frontend/`, use the commands for your shell.

PowerShell

```powershell
cd frontend
npm install
npm run dev
```

Bash

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 to view the frontend (default Next.js port).

If you want the frontend to call the backend during development, either:
- Use full URLs in the frontend (e.g. `http://localhost:8000/api/convert`), or
- Add a Next.js rewrites/proxy or configure environment variables in `next.config.js`.

## Run both services (recommended for dev)

The simplest approach is to run the backend and frontend in separate terminals. Choose the commands for your shell.

PowerShell (two terminals)

Terminal 1 — backend:

```powershell
.\.venv\Scripts\Activate
uvicorn app.main:app --reload --port 8000
```

Terminal 2 — frontend:

```powershell
cd frontend
npm run dev
```

Bash (two terminals)

Terminal 1 — backend:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Terminal 2 — frontend:

```bash
cd frontend
npm run dev
```

Optional: use `docker-compose` to run the backend, frontend, and any worker/storage services together. If you'd like, I can add a `docker-compose.yml` that uses one image for the backend and one for the frontend.

## API contract / example

If the backend is FastAPI and exposes a `/convert` endpoint that accepts multipart file uploads, a minimal curl example to upload a file would be:

```bash
curl -X POST -F "file=@path/to/file.mp4" -F "output_format=mp3" \
  http://127.0.0.1:8000/convert --output result.mp3
```

Replace host/port and parameter names according to your actual API implementation.

## Testing

- Add unit tests under `app/tests` and use pytest to run them.

Example (PowerShell):

```powershell
.\.venv\Scripts\Activate
pip install pytest
pytest -q
```

Example (Bash):

```bash
source .venv/bin/activate
pip install pytest
pytest -q
```

## Contribution & notes

- Keep conversion logic separated from I/O so it can be tested without filesystem or network calls.
- Move heavy/long conversions to background workers (Celery / RQ) and return a job id from the API.
- Add file size limits and format validation to avoid DoS by huge uploads.

If you'd like, I can:
- scaffold a minimal `app/main.py` (FastAPI) and a `frontend` upload page (Next.js), or
- add a `docker-compose.yml` for local development.

Tell me which of those you'd like next and I will implement it.

## License

MIT. See `LICENSE` if present.

---

If any of the commands or paths above don't match your current project layout, tell me what differs and I'll adapt the README and scripts accordingly.