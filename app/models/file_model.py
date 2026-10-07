from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.database import Base # Mengambil Base dari koneksi DB yang kita buat di Fase 1

class FileRecord(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    local_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False)