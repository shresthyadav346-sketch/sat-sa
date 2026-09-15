"""
Unit tests for Offline Machine Learning and NLP pipelines.
"""

import pytest
from backend.app.database import SessionLocal
from analytics.metrics.calculator import calculate_all_cse_metrics
from ml.anomaly_detection.detector import OperationalAnomalyDetector
from ml.clustering.clusterer import PeerClusterer
from ml.nlp.repetition_analyzer import InvestigationRepetitionAnalyzer

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_isolation_forest_pipeline(db):
    """Verify Isolation Forest detector trains and assigns normalized 0-100 scores."""
    metrics_map = calculate_all_cse_metrics(db)
    detector = OperationalAnomalyDetector()
    scores = detector.fit_predict(metrics_map)
    
    assert len(scores) == len(metrics_map)
    for cse_id, score in scores.items():
        assert 0.0 <= score <= 100.0

def test_kmeans_peer_clustering(db):
    """Verify K-Means clusters CSEs into 3 operational tiers."""
    metrics_map = calculate_all_cse_metrics(db)
    clusterer = PeerClusterer(n_clusters=3)
    clusters = clusterer.cluster_cses(metrics_map)
    
    assert len(clusters) == len(metrics_map)
    cluster_ids = {c["cluster_id"] for c in clusters.values()}
    assert len(cluster_ids) == 3

def test_nlp_repetition_analyzer(db):
    """Verify TF-IDF Cosine similarity detector outputs valid repetition score."""
    analyzer = InvestigationRepetitionAnalyzer()
    res = analyzer.analyze_cse_investigations(db, "CSE-021")
    
    assert "repetition_score" in res
    assert 0.0 <= res["repetition_score"] <= 1.0
    assert "top_repetitive_texts" in res
    assert "sample_case_ids" in res
