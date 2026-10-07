from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager

from app.api.routes import upload, eda
from app.services.cleanup_task import cleanup_old_files

# Lifespan untuk menjalankan background task (Cleanup) saat server menyala
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Menyala: Jalankan fungsi pembersihan di latar belakang
    task = asyncio.create_task(cleanup_old_files())
    yield
    # Mati: Batalkan task saat server dimatikan
    task.cancel()

app = FastAPI(title="EDA Mobile API", lifespan=lifespan)

# Konfigurasi CORS agar Flutter bisa menembak API ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Ganti dengan spesifik domain saat production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mendaftarkan Endpoint dari folder routes
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(eda.router, prefix="/api", tags=["Exploration"])

@app.get("/")
def read_root():
    return {"message": "API siap. Endpoint Upload dan Auto-Cleanup berjalan."}