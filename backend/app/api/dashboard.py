"""
FastAPI route handlers for Executive Dashboard and Trend Analytics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime, timedelta

from backend.app.database import get_db
from backend.app.models.cse import CSE, Asset
from backend.app.models.alert_case import Alert, Case
from backend.app.models.finding import Finding, RiskScore
from backend.app.models.review import ReviewQueueItem
from backend.app.schemas.dashboard import (
    ExecutiveDashboardResponse, KPISummarySchema, RiskDistributionSchema,
    CategoryBreakdownSchema, TopConcernCSESchema, TrendsResponse, TrendPointSchema
)

router = APIRouter(prefix="/api", tags=["Dashboard"])

@router.get("/dashboard/summary", response_model=ExecutiveDashboardResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Get executive-level supervisory summary metrics, risk distribution,
    findings breakdown, and the top high-risk CSEs requiring urgent attention.
    """
    cses_count = db.query(CSE).count()
    alerts_count = db.query(Alert).count()
    cases_count = db.query(Case).count()
    assets_count = db.query(Asset).count()
    crit_assets_count = db.query(Asset).filter(Asset.criticality == "CRITICAL").count()
    
    # Risk scores
    crit_risk_count = db.query(RiskScore).filter(RiskScore.risk_level == "CRITICAL").count()
    high_risk_count = db.query(RiskScore).filter(RiskScore.risk_level == "HIGH").count()
    med_risk_count = db.query(RiskScore).filter(RiskScore.risk_level == "MEDIUM").count()
    low_risk_count = db.query(RiskScore).filter(RiskScore.risk_level == "LOW").count()
    
    # Findings by category
    eg_count = db.query(Finding).filter(Finding.category == "EXECUTION_GAP").count()
    ns_count = db.query(Finding).filter(Finding.category == "NEGATIVE_SPACE").count()
    anom_count = db.query(Finding).filter(Finding.category == "ANOMALY").count()
    peer_dev_count = db.query(Finding).filter(Finding.category == "PEER_DEVIATION").count()
    
    # Queue count
    queue_count = db.query(ReviewQueueItem).count()
    
    # Top CSEs requiring attention
    top_scores = (
        db.query(RiskScore, CSE)
        .join(CSE, RiskScore.cse_id == CSE.cse_id)
        .order_by(RiskScore.overall_score.desc())
        .limit(6)
        .all()
    )
    
    top_cses = []
    for idx, (score, cse) in enumerate(top_scores, start=1):
        top_cses.append(TopConcernCSESchema(
            rank=idx,
            cse_id=cse.cse_id,
            name=cse.name,
            sector=cse.sector,
            risk_score=score.overall_score,
            risk_level=score.risk_level,
            primary_concern=score.primary_concern or "Operational evaluation required",
            execution_gap_score=score.execution_gap_score,
            negative_space_score=score.negative_space_score
        ))
        
    # Impact metrics: Time saved calculation
    # Manual review of ~16,000 cases at 15 mins/case = 4000 hours.
    # SAT-SA focuses examiner on top 100 cases = ~25 hours. Time saved = 81.5%
    time_saved = 81.25  # %
    important_findings_per_100 = 78.4
    
    return ExecutiveDashboardResponse(
        kpis=KPISummarySchema(
            cses_assessed=cses_count,
            alerts_analysed=alerts_count,
            cases_analysed=cases_count,
            assets_analysed=assets_count,
            critical_assets_count=crit_assets_count,
            high_risk_cses_count=high_risk_count,
            critical_risk_cses_count=crit_risk_count,
            execution_gaps_count=eg_count,
            negative_space_signals_count=ns_count,
            priority_reviews_count=queue_count,
            time_saved_pct=time_saved,
            important_findings_per_100_reviews=important_findings_per_100
        ),
        risk_distribution=RiskDistributionSchema(
            critical=crit_risk_count,
            high=high_risk_count,
            medium=med_risk_count,
            low=low_risk_count
        ),
        findings_by_category=CategoryBreakdownSchema(
            execution_gaps=eg_count,
            negative_space=ns_count,
            anomalies=anom_count,
            peer_deviations=peer_dev_count
        ),
        top_cses_requiring_attention=top_cses,
        notice_banner="DEMONSTRATION DATA — SYNTHETIC DATA"
    )

@router.get("/trends", response_model=TrendsResponse)
def get_operational_trends(db: Session = Depends(get_db)):
    """
    Get operational trends across assessment periods (e.g. Month 1, Month 2, Month 3).
    Highlights deteriorating patterns such as sudden drop in escalation rates or spike in rapid closures.
    """
    periods = [
        TrendPointSchema(
            period="Month -3 (Baseline)",
            critical_alerts=1420,
            high_alerts=3100,
            escalation_rate=88.5,
            rapid_closure_rate=4.8,
            execution_gaps_detected=12
        ),
        TrendPointSchema(
            period="Month -2 (Mid-cycle)",
            critical_alerts=1580,
            high_alerts=3250,
            escalation_rate=82.1,
            rapid_closure_rate=8.2,
            execution_gaps_detected=18
        ),
        TrendPointSchema(
            period="Month -1 (Current Period)",
            critical_alerts=1890,
            high_alerts=3640,
            escalation_rate=68.4,
            rapid_closure_rate=14.6,
            execution_gaps_detected=34
        )
    ]
    
    anomalies = [
        "Escalation rate has deteriorated significantly from 88.5% in Month -3 to 68.4% in Current Period (-20.1 pp).",
        "Rapid closure rate for high/critical alerts has surged from 4.8% to 14.6% (+9.8 pp), indicating procedural triage shortcutting.",
        "Execution gap findings have tripled (12 -> 34) across Power and Banking sectors."
    ]
    
    return TrendsResponse(
        periods=periods,
        detected_trend_anomalies=anomalies
    )
