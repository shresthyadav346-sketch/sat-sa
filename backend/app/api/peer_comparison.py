"""
FastAPI route handlers for Peer Comparison and Sector Benchmarking.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from backend.app.database import get_db
from backend.app.models.cse import CSE
from analytics.metrics.calculator import calculate_all_cse_metrics
from analytics.peer_comparison.peer_analyzer import PeerAnalyzer
from ml.clustering.clusterer import PeerClusterer

router = APIRouter(prefix="/api/peer-comparison", tags=["Peer Comparison"])

@router.get("")
def get_peer_comparison(
    cse_ids: Optional[str] = Query(None, description="Comma-separated list of CSE IDs to compare (e.g. CSE-007,CSE-014)"),
    db: Session = Depends(get_db)
):
    """
    Compare entities side-by-side against statistical peer baselines.
    Returns:
    - peer_benchmarks: Medians, p25, p75, mins, maxs
    - selected_cses: Individual metrics, deviations, and z-scores
    - cluster_tiers: Operational cluster assignments
    """
    all_metrics = calculate_all_cse_metrics(db)
    analyzer = PeerAnalyzer(all_metrics)
    benchmarks = analyzer.get_peer_benchmarks()
    
    clusterer = PeerClusterer()
    clusters = clusterer.cluster_cses(all_metrics)
    
    # Parse target CSE IDs
    if cse_ids:
        target_ids = [cid.strip() for cid in cse_ids.split(",") if cid.strip()]
    else:
        # Default to high-profile entities
        target_ids = ["CSE-007", "CSE-014", "CSE-021", "CSE-032", "CSE-041"]
        
    compared_entities = []
    for cid in target_ids:
        if cid in all_metrics:
            cse = db.query(CSE).filter(CSE.cse_id == cid).first()
            deviations = analyzer.get_cse_peer_deviations(cid)
            compared_entities.append({
                "cse_id": cid,
                "name": cse.name if cse else cid,
                "sector": cse.sector if cse else "Unknown",
                "metrics": all_metrics[cid],
                "deviations": deviations,
                "cluster": clusters.get(cid, {})
            })
            
    return {
        "peer_benchmarks": benchmarks,
        "entities": compared_entities,
        "available_cse_ids": list(all_metrics.keys())
    }
