"""
SAT-SA Synthetic Data Generator
Generates realistic SOC telemetry across 35 CSEs with injected ground-truth anomalies.
Guaranteed offline-capable, deterministic with random seed, and high-performance.
"""

import os
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
import pandas as pd

from backend.app.database import SessionLocal, init_db
from backend.app.models.cse import CSE, Asset
from backend.app.models.alert_case import Alert, Case, Investigation, Escalation
from backend.app.models.metadata import DatasetVersion
from data_generator.inject_anomalies import ANOMALY_PROFILES

SECTORS = ["Power", "Banking", "Telecom", "Transport", "Defence"]
ASSET_TYPES = [
    ("SCADA RTU / PLC", "Industrial Control Gateway"),
    ("Core Banking Switch", "Payment Processing Engine"),
    ("Domain Controller (AD)", "Identity and Access Management"),
    ("NextGen Firewall", "Perimeter Defense"),
    ("Relational Database Server", "Transactional Database"),
    ("Web Application Server", "Customer Portal"),
    ("OT Engineering Workstation", "Substation Automation"),
    ("SIEM Collector Node", "Telemetry Aggregation"),
]

ALERT_CATEGORIES = [
    ("Privilege Escalation", "CRITICAL"),
    ("Ransomware Payload Detected", "CRITICAL"),
    ("Unauthorized Lateral Movement", "HIGH"),
    ("Data Exfiltration (High Volume)", "CRITICAL"),
    ("Brute Force Authentication", "MEDIUM"),
    ("Malicious PowerShell Execution", "HIGH"),
    ("Port Sweep / Reconnaissance", "LOW"),
    ("Credential Dumping (Mimikatz)", "CRITICAL"),
    ("Suspicious Service Creation", "HIGH"),
    ("Anomalous Outbound SSH/RDP", "MEDIUM"),
]

INVESTIGATION_ACTIONS = [
    "Firewall Log Correlation",
    "Endpoint Memory Dump Analysis",
    "Process Tree Inspection",
    "Network Packet Capture",
    "Active Directory Audit Review",
    "Threat Intelligence Hash Verification",
    "User Activity Timeline Reconstruction",
    "Host Isolation and Quarantine",
]

NORMAL_INVESTIGATION_DESCRIPTIONS = [
    "Correlated firewall logs with source workstation. Identified unusual SMB beaconing. Verified process hash against threat intelligence. Quarantined infected endpoint and revoked Kerberos ticket.",
    "Analyst reviewed authentication failures. Found 45 failed attempts followed by success. Verified with user who confirmed forgotten password. Logged as benign positive with password reset.",
    "Examined PowerShell process argument. Found obfuscated base64 payload downloading staging script. Isolated machine from VLAN and submitted hash to incident response.",
    "High outbound data transfer inspected. Source was automated scheduled backup to disaster recovery cluster. Verified backup schedule and checksums. Benign operational transfer.",
    "Memory dump analysis showed code injection into svchost.exe. Extracted C2 IP address and blocked at perimeter firewall. Assigned Tier-2 IR for full disk forensic imaging."
]

