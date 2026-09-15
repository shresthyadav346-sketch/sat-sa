"""
SAT-SA: Supervisory Analytics Tool for SOC Assessment
Database Session and Engine Management
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.config import settings

# Configure engine
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

# SQLite optimization listeners for fast bulk writes & concurrency
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency for obtaining database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all database tables and ensure audit blockchain schema is initialized."""
    import backend.app.models  # Ensure all models are registered
    Base.metadata.create_all(bind=engine)

    # Auto-migration for SQLite if existing database lacks new blockchain columns
    if settings.DATABASE_URL.startswith("sqlite"):
        with engine.connect() as conn:
            from sqlalchemy import text
            res = conn.execute(text("PRAGMA table_info(audit_logs)")).fetchall()
            cols = {row[1] for row in res}
            if cols and "block_index" not in cols:
                conn.execute(text("ALTER TABLE audit_logs ADD COLUMN block_index INTEGER DEFAULT 0"))
                conn.execute(text("ALTER TABLE audit_logs ADD COLUMN previous_hash VARCHAR(64) DEFAULT '0000000000000000000000000000000000000000000000000000000000000000'"))
                conn.execute(text("ALTER TABLE audit_logs ADD COLUMN block_hash VARCHAR(64) DEFAULT ''"))
                conn.execute(text("ALTER TABLE audit_logs ADD COLUMN nonce INTEGER DEFAULT 0"))
                conn.commit()

