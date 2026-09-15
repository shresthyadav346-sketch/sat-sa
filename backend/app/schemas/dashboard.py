"""
Pydantic schemas for Executive Dashboard and Trend Analytics.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class KPISummarySchema(BaseModel):
    cses_assessed: int
    alerts_analysed: int
    cases_analysed: int
    assets_analysed: int
    critical_assets_count: int
    high_risk_cses_count: int
    critical_risk_cses_count: int
    execution_gaps_count: int
    negative_space_signals_count: int
    priority_reviews_count: int
    time_saved_pct: float
    important_findings_per_100_reviews: float

class RiskDistributionSchema(BaseModel):
    critical: int
    high: int
    medium: int
    low: int

class CategoryBreakdownSchema(BaseModel):
    execution_gaps: int
    negative_space: int
    anomalies: int
    peer_deviations: int

class TopConcernCSESchema(BaseModel):
    rank: int
    cse_id: str
    name: str
    sector: str
    risk_score: float
    risk_level: str
    primary_concern: str
    execution_gap_score: float
    negative_space_score: float

class ExecutiveDashboardResponse(BaseModel):
    kpis: KPISummarySchema
    risk_distribution: RiskDistributionSchema
    findings_by_category: CategoryBreakdownSchema
    top_cses_requiring_attention: List[TopConcernCSESchema]
    notice_banner: str = "DEMONSTRATION DATA — SYNTHETIC DATA"

class TrendPointSchema(BaseModel):
    period: str  # Month or week
    critical_alerts: int
    high_alerts: int
    escalation_rate: float
    rapid_closure_rate: float
    execution_gaps_detected: int

class TrendsResponse(BaseModel):
    periods: List[TrendPointSchema]
    detected_trend_anomalies: List[str]
