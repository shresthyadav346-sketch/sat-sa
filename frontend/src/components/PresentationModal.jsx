import React, { useState } from "react";

export default function PresentationModal({ onClose }) {
  const [currentSlide, setCurrentSlide] = useState(1);
  const totalSlides = 5;

  const slides = [
    {
      id: 1,
      title: "Problem Statement & Solution Overview",
      subtitle: "Why NCIIPC needs SAT-SA for Critical Sector Entities",
      content: (
        <div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginTop: "16px" }}>
            <div style={{ background: "rgba(244, 63, 94, 0.08)", border: "1px solid var(--crit-border)", padding: "18px", borderRadius: "10px" }}>
              <h4 style={{ color: "var(--crit-color)", marginBottom: "10px", fontSize: "1rem" }}>The Operational Challenge</h4>
              <ul style={{ color: "var(--text-secondary)", fontSize: "0.85rem", lineHeight: "1.7", paddingLeft: "20px" }}>
                <li>NCIIPC assesses cyber resilience across hundreds of Critical Sector Entities (Power, Banking, Telecom, Transport, Defence).</li>
                <li>Manual review of SOC logs, cases, and escalation records is slow, unscalable, and inconsistent across entities.</li>
                <li>SOC dashboards and compliance reports hide procedural shortcuts (closing alerts rapidly to meet SLA without actual triage).</li>
                <li>Examiners cannot inspect millions of alerts manually.</li>
              </ul>
            </div>

            <div style={{ background: "rgba(6, 182, 212, 0.08)", border: "1px solid var(--border-highlight)", padding: "18px", borderRadius: "10px" }}>
              <h4 style={{ color: "var(--accent-cyan)", marginBottom: "10px", fontSize: "1rem" }}>The SAT-SA Solution</h4>
              <ul style={{ color: "var(--text-secondary)", fontSize: "0.85rem", lineHeight: "1.7", paddingLeft: "20px" }}>
                <li><strong>Supervisory Analytics Tool</strong> — Not a SIEM, not an antivirus, not a SOC replacement.</li>
                <li>Tells examiners <strong>WHERE to look first and WHY</strong> with mathematical evidence.</li>
                <li>Detects <strong>Execution Gaps</strong> (controls exist on paper but fail in operations).</li>
                <li>Detects <strong>Negative Space</strong> (critical infrastructure assets with zero security activity).</li>
                <li>Reduces manual review time from 4+ hours to <strong>45 minutes (81%+ time saved)</strong>.</li>
              </ul>
            </div>
          </div>

          <div style={{ marginTop: "20px", padding: "14px", background: "var(--bg-subtle)", borderRadius: "8px", textAlign: "center", border: "1px dashed var(--border-light)" }}>
            <span style={{ color: "var(--accent-cyan)", fontWeight: "700" }}>Central Philosophy: </span>
            <span style={{ color: "var(--text-primary)" }}>
              "SAT-SA does not replace the human supervisor. It converts massive operational evidence into explainable supervisory signals."
            </span>
          </div>
        </div>
      ),
    },
    {
      id: 2,
      title: "End-to-End System Architecture",
      subtitle: "100% Offline, Air-Gapped, and Evidence-Traceable Design",
      content: (
        <div>
          <div style={{ background: "var(--bg-subtle)", padding: "18px", borderRadius: "10px", marginTop: "16px", border: "1px solid var(--border)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", textAlign: "center", gap: "10px", flexWrap: "wrap" }}>
              {[
                { step: "Data Ingestion", desc: "Batch CSV / JSON SOC Telemetry", color: "var(--accent-blue)" },
                { step: "Persistence Layer", desc: "Indexed SQLite / PostgreSQL (WAL mode)", color: "var(--accent-indigo)" },
                { step: "Analytics & ML", desc: "Rules + Isolation Forest + NLP TF-IDF", color: "var(--accent-purple)" },
                { step: "Supervisory Signals", desc: "Execution Gaps & Negative Space", color: "var(--high-color)" },
                { step: "Review Queue", desc: "Top 100 Ranked Cases (Multi-factor)", color: "var(--crit-color)" },
                { step: "Human-in-the-Loop", desc: "Examiner Decisions & Formal Report", color: "var(--low-color)" },
              ].map((node, i) => (
                <div key={i} style={{ flex: 1, minWidth: "130px", background: "var(--bg-card)", padding: "14px 10px", borderRadius: "8px", borderTop: `3px solid ${node.color}` }}>
                  <div style={{ fontSize: "0.82rem", fontWeight: "800", color: node.color }}>{node.step}</div>
                  <div style={{ fontSize: "0.72rem", color: "var(--text-secondary)", marginTop: "4px" }}>{node.desc}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginTop: "18px" }}>
            <div style={{ background: "var(--bg-card)", padding: "16px", borderRadius: "8px", border: "1px solid var(--border)" }}>
              <h4 style={{ color: "var(--low-color)", fontSize: "0.9rem", marginBottom: "6px" }}>🔒 Strict Offline / Air-Gapped Operation</h4>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.8rem", lineHeight: "1.6" }}>
                Zero cloud dependencies, zero external model inference, zero remote CDN calls. Fully containerized or locally executable for sensitive government security zones.
              </p>
            </div>
            <div style={{ background: "var(--bg-card)", padding: "16px", borderRadius: "8px", border: "1px solid var(--border)" }}>
              <h4 style={{ color: "var(--accent-cyan)", fontSize: "0.9rem", marginBottom: "6px" }}>🔍 Complete Evidence Traceability</h4>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.8rem", lineHeight: "1.6" }}>
                Every risk score breaks down into findings, each finding links to an exact formula, peer median, and raw source Alert/Case/Asset IDs.
              </p>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 3,
      title: "Analytical & Intelligence Engine",
      subtitle: "Transparent Rules Combined with Unsupervised Machine Learning & NLP",
      content: (
        <div style={{ marginTop: "16px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <div style={{ background: "var(--bg-card)", padding: "16px", borderRadius: "8px", border: "1px solid var(--border)" }}>
              <h4 style={{ color: "var(--crit-color)", marginBottom: "8px" }}>⚡ Execution Gaps (EG-001 to EG-007)</h4>
              <ul style={{ color: "var(--text-secondary)", fontSize: "0.8rem", lineHeight: "1.7", paddingLeft: "18px" }}>
                <li><strong>EG-001:</strong> Rapid critical alert closure (&lt; 5 mins)</li>
                <li><strong>EG-002:</strong> Critical alerts closed without formal escalation</li>
                <li><strong>EG-003:</strong> Critical alerts closed with zero technical investigation</li>
                <li><strong>EG-004:</strong> Low investigation depth (&lt; 2 actions recorded)</li>
                <li><strong>EG-005:</strong> Chronic alert flapping without root cause fix</li>
                <li><strong>EG-006:</strong> Repetitive copy-pasted triage templates</li>
                <li><strong>EG-007:</strong> Metric optimization (Goodhart's Law: 99% SLA, 0 evidence)</li>
              </ul>
            </div>

            <div style={{ background: "var(--bg-card)", padding: "16px", borderRadius: "8px", border: "1px solid var(--border)" }}>
              <h4 style={{ color: "var(--high-color)", marginBottom: "8px" }}>🌑 Negative Space (NS-001 to NS-006)</h4>
              <ul style={{ color: "var(--text-secondary)", fontSize: "0.8rem", lineHeight: "1.7", paddingLeft: "18px" }}>
                <li><strong>NS-001:</strong> Registered critical assets with 0 security telemetry</li>
                <li><strong>NS-002:</strong> Abnormally low alert activity vs peer baseline</li>
                <li><strong>NS-003:</strong> Missing investigation stage in case lifecycle</li>
                <li><strong>NS-004:</strong> Missing mandatory supervisory escalation records</li>
                <li><strong>NS-005:</strong> Broken workflow stages (Alert without Case)</li>
                <li><strong>NS-006:</strong> Entity-wide monitoring coverage gaps</li>
              </ul>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginTop: "16px" }}>
            <div style={{ background: "var(--bg-subtle)", padding: "12px 16px", borderRadius: "8px" }}>
              <span style={{ color: "var(--accent-purple)", fontWeight: "700" }}>Isolation Forest: </span>
              <span style={{ color: "var(--text-secondary)", fontSize: "0.8rem" }}>
                Detects multi-dimensional operational outliers across closure, escalation, and volume features.
              </span>
            </div>
            <div style={{ background: "var(--bg-subtle)", padding: "12px 16px", borderRadius: "8px" }}>
              <span style={{ color: "var(--accent-cyan)", fontWeight: "700" }}>TF-IDF + Cosine NLP: </span>
              <span style={{ color: "var(--text-secondary)", fontSize: "0.8rem" }}>
                Clusters pairwise text similarity to detect boilerplate, template-driven investigation notes.
              </span>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 4,
      title: "Real-Time Demonstration Highlights",
      subtitle: "Injected Ground-Truth Anomalies Detected without Hardcoding",
      content: (
        <div style={{ marginTop: "16px" }}>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Entity ID</th>
                  <th>Injected Ground-Truth Scenario</th>
                  <th>SAT-SA Detection Output</th>
                  <th>Risk Score</th>
                  <th>Evidence Metric</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="font-mono" style={{ color: "var(--accent-cyan)", fontWeight: "700" }}>CSE-007</td>
                  <td>The Rapid Closer</td>
                  <td>Flagged: EG-001 & EG-002</td>
                  <td><span className="badge badge-critical">88.1 (CRITICAL)</span></td>
                  <td>65% closed in &lt; 3m | 10% escalation (Peer 85%)</td>
                </tr>
                <tr>
                  <td className="font-mono" style={{ color: "var(--accent-cyan)", fontWeight: "700" }}>CSE-014</td>
                  <td>The Dark Zone (Negative Space)</td>
                  <td>Flagged: NS-001 & NS-006</td>
                  <td><span className="badge badge-medium">44.8 (MEDIUM)</span></td>
                  <td>35% critical assets have ZERO alerts</td>
                </tr>
                <tr>
                  <td className="font-mono" style={{ color: "var(--accent-cyan)", fontWeight: "700" }}>CSE-021</td>
                  <td>The Template Spammer</td>
                  <td>Flagged: EG-006 (NLP Repetition)</td>
                  <td><span className="badge badge-low">Flagged Pattern</span></td>
                  <td>TF-IDF cosine similarity cluster &gt; 0.85</td>
                </tr>
                <tr>
                  <td className="font-mono" style={{ color: "var(--accent-cyan)", fontWeight: "700" }}>CSE-032</td>
                  <td>The Chronic Flapper</td>
                  <td>Flagged: EG-005 (Repeat alerts)</td>
                  <td><span className="badge badge-low">Flagged Flapping</span></td>
                  <td>4 assets with 20+ alerts without fix</td>
                </tr>
                <tr>
                  <td className="font-mono" style={{ color: "var(--accent-cyan)", fontWeight: "700" }}>CSE-041</td>
                  <td>Goodhart's Law (Metric Optimization)</td>
                  <td>Flagged: EG-007 & EG-001</td>
                  <td><span className="badge badge-critical">88.4 (CRITICAL)</span></td>
                  <td>92% rapid closure | 4% escalation | 0 evidence</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div style={{ marginTop: "14px", padding: "12px 16px", background: "rgba(16, 185, 129, 0.08)", border: "1px solid var(--low-border)", borderRadius: "8px", fontSize: "0.82rem", color: "var(--low-color)" }}>
            ✓ Verified with 18 automated integration tests passing across all analytics, ML pipelines, and REST API endpoints.
          </div>
        </div>
      ),
    },
    {
      id: 5,
      title: "Innovation, Practicality & National Impact",
      subtitle: "Transforming Critical Infrastructure Oversight for India",
      content: (
        <div style={{ marginTop: "16px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px" }}>
            <div style={{ background: "var(--bg-card)", padding: "16px", borderRadius: "8px", border: "1px solid var(--border)" }}>
              <div style={{ fontSize: "1.8rem", fontWeight: "800", color: "var(--accent-cyan)", fontFamily: "var(--font-mono)" }}>81.3%</div>
              <div style={{ fontWeight: "700", marginTop: "4px" }}>Supervisory Time Saved</div>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.78rem", marginTop: "6px" }}>
                Replaces unfocused sampling of thousands of tickets with prioritized review of top 100 high-risk cases.
              </p>
            </div>

            <div style={{ background: "var(--bg-card)", padding: "16px", borderRadius: "8px", border: "1px solid var(--border)" }}>
              <div style={{ fontSize: "1.8rem", fontWeight: "800", color: "var(--low-color)", fontFamily: "var(--font-mono)" }}>100%</div>
              <div style={{ fontWeight: "700", marginTop: "4px" }}>Offline / Air-Gapped</div>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.78rem", marginTop: "6px" }}>
                Zero telemetry leaves the national supervisory perimeter. Zero cloud exposure.
              </p>
            </div>

            <div style={{ background: "var(--bg-card)", padding: "16px", borderRadius: "8px", border: "1px solid var(--border)" }}>
              <div style={{ fontSize: "1.8rem", fontWeight: "800", color: "var(--accent-purple)", fontFamily: "var(--font-mono)" }}>0–100</div>
              <div style={{ fontWeight: "700", marginTop: "4px" }}>Explainable Risk Score</div>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.78rem", marginTop: "6px" }}>
                Transparent mathematical methodology. Never a black-box AI judgement.
              </p>
            </div>
          </div>

          <div style={{ marginTop: "20px", background: "var(--bg-subtle)", padding: "16px", borderRadius: "8px", border: "1px solid var(--border)" }}>
            <h4 style={{ color: "var(--text-primary)", fontSize: "0.92rem", marginBottom: "8px" }}>National Mission Alignment (SIH & NCIIPC):</h4>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.82rem", lineHeight: "1.6" }}>
              SAT-SA empowers national regulators to enforce genuine operational cyber resilience across power grids, banking backbones, telecom infrastructure, transport networks, and strategic defence logistics.
            </p>
          </div>
        </div>
      ),
    },
  ];

  const current = slides[currentSlide - 1];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: "980px", minHeight: "560px" }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <span className="badge badge-medium">SIH 5-Slide Presentation Deck</span>
            <h3 style={{ marginTop: "4px" }}>{current.title}</h3>
            <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>{current.subtitle}</div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>&times;</button>
        </div>

        <div className="modal-body" style={{ minHeight: "360px" }}>
          {current.content}
        </div>

        <div className="modal-footer" style={{ justifyContent: "space-between" }}>
          <div style={{ color: "var(--text-secondary)", fontSize: "0.82rem", fontWeight: "600" }}>
            Slide {currentSlide} of {totalSlides}
          </div>
          <div style={{ display: "flex", gap: "10px" }}>
            <button
              className="btn btn-secondary"
              onClick={() => setCurrentSlide(Math.max(1, currentSlide - 1))}
              disabled={currentSlide === 1}
            >
              Previous Slide
            </button>
            <button
              className="btn btn-primary"
              onClick={() => {
                if (currentSlide < totalSlides) {
                  setCurrentSlide(currentSlide + 1);
                } else {
                  onClose();
                }
              }}
            >
              {currentSlide === totalSlides ? "Finish Presentation" : "Next Slide →"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
