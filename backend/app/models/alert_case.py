"""
SQLAlchemy models for Security Alerts, Cases, Investigations, and Escalations.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    alert_id = Column(String(64), primary_key=True, index=True)
    cse_id = Column(String(32), ForeignKey("cse.cse_id"), nullable=False, index=True)
    asset_id = Column(String(64), ForeignKey("assets.asset_id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    severity = Column(String(16), nullable=False, index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    alert_category = Column(String(64), index=True)  # Privilege Escalation, Malware, Data Exfiltration, etc.
    source_ip = Column(String(45))
    destination_ip = Column(String(45))
    asset_criticality = Column(String(16))
    status = Column(String(32), default="CLOSED", index=True)  # CLOSED, OPEN, IN_PROGRESS
    disposition = Column(String(64))  # True Positive, False Positive, Benign Positive
    created_at = Column(DateTime, nullable=False)
    acknowledged_at = Column(DateTime)
    closed_at = Column(DateTime)
    analyst_id = Column(String(32))
    case_id = Column(String(64), nullable=True, index=True)
    
    cse = relationship("CSE", back_populates="alerts")
    asset = relationship("Asset", back_populates="alerts")

class Case(Base):
    __tablename__ = "cases"
    
    case_id = Column(String(64), primary_key=True, index=True)
    cse_id = Column(String(32), ForeignKey("cse.cse_id"), nullable=False, index=True)
    alert_id = Column(String(64), ForeignKey("alerts.alert_id"), nullable=True, index=True)
    priority = Column(String(16))
    severity = Column(String(16), nullable=False, index=True)
    assigned_analyst = Column(String(32))
    created_at = Column(DateTime, nullable=False)
    investigation_started_at = Column(DateTime)
    closed_at = Column(DateTime)
    status = Column(String(32), default="CLOSED")
    closure_reason = Column(String(128))
    resolution = Column(String(256))
    reopen_count = Column(Integer, default=0)
    
    cse = relationship("CSE", back_populates="cases")
    investigations = relationship("Investigation", back_populates="case", cascade="all, delete-orphan")
    escalation = relationship("Escalation", back_populates="case", uselist=False, cascade="all, delete-orphan")

class Investigation(Base):
    __tablename__ = "investigations"
    
    investigation_id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("cases.case_id"), nullable=False, index=True)
    analyst_id = Column(String(32))
    timestamp = Column(DateTime, nullable=False)
    action = Column(String(64))  # Log Review, Endpoint Isolation, Packet Capture, Hash Verification
    description = Column(Text)
    evidence_count = Column(Integer, default=0)
    root_cause = Column(String(256))
    resolution = Column(String(256))
    
    case = relationship("Case", back_populates="investigations")

class Escalation(Base):
    __tablename__ = "escalations"
    
    escalation_id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("cases.case_id"), nullable=False, index=True)
    severity = Column(String(16))
    escalated = Column(Boolean, default=False)
    escalation_time = Column(DateTime)
    escalated_by = Column(String(32))
    escalated_to = Column(String(64))  # Tier-2 SOC, CISO Team, CERT-In, Incident Response
    escalation_reason = Column(String(256))
    
    case = relationship("Case", back_populates="escalation")
