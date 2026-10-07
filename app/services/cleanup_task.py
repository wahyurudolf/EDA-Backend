import asyncio
import os
from datetime import datetime, timedelta, timezone
from app.db.database import SessionLocal
from app.models.file_model import FileRecord

async def cleanup_old_files():
    """
    Background task yang berjalan terus menerus.
    Mengecek dan menghapus file fisik yang usianya lebih dari 24 jam setiap 1 jam sekali.
    """
    while True:
        db = SessionLocal()
        try:
            # Cari waktu 24 jam yang lalu
            threshold_time = datetime.now(timezone.utc) - timedelta(hours=24)
            
            # Kueri ke PostgreSQL: cari file yang belum dihapus dan umurnya > 24 jam
            old_files = db.query(FileRecord).filter(
                FileRecord.uploaded_at < threshold_time,
                FileRecord.is_deleted == False
            ).all()

            for record in old_files:
                # Hapus file fisik di local disk
                if os.path.exists(record.local_path):
                    os.remove(record.local_path)
                
                # Update status di database agar Flutter tahu file ini sudah kedaluwarsa
                record.is_deleted = True
            
            db.commit()
            print(f"[{datetime.now()}] Cleanup Task: Berhasil membersihkan {len(old_files)} file lama.")
            
        except Exception as e:
            print(f"Error pada cleanup task: {e}")
        finally:
            db.close()
            
        # Jeda selama 1 jam sebelum mengecek ulang (3600 detik)
        await asyncio.sleep(3600)