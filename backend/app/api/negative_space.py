"""
FastAPI route handlers for Negative Space and Monitoring Blindspots.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional

from backend.app.database import get_db
from backend.app.models.cse import CSE, Asset
from backend.app.models.alert_case import Alert
from backend.app.schemas.cse import AssetSchema

router = APIRouter(prefix="/api/negative-space", tags=["Negative Space"])

@router.get("")
def get_negative_space_overview(db: Session = Depends(get_db)):
    """
    Get systemic overview of negative space conditions across all CSEs:
    Critical asset monitoring coverage, silent assets by sector, and most affected entities.
    """
    total_crit_assets = db.query(Asset).filter(Asset.criticality == "CRITICAL").count()
    
    # Active assets
    active_asset_ids = {
        row[0] for row in db.query(Alert.asset_id).distinct().all()
    }
    
    all_crit_assets = db.query(Asset).filter(Asset.criticality == "CRITICAL").all()
    silent_crit_assets = [a for a in all_crit_assets if a.asset_id not in active_asset_ids]
    
    # Group by CSE
    silent_by_cse: Dict[str, List[Dict[str, Any]]] = {}
    for a in silent_crit_assets:
        if a.cse_id not in silent_by_cse:
            silent_by_cse[a.cse_id] = []
        silent_by_cse[a.cse_id].append({
            "asset_id": a.asset_id,
            "asset_type": a.asset_type,
            "business_function": a.business_function,
            "environment": a.environment
        })
        
    entity_summaries = []
    for cse_id, assets in silent_by_cse.items():
        cse = db.query(CSE).filter(CSE.cse_id == cse_id).first()
        cse_crit_total = db.query(Asset).filter(Asset.cse_id == cse_id, Asset.criticality == "CRITICAL").count()
        entity_summaries.append({
            "cse_id": cse_id,
            "name": cse.name if cse else cse_id,
            "sector": cse.sector if cse else "Unknown",
            "critical_assets_count": cse_crit_total,
            "silent_critical_assets_count": len(assets),
            "critical_coverage_pct": round((cse_crit_total - len(assets)) / cse_crit_total * 100.0, 1) if cse_crit_total > 0 else 100.0,
            "sample_silent_assets": assets[:8]
        })
        
    entity_summaries.sort(key=lambda x: x["silent_critical_assets_count"], reverse=True)
    
    return {
        "total_critical_assets": total_crit_assets,
        "silent_critical_assets_count": len(silent_crit_assets),
        "overall_critical_coverage_pct": round((total_crit_assets - len(silent_crit_assets)) / total_crit_assets * 100.0, 1) if total_crit_assets > 0 else 100.0,
        "affected_entities_count": len(silent_by_cse),
        "entities": entity_summaries
    }

@router.get("/{cse_id}")
def get_cse_negative_space(cse_id: str, db: Session = Depends(get_db)):
    """
    Detailed negative space inspection for a single CSE.
    Categorizes critical assets into:
    - Normal activity
    - Low activity
    - Zero activity (Silent blindspots)
    """
    crit_assets = db.query(Asset).filter(Asset.cse_id == cse_id, Asset.criticality == "CRITICAL").all()
    
    # Alert counts per asset
    counts = (
        db.query(Alert.asset_id, func.count(Alert.alert_id))
        .filter(Alert.cse_id == cse_id)
        .group_by(Alert.asset_id)
        .all()
    )
    alert_counts_map = {row[0]: row[1] for row in counts}
    
    normal_assets = []
    low_activity_assets = []
    zero_activity_assets = []
    
    for a in crit_assets:
        cnt = alert_counts_map.get(a.asset_id, 0)
        asset_info = {
            "asset_id": a.asset_id,
            "asset_type": a.asset_type,
            "business_function": a.business_function,
            "environment": a.environment,
            "alert_count": cnt
        }
        if cnt == 0:
            zero_activity_assets.append(asset_info)
        elif cnt <= 5:
            low_activity_assets.append(asset_info)
        else:
            normal_assets.append(asset_info)
            
    return {
        "cse_id": cse_id,
        "total_critical_assets": len(crit_assets),
        "breakdown": {
            "normal_activity_count": len(normal_assets),
            "low_activity_count": len(low_activity_assets),
            "zero_activity_count": len(zero_activity_assets)
        },
        "zero_activity_assets": zero_activity_assets,
        "low_activity_assets": low_activity_assets,
        "normal_assets": normal_assets[:10]  # Sample
    }
