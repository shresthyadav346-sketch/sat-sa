"""
SQLAlchemy models for Reproducibility, Dataset Versioning, and Model Tracking.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
from datetime import datetime
from backend.app.database import Base

class DatasetVersion(Base):
    __tablename__ = "dataset_versions"
    
    version_id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    total_records = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    model_id = Column(String(64), primary_key=True)
    model_type = Column(String(64), nullable=False)  # ISOLATION_FOREST, KMEANS_CLUSTERING, TFIDF_NLP
    version = Column(String(32), default="v1.0.0")
    trained_at = Column(DateTime, default=datetime.utcnow)
    parameters = Column(Text)  # JSON
    metrics = Column(Text)  # JSON
