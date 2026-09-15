import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import RiskBadge from "../components/RiskBadge";
import WorkflowTimeline from "../components/WorkflowTimeline";

export default function CaseDetails({ caseId, onBack, onNavigateCSE }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [verdict, setVerdict] = useState("CONFIRMED_GAP");
  const [triageNotes, setTriageNotes] = useState("");
  const [triageSaved, setTriageSaved] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const loadCase = async () => {
    setLoading(true);
    try {
      const res = await api.getCaseDetail(caseId);
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCase();
  }, [caseId]);

  const handleTriageSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.triageCase(caseId, {
        verdict,
        notes: triageNotes,
        reviewer: "chief_supervisory_examiner"
      });
      setTriageSaved(true);
      await loadCase();
    } catch (err) {
      alert("Failed to submit triage: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: "center", padding: "80px 0" }}>
        <div style={{ fontSize: "1.3rem", color: "var(--accent-cyan)", fontWeight: "700" }}>Loading Forensic Inspection for {caseId}...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="page-container">
        <div className="card">Case {caseId} not found. <button className="btn btn-secondary" onClick={onBack}>Back</button></div>
      </div>
    );
  }

  const { alert, investigations, escalation, workflow_stages } = data;

  // Calculate closure duration
  let closureDurationMins = null;
  if (alert?.created_at && alert?.closed_at) {
    const start = new Date(alert.created_at);
    const end = new Date(alert.closed_at);
    closureDurationMins = ((end - start) / 60000).toFixed(1);
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <button className="btn btn-sm btn-secondary" onClick={onBack} style={{ marginBottom: "8px" }}>
            ← Back to Review Queue
          </button>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <span className="font-mono" style={{ fontSize: "1.4rem", fontWeight: "800", color: "var(--accent-cyan)" }}>
              {data.case_id}
            </span>
            <RiskBadge level={data.severity} />
            <span className="badge badge-medium" onClick={() => onNavigateCSE(data.cse_id)} style={{ cursor: "pointer" }}>
              Entity: {data.cse_id} ↗
            </span>
          </div>
          <p className="page-description">
            Assigned Analyst: <strong>{data.assigned_analyst || "Unassigned"}</strong> • Status: <strong>{data.status}</strong> • Reopens: <strong>{data.reopen_count}</strong>
          </p>
        </div>
      </div>

      {/* 6-Stage Visual Workflow Pipeline */}
      <div className="card" style={{ marginBottom: "20px" }}>
        <div className="card-title">
          <span>Lifecycle Workflow Audit (Stage-by-Stage Verification)</span>
          <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Policy Mandated SOC Progression</span>
        </div>
        <WorkflowTimeline stages={workflow_stages} />
      </div>

      {/* Why is this case prioritized? Box */}
      <div className="card" style={{ borderLeft: "4px solid var(--crit-color)", marginBottom: "20px" }}>
        <h3 style={{ fontSize: "1rem", color: "var(--crit-color)", marginBottom: "8px" }}>
          ⚠️ Why is this case prioritized for manual examination?
        </h3>
        <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "0.85rem", color: "var(--text-primary)" }}>
          {closureDurationMins && parseFloat(closureDurationMins) <= 5.0 && (
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ color: "var(--crit-color)", fontWeight: "800" }}>• Rapid Closure:</span>
              Closed in only <strong>{closureDurationMins} minutes</strong> from alert creation (Threshold: 5 mins). Indicates procedural auto-closure without thorough triage.
            </div>
          )}
          {data.severity === "CRITICAL" && !workflow_stages.escalation && (
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ color: "var(--crit-color)", fontWeight: "800" }}>• Missing Escalation:</span>
              Alert is marked <strong>CRITICAL</strong> but has zero escalation record to Tier-2 SOC, incident response, or national liaison.
            </div>
          )}
          {investigations.length === 0 && (
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ color: "var(--high-color)", fontWeight: "800" }}>• Zero Investigation:</span>
              No technical investigation steps (memory dump, process tree, or log analysis) recorded prior to case resolution.
            </div>
          )}
          {alert?.asset_criticality === "CRITICAL" && (
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ color: "var(--accent-cyan)", fontWeight: "800" }}>• High Consequence Asset:</span>
              Target system <strong>{alert.asset_id}</strong> is registered as a national CRITICAL infrastructure asset.
            </div>
          )}
        </div>
      </div>

      {/* Grid: Alert Details & Investigation Actions */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "24px" }}>
        {/* Alert Telemetry */}
        <div className="card">
          <div className="card-title">
            <span>Originating Security Alert</span>
            <span className="font-mono" style={{ fontSize: "0.75rem", color: "var(--accent-cyan)" }}>{alert?.alert_id}</span>
          </div>

          {alert ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "0.82rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Alert Category:</span>
                <span style={{ fontWeight: "700" }}>{alert.alert_category}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Target Asset:</span>
                <span className="font-mono" style={{ fontWeight: "700" }}>{alert.asset_id} ({alert.asset_criticality})</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Source IP → Dest IP:</span>
                <span className="font-mono">{alert.source_ip} → {alert.destination_ip}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Disposition:</span>
                <span className="badge badge-medium">{alert.disposition}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Created At:</span>
                <span className="font-mono">{new Date(alert.created_at).toLocaleString()}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Closed At:</span>
                <span className="font-mono">{new Date(alert.closed_at).toLocaleString()}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", background: "var(--bg-subtle)", padding: "8px 10px", borderRadius: "6px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Total Closure Duration:</span>
                <span className="font-mono" style={{ fontWeight: "800", color: parseFloat(closureDurationMins) <= 5.0 ? "var(--crit-color)" : "var(--low-color)" }}>
                  {closureDurationMins} minutes
                </span>
              </div>
            </div>
          ) : (
            <div style={{ color: "var(--text-muted)" }}>No alert record linked.</div>
          )}
        </div>

        {/* Escalation Stage */}
        <div className="card">
          <div className="card-title">
            <span>Escalation Protocol Verification</span>
            <span className="badge badge-medium">Stage 4</span>
          </div>

          {escalation && escalation.escalated ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "0.82rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Escalation Status:</span>
                <span className="badge badge-low">✓ Escalated</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Escalated To:</span>
                <span style={{ fontWeight: "700" }}>{escalation.escalated_to}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Escalated By:</span>
                <span className="font-mono">{escalation.escalated_by}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Reason:</span>
                <span>{escalation.escalation_reason}</span>
              </div>
            </div>
          ) : (
            <div style={{ background: "var(--crit-bg)", border: "1px solid var(--crit-border)", padding: "16px", borderRadius: "8px", textAlign: "center" }}>
              <div style={{ fontSize: "1.4rem", color: "var(--crit-color)" }}>⚠️</div>
              <div style={{ fontWeight: "800", color: "var(--crit-color)", marginTop: "4px" }}>
                MANDATORY SUPERVISORY ESCALATION OMITTED
              </div>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.78rem", marginTop: "6px" }}>
                This {data.severity} incident was marked as resolved without escalation to Tier-2 SOC, CISO team, or CERT-In liaison.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Investigation Records List */}
      <div className="card" style={{ marginBottom: "24px" }}>
        <div className="card-title">
          <span>Recorded Technical Investigation Actions ({investigations.length})</span>
          <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Stage 3 Forensic Triage</span>
        </div>

        {investigations.length === 0 ? (
          <div style={{ background: "rgba(244, 63, 94, 0.08)", border: "1px dashed var(--crit-border)", padding: "24px", borderRadius: "8px", textAlign: "center", color: "var(--crit-color)" }}>
            <strong>Negative Space Condition: Zero technical investigation actions recorded.</strong>
            <p style={{ fontSize: "0.78rem", color: "var(--text-secondary)", marginTop: "4px" }}>
              Case was transitioned directly from ingestion to closure without recording forensic steps.
            </p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {investigations.map((inv) => (
              <div key={inv.investigation_id} style={{ background: "var(--bg-subtle)", padding: "12px 16px", borderRadius: "8px", borderLeft: "3px solid var(--accent-cyan)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                  <span style={{ fontWeight: "700", fontSize: "0.85rem", color: "var(--accent-cyan)" }}>
                    {inv.action}
                  </span>
                  <span className="font-mono" style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                    {new Date(inv.timestamp).toLocaleString()} • Evidence count: {inv.evidence_count}
                  </span>
                </div>
                <p style={{ fontSize: "0.82rem", color: "var(--text-primary)", lineHeight: "1.5" }}>
                  {inv.description}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Examiner Triage Decision Card */}
      <div className="card" style={{ border: "1px solid var(--border-highlight)" }}>
        <div className="card-title">
          <span>Supervisory Examiner Case Triage Verdict</span>
          <span className="badge badge-medium">Human-in-the-Loop</span>
        </div>

        {triageSaved && (
          <div style={{ background: "rgba(16, 185, 129, 0.12)", border: "1px solid var(--low-border)", color: "var(--low-color)", padding: "10px 14px", borderRadius: "6px", marginBottom: "14px", fontSize: "0.82rem" }}>
            ✓ Triage verdict successfully committed to supervisory audit log.
          </div>
        )}

        <form onSubmit={handleTriageSubmit}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "16px" }}>
            <div className="form-group">
              <label className="form-label">Triage Verdict</label>
              <select
                className="form-select"
                value={verdict}
                onChange={(e) => setVerdict(e.target.value)}
              >
                <option value="CONFIRMED_GAP">Confirmed Execution Gap</option>
                <option value="BENIGN_OPERATIONAL">Benign Operational Context</option>
                <option value="FALSE_POSITIVE">False Positive Indicator</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Supervisory Notes & Findings Rationale</label>
              <input
                type="text"
                className="form-input"
                placeholder="Document examiner rationale for the audit record..."
                value={triageNotes}
                onChange={(e) => setTriageNotes(e.target.value)}
                required
              />
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "10px" }}>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? "Saving Verdict..." : "Commit Case Triage Decision"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
