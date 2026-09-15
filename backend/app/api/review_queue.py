"""
FastAPI route handlers for Priority Review Queue and Case Workflow Deep-Dive.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.app.database import get_db
from backend.app.models.review import ReviewQueueItem
from backend.app.services.blockchain_audit import create_audit_block
from backend.app.models.alert_case import Case, Alert, Investigation, Escalation
from backend.app.schemas.review import ReviewQueueItemSchema, CaseDetailSchema

router = APIRouter(prefix="/api", tags=["Review Queue & Cases"])

class CaseTriageRequest(BaseModel):
    verdict: str  # CONFIRMED_GAP, BENIGN_OPERATIONAL, FALSE_POSITIVE
    notes: Optional[str] = None
    reviewer: str = "supervisory_examiner_1"

@router.get("/review-queue", response_model=List[ReviewQueueItemSchema])
def get_review_queue(
    cse_id: Optional[str] = Query(None, description="Filter queue by CSE ID"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    workflow_status: Optional[str] = Query(None, description="Filter by workflow break condition"),
    unreviewed_only: bool = Query(False, description="Filter only unreviewed cases"),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get the top priority cases requiring manual supervisory examination.
    Sorted by multi-criteria priority score descending.
    """
    query = db.query(ReviewQueueItem)
    if cse_id:
        query = query.filter(ReviewQueueItem.cse_id == cse_id)
    if severity:
        query = query.filter(ReviewQueueItem.severity == severity)
    if workflow_status:
        query = query.filter(ReviewQueueItem.workflow_integrity_status == workflow_status)
    if unreviewed_only:
        query = query.filter(ReviewQueueItem.reviewed == False)
        
    return query.order_by(ReviewQueueItem.priority_score.desc()).limit(limit).all()

@router.get("/cases/{case_id}", response_model=CaseDetailSchema)
def get_case_workflow_detail(case_id: str, db: Session = Depends(get_db)):
    """
    Detailed forensic examination of a case:
    Full workflow lifecycle inspection (Alert -> Case -> Investigation -> Escalation -> Resolution -> Closure).
    Highlights missing stages and displays technical investigation steps.
    """
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found.")
        
    alert = db.query(Alert).filter(Alert.alert_id == case.alert_id).first()
    investigations = db.query(Investigation).filter(Investigation.case_id == case_id).order_by(Investigation.timestamp.asc()).all()
    escalation = db.query(Escalation).filter(Escalation.case_id == case_id).first()
    
    # Analyze 6-stage lifecycle integrity
    has_alert = alert is not None
    has_case = True
    has_investigation = len(investigations) > 0
    has_escalation = escalation is not None and escalation.escalated is True
    has_resolution = bool(case.resolution and len(case.resolution) > 0)
    has_closure = case.status == "CLOSED"
    
    workflow_stages = {
        "alert": has_alert,
        "case": has_case,
        "investigation": has_investigation,
        "escalation": has_escalation,
        "resolution": has_resolution,
        "closure": has_closure
    }
    
    return CaseDetailSchema(
        case_id=case.case_id,
        cse_id=case.cse_id,
        alert_id=case.alert_id,
        priority=case.priority,
        severity=case.severity,
        assigned_analyst=case.assigned_analyst,
        created_at=case.created_at,
        investigation_started_at=case.investigation_started_at,
        closed_at=case.closed_at,
        status=case.status,
        closure_reason=case.closure_reason,
        resolution=case.resolution,
        reopen_count=case.reopen_count or 0,
        alert=alert,
        investigations=investigations,
        escalation=escalation,
        workflow_stages=workflow_stages
    )

@router.post("/cases/{case_id}/triage", response_model=ReviewQueueItemSchema)
def triage_case(
    case_id: str,
    req: CaseTriageRequest,
    db: Session = Depends(get_db)
):
    """
    Record supervisory review verdict on a priority queue case.
    """
    queue_item = db.query(ReviewQueueItem).filter(ReviewQueueItem.case_id == case_id).first()
    if not queue_item:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not in review queue.")
        
    queue_item.reviewed = True
    queue_item.supervisor_verdict = req.verdict
    queue_item.reviewed_at = datetime.utcnow()
    queue_item.reviewed_by = req.reviewer
    
    # Record in Audit Trail (Cryptographically Chained Audit Block)
    create_audit_block(
        db=db,
        user=req.reviewer,
        action=f"TRIAGE_CASE_{req.verdict}",
        entity_type="CASE",
        entity_id=case_id,
        details=f"Supervisor verdict: {req.verdict}. Notes: {req.notes or 'None'}"
    )
    db.commit()
    db.refresh(queue_item)
    return queue_item
