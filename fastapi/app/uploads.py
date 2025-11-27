import os
import uuid
from pathlib import Path
from typing import Tuple

from .config import settings

UPLOAD_DIR = Path(settings.upload_folder)

def upload_dir_exists() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def generate_stored_name(original_name: str) -> Tuple[str, Path]:
    extension = Path(original_name).suffix
    stored_name = f"{uuid.uuid4().hex}{extension}"
    full_path = UPLOAD_DIR / stored_name
    return stored_name, full_path

