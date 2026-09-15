"""
FastAPI route handlers for Cryptographic Audit Hash Chain (Private Blockchain).
Provides endpoints for retrieving audit blocks, verifying cryptographic chain integrity,
and live demonstration simulations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models.review import AuditLog
from backend.app.schemas.review import AuditLogSchema, ChainVerificationSchema
from backend.app.services.blockchain_audit import verify_chain, compute_block_hash

router = APIRouter(prefix="/api/audit", tags=["Audit Blockchain"])


class TamperSimulationRequest(BaseModel):
    block_index: Optional[int] = None
    tampered_details: str = "[TAMPERED] Unauthorized modification of audit details."


@router.get("/chain", response_model=List[AuditLogSchema])
def get_audit_chain(
    order: str = Query("asc", description="Sort order: 'asc' (chronological block 0..N) or 'desc'"),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Retrieve the full cryptographically hash-chained audit block sequence.
    Each block includes block_index, previous_hash, block_hash, and action payload.
    """
    query = db.query(AuditLog)
    if order.lower() == "desc":
        query = query.order_by(AuditLog.block_index.desc(), AuditLog.log_id.desc())
    else:
        query = query.order_by(AuditLog.block_index.asc(), AuditLog.log_id.asc())
    
    return query.limit(limit).all()


@router.get("/verify", response_model=ChainVerificationSchema)
def verify_audit_chain(db: Session = Depends(get_db)):
    """
    Verify the cryptographic integrity of the entire audit trail.
    Traverses all blocks and recalculates SHA-256 hashes to guarantee no data has been modified.
    """
    return verify_chain(db)


@router.post("/simulate-tamper")
def simulate_tamper(
    req: TamperSimulationRequest = TamperSimulationRequest(),
    db: Session = Depends(get_db)
):
    """
    SIH / NCIIPC Demonstration Utility:
    Deliberately mutate an audit record's details without recomputing hashes
    to demonstrate live tamper detection to supervisory examiners and judges.
    """
    if req.block_index is not None:
        block = db.query(AuditLog).filter(AuditLog.block_index == req.block_index).first()
    else:
        # Default to the middle block or the latest block
        count = db.query(AuditLog).count()
        if count == 0:
            raise HTTPException(status_code=400, detail="Cannot tamper an empty chain. Perform some supervisory actions first.")
        target_idx = max(0, count // 2)
        block = db.query(AuditLog).filter(AuditLog.block_index == target_idx).first()

    if not block:
        raise HTTPException(status_code=404, detail="Target audit block not found.")

    original_details = block.details
    block.details = req.tampered_details
    db.commit()

    return {
        "status": "TAMPER_SIMULATED",
        "tampered_block_index": block.block_index,
        "original_details": original_details,
        "new_details": block.details,
        "message": (
            f"Block #{block.block_index} payload has been altered directly in the database. "
            f"Now call GET /api/audit/verify to observe cryptographic failure detection."
        )
    }


@router.post("/repair-tamper")
def repair_tamper(
    block_index: int = Query(..., description="Block index to re-hash or restore"),
    db: Session = Depends(get_db)
):
    """
    Demo utility to recompute block hash so the chain returns to VALID state.
    """
    block = db.query(AuditLog).filter(AuditLog.block_index == block_index).first()
    if not block:
        raise HTTPException(status_code=404, detail="Target audit block not found.")

    block.block_hash = compute_block_hash(
        block_index=block.block_index,
        timestamp=block.timestamp,
        user=block.user,
        action=block.action,
        entity_type=block.entity_type,
        entity_id=block.entity_id,
        details=block.details,
        previous_hash=block.previous_hash,
        nonce=block.nonce or 0
    )
    db.commit()
    return {"status": "REPAIRED", "block_index": block.block_index, "new_block_hash": block.block_hash}
