"""
This implements a private, append-only hash chain (blockchain-inspired data structure)
for audit-log tamper evidence. It is NOT a distributed ledger / consensus network — by design,
since SAT-SA must run fully offline in air-gapped NCIIPC environments. Each audit entry ('block')
cryptographically commits to the previous entry via SHA-256, so any retroactive modification
of a past audit record changes its hash and breaks the chain for all subsequent blocks,
making tampering detectable via GET /api/audit/verify.
"""

import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from backend.app.models.review import AuditLog

GENESIS_PREVIOUS_HASH = "0" * 64


def compute_block_hash(
    block_index: int,
    timestamp: Union[datetime, str],
    user: str,
    action: str,
    entity_type: str,
    entity_id: str,
    details: Optional[str],
    previous_hash: str,
    nonce: int = 0
) -> str:
    """
    Concatenate block fields into a canonical string in fixed order separated by '|',
    encode UTF-8, and return the SHA-256 hexadecimal digest.
    """
    if isinstance(timestamp, datetime):
        ts_str = timestamp.isoformat()
    elif isinstance(timestamp, str):
        ts_str = timestamp.strip().replace(" ", "T")
    else:
        ts_str = ""

    raw_details = details if details is not None else ""
    canonical_payload = (
        f"{block_index}|{ts_str}|{user}|{action}|{entity_type}|{entity_id}|{raw_details}|{previous_hash}|{nonce}"
    )
    return hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()


def create_audit_block(
    db: Session,
    user: str,
    action: str,
    entity_type: str,
    entity_id: str,
    details: Optional[str] = None,
    dataset_version: str = "v1.0-synthetic",
    rule_version: str = "v1.0.0",
    nonce: int = 0
) -> AuditLog:
    """
    Create and commit a new cryptographically hash-chained audit block.
    If no audit blocks exist, initializes the chain with the genesis block (block_index=0, previous_hash='0'*64).
    """
    last_block = db.query(AuditLog).order_by(AuditLog.block_index.desc(), AuditLog.log_id.desc()).first()

    if last_block is not None and last_block.block_hash:
        previous_hash = last_block.block_hash
        block_index = (last_block.block_index + 1) if last_block.block_index is not None else 0
    else:
        previous_hash = GENESIS_PREVIOUS_HASH
        block_index = 0

    now_utc = datetime.utcnow()
    block_hash = compute_block_hash(
        block_index=block_index,
        timestamp=now_utc,
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        previous_hash=previous_hash,
        nonce=nonce
    )

    audit_entry = AuditLog(
        timestamp=now_utc,
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        dataset_version=dataset_version,
        rule_version=rule_version,
        block_index=block_index,
        previous_hash=previous_hash,
        block_hash=block_hash,
        nonce=nonce
    )

    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry


def verify_chain(db: Session) -> Dict[str, Any]:
    """
    Verify the cryptographic integrity of the entire audit hash chain.
    Walks all blocks ordered by block_index ascending, checking:
      1. Genesis block has previous_hash == '0'*64 and block_index == 0.
      2. Consecutive blocks have current.previous_hash == previous.block_hash and block_index == prev.block_index + 1.
      3. Current block's recomputed SHA-256 hash strictly matches stored block_hash.

    Returns:
      {
        "valid": bool,
        "total_blocks": int,
        "broken_at_index": Optional[int],
        "details": str
      }
    """
    blocks = db.query(AuditLog).order_by(AuditLog.block_index.asc(), AuditLog.log_id.asc()).all()

    if not blocks:
        return {
            "valid": True,
            "total_blocks": 0,
            "broken_at_index": None,
            "details": "Audit chain is empty. Genesis block pending first action."
        }

    previous_stored_hash: Optional[str] = None
    expected_index = 0

    for idx, block in enumerate(blocks):
        # 1. Check sequence index
        if block.block_index != expected_index:
            return {
                "valid": False,
                "total_blocks": len(blocks),
                "broken_at_index": block.block_index,
                "details": f"Sequence anomaly at block #{block.block_index}: expected block_index {expected_index}."
            }

        # 2. Check previous hash linkage
        if expected_index == 0:
            if block.previous_hash != GENESIS_PREVIOUS_HASH:
                return {
                    "valid": False,
                    "total_blocks": len(blocks),
                    "broken_at_index": 0,
                    "details": f"Genesis block #0 invalid: expected previous_hash '{GENESIS_PREVIOUS_HASH}', got '{block.previous_hash}'."
                }
        else:
            if block.previous_hash != previous_stored_hash:
                return {
                    "valid": False,
                    "total_blocks": len(blocks),
                    "broken_at_index": block.block_index,
                    "details": (
                        f"Broken chain link at block #{block.block_index}: previous_hash '{block.previous_hash}' "
                        f"does not match previous block #{expected_index - 1} block_hash '{previous_stored_hash}'."
                    )
                }

        # 3. Recompute block hash from stored fields
        recomputed_hash = compute_block_hash(
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

        if recomputed_hash != block.block_hash:
            return {
                "valid": False,
                "total_blocks": len(blocks),
                "broken_at_index": block.block_index,
                "details": (
                    f"Tamper detected at block #{block.block_index}: recomputed SHA-256 hash '{recomputed_hash}' "
                    f"differs from stored block_hash '{block.block_hash}'. Payload contents were modified."
                )
            }

        previous_stored_hash = block.block_hash
        expected_index += 1

    return {
        "valid": True,
        "total_blocks": len(blocks),
        "broken_at_index": None,
        "details": f"Chain verified. All {len(blocks)} audit blocks cryptographically intact."
    }