def generate_synthetic_soc_dataset(
    num_cses: int = 45,
    base_alerts_per_cse: int = 800,
    days_history: int = 90,
    seed: int = 42,
    db_session: Session = None,
    export_csv: bool = True
) -> Dict[str, int]:
    """
    Generate complete synthetic dataset with injected ground-truth anomalies.
    Returns counts of generated entities.
    """
    random.seed(seed)
    now = datetime.utcnow()
    start_date = now - timedelta(days=days_history)
    
    cses_data: List[CSE] = []
    assets_data: List[Asset] = []
    alerts_data: List[Alert] = []
    cases_data: List[Case] = []
    investigations_data: List[Investigation] = []
    escalations_data: List[Escalation] = []
    
    print(f"[*] Generating {num_cses} Critical Sector Entities...")
    
    # 1. Create CSEs
    cse_id_list = [f"CSE-{i:03d}" for i in range(1, num_cses + 1)]
    for cse_id in cse_id_list:
        if cse_id in ANOMALY_PROFILES:
            name = ANOMALY_PROFILES[cse_id]["name"]
            sector = ANOMALY_PROFILES[cse_id]["sector"]
            crit = "CRITICAL"
        else:
            sector = random.choice(SECTORS)
            name = f"{sector} Critical Infrastructure Node {cse_id}"
            crit = random.choice(["CRITICAL", "HIGH", "MEDIUM"])
            
        cse = CSE(
            cse_id=cse_id,
            name=name,
            sector=sector,
            criticality=crit,
            total_assets=0,
            created_at=start_date - timedelta(days=180)
        )
        cses_data.append(cse)
        
        # 2. Create Assets for this CSE (40 to 110 assets per CSE)
        asset_count = random.randint(45, 110)
        # CSE-014 has high critical assets to demonstrate the monitoring gap
        if cse_id == "CSE-014":
            asset_count = 135
            
        cse_assets: List[Asset] = []
        for a_idx in range(1, asset_count + 1):
            asset_id = f"AST-{cse_id}-{a_idx:03d}"
            atype, bfunc = random.choice(ASSET_TYPES)
            
            # Asset criticality distribution
            if cse_id == "CSE-014":
                acrit = "CRITICAL" if a_idx <= 65 else ("HIGH" if a_idx <= 100 else "MEDIUM")
            else:
                acrit = "CRITICAL" if a_idx <= int(asset_count * 0.28) else (
                    "HIGH" if a_idx <= int(asset_count * 0.65) else random.choice(["MEDIUM", "LOW"])
                )
                
            env = "Production" if acrit in ["CRITICAL", "HIGH"] else random.choice(["Production", "Staging", "DR"])
            asset = Asset(
                asset_id=asset_id,
                cse_id=cse_id,
                asset_type=atype,
                criticality=acrit,
                business_function=bfunc,
                environment=env,
                monitoring_status="ACTIVE"
            )
            cse_assets.append(asset)
            assets_data.append(asset)
            
        cse.total_assets = len(cse_assets)
        
        # 3. Generate Alerts for this CSE
        anomaly_cfg = ANOMALY_PROFILES.get(cse_id, {})
        alert_multiplier = 1.0
        if cse_id == "CSE-007":
            alert_multiplier = 1.4  # High volume
        elif cse_id == "CSE-014":
            alert_multiplier = 0.5  # Suppressed volume
        elif cse_id == "CSE-032":
            alert_multiplier = 1.3
            
        target_alerts = int(base_alerts_per_cse * alert_multiplier)
        
        # Determine available assets for alerts (Handling CSE-014 Negative Space)
        available_assets = list(cse_assets)
        zero_activity_assets = set()
        if cse_id == "CSE-014":
            # In CSE-014, hide 35% of CRITICAL assets from receiving ANY alerts
            crit_assets = [a for a in cse_assets if a.criticality == "CRITICAL"]
            suppress_count = int(len(crit_assets) * 0.40)
            zero_activity_assets = set(crit_assets[:suppress_count])
            available_assets = [a for a in cse_assets if a not in zero_activity_assets]
            
        # Flapping assets for CSE-032
        flapping_assets = []
        if cse_id == "CSE-032":
            flapping_assets = [a for a in cse_assets if a.criticality == "CRITICAL"][:4]
            
        alert_seq = 1
        case_seq = 1
        inv_seq = 1
        esc_seq = 1
        
        # Generate periodic alerts over history window
        for _ in range(target_alerts):
            # Select asset
            if flapping_assets and random.random() < 0.35:
                asset = random.choice(flapping_assets)
            else:
                asset = random.choice(available_assets)
                
            # Alert category & severity
            cat_name, default_sev = random.choice(ALERT_CATEGORIES)
            
            # Weighted severity distribution
            r_sev = random.random()
            if r_sev < 0.18:
                severity = "CRITICAL"
            elif r_sev < 0.45:
                severity = "HIGH"
            elif r_sev < 0.80:
                severity = "MEDIUM"
            else:
                severity = "LOW"
                
            # If critical asset, boost severity probability
            if asset.criticality == "CRITICAL" and random.random() < 0.40:
                severity = "CRITICAL"
                
            # Alert timestamps
            days_ago = random.uniform(0, days_history)
            created_ts = now - timedelta(days=days_ago, minutes=random.randint(1, 1440))
            
            # Closure duration logic (Ground-truth injected anomalies)
            is_rapid_closure = False
            if cse_id == "CSE-007" and severity in ["CRITICAL", "HIGH"]:
                # CSE-007: 65% closed in < 3 minutes
                if random.random() < anomaly_cfg.get("rapid_closure_rate", 0.65):
                    close_duration_mins = random.uniform(0.5, 2.5)
                    ack_delay = random.uniform(0.1, 0.5)
                    is_rapid_closure = True
                else:
                    close_duration_mins = random.uniform(15, 60)
                    ack_delay = random.uniform(2, 12)
            elif cse_id == "CSE-041":
                # CSE-041: 92% closed rapidly to optimize SLA metrics
                close_duration_mins = random.uniform(0.5, 2.2)
                ack_delay = random.uniform(0.1, 0.5)
                is_rapid_closure = True
            else:
                # Normal baseline
                if random.random() < 0.04:  # Baseline 4% rapid closure
                    close_duration_mins = random.uniform(0.5, 2.5)
                    ack_delay = random.uniform(0.1, 0.5)
                    is_rapid_closure = True
                else:
                    ack_delay = random.uniform(2, 15)
                    if severity == "CRITICAL":
                        close_duration_mins = random.uniform(30, 180)
                    elif severity == "HIGH":
                        close_duration_mins = random.uniform(20, 90)
                    else:
                        close_duration_mins = random.uniform(10, 45)
                        
            ack_ts = created_ts + timedelta(minutes=ack_delay)
            close_ts = ack_ts + timedelta(minutes=close_duration_mins)
            
            alert_id = f"ALT-{cse_id}-{alert_seq:05d}"
            alert_seq += 1
            
            disposition = "False Positive" if random.random() < 0.45 else ("True Positive" if severity in ["CRITICAL", "HIGH"] else "Benign Positive")
            
            # Decide if alert generates a Case
            has_case = False
            if severity == "CRITICAL":
                has_case = True
            elif severity == "HIGH":
                has_case = random.random() < 0.75
            elif severity == "MEDIUM":
                has_case = random.random() < 0.30
            else:
                has_case = random.random() < 0.10
                
            case_id = f"CAS-{cse_id}-{case_seq:05d}" if has_case else None
            if has_case:
                case_seq += 1
                
            alert = Alert(
                alert_id=alert_id,
                cse_id=cse_id,
                asset_id=asset.asset_id,
                timestamp=created_ts,
                severity=severity,
                alert_category=cat_name,
                source_ip=f"10.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
                destination_ip=f"192.168.{random.randint(1, 10)}.{random.randint(1, 254)}",
                asset_criticality=asset.criticality,
                status="CLOSED",
                disposition=disposition,
                created_at=created_ts,
                acknowledged_at=ack_ts,
                closed_at=close_ts,
                analyst_id=f"ANL-{random.randint(101, 118)}",
                case_id=case_id
            )
            alerts_data.append(alert)
            
            # 4. Generate Case, Investigations, Escalations if Case exists
            if has_case:
                case_created_ts = ack_ts + timedelta(minutes=random.randint(1, 5))
                inv_start_ts = case_created_ts + timedelta(minutes=random.randint(1, 10))
                case_close_ts = max(close_ts, inv_start_ts + timedelta(minutes=random.randint(5, 30)))
                
                # Reopen count (CSE-032 has higher reopen count)
                reopens = 0
                if cse_id == "CSE-032" and asset in flapping_assets:
                    reopens = random.choice([1, 2, 3])
                    
                case = Case(
                    case_id=case_id,
                    cse_id=cse_id,
                    alert_id=alert_id,
                    priority=severity,
                    severity=severity,
                    assigned_analyst=alert.analyst_id,
                    created_at=case_created_ts,
                    investigation_started_at=inv_start_ts,
                    closed_at=case_close_ts,
                    status="CLOSED",
                    closure_reason=f"Resolved via standard protocol - {disposition}",
                    resolution=f"Action completed by {alert.analyst_id}",
                    reopen_count=reopens
                )
                cases_data.append(case)
                
                # 5. Investigation generation
                num_actions = 0
                if cse_id in ["CSE-007", "CSE-041"]:
                    # Anomaly: 0 or 1 superficial action
                    num_actions = random.choice([0, 1])
                else:
                    if severity == "CRITICAL":
                        num_actions = random.randint(2, 5)
                    elif severity == "HIGH":
                        num_actions = random.randint(1, 3)
                    else:
                        num_actions = random.randint(1, 2)
                        
                for act_idx in range(num_actions):
                    inv_id = f"INV-{cse_id}-{inv_seq:05d}"
                    inv_seq += 1
                    
                    # Investigation description selection
                    if cse_id == "CSE-021" and random.random() < 0.80:
                        desc = random.choice(anomaly_cfg["template_pool"])
                    elif cse_id in ["CSE-007", "CSE-041"]:
                        desc = "Checked logs and closed." if random.random() < 0.6 else "Alert verified. No action required."
                    else:
                        desc = random.choice(NORMAL_INVESTIGATION_DESCRIPTIONS)
                        
                    inv = Investigation(
                        investigation_id=inv_id,
                        case_id=case_id,
                        analyst_id=alert.analyst_id,
                        timestamp=inv_start_ts + timedelta(minutes=act_idx * 12),
                        action=random.choice(INVESTIGATION_ACTIONS),
                        description=desc,
                        evidence_count=0 if cse_id == "CSE-041" else random.randint(1, 6),
                        root_cause="Credential misuse / unauthorized command" if disposition == "True Positive" else "Noise / benign utility",
                        resolution="Host patched & alert cleared"
                    )
                    investigations_data.append(inv)
                    
                # 6. Escalation generation
                # Determine if escalated
                should_escalate = False
                if severity == "CRITICAL":
                    if cse_id == "CSE-007":
                        should_escalate = random.random() < 0.10  # Anomaly: only 10%
                    elif cse_id == "CSE-041":
                        should_escalate = random.random() < 0.04  # Anomaly: only 4%
                    else:
                        should_escalate = random.random() < 0.88  # Normal baseline: 88%
                elif severity == "HIGH":
                    if cse_id in ["CSE-007", "CSE-041"]:
                        should_escalate = random.random() < 0.05
                    else:
                        should_escalate = random.random() < 0.55
                else:
                    should_escalate = random.random() < 0.08
                    
                if should_escalate or random.random() < 0.05:
                    esc_id = f"ESC-{cse_id}-{esc_seq:05d}"
                    esc_seq += 1
                    escalation = Escalation(
                        escalation_id=esc_id,
                        case_id=case_id,
                        severity=severity,
                        escalated=should_escalate,
                        escalation_time=case_created_ts + timedelta(minutes=random.randint(10, 45)) if should_escalate else None,
                        escalated_by=alert.analyst_id if should_escalate else None,
                        escalated_to=random.choice(["Tier-2 SOC", "CISO Incident Response", "NCIIPC Advisory Group", "CERT-In Liaison"]) if should_escalate else None,
                        escalation_reason=f"Mandatory escalation for {severity} threat pattern" if should_escalate else "Not escalated per initial triage"
                    )
                    escalations_data.append(escalation)

    print(f"[+] Total generated:")
    print(f"    CSEs: {len(cses_data)}")
    print(f"    Assets: {len(assets_data)}")
    print(f"    Alerts: {len(alerts_data)}")
    print(f"    Cases: {len(cases_data)}")
    print(f"    Investigations: {len(investigations_data)}")
    print(f"    Escalations: {len(escalations_data)}")
    
    # Save to database if session provided
    if db_session:
        print("[*] Persisting to database...")
        from backend.app.models.review import ReviewQueueItem, AuditLog
        from backend.app.models.finding import Finding, RiskScore
        
        db_session.query(ReviewQueueItem).delete()
        db_session.query(Finding).delete()
        db_session.query(RiskScore).delete()
        db_session.query(Escalation).delete()
        db_session.query(Investigation).delete()
        db_session.query(Case).delete()
        db_session.query(Alert).delete()
        db_session.query(Asset).delete()
        db_session.query(CSE).delete()
        
        db_session.bulk_save_objects(cses_data)
        db_session.bulk_save_objects(assets_data)
        db_session.bulk_save_objects(alerts_data)
        db_session.bulk_save_objects(cases_data)
        db_session.bulk_save_objects(investigations_data)
        db_session.bulk_save_objects(escalations_data)
        
        # Record dataset version
        version = DatasetVersion(
            version_id="v1.0-synthetic-sih",
            name="SIH Synthetic SOC Telemetry Dataset",
            description="35 CSEs across 5 critical sectors with injected ground-truth operational anomalies.",
            total_records=len(alerts_data),
            is_active=True
        )
        db_session.merge(version)
        db_session.commit()
        print("[+] Database population complete!")
        
    # Export CSVs for offline portability
    if export_csv:
        os.makedirs("sample_data", exist_ok=True)
        print("[*] Exporting CSV summaries to sample_data/ ...")
        pd.DataFrame([{
            "cse_id": c.cse_id, "name": c.name, "sector": c.sector,
            "criticality": c.criticality, "total_assets": c.total_assets
        } for c in cses_data]).to_csv("sample_data/cses.csv", index=False)
        
        pd.DataFrame([{
            "asset_id": a.asset_id, "cse_id": a.cse_id, "asset_type": a.asset_type,
            "criticality": a.criticality, "business_function": a.business_function,
            "environment": a.environment, "monitoring_status": a.monitoring_status
        } for a in assets_data]).to_csv("sample_data/assets.csv", index=False)
        
    return {
        "cses": len(cses_data),
        "assets": len(assets_data),
        "alerts": len(alerts_data),
        "cases": len(cases_data),
        "investigations": len(investigations_data),
        "escalations": len(escalations_data)
    }

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    try:
        counts = generate_synthetic_soc_dataset(db_session=db)
        print("[SUCCESS] Synthetic dataset generated and committed.")
    finally:
        db.close()
