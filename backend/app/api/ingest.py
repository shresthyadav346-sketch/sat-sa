"""
FastAPI route handlers for Ingestion, Re-analysis, and Dataset Management.
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.app.database import get_db

router = APIRouter(prefix="/api/datasets", tags=["Dataset & Ingestion"])

class ReanalyzeRequest(BaseModel):
    user: str = "supervisory_examiner_1"
    note: Optional[str] = "Manual supervisory re-analysis trigger"

@router.post("/reanalyze")
def trigger_reanalysis(req: ReanalyzeRequest, db: Session = Depends(get_db)):
    """
    Trigger full operational metrics, peer baselining, ML anomaly detection,
    and rule evaluations across all entities in the database.
    """
    from backend.app.services.analysis_runner import run_full_supervisory_analysis
    res = run_full_supervisory_analysis(db)
    return {
        "status": "SUCCESS",
        "message": "Full supervisory analysis pipeline executed successfully.",
        "results": res
    }

@router.post("/regenerate")
def regenerate_data(num_cses: int = 45, db: Session = Depends(get_db)):
    """
    Re-generate synthetic dataset with ground-truth validation anomalies.
    """
    from data_generator.generator import generate_synthetic_soc_dataset
    from backend.app.services.analysis_runner import run_full_supervisory_analysis
    counts = generate_synthetic_soc_dataset(num_cses=num_cses, db_session=db)
    analysis_res = run_full_supervisory_analysis(db)
    return {
        "status": "SUCCESS",
        "message": "Dataset generated and analyzed.",
        "generated_counts": counts,
        "analysis_results": analysis_res
    }
