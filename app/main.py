from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import os
import uuid
import asyncio
from datetime import datetime, time
from utils.logger_config import setup_logger
from .auth import verify_api_key, reset_daily_usage

app = FastAPI(title="Media File Converter")

logger = setup_logger()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "converted")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Background task for daily cleanup
async def daily_cleanup_task():
    """Background task that runs daily cleanup at 2 AM"""
    while True:
        now = datetime.now()
        # Calculate seconds until 2 AM tomorrow
        target_time = now.replace(hour=2, minute=0, second=0, microsecond=0)
        if target_time <= now:
            target_time = target_time.replace(day=target_time.day + 1)
        
        sleep_seconds = (target_time - now).total_seconds()
        
        logger.info(f"Next cleanup scheduled at {target_time} (in {sleep_seconds/3600:.1f} hours)")
        await asyncio.sleep(sleep_seconds)
        
        try:
            reset_daily_usage()
            logger.info("Daily usage cleanup completed")
        except Exception as e:
            logger.error(f"Daily cleanup failed: {e}")

@app.on_event("startup")
async def startup_event():
    """Start background tasks when the app starts"""
    logger.info("Starting FileConvertor API...")
    logger.info("Starting daily cleanup scheduler...")
    asyncio.create_task(daily_cleanup_task())

@app.get("/")
async def root():
    return {"message": "Media File Converter API is running successfully."}

@app.post("/convert")
async def convert_media(
    file: UploadFile = File(...),
    output_format: str = Form(default="mp3"),
    authorized: bool = Depends(verify_api_key)
):
    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    base_name = os.path.splitext(file.filename)[0]
    output_path = os.path.join(OUTPUT_DIR, f"{base_name}_{file_id}.{output_format}")

    try:
        with open(input_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"Received file '{file.filename}' saved as '{input_path}'")

        subprocess.run(
            ["ffmpeg", "-i", input_path, output_path, "-y"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        logger.info(f"Converted '{file.filename}' to '{output_format}' successfully")

        return FileResponse(
            output_path,
            filename=os.path.basename(output_path),
            media_type="application/octet-stream"
        )

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg conversion failed for '{file.filename}': {e}")
        return JSONResponse({"error": "Conversion failed"}, status_code=500)

    except Exception as e:
        logger.exception(f"Unexpected error converting '{file.filename}': {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
            logger.debug(f"Deleted temp file '{input_path}'")
