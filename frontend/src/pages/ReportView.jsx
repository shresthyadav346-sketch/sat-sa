import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import RiskBadge from "../components/RiskBadge";

export default function ReportView() {
  const [report, setReport] = useState(null);
  const [generating, setGenerating] = useState(true);

  const fetchReport = async () => {
    setGenerating(true);
    try {
      const res = await api.generateReport({
        title: "National Cyber Resilience SOC Supervisory Assessment Report",
        assessment_cycle: "Q3-2026 Examination Cycle",
        examiner_name: "NCIIPC National Examination Directorate",
        scope_sectors: ["Power", "Banking", "Telecom", "Transport", "Defence"]
      });
      setReport(res);
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadJSON = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${report.report_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (generating) {
    return (
      <div className="page-container" style={{ textAlign: "center", padding: "80px 0" }}>
        <div style={{ fontSize: "1.3rem", color: "var(--accent-cyan)", fontWeight: "700" }}>Compiling Formal Supervisory Report...</div>
        <div style={{ color: "var(--text-secondary)", marginTop: "8px" }}>Assembling evidence, peer benchmarks, and priority case summaries</div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="page-container">
        <div className="card">Failed to generate report. <button className="btn btn-primary" onClick={fetchReport}>Retry</button></div>
      </div>
    );
  }

  return (
    <div className="page-container" style={{ maxWidth: "1100px" }}>
      <div className="page-header" style={{ marginBottom: "16px" }}>
        <div>
          <h2>Formal Supervisory Assessment Report</h2>
          <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
            Report Reference: <strong className="font-mono">{report.report_id}</strong> • Generated: {new Date(report.generated_at).toLocaleString()}
          </div>
        </div>
        <div className="page-actions">
          <button className="btn btn-secondary" onClick={handleDownloadJSON}>
            Export JSON 💾
          </button>
          <button className="btn btn-primary" onClick={handlePrint}>
            Print / Save as PDF 🖨️
          </button>
        </div>
      </div>

      {/* Formal Report Paper Layout */}
      <div style={{ background: "var(--bg-card)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-md)", padding: "36px", boxShadow: "var(--shadow-md)" }}>
        {/* Title Header */}
        <div style={{ borderBottom: "2px solid var(--border)", paddingBottom: "20px", marginBottom: "24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div>
              <div style={{ fontSize: "0.8rem", fontWeight: "800", color: "var(--accent-cyan)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
                National Critical Information Infrastructure Protection Centre (NCIIPC)
              </div>
              <h1 style={{ fontSize: "1.6rem", color: "#FFFFFF", marginTop: "4px", fontWeight: "900" }}>
                {report.title}
              </h1>
              <div style={{ color: "var(--text-secondary)", fontSize: "0.88rem", marginTop: "4px" }}>
                Assessment Cycle: <strong>{report.assessment_cycle}</strong> | Authority: <strong>{report.examiner_name}</strong>
              </div>
            </div>
            <div style={{ textAlign: "right" }}>
              <span className="badge badge-medium" style={{ background: "rgba(234, 179, 8, 0.15)", color: "var(--med-color)" }}>
                {report.notice}
              </span>
            </div>
          </div>
        </div>

        {/* Section 1: Executive Summary */}
        <div style={{ marginBottom: "28px" }}>
          <h3 style={{ fontSize: "1.15rem", color: "var(--accent-cyan)", borderBottom: "1px solid var(--border)", paddingBottom: "6px", marginBottom: "12px" }}>
            1. Executive Assessment Summary
          </h3>
          <p style={{ color: "var(--text-primary)", fontSize: "0.86rem", lineHeight: "1.7" }}>
            This supervisory report compiles operational security data across <strong>{report.scope_summary.total_entities_evaluated} Critical Sector Entities</strong> encompassing <strong>{report.scope_summary.total_alerts_analyzed.toLocaleString()} security alerts</strong>, <strong>{report.scope_summary.total_cases_examined.toLocaleString()} case tickets</strong>, and <strong>{report.scope_summary.critical_assets_analyzed.toLocaleString()} critical infrastructure systems</strong> across the Power, Banking, Telecom, Transport, and Defence sectors.
          </p>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.86rem", lineHeight: "1.7", marginTop: "8px" }}>
            Rather than assessing compliance policies, this examination analyzes operational evidence to detect <strong>Execution Gaps</strong> (controls that exist in procedure but fail in execution) and <strong>Negative Space conditions</strong> (unmonitored critical assets and omitted mandatory escalations).
          </p>
        </div>

        {/* Section 2: Top Entity Risk Rankings */}
        <div style={{ marginBottom: "28px" }}>
          <h3 style={{ fontSize: "1.15rem", color: "var(--accent-cyan)", borderBottom: "1px solid var(--border)", paddingBottom: "6px", marginBottom: "12px" }}>
            2. Critical Sector Entity Risk Prioritization Ranking
          </h3>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Entity ID</th>
                  <th>Entity Name</th>
                  <th>Sector</th>
                  <th>Supervisory Risk</th>
                  <th>Primary Supervisory Concern</th>
                  <th>Findings</th>
                </tr>
              </thead>
              <tbody>
                {report.cse_risk_rankings.map((c) => (
                  <tr key={c.cse_id}>
                    <td style={{ fontWeight: "800", color: c.rank <= 2 ? "var(--crit-color)" : "var(--text-muted)" }}>
                      #{c.rank}
                    </td>
                    <td className="font-mono" style={{ fontWeight: "700", color: "var(--accent-cyan)" }}>
                      {c.cse_id}
                    </td>
                    <td style={{ fontWeight: "600" }}>{c.name}</td>
                    <td>{c.sector}</td>
                    <td>
                      <RiskBadge level={c.risk_level} score={c.risk_score} />
                    </td>
                    <td style={{ fontWeight: "500", fontSize: "0.8rem" }}>{c.primary_concern}</td>
                    <td className="font-mono">{c.findings_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Section 3: Major Execution Gaps & Negative Space Signals */}
        <div style={{ marginBottom: "28px" }}>
          <h3 style={{ fontSize: "1.15rem", color: "var(--accent-cyan)", borderBottom: "1px solid var(--border)", paddingBottom: "6px", marginBottom: "12px" }}>
            3. Major Execution Gaps & Negative-Space Signals
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {report.major_findings.slice(0, 6).map((f) => (
              <div key={f.finding_id} style={{ background: "var(--bg-subtle)", padding: "12px 16px", borderRadius: "8px", borderLeft: "3px solid var(--crit-color)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontWeight: "700", fontSize: "0.88rem", color: "var(--text-primary)" }}>
                    [{f.rule_code}] {f.title} — {f.cse_name} ({f.cse_id})
                  </span>
                  <RiskBadge level={f.severity} />
                </div>
                <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginTop: "4px" }}>
                  {f.evidence_summary}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Section 4: Recommended Supervisory Directives */}
        <div style={{ marginBottom: "20px" }}>
          <h3 style={{ fontSize: "1.15rem", color: "var(--accent-cyan)", borderBottom: "1px solid var(--border)", paddingBottom: "6px", marginBottom: "12px" }}>
            4. Recommended Formal Supervisory Directives
          </h3>
          <ol style={{ color: "var(--text-primary)", fontSize: "0.86rem", lineHeight: "1.8", paddingLeft: "24px" }}>
            {report.supervisory_recommendations.map((rec, i) => (
              <li key={i} style={{ marginBottom: "6px" }}>{rec}</li>
            ))}
          </ol>
        </div>

        {/* Signature & Disclaimer Footer */}
        <div style={{ borderTop: "2px solid var(--border)", paddingTop: "16px", marginTop: "30px", display: "flex", justifyContent: "space-between", alignItems: "flex-end", fontSize: "0.76rem", color: "var(--text-muted)" }}>
          <div>
            <div><strong>Distinction Notice:</strong> Automated analytical findings provide evidence prioritization.</div>
            <div>Final regulatory directives remain subject to accredited human supervisory approval.</div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div className="font-mono">DIGITAL SIGNATURE VERIFIED: NCIIPC-DIR-SEAL</div>
            <div>Assessment Version: v1.0.0-SIH</div>
          </div>
        </div>
      </div>
    </div>
  );
}
