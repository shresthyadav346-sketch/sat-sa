import React, { useState } from "react";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import CseRanking from "./pages/CseRanking";
import CseDetails from "./pages/CseDetails";
import ReviewQueue from "./pages/ReviewQueue";
import CaseDetails from "./pages/CaseDetails";
import NegativeSpace from "./pages/NegativeSpace";
import PeerComparison from "./pages/PeerComparison";
import Trends from "./pages/Trends";
import FindingsCentral from "./pages/FindingsCentral";
import AuditLogView from "./pages/AuditLogView";
import ReportView from "./pages/ReportView";
import PresentationModal from "./components/PresentationModal";
import DemoTourModal from "./components/DemoTourModal";
import { api } from "./services/api";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [selectedCseId, setSelectedCseId] = useState("CSE-007");
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [queueCseFilter, setQueueCseFilter] = useState("");
  const [presentationOpen, setPresentationOpen] = useState(false);
  const [demoTourOpen, setDemoTourOpen] = useState(false);
  const [isReanalyzing, setIsReanalyzing] = useState(false);
  const [reanalysisMessage, setReanalysisMessage] = useState(null);

  const handleNavigateCSE = (cseId) => {
    setSelectedCseId(cseId);
    setActiveTab("cse-detail");
  };

  const handleNavigateCase = (caseId) => {
    setSelectedCaseId(caseId);
    setActiveTab("case-detail");
  };

  const handleNavigateQueueWithFilter = (cseId) => {
    setQueueCseFilter(cseId);
    setActiveTab("review-queue");
  };

  const handleReanalyze = async () => {
    setIsReanalyzing(true);
    setReanalysisMessage("Executing supervisory pipeline across all telemetry...");
    try {
      const res = await api.triggerReanalysis("Supervisor manual re-analysis");
      setReanalysisMessage(`Success: Analyzed ${res.results.cses_analyzed} CSEs and generated ${res.results.findings_generated} findings.`);
      setTimeout(() => setReanalysisMessage(null), 5000);
      // reload by switching tab back & forth
      const cur = activeTab;
      setActiveTab("dashboard");
      setTimeout(() => setActiveTab(cur), 50);
    } catch (err) {
      setReanalysisMessage("Pipeline execution failed: " + err.message);
      setTimeout(() => setReanalysisMessage(null), 6000);
    } finally {
      setIsReanalyzing(false);
    }
  };

  const handleDemoNav = (target) => {
    if (target === "dashboard") setActiveTab("dashboard");
    else if (target === "ranking") setActiveTab("ranking");
    else if (target === "cse-007") {
      setSelectedCseId("CSE-007");
      setActiveTab("cse-detail");
    } else if (target === "negative-space") setActiveTab("negative-space");
    else if (target === "review-queue") setActiveTab("review-queue");
    else if (target === "reports") setActiveTab("reports");
  };

  return (
    <div>
      <Navbar
        activeTab={activeTab}
        onTabChange={(tab) => {
          if (tab === "review-queue") setQueueCseFilter("");
          setActiveTab(tab);
        }}
        onOpenPresentation={() => setPresentationOpen(true)}
        onOpenDemoTour={() => setDemoTourOpen(true)}
        onReanalyze={handleReanalyze}
        isReanalyzing={isReanalyzing}
      />

      {reanalysisMessage && (
        <div style={{ background: "rgba(6, 182, 212, 0.15)", borderBottom: "1px solid var(--border-highlight)", color: "var(--accent-cyan)", padding: "8px 24px", textAlign: "center", fontSize: "0.82rem", fontWeight: "600" }}>
          {reanalysisMessage}
        </div>
      )}

      <main>
        {activeTab === "dashboard" && (
          <Dashboard
            onNavigateCSE={handleNavigateCSE}
            onNavigateTab={(tab) => {
              if (tab === "review-queue") setQueueCseFilter("");
              setActiveTab(tab);
            }}
          />
        )}

        {activeTab === "ranking" && (
          <CseRanking
            onSelectCSE={handleNavigateCSE}
          />
        )}

        {activeTab === "cse-detail" && (
          <CseDetails
            cseId={selectedCseId}
            onBack={() => setActiveTab("ranking")}
            onNavigateCase={handleNavigateCase}
            onNavigateQueue={handleNavigateQueueWithFilter}
          />
        )}

        {activeTab === "review-queue" && (
          <ReviewQueue
            initialCseFilter={queueCseFilter}
            onSelectCase={handleNavigateCase}
          />
        )}

        {activeTab === "case-detail" && (
          <CaseDetails
            caseId={selectedCaseId || "CAS-CSE-007-00001"}
            onBack={() => setActiveTab("review-queue")}
            onNavigateCSE={handleNavigateCSE}
          />
        )}

        {activeTab === "negative-space" && (
          <NegativeSpace
            onSelectCSE={handleNavigateCSE}
          />
        )}

        {activeTab === "peer-benchmarks" && (
          <PeerComparison />
        )}

        {activeTab === "trends" && (
          <Trends />
        )}

        {activeTab === "findings" && (
          <FindingsCentral
            onSelectCase={handleNavigateCase}
            onSelectCSE={handleNavigateCSE}
          />
        )}

        {activeTab === "audit-log" && (
          <AuditLogView />
        )}

        {activeTab === "reports" && (
          <ReportView />
        )}
      </main>

      {/* 5-Slide Presentation Deck Modal */}
      {presentationOpen && (
        <PresentationModal onClose={() => setPresentationOpen(false)} />
      )}

      {/* 2-Minute Demo Script Guide Modal */}
      {demoTourOpen && (
        <DemoTourModal
          onClose={() => setDemoTourOpen(false)}
          onNavigate={handleDemoNav}
        />
      )}
    </div>
  );
}
