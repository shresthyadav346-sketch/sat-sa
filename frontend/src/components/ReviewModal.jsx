import React, { useState } from "react";

export default function ReviewModal({ finding, onClose, onSave }) {
  const [action, setAction] = useState("ACCEPT");
  const [notes, setNotes] = useState("");
  const [reviewer, setReviewer] = useState("chief_supervisory_examiner");
  const [submitting, setSubmitting] = useState(false);

  if (!finding) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSave(finding.finding_id, { action, notes, reviewer });
      onClose();
    } catch (err) {
      alert("Failed to submit review: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: "600px" }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <span className="badge badge-medium">{finding.rule_code}</span>
            <h3 style={{ marginTop: "4px" }}>Human-in-the-Loop Review</h3>
          </div>
          <button className="modal-close-btn" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div style={{ marginBottom: "16px" }}>
              <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>Target Finding:</div>
              <div style={{ fontSize: "0.95rem", fontWeight: "700", color: "var(--text-primary)" }}>{finding.title}</div>
            </div>

            <div className="form-group">
              <label className="form-label">Supervisory Action Decision</label>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
                {[
                  { id: "ACCEPT", label: "Accept Finding", desc: "Confirmed execution gap or blindspot", color: "var(--crit-color)" },
                  { id: "REJECT", label: "Reject Finding", desc: "Operational evidence acceptable", color: "var(--text-muted)" },
                  { id: "FALSE_POSITIVE", label: "Mark False Positive", desc: "Benign architectural reason", color: "var(--med-color)" },
                  { id: "SEND_FOR_MANUAL_REVIEW", label: "Escalate for Audit", desc: "Mandate formal on-site audit", color: "var(--accent-cyan)" },
                ].map((opt) => (
                  <label
                    key={opt.id}
                    style={{
                      display: "block",
                      background: action === opt.id ? "rgba(6, 182, 212, 0.12)" : "var(--bg-subtle)",
                      border: `1px solid ${action === opt.id ? "var(--accent-cyan)" : "var(--border)"}`,
                      padding: "10px 12px",
                      borderRadius: "8px",
                      cursor: "pointer",
                      transition: "all 0.15s ease",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <input
                        type="radio"
                        name="review_action"
                        value={opt.id}
                        checked={action === opt.id}
                        onChange={(e) => setAction(e.target.value)}
                      />
                      <span style={{ fontWeight: "700", fontSize: "0.82rem", color: opt.color }}>{opt.label}</span>
                    </div>
                    <div style={{ fontSize: "0.7rem", color: "var(--text-secondary)", marginTop: "4px", paddingLeft: "20px" }}>
                      {opt.desc}
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Supervisory Justification & Audit Notes</label>
              <textarea
                className="form-textarea"
                rows="4"
                placeholder="Enter justification, evidence review rationale, or directives for entity..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Examiner Credentials / Signature</label>
              <input
                type="text"
                className="form-input"
                value={reviewer}
                onChange={(e) => setReviewer(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={submitting}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? "Recording Audit..." : "Commit Decision to Audit Trail"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
