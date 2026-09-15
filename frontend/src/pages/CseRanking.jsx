import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import RiskBadge from "../components/RiskBadge";

export default function CseRanking({ onSelectCSE }) {
  const [cses, setCses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sectorFilter, setSectorFilter] = useState("");
  const [riskFilter, setRiskFilter] = useState("");
  const [search, setSearch] = useState("");

  const fetchCses = async () => {
    setLoading(true);
    try {
      const params = {};
      if (sectorFilter) params.sector = sectorFilter;
      if (riskFilter) params.risk_level = riskFilter;
      if (search) params.search = search;
      const res = await api.getCSESummaries(params);
      setCses(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCses();
  }, [sectorFilter, riskFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchCses();
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-title-group">
          <h2>Critical Sector Entities — Supervisory Risk Ranking</h2>
          <p className="page-description">
            Objective, evidence-backed risk prioritization for all registered national entities.
            Higher scores identify entities with significant operational execution gaps, silent critical assets, or triage anomalies.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ marginBottom: "20px", padding: "14px 20px" }}>
        <form onSubmit={handleSearchSubmit} style={{ display: "flex", gap: "14px", alignItems: "center", flexWrap: "wrap" }}>
          <div style={{ flex: 1, minWidth: "220px" }}>
            <input
              type="text"
              className="form-input"
              placeholder="Search by entity name or CSE ID (e.g. CSE-007)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div style={{ width: "180px" }}>
            <select
              className="form-select"
              value={sectorFilter}
              onChange={(e) => setSectorFilter(e.target.value)}
            >
              <option value="">All Sectors</option>
              <option value="Power">Power Sector</option>
              <option value="Banking">Banking & Financial</option>
              <option value="Telecom">Telecommunications</option>
              <option value="Transport">Transport & Rail</option>
              <option value="Defence">Defence & Strategic</option>
            </select>
          </div>

          <div style={{ width: "180px" }}>
            <select
              className="form-select"
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
            >
              <option value="">All Risk Levels</option>
              <option value="CRITICAL">Critical (81–100)</option>
              <option value="HIGH">High (61–80)</option>
              <option value="MEDIUM">Medium (31–60)</option>
              <option value="LOW">Low (0–30)</option>
            </select>
          </div>

          <button type="submit" className="btn btn-secondary">
            Search
          </button>
          {(sectorFilter || riskFilter || search) && (
            <button
              type="button"
              className="btn btn-sm btn-secondary"
              onClick={() => {
                setSectorFilter("");
                setRiskFilter("");
                setSearch("");
              }}
            >
              Clear Filters
            </button>
          )}
        </form>
      </div>

      {/* Table */}
      {loading ? (
        <div style={{ textAlign: "center", padding: "60px 0", color: "var(--text-secondary)" }}>
          Loading entity rankings...
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Entity ID</th>
                <th>Entity Name</th>
                <th>Sector</th>
                <th>Criticality</th>
                <th>Assets</th>
                <th>Risk Score</th>
                <th>Primary Concern</th>
                <th>Findings</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {cses.map((cse, idx) => {
                const score = cse.risk_score?.overall_score ?? 0;
                const level = cse.risk_score?.risk_level ?? "LOW";
                const concern = cse.risk_score?.primary_concern ?? "Normal operational discipline";

                return (
                  <tr key={cse.cse_id}>
                    <td style={{ fontWeight: "800", color: idx < 2 ? "var(--crit-color)" : "var(--text-muted)" }}>
                      #{idx + 1}
                    </td>
                    <td className="font-mono" style={{ fontWeight: "700", color: "var(--accent-cyan)" }}>
                      {cse.cse_id}
                    </td>
                    <td style={{ fontWeight: "600" }}>{cse.name}</td>
                    <td>
                      <span className="badge badge-medium">{cse.sector}</span>
                    </td>
                    <td>
                      <span style={{ fontSize: "0.75rem", fontWeight: "700", color: cse.criticality === "CRITICAL" ? "var(--crit-color)" : "var(--text-secondary)" }}>
                        {cse.criticality}
                      </span>
                    </td>
                    <td className="font-mono">{cse.total_assets}</td>
                    <td>
                      <div style={{ display: "flex", flexDirection: "column", gap: "4px", width: "120px" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <RiskBadge level={level} score={score} />
                        </div>
                        <div className="score-progress-bar">
                          <div
                            className="score-fill"
                            style={{
                              width: `${score}%`,
                              background: level === "CRITICAL" ? "var(--crit-color)" : (level === "HIGH" ? "var(--high-color)" : "var(--accent-cyan)")
                            }}
                          />
                        </div>
                      </div>
                    </td>
                    <td style={{ maxWidth: "260px", color: "var(--text-primary)", fontWeight: "500" }}>
                      {concern}
                    </td>
                    <td className="font-mono">
                      <span className="badge badge-medium" style={{ background: cse.findings_count > 0 ? "rgba(249, 115, 22, 0.15)" : "var(--bg-subtle)", color: cse.findings_count > 0 ? "var(--high-color)" : "var(--text-muted)" }}>
                        {cse.findings_count}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-sm btn-primary"
                        onClick={() => onSelectCSE(cse.cse_id)}
                      >
                        Examine Profile →
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
