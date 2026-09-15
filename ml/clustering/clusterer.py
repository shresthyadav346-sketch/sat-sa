"""
K-Means Operational Peer Clustering Module.
Clusters CSEs into comparable operational groups based on operational volume and asset scale.
"""

from typing import Dict, Any, List
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class PeerClusterer:
    def __init__(self, n_clusters: int = 3, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        self.scaler = StandardScaler()
        
    def cluster_cses(self, cse_metrics_map: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Group entities into comparable operational tiers.
        Returns cluster assignments and tier descriptions.
        """
        cse_ids = list(cse_metrics_map.keys())
        if len(cse_ids) < self.n_clusters:
            return {cid: {"cluster_id": 0, "tier_name": "Standard Operations"} for cid in cse_ids}
            
        features = []
        for cid in cse_ids:
            m = cse_metrics_map[cid]
            features.append([
                float(m.get("total_assets", 50)),
                float(m.get("total_alerts", 500)),
                float(m.get("critical_assets", 15))
            ])
            
        X = np.array(features)
        X_scaled = self.scaler.fit_transform(X)
        self.kmeans.fit(X_scaled)
        
        labels = self.kmeans.labels_
        
        # Determine average alert volume per cluster to assign meaningful tier names
        cluster_means = {}
        for c_id in range(self.n_clusters):
            idxs = np.where(labels == c_id)[0]
            cluster_means[c_id] = float(np.mean(X[idxs, 1])) if len(idxs) > 0 else 0.0
            
        sorted_clusters = sorted(cluster_means.items(), key=lambda x: x[1], reverse=True)
        tier_names = ["Tier 1: High-Volume Strategic Infrastructure",
                      "Tier 2: Medium-Scale Critical Operations",
                      "Tier 3: Specialized / Regional Infrastructure"]
        tier_mapping = {sorted_clusters[i][0]: tier_names[i] for i in range(len(sorted_clusters))}
        
        results: Dict[str, Dict[str, Any]] = {}
        for idx, cid in enumerate(cse_ids):
            c_label = int(labels[idx])
            results[cid] = {
                "cluster_id": c_label,
                "tier_name": tier_mapping.get(c_label, f"Operational Tier {c_label}")
            }
            
        return results
