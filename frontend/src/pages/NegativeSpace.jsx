import React, { useEffect, useState } from "react";
import { api } from "../services/api";

export default function NegativeSpace({ onSelectCSE }) {
  const [overview, setOverview] = useState(null);
  const [selectedCseId, setSelectedCseId] = useState("CSE-014");
  const [cseDetail, setCseDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadOverview = async () => {
    setLoading(true);
    try {
      const res = await api.getNegativeSpaceOverview();
      setOverview(res);
      if (res.entities && res.entities.length > 0) {
        // default to first or CSE-014
        const target = res.entities.find((e) => e.cse_id === "CSE-014") || res.entities[0];
        setSelectedCseId(target.cse_id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadCseNegativeSpace = async (cid) => {
    try {
      const res = await api.getCSENegativeSpace(cid);
      setCseDetail(res);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadOverview();
  }, []);

  useEffect(() => {
    if (selectedCseId) {
      loadCseNegativeSpace(selectedCseId);
    }
  }, [selectedCseId]);

  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: "center", padding: "80px 0" }}>
        <div style={{ fontSize: "1.3rem", color: "var(--accent-cyan)", fontWeight: "700" }}>Loading Negative Space Telemetry...</div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-title-group">
          <h2>Negative Space Analytics — Critical Infrastructure Blindspots</h2>
          <p className="page-description">
            Negative Space detects the <strong>absence of expected evidence</strong>.
            Identifies high-value critical systems with zero or near-zero security telemetry over 90 days.
          </p>
        </div>
      </div>

      {/* Summary Metrics */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px", marginBottom: "24px" }}>
        <div className="kpi-card">
          <div className="kpi-label">Registered Critical Assets</div>
          <div className="kpi-value">{overview?.total_critical_assets || 0}</div>
          <div className="kpi-sub">Across all critical sectors</div>
        </div>

        <div className="kpi-card kpi-critical">
          <div className="kpi-label">Silent Critical Assets (Zero Alerts)</div>
          <div className="kpi-value" style={{ color: "var(--crit-color)" }}>
            {overview?.silent_critical_assets_count || 0}
          </div>
          <div className="kpi-sub">Telemetry dead zones</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">Overall Critical Coverage</div>
          <div className="kpi-value" style={{ color: "var(--accent-cyan)" }}>
            {overview?.overall_critical_coverage_pct || 0}%
          </div>
          <div className="kpi-sub">Active monitored critical assets</div>
        </div>

        <div className="kpi-card kpi-warning">
          <div className="kpi-label">Affected Entities</div>
          <div className="kpi-value">{overview?.affected_entities_count || 0}</div>
          <div className="kpi-sub">Entities with telemetry blindspots</div>
        </div>
      </div>

      {/* Split Grid: Entity List & Deep-Dive Asset Breakdown */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.3fr", gap: "20px" }}>
        {/* Entity List */}
        <div className="card">
          <div className="card-title">
            <span>Entities with Monitoring Coverage Gaps</span>
            <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Ranked by Silent Asset Count</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "12px", maxHeight: "600px", overflowY: "auto" }}>
            {overview?.entities?.map((e) => (
              <div
                key={e.cse_id}
                onClick={() => setSelectedCseId(e.cse_id)}
                style={{
                  background: selectedCseId === e.cse_id ? "rgba(6, 182, 212, 0.12)" : "var(--bg-subtle)",
                  border: `1px solid ${selectedCseId === e.cse_id ? "var(--accent-cyan)" : "var(--border)"}`,
                  borderRadius: "8px",
                  padding: "14px 16px",
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span className="font-mono" style={{ fontWeight: "800", color: "var(--accent-cyan)" }}>
                    {e.cse_id}
                  </span>
                  <span className="badge badge-critical">
                    {e.silent_critical_assets_count} Silent Critical Assets
                  </span>
                </div>
                <div style={{ fontWeight: "600", fontSize: "0.85rem", marginTop: "4px" }}>
                  {e.name}
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.72rem", color: "var(--text-secondary)", marginTop: "6px" }}>
                  <span>Sector: {e.sector}</span>
                  <span>Critical Coverage: <strong>{e.critical_coverage_pct}%</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Selected Entity Visualizer */}
        <div className="card">
          <div className="card-title">
            <div>
              <span>Entity Deep-Dive: {selectedCseId}</span>
              <div style={{ fontSize: "0.72rem", color: "var(--text-secondary)", marginTop: "2px" }}>
                Critical Asset Telemetry Activity Breakdown
              </div>
            </div>
            <button className="btn btn-sm btn-secondary" onClick={() => onSelectCSE(selectedCseId)}>
              View Full Profile →
            </button>
          </div>

          {cseDetail ? (
            <div>
              {/* Activity Bar Breakdown */}
              <div style={{ display: "flex", gap: "12px", margin: "16px 0" }}>
                <div style={{ flex: 1, background: "rgba(16, 185, 129, 0.1)", border: "1px solid var(--low-border)", padding: "12px", borderRadius: "8px", textAlign: "center" }}>
                  <div style={{ fontSize: "1.4rem", fontWeight: "800", color: "var(--low-color)", fontFamily: "var(--font-mono)" }}>
                    {cseDetail.breakdown.normal_activity_count}
                  </div>
                  <div style={{ fontSize: "0.72rem", color: "var(--text-secondary)" }}>Normal Activity</div>
                </div>

                <div style={{ flex: 1, background: "rgba(245, 158, 11, 0.1)", border: "1px solid var(--high-border)", padding: "12px", borderRadius: "8px", textAlign: "center" }}>
                  <div style={{ fontSize: "1.4rem", fontWeight: "800", color: "var(--high-color)", fontFamily: "var(--font-mono)" }}>
                    {cseDetail.breakdown.low_activity_count}
                  </div>
                  <div style={{ fontSize: "0.72rem", color: "var(--text-secondary)" }}>Low Activity (&le; 5 alerts)</div>
                </div>

                <div style={{ flex: 1, background: "rgba(244, 63, 94, 0.1)", border: "1px solid var(--crit-border)", padding: "12px", borderRadius: "8px", textAlign: "center" }}>
                  <div style={{ fontSize: "1.4rem", fontWeight: "800", color: "var(--crit-color)", fontFamily: "var(--font-mono)" }}>
                    {cseDetail.breakdown.zero_activity_count}
                  </div>
                  <div style={{ fontSize: "0.72rem", color: "var(--crit-color)", fontWeight: "700" }}>Zero Activity (Silent)</div>
                </div>
              </div>

              {/* Silent Assets Table */}
              <h4 style={{ fontSize: "0.9rem", color: "var(--crit-color)", margin: "16px 0 8px 0" }}>
                ⚠️ High-Consequence Assets with ZERO Security Activity ({cseDetail.zero_activity_assets.length})
              </h4>
              <div className="table-container" style={{ maxHeight: "360px", overflowY: "auto" }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Asset ID</th>
                      <th>Asset Type</th>
                      <th>Business Function</th>
                      <th>Environment</th>
                      <th>Alerts</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cseDetail.zero_activity_assets.map((a) => (
                      <tr key={a.asset_id}>
                        <td className="font-mono" style={{ fontWeight: "700", color: "var(--crit-color)" }}>
                          {a.asset_id}
                        </td>
                        <td>{a.asset_type}</td>
                        <td style={{ fontSize: "0.78rem" }}>{a.business_function}</td>
                        <td>
                          <span className="badge badge-medium">{a.environment}</span>
                        </td>
                        <td className="font-mono" style={{ fontWeight: "800", color: "var(--crit-color)" }}>
                          0
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div style={{ color: "var(--text-muted)" }}>Select an entity to inspect blindspots.</div>
          )}
        </div>
      </div>
    </div>
  );
}
