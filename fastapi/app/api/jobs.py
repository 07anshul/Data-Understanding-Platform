from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models import Job as JobModel

router = APIRouter(prefix="/job", tags=["jobs"])

@router.get("/{job_id}")
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(JobModel).where(JobModel.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.id,
        "file_id": job.file_id,
        "status": job.status,
        "progress": job.progress,
        "model_version": job.model_version,
        "result_path": job.result_path,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "finished_at": job.finished_at
    }