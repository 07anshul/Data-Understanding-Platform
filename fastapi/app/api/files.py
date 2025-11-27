from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED

from app.db import get_db
from app.models import File as FileModel
from app.uploads import upload_dir_exists, generate_stored_name

router = APIRouter(prefix="/files", tags=["files"])

MAX_UPLOAD_SIZE_MB = 1024
CHUNK_SIZE = 1024 * 1024

@router.post("/upload", status_code=HTTP_201_CREATED)
async def upload_file(
        uploaded_file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        # user User = Depends(get_current_user)
):
    upload_dir_exists()

    stored_name, full_path = generate_stored_name(uploaded_file.filename)
    bytes_written = 0

    try:
        with open(full_path, "wb") as f:
            while True:
                chunk = await uploaded_file.read(CHUNK_SIZE)
                if not chunk:
                    break
                bytes_written += len(chunk)
                if bytes_written > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                    f.close()
                    full_path.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail="File size exceeds the max storage limit.")
                f.write(chunk)
    finally:
        await uploaded_file.close()

    file_row = FileModel(
        user_id = None,
        original_name = uploaded_file.filename,
        stored_name = stored_name,
        path = str(full_path),
        size_bytes = bytes_written,
        mime_type = uploaded_file.content_type,
        status = "uploaded",
    )
    db.add(file_row)
    await db.commit()
    await db.refresh(file_row)

    return {
        "file_id": file_row.id,
        "original_name": file_row.original_name,
        "size_bytes": file_row.size_bytes,
        "status": file_row.status
    }
