from pydantic import BaseModel
from typing import Dict, Any, List

class EDAMetricsResponse(BaseModel):
    file_id: int
    overview: Dict[str, Any]
    columns_info: List[Dict[str, Any]]
    data_quality_score: float
    missing_values: Dict[str, int]
    duplicate_rows: int