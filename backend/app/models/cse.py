"""
SQLAlchemy models for Critical Sector Entities (CSE) and Asset Inventory.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class CSE(Base):
    __tablename__ = "cse"
    
    cse_id = Column(String(32), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    sector = Column(String(64), nullable=False, index=True)  # Power, Banking, Telecom, Transport, Defence
    criticality = Column(String(16), nullable=False, default="HIGH")  # CRITICAL, HIGH, MEDIUM
    total_assets = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assets = relationship("Asset", back_populates="cse", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="cse", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="cse", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="cse", cascade="all, delete-orphan")
    risk_score = relationship("RiskScore", back_populates="cse", uselist=False, cascade="all, delete-orphan")

class Asset(Base):
    __tablename__ = "assets"
    
    asset_id = Column(String(64), primary_key=True, index=True)
    cse_id = Column(String(32), ForeignKey("cse.cse_id"), nullable=False, index=True)
    asset_type = Column(String(64), nullable=False)  # Domain Controller, SCADA RTU, Core Banking, Firewall, Database
    criticality = Column(String(16), nullable=False, index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    business_function = Column(String(128))
    environment = Column(String(32), default="Production")  # Production, Staging, DR
    monitoring_status = Column(String(32), default="ACTIVE")  # ACTIVE, INACTIVE, UNMONITORED
    
    cse = relationship("CSE", back_populates="assets")
    alerts = relationship("Alert", back_populates="asset")
