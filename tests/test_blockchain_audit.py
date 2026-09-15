"""
Automated unit and integration tests for SAT-SA's hash-chained tamper-evident audit trail.
Verifies private blockchain integrity, sequential cryptographic block links, and live tamper detection.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.database import Base
from backend.app.models.review import AuditLog
from backend.app.services.blockchain_audit import (
    create_audit_block,
    verify_chain,
    compute_block_hash,
    GENESIS_PREVIOUS_HASH
)
from backend.app.main import app

# Use in-memory SQLite for isolated unit testing
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session():
    """Provides a clean in-memory database schema for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def test_genesis_block_creation(db_session):
    """Asserts that the first block in an empty chain is properly initialized as Genesis."""
    block0 = create_audit_block(
        db=db_session,
        user="supervisory_examiner_1",
        action="SYSTEM_INIT",
        entity_type="SYSTEM",
        entity_id="GLOBAL",
        details="Genesis audit block initialization"
    )

    assert block0.block_index == 0
    assert block0.previous_hash == GENESIS_PREVIOUS_HASH
    assert len(block0.block_hash) == 64
    assert block0.nonce == 0

    verification = verify_chain(db_session)
    assert verification["valid"] is True
    assert verification["total_blocks"] == 1
    assert verification["broken_at_index"] is None


def test_sequential_three_blocks_verification(db_session):
    """Creates 3 audit blocks in sequence and asserts verify_chain returns valid=True."""
    b0 = create_audit_block(
        db=db_session,
        user="examiner_alpha",
        action="REVIEW_CASE",
        entity_type="CASE",
        entity_id="CASE-001",
        details="Initial case review for CSE-007"
    )

    b1 = create_audit_block(
        db=db_session,
        user="examiner_beta",
        action="ACCEPT_FINDING",
        entity_type="FINDING",
        entity_id="EG-001-CSE-007",
        details="Confirmed rapid closure execution gap"
    )

    b2 = create_audit_block(
        db=db_session,
        user="examiner_lead",
        action="GENERATE_REPORT",
        entity_type="REPORT",
        entity_id="REP-2026-Q3",
        details="Formal supervisory assessment generated"
    )

    # Assert block indices are sequential
    assert b0.block_index == 0
    assert b1.block_index == 1
    assert b2.block_index == 2

    # Assert cryptographic hash links
    assert b0.previous_hash == GENESIS_PREVIOUS_HASH
    assert b1.previous_hash == b0.block_hash
    assert b2.previous_hash == b1.block_hash

    # Verify entire chain integrity
    result = verify_chain(db_session)
    assert result["valid"] is True
    assert result["total_blocks"] == 3
    assert result["broken_at_index"] is None


def test_tamper_detection_on_modified_details(db_session):
    """
    Manually modifies one row's details field directly in the DB session,
    then asserts verify_chain returns valid=False with the exact broken_at_index.
    """
    # Create 4 blocks
    for i in range(4):
        create_audit_block(
            db=db_session,
            user=f"user_{i}",
            action=f"ACTION_{i}",
            entity_type="CASE",
            entity_id=f"CASE-00{i}",
            details=f"Legitimate details for block {i}"
        )

    # Initial chain must be valid
    assert verify_chain(db_session)["valid"] is True

    # Maliciously tamper with Block #1's details directly in SQL
    tampered_block = db_session.query(AuditLog).filter(AuditLog.block_index == 1).first()
    tampered_block.details = "MALICIOUSLY ALTERED DETAILS (EVIDENCE SUPPRESSION)"
    db_session.commit()

    # Verification MUST fail and point precisely to block #1
    tamper_result = verify_chain(db_session)
    assert tamper_result["valid"] is False
    assert tamper_result["total_blocks"] == 4
    assert tamper_result["broken_at_index"] == 1
    assert "Tamper detected at block #1" in tamper_result["details"]


def test_tamper_detection_on_broken_hash_link(db_session):
    """Asserts that altering a previous_hash link breaks the chain."""
    for i in range(3):
        create_audit_block(
            db=db_session,
            user="examiner",
            action=f"ACTION_{i}",
            entity_type="CSE",
            entity_id="CSE-001",
            details=f"Record {i}"
        )

    # Maliciously alter previous_hash on block 2
    block2 = db_session.query(AuditLog).filter(AuditLog.block_index == 2).first()
    block2.previous_hash = "f" * 64
    db_session.commit()

    tamper_result = verify_chain(db_session)
    assert tamper_result["valid"] is False
    assert tamper_result["broken_at_index"] == 2


def test_api_audit_chain_and_verify_endpoints():
    """Integration test for GET /api/audit/chain and GET /api/audit/verify."""
    client = TestClient(app)

    # Test chain retrieval
    res_chain = client.get("/api/audit/chain")
    assert res_chain.status_code == 200
    chain_data = res_chain.json()
    assert isinstance(chain_data, list)
    if len(chain_data) > 0:
        first_block = chain_data[0]
        assert "block_index" in first_block
        assert "previous_hash" in first_block
        assert "block_hash" in first_block
        assert "user" in first_block
        assert "action" in first_block

    # Test chain verification endpoint
    res_verify = client.get("/api/audit/verify")
    assert res_verify.status_code == 200
    verify_data = res_verify.json()
    assert "valid" in verify_data
    assert "total_blocks" in verify_data
    assert "broken_at_index" in verify_data
    assert "details" in verify_data
