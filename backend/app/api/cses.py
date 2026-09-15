"""
FastAPI route handlers for Critical Sector Entities (CSE) queries.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any

from backend.app.database import get_db
from backend.app.models.cse import CSE, Asset
from backend.app.models.finding import Finding, RiskScore
from backend.app.models.alert_case import Alert
from backend.app.schemas.cse import CSESummarySchema, CSEDetailSchema, AssetSchema
from backend.app.schemas.finding import FindingSchema
from analytics.metrics.calculator import calculate_cse_metrics, calculate_all_cse_metrics
from analytics.peer_comparison.peer_analyzer import PeerAnalyzer
from ml.clustering.clusterer import PeerClusterer

router = APIRouter(prefix="/api/cses", tags=["CSEs"])

@router.get("", response_model=List[CSESummarySchema])
def list_cses(
    sector: Optional[str] = Query(None, description="Filter by sector (Power, Banking, Telecom, Transport, Defence)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (CRITICAL, HIGH, MEDIUM, LOW)"),
    search: Optional[str] = Query(None, description="Search by name or cse_id"),
    db: Session = Depends(get_db)
):
    """
    List all Critical Sector Entities with their supervisory risk scores and finding counts.
    Sorted by overall supervisory risk descending.
    """
    query = (
        db.query(CSE, RiskScore)
        .outerjoin(RiskScore, CSE.cse_id == RiskScore.cse_id)
    )
    
    if sector:
        query = query.filter(CSE.sector == sector)
    if risk_level:
        query = query.filter(RiskScore.risk_level == risk_level)
    if search:
        s = f"%{search}%"
        query = query.filter((CSE.name.ilike(s)) | (CSE.cse_id.ilike(s)))
        
    query = query.order_by(RiskScore.overall_score.desc().nullslast())
    results = query.all()
    
    output = []
    for cse, score in results:
        findings_count = db.query(Finding).filter(Finding.cse_id == cse.cse_id).count()
        output.append(CSESummarySchema(
            cse_id=cse.cse_id,
            name=cse.name,
            sector=cse.sector,
            criticality=cse.criticality,
            total_assets=cse.total_assets or 0,
            risk_score=score,
            findings_count=findings_count
        ))
    return output

@router.get("/{cse_id}", response_model=CSEDetailSchema)
def get_cse_detail(cse_id: str, db: Session = Depends(get_db)):
    """
    Get in-depth supervisory profile for a specific CSE:
    Risk score breakdown, exact operational metrics, peer deviations, and operational cluster.
    """
    cse = db.query(CSE).filter(CSE.cse_id == cse_id).first()
    if not cse:
        raise HTTPException(status_code=404, detail=f"Entity {cse_id} not found.")
        
    risk_score = db.query(RiskScore).filter(RiskScore.cse_id == cse_id).first()
    metrics = calculate_cse_metrics(db, cse_id)
    
    # Calculate peer deviations
    all_metrics = calculate_all_cse_metrics(db)
    analyzer = PeerAnalyzer(all_metrics)
    deviations = analyzer.get_cse_peer_deviations(cse_id)
    
    # Cluster assignment
    clusterer = PeerClusterer()
    clusters = clusterer.cluster_cses(all_metrics)
    cluster_info = clusters.get(cse_id, {"cluster_id": 0, "tier_name": "Standard Operations"})
    
    return CSEDetailSchema(
        cse_id=cse.cse_id,
        name=cse.name,
        sector=cse.sector,
        criticality=cse.criticality,
        total_assets=cse.total_assets or 0,
        created_at=cse.created_at,
        risk_score=risk_score,
        metrics=metrics,
        deviations=deviations,
        cluster_info=cluster_info
    )

@router.get("/{cse_id}/findings", response_model=List[FindingSchema])
def get_cse_findings(cse_id: str, db: Session = Depends(get_db)):
    """
    Get all evidence-backed supervisory findings for a specific CSE.
    """
    return (
        db.query(Finding)
        .filter(Finding.cse_id == cse_id)
        .order_by(Finding.severity.desc(), Finding.created_at.desc())
        .all()
    )

@router.get("/{cse_id}/assets", response_model=List[AssetSchema])
def get_cse_assets(cse_id: str, db: Session = Depends(get_db)):
    """
    Get asset inventory for this CSE with criticality and monitoring status.
    """
    return db.query(Asset).filter(Asset.cse_id == cse_id).all()
