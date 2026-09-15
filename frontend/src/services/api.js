/**
 * SAT-SA Frontend API Client.
 * Connects to the local FastAPI backend.
 * Guaranteed 100% offline-first.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  };

  try {
    const res = await fetch(url, config);
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed with status ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Dashboard & Trends
  getDashboardSummary: () => request("/dashboard/summary"),
  getTrends: () => request("/trends"),

  // CSEs
  getCSESummaries: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/cses${query ? `?${query}` : ""}`);
  },
  getCSEDetail: (cseId) => request(`/cses/${cseId}`),
  getCSEFindings: (cseId) => request(`/cses/${cseId}/findings`),
  getCSEAssets: (cseId) => request(`/cses/${cseId}/assets`),

  // Review Queue & Cases
  getReviewQueue: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/review-queue${query ? `?${query}` : ""}`);
  },
  getCaseDetail: (caseId) => request(`/cases/${caseId}`),
  triageCase: (caseId, payload) => request(`/cases/${caseId}/triage`, {
    method: "POST",
    body: JSON.stringify(payload),
  }),

  // Negative Space
  getNegativeSpaceOverview: () => request("/negative-space"),
  getCSENegativeSpace: (cseId) => request(`/negative-space/${cseId}`),

  // Peer Comparison
  getPeerComparison: (cseIds = "") => {
    const query = cseIds ? `?cse_ids=${encodeURIComponent(cseIds)}` : "";
    return request(`/peer-comparison${query}`);
  },

  // Findings
  getFindings: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/findings${query ? `?${query}` : ""}`);
  },
  getFindingDetail: (findingId) => request(`/findings/${findingId}`),
  reviewFinding: (findingId, payload) => request(`/findings/${findingId}/review`, {
    method: "POST",
    body: JSON.stringify(payload),
  }),

  // Audit Logs & Hash Chain (Private Blockchain)
  getAuditLogs: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/audit-log${query ? `?${query}` : ""}`);
  },
  getAuditChain: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/audit/chain${query ? `?${query}` : ""}`);
  },
  verifyAuditChain: () => request("/audit/verify"),
  simulateAuditTamper: (payload = {}) => request("/audit/simulate-tamper", {
    method: "POST",
    body: JSON.stringify(payload),
  }),
  repairAuditTamper: (blockIndex) => request(`/audit/repair-tamper?block_index=${blockIndex}`, {
    method: "POST",
  }),

  // Reports
  generateReport: (payload) => request("/reports/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  }),

  // Ingestion & Pipeline
  triggerReanalysis: (note = "") => request("/datasets/reanalyze", {
    method: "POST",
    body: JSON.stringify({ user: "supervisory_examiner_1", note }),
  }),
  regenerateData: (numCses = 45) => request(`/datasets/regenerate?num_cses=${numCses}`, {
    method: "POST",
  }),
};
