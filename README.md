# SAT-SA: Supervisory Analytics Tool for SOC Assessment

### Smart India Hackathon (SIH) Prototype
**National Critical Information Infrastructure Protection Centre (NCIIPC)**

> **"SAT-SA does not replace expert supervisory judgement. It converts large volumes of SOC operational evidence into explainable supervisory signals, allowing examiners to focus their limited manual-review effort on the cases, entities, and processes most deserving of attention."**

---

## 1. Executive Overview

The **National Critical Information Infrastructure Protection Centre (NCIIPC)** assesses the cyber resilience of **Critical Sector Entities (CSEs)** across Power, Banking, Telecom, Transport, and Defence.

Manual supervisory reviews of SOC alerts and case-management workflows are time-consuming, resource-intensive, and fail to scale across millions of operational records. Moreover, compliance dashboards often hide operational weaknesses—such as closing critical alerts rapidly to meet SLA compliance without technical triage.

**SAT-SA (Supervisory Analytics Tool for SOC Assessment)** is an offline-capable, evidence-backed decision-support system that:
1. Prioritizes entities requiring immediate supervisory attention via an explainable 0–100 Risk Score.
2. Identifies **Execution Gaps** (controls that exist in procedure but fail in execution).
3. Detects **Negative Space conditions** (unmonitored or silent critical infrastructure systems).
4. Ranks the **Top 100 cases** requiring manual examiner triage in a Priority Review Queue.
5. Provides full mathematical and record-level **evidence traceability** for every finding.
6. Enforces **Human-in-the-Loop** governance and generates formal supervisory assessment reports.

---

## 2. Injected Ground-Truth Validation Anomalies

SAT-SA detects operational weaknesses without hardcoding entity IDs:

| Entity | Real-World Anomaly Pattern | Ground-Truth Injected Characteristics | SAT-SA Detection Output |
| :--- | :--- | :--- | :--- |
| **CSE-007** | **The Rapid Closer** | 65% of critical alerts closed in < 3m; critical escalation compliance only 10% (Peer baseline: 85%). | **Flagged EG-001 & EG-002** (Score: 88.1 / 100 CRITICAL) |
| **CSE-014** | **The Dark Zone (Negative Space)** | 135 total assets; 35% of registered CRITICAL assets have **ZERO** alerts over 90 days. | **Flagged NS-001 & NS-006** (Score: 44.8 / 100 MEDIUM) |
| **CSE-021** | **The Template Spammer** | 80% of investigation notes are word-for-word copy-pasted checklist templates. | **Flagged EG-006** (NLP Cosine Similarity Cluster > 0.85) |
| **CSE-032** | **The Chronic Flapper** | 4 critical database assets generate 20+ repeat alerts without systemic root cause fix. | **Flagged EG-005** (Chronic Alert Flapping) |
| **CSE-041** | **Goodhart's Law (Metric Optimization)** | 99.8% SLA adherence (< 3 min closure), but 0 technical evidence and 4% escalation. | **Flagged EG-007 & EG-001** (Score: 88.4 / 100 CRITICAL) |

---

## 3. Core Analytical Capabilities

### Execution Gaps (EG-001 to EG-007)
* **EG-001 Rapid Critical Closure**: High/critical alerts closed in &le; 5 minutes (or &lt; 10th percentile of peer baseline).
* **EG-002 Critical Alert Without Escalation**: Severity = CRITICAL without corresponding supervisory escalation record.
* **EG-003 Critical Alert Without Investigation**: Case ticket closed with zero technical investigation records.
* **EG-004 Low Investigation Depth**: Incidents closed with &le; 1 technical investigation action.
* **EG-005 Repeated Alerts Without Remediation**: Same asset generating &ge; 5 alerts in 14 days without root cause fix.
* **EG-006 Repetitive Investigations**: Local NLP (TF-IDF + Cosine Similarity) detects copy-pasted triage notes.
* **EG-007 KPI vs Operational Effectiveness**: Divergence detection where SLA compliance is 95%+ but investigation depth is bottom 5%.

### Negative Space (NS-001 to NS-006)
* **NS-001 Critical Asset With Zero Activity**: Registered CRITICAL asset with zero security alerts over 90 days.
* **NS-002 Critical Asset With Very Low Activity**: Activity &lt; 15% of peer median asset baseline.
* **NS-003 Missing Investigation**: Case ticket transitioned directly from ingestion to closure.
* **NS-004 Missing Mandatory Escalation**: Critical incident missing required regulatory escalation.
* **NS-005 Missing Workflow Stage**: Broken lifecycle audit trail (Alert &rarr; Case &rarr; Investigation &rarr; Escalation &rarr; Resolution &rarr; Closure).
* **NS-006 Broad Monitoring Coverage Gap**: Entity-wide asset telemetry coverage &lt; 75%.

