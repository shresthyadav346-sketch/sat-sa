"""
Analysis Runner and Supervisory Pipeline Coordinator.
Orchestrates metrics, peer baselines, ML anomaly detection, NLP repetition analysis,
Execution Gap rules, Negative Space detection, explainable Risk Scoring, and Priority Review Queue.
"""

from typing import Dict, Any, List
import json
from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.models.cse import CSE
from backend.app.models.finding import Finding, RiskScore
from backend.app.models.review import ReviewQueueItem
from backend.app.services.blockchain_audit import create_audit_block
from backend.app.models.metadata import ModelVersion
from analytics.metrics.calculator import calculate_all_cse_metrics
from analytics.peer_comparison.peer_analyzer import PeerAnalyzer
from analytics.rules.execution_gaps import evaluate_execution_gaps
from analytics.negative_space.negative_space import evaluate_negative_space
from analytics.risk_scoring.scorer import calculate_supervisory_risk_score, populate_priority_review_queue
from ml.anomaly_detection.detector import OperationalAnomalyDetector
from ml.clustering.clusterer import PeerClusterer
from ml.nlp.repetition_analyzer import InvestigationRepetitionAnalyzer

def run_full_supervisory_analysis(db: Session = None) -> Dict[str, Any]:
    """
    Run complete SAT-SA analysis pipeline across all active CSEs in the database.
    """
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
        
    try:
        print("[*] STEP 1: Calculating core operational metrics...")
        metrics_map = calculate_all_cse_metrics(db)
        
        print("[*] STEP 2: Computing statistical peer baselines & distributions...")
        peer_analyzer = PeerAnalyzer(metrics_map)
        peer_benchmarks = peer_analyzer.get_peer_benchmarks()
        
        print("[*] STEP 3: Training Isolation Forest anomaly detector...")
        anomaly_detector = OperationalAnomalyDetector()
        anomaly_scores = anomaly_detector.fit_predict(metrics_map)
        
        print("[*] STEP 4: Performing K-Means operational peer clustering...")
        clusterer = PeerClusterer()
        clusters = clusterer.cluster_cses(metrics_map)
        
        print("[*] STEP 5: Running NLP repetition analysis on investigations...")
        nlp_analyzer = InvestigationRepetitionAnalyzer()
        repetition_data: Dict[str, Dict[str, Any]] = {}
        for cse_id in metrics_map.keys():
            repetition_data[cse_id] = nlp_analyzer.analyze_cse_investigations(db, cse_id)
            
        print("[*] STEP 6: Evaluating Execution Gaps & Negative Space rules...")
        # Clear existing un-reviewed findings and risk scores
        db.query(Finding).delete()
        db.query(RiskScore).delete()
        
        all_findings: List[Finding] = []
        all_risk_scores: List[RiskScore] = []
        
        for cse_id, m in metrics_map.items():
            deviations = peer_analyzer.get_cse_peer_deviations(cse_id)
            rep_info = repetition_data.get(cse_id, {})
            rep_score = rep_info.get("repetition_score", 0.0)
            
            # Execution Gap Findings (EG-001 to EG-007)
            eg_findings = evaluate_execution_gaps(
                db=db,
                cse_id=cse_id,
                cse_metrics=m,
                peer_benchmarks=peer_benchmarks,
                repetition_score=rep_score,
                repetition_details=rep_info
            )
            
            # Negative Space Findings (NS-001 to NS-006)
            ns_findings = evaluate_negative_space(
                db=db,
                cse_id=cse_id,
                cse_metrics=m,
                peer_benchmarks=peer_benchmarks
            )
            
            cse_findings = eg_findings + ns_findings
            all_findings.extend(cse_findings)
            
            # Supervisory Risk Score (0-100)
            risk = calculate_supervisory_risk_score(
                cse_id=cse_id,
                cse_metrics=m,
                findings=cse_findings,
                peer_deviations=deviations,
                ml_anomaly_score=anomaly_scores.get(cse_id, 15.0)
            )
            all_risk_scores.append(risk)
            
        db.bulk_save_objects(all_findings)
        db.bulk_save_objects(all_risk_scores)
        db.commit()
        print(f"[+] Persisted {len(all_findings)} supervisory findings and {len(all_risk_scores)} risk scores.")
        
        print("[*] STEP 7: Populating Top 100 Priority Review Queue...")
        populate_priority_review_queue(db, top_n=100)
        
        # Record model versions and audit trail
        mv = ModelVersion(
            model_id="ML-IF-v1.0",
            model_type="ISOLATION_FOREST",
            version="1.0.0",
            parameters=json.dumps({"contamination": 0.15, "n_estimators": 100}),
            metrics=json.dumps({"total_entities_evaluated": len(metrics_map)})
        )
        db.merge(mv)
        
        # Cryptographically Chained Audit Block
        create_audit_block(
            db=db,
            user="system_pipeline",
            action="EXECUTE_FULL_SUPERVISORY_ANALYSIS",
            entity_type="SYSTEM",
            entity_id="GLOBAL",
            details=f"Analyzed {len(metrics_map)} CSEs. Generated {len(all_findings)} findings and top 100 queue."
        )
        
        print("[SUCCESS] SAT-SA Supervisory Analysis Pipeline execution completed!")
        return {
            "cses_analyzed": len(metrics_map),
            "findings_generated": len(all_findings),
            "risk_scores_calculated": len(all_risk_scores),
            "top_review_queue_size": 100
        }
    finally:
        if should_close:
            db.close()

if __name__ == "__main__":
    result = run_full_supervisory_analysis()
    print("Result summary:", result)
