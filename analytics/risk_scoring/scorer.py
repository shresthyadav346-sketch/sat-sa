"""
Supervisory Risk Scoring & Priority Review Queue Scorer.
Computes explainable 0-100 risk scores and ranks top 100 cases for manual examiner review.
"""

from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models.finding import Finding, RiskScore
from backend.app.models.review import ReviewQueueItem
from backend.app.models.alert_case import Alert, Case, Investigation, Escalation
from backend.app.models.cse import Asset
from backend.app.config import settings

def calculate_supervisory_risk_score(
    cse_id: str,
    cse_metrics: Dict[str, Any],
    findings: List[Finding],
    peer_deviations: Dict[str, Dict[str, float]],
    ml_anomaly_score: float = 0.0
) -> RiskScore:
    """
    Calculate explainable 0-100 Supervisory Risk Score with transparent component breakdown.
    """
    # 1. Execution Gap Component (0-100)
    eg_findings = [f for f in findings if f.category == "EXECUTION_GAP"]
    eg_score = 0.0
    for f in eg_findings:
        if f.severity == "CRITICAL":
            eg_score += 45.0
        elif f.severity == "HIGH":
            eg_score += 25.0
        elif f.severity == "MEDIUM":
            eg_score += 15.0
    eg_score = min(100.0, eg_score)
    
    # 2. Negative Space Component (0-100)
    ns_findings = [f for f in findings if f.category == "NEGATIVE_SPACE"]
    ns_score = 0.0
    for f in ns_findings:
        if f.severity == "CRITICAL":
            ns_score += 50.0
        elif f.severity == "HIGH":
            ns_score += 25.0
        elif f.severity == "MEDIUM":
            ns_score += 15.0
    ns_score = min(100.0, ns_score)
    
    # 3. Investigation Weakness Component (0-100)
    avg_actions = cse_metrics.get("avg_investigation_actions", 2.5)
    cases_without_inv_count = cse_metrics.get("cases_without_investigation_count", 0)
    total_cases = cse_metrics.get("cases_count", 1)
    uninv_ratio = (cases_without_inv_count / total_cases) if total_cases > 0 else 0.0
    
    inv_score = 0.0
    if avg_actions < 1.2:
        inv_score += 50.0
    elif avg_actions < 1.8:
        inv_score += 25.0
    inv_score += min(50.0, uninv_ratio * 100.0)
    inv_score = min(100.0, inv_score)
    
    # 4. Escalation Weakness Component (0-100)
    crit_esc_rate = cse_metrics.get("critical_escalation_rate", 85.0)
    if crit_esc_rate < 15.0:
        esc_score = 95.0
    elif crit_esc_rate < 35.0:
        esc_score = 75.0
    elif crit_esc_rate < 60.0:
        esc_score = 45.0
    elif crit_esc_rate < 80.0:
        esc_score = 20.0
    else:
        esc_score = 5.0
        
    # 5. ML Anomaly Score (0-100)
    anomaly_score = max(0.0, min(100.0, ml_anomaly_score))
    
    # 6. Peer Deviation Score (0-100)
    peer_dev_score = 0.0
    for metric, dev_data in peer_deviations.items():
        z = abs(dev_data.get("z_score", 0.0))
        if z > 2.5:
            peer_dev_score += 25.0
        elif z > 1.5:
            peer_dev_score += 12.0
    peer_dev_score = min(100.0, peer_dev_score)
    
    # Calculate weighted overall score
    overall = (
        settings.WEIGHT_EXECUTION_GAP * eg_score +
        settings.WEIGHT_NEGATIVE_SPACE * ns_score +
        settings.WEIGHT_INVESTIGATION * inv_score +
        settings.WEIGHT_ESCALATION * esc_score +
        settings.WEIGHT_ANOMALY * anomaly_score +
        settings.WEIGHT_PEER_DEVIATION * peer_dev_score
    )
    overall = round(max(0.0, min(100.0, overall)), 1)
    
    # Determine risk category
    if overall > settings.RISK_HIGH_MAX:
        risk_level = "CRITICAL"
    elif overall > settings.RISK_MEDIUM_MAX:
        risk_level = "HIGH"
    elif overall > settings.RISK_LOW_MAX:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
        
    # Determine Primary Concern based on actual rule codes and scores
    concerns = []
    finding_codes = {f.rule_code for f in findings}
    
    if "EG-007" in finding_codes:
        concerns.append("Metric optimization / SLA divergence")
    if "EG-002" in finding_codes or esc_score > 70.0:
        concerns.append("Severe escalation failure")
    if "EG-001" in finding_codes or eg_score > 60.0:
        concerns.append("Rapid critical closure")
    if "NS-001" in finding_codes or ns_score > 50.0:
        concerns.append("Critical asset monitoring blindspot")
    if "EG-006" in finding_codes:
        concerns.append("Repetitive investigation patterns")
    if "EG-005" in finding_codes:
        concerns.append("Repeated alert flapping on assets")
    if inv_score > 60.0:
        concerns.append("Superficial investigation depth")
    if not concerns:
        concerns.append("Normal operational discipline")
        
    primary_concern = " & ".join(concerns[:2])
    
    return RiskScore(
        cse_id=cse_id,
        overall_score=overall,
        risk_level=risk_level,
        execution_gap_score=round(eg_score, 1),
        negative_space_score=round(ns_score, 1),
        investigation_score=round(inv_score, 1),
        escalation_score=round(esc_score, 1),
        anomaly_score=round(anomaly_score, 1),
        peer_deviation_score=round(peer_dev_score, 1),
        primary_concern=primary_concern
    )

def populate_priority_review_queue(db: Session, top_n: int = 100) -> List[ReviewQueueItem]:
    """
    Ranks cases across the entire dataset to populate the Top 100 Priority Review Queue.
    Evaluates severity, execution gaps (rapid closure, missing escalation), asset criticality,
    and investigation depth.
    """
    print(f"[*] Scoring and populating top {top_n} Priority Review Queue...")
    db.query(ReviewQueueItem).delete()
    
    # Query all cases with alerts, escalations, and investigations
    cases = db.query(Case).all()
    
    scored_candidates = []
    
    for case in cases:
        alert = db.query(Alert).filter(Alert.alert_id == case.alert_id).first()
        if not alert:
            continue
            
        inv_count = db.query(Investigation).filter(Investigation.case_id == case.case_id).count()
        esc = db.query(Escalation).filter(Escalation.case_id == case.case_id).first()
        is_escalated = esc.escalated if esc else False
        
        # Base severity score
        sev_scores = {"CRITICAL": 40.0, "HIGH": 25.0, "MEDIUM": 12.0, "LOW": 5.0}
        score = sev_scores.get(case.severity, 10.0)
        
        reasons = []
        workflow_status = "Complete"
        
        # Gap 1: Rapid closure on High/Critical
        closure_mins = 999.0
        if alert.created_at and alert.closed_at:
            closure_mins = (alert.closed_at - alert.created_at).total_seconds() / 60.0
            if closure_mins <= settings.RAPID_CLOSURE_THRESHOLD_MINUTES and case.severity in ["CRITICAL", "HIGH"]:
                score += 25.0
                reasons.append(f"Rapid closure ({closure_mins:.1f}m)")
                workflow_status = "Rapid Closure"
                
        # Gap 2: Missing escalation on Critical
        if case.severity == "CRITICAL" and not is_escalated:
            score += 25.0
            reasons.append("Missing mandatory escalation")
            workflow_status = "Missing Escalation"
            
        # Gap 3: Missing or low investigation on Critical/High
        if inv_count == 0:
            score += 20.0
            reasons.append("Zero technical investigation")
            if workflow_status == "Complete":
                workflow_status = "Missing Investigation"
        elif inv_count == 1 and case.severity in ["CRITICAL", "HIGH"]:
            score += 10.0
            reasons.append("Low investigation depth")
            
        # Gap 4: Asset criticality boost
        if alert.asset_criticality == "CRITICAL":
            score += 10.0
            
        # Gap 5: Reopened case
        if (case.reopen_count or 0) > 0:
            score += 10.0
            reasons.append(f"Reopened {case.reopen_count}x")
            
        if not reasons:
            reasons.append("Routine supervisory audit sample")
            
        priority_score = min(100.0, round(score, 1))
        
        scored_candidates.append({
            "case_id": case.case_id,
            "alert_id": alert.alert_id,
            "cse_id": case.cse_id,
            "priority_score": priority_score,
            "primary_reason": " • ".join(reasons),
            "severity": case.severity,
            "asset_criticality": alert.asset_criticality,
            "workflow_integrity_status": workflow_status,
            "evidence_count": inv_count
        })
        
    # Sort descending by priority_score
    scored_candidates.sort(key=lambda x: x["priority_score"], reverse=True)
    top_candidates = scored_candidates[:top_n]
    
    queue_items = []
    for cand in top_candidates:
        item = ReviewQueueItem(
            case_id=cand["case_id"],
            alert_id=cand["alert_id"],
            cse_id=cand["cse_id"],
            priority_score=cand["priority_score"],
            primary_reason=cand["primary_reason"],
            severity=cand["severity"],
            asset_criticality=cand["asset_criticality"],
            workflow_integrity_status=cand["workflow_integrity_status"],
            evidence_count=cand["evidence_count"],
            reviewed=False
        )
        queue_items.append(item)
        
    db.bulk_save_objects(queue_items)
    db.commit()
    print(f"[+] Top {len(queue_items)} priority review cases committed.")
    return queue_items
