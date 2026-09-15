"""
FastAPI route handlers for Supervisory Findings and Human-in-the-Loop Reviews.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.app.database import get_db
from backend.app.models.finding import Finding
from backend.app.services.blockchain_audit import create_audit_block
from backend.app.schemas.finding import FindingSchema, FindingReviewRequest

router = APIRouter(prefix="/api/findings", tags=["Findings"])

@router.get("", response_model=List[FindingSchema])
def list_findings(
    category: Optional[str] = Query(None, description="EXECUTION_GAP, NEGATIVE_SPACE, ANOMALY, PEER_DEVIATION"),
    severity: Optional[str] = Query(None, description="CRITICAL, HIGH, MEDIUM, LOW"),
    status: Optional[str] = Query(None, description="NEW, ACCEPTED, REJECTED, FALSE_POSITIVE"),
    cse_id: Optional[str] = Query(None, description="Filter by CSE ID"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    List supervisory findings with evidence summaries across all evaluated entities.
    """
    query = db.query(Finding)
    if category:
        query = query.filter(Finding.category == category)
    if severity:
        query = query.filter(Finding.severity == severity)
    if status:
        query = query.filter(Finding.status == status)
    if cse_id:
        query = query.filter(Finding.cse_id == cse_id)
        
    return query.order_by(Finding.created_at.desc()).limit(limit).all()

@router.get("/{finding_id}", response_model=FindingSchema)
def get_finding(finding_id: str, db: Session = Depends(get_db)):
    """
    Retrieve full evidence and source record IDs for a single finding.
    """
    finding = db.query(Finding).filter(Finding.finding_id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail=f"Finding {finding_id} not found.")
    return finding

@router.post("/{finding_id}/review", response_model=FindingSchema)
def review_finding(
    finding_id: str,
    req: FindingReviewRequest,
    db: Session = Depends(get_db)
):
    """
    Human-in-the-Loop decision endpoint:
    Supervisor can ACCEPT, REJECT, or mark FALSE_POSITIVE with justification notes.
    Action is permanently recorded in the immutable supervisory audit log.
    """
    finding = db.query(Finding).filter(Finding.finding_id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail=f"Finding {finding_id} not found.")
        
    action_map = {
        "ACCEPT": "ACCEPTED",
        "REJECT": "REJECTED",
        "FALSE_POSITIVE": "FALSE_POSITIVE",
        "SEND_FOR_MANUAL_REVIEW": "UNDER_MANUAL_REVIEW"
    }
    
    new_status = action_map.get(req.action.upper(), "REVIEWED")
    old_status = finding.status
    
    finding.status = new_status
    finding.supervisor_notes = req.notes
    finding.reviewed_by = req.reviewer
    finding.reviewed_at = datetime.utcnow()
    
    # Record in Audit Trail (Cryptographically Chained Audit Block)
    create_audit_block(
        db=db,
        user=req.reviewer,
        action=f"SUPERVISOR_{new_status}",
        entity_type="FINDING",
        entity_id=finding_id,
        details=f"Status changed from {old_status} to {new_status}. Notes: {req.notes or 'None'}"
    )
    db.commit()
    db.refresh(finding)
    
    return finding
