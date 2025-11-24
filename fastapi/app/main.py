import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from .config import settings

app = FastAPI(title="Platform")

os.makedirs(settings.upload_folder, exist_ok=True)
os.makedirs(settings.output_folder, exist_ok=True)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/upload")
async def upload(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    dest_path = os.path.join(settings.upload_folder, f"{file_id}_{file.filename}")
    try:
        with open(dest_path, "wb") as f:
            while True:
                chunk = await file.read(1024*1024)
                if not chunk:
                    break
                f.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, details=f"Failed saving file: {e}")
        # db entry for file job

    return JSONResponse({"file_id": file_id, "path": dest_path})
