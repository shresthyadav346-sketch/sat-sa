import React, { useEffect, useState } from "react";
import { api } from "../services/api";

export default function Trends() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrends = async () => {
      setLoading(true);
      try {
        const res = await api.getTrends();
        setData(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchTrends();
  }, []);

  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: "center", padding: "80px 0" }}>
        <div style={{ fontSize: "1.3rem", color: "var(--accent-cyan)", fontWeight: "700" }}>Loading Historical Trend Models...</div>
      </div>
    );
  }

  const { periods, detected_trend_anomalies } = data || {};

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-title-group">
          <h2>Operational Trends & Longitudinal Assessment</h2>
          <p className="page-description">
            Tracks SOC discipline over quarterly cycles. Identifies procedural drift, gradual deterioration in escalation compliance,
            and systemic rapid-closure spikes before an incident occurs.
          </p>
        </div>
      </div>

      {/* Detected Deterioration Signals */}
      <div className="card" style={{ borderLeft: "4px solid var(--crit-color)", marginBottom: "24px" }}>
        <h3 style={{ fontSize: "1rem", color: "var(--crit-color)", marginBottom: "8px" }}>
          ⚠️ Critical Longitudinal Deterioration Signals Detected
        </h3>
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          {detected_trend_anomalies?.map((sig, idx) => (
            <div key={idx} style={{ fontSize: "0.84rem", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ color: "var(--crit-color)", fontWeight: "900" }}>•</span>
              <span>{sig}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Period Timeline Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "20px", marginBottom: "24px" }}>
        {periods?.map((p, idx) => {
          const isCurrent = idx === periods.length - 1;
          return (
            <div
              key={p.period}
              className="card"
              style={{
                borderTop: `4px solid ${isCurrent ? "var(--crit-color)" : "var(--accent-cyan)"}`,
                background: isCurrent ? "rgba(244, 63, 94, 0.04)" : "var(--bg-card)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <h4 style={{ fontSize: "0.95rem", color: isCurrent ? "var(--crit-color)" : "var(--text-primary)" }}>{p.period}</h4>
                {isCurrent && <span className="badge badge-critical">Active Cycle</span>}
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "12px", fontSize: "0.82rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Critical Threats Ingested:</span>
                  <span className="font-mono" style={{ fontWeight: "700" }}>{p.critical_alerts}</span>
                </div>

                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                    <span style={{ color: "var(--text-secondary)" }}>Escalation Compliance:</span>
                    <span className="font-mono" style={{ fontWeight: "800", color: p.escalation_rate < 75 ? "var(--crit-color)" : "var(--low-color)" }}>
                      {p.escalation_rate}%
                    </span>
                  </div>
                  <div className="score-progress-bar">
                    <div className="score-fill" style={{ width: `${p.escalation_rate}%`, background: p.escalation_rate < 75 ? "var(--crit-color)" : "var(--low-color)" }} />
                  </div>
                </div>

                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                    <span style={{ color: "var(--text-secondary)" }}>Rapid Closure Rate:</span>
                    <span className="font-mono" style={{ fontWeight: "800", color: p.rapid_closure_rate > 10 ? "var(--crit-color)" : "var(--accent-cyan)" }}>
                      {p.rapid_closure_rate}%
                    </span>
                  </div>
                  <div className="score-progress-bar">
                    <div className="score-fill" style={{ width: `${p.rapid_closure_rate * 5}%`, background: p.rapid_closure_rate > 10 ? "var(--crit-color)" : "var(--accent-cyan)" }} />
                  </div>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", borderTop: "1px solid var(--border)", paddingTop: "8px", marginTop: "4px" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Execution Gaps Flagged:</span>
                  <span className="badge badge-medium">{p.execution_gaps_detected}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
