import React, { useEffect, useState } from "react";
import { api } from "../services/api";

export default function PeerComparison() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState("CSE-007,CSE-014,CSE-021,CSE-041");

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await api.getPeerComparison(selectedIds);
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedIds]);

  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: "center", padding: "80px 0" }}>
        <div style={{ fontSize: "1.3rem", color: "var(--accent-cyan)", fontWeight: "700" }}>Computing Peer Distributions & Baselines...</div>
      </div>
    );
  }

  const { peer_benchmarks, entities, available_cse_ids } = data || {};

  const metricsToCompare = [
    { key: "critical_rapid_closure_rate", label: "Critical Rapid Closure Rate (%)", unit: "%", lowerIsBetter: true },
    { key: "critical_escalation_rate", label: "Critical Escalation Rate (%)", unit: "%", lowerIsBetter: false },
    { key: "avg_investigation_actions", label: "Avg Investigation Actions / Case", unit: "", lowerIsBetter: false },
    { key: "median_closure_time_mins", label: "Median Closure Time (Minutes)", unit: "m", lowerIsBetter: false },
    { key: "monitoring_coverage", label: "Asset Monitoring Coverage (%)", unit: "%", lowerIsBetter: false },
    { key: "reopen_rate", label: "Ticket Reopen Rate (%)", unit: "%", lowerIsBetter: true },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-title-group">
          <h2>Peer Comparison & Operational Benchmarking</h2>
          <p className="page-description">
            Objective baseline comparison across entities. Measures deviations against peer medians and cluster distributions,
            highlighting abnormal operational behavior.
          </p>
        </div>
      </div>

      {/* Preset Entity Buttons */}
      <div className="card" style={{ marginBottom: "20px", padding: "14px 20px" }}>
        <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
          <span style={{ fontSize: "0.82rem", fontWeight: "700", color: "var(--text-secondary)" }}>Quick Comparison Presets:</span>
          <button
            className="btn btn-sm btn-secondary"
            onClick={() => setSelectedIds("CSE-007,CSE-014,CSE-021,CSE-041")}
          >
            Injected Anomaly Benchmark (CSE-007, 014, 021, 041)
          </button>
          <button
            className="btn btn-sm btn-secondary"
            onClick={() => setSelectedIds("CSE-001,CSE-002,CSE-003,CSE-004")}
          >
            Baseline Operational Entities (CSE-001 to 004)
          </button>
          <button
            className="btn btn-sm btn-secondary"
            onClick={() => setSelectedIds("CSE-007,CSE-001")}
          >
            CSE-007 (Anomalous) vs CSE-001 (Baseline)
          </button>
        </div>
      </div>

      {/* Side-by-Side Comparison Matrix */}
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ minWidth: "220px" }}>Operational Metric</th>
              <th style={{ background: "rgba(6, 182, 212, 0.12)", color: "var(--accent-cyan)", minWidth: "120px" }}>
                Peer Median
              </th>
              {entities?.map((e) => (
                <th key={e.cse_id} style={{ minWidth: "160px" }}>
                  <div className="font-mono" style={{ color: "var(--accent-cyan)", fontWeight: "800" }}>{e.cse_id}</div>
                  <div style={{ fontSize: "0.68rem", color: "var(--text-secondary)", textTransform: "none" }}>{e.name}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {metricsToCompare.map((m) => {
              const peerMed = peer_benchmarks?.[m.key]?.median ?? 0;

              return (
                <tr key={m.key}>
                  <td style={{ fontWeight: "700" }}>{m.label}</td>
                  <td className="font-mono" style={{ fontWeight: "800", color: "var(--accent-cyan)", background: "rgba(6, 182, 212, 0.05)" }}>
                    {peerMed} {m.unit}
                  </td>
                  {entities?.map((e) => {
                    const val = e.metrics?.[m.key] ?? 0;
                    const dev = e.deviations?.[m.key]?.deviation ?? (val - peerMed);
                    const z = e.deviations?.[m.key]?.z_score ?? 0;
                    const isSevereDev = Math.abs(z) > 2.0;

                    return (
                      <td key={e.cse_id}>
                        <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                          <span className="font-mono" style={{ fontWeight: "800", fontSize: "0.95rem", color: isSevereDev ? "var(--crit-color)" : "var(--text-primary)" }}>
                            {val} {m.unit}
                          </span>
                          <span style={{ fontSize: "0.7rem", color: dev < 0 ? "var(--accent-cyan)" : "var(--high-color)", fontWeight: "600" }}>
                            {dev > 0 ? `+${dev.toFixed(1)}` : dev.toFixed(1)} vs median ({z}σ)
                          </span>
                        </div>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
