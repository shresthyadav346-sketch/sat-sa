"""
Negative Space Rules Engine (NS-001 to NS-006).
Identifies the absence of expected security evidence:
- Unmonitored or silent critical infrastructure assets
- Omitted workflow stages (Missing Investigation, Missing Escalation)
- Critical monitoring blindspots
"""

from typing import List, Dict, Any
import json
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.finding import Finding
from backend.app.models.cse import Asset
from backend.app.models.alert_case import Alert, Case, Investigation, Escalation

def evaluate_negative_space(
    db: Session,
    cse_id: str,
    cse_metrics: Dict[str, Any],
    peer_benchmarks: Dict[str, Dict[str, float]]
) -> List[Finding]:
    """
    Evaluate all 6 Negative Space rules for a specific CSE.
    Returns structured Finding objects.
    """
    findings: List[Finding] = []
    
    # -------------------------------------------------------------
    # NS-001: Critical Asset With Zero Activity
    # -------------------------------------------------------------
    crit_assets_without_act = cse_metrics.get("crit_assets_without_activity", 0)
    total_crit_assets = cse_metrics.get("critical_assets", 0)
    crit_coverage = cse_metrics.get("critical_coverage", 100.0)
    peer_crit_cov_med = peer_benchmarks.get("critical_coverage", {}).get("median", 98.0)
    
    if crit_assets_without_act > 0 and crit_coverage < 85.0:
        # Query specific silent critical assets
        active_asset_ids = {
            row[0] for row in db.query(Alert.asset_id).filter(Alert.cse_id == cse_id).distinct().all()
        }
        silent_assets = (
            db.query(Asset)
            .filter(Asset.cse_id == cse_id, Asset.criticality == "CRITICAL", ~Asset.asset_id.in_(active_asset_ids))
            .limit(15)
            .all()
        )
        silent_ids = [a.asset_id for a in silent_assets]
        
        severity = "CRITICAL" if crit_coverage < 70.0 else "HIGH"
        findings.append(Finding(
            finding_id=f"NS-001-{cse_id}",
            cse_id=cse_id,
            category="NEGATIVE_SPACE",
            rule_code="NS-001",
            title="Critical assets with complete absence of security telemetry",
            description=(
                f"{crit_assets_without_act} of {total_crit_assets} registered CRITICAL assets have generated "
                "ZERO security alerts or logs over the entire 90-day assessment period. "
                "This indicates a severe telemetry ingestion failure, disabled agent, or network segmentation blindspot."
            ),
            severity=severity,
            confidence="HIGH",
            metric_name="silent_critical_assets_count",
            metric_value=float(crit_assets_without_act),
            peer_median=0.0,
            threshold_value=1.0,
            evidence_summary=(
                f"{crit_assets_without_act} critical assets (e.g., {', '.join(silent_ids[:4])}) show zero alerts. "
                f"Critical coverage is {crit_coverage:.1f}% vs peer baseline of {peer_crit_cov_med:.1f}%."
            ),
            source_record_ids=json.dumps(silent_ids),
            status="NEW"
        ))

    # -------------------------------------------------------------
    # NS-002: Critical Asset With Very Low Activity
    # -------------------------------------------------------------
    alerts_per_asset = cse_metrics.get("alerts_per_asset", 0.0)
    peer_alerts_per_asset = peer_benchmarks.get("alerts_per_asset", {}).get("median", 15.0)
    
    if alerts_per_asset < (peer_alerts_per_asset * 0.35) and cse_metrics.get("total_alerts", 0) > 0:
        findings.append(Finding(
            finding_id=f"NS-002-{cse_id}",
            cse_id=cse_id,
            category="NEGATIVE_SPACE",
            rule_code="NS-002",
            title="Abnormally low alert density across critical systems",
            description=(
                f"Overall alert density is {alerts_per_asset:.1f} alerts/asset compared to the peer median of "
                f"{peer_alerts_per_asset:.1f}. Represents an under-reporting or log filtering anomaly."
            ),
            severity="MEDIUM",
            confidence="MEDIUM",
            metric_name="alerts_per_asset",
            metric_value=alerts_per_asset,
            peer_median=peer_alerts_per_asset,
            threshold_value=peer_alerts_per_asset * 0.4,
            evidence_summary=(
                f"Observed density: {alerts_per_asset:.1f} vs peer baseline: {peer_alerts_per_asset:.1f} alerts/asset."
            ),
            source_record_ids=json.dumps([]),
            status="NEW"
        ))

    # -------------------------------------------------------------
    # NS-003: Missing Investigation Workflow Stage
    # -------------------------------------------------------------
    cases_without_inv = cse_metrics.get("cases_without_investigation_count", 0)
    if cases_without_inv > 25:
        sample_uninv = (
            db.query(Case.case_id)
            .outerjoin(Investigation, Case.case_id == Investigation.case_id)
            .filter(Case.cse_id == cse_id, Investigation.investigation_id == None)
            .limit(10)
            .all()
        )
        sample_ids = [r[0] for r in sample_uninv]
        findings.append(Finding(
            finding_id=f"NS-003-{cse_id}",
            cse_id=cse_id,
            category="NEGATIVE_SPACE",
            rule_code="NS-003",
            title="Systematic omission of investigation phase in case management",
            description=(
                f"Identified {cases_without_inv} cases transitioned directly from alert triage to closure "
                "with zero forensic investigation actions recorded."
            ),
            severity="HIGH",
            confidence="HIGH",
            metric_name="missing_investigation_cases",
            metric_value=float(cases_without_inv),
            peer_median=5.0,
            threshold_value=20.0,
            evidence_summary=(
                f"{cases_without_inv} cases completely bypass technical investigation. Sample: {', '.join(sample_ids[:5])}"
            ),
            source_record_ids=json.dumps(sample_ids),
            status="NEW"
        ))

    # -------------------------------------------------------------
    # NS-004: Missing Escalation for Critical Severity Cases
    # -------------------------------------------------------------
    crit_esc_rate = cse_metrics.get("critical_escalation_rate", 0.0)
    if crit_esc_rate < 30.0:
        crit_cases_without_esc = (
            db.query(Case.case_id)
            .outerjoin(Escalation, Case.case_id == Escalation.case_id)
            .filter(Case.cse_id == cse_id, Case.severity == "CRITICAL", (Escalation.escalated == False) | (Escalation.escalation_id == None))
            .limit(10)
            .all()
        )
        crit_ids = [r[0] for r in crit_cases_without_esc]
        findings.append(Finding(
            finding_id=f"NS-004-{cse_id}",
            cse_id=cse_id,
            category="NEGATIVE_SPACE",
            rule_code="NS-004",
            title="Negative space: Missing mandatory supervisory escalation records",
            description=(
                f"Critical alert escalation record is completely absent in {100.0 - crit_esc_rate:.1f}% "
                "of critical security cases where organizational policy mandates formal escalation."
            ),
            severity="HIGH",
            confidence="HIGH",
            metric_name="missing_escalation_rate",
            metric_value=round(100.0 - crit_esc_rate, 1),
            peer_median=15.0,
            threshold_value=50.0,
            evidence_summary=(
                f"Escalation records absent for {len(crit_ids)}+ sampled critical cases: {', '.join(crit_ids[:5])}"
            ),
            source_record_ids=json.dumps(crit_ids),
            status="NEW"
        ))

    # -------------------------------------------------------------
    # NS-005: Missing Workflow Stage (Lifecycle Integrity)
    # -------------------------------------------------------------
    # Check for alerts closed without case creation despite CRITICAL severity
    crit_alerts_without_case = (
        db.query(Alert.alert_id)
        .filter(Alert.cse_id == cse_id, Alert.severity == "CRITICAL", Alert.case_id == None)
        .limit(10)
        .all()
    )
    if len(crit_alerts_without_case) > 0:
        alert_sample = [r[0] for r in crit_alerts_without_case]
        findings.append(Finding(
            finding_id=f"NS-005-{cse_id}",
            cse_id=cse_id,
            category="NEGATIVE_SPACE",
            rule_code="NS-005",
            title="Workflow integrity break: Critical alerts closed without case instantiation",
            description=(
                "Multiple critical severity alerts were marked as CLOSED without creating an associated "
                "formal case ticket, breaking the audit trail from alert detection to resolution."
            ),
            severity="HIGH",
            confidence="HIGH",
            metric_name="caseless_critical_alerts",
            metric_value=float(len(crit_alerts_without_case)),
            peer_median=0.0,
            threshold_value=1.0,
            evidence_summary=f"Sample caseless critical alerts: {', '.join(alert_sample[:5])}",
            source_record_ids=json.dumps(alert_sample),
            status="NEW"
        ))

    # -------------------------------------------------------------
    # NS-006: Monitoring Coverage Gap Across Entity Assets
    # -------------------------------------------------------------
    monitoring_coverage = cse_metrics.get("monitoring_coverage", 100.0)
    peer_mon_cov_med = peer_benchmarks.get("monitoring_coverage", {}).get("median", 95.0)
    
    if monitoring_coverage < 75.0:
        findings.append(Finding(
            finding_id=f"NS-006-{cse_id}",
            cse_id=cse_id,
            category="NEGATIVE_SPACE",
            rule_code="NS-006",
            title="Broad asset monitoring coverage gap",
            description=(
                f"Entity-wide asset monitoring coverage is only {monitoring_coverage:.1f}% "
                f"(peer median is {peer_mon_cov_med:.1f}%). More than a quarter of all inventory assets "
                "have zero operational telemetry in the centralized SOC."
            ),
            severity="HIGH",
            confidence="HIGH",
            metric_name="monitoring_coverage",
            metric_value=monitoring_coverage,
            peer_median=peer_mon_cov_med,
            threshold_value=80.0,
            evidence_summary=f"Coverage is {monitoring_coverage:.1f}% vs peer baseline of {peer_mon_cov_med:.1f}%.",
            source_record_ids=json.dumps([]),
            status="NEW"
        ))

    return findings
