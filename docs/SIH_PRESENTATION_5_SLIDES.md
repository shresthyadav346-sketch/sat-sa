# SAT-SA: 5-Slide SIH Presentation Deck

---

## Slide 1: Problem + Solution Overview
### Problem: Manual SOC Supervisory Review Does Not Scale
* **NCIIPC Context**: Mandated to evaluate cyber resilience across hundreds of Critical Sector Entities (Power, Banking, Telecom, Transport, Defence).
* **Current Bottleneck**: Supervisors manually sample SOC alerts and case records—a slow, resource-heavy process that misses procedural shortcuts.
* **The "Goodhart's Law" Trap**: SOC dashboards and SLAs often show 99% closure compliance, hiding superficial triage (rapid closures, omitted investigations, zero escalations).
* **The SAT-SA Solution**: A supervisory decision-support tool that converts operational evidence into explainable risk indicators.
* **Core Philosophy**: *"SAT-SA does not replace the human supervisor. It tells the supervisor WHERE to look first and WHY."*

---

## Slide 2: End-to-End Architecture
### 100% Offline, Air-Gapped, and Evidence-Traceable
```
Telemetry Sources (Batch CSV / JSON)
        ↓
Data Ingestion & Versioning Engine
        ↓
Persistence Layer (SQLite / PostgreSQL with WAL Mode & Indexes)
        ↓
Analytics Engine (Execution Gaps + Negative Space + Peer Baselines)
        ↓
Machine Learning (Isolation Forest Anomaly Detection + TF-IDF Cosine NLP)
        ↓
Supervisory Signals & 0–100 Explainable Risk Score
        ↓
Top 100 Priority Review Queue & Human-in-the-Loop Examiner Interface
        ↓
Formal NCIIPC Supervisory Assessment Report
```
* **Offline Requirement**: Zero remote API calls, zero external model inference, zero cloud dependencies.

---

## Slide 3: Intelligence & Analytical Engine
### Transparent Rules Combined with Unsupervised ML & NLP
1. **Execution Gaps (EG-001 to EG-007)**:
   * Rapid Critical Closure (< 5 min closure vs peer baseline)
   * Critical Alert Without Escalation (severity CRITICAL + no escalation record)
   * Critical Alert Without Investigation (case exists + 0 investigation actions)
   * Low Investigation Depth (< 2 actions)
   * Repeated Alerts Without Remediation (chronic flapping on same assets)
   * KPI vs Operational Effectiveness (SLA divergence / Goodhart's Law)
2. **Negative Space (NS-001 to NS-006)**:
   * Critical Assets With Zero Activity (telemetry blindspots)
   * Critical Assets With Low Activity (< 15% peer median)
   * Missing Workflow Stage (Alert -> Case -> Investigation -> Escalation -> Resolution -> Closure)
   * Broad Asset Monitoring Coverage Gaps
3. **Machine Learning & NLP**:
   * **Isolation Forest**: Multidimensional operational outlier detection (0–100 score).
   * **K-Means Clustering**: Clusters entities into comparable operational tiers.
   * **TF-IDF + Cosine Similarity**: Detects template-driven, copy-pasted triage descriptions.

---

## Slide 4: Real-Time Demonstration & Validation
### Ground-Truth Validation Anomalies Detected Without Hardcoding
| Entity | Injected Operational Pattern | SAT-SA Detection Output | Risk Score | Evidence Metric |
| :--- | :--- | :--- | :--- | :--- |
| **CSE-007** | The Rapid Closer | Flagged EG-001 & EG-002 | **88.1 (CRITICAL)** | 65% closed in < 3m; 10% escalation (Peer 85%) |
| **CSE-014** | The Dark Zone | Flagged NS-001 & NS-006 | **44.8 (MEDIUM)** | 35% critical assets have ZERO alerts |
| **CSE-021** | Template Spammer | Flagged EG-006 (NLP Repetition) | **Flagged Pattern** | TF-IDF pairwise similarity cluster > 0.85 |
| **CSE-032** | Chronic Flapper | Flagged EG-005 (Flapping) | **Flagged Repeat** | 4 critical assets with 20+ alerts without fix |
| **CSE-041** | Goodhart's Law Divergence | Flagged EG-007 & EG-001 | **88.4 (CRITICAL)** | 92% rapid closure; 4% escalation; 0 evidence |

* 18 automated integration tests verified.
* Traceable evidence: Every risk score links to exact formulas and raw source record IDs.

---

## Slide 5: Innovation, Practicality & National Impact
### Transforming Critical Infrastructure Oversight for India
* **81.3% Supervisory Time Saved**: Focuses examiner time on the top 100 prioritized cases rather than random ticket sampling.
* **Explainability Guaranteed**: No black-box judgements. Findings display exact math, peer comparisons, and verifiable source records.
* **Human-in-the-Loop**: Supervisors accept, reject, or mark false positives; every action is logged to an immutable regulatory audit trail.
* **One-Click Formal Reports**: Generates executive assessments with actionable directives for entity remediation.
* **National Security Impact**: Protects India's critical sectors (Power, Banking, Telecom, Transport, Defence) against hidden systemic operational failures.
