# SAT-SA: 2-Minute Live SIH Demonstration Script

Use this script during the live Smart India Hackathon jury evaluation.

---

### [0:00 – 0:15] Problem Statement & Context
* **Presenter speaks**:
  > "Good morning, respected judges. The National Critical Information Infrastructure Protection Centre (NCIIPC) assesses the cyber resilience of critical entities across Power, Banking, Telecom, Transport, and Defence.
  > Today, supervisors manually review sample SOC tickets—a slow, inconsistent process that misses procedural shortcuts like closing alerts in seconds to meet SLA targets.
  > Our solution is **SAT-SA: Supervisory Analytics Tool for SOC Assessment**."
* **Screen**: Executive Dashboard (`http://localhost:5173`). Highlight the `DEMONSTRATION DATA — SYNTHETIC DATA` banner and `100% OFFLINE` indicator.

---

### [0:15 – 0:30] Data Ingestion & Offline Architecture
* **Presenter speaks**:
  > "SAT-SA is completely offline and air-gapped. Notice our dataset: 45 Critical Sector Entities, over 36,000 alerts, and 20,000 cases across 3 months.
  > We do not replace the SOC or the human examiner. SAT-SA converts massive operational evidence into explainable supervisory signals."
* **Action**: Point out the KPI grid: 45 Entities Assessed, 36,160 Alerts, 105 Execution Gaps, and 81.3% Time Saved.

---

### [0:30 – 0:50] Entity Risk Ranking: Identifying Who Needs Attention First
* **Presenter speaks**:
  > "Rather than sampling tickets blindly, SAT-SA calculates an explainable 0–100 Supervisory Risk Score.
  > Looking at the CSE Ranking page, the system immediately prioritizes entities with systemic operational failures.
  > In top positions, we see **CSE-041** and **CSE-007** in CRITICAL status, and **CSE-014** with severe monitoring blindspots."
* **Action**: Click **CSE Ranking** in the navbar. Point out the color-coded score bars and primary concerns.

---

### [0:50 – 1:10] Execution Gaps: Deep-Dive into CSE-007
* **Presenter speaks**:
  > "Let's examine CSE-007. The system doesn't just say 'score 88'; it proves WHY:
  > First, **65% of critical alerts were closed in under 3 minutes** (Rule EG-001).
  > Second, **critical escalation compliance is only 10%**, compared to the peer median of 85% (Rule EG-002).
  > Every finding links directly to raw source Alert and Case IDs for complete audit traceability."
* **Action**: Click into **CSE-007**. Show the 6-component score breakdown, the 'Why Flagged' cards, and click **Inspect Evidence** to display sample record IDs.

---

### [1:10 – 1:30] Negative Space: Spotting CSE-014's Telemetry Blindspot
* **Presenter speaks**:
  > "Now let's examine Negative Space—detecting the absence of evidence.
  > Standard SOC dashboards show green lights for CSE-014 because no alerts are firing.
  > But SAT-SA correlates the asset inventory against ingested telemetry: **35% of its registered critical banking switches have generated ZERO alerts in 90 days**. We have immediately uncovered a critical telemetry blindspot."
* **Action**: Click **Negative Space** in the navbar. Click on CSE-014 to reveal the silent critical assets table.

---

### [1:30 – 1:45] Priority Review Queue: Triaging the Top 100 Cases
* **Presenter speaks**:
  > "Out of 20,000 cases, SAT-SA ranks the Top 100 cases requiring manual review.
  > Let's open Case CAS-CSE-007-00001. Our workflow pipeline visually demonstrates: Alert present, Case created, Investigation present, but **MANDATORY SUPERVISORY ESCALATION OMITTED**.
  > The examiner can confirm the operational gap in one click."
* **Action**: Click **Review Queue**, select the top case, show the 6-stage lifecycle visual pipeline with the glowing red cross on Escalation.

---

### [1:45 – 1:55] Human-in-the-Loop & Formal Report Generation
* **Presenter speaks**:
  > "SAT-SA keeps the human supervisor in full command. Examiners accept, reject, or mark false positives, with every action committed to an immutable audit trail.
  > In one click, we generate an official NCIIPC Supervisory Assessment Report complete with executive rankings and formal regulatory directives."
* **Action**: Click **Supervisory Report**, scroll to show the formal report layout, and click **Print / Save as PDF**.

---

### [1:55 – 2:00] Conclusion & Core Impact
* **Presenter speaks**:
  > "In summary: SAT-SA reduces manual review effort by 81%.
  > It does not replace the human supervisor—**it tells the supervisor WHERE to look first and WHY with mathematical proof.**
  > Thank you, and we are ready for your questions."
