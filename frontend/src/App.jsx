import React, { useState } from 'react';
import './App.css';

import { useGitHub } from './hooks/useGithub';
import { useCompliance } from './hooks/useCompliance';
import { useDiagram } from './hooks/useDiagram';

// Landing Components
import LoginForm from './components/landing/LoginForm';
import RepoList from './components/landing/RepoList';

// Dashboard Components
import DashboardHeader from './components/dashboard/DashboardHeader';
import FolderGrid from './components/dashboard/FolderGrid';
import ComplianceSidePanel from './components/dashboard/ComplianceSidePanel';

// View/Modal Components
import AiAnalysisModal from './components/modals/AiAnalysisModal';
import ReviewCenter from './components/review/ReviewCenter';
import ArchitectureView from './components/diagram/ArchitectureView'; // Added this import

function App() {
  const [view, setView] = useState('dashboard');

  const {
    config,
    setConfig,
    isConnected,
    searchQuery,
    setSearchQuery,
    sortType,
    setSortType,
    selectedRepo,
    selectedRepoOwner,
    repoData,
    loading,
    visibleDescriptions,
    handleConnect,
    handleSelectRepo,
    handleLogout,
    handleBackToProjects,
    toggleDescription,
    filteredAndSortedRepos
  } = useGitHub();

  const {
    complianceReports,
    checkingPath,
    focusedCard,
    aiAnalysis,
    isAnalyzing,
    auditSelections,
    handleHybridCompliance,
    handleComprehensiveAnalysis,
    handleAuditChange,
    handlePushToReview,
    closeSidePanel,
    closeAiAnalysis,
    flaggedCount
  } = useCompliance(config, selectedRepo, selectedRepoOwner);

  const {
    diagramUrl,
    isGenerating,
    handleGenerateDiagram
  } = useDiagram(config, selectedRepo, selectedRepoOwner);

  // --- VIEW: LANDING PAGE ---
  if (!selectedRepo) {
    return (
      <div className="landing-page">
        <div className="user-info top-right">
          <span>Connected to: <strong>{config.owner}</strong></span>
          <button className="small-btn logout-btn" onClick={handleLogout}>
            Log Out
          </button>
        </div>

        <h1>GitHub Repo Visualizer</h1>

        {!isConnected ? (
          <LoginForm
            config={config}
            setConfig={setConfig}
            onConnect={handleConnect}
          />
        ) : (
          <RepoList
            filteredRepos={filteredAndSortedRepos}
            searchQuery={searchQuery}
            sortType={sortType}
            onSearchChange={setSearchQuery}
            onSortChange={setSortType}
            onSelectRepo={handleSelectRepo}
            onToggleDescription={toggleDescription}
            visibleDescriptions={visibleDescriptions}
          />
        )}
      </div>
    );
  }

  // --- VIEW: LOADING ---
  if (loading) {
    return (
      <div className="dashboard">
        <h1>Processing Data...</h1>
      </div>
    );
  }

  // --- VIEW: REVIEW CENTER ---
  if (view === 'review') {
    return (
      <ReviewCenter
        auditSelections={auditSelections}
        complianceReports={complianceReports}
        onBack={() => setView('dashboard')}
      />
    );
  }

  // --- VIEW: ARCHITECTURE DIAGRAM ---
  if (view === 'diagram') {
    return (
      <ArchitectureView
        imageUrl={diagramUrl}
        repoName={selectedRepo}
        onBack={() => setView('dashboard')}
        handleGenerateDiagram={handleGenerateDiagram} // Pass this if you added the Re-scan button
        isGenerating={isGenerating}
      />
    );
  }

  // --- VIEW: MAIN DASHBOARD ---
  return (
    <div className="dashboard">
      <AiAnalysisModal
        aiAnalysis={aiAnalysis}
        selectedRepo={selectedRepo}
        onClose={closeAiAnalysis}
      />

      <DashboardHeader
        selectedRepo={selectedRepo}
        isAnalyzing={isAnalyzing}
        flaggedCount={flaggedCount}
        onBack={() => handleBackToProjects(() => {
          closeSidePanel();
          setView('dashboard');
        })}
        onAnalyze={handleComprehensiveAnalysis}
        onOpenReview={() => setView('review')}
        onViewDiagram={() => {
          handleGenerateDiagram();
          setView('diagram');
        }}
        isGeneratingDiagram={isGenerating}
      />

      {/* Note: DiagramModal removed as it's replaced by ArchitectureView */}

      <div className={`dashboard-container ${focusedCard ? 'split-view' : ''}`}>
        <div className="main-content">
          <FolderGrid
            repoData={repoData}
            focusedCard={focusedCard}
            checkingPath={checkingPath}
            onRunCompliance={handleHybridCompliance}
          />
        </div>

        {focusedCard && (
          <ComplianceSidePanel
            focusedCard={focusedCard}
            complianceReports={complianceReports}
            auditSelections={auditSelections}
            onAuditChange={handleAuditChange}
            onClose={closeSidePanel}
            onPushToReview={handlePushToReview}
          />
        )}
      </div>
    </div>
  );
}

export default App;