import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import RiskBadge from "../components/RiskBadge";
import EvidenceModal from "../components/EvidenceModal";
import ReviewModal from "../components/ReviewModal";

export default function FindingsCentral({ onSelectCase, onSelectCSE }) {
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState("");
  const [severityFilter, setSeverityFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [reviewFinding, setReviewFinding] = useState(null);

  const loadFindings = async () => {
    setLoading(true);
    try {
      const params = { limit: 150 };
      if (categoryFilter) params.category = categoryFilter;
      if (severityFilter) params.severity = severityFilter;
      if (statusFilter) params.status = statusFilter;
      const res = await api.getFindings(params);
      setFindings(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFindings();
  }, [categoryFilter, severityFilter, statusFilter]);

  const handleReviewSave = async (findingId, payload) => {
    await api.reviewFinding(findingId, payload);
    await loadFindings();
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-title-group">
          <h2>Supervisory Findings Central Repository</h2>
          <p className="page-description">
            Comprehensive catalog of all algorithmic signals, execution gaps, and negative space detections.
            Every item includes evidence thresholds and supports examiner sign-off.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ marginBottom: "20px", padding: "14px 20px" }}>
        <div style={{ display: "flex", gap: "14px", alignItems: "center", flexWrap: "wrap" }}>
          <div style={{ width: "200px" }}>
            <select
              className="form-select"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              <option value="">All Categories</option>
              <option value="EXECUTION_GAP">Execution Gaps (EG)</option>
              <option value="NEGATIVE_SPACE">Negative Space (NS)</option>
              <option value="ANOMALY">ML Operational Anomalies</option>
              <option value="PEER_DEVIATION">Peer Deviations</option>
            </select>
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

          <div style={{ width: "180px" }}>
            <select
              className="form-select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All Review Statuses</option>
              <option value="NEW">New (Unreviewed)</option>
              <option value="ACCEPTED">Accepted Finding</option>
              <option value="REJECTED">Rejected Finding</option>
              <option value="FALSE_POSITIVE">False Positive</option>
            </select>
          </div>

          {(categoryFilter || severityFilter || statusFilter) && (
            <button
              className="btn btn-sm btn-secondary"
              onClick={() => {
                setCategoryFilter("");
                setSeverityFilter("");
                setStatusFilter("");
              }}
            >
              Reset Filters
            </button>
          )}

          <div style={{ marginLeft: "auto", fontSize: "0.8rem", color: "var(--text-secondary)" }}>
            Showing <strong>{findings.length}</strong> findings
          </div>
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <div style={{ textAlign: "center", padding: "60px 0", color: "var(--text-secondary)" }}>
          Loading findings...
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Rule Code</th>
                <th>Finding ID</th>
                <th>Entity</th>
                <th>Finding Title</th>
                <th>Severity</th>
                <th>Confidence</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {findings.map((f) => (
                <tr key={f.finding_id}>
                  <td>
                    <span className="badge badge-medium" style={{ fontFamily: "var(--font-mono)" }}>
                      {f.rule_code}
                    </span>
                  </td>
                  <td className="font-mono" style={{ fontSize: "0.76rem", color: "var(--text-secondary)" }}>
                    {f.finding_id}
                  </td>
                  <td className="font-mono" style={{ fontWeight: "700", color: "var(--accent-cyan)", cursor: "pointer" }} onClick={() => onSelectCSE(f.cse_id)}>
                    {f.cse_id} ↗
                  </td>
                  <td style={{ fontWeight: "600", maxWidth: "320px" }}>
                    {f.title}
                  </td>
                  <td>
                    <RiskBadge level={f.severity} />
                  </td>
                  <td>
                    <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>
                      {f.confidence}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${f.status === "ACCEPTED" ? "badge-critical" : (f.status === "FALSE_POSITIVE" ? "badge-medium" : "badge-low")}`}>
                      {f.status}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: "flex", gap: "6px" }}>
                      <button
                        className="btn btn-sm btn-secondary"
                        onClick={() => setSelectedFinding(f)}
                      >
                        Evidence 🔍
                      </button>
                      <button
                        className="btn btn-sm btn-primary"
                        onClick={() => setReviewFinding(f)}
                      >
                        Triage ✍️
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Evidence Modal */}
      {selectedFinding && (
        <EvidenceModal
          finding={selectedFinding}
          onClose={() => setSelectedFinding(null)}
          onOpenCase={(cid) => {
            setSelectedFinding(null);
            onSelectCase(cid);
          }}
        />
      )}

      {/* Review Modal */}
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
