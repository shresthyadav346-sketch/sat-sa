"""
FastAPI route handlers for Supervisory Report Generation.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models.cse import CSE, Asset
from backend.app.models.alert_case import Alert, Case
from backend.app.models.finding import Finding, RiskScore
from backend.app.models.review import ReviewQueueItem
from backend.app.services.blockchain_audit import create_audit_block

router = APIRouter(prefix="/api/reports", tags=["Reports"])

class ReportGenerateRequest(BaseModel):
    title: str = "NCIIPC National Cyber Resilience Supervisory Assessment Report"
    assessment_cycle: str = "Q3-2026 Cycle"
    examiner_name: str = "Supervisory Examiner Team Lead"
    scope_sectors: List[str] = ["Power", "Banking", "Telecom", "Transport", "Defence"]

@router.post("/generate")
def generate_supervisory_report(
    req: ReportGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive supervisory report for NCIIPC examiners.
    Includes executive summary, high-risk entity rankings, execution gap findings,
    negative space signals, priority review queue, and formal supervisory recommendations.
    """
    # 1. High Risk CSEs
    top_cses = (
        db.query(RiskScore, CSE)
        .join(CSE, RiskScore.cse_id == CSE.cse_id)
        .order_by(RiskScore.overall_score.desc())
        .limit(10)
        .all()
    )
    
    cse_rankings = []
    for rank, (score, cse) in enumerate(top_cses, start=1):
        findings = db.query(Finding).filter(Finding.cse_id == cse.cse_id).all()
        cse_rankings.append({
            "rank": rank,
            "cse_id": cse.cse_id,
            "name": cse.name,
            "sector": cse.sector,
            "risk_score": score.overall_score,
            "risk_level": score.risk_level,
            "primary_concern": score.primary_concern,
            "execution_gap_score": score.execution_gap_score,
            "negative_space_score": score.negative_space_score,
            "findings_count": len(findings)
        })
        
    # 2. Critical Findings
    crit_findings = (
        db.query(Finding)
        .filter(Finding.severity.in_(["CRITICAL", "HIGH"]))
        .order_by(Finding.severity.desc(), Finding.created_at.desc())
        .limit(15)
        .all()
    )
    
    findings_list = []
    for f in crit_findings:
        cse = db.query(CSE).filter(CSE.cse_id == f.cse_id).first()
        findings_list.append({
            "finding_id": f.finding_id,
            "cse_id": f.cse_id,
            "cse_name": cse.name if cse else f.cse_id,
            "rule_code": f.rule_code,
            "category": f.category,
            "title": f.title,
            "severity": f.severity,
            "confidence": f.confidence,
            "evidence_summary": f.evidence_summary,
            "status": f.status
        })
        
    # 3. Priority Review Queue top cases
    top_cases = (
        db.query(ReviewQueueItem)
        .order_by(ReviewQueueItem.priority_score.desc())
        .limit(15)
        .all()
    )
    cases_list = []
    for q in top_cases:
        cases_list.append({
            "case_id": q.case_id,
            "alert_id": q.alert_id,
            "cse_id": q.cse_id,
            "priority_score": q.priority_score,
            "reason": q.primary_reason,
            "workflow_status": q.workflow_integrity_status,
            "reviewed": q.reviewed
        })
        
    # Formal recommendations
    recommendations = [
        "Issue formal supervisory inquiry to CSE-007 and CSE-041 regarding rapid alert closure procedures and failure to adhere to mandatory critical-threat escalation protocols.",
        "Mandate an immediate operational audit of telemetry infrastructure at CSE-014 to resolve critical asset monitoring blindspots across core banking switches.",
        "Require CSE-021 to review SOC analyst investigation workflows and discontinue boilerplate checklist triage templates.",
        "Conduct on-site manual forensic examination of the top 100 cases identified in the SAT-SA Priority Review Queue."
    ]
    
    report_data = {
        "report_id": f"REP-NCIIPC-{datetime.utcnow().strftime('%Y%m%d-%H%M')}",
        "generated_at": datetime.utcnow().isoformat(),
        "title": req.title,
        "assessment_cycle": req.assessment_cycle,
        "examiner_name": req.examiner_name,
        "notice": "DEMONSTRATION DATA — SYNTHETIC DATA",
        "scope_summary": {
            "sectors_covered": req.scope_sectors,
            "total_entities_evaluated": db.query(CSE).count(),
            "total_alerts_analyzed": db.query(Alert).count(),
            "total_cases_examined": db.query(Case).count(),
            "critical_assets_analyzed": db.query(Asset).filter(Asset.criticality == "CRITICAL").count()
        },
        "cse_risk_rankings": cse_rankings,
        "major_findings": findings_list,
        "priority_review_sample": cases_list,
        "supervisory_recommendations": recommendations
    }
    
    # Cryptographically Chained Audit Block
    create_audit_block(
        db=db,
        user=req.examiner_name,
        action="GENERATE_SUPERVISORY_REPORT",
        entity_type="REPORT",
        entity_id=report_data["report_id"],
        details=f"Generated formal report for {req.assessment_cycle} with {len(cse_rankings)} ranked entities."
    )
    
    return report_data
