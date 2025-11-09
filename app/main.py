from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import os
import uuid
from utils.logger_config import setup_logger

app = FastAPI(title="Media File Converter")

logger = setup_logger()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "converted")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Media File Converter API is running successfully."}

@app.post("/convert")
async def convert_media(
    file: UploadFile = File(...),
    output_format: str = Form(default="mp3")
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
