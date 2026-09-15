import React from "react";

export default function MetricCard({ label, value, subtext, variant = "default" }) {
  let cardClass = "kpi-card cyber-card";
  let icon = "📊";

  if (variant === "critical") {
    cardClass += " kpi-critical";
    icon = "🚨";
  } else if (variant === "high") {
    cardClass += " kpi-high";
    icon = "⚠️";
  } else if (variant === "warning") {
    cardClass += " kpi-warning";
    icon = "⚡";
  } else if (variant === "success") {
    cardClass += " kpi-success";
    icon = "✨";
  }

  // Specific contextual icons
  const lower = label.toLowerCase();
  if (lower.includes("entities")) icon = "🏛️";
  else if (lower.includes("alerts")) icon = "📡";
  else if (lower.includes("cases")) icon = "📑";
  else if (lower.includes("assets")) icon = "🖥️";
  else if (lower.includes("execution gaps")) icon = "⚡";
  else if (lower.includes("negative space")) icon = "🌑";
  else if (lower.includes("time saved")) icon = "⏱️";

  return (
    <div className={cardClass}>
      <div className="kpi-header-row">
        <span className="kpi-label">{label}</span>
        <span className="kpi-icon-badge">{icon}</span>
      </div>
      <div className="kpi-value-container">
        <div className="kpi-value">{value}</div>
      </div>
      {subtext && <div className="kpi-sub">{subtext}</div>}
      <div className="kpi-corner-accent"></div>
    </div>
  );
}
