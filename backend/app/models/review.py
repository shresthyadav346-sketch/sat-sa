"""
SQLAlchemy models for Review Queue and Supervisory Audit Logging.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from datetime import datetime
from backend.app.database import Base

class ReviewQueueItem(Base):
    __tablename__ = "review_queue"
    
    queue_id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(64), ForeignKey("cases.case_id"), index=True)
    alert_id = Column(String(64), ForeignKey("alerts.alert_id"), index=True)
    cse_id = Column(String(32), ForeignKey("cse.cse_id"), nullable=False, index=True)
    priority_score = Column(Float, nullable=False, index=True)  # 0-100
    primary_reason = Column(String(256), nullable=False)
    severity = Column(String(16), index=True)
    asset_criticality = Column(String(16))
    workflow_integrity_status = Column(String(64))  # e.g., "Missing Escalation", "Rapid Closure", "Missing Investigation"
    evidence_count = Column(Integer, default=0)
    reviewed = Column(Boolean, default=False)
    supervisor_verdict = Column(String(32))  # CONFIRMED_GAP, BENIGN_OPERATIONAL, FALSE_POSITIVE
    reviewed_at = Column(DateTime)
    reviewed_by = Column(String(64))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user = Column(String(64), nullable=False, default="supervisory_examiner_1")
    action = Column(String(64), nullable=False)  # ACCEPT_FINDING, REJECT_FINDING, GENERATE_REPORT, REVIEW_CASE
    entity_type = Column(String(32), nullable=False)  # FINDING, CASE, CSE, DATASET
    entity_id = Column(String(64), nullable=False)
    details = Column(Text)
    dataset_version = Column(String(32), default="v1.0-synthetic")
    rule_version = Column(String(32), default="v1.0.0")

    # Hash-chained tamper-evident blockchain fields
    block_index = Column(Integer, nullable=False, default=0, index=True)
    previous_hash = Column(String(64), nullable=False, default="0" * 64)
    block_hash = Column(String(64), nullable=False, index=True)
    nonce = Column(Integer, default=0)

