"""
SQLAlchemy models for Supervisory Findings and Entity Risk Scores.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class Finding(Base):
    __tablename__ = "findings"
    
    finding_id = Column(String(64), primary_key=True, index=True)
    cse_id = Column(String(32), ForeignKey("cse.cse_id"), nullable=False, index=True)
    category = Column(String(32), nullable=False, index=True)  # EXECUTION_GAP, NEGATIVE_SPACE, ANOMALY, PEER_DEVIATION
    rule_code = Column(String(16), nullable=False, index=True)  # EG-001..EG-007, NS-001..NS-006, ML-001
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(16), nullable=False, index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    confidence = Column(String(16), nullable=False, default="HIGH")  # HIGH, MEDIUM, LOW
    metric_name = Column(String(64))
    metric_value = Column(Float)
    peer_median = Column(Float)
    threshold_value = Column(Float)
    evidence_summary = Column(Text, nullable=False)
    source_record_ids = Column(Text)  # JSON-encoded array of IDs
    status = Column(String(32), default="NEW", index=True)  # NEW, ACCEPTED, REJECTED, FALSE_POSITIVE
    supervisor_notes = Column(Text)
    reviewed_by = Column(String(64))
    reviewed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    cse = relationship("CSE", back_populates="findings")

class RiskScore(Base):
    __tablename__ = "risk_scores"
    
    cse_id = Column(String(32), ForeignKey("cse.cse_id"), primary_key=True)
    overall_score = Column(Float, nullable=False, index=True)  # 0-100
    risk_level = Column(String(16), nullable=False, index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    execution_gap_score = Column(Float, nullable=False)
    negative_space_score = Column(Float, nullable=False)
    investigation_score = Column(Float, nullable=False)
    escalation_score = Column(Float, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    peer_deviation_score = Column(Float, nullable=False)
    primary_concern = Column(String(256))
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    cse = relationship("CSE", back_populates="risk_score")
