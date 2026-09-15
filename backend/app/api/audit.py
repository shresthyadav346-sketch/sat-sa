"""
FastAPI route handlers for Supervisory Audit Log.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models.review import AuditLog
from backend.app.schemas.review import AuditLogSchema

router = APIRouter(prefix="/api/audit-log", tags=["Audit Log"])

@router.get("", response_model=List[AuditLogSchema])
def get_audit_log(
    limit: int = Query(50, ge=1, le=200),
    entity_type: Optional[str] = Query(None, description="FINDING, CASE, CSE, SYSTEM"),
    db: Session = Depends(get_db)
):
    """
    Retrieve supervisory actions, decisions, and system events.
    Immutable log for regulatory compliance and examination auditability.
    """
    query = db.query(AuditLog)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
