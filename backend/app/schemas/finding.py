"""
Pydantic schemas for Supervisory Findings and Review Requests.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class FindingSchema(BaseModel):
    finding_id: str
    cse_id: str
    category: str
    rule_code: str
    title: str
    description: str
    severity: str
    confidence: str
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    peer_median: Optional[float] = None
    threshold_value: Optional[float] = None
    evidence_summary: str
    source_record_ids: Optional[str] = None
    status: str
    supervisor_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FindingReviewRequest(BaseModel):
    action: str  # ACCEPT, REJECT, FALSE_POSITIVE, SEND_FOR_MANUAL_REVIEW
    notes: Optional[str] = None
    reviewer: str = "supervisory_examiner_1"