### Machine Learning & Offline NLP
* **Isolation Forest Anomaly Detector**: Unsupervised operational outlier scoring (0–100) trained on multi-dimensional volume, escalation, closure, and coverage features.
* **K-Means Operational Peer Clustering**: Groups entities into 3 operational scale tiers (Tier 1: High-Volume Strategic, Tier 2: Medium-Scale, Tier 3: Specialized).
* **TF-IDF + Pairwise Cosine Similarity**: Fast offline text clustering to identify boilerplate triage checklists.

---

## 4. Technology Stack

* **Backend**: Python 3.11+ / 3.14, FastAPI, Pydantic v2, SQLAlchemy 2.0.
* **Database**: SQLite (WAL mode, foreign keys, and indexes) by default for **zero-dependency instant execution**, configurable to PostgreSQL.
* **Data Science & ML**: Scikit-learn, Pandas, NumPy, SciPy (100% offline, zero cloud calls).
* **Frontend**: React, Vite, Vanilla Modern CSS Design System (Dark Cyber Defense theme).
* **Testing**: Pytest, Starlette/FastAPI TestClient, HTTPX (18 automated tests passing).
* **Deployment**: Windows Batch scripts (`run_all.bat`), Docker, and Docker Compose.

---

## 5. Quick Start Instructions (Local Execution)

### Prerequisites
* Python 3.10+ installed
* Node.js v18+ and npm installed

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Synthetic Telemetry & Run Analysis Pipeline
```bash
# Generates 45 CSEs, ~36,000 alerts, ~20,000 cases, and executes analytical rules
python -m data_generator.generator
python -m backend.app.services.analysis_runner
```

### 3. Run Automated Test Suite
```bash
pytest tests/ -v
```

### 4. Launch Backend & Frontend
#### Option A: One-Click Launch (Windows)
Double click `deployment/run_all.bat` or run in terminal:
```cmd
deployment\run_all.bat
```

#### Option B: Individual Launch
```bash
# Terminal 1: Backend
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Visit the platform in your browser at:
👉 **`http://localhost:5173`** (or `http://localhost:8000` for production build)

---

## 6. Docker & Air-Gapped Deployment

For air-gapped evaluation environments, SAT-SA is fully containerized:

```bash
docker compose -f deployment/docker-compose.yml up --build
```
Access the application at `http://localhost:8000`.

---

## 7. Key REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health status and offline mode confirmation |
| `GET` | `/api/dashboard/summary` | Executive summary metrics, risk distribution, high-risk entities |
| `GET` | `/api/trends` | Multi-period operational trend points and deterioration signals |
| `GET` | `/api/cses` | List all entities ranked by supervisory risk score |
| `GET` | `/api/cses/{id}` | In-depth entity profile, radar metrics, peer deviations, cluster |
| `GET` | `/api/review-queue` | Top 100 cases prioritized for manual examiner review |
| `GET` | `/api/cases/{id}` | 6-stage lifecycle forensic inspection and missing stage auditor |
| `POST`| `/api/cases/{id}/triage` | Examiner case triage decision commit |
| `GET` | `/api/negative-space` | Silent critical assets and monitoring blindspots |
| `GET` | `/api/peer-comparison` | Side-by-side benchmarking of entities vs peer medians |
| `GET` | `/api/findings` | Central repository of all algorithmic findings |
| `POST`| `/api/findings/{id}/review` | Human-in-the-loop decision (Accept, Reject, False Positive) |
| `GET` | `/api/audit-log` | Immutable supervisory action and governance trail |
| `POST`| `/api/reports/generate` | Generates full formal NCIIPC supervisory assessment report |
| `POST`| `/api/datasets/reanalyze` | Triggers full algorithmic re-analysis pipeline |

---

## 8. Smart India Hackathon Presentation Resources

1. **5-Slide Presentation Deck**: Available inside the running app via the **"📽 5 Slides"** button, or documented in [`docs/SIH_PRESENTATION_5_SLIDES.md`](docs/SIH_PRESENTATION_5_SLIDES.md).
2. **2-Minute Live Pitch Script**: Available inside the app via the **"⏱ 2-Min Demo"** button, or documented in [`docs/TWO_MINUTE_DEMO_SCRIPT.md`](docs/TWO_MINUTE_DEMO_SCRIPT.md).
3. **Sample Exported Data**: Standalone CSV summaries available in `sample_data/`.
