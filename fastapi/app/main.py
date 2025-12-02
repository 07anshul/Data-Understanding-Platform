import os
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.files import router as files_router
from app.api.jobs import router as jobs_router

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     os.makedirs(settings.upload_folder, exist_ok=True)
#     os.makedirs(settings.output_folder, exist_ok=True)
#
#     yield
#
# app = FastAPI(title="Platform", lifespan=lifespan)
app = FastAPI(title="Platform")

app.include_router(files_router)
app.include_router(jobs_router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/verify/settings")
def verify_settings():
    return {
        "database_user": settings.database_user,
        "database_host": settings.database_host,
        "database_port": settings.database_port,
        "sql_url": settings.sql_url,
    }