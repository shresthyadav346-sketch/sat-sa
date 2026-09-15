"""
Unit tests for SAT-SA Execution Gaps and Negative Space analytical rules.
"""

import pytest
from backend.app.database import SessionLocal
from backend.app.models.finding import Finding, RiskScore
from backend.app.models.review import ReviewQueueItem

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_critical_rapid_closure_detected(db):
    """Verify EG-001 (Rapid Critical Closure) correctly flagged for CSE-007."""
    finding = db.query(Finding).filter(Finding.cse_id == "CSE-007", Finding.rule_code == "EG-001").first()
    assert finding is not None
    assert finding.severity in ["CRITICAL", "HIGH"]
    assert finding.metric_value > 15.0

def test_missing_escalation_detected(db):
    """Verify EG-002 / NS-004 (Missing Escalation) correctly flagged for CSE-007 and CSE-041."""
    findings = db.query(Finding).filter(Finding.rule_code.in_(["EG-002", "NS-004"])).all()
    assert len(findings) > 0
    flagged_cses = {f.cse_id for f in findings}
    assert "CSE-007" in flagged_cses or "CSE-041" in flagged_cses

def test_negative_space_silent_assets_detected(db):
    """Verify NS-001 (Critical Asset Zero Activity) correctly identifies blindspots in CSE-014."""
    finding = db.query(Finding).filter(Finding.cse_id == "CSE-014", Finding.rule_code == "NS-001").first()
    assert finding is not None
    assert finding.metric_value >= 1.0

def test_repetitive_investigations_detected(db):
    """Verify EG-006 (Template Spammer / Repetitive Investigations) flags template-heavy entities."""
    findings = db.query(Finding).filter(Finding.rule_code == "EG-006").all()
    assert len(findings) > 0

def test_supervisory_risk_score_hierarchy(db):
    """Verify ground truth anomalies (CSE-007, CSE-041) receive higher risk scores than baseline entities."""
    top_cse = db.query(RiskScore).order_by(RiskScore.overall_score.desc()).first()
    assert top_cse.cse_id in ["CSE-007", "CSE-041"]
    assert top_cse.overall_score >= 80.0
    assert top_cse.risk_level == "CRITICAL"

def test_priority_review_queue_ordering(db):
    """Verify priority review queue contains 100 items ordered by priority score descending."""
    items = db.query(ReviewQueueItem).order_by(ReviewQueueItem.priority_score.desc()).all()
    assert len(items) == 100
    assert items[0].priority_score >= items[-1].priority_score
    # Top cases should be critical severity or have execution gap indicators
    assert items[0].priority_score >= 60.0
