"""
Pydantic schemas for Review Queue items, Case workflow details, and Audit logs.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ReviewQueueItemSchema(BaseModel):
    queue_id: int
    case_id: Optional[str] = None
    alert_id: Optional[str] = None
    cse_id: str
    priority_score: float
    primary_reason: str
    severity: Optional[str] = None
    asset_criticality: Optional[str] = None
    workflow_integrity_status: Optional[str] = None
    evidence_count: int = 0
    reviewed: bool = False
    supervisor_verdict: Optional[str] = None

    class Config:
        from_attributes = True

class InvestigationItemSchema(BaseModel):
    investigation_id: str
    action: Optional[str] = None
    description: Optional[str] = None
    timestamp: datetime
    evidence_count: int = 0
    root_cause: Optional[str] = None
    resolution: Optional[str] = None

    class Config:
        from_attributes = True

class EscalationItemSchema(BaseModel):
    escalation_id: str
    severity: Optional[str] = None
    escalated: bool = False
    escalation_time: Optional[datetime] = None
    escalated_by: Optional[str] = None
    escalated_to: Optional[str] = None
    escalation_reason: Optional[str] = None

    class Config:
        from_attributes = True

class AlertDetailSchema(BaseModel):
    alert_id: str
    cse_id: str
    asset_id: str
    timestamp: datetime
    severity: str
    alert_category: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    asset_criticality: Optional[str] = None
    status: str
    disposition: Optional[str] = None
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    analyst_id: Optional[str] = None

    class Config:
        from_attributes = True

class CaseDetailSchema(BaseModel):
    case_id: str
    cse_id: str
    alert_id: Optional[str] = None
    priority: Optional[str] = None
    severity: str
    assigned_analyst: Optional[str] = None
    created_at: datetime
    investigation_started_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    status: str
    closure_reason: Optional[str] = None
    resolution: Optional[str] = None
    reopen_count: int = 0
    alert: Optional[AlertDetailSchema] = None
    investigations: List[InvestigationItemSchema] = []
    escalation: Optional[EscalationItemSchema] = None
    workflow_stages: Dict[str, bool] = {}  # {alert: true, case: true, investigation: true/false, escalation: true/false, resolution: true, closure: true}

    class Config:
        from_attributes = True

class AuditLogSchema(BaseModel):
    log_id: int
    timestamp: datetime
    user: str
    action: str
    entity_type: str
    entity_id: str
    details: Optional[str] = None
    dataset_version: Optional[str] = None
    rule_version: Optional[str] = None
    block_index: Optional[int] = 0
    previous_hash: Optional[str] = None
    block_hash: Optional[str] = None
    nonce: Optional[int] = 0

    class Config:
        from_attributes = True

class ChainVerificationSchema(BaseModel):
    valid: bool
    total_blocks: int
    broken_at_index: Optional[int] = None
    details: str

