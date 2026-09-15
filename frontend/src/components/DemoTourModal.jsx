import React from "react";

export default function DemoTourModal({ onClose, onNavigate }) {
  const steps = [
    {
      time: "0:00 – 0:15",
      title: "1. Problem: Manual SOC Review Fails to Scale",
      script: "Good morning judges. NCIIPC assesses the cyber resilience of Critical Sector Entities. Today, supervisors manually review sample SOC tickets—a slow, inconsistent process that misses procedural shortcuts. SAT-SA solves this by converting operational evidence into explainable supervisory risk signals.",
      action: "Stay on Executive Dashboard",
      navTo: "dashboard"
    },
    {
      time: "0:15 – 0:30",
      title: "2. Architecture: 100% Offline & Evidence-Traceable",
      script: "Our solution is 100% offline and air-gapped. Everything runs locally on FastAPI, SQLite/PostgreSQL with indexed queries, Scikit-learn, and React. Notice the demonstration banner: all telemetry shown is synthetic data with injected ground-truth validation anomalies.",
      action: "Inspect KPI Summary & Offline Badges",
      navTo: "dashboard"
    },
    {
      time: "0:30 – 0:50",
      title: "3. CSE Risk Ranking: Identifying Who Needs Attention First",
      script: "Rather than inspecting 45 entities blindly, SAT-SA calculates an explainable 0 to 100 Supervisory Risk Score. Immediately, we see CSE-041 and CSE-007 flagged in CRITICAL status, and CSE-014 in MEDIUM status with specific operational concerns.",
      action: "Open CSE Ranking",
      navTo: "ranking"
    },
    {
      time: "0:50 – 1:10",
      title: "4. Execution Gaps: Investigating CSE-007",
      script: "Let's click into CSE-007. The system doesn't just give an 88 score; it tells the supervisor WHY: 65% of critical alerts were closed in under 3 minutes, and critical escalation rate is only 10% compared to the 85% peer median. Every finding links directly to raw source Alert and Case IDs.",
      action: "Examine CSE-007 Details",
      navTo: "cse-007"
    },
    {
      time: "1:10 – 1:30",
      title: "5. Negative Space: Spotting CSE-014's Blindspot",
      script: "Next, we open Negative Space. While CSE-014 shows good SLA metrics, SAT-SA detects that 35% of its registered critical assets have generated ZERO alerts in 90 days. We instantly uncover a critical telemetry blindspot that regular SOC dashboards hide.",
      action: "Open Negative Space Visualizer",
      navTo: "negative-space"
    },
    {
      time: "1:30 – 1:45",
      title: "6. Priority Review Queue: Triaging the Top 100 Cases",
      script: "Out of 20,000+ cases, SAT-SA ranks the Top 100 cases requiring manual review. Let's open Case CAS-CSE-007-00001. Our workflow pipeline visually shows: Alert present, Case created, Investigation present, but MANDATORY ESCALATION OMITTED. We can confirm the gap in one click.",
      action: "Open Review Queue",
      navTo: "review-queue"
    },
    {
      time: "1:45 – 1:55",
      title: "7. Human-in-the-Loop & Supervisory Report",
      script: "SAT-SA keeps the human in control. Examiners can accept, reject, or mark findings as false positives. In one click, we generate an official NCIIPC Supervisory Assessment Report with executive rankings, evidence breakdowns, and actionable directives.",
      action: "Open Supervisory Report",
      navTo: "reports"
    },
    {
      time: "1:55 – 2:00",
      title: "8. Summary & Impact",
      script: "SAT-SA saves 81% of manual review time. It does not replace the human supervisor—it tells the supervisor WHERE to look first and WHY with mathematical proof. Thank you!",
      action: "Complete Demo",
      navTo: "dashboard"
    }
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: "860px" }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <span className="badge badge-critical">Smart India Hackathon</span>
            <h3 style={{ marginTop: "4px" }}>2-Minute Live SIH Demonstration Guide</h3>
            <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
              Step-by-step timed presenter script and quick navigation shortcuts.
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>&times;</button>
        </div>

        <div className="modal-body" style={{ maxHeight: "480px" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            {steps.map((step, idx) => (
              <div
                key={idx}
                style={{
                  background: "var(--bg-subtle)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  padding: "14px 16px",
                  borderLeft: `4px solid ${idx % 2 === 0 ? "var(--accent-cyan)" : "var(--accent-blue)"}`
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                  <span style={{ fontWeight: "800", fontSize: "0.86rem", color: "var(--text-primary)" }}>
                    {step.title}
                  </span>
                  <span className="badge badge-medium" style={{ fontFamily: "var(--font-mono)" }}>
                    ⏱ {step.time}
                  </span>
                </div>
                <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: "1.6", fontStyle: "italic" }}>
                  "{step.script}"
                </p>
                <div style={{ marginTop: "8px", display: "flex", justifyContent: "flex-end" }}>
                  <button
                    className="btn btn-sm btn-secondary"
                    onClick={() => {
                      onNavigate(step.navTo);
                      onClose();
                    }}
                  >
                    Go to {step.action} →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-primary" onClick={onClose}>Close Demo Guide</button>
        </div>
      </div>
    </div>
  );
}
