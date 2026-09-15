"""
Isolation Forest Operational Anomaly Detector.
Trains an unsupervised Isolation Forest on entity-level operational metrics to detect
multidimensional operational outliers and compute explainable anomaly scores.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler

class OperationalAnomalyDetector:
    def __init__(self, contamination: float = 0.15, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.scaler = RobustScaler()
        self.feature_names = [
            "total_alerts",
            "critical_rapid_closure_rate",
            "median_closure_time_mins",
            "critical_escalation_rate",
            "avg_investigation_actions",
            "monitoring_coverage",
            "reopen_rate"
        ]
        
    def fit_predict(self, cse_metrics_map: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Fit Isolation Forest and return a 0-100 anomaly score for each CSE.
        Higher score = more anomalous operational behavior.
        """
        cse_ids = list(cse_metrics_map.keys())
        if len(cse_ids) < 5:
            # Not enough samples for statistical model
            return {cid: 10.0 for cid in cse_ids}
            
        # Build feature matrix
        rows = []
        for cid in cse_ids:
            m = cse_metrics_map[cid]
            rows.append([
                float(m.get(f, 0.0)) for f in self.feature_names
            ])
            
        X = np.array(rows)
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit model
        self.model.fit(X_scaled)
        
        # decision_function gives negative scores for outliers (lower = more abnormal)
        raw_scores = self.model.decision_function(X_scaled)
        
        # Invert and normalize to 0-100: min raw score becomes ~95, max raw score becomes ~10
        min_s = float(np.min(raw_scores))
        max_s = float(np.max(raw_scores))
        span = (max_s - min_s) if abs(max_s - min_s) > 1e-4 else 1.0
        
        scores: Dict[str, float] = {}
        for idx, cid in enumerate(cse_ids):
            # Invert: lowest decision score -> highest anomaly score
            norm_anomaly = (max_s - raw_scores[idx]) / span
            # Scale to 10 - 95
            score_100 = round(10.0 + (norm_anomaly * 85.0), 1)
            scores[cid] = max(0.0, min(100.0, score_100))
            
        return scores
