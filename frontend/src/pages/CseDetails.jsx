import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import RiskBadge from "../components/RiskBadge";
import EvidenceModal from "../components/EvidenceModal";
import ReviewModal from "../components/ReviewModal";

export default function CseDetails({ cseId, onBack, onNavigateCase, onNavigateQueue }) {
  const [cse, setCse] = useState(null);
  const [findings, setFindings] = useState([]);
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [reviewFinding, setReviewFinding] = useState(null);
  const [activeTab, setActiveTab] = useState("findings"); // findings | peer_deviations | assets

  const loadData = async () => {
    setLoading(true);
    try {
      const [cseRes, findingsRes, assetsRes] = await Promise.all([
        api.getCSEDetail(cseId),
        api.getCSEFindings(cseId),
        api.getCSEAssets(cseId),
      ]);
      setCse(cseRes);
      setFindings(findingsRes);
      setAssets(assetsRes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [cseId]);

  const handleReviewSave = async (findingId, payload) => {
    await api.reviewFinding(findingId, payload);
    await loadData();
  };

  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: "center", padding: "80px 0" }}>
        <div style={{ fontSize: "1.3rem", color: "var(--accent-cyan)", fontWeight: "700" }}>Loading Profile for {cseId}...</div>
      </div>
    );
  }

  if (!cse) {
    return (
      <div className="page-container">
        <div className="card">Entity {cseId} not found. <button className="btn btn-secondary" onClick={onBack}>Back</button></div>
      </div>
    );
  }

  const score = cse.risk_score || {
    overall_score: 0,
    risk_level: "LOW",
    execution_gap_score: 0,
    negative_space_score: 0,
    investigation_score: 0,
    escalation_score: 0,
    anomaly_score: 0,
    peer_deviation_score: 0,
    primary_concern: "Normal operational discipline",
  };

  const silentAssets = assets.filter(
    (a) => a.criticality === "CRITICAL" && (cse.metrics.crit_assets_without_activity > 0)
  );

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <button className="btn btn-sm btn-secondary" onClick={onBack} style={{ marginBottom: "8px" }}>
            ← Back to All Entities
          </button>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <span className="font-mono" style={{ fontSize: "1.4rem", fontWeight: "800", color: "var(--accent-cyan)" }}>
              {cse.cse_id}
            </span>
            <h2 style={{ fontSize: "1.6rem" }}>{cse.name}</h2>
            <RiskBadge level={score.risk_level} score={score.overall_score} />
          </div>
          <p className="page-description">
            Sector: <strong>{cse.sector}</strong> • Criticality: <strong>{cse.criticality}</strong> • Total Inventory Assets: <strong>{cse.total_assets}</strong> • Operational Tier: <strong>{cse.cluster_info?.tier_name || "Tier 1"}</strong>
          </p>
        </div>

        <div className="page-actions">
          <button className="btn btn-secondary" onClick={() => onNavigateQueue(cse.cse_id)}>
            Filter Review Queue for {cse.cse_id} →
          </button>
        </div>
      </div>

      {/* Risk Breakdown Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: "20px", marginBottom: "24px" }}>
        {/* Overall Score Card */}
        <div className="card" style={{ textAlign: "center", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", padding: "30px 20px" }}>
          <div style={{ fontSize: "0.76rem", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: "700" }}>
            Supervisory Risk Score
          </div>
          <div style={{ fontSize: "4rem", fontWeight: "900", fontFamily: "var(--font-mono)", color: score.risk_level === "CRITICAL" ? "var(--crit-color)" : (score.risk_level === "HIGH" ? "var(--high-color)" : "var(--accent-cyan)"), lineHeight: "1.1", margin: "10px 0" }}>
            {score.overall_score}
            <span style={{ fontSize: "1.4rem", color: "var(--text-muted)" }}>/100</span>
          </div>
          <RiskBadge level={score.risk_level} />
          <div style={{ marginTop: "14px", fontSize: "0.84rem", fontWeight: "600", color: "var(--text-primary)" }}>
            {score.primary_concern}
          </div>
        </div>

        {/* 6 Component Breakdown */}
        <div className="card">
          <div className="card-title">
            <span>Explainable Risk Score Components</span>
            <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Weighted Scoring Model (1.00 Total)</span>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginTop: "10px" }}>
            {[
              { label: "Execution Gap Score (25%)", val: score.execution_gap_score, color: "var(--high-color)", desc: "Procedural failures & rapid closures" },
              { label: "Negative Space Score (20%)", val: score.negative_space_score, color: "var(--crit-color)", desc: "Silent assets & omitted escalations" },
              { label: "Investigation Weakness (15%)", val: score.investigation_score, color: "var(--med-color)", desc: "Superficial triage & single actions" },
              { label: "Escalation Weakness (15%)", val: score.escalation_score, color: "var(--crit-color)", desc: "Failure to escalate critical threats" },
              { label: "ML Anomaly Score (15%)", val: score.anomaly_score, color: "var(--accent-purple)", desc: "Isolation Forest multidimensional outlier" },
              { label: "Peer Deviation Score (10%)", val: score.peer_deviation_score, color: "var(--accent-cyan)", desc: "Deviations from sector cluster baseline" },
            ].map((comp, idx) => (
              <div key={idx} style={{ background: "var(--bg-subtle)", padding: "12px 14px", borderRadius: "8px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", fontWeight: "700" }}>
                  <span>{comp.label}</span>
                  <span className="font-mono" style={{ color: comp.color }}>{comp.val}</span>
                </div>
                <div className="score-progress-bar" style={{ margin: "6px 0" }}>
                  <div className="score-fill" style={{ width: `${comp.val}%`, background: comp.color }} />
                </div>
                <div style={{ fontSize: "0.68rem", color: "var(--text-muted)" }}>{comp.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: "8px", borderBottom: "1px solid var(--border)", marginBottom: "20px" }}>
        {[
          { id: "findings", label: `Evidence-Backed Findings (${findings.length})` },
          { id: "peer_deviations", label: "Peer Baseline Deviations" },
          { id: "assets", label: `Asset Inventory (${assets.length})` },
        ].map((tab) => (
          <button
            key={tab.id}
            className={`nav-btn ${activeTab === tab.id ? "active" : ""}`}
            style={{ borderRadius: "6px 6px 0 0", padding: "10px 18px" }}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Findings (Why was this CSE flagged?) */}
      {activeTab === "findings" && (
        <div>
          <div style={{ marginBottom: "14px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3 style={{ fontSize: "1.1rem" }}>Why was {cse.cse_id} flagged?</h3>
            <span style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
              Every finding is backed by mathematical thresholds and traceable source records
            </span>
          </div>

          {findings.length === 0 ? (
            <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--low-color)" }}>
              ✓ No execution gaps or negative space conditions flagged for this entity.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              {findings.map((f) => (
                <div
                  key={f.finding_id}
                  className="card"
                  style={{
                    borderLeft: `4px solid ${f.severity === "CRITICAL" ? "var(--crit-color)" : "var(--high-color)"}`,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "8px" }}>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                        <span className="badge badge-medium">{f.rule_code}</span>
                        <RiskBadge level={f.severity} />
                        <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Category: {f.category}</span>
                        <span className={`badge ${f.status === "ACCEPTED" ? "badge-critical" : "badge-medium"}`}>
                          Status: {f.status}
                        </span>
                      </div>
                      <h4 style={{ fontSize: "1.05rem", color: "#FFFFFF" }}>{f.title}</h4>
                    </div>

                    <div style={{ display: "flex", gap: "8px" }}>
                      <button
                        className="btn btn-sm btn-secondary"
                        onClick={() => setSelectedFinding(f)}
                      >
                        Inspect Evidence & Records 🔍
                      </button>
                      <button
                        className="btn btn-sm btn-primary"
                        onClick={() => setReviewFinding(f)}
                      >
                        Human Review ✍️
                      </button>
                    </div>
                  </div>

                  <p style={{ color: "var(--text-secondary)", fontSize: "0.84rem", margin: "10px 0", lineHeight: "1.6" }}>
                    {f.description}
                  </p>

                  <div className="evidence-box">
                    <div className="evidence-label">Observed Operational Evidence</div>
                    <div>{f.evidence_summary}</div>
                  </div>

                  {f.supervisor_notes && (
                    <div style={{ fontSize: "0.78rem", color: "var(--low-color)", marginTop: "6px" }}>
                      <strong>Supervisor Note:</strong> {f.supervisor_notes} (by {f.reviewed_by})
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Peer Baseline Deviations */}
      {activeTab === "peer_deviations" && (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Operational Metric</th>
                <th>Entity Value</th>
                <th>Peer Median</th>
                <th>Deviation</th>
                <th>Z-Score</th>
                <th>Evaluation</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(cse.deviations || {}).map(([metric, stats]) => {
                const z = stats.z_score || 0;
                const isAbnormal = Math.abs(z) > 1.8;
                return (
                  <tr key={metric}>
                    <td style={{ fontWeight: "700" }}>{metric.replace(/_/g, " ")}</td>
                    <td className="font-mono" style={{ fontWeight: "800", color: isAbnormal ? "var(--crit-color)" : "var(--text-primary)" }}>
                      {stats.value}
                    </td>
                    <td className="font-mono">{stats.peer_median}</td>
                    <td className="font-mono" style={{ color: stats.deviation > 0 ? "var(--high-color)" : "var(--accent-cyan)" }}>
                      {stats.deviation > 0 ? `+${stats.deviation}` : stats.deviation}
                    </td>
                    <td className="font-mono">
                      <span className={`badge ${Math.abs(z) > 2.5 ? "badge-critical" : (Math.abs(z) > 1.5 ? "badge-medium" : "badge-low")}`}>
                        {z} σ
                      </span>
                    </td>
                    <td style={{ fontSize: "0.78rem", color: isAbnormal ? "var(--crit-color)" : "var(--low-color)" }}>
                      {isAbnormal ? "Significant Operational Deviation" : "Within Normal Peer Tolerance"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 3: Asset Inventory */}
      {activeTab === "assets" && (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Asset ID</th>
                <th>Asset Type</th>
                <th>Criticality</th>
                <th>Business Function</th>
                <th>Environment</th>
                <th>Monitoring Status</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((a) => (
                <tr key={a.asset_id}>
                  <td className="font-mono" style={{ fontWeight: "700", color: "var(--accent-cyan)" }}>
                    {a.asset_id}
                  </td>
                  <td>{a.asset_type}</td>
                  <td>
                    <span style={{ fontWeight: "700", color: a.criticality === "CRITICAL" ? "var(--crit-color)" : "var(--text-secondary)" }}>
                      {a.criticality}
                    </span>
                  </td>
                  <td>{a.business_function}</td>
                  <td>
                    <span className="badge badge-medium">{a.environment}</span>
                  </td>
                  <td>
                    <span className="badge badge-low">
                      <span className="badge-dot" />
                      {a.monitoring_status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Evidence Drilldown Modal */}
      {selectedFinding && (
        <EvidenceModal
          finding={selectedFinding}
          onClose={() => setSelectedFinding(null)}
          onOpenCase={(caseId) => {
            setSelectedFinding(null);
            onNavigateCase(caseId);
          }}
        />
      )}

      {/* Human-in-the-Loop Review Modal */}
      {reviewFinding && (
        <ReviewModal
          finding={reviewFinding}
          onClose={() => setReviewFinding(null)}
          onSave={handleReviewSave}
        />
      )}
    </div>
  );
}
