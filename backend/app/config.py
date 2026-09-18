"""
SAT-SA: Supervisory Analytics Tool for SOC Assessment
Configuration and Thresholds
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# In Vercel serverless environment, filesystem is read-only, so clone database to /tmp
if os.environ.get("VERCEL"):
    tmp_db = "/tmp/sat_sa.db"
    seed_db = os.path.join(BASE_DIR, "sat_sa.db")
    if not os.path.exists(tmp_db) and os.path.exists(seed_db):
        import shutil
        try:
            shutil.copy2(seed_db, tmp_db)
        except Exception:
            pass
    DEFAULT_DB_URL = f"sqlite:///{tmp_db}"
else:
    DEFAULT_DB_PATH = os.path.join(BASE_DIR, "sat_sa.db").replace("\\", "/")
    DEFAULT_DB_URL = f"sqlite:///{DEFAULT_DB_PATH}"

class Settings(BaseSettings):
    APP_NAME: str = "SAT-SA: Supervisory Analytics Tool for SOC Assessment"
    APP_VERSION: str = "1.0.0-SIH"
    NCIIPC_BANNER: str = "DEMONSTRATION DATA — SYNTHETIC DATA"
    DEBUG: bool = True
    
    # Database configuration (SQLite by default for 100% offline zero-config operation)
    DATABASE_URL: str = Field(
        default=DEFAULT_DB_URL,
        description="SQLAlchemy database connection string. Can be swapped to PostgreSQL."
    )
    
    # Operational Thresholds (Configurable)
    RAPID_CLOSURE_THRESHOLD_MINUTES: float = 5.0  # Alert closed in <= 5 mins is rapid
    CRITICAL_ESCALATION_WINDOW_HOURS: float = 2.0  # Critical alert expected escalation
    REPEAT_ALERT_WINDOW_DAYS: int = 14            # Window for flapping asset detection
    REPEAT_ALERT_THRESHOLD_COUNT: int = 5         # Repeat alerts on same asset to flag
    MIN_INVESTIGATION_ACTIONS: int = 2            # High/Crit cases need >= 2 actions
    TFIDF_SIMILARITY_THRESHOLD: float = 0.85      # Cosine similarity for template investigations
    LOW_ACTIVITY_ASSET_RATIO: float = 0.15        # < 15% of peer median asset alert volume
    
    # Supervisory Risk Scoring Weights (Must sum to 1.0)
    WEIGHT_EXECUTION_GAP: float = 0.25
    WEIGHT_NEGATIVE_SPACE: float = 0.20
    WEIGHT_INVESTIGATION: float = 0.15
    WEIGHT_ESCALATION: float = 0.15
    WEIGHT_ANOMALY: float = 0.15
    WEIGHT_PEER_DEVIATION: float = 0.10
    
    # Risk Level Boundaries
    RISK_LOW_MAX: float = 30.0
    RISK_MEDIUM_MAX: float = 60.0
    RISK_HIGH_MAX: float = 80.0
    
    # Priority Review Queue
    TOP_REVIEW_QUEUE_LIMIT: int = 100
    
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
