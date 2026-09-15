import React from "react";

export default function Navbar({ activeTab, onTabChange, onOpenPresentation, onOpenDemoTour, onReanalyze, isReanalyzing }) {
  const navItems = [
    { id: "dashboard", label: "Executive Dashboard" },
    { id: "ranking", label: "CSE Ranking" },
    { id: "review-queue", label: "Review Queue" },
    { id: "negative-space", label: "Negative Space" },
    { id: "peer-benchmarks", label: "Peer Benchmarks" },
    { id: "trends", label: "Trends" },
    { id: "findings", label: "Findings Central" },
    { id: "audit-log", label: "Audit Log" },
    { id: "reports", label: "Supervisory Report" },
  ];

  return (
    <>
      <nav className="navbar">
        <div className="brand-section">
          <div className="brand-logo cyber-glow">
            <span className="logo-text">SA</span>
            <div className="logo-corner-accent"></div>
          </div>
          <div className="brand-info">
            <h1>
              <span className="brand-title-gradient">SAT-SA</span>
            </h1>
          </div>
        </div>

        <ul className="nav-links">
          {navItems.map((item) => (
            <li key={item.id}>
              <button
                className={`nav-btn ${activeTab === item.id || (item.id === "ranking" && activeTab.startsWith("cse-")) ? "active" : ""}`}
                onClick={() => onTabChange(item.id)}
              >
                <span>{item.label}</span>
              </button>
            </li>
          ))}
        </ul>

        <div className="nav-actions">
          <div className="offline-pill" title="Cryptographically locked offline air-gapped system">
            <span className="live-radar-dot"></span>
            <span className="offline-pill-text">AIR-GAPPED DEFENSE</span>
          </div>
          <button className="btn btn-sm btn-accent cyber-btn" onClick={onOpenPresentation} title="Open 5-slide presentation deck">
            5 Slides
          </button>
          <button
            className="btn btn-sm btn-primary cyber-btn"
            onClick={onReanalyze}
            disabled={isReanalyzing}
            title="Execute pipeline across all telemetry"
          >
            {isReanalyzing ? "Analyzing..." : "Re-Analyze"}
          </button>
        </div>
      </nav>
    </>
  );
}
