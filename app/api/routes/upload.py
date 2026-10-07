from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import uuid
import shutil
from app.db.database import get_db
from app.models.file_model import FileRecord
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE_MB = os.getenv("MAX_FILE_SIZE_MB")
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Pastikan folder uploads tersedia
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(
    user_id: str = Form(...), 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # 1. Validasi Ekstensi File
    if not file.filename.endswith(('.csv', '.xlsx', '.parquet')):
        raise HTTPException(status_code=400, detail="Hanya format CSV, Excel, atau Parquet yang diizinkan.")

    # 2. Validasi Ukuran File (Maksimal 20MB)
    file.file.seek(0, 2) # Pindah kursor ke akhir file
    file_size = file.file.tell() # Cek ukuran
    file.file.seek(0) # Kembalikan kursor ke awal
    
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"Ukuran file melebihi batas {MAX_FILE_SIZE_MB}MB.")

    # 3. Simpan File ke Local Disk
    # Gunakan UUID agar nama file unik (mencegah bentrok jika ada nama file yang sama)
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    local_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(local_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 4. Simpan Metadata ke PostgreSQL
    new_file_record = FileRecord(
        user_id=user_id,
        original_name=file.filename,
        file_size_bytes=file_size,
        local_path=local_path
    )
    db.add(new_file_record)
    db.commit()
    db.refresh(new_file_record)

    return {
        "message": "File berhasil diunggah dan disimpan.",
        "file_id": new_file_record.id,
        "original_name": file.filename
    }