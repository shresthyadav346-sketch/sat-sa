import React from "react";

export default function WorkflowTimeline({ stages = {} }) {
  const steps = [
    { key: "alert", label: "1. Alert Ingestion", default: true },
    { key: "case", label: "2. Case Created", default: true },
    { key: "investigation", label: "3. Investigation", default: false },
    { key: "escalation", label: "4. Escalation", default: false },
    { key: "resolution", label: "5. Resolution", default: true },
    { key: "closure", label: "6. Formal Closure", default: true },
  ];

  return (
    <div className="workflow-pipeline">
      {steps.map((step, idx) => {
        const isPresent = stages[step.key] !== undefined ? stages[step.key] : step.default;
        const nextStep = steps[idx + 1];
        const nextPresent = nextStep ? (stages[nextStep.key] !== undefined ? stages[nextStep.key] : nextStep.default) : true;
        const connectorBroken = !isPresent || !nextPresent;

        return (
          <React.Fragment key={step.key}>
            <div className="workflow-step">
              <div className={`step-node ${isPresent ? "node-success" : "node-missing"}`}>
                {isPresent ? "✓" : "✗"}
              </div>
              <span className="step-title">{step.label}</span>
              <span className="step-status" style={{ color: isPresent ? "var(--low-color)" : "var(--crit-color)" }}>
                {isPresent ? "Recorded" : "MISSING"}
              </span>
            </div>
            {idx < steps.length - 1 && (
              <div
                className={`step-connector ${connectorBroken ? "connector-broken" : "connector-active"}`}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}
