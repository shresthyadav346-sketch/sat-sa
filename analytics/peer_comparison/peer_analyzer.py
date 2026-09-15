"""
Peer Comparison & Baseline Statistics Module.
Calculates statistical distributions (median, mean, std, percentiles) and deviations.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd

class PeerAnalyzer:
    def __init__(self, cse_metrics_map: Dict[str, Dict[str, Any]]):
        self.metrics_map = cse_metrics_map
        self.df = pd.DataFrame.from_dict(cse_metrics_map, orient="index")
        
    def get_peer_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate statistical baselines across all entities.
        """
        numeric_cols = [
            "rapid_closure_rate", "critical_rapid_closure_rate", "median_closure_time_mins",
            "escalation_rate", "critical_escalation_rate", "avg_investigation_actions",
            "monitoring_coverage", "critical_coverage", "reopen_rate", "alerts_per_asset"
        ]
        
        benchmarks = {}
        for col in numeric_cols:
            if col in self.df.columns and len(self.df[col]) > 0:
                vals = self.df[col].dropna().values
                benchmarks[col] = {
                    "median": float(np.median(vals)),
                    "mean": float(np.mean(vals)),
                    "std": float(np.std(vals)) if len(vals) > 1 else 0.0,
                    "p25": float(np.percentile(vals, 25)),
                    "p75": float(np.percentile(vals, 75)),
                    "min": float(np.min(vals)),
                    "max": float(np.max(vals))
                }
        return benchmarks

    def get_cse_peer_deviations(self, cse_id: str) -> Dict[str, Dict[str, float]]:
        """
        Calculate deviations and z-scores for a specific CSE relative to peer median.
        """
        if cse_id not in self.metrics_map:
            return {}
            
        benchmarks = self.get_peer_benchmarks()
        cse_metrics = self.metrics_map[cse_id]
        
        deviations = {}
        for metric, stats in benchmarks.items():
            val = float(cse_metrics.get(metric, 0.0))
            peer_med = stats["median"]
            std = stats["std"]
            
            diff = val - peer_med
            z_score = (diff / std) if std > 1e-4 else 0.0
            
            deviations[metric] = {
                "value": round(val, 2),
                "peer_median": round(peer_med, 2),
                "deviation": round(diff, 2),
                "z_score": round(z_score, 2),
                "p25": round(stats["p25"], 2),
                "p75": round(stats["p75"], 2)
            }
            
        return deviations
