import React from "react";
import RiskBadge from "./RiskBadge";

export default function EvidenceModal({ finding, onClose, onOpenCase }) {
  if (!finding) return null;

  let sourceIds = [];
  try {
    if (finding.source_record_ids) {
      sourceIds = JSON.parse(finding.source_record_ids);
    }
  } catch (e) {
    sourceIds = [];
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
              <span className="badge badge-medium">{finding.rule_code}</span>
              <RiskBadge level={finding.severity} />
              <span style={{ fontSize: "0.74rem", color: "var(--text-muted)" }}>Confidence: {finding.confidence}</span>
            </div>
            <h3>{finding.title}</h3>
          </div>
          <button className="modal-close-btn" onClick={onClose}>&times;</button>
        </div>

        <div className="modal-body">
          <div className="form-group">
            <label className="form-label">Supervisory Finding Description</label>
            <p style={{ color: "var(--text-primary)", lineHeight: "1.6" }}>{finding.description}</p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px", margin: "16px 0" }}>
            <div style={{ background: "var(--bg-subtle)", padding: "12px", borderRadius: "8px" }}>
              <div style={{ fontSize: "0.7rem", color: "var(--text-secondary)", textTransform: "uppercase" }}>Entity Value</div>
              <div style={{ fontSize: "1.2rem", fontWeight: "800", color: "var(--crit-color)", fontFamily: "var(--font-mono)" }}>
                {finding.metric_value !== null ? finding.metric_value : "N/A"}
              </div>
            </div>

            <div style={{ background: "var(--bg-subtle)", padding: "12px", borderRadius: "8px" }}>
              <div style={{ fontSize: "0.7rem", color: "var(--text-secondary)", textTransform: "uppercase" }}>Peer Median</div>
              <div style={{ fontSize: "1.2rem", fontWeight: "800", color: "var(--accent-cyan)", fontFamily: "var(--font-mono)" }}>
                {finding.peer_median !== null ? finding.peer_median : "N/A"}
              </div>
            </div>

            <div style={{ background: "var(--bg-subtle)", padding: "12px", borderRadius: "8px" }}>
              <div style={{ fontSize: "0.7rem", color: "var(--text-secondary)", textTransform: "uppercase" }}>Threshold</div>
              <div style={{ fontSize: "1.2rem", fontWeight: "800", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                {finding.threshold_value !== null ? finding.threshold_value : "N/A"}
              </div>
            </div>
          </div>

          <div className="evidence-box">
            <div className="evidence-label">Mathematical & Operational Evidence</div>
            <div>{finding.evidence_summary}</div>
          </div>

          {sourceIds.length > 0 && (
            <div style={{ marginTop: "16px" }}>
              <label className="form-label">Traceable Source Records ({sourceIds.length} Sample Catalogued)</label>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", maxHeight: "140px", overflowY: "auto", padding: "8px 0" }}>
                {sourceIds.map((id) => (
                  <span
                    key={id}
                    className="badge badge-medium"
                    style={{ cursor: onOpenCase && id.startsWith("CAS-") ? "pointer" : "default" }}
                    onClick={() => onOpenCase && id.startsWith("CAS-") && onOpenCase(id)}
                    title={id.startsWith("CAS-") ? "Click to examine case workflow" : "Source record identifier"}
                  >
                    {id} {id.startsWith("CAS-") && "↗"}
                  </span>
                ))}
              </div>
            </div>
          )}

          {finding.supervisor_notes && (
            <div style={{ marginTop: "16px", background: "rgba(16, 185, 129, 0.08)", border: "1px solid var(--low-border)", padding: "12px", borderRadius: "8px" }}>
              <div style={{ fontSize: "0.72rem", color: "var(--low-color)", fontWeight: "700", textTransform: "uppercase" }}>
                Supervisor Decision Notes (Reviewed by {finding.reviewed_by || "Examiner"})
              </div>
              <div style={{ color: "var(--text-primary)", marginTop: "4px" }}>{finding.supervisor_notes}</div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
