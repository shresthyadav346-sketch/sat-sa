import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import RiskBadge from "../components/RiskBadge";

export default function ReviewQueue({ onSelectCase, initialCseFilter = "" }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cseFilter, setCseFilter] = useState(initialCseFilter);
  const [severityFilter, setSeverityFilter] = useState("");
  const [unreviewedOnly, setUnreviewedOnly] = useState(false);

  const loadQueue = async () => {
    setLoading(true);
    try {
      const params = { limit: 100 };
      if (cseFilter) params.cse_id = cseFilter;
      if (severityFilter) params.severity = severityFilter;
      if (unreviewedOnly) params.unreviewed_only = true;
      const res = await api.getReviewQueue(params);
      setItems(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, [cseFilter, severityFilter, unreviewedOnly]);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-title-group">
          <h2>Priority Review Queue — Top 100 High-Consequence Cases</h2>
          <p className="page-description">
            Multi-factor decision support queue ranking cases by severity, execution-gap indicators,
            negative-space conditions, and procedural breakdown. Tells examiners exactly which cases to review manually.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ marginBottom: "20px", padding: "14px 20px" }}>
        <div style={{ display: "flex", gap: "14px", alignItems: "center", flexWrap: "wrap" }}>
          <div style={{ width: "220px" }}>
            <input
              type="text"
              className="form-input"
              placeholder="Filter by CSE (e.g. CSE-007)..."
              value={cseFilter}
              onChange={(e) => setCseFilter(e.target.value)}
            />
          </div>

          <div style={{ width: "180px" }}>
            <select
              className="form-select"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <option value="">All Severities</option>
              <option value="CRITICAL">Critical Severity</option>
              <option value="HIGH">High Severity</option>
              <option value="MEDIUM">Medium Severity</option>
            </select>
          </div>

          <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "0.82rem", color: "var(--text-secondary)", cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={unreviewedOnly}
              onChange={(e) => setUnreviewedOnly(e.target.checked)}
            />
            Show Pending Triage Only
          </label>

          {(cseFilter || severityFilter || unreviewedOnly) && (
            <button
              className="btn btn-sm btn-secondary"
              onClick={() => {
                setCseFilter("");
                setSeverityFilter("");
                setUnreviewedOnly(false);
              }}
            >
              Reset Filters
            </button>
          )}

          <div style={{ marginLeft: "auto", fontSize: "0.8rem", color: "var(--text-secondary)" }}>
            Showing <strong>{items.length}</strong> prioritized cases
          </div>
        </div>
      </div>

      {/* Queue Table */}
      {loading ? (
        <div style={{ textAlign: "center", padding: "60px 0", color: "var(--text-secondary)" }}>
          Loading priority review cases...
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Priority Score</th>
                <th>Case ID</th>
                <th>Alert ID</th>
                <th>Entity</th>
                <th>Severity</th>
                <th>Asset Criticality</th>
                <th>Primary Supervisory Reason</th>
                <th>Workflow Integrity Status</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, idx) => (
                <tr key={item.queue_id}>
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <span className="font-mono" style={{ fontSize: "1rem", fontWeight: "900", color: item.priority_score >= 80 ? "var(--crit-color)" : (item.priority_score >= 60 ? "var(--high-color)" : "var(--accent-cyan)") }}>
                        {item.priority_score}
                      </span>
                      <div className="score-progress-bar" style={{ width: "45px" }}>
                        <div
                          className="score-fill"
                          style={{
                            width: `${item.priority_score}%`,
                            background: item.priority_score >= 80 ? "var(--crit-color)" : (item.priority_score >= 60 ? "var(--high-color)" : "var(--accent-cyan)")
                          }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="font-mono" style={{ fontWeight: "700", color: "var(--text-primary)" }}>
                    {item.case_id}
                  </td>
                  <td className="font-mono" style={{ color: "var(--text-secondary)", fontSize: "0.76rem" }}>
                    {item.alert_id}
                  </td>
                  <td className="font-mono" style={{ color: "var(--accent-cyan)", fontWeight: "700" }}>
                    {item.cse_id}
                  </td>
                  <td>
                    <RiskBadge level={item.severity} />
                  </td>
                  <td>
                    <span style={{ fontSize: "0.76rem", fontWeight: "700", color: item.asset_criticality === "CRITICAL" ? "var(--crit-color)" : "var(--text-secondary)" }}>
                      {item.asset_criticality}
                    </span>
                  </td>
                  <td style={{ maxWidth: "260px", fontWeight: "600", fontSize: "0.8rem", color: "var(--text-primary)" }}>
                    {item.primary_reason}
                  </td>
                  <td>
                    <span
                      className={`badge ${item.workflow_integrity_status === "Complete" ? "badge-low" : "badge-critical"}`}
                      style={{ fontSize: "0.68rem" }}
                    >
                      {item.workflow_integrity_status}
                    </span>
                  </td>
                  <td>
                    {item.reviewed ? (
                      <span className="badge badge-low">
                        ✓ {item.supervisor_verdict || "Triaged"}
                      </span>
                    ) : (
                      <span className="badge badge-medium" style={{ background: "rgba(234, 179, 8, 0.12)", color: "var(--med-color)" }}>
                        Pending Triage
                      </span>
                    )}
                  </td>
                  <td>
                    <button
                      className="btn btn-sm btn-primary"
                      onClick={() => onSelectCase(item.case_id)}
                    >
                      Examine Case →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
