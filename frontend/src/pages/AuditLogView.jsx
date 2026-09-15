import React, { useEffect, useState } from "react";
import { api } from "../services/api";

export default function AuditLogView() {
  const [blocks, setBlocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [verification, setVerification] = useState(null);
  const [actionMessage, setActionMessage] = useState(null);
  const [orderDesc, setOrderDesc] = useState(false);

  const fetchChainAndVerify = async () => {
    setLoading(true);
    try {
      const [chainData, verifyData] = await Promise.all([
        api.getAuditChain({ order: orderDesc ? "desc" : "asc", limit: 200 }),
        api.verifyAuditChain(),
      ]);
      setBlocks(chainData || []);
      setVerification(verifyData);
    } catch (err) {
      console.error("Failed to load audit chain:", err);
      setActionMessage({ type: "error", text: "Failed to connect to audit chain service." });
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    setVerifying(true);
    try {
      const verifyData = await api.verifyAuditChain();
      setVerification(verifyData);
      const chainData = await api.getAuditChain({ order: orderDesc ? "desc" : "asc", limit: 200 });
      setBlocks(chainData || []);
      if (verifyData.valid) {
        setActionMessage({
          type: "success",
          text: `Chain verification complete: All ${verifyData.total_blocks} blocks are cryptographically intact.`,
        });
      } else {
        setActionMessage({
          type: "error",
          text: `Tamper alert: Cryptographic check failed at block #${verifyData.broken_at_index}.`,
        });
      }
    } catch (err) {
      console.error(err);
      setActionMessage({ type: "error", text: "Verification request failed." });
    } finally {
      setVerifying(false);
    }
  };

  const handleSimulateTamper = async () => {
    try {
      // Tamper with block #1 if it exists, otherwise middle block
      const targetIdx = blocks.length > 1 ? 1 : 0;
      const res = await api.simulateAuditTamper({
        block_index: targetIdx,
        tampered_details: "[TAMPERED VIA DB INJECTION] Finding verdict retroactively modified by unauthorized party.",
      });
      setActionMessage({
        type: "warning",
        text: `Tamper simulated on Block #${res.tampered_block_index}! Running verification...`,
      });
      // Re-verify immediately to show judges the instant detection
      const verifyData = await api.verifyAuditChain();
      setVerification(verifyData);
      const chainData = await api.getAuditChain({ order: orderDesc ? "desc" : "asc", limit: 200 });
      setBlocks(chainData || []);
    } catch (err) {
      console.error(err);
      setActionMessage({ type: "error", text: "Failed to simulate tampering." });
    }
  };

  const handleRepairTamper = async (blockIndex) => {
    try {
      await api.repairAuditTamper(blockIndex);
      setActionMessage({
        type: "success",
        text: `Block #${blockIndex} re-hashed and restored. Re-verifying chain...`,
      });
      const verifyData = await api.verifyAuditChain();
      setVerification(verifyData);
      const chainData = await api.getAuditChain({ order: orderDesc ? "desc" : "asc", limit: 200 });
      setBlocks(chainData || []);
    } catch (err) {
      console.error(err);
      setActionMessage({ type: "error", text: "Failed to restore block hash." });
    }
  };

  useEffect(() => {
    fetchChainAndVerify();
  }, [orderDesc]);

  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: "center", padding: "80px 0" }}>
        <div style={{ fontSize: "1.3rem", color: "var(--accent-cyan)", fontWeight: "700" }}>
          Auditing SHA-256 Hash Chain...
        </div>
        <div style={{ color: "var(--text-secondary)", marginTop: "8px" }}>
          Validating parent block linkages and tamper-evident signatures
        </div>
      </div>
    );
  }

  const isChainValid = verification && verification.valid;
  const brokenIndex = verification ? verification.broken_at_index : null;

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
        <div className="page-title-group">
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
            <h2>Supervisory Audit Trail & Cryptographic Hash Chain</h2>
            <span className="badge badge-low" style={{ background: "rgba(6, 182, 212, 0.12)", color: "var(--accent-cyan)", border: "1px solid rgba(6, 182, 212, 0.3)" }}>
              Private Single-Node Blockchain
            </span>
            <span className="badge badge-medium" style={{ background: "rgba(99, 102, 241, 0.12)", color: "var(--accent-indigo)", border: "1px solid rgba(99, 102, 241, 0.3)" }}>
              Air-Gapped & Offline
            </span>
          </div>
          <p className="page-description">
            Immutable regulatory record tracking examiner decisions, finding triage actions, and report generations.
            Every supervisory action forms a SHA-256 block cryptographically linked to the previous entry, ensuring retroactive tampering is immediately detectable.
          </p>
        </div>

        {/* Action Controls */}
        <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
          <button
            className="btn btn-secondary"
            onClick={() => setOrderDesc(!orderDesc)}
            title="Toggle chronological vs reverse ordering"
            style={{ fontSize: "0.8rem", padding: "7px 14px" }}
          >
            {orderDesc ? "Order: Block N → 0" : "Order: Block 0 → N (Genesis First)"}
          </button>
          <button
            className="btn btn-secondary"
            onClick={handleSimulateTamper}
            title="Demonstrate tamper detection for judges"
            style={{ fontSize: "0.8rem", padding: "7px 14px", borderColor: "var(--high-color)", color: "var(--high-color)" }}
          >
            🧪 Simulate Tamper (Judge Demo)
          </button>
          <button
            className="btn btn-primary"
            onClick={handleVerify}
            disabled={verifying}
            style={{ fontSize: "0.85rem", padding: "8px 18px", display: "flex", alignItems: "center", gap: "6px" }}
          >
            {verifying ? "Verifying Chain..." : "🔍 Run Integrity Check"}
          </button>
        </div>
      </div>

      {/* Action Notification Toast */}
      {actionMessage && (
        <div
          style={{
            padding: "10px 16px",
            marginBottom: "16px",
            borderRadius: "var(--radius-md)",
            fontSize: "0.85rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            background: actionMessage.type === "error" ? "var(--crit-bg)" : actionMessage.type === "warning" ? "var(--high-bg)" : "var(--low-bg)",
            border: `1px solid ${actionMessage.type === "error" ? "var(--crit-border)" : actionMessage.type === "warning" ? "var(--high-border)" : "var(--low-border)"}`,
            color: actionMessage.type === "error" ? "var(--crit-color)" : actionMessage.type === "warning" ? "var(--high-color)" : "var(--low-color)",
          }}
        >
          <span>{actionMessage.text}</span>
          <button
            onClick={() => setActionMessage(null)}
            style={{ background: "none", border: "none", color: "inherit", cursor: "pointer", fontWeight: "700" }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Primary Chain Integrity Verification Banner */}
      <div
        className="card"
        style={{
          marginBottom: "24px",
          padding: "20px 24px",
          borderRadius: "var(--radius-lg)",
          background: isChainValid
            ? "linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(13, 19, 34, 0.95) 100%)"
            : "linear-gradient(135deg, rgba(244, 63, 94, 0.15) 0%, rgba(13, 19, 34, 0.95) 100%)",
          border: `1px solid ${isChainValid ? "var(--low-border)" : "var(--crit-border)"}`,
          boxShadow: isChainValid ? "0 0 24px rgba(16, 185, 129, 0.12)" : "0 0 24px rgba(244, 63, 94, 0.2)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "16px" }}>
            <div style={{ fontSize: "2.4rem", lineHeight: "1" }}>
              {isChainValid ? "✅" : "❌"}
            </div>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
                <h3 style={{ fontSize: "1.25rem", fontWeight: "800", color: isChainValid ? "var(--low-color)" : "var(--crit-color)" }}>
                  {isChainValid
                    ? `Chain Verified — ${verification.total_blocks} Blocks, No Tampering Detected`
                    : `Tamper Detected at Block #${brokenIndex}`}
                </h3>
                <span
                  className="badge"
                  style={{
                    fontSize: "0.72rem",
                    fontWeight: "700",
                    background: isChainValid ? "rgba(16, 185, 129, 0.2)" : "rgba(244, 63, 94, 0.2)",
                    color: isChainValid ? "var(--low-color)" : "var(--crit-color)",
                    border: `1px solid ${isChainValid ? "var(--low-border)" : "var(--crit-border)"}`,
                  }}
                >
                  {isChainValid ? "CRYPTOGRAPHIC INTEGRITY INTACT" : "HASH MISMATCH DETECTED"}
                </span>
              </div>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginTop: "6px", maxWidth: "800px" }}>
                {verification ? verification.details : "Running cryptographic verification..."}
              </p>
            </div>
          </div>

          {/* Quick Repair Button if Tampered */}
          {!isChainValid && brokenIndex !== null && (
            <button
              className="btn btn-primary"
              onClick={() => handleRepairTamper(brokenIndex)}
              style={{ background: "var(--accent-cyan)", border: "none", color: "var(--text-inverse)", fontWeight: "700" }}
            >
              🔧 Re-hash & Repair Block #{brokenIndex}
            </button>
          )}
        </div>

        {/* Chain Metadata Summary Cards */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "16px",
            marginTop: "18px",
            paddingTop: "16px",
            borderTop: "1px solid var(--border)",
          }}
        >
          <div>
            <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Total Ledger Blocks
            </div>
            <div className="font-mono" style={{ fontSize: "1.2rem", fontWeight: "700", color: "var(--text-primary)", marginTop: "2px" }}>
              {blocks.length} Blocks
            </div>
          </div>

          <div>
            <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Genesis Block Hash (#0)
            </div>
            <div className="font-mono" style={{ fontSize: "0.8rem", color: "var(--accent-cyan)", marginTop: "2px" }} title={blocks.length > 0 ? blocks[0].block_hash : "N/A"}>
              {blocks.length > 0 && blocks[0].block_hash ? `${blocks[0].block_hash.slice(0, 16)}...` : "0000000000000000..."}
            </div>
          </div>

          <div>
            <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Latest Head Hash
            </div>
            <div className="font-mono" style={{ fontSize: "0.8rem", color: "var(--accent-indigo)", marginTop: "2px" }} title={blocks.length > 0 ? blocks[blocks.length - 1].block_hash : "N/A"}>
              {blocks.length > 0 && blocks[blocks.length - 1].block_hash
                ? `${blocks[blocks.length - 1].block_hash.slice(0, 16)}...`
                : "N/A"}
            </div>
          </div>

          <div>
            <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Verification Algorithm
            </div>
            <div className="font-mono" style={{ fontSize: "0.85rem", fontWeight: "700", color: isChainValid ? "var(--low-color)" : "var(--crit-color)", marginTop: "2px" }}>
              SHA-256 (Canonical Payload)
            </div>
          </div>
        </div>
      </div>

      {/* Audit Blocks Table */}
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: "90px" }}>Block #</th>
              <th style={{ width: "180px" }}>Block Hash (SHA-256)</th>
              <th style={{ width: "180px" }}>Previous Hash</th>
              <th style={{ width: "150px" }}>Timestamp</th>
              <th style={{ width: "120px" }}>Examiner</th>
              <th style={{ width: "160px" }}>Supervisory Action</th>
              <th style={{ width: "110px" }}>Target</th>
              <th>Audit Payload & Directives</th>
            </tr>
          </thead>
          <tbody>
            {blocks.map((block) => {
              const isBroken = !isChainValid && block.block_index === brokenIndex;
              const isGenesis = block.block_index === 0;

              return (
                <tr
                  key={block.log_id}
                  style={{
                    backgroundColor: isBroken ? "rgba(244, 63, 94, 0.1)" : undefined,
                    borderLeft: isBroken ? "4px solid var(--crit-color)" : isGenesis ? "4px solid var(--accent-cyan)" : undefined,
                  }}
                >
                  {/* Block Index */}
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <span className="font-mono" style={{ fontWeight: "800", color: isBroken ? "var(--crit-color)" : "var(--text-primary)" }}>
                        #{block.block_index ?? block.log_id}
                      </span>
                      {isGenesis && (
                        <span className="badge" style={{ fontSize: "0.6rem", background: "rgba(6, 182, 212, 0.2)", color: "var(--accent-cyan)", padding: "1px 4px" }}>
                          GENESIS
                        </span>
                      )}
                      {isBroken && (
                        <span className="badge" style={{ fontSize: "0.6rem", background: "rgba(244, 63, 94, 0.25)", color: "var(--crit-color)", padding: "1px 4px" }}>
                          CORRUPT
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Block Hash */}
                  <td className="font-mono" style={{ fontSize: "0.75rem" }}>
                    <div
                      style={{
                        padding: "3px 6px",
                        background: "rgba(0,0,0,0.35)",
                        borderRadius: "4px",
                        color: isBroken ? "var(--crit-color)" : "var(--accent-cyan)",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                        maxWidth: "160px",
                        cursor: "pointer",
                      }}
                      title={`Full Block Hash: ${block.block_hash || 'None'}\nClick to copy`}
                      onClick={() => {
                        if (block.block_hash) {
                          navigator.clipboard.writeText(block.block_hash);
                          setActionMessage({ type: "success", text: `Copied Block #${block.block_index} hash to clipboard.` });
                        }
                      }}
                    >
                      {block.block_hash ? `${block.block_hash.slice(0, 10)}...${block.block_hash.slice(-6)}` : "None"}
                    </div>
                  </td>

                  {/* Previous Hash */}
                  <td className="font-mono" style={{ fontSize: "0.72rem" }}>
                    <div
                      style={{
                        padding: "3px 6px",
                        background: "rgba(0,0,0,0.25)",
                        borderRadius: "4px",
                        color: isGenesis ? "var(--text-muted)" : "var(--text-secondary)",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                        maxWidth: "160px",
                      }}
                      title={`Previous Hash: ${block.previous_hash || 'None'}`}
                    >
                      {isGenesis
                        ? "00000000... (Root)"
                        : block.previous_hash
                        ? `${block.previous_hash.slice(0, 8)}...${block.previous_hash.slice(-4)}`
                        : "None"}
                    </div>
                  </td>

                  {/* Timestamp */}
                  <td className="font-mono" style={{ fontSize: "0.74rem", whiteSpace: "nowrap" }}>
                    {new Date(block.timestamp).toLocaleString()}
                  </td>

                  {/* Examiner User */}
                  <td style={{ fontWeight: "700", color: "var(--accent-cyan)", fontSize: "0.82rem" }}>
                    {block.user}
                  </td>

                  {/* Action */}
                  <td>
                    <span
                      className="badge"
                      style={{
                        fontSize: "0.68rem",
                        background: "rgba(59, 130, 246, 0.15)",
                        color: "var(--accent-blue)",
                        border: "1px solid rgba(59, 130, 246, 0.3)",
                      }}
                    >
                      {block.action}
                    </span>
                  </td>

                  {/* Target Entity */}
                  <td className="font-mono" style={{ fontWeight: "700", fontSize: "0.82rem" }}>
                    <span style={{ color: "var(--text-muted)", fontSize: "0.7rem", marginRight: "4px" }}>
                      {block.entity_type}:
                    </span>
                    {block.entity_id}
                  </td>

                  {/* Audit Details */}
                  <td style={{ maxWidth: "380px", fontSize: "0.8rem", color: isBroken ? "var(--crit-color)" : "var(--text-primary)" }}>
                    {block.details}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
