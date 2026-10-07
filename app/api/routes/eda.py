from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.file_model import FileRecord
from app.services.data_engine import perform_eda_polars
from app.schemas.eda_schema import EDAMetricsResponse
from app.services.query_engine import get_paginated_data
from typing import List, Dict, Any

router = APIRouter()

@router.get("/eda/{file_id}", response_model=EDAMetricsResponse)
def analyze_data(file_id: int, db: Session = Depends(get_db)):
    """
    Endpoint untuk mengeksekusi kalkulasi EDA menggunakan Polars 
    berdasarkan ID file yang ada di database.
    """
    # 1. Cari file di database (PostgreSQL)
    file_record = db.query(FileRecord).filter(
        FileRecord.id == file_id, 
        FileRecord.is_deleted == False
    ).first()

    if not file_record:
        raise HTTPException(status_code=404, detail="File tidak ditemukan atau telah kedaluwarsa.")

    # 2. Jalankan Polars Data Engine
    try:
        eda_results = perform_eda_polars(file_record.local_path, file_record.id)
        
        # Opsional: Di sini Anda bisa menyimpan ringkasan metrik (seperti Quality Score) 
        # ke tabel `eda_metrics` jika ingin menyimpannya ke database untuk riwayat.
        
        return eda_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses data: {str(e)}")

@router.get("/data/{file_id}", response_model=List[Dict[str, Any]])
def preview_data(file_id: int, page: int = 1, limit: int = 50, db: Session = Depends(get_db)):
    """
    Endpoint untuk Data Preview.
    Contoh penggunaan di Flutter: /api/data/123?page=2&limit=50
    """
    file_record = db.query(FileRecord).filter(FileRecord.id == file_id, FileRecord.is_deleted == False).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File tidak ditemukan.")

    offset = (page - 1) * limit
    try:
        data = get_paginated_data(file_record.local_path, limit, offset)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat tabel: {str(e)}")