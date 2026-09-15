import React from "react";

export default function RiskBadge({ level = "LOW", score = null }) {
  const normalized = (level || "LOW").toUpperCase();
  let className = "badge-low";
  if (normalized === "CRITICAL") className = "badge-critical";
  else if (normalized === "HIGH") className = "badge-high";
  else if (normalized === "MEDIUM") className = "badge-medium";

  return (
    <span className={`badge ${className}`}>
      <span className="badge-dot" />
      {normalized} {score !== null && score !== undefined && `(${score})`}
    </span>
  );
}
