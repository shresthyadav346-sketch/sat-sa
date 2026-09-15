"""
Ground-truth anomaly injection rules for synthetic SOC dataset.
Enforces realistic operational behavior patterns for validation:
- CSE-007: Rapid Critical Closure & Missing Escalation
- CSE-014: Critical Asset Blindspot / Negative Space
- CSE-021: Template Spammer / Repetitive Investigations
- CSE-032: Chronic Alert Flapping on Same Assets without Remediation
- CSE-041: Metric Optimization (Goodhart's Law) - rapid SLA, 0 investigation actions
"""

from typing import Dict, Any
import random
from datetime import timedelta

ANOMALY_PROFILES: Dict[str, Dict[str, Any]] = {
    "CSE-007": {
        "name": "State Grid Northern Transmission",
        "sector": "Power",
        "anomaly_type": "RAPID_CRITICAL_CLOSURE_AND_ESCALATION_FAILURE",
        "description": "Critical alerts closed under 3 minutes; minimal escalation; superficial triage.",
        "rapid_closure_rate": 0.65,        # 65% of critical alerts closed in < 3 mins
        "escalation_rate": 0.10,           # Only 10% of critical alerts escalated
        "min_inv_actions": 0,
        "max_inv_actions": 1,
        "inv_text_template": "Quick check performed. False alarm. Closed.",
    },
    "CSE-014": {
        "name": "National Payment Clearing Switch",
        "sector": "Banking",
        "anomaly_type": "CRITICAL_ASSET_MONITORING_BLINDSPOT",
        "description": "Has high critical asset count, but 35% of critical assets have ZERO alerts.",
        "zero_activity_asset_ratio": 0.35, # 35% of critical assets receive 0 alerts
        "suppress_telemetry": True,
        "rapid_closure_rate": 0.05,
        "escalation_rate": 0.85,
    },
    "CSE-021": {
        "name": "Metro Transit Rail Automation",
        "sector": "Transport",
        "anomaly_type": "REPETITIVE_INVESTIGATION_TEMPLATES",
        "description": "High text repetition across investigations. Copy-pasted triage notes.",
        "repetition_rate": 0.80,            # 80% copy-paste identical template
        "template_pool": [
            "Checked firewall and antivirus logs. No abnormal lateral traffic observed. Closed as benign activity.",
            "Reviewed endpoint security events. Verified with system owner. Benign administrative activity.",
            "Standard log audit completed. No malicious IOC matches. Ticket resolved."
        ],
        "rapid_closure_rate": 0.08,
        "escalation_rate": 0.75,
    },
    "CSE-032": {
        "name": "Federal Satellite Telemetry Centre",
        "sector": "Telecom",
        "anomaly_type": "REPEATED_ALERTS_NO_ROOT_CAUSE",
        "description": "Chronic alert flapping on 4 key database assets; closed repeatedly without fix.",
        "flapping_asset_count": 4,
        "repeat_alert_burst": 22,          # Each flapping asset gets 20+ alerts
        "reopen_rate": 0.40,
        "rapid_closure_rate": 0.05,
        "escalation_rate": 0.60,
    },
    "CSE-041": {
        "name": "Naval Strategic Logistics Depot",
        "sector": "Defence",
        "anomaly_type": "METRIC_OPTIMIZATION_GOODHARTS_LAW",
        "description": "Near-perfect SLA closure metrics (< 8 min median), but 0 evidence and 0 escalation.",
        "rapid_closure_rate": 0.92,
        "escalation_rate": 0.04,
        "zero_evidence_rate": 0.95,
        "min_inv_actions": 0,
        "max_inv_actions": 1,
    }
}
