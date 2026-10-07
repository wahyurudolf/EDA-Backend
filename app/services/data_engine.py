import polars as pl
import os
from typing import Dict, Any

def calculate_data_quality_score(total_rows: int, total_missing: int, total_duplicates: int) -> float:
    """
    Menghitung skor kualitas data 0-100.
    Berdasarkan penalti untuk baris duplikat dan persentase nilai kosong.
    """
    if total_rows == 0:
        return 0.0
    
    # Penalti nilai kosong (1 baris kosong = penalti 1 point, dinormalisasi)
    missing_penalty = (total_missing / total_rows) * 50 
    
    # Penalti duplikat
    duplicate_penalty = (total_duplicates / total_rows) * 50

    score = 100 - (missing_penalty + duplicate_penalty)
    return max(0.0, round(score, 2))

def perform_eda_polars(file_path: str, file_id: int) -> Dict[str, Any]:
    """
    Membaca file menggunakan Polars dan mengekstrak metrik utama EDA.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan di path: {file_path}")

    # Membaca file berdasarkan ekstensi
    if file_path.endswith('.csv'):
        df = pl.read_csv(file_path, ignore_errors=True)
    elif file_path.endswith(('.xls', '.xlsx')):
        df = pl.read_excel(file_path)
    elif file_path.endswith('.parquet'):
        df = pl.read_parquet(file_path)
    else:
        raise ValueError("Format file tidak didukung.")

    total_rows = df.height
    total_columns = df.width

    # 1. Menghitung Duplikat
    duplicate_rows = df.is_duplicated().sum()

    # 2. Menghitung Missing Values (per kolom dan total)
    null_counts = df.null_count()
    missing_dict = null_counts.to_dicts()[0]
    total_missing = sum(missing_dict.values())

    # 3. Kalkulasi Skor Kualitas Data
    quality_score = calculate_data_quality_score(total_rows, total_missing, duplicate_rows)

    # 4. Informasi Kolom dan Statistik Dasar
    columns_info = []
    
    # Polars .describe() untuk komputasi kilat metrik dasar
    describe_df = df.describe()
    
    for col_name in df.columns:
        col_type = str(df[col_name].dtype)
        
        # Ekstrak metrik spesifik untuk kolom dari dataframe describe
        col_stats = describe_df.filter(pl.col("statistic").is_in(["mean", "min", "max", "std"]))
        
        # Ambil nilai unik (kardinalitas)
        unique_count = df[col_name].n_unique()

        info = {
            "column_name": col_name,
            "data_type": col_type,
            "unique_values": unique_count,
            "missing_count": missing_dict.get(col_name, 0)
        }

        # Jika kolom numerik, tambahkan statistik (mean, min, max, dll)
        if df[col_name].dtype in [pl.Int64, pl.Float64, pl.Int32, pl.Float32]:
            try:
                # Mengambil nilai dari describe_df dengan aman
                info["mean"] = float(col_stats.filter(pl.col("statistic") == "mean")[col_name][0])
                info["min"] = float(col_stats.filter(pl.col("statistic") == "min")[col_name][0])
                info["max"] = float(col_stats.filter(pl.col("statistic") == "max")[col_name][0])
                
                # Deteksi Outliers sederhana (menggunakan IQR)
                q1 = df[col_name].quantile(0.25)
                q3 = df[col_name].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers_count = df.filter((pl.col(col_name) < lower_bound) | (pl.col(col_name) > upper_bound)).height
                info["outliers_count"] = outliers_count

            except Exception:
                pass # Abaikan jika kolom memiliki format yang membuat describe gagal

        columns_info.append(info)

    # Mengembalikan struktur JSON siap pakai
    return {
        "file_id": file_id,
        "overview": {
            "total_rows": total_rows,
            "total_columns": total_columns,
            "estimated_memory_kb": round(df.estimated_size() / 1024, 2)
        },
        "columns_info": columns_info,
        "data_quality_score": quality_score,
        "missing_values": missing_dict,
        "duplicate_rows": duplicate_rows
    }