"""
Integration tests for FastAPI supervisory endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["offline_mode"] is True

def test_dashboard_summary_endpoint(client):
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["kpis"]["cses_assessed"] >= 35
    assert data["kpis"]["alerts_analysed"] > 10000
    assert len(data["top_cses_requiring_attention"]) > 0

def test_cses_list_and_detail(client):
    res = client.get("/api/cses")
    assert res.status_code == 200
    cses = res.json()
    assert len(cses) >= 35
    
    # Detail check
    top_cse_id = cses[0]["cse_id"]
    res_detail = client.get(f"/api/cses/{top_cse_id}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert "metrics" in detail
    assert "deviations" in detail

def test_review_queue_endpoint(client):
    res = client.get("/api/review-queue?limit=10")
    assert res.status_code == 200
    queue = res.json()
    assert len(queue) == 10
    
    # Case detail inspection
    case_id = queue[0]["case_id"]
    res_case = client.get(f"/api/cases/{case_id}")
    assert res_case.status_code == 200
    case_detail = res_case.json()
    assert "workflow_stages" in case_detail
    assert "alert" in case_detail

def test_negative_space_endpoint(client):
    res = client.get("/api/negative-space")
    assert res.status_code == 200
    data = res.json()
    assert "total_critical_assets" in data
    assert "silent_critical_assets_count" in data

def test_peer_comparison_endpoint(client):
    res = client.get("/api/peer-comparison?cse_ids=CSE-007,CSE-014")
    assert res.status_code == 200
    data = res.json()
    assert len(data["entities"]) == 2
    assert "peer_benchmarks" in data

def test_human_in_the_loop_review(client):
    # Fetch a finding
    findings_res = client.get("/api/findings?limit=1")
    assert findings_res.status_code == 200
    findings = findings_res.json()
    if findings:
        f_id = findings[0]["finding_id"]
        review_res = client.post(
            f"/api/findings/{f_id}/review",
            json={
                "action": "ACCEPT",
                "notes": "Verified by supervisory review committee during assessment cycle.",
                "reviewer": "chief_examiner_sih"
            }
        )
        assert review_res.status_code == 200
        assert review_res.json()["status"] == "ACCEPTED"

def test_report_generation(client):
    res = client.post(
        "/api/reports/generate",
        json={
            "title": "National SOC Supervisory Examination Summary",
            "assessment_cycle": "SIH-2026 Evaluation",
            "examiner_name": "NCIIPC Supervisory Board"
        }
    )
    assert res.status_code == 200
    report = res.json()
    assert "report_id" in report
    assert len(report["cse_risk_rankings"]) > 0
    assert len(report["major_findings"]) > 0

def test_audit_log_endpoint(client):
    res = client.get("/api/audit-log")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0
