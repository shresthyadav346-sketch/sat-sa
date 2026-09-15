"""
Pydantic schemas for CSE and Asset API endpoints.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class AssetSchema(BaseModel):
    asset_id: str
    cse_id: str
    asset_type: str
    criticality: str
    business_function: Optional[str] = None
    environment: Optional[str] = None
    monitoring_status: str

    class Config:
        from_attributes = True

class RiskScoreSchema(BaseModel):
    overall_score: float
    risk_level: str
    execution_gap_score: float
    negative_space_score: float
    investigation_score: float
    escalation_score: float
    anomaly_score: float
    peer_deviation_score: float
    primary_concern: Optional[str] = None
    calculated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CSESummarySchema(BaseModel):
    cse_id: str
    name: str
    sector: str
    criticality: str
    total_assets: int
    risk_score: Optional[RiskScoreSchema] = None
    findings_count: int = 0

    class Config:
        from_attributes = True

class CSEDetailSchema(BaseModel):
    cse_id: str
    name: str
    sector: str
    criticality: str
    total_assets: int
    created_at: Optional[datetime] = None
    risk_score: Optional[RiskScoreSchema] = None
    metrics: Dict[str, Any] = {}
    deviations: Dict[str, Any] = {}
    cluster_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
