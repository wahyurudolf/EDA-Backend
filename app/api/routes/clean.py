from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.file_model import FileRecord
import polars as pl
import os

router = APIRouter()

@router.get("/clean/{file_id}")
def clean_and_export_data(file_id: int, db: Session = Depends(get_db)):
    """
    Menggunakan Polars untuk menghapus baris duplikat dan baris dengan nilai kosong (One-Click Clean).
    Mengembalikan file bersih dalam format CSV agar bisa diunduh ke ponsel.
    """
    file_record = db.query(FileRecord).filter(FileRecord.id == file_id, FileRecord.is_deleted == False).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File tidak ditemukan.")

    file_path = file_record.local_path
    
    try:
        # Load dataset
        if file_path.endswith('.csv'):
            df = pl.read_csv(file_path, ignore_errors=True)
        else:
            raise HTTPException(status_code=400, detail="Untuk demo ini, fitur clean hanya mendukung CSV.")

        # PROSES PEMBERSIHAN (One-Click Clean)
        # 1. Hapus nilai kosong (drop_nulls)
        # 2. Hapus duplikat (unique)
        clean_df = df.drop_nulls().unique()
        
        # Simpan file bersih dengan nama baru
        clean_file_path = file_path.replace(".csv", "_cleaned.csv")
        clean_df.write_csv(clean_file_path)

        # Kembalikan file agar di-download oleh Frontend
        return FileResponse(
            path=clean_file_path, 
            filename=f"Cleaned_{file_record.original_name}",
            media_type='text/csv'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membersihkan data: {str(e)}")