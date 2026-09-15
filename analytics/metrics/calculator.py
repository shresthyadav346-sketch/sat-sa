"""
Core Metrics Calculator for Supervisory Analytics.
Aggregates detection, investigation, escalation, closure, and asset coverage metrics.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import numpy as np

from backend.app.models.cse import CSE, Asset
from backend.app.models.alert_case import Alert, Case, Investigation, Escalation
from backend.app.config import settings

def calculate_cse_metrics(db: Session, cse_id: str) -> Dict[str, Any]:
    """
    Calculate comprehensive operational metrics for a single CSE.
    """
    # 1. Asset Metrics
    total_assets = db.query(Asset).filter(Asset.cse_id == cse_id).count()
    critical_assets = db.query(Asset).filter(Asset.cse_id == cse_id, Asset.criticality == "CRITICAL").count()
    
    # Assets with at least 1 alert
    active_asset_ids = {
        row[0] for row in db.query(Alert.asset_id).filter(Alert.cse_id == cse_id).distinct().all()
    }
    assets_with_activity = len(active_asset_ids)
    
    # Critical assets without activity (Negative space)
    all_crit_assets = db.query(Asset.asset_id).filter(Asset.cse_id == cse_id, Asset.criticality == "CRITICAL").all()
    crit_asset_ids = {row[0] for row in all_crit_assets}
    crit_assets_without_activity = len(crit_asset_ids - active_asset_ids)
    
    monitoring_coverage = (assets_with_activity / total_assets * 100.0) if total_assets > 0 else 100.0
    critical_coverage = ((len(crit_asset_ids) - crit_assets_without_activity) / len(crit_asset_ids) * 100.0) if crit_asset_ids else 100.0

    # 2. Alert Metrics
    alerts = db.query(Alert).filter(Alert.cse_id == cse_id).all()
    total_alerts = len(alerts)
    if total_alerts == 0:
        return {
            "cse_id": cse_id,
            "total_alerts": 0,
            "critical_alerts": 0,
            "high_alerts": 0,
            "alerts_per_asset": 0.0,
            "total_assets": total_assets,
            "critical_assets": critical_assets,
            "crit_assets_without_activity": crit_assets_without_activity,
            "monitoring_coverage": monitoring_coverage,
            "critical_coverage": critical_coverage,
            "rapid_closure_rate": 0.0,
            "critical_rapid_closure_rate": 0.0,
            "median_closure_time_mins": 0.0,
            "escalation_rate": 0.0,
            "critical_escalation_rate": 0.0,
            "cases_count": 0,
            "avg_investigation_actions": 0.0,
            "cases_without_investigation_count": 0,
            "reopen_rate": 0.0
        }

    critical_alerts = [a for a in alerts if a.severity == "CRITICAL"]
    high_alerts = [a for a in alerts if a.severity == "HIGH"]
    
    # Rapid closures (<= settings.RAPID_CLOSURE_THRESHOLD_MINUTES)
    closure_durations = []
    rapid_closure_count = 0
    crit_rapid_count = 0
    
    for a in alerts:
        if a.created_at and a.closed_at:
            duration_mins = (a.closed_at - a.created_at).total_seconds() / 60.0
            closure_durations.append(duration_mins)
            if duration_mins <= settings.RAPID_CLOSURE_THRESHOLD_MINUTES:
                rapid_closure_count += 1
                if a.severity == "CRITICAL":
                    crit_rapid_count += 1
                    
    rapid_closure_rate = (rapid_closure_count / total_alerts * 100.0) if total_alerts > 0 else 0.0
    crit_rapid_closure_rate = (crit_rapid_count / len(critical_alerts) * 100.0) if critical_alerts else 0.0
    median_closure_mins = float(np.median(closure_durations)) if closure_durations else 0.0

    # 3. Cases & Investigations
    cases = db.query(Case).filter(Case.cse_id == cse_id).all()
    cases_count = len(cases)
    crit_cases = [c for c in cases if c.severity == "CRITICAL"]
    
    case_ids = [c.case_id for c in cases]
    inv_actions_by_case: Dict[str, int] = {}
    if case_ids:
        inv_counts = (
            db.query(Investigation.case_id, func.count(Investigation.investigation_id))
            .filter(Investigation.case_id.in_(case_ids))
            .group_by(Investigation.case_id)
            .all()
        )
        inv_actions_by_case = {cid: cnt for cid, cnt in inv_counts}
        
    action_counts = [inv_actions_by_case.get(cid, 0) for cid in case_ids]
    avg_inv_actions = float(np.mean(action_counts)) if action_counts else 0.0
    cases_without_inv = sum(1 for cid in case_ids if inv_actions_by_case.get(cid, 0) == 0)
    
    # 4. Escalations
    escalations = (
        db.query(Escalation)
        .join(Case, Escalation.case_id == Case.case_id)
        .filter(Case.cse_id == cse_id)
        .all()
    )
    total_escalated = sum(1 for e in escalations if e.escalated)
    crit_escalated = sum(1 for e in escalations if e.escalated and e.severity == "CRITICAL")
    
    escalation_rate = (total_escalated / cases_count * 100.0) if cases_count > 0 else 0.0
    critical_escalation_rate = (crit_escalated / len(crit_cases) * 100.0) if crit_cases else 0.0
    
    # Reopen rate
    reopened_cases = sum(1 for c in cases if (c.reopen_count or 0) > 0)
    reopen_rate = (reopened_cases / cases_count * 100.0) if cases_count > 0 else 0.0

    return {
        "cse_id": cse_id,
        "total_alerts": total_alerts,
        "critical_alerts": len(critical_alerts),
        "high_alerts": len(high_alerts),
        "alerts_per_asset": round(total_alerts / total_assets, 2) if total_assets > 0 else 0.0,
        "total_assets": total_assets,
        "critical_assets": critical_assets,
        "crit_assets_without_activity": crit_assets_without_activity,
        "monitoring_coverage": round(monitoring_coverage, 2),
        "critical_coverage": round(critical_coverage, 2),
        "rapid_closure_rate": round(rapid_closure_rate, 2),
        "critical_rapid_closure_rate": round(crit_rapid_closure_rate, 2),
        "median_closure_time_mins": round(median_closure_mins, 2),
        "escalation_rate": round(escalation_rate, 2),
        "critical_escalation_rate": round(critical_escalation_rate, 2),
        "cases_count": cases_count,
        "avg_investigation_actions": round(avg_inv_actions, 2),
        "cases_without_investigation_count": cases_without_inv,
        "reopen_rate": round(reopen_rate, 2)
    }

def calculate_all_cse_metrics(db: Session) -> Dict[str, Dict[str, Any]]:
    """Calculate metrics for all CSEs in the database."""
    cses = db.query(CSE.cse_id).all()
    results = {}
    for (cse_id,) in cses:
        results[cse_id] = calculate_cse_metrics(db, cse_id)
    return results
