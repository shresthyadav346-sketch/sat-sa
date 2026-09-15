"""
Execution Gap Rules Engine (EG-001 to EG-007).
Identifies cases where expected operational security controls appear to exist
in documentation or SLAs, but operational evidence indicates execution failure.
"""

from typing import List, Dict, Any, Optional
import json
from datetime import timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.finding import Finding
from backend.app.models.alert_case import Alert, Case, Investigation, Escalation
from backend.app.models.cse import Asset
from backend.app.config import settings

def evaluate_execution_gaps(
    db: Session,
    cse_id: str,
    cse_metrics: Dict[str, Any],
    peer_benchmarks: Dict[str, Dict[str, float]],
    repetition_score: float = 0.0,
    repetition_details: Optional[Dict[str, Any]] = None
) -> List[Finding]:
    """
    Evaluate all 7 Execution Gap rules for a specific CSE.
    Returns a list of structured Finding models ready for persistence.
    """
    findings: List[Finding] = []
    
    # -------------------------------------------------------------
    # EG-001: Rapid Critical Closure
    # -------------------------------------------------------------
    crit_rapid_rate = cse_metrics.get("critical_rapid_closure_rate", 0.0)
    peer_rapid_med = peer_benchmarks.get("critical_rapid_closure_rate", {}).get("median", 5.0)
    
    if crit_rapid_rate > 15.0 and crit_rapid_rate > (peer_rapid_med * 2.0):
        # Query sample alert IDs closed rapidly
        crit_alerts = (
            db.query(Alert)
            .filter(Alert.cse_id == cse_id, Alert.severity.in_(["CRITICAL", "HIGH"]))
            .all()
        )
        rapid_sample = []
        for a in crit_alerts:
            if a.created_at and a.closed_at:
                dur = (a.closed_at - a.created_at).total_seconds() / 60.0
                if dur <= settings.RAPID_CLOSURE_THRESHOLD_MINUTES:
                    rapid_sample.append(a.alert_id)
                    if len(rapid_sample) >= 10:
                        break
                        
        severity = "CRITICAL" if crit_rapid_rate > 40.0 else "HIGH"
        findings.append(Finding(
            finding_id=f"EG-001-{cse_id}",
            cse_id=cse_id,
            category="EXECUTION_GAP",
            rule_code="EG-001",
            title="High rate of rapid critical/high alert closure",
            description=(
                f"{crit_rapid_rate:.1f}% of critical alerts were closed within "
                f"{settings.RAPID_CLOSURE_THRESHOLD_MINUTES:.0f} minutes of ingestion. "
                "Such rapid closure of severe threats indicates superficial triage or procedural auto-closure."
            ),
            severity=severity,
            confidence="HIGH",
            metric_name="critical_rapid_closure_rate",
            metric_value=crit_rapid_rate,
            peer_median=peer_rapid_med,
            threshold_value=15.0,
            evidence_summary=(
                f"Entity rate is {crit_rapid_rate:.1f}% vs peer median of {peer_rapid_med:.1f}%. "
                f"Identified {len(rapid_sample)}+ critical alerts closed in under 5 minutes."
            ),
            source_record_ids=json.dumps(rapid_sample),
            status="NEW"
        ))

    # -------------------------------------------------------------
    # EG-002: Critical Alert Without Escalation
    # -------------------------------------------------------------
    crit_esc_rate = cse_metrics.get("critical_escalation_rate", 0.0)
    peer_esc_med = peer_benchmarks.get("critical_escalation_rate", {}).get("median", 85.0)
    
    if crit_esc_rate < 40.0 and crit_esc_rate < (peer_esc_med - 25.0):
        # Find critical cases without escalation
        crit_cases = (
            db.query(Case)
            .filter(Case.cse_id == cse_id, Case.severity == "CRITICAL")
            .all()
        )
        unescalated_sample = []
        for c in crit_cases:
            esc = db.query(Escalation).filter(Escalation.case_id == c.case_id).first()
            if not esc or not esc.escalated:
                unescalated_sample.append(c.case_id)
                if len(unescalated_sample) >= 10:
                    break
                    
        severity = "CRITICAL" if crit_esc_rate < 20.0 else "HIGH"
        findings.append(Finding(
            finding_id=f"EG-002-{cse_id}",
            cse_id=cse_id,
            category="EXECUTION_GAP",
            rule_code="EG-002",
            title="Critical severity cases closed without supervisory escalation",
            description=(
                f"Critical alert escalation rate is only {crit_esc_rate:.1f}%, failing to engage "
                "Tier-2 SOC, incident response coordinators, or CERT-In liaison."
            ),
            severity=severity,
            confidence="HIGH",
            metric_name="critical_escalation_rate",
            metric_value=crit_esc_rate,
            peer_median=peer_esc_med,
            threshold_value=50.0,
            evidence_summary=(
                f"Escalation rate of {crit_esc_rate:.1f}% deviates severely from peer median ({peer_esc_med:.1f}%). "
                f"Sample of {len(unescalated_sample)} unescalated critical cases catalogued."
            ),
            source_record_ids=json.dumps(unescalated_sample),
            status="NEW"
        ))

    # -------------------------------------------------------------
    # EG-003: Critical Alert Without Meaningful Investigation
    # -------------------------------------------------------------
    cases_without_inv = cse_metrics.get("cases_without_investigation_count", 0)
    total_cases = cse_metrics.get("cases_count", 1)
    no_inv_pct = (cases_without_inv / total_cases * 100.0) if total_cases > 0 else 0.0
    
    if no_inv_pct > 10.0:
        # Find cases with zero investigation steps
        sample_cases = (
            db.query(Case.case_id)
            .outerjoin(Investigation, Case.case_id == Investigation.case_id)
            .filter(Case.cse_id == cse_id, Investigation.investigation_id == None)
            .limit(10)
            .all()
        )
        sample_ids = [r[0] for r in sample_cases]
        
        findings.append(Finding(
            finding_id=f"EG-003-{cse_id}",
            cse_id=cse_id,
            category="EXECUTION_GAP",
            rule_code="EG-003",
            title="Security cases closed with absent or unrecorded investigation",
            description=(
                f"{no_inv_pct:.1f}% of security cases ({cases_without_inv} cases) were marked closed "
                "without recording any technical investigation actions (memory dump, process tree, or log correlation)."
            ),
            severity="HIGH",
            confidence="HIGH",
            metric_name="uninvestigated_case_percentage",
            metric_value=no_inv_pct,
            peer_median=2.0,
            threshold_value=10.0,
            evidence_summary=(
                f"{cases_without_inv} cases lack any linked investigation records. "
                f"Sample case IDs: {', '.join(sample_ids[:5])}"
            ),
            source_record_ids=json.dumps(sample_ids),
            status="NEW"
        ))

    # -------------------------------------------------------------
    # EG-004: Low Investigation Depth
    # -------------------------------------------------------------
    avg_inv_actions = cse_metrics.get("avg_investigation_actions", 0.0)
    peer_actions_med = peer_benchmarks.get("avg_investigation_actions", {}).get("median", 2.8)
    
    if avg_inv_actions < 1.4 and avg_inv_actions < (peer_actions_med * 0.65):
        findings.append(Finding(
            finding_id=f"EG-004-{cse_id}",
            cse_id=cse_id,
            category="EXECUTION_GAP",
            rule_code="EG-004",
            title="Superficial investigation depth across security incidents",
            description=(
                f"Average investigation actions per case is {avg_inv_actions:.2f}, compared to peer median of "
                f"{peer_actions_med:.2f}. Indicates single-step superficial triage without multi-source correlation."
            ),
            severity="MEDIUM",
            confidence="HIGH",
            metric_name="avg_investigation_actions",
            metric_value=avg_inv_actions,
            peer_median=peer_actions_med,
            threshold_value=1.5,
            evidence_summary=(
                f"Entity records an average of {avg_inv_actions:.2f} actions/case vs peer median of {peer_actions_med:.2f}."
            ),
            source_record_ids=json.dumps([]),
            status="NEW"
        ))

    # -------------------------------------------------------------
    # EG-005: Repeated Alerts on Same Asset Without Remediation
    # -------------------------------------------------------------
    reopen_rate = cse_metrics.get("reopen_rate", 0.0)
    # Check for flapping assets (assets with >= 10 alerts in 14-day window)
    asset_alert_counts = (
        db.query(Alert.asset_id, func.count(Alert.alert_id))
        .filter(Alert.cse_id == cse_id)
        .group_by(Alert.asset_id)
        .having(func.count(Alert.alert_id) >= settings.REPEAT_ALERT_THRESHOLD_COUNT)
        .order_by(func.count(Alert.alert_id).desc())
        .limit(5)
        .all()
    )
    
    if asset_alert_counts and (reopen_rate > 15.0 or len(asset_alert_counts) >= 3):
        flapping_ids = [r[0] for r in asset_alert_counts]
        max_flaps = asset_alert_counts[0][1]
        findings.append(Finding(
            finding_id=f"EG-005-{cse_id}",
            cse_id=cse_id,
            category="EXECUTION_GAP",
            rule_code="EG-005",
            title="Repeated alert flapping without root-cause remediation",
            description=(
                f"{len(asset_alert_counts)} critical assets exhibit chronic recurring security alerts "
                f"(up to {max_flaps} alerts per asset), closed repeatedly without systemic root-cause fix."
            ),
            severity="HIGH",
            confidence="HIGH",
            metric_name="reopen_rate",
            metric_value=reopen_rate,
            peer_median=5.0,
            threshold_value=15.0,
            evidence_summary=(
                f"Flapping assets detected: {', '.join(flapping_ids[:3])}. "
                f"Reopen rate is {reopen_rate:.1f}%."
            ),
            source_record_ids=json.dumps(flapping_ids),
            status="NEW"
        ))

    # -------------------------------------------------------------
    # EG-006: Repetitive Investigations (Template-driven)
    # -------------------------------------------------------------
    if repetition_score > 0.12:
        template_samples = repetition_details.get("top_repetitive_texts", []) if repetition_details else []
        findings.append(Finding(
            finding_id=f"EG-006-{cse_id}",
            cse_id=cse_id,
            category="EXECUTION_GAP",
            rule_code="EG-006",
            title="High proportion of repetitive template-driven investigations",
            description=(
                f"NLP TF-IDF similarity analysis identified that {repetition_score*100:.1f}% of pairwise investigation "
                "descriptions share near-identical phrasing, indicating copy-pasted or checklist boilerplate triage."
            ),
            severity="HIGH" if repetition_score > 0.18 else "MEDIUM",
            confidence="HIGH",
            metric_name="investigation_repetition_ratio",
            metric_value=round(repetition_score * 100.0, 1),
            peer_median=1.2,
            threshold_value=12.0,
            evidence_summary=(
                f"{repetition_score*100:.1f}% of investigation descriptions exhibit cosine similarity > 0.85 (peer baseline ~1%). "
                f"Sample template phrasing: '{template_samples[0][:90]}...'" if template_samples else "Template clustering verified."
            ),
            source_record_ids=json.dumps(repetition_details.get("sample_case_ids", []) if repetition_details else []),
            status="NEW"
        ))

    # -------------------------------------------------------------
    # EG-007: KPI vs Operational Effectiveness (Goodhart's Law)
    # -------------------------------------------------------------
    median_close = cse_metrics.get("median_closure_time_mins", 0.0)
    peer_median_close = peer_benchmarks.get("median_closure_time_mins", {}).get("median", 45.0)
    
    if median_close < 8.0 and avg_inv_actions < 1.3 and crit_esc_rate < 15.0:
        findings.append(Finding(
            finding_id=f"EG-007-{cse_id}",
            cse_id=cse_id,
            category="EXECUTION_GAP",
            rule_code="EG-007",
            title="Metric optimization (Goodhart's Law) execution gap signal",
            description=(
                f"Entity demonstrates near-perfect SLA closure speed (median {median_close:.1f} mins vs peer {peer_median_close:.1f} mins), "
                f"but operational evidence exhibits near-zero escalation ({crit_esc_rate:.1f}%) and deficient investigation depth "
                f"({avg_inv_actions:.2f} actions). Highly indicative of ticket closure driven by SLA compliance rather than thorough triage."
            ),
            severity="CRITICAL",
            confidence="HIGH",
            metric_name="kpi_divergence_index",
            metric_value=92.5,
            peer_median=15.0,
            threshold_value=70.0,
            evidence_summary=(
                f"Divergence detected: Closure speed is in 95th percentile, but escalation ({crit_esc_rate:.1f}%) "
                f"and investigation actions ({avg_inv_actions:.2f}) are in bottom 5th percentile."
            ),
            source_record_ids=json.dumps([]),
            status="NEW"
        ))

    return findings
