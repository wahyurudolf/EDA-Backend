from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.file_model import FileRecord
from app.services.data_engine import perform_eda_polars
from app.schemas.eda_schema import EDAMetricsResponse

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