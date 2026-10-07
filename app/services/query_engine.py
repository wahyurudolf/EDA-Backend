import duckdb
import os
from typing import Dict, Any, List

def get_paginated_data(file_path: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Membaca data file menggunakan DuckDB secara langsung (tanpa memuat seluruhnya ke RAM)
    untuk keperluan paginasi tabel di Flutter.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError("File tidak ditemukan di sistem lokal.")

    # DuckDB bisa mendeteksi format file secara otomatis, tapi kita bisa tegaskan
    if file_path.endswith('.csv'):
        table_name = f"read_csv_auto('{file_path}')"
    elif file_path.endswith('.parquet'):
        table_name = f"read_parquet('{file_path}')"
    else:
        # Fallback (contoh untuk excel, duckdb butuh plugin khusus, jadi kita fokus CSV/Parquet)
        raise ValueError("Format file ini belum didukung untuk kueri langsung DuckDB.")

    # Eksekusi kueri LIMIT dan OFFSET
    query = f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"
    
    # Menjalankan kueri dan mengubah hasil menjadi list of dictionaries (JSON)
    result_df = duckdb.query(query).df()
    
    # Convert hasil DataFrame ke JSON (list of dict)
    return result_df.to_dict(orient="records")