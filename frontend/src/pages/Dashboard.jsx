import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import MetricCard from "../components/MetricCard";
import RiskBadge from "../components/RiskBadge";

export default function Dashboard({ onNavigateCSE, onNavigateTab }) {
  const [data, setData] = useState(null);
  const [chainStatus, setChainStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSector, setSelectedSector] = useState("ALL");

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const [res, chainRes] = await Promise.all([
        api.getDashboardSummary(),
        api.verifyAuditChain().catch(() => null),
      ]);
      setData(res);
      setChainStatus(chainRes);
    } catch (err) {
      setError(err.message || "Failed to load executive dashboard.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: "center", padding: "80px 0" }}>
        <div style={{ fontSize: "1.5rem", fontWeight: "700", color: "var(--accent-cyan)" }}>Loading Supervisory Analytics...</div>
        <div style={{ color: "var(--text-secondary)", marginTop: "8px" }}>Aggregating national SOC operational telemetry</div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="page-container">
        <div className="card" style={{ borderLeft: "4px solid var(--crit-color)", textAlign: "center", padding: "40px" }}>
          <h3 style={{ color: "var(--crit-color)" }}>Error Connecting to Local Backend</h3>
          <p style={{ color: "var(--text-secondary)", margin: "12px 0" }}>{error || "Unknown error occurred"}</p>
          <button className="btn btn-primary" onClick={fetchDashboard}>Retry Connection</button>
        </div>
      </div>
    );
  }

  const { kpis, risk_distribution, findings_by_category, top_cses_requiring_attention } = data;

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div className="page-title-group">
          <h2>Executive Supervisory Dashboard</h2>
          <p className="page-description">
            Continuous operational evidence assessment for Critical Sector Entities (CSEs).
            Identifies execution gaps, negative space conditions, and anomalous behavior without replacing expert human review.
          </p>
        </div>
        <div className="page-actions">
          <button className="btn btn-secondary" onClick={() => onNavigateTab("review-queue")}>
            Review Queue ({kpis.priority_reviews_count})
          </button>
          <button className="btn btn-primary" onClick={() => onNavigateTab("reports")}>
            Generate Formal Report
          </button>
        </div>
      </div>

      {/* Live National Threat & Operational Telemetry Stream */}
      <div className="telemetry-ticker">
        <div className="ticker-badge">
          <span className="live-radar-dot" style={{ width: "6px", height: "6px" }}></span>
          SUPERVISORY RADAR
        </div>
        <div className="ticker-items">
          <div className="ticker-item">
            <span className="ticker-dot" style={{ background: "var(--crit-color)" }}></span>
            <span style={{ color: "var(--text-primary)", fontWeight: "700" }}>CSE-007 (Power):</span>
            <span style={{ color: "var(--crit-color)", fontWeight: "600" }}>65% Critical closures &lt; 3m (Flagged EG-001)</span>
          </div>
          <div className="ticker-item">
            <span className="ticker-dot" style={{ background: "var(--high-color)" }}></span>
            <span style={{ color: "var(--text-primary)", fontWeight: "700" }}>CSE-014 (Telecom):</span>
            <span>Negative Space 35% silent critical assets (NS-001)</span>
          </div>
          <div className="ticker-item">
            <span className="ticker-dot" style={{ background: "var(--accent-purple)" }}></span>
            <span style={{ color: "var(--text-primary)", fontWeight: "700" }}>CSE-021 (Banking):</span>
            <span>Template Spammer NLP Cosine Cluster &gt; 0.85 (EG-006)</span>
          </div>
          <div className="ticker-item">
            <span className="ticker-dot" style={{ background: "var(--low-color)" }}></span>
            <span style={{ color: "var(--text-primary)", fontWeight: "700" }}>Cryptographic Ledger:</span>
            <span style={{ color: "var(--low-color)" }}>{chainStatus?.total_blocks || 15} SHA-256 blocks chained</span>
          </div>
        </div>
      </div>

      {/* Chain Integrity Live Indicator */}
      {chainStatus && (
        <div
          className="card"
          style={{
            marginBottom: "20px",
            padding: "12px 18px",
            borderRadius: "var(--radius-md)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "12px",
            background: chainStatus.valid
              ? "linear-gradient(90deg, rgba(16, 185, 129, 0.09) 0%, rgba(13, 19, 34, 0.7) 100%)"
              : "linear-gradient(90deg, rgba(244, 63, 94, 0.14) 0%, rgba(13, 19, 34, 0.7) 100%)",
            border: `1px solid ${chainStatus.valid ? "var(--low-border)" : "var(--crit-border)"}`,
            boxShadow: chainStatus.valid ? "0 0 16px rgba(16, 185, 129, 0.1)" : "0 0 16px rgba(244, 63, 94, 0.15)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ fontSize: "1.2rem" }}>{chainStatus.valid ? "🔒" : "⚠️"}</span>
            <span style={{ fontWeight: "700", fontSize: "0.88rem", color: chainStatus.valid ? "var(--low-color)" : "var(--crit-color)" }}>
              {chainStatus.valid
                ? `✅ Supervisory Audit Hash Chain Verified — ${chainStatus.total_blocks} Blocks Cryptographically Intact (SHA-256)`
                : `❌ Audit Trail Integrity Compromised — Tamper Detected at Block #${chainStatus.broken_at_index}`}
            </span>
          </div>
          <button
            className="btn btn-secondary"
            onClick={() => onNavigateTab("audit-log")}
            style={{ fontSize: "0.78rem", padding: "5px 14px", border: "1px solid rgba(56, 189, 248, 0.3)" }}
          >
            Inspect Blockchain Ledger →
          </button>
        </div>
      )}

      {/* KPI Grid */}
      <div className="kpi-grid">
        <MetricCard
          label="Entities Assessed"
          value={kpis.cses_assessed}
          subtext="Power, Banking, Telecom, Transport, Defence"
          variant="default"
        />
        <MetricCard
          label="Security Alerts Analyzed"
          value={kpis.alerts_analysed.toLocaleString()}
          subtext="Raw telemetry processed locally"
          variant="default"
        />
        <MetricCard
          label="Cases Examined"
          value={kpis.cases_analysed.toLocaleString()}
          subtext="Full lifecycle workflow audit"
          variant="default"
        />
        <MetricCard
          label="Critical Assets"
          value={kpis.critical_assets_count.toLocaleString()}
          subtext="High-consequence infrastructure"
          variant="default"
        />
        <MetricCard
          label="High-Risk CSEs"
          value={kpis.high_risk_cses_count + kpis.critical_risk_cses_count}
          subtext={`${kpis.critical_risk_cses_count} Critical • ${kpis.high_risk_cses_count} High Risk`}
          variant="critical"
        />
        <MetricCard
          label="Execution Gaps"
          value={kpis.execution_gaps_count}
          subtext="Procedural failures & rapid closures"
          variant="warning"
        />
        <MetricCard
          label="Negative Space Signals"
          value={kpis.negative_space_signals_count}
          subtext="Silent assets & missing escalations"
          variant="critical"
        />
        <MetricCard
          label="Supervisory Time Saved"
          value={`${kpis.time_saved_pct}%`}
          subtext="Focused on top 100 cases vs manual sampling"
          variant="success"
        />
      </div>

      {/* Distribution & Breakdown Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "24px" }}>
        {/* Risk Distribution Card */}
        <div className="card">
          <div className="card-title">
            <span>Entity Supervisory Risk Distribution</span>
            <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>{kpis.cses_assessed} Total Entities</span>
          </div>

          <div style={{ display: "flex", gap: "12px", margin: "16px 0" }}>
            {[
              { label: "Critical Risk (81-100)", count: risk_distribution.critical, color: "var(--crit-color)", bg: "var(--crit-bg)" },
              { label: "High Risk (61-80)", count: risk_distribution.high, color: "var(--high-color)", bg: "var(--high-bg)" },
              { label: "Medium Risk (31-60)", count: risk_distribution.medium, color: "var(--med-color)", bg: "var(--med-bg)" },
              { label: "Low / Normal (0-30)", count: risk_distribution.low, color: "var(--low-color)", bg: "var(--low-bg)" },
            ].map((item, idx) => (
              <div key={idx} style={{ flex: 1, background: item.bg, border: `1px solid ${item.color}33`, borderRadius: "8px", padding: "12px 14px", textAlign: "center" }}>
                <div style={{ fontSize: "1.6rem", fontWeight: "800", color: item.color, fontFamily: "var(--font-mono)" }}>
                  {item.count}
                </div>
                <div style={{ fontSize: "0.72rem", color: "var(--text-secondary)", marginTop: "4px" }}>
                  {item.label}
                </div>
              </div>
            ))}
          </div>

          <p style={{ fontSize: "0.78rem", color: "var(--text-secondary)", lineHeight: "1.5" }}>
            Supervisory risk score synthesizes execution gaps, telemetry blindspots, investigation depth, escalation discipline, and statistical peer deviations into an explainable 0–100 index.
          </p>
        </div>

        {/* Findings by Category Card */}
        <div className="card">
          <div className="card-title">
            <span>Operational Findings by Category</span>
            <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>Total Active Signals</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "14px" }}>
            {[
              { label: "Execution Gaps (EG-001 to EG-007)", count: findings_by_category.execution_gaps, color: "var(--high-color)", max: 60 },
              { label: "Negative Space Conditions (NS-001 to NS-006)", count: findings_by_category.negative_space, color: "var(--crit-color)", max: 30 },
              { label: "Multidimensional ML Anomalies (Isolation Forest)", count: findings_by_category.anomalies, color: "var(--accent-purple)", max: 15 },
              { label: "Statistical Peer Deviations (Z-score &gt; 2.0)", count: findings_by_category.peer_deviations, color: "var(--accent-cyan)", max: 20 },
            ].map((cat, idx) => (
              <div key={idx}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", marginBottom: "4px" }}>
                  <span style={{ color: "var(--text-primary)", fontWeight: "600" }}>{cat.label}</span>
                  <span style={{ color: cat.color, fontWeight: "700", fontFamily: "var(--font-mono)" }}>{cat.count} findings</span>
                </div>
                <div className="score-progress-bar">
                  <div className="score-fill" style={{ width: `${Math.min(100, (cat.count / cat.max) * 100)}%`, background: cat.color }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top CSEs Requiring Immediate Attention */}
      <div className="card">
        <div className="card-title" style={{ flexWrap: "wrap", gap: "12px" }}>
          <div>
            <span style={{ fontSize: "1.1rem" }}>Top Critical Sector Entities Requiring Immediate Attention</span>
            <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "2px" }}>
              Ranked by supervisory risk severity, execution gaps, and monitoring blindspots
            </div>
          </div>
          
          <div style={{ display: "flex", gap: "8px", alignItems: "center", flexWrap: "wrap" }}>
            <div style={{ display: "flex", gap: "4px", background: "rgba(0,0,0,0.25)", padding: "3px", borderRadius: "16px", border: "1px solid rgba(255,255,255,0.06)" }}>
              {["ALL", "Power", "Banking", "Telecom", "Transport", "Defence"].map((sec) => (
                <button
                  key={sec}
                  onClick={() => setSelectedSector(sec)}
                  style={{
                    fontSize: "0.72rem",
                    padding: "3px 10px",
                    borderRadius: "12px",
                    border: "none",
                    cursor: "pointer",
                    fontWeight: "700",
                    background: selectedSector === sec ? "var(--accent-blue)" : "transparent",
                    color: selectedSector === sec ? "white" : "var(--text-secondary)",
                    transition: "all 0.2s ease",
                  }}
                >
                  {sec === "ALL" ? "All Sectors" : sec}
                </button>
              ))}
            </div>

            <button className="btn btn-sm btn-secondary" onClick={() => onNavigateTab("ranking")}>
              View All 45 Entities →
            </button>
          </div>
        </div>

        <div className="table-container" style={{ marginTop: "14px" }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Entity ID</th>
                <th>Entity Name</th>
                <th>Critical Sector</th>
                <th>Supervisory Risk</th>
                <th>Primary Supervisory Concern</th>
                <th>Execution Gap</th>
                <th>Negative Space</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {top_cses_requiring_attention
                .filter((cse) => selectedSector === "ALL" || cse.sector.toLowerCase() === selectedSector.toLowerCase())
                .map((cse) => (
                  <tr key={cse.cse_id}>
                    <td style={{ fontWeight: "800", color: cse.rank <= 2 ? "var(--crit-color)" : "var(--text-muted)" }}>
                      #{cse.rank}
                    </td>
                    <td className="font-mono" style={{ fontWeight: "700", color: "var(--accent-cyan)" }}>
                      {cse.cse_id}
                    </td>
                    <td style={{ fontWeight: "600" }}>
                      <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: "6px" }}>
                        <span>{cse.name}</span>
                        {cse.cse_id === "CSE-007" && <span className="badge badge-critical" style={{ fontSize: "0.6rem" }}>⚡ THE RAPID CLOSER</span>}
                        {cse.cse_id === "CSE-014" && <span className="badge badge-medium" style={{ fontSize: "0.6rem" }}>🌑 THE DARK ZONE</span>}
                        {cse.cse_id === "CSE-021" && <span className="badge badge-medium" style={{ fontSize: "0.6rem" }}>📋 TEMPLATE SPAMMER</span>}
                        {cse.cse_id === "CSE-032" && <span className="badge badge-medium" style={{ fontSize: "0.6rem" }}>🔄 CHRONIC FLAPPER</span>}
                        {cse.cse_id === "CSE-041" && <span className="badge badge-critical" style={{ fontSize: "0.6rem" }}>🎯 GOODHART'S LAW</span>}
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-medium">{cse.sector}</span>
                    </td>
                    <td>
                      <RiskBadge level={cse.risk_level} score={cse.risk_score} />
                    </td>
                    <td style={{ color: "var(--text-primary)", fontWeight: "600" }}>
                      {cse.primary_concern}
                    </td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <span className="font-mono" style={{ fontSize: "0.75rem", width: "32px" }}>{cse.execution_gap_score}</span>
                        <div className="score-progress-bar" style={{ width: "80px" }}>
                          <div className="score-fill" style={{ width: `${cse.execution_gap_score}%`, background: "var(--high-color)" }} />
                        </div>
                      </div>
                    </td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <span className="font-mono" style={{ fontSize: "0.75rem", width: "32px" }}>{cse.negative_space_score}</span>
                        <div className="score-progress-bar" style={{ width: "80px" }}>
                          <div className="score-fill" style={{ width: `${cse.negative_space_score}%`, background: "var(--crit-color)" }} />
                        </div>
                      </div>
                    </td>
                    <td>
                      <button
                        className="btn btn-sm btn-primary"
                        onClick={() => onNavigateCSE(cse.cse_id)}
                      >
                        Investigate →
                      </button>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
