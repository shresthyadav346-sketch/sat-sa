"""
Migration script to backfill existing AuditLog rows with valid blockchain hashes and block indexes.
"""

import sqlite3
from backend.app.config import settings
from backend.app.services.blockchain_audit import compute_block_hash, GENESIS_PREVIOUS_HASH

def migrate_audit_logs():
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cols = [c[1] for c in cur.execute("PRAGMA table_info(audit_logs)").fetchall()]
    if "block_index" not in cols:
        cur.execute("ALTER TABLE audit_logs ADD COLUMN block_index INTEGER DEFAULT 0")
        cur.execute(f"ALTER TABLE audit_logs ADD COLUMN previous_hash VARCHAR(64) DEFAULT '{GENESIS_PREVIOUS_HASH}'")
        cur.execute("ALTER TABLE audit_logs ADD COLUMN block_hash VARCHAR(64) DEFAULT ''")
        cur.execute("ALTER TABLE audit_logs ADD COLUMN nonce INTEGER DEFAULT 0")
        con.commit()

    rows = cur.execute(
        "SELECT log_id, timestamp, user, action, entity_type, entity_id, details, nonce FROM audit_logs ORDER BY log_id ASC"
    ).fetchall()

    prev_hash = GENESIS_PREVIOUS_HASH
    for idx, row in enumerate(rows):
        log_id, ts, user, action, ent_type, ent_id, details, nonce = row
        nonce = nonce or 0
        bh = compute_block_hash(idx, ts, user, action, ent_type, ent_id, details, prev_hash, nonce)
        cur.execute(
            "UPDATE audit_logs SET block_index=?, previous_hash=?, block_hash=?, nonce=? WHERE log_id=?",
            (idx, prev_hash, bh, nonce, log_id)
        )
        prev_hash = bh

    con.commit()
    con.close()
    print(f"[+] Migrated {len(rows)} audit log records into blockchain hash chain.")

if __name__ == "__main__":
    migrate_audit_logs()
