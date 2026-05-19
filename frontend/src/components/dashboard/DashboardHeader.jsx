import React from 'react';

const DashboardHeader = ({
  selectedRepo,
  isAnalyzing,
  flaggedCount,
  onBack,
  onAnalyze,
  onOpenReview,
  isGeneratingDiagram,
  onViewDiagram
}) => {
  return (
    <div className="dashboard-header-container">
      {/* Left Side: Back Button alone */}
      <button className="back-btn" onClick={onBack}>
        ← Back to Projects
      </button>

      {/* Right Side: Title top, Buttons bottom */}
      <div className="header-main-content">
        <div className="header-title-row">
          <h2>Dashboard: {selectedRepo}</h2>
        </div>

        <div className="header-actions-row">
          <button 
            className="architecture-btn" 
            onClick={onViewDiagram}
            disabled={isGeneratingDiagram}
          >
            {isGeneratingDiagram ? "⏳ Drawing..." : "📊 View Architecture"}
          </button>

          <button
            className="ai-analyze-btn"
            onClick={onAnalyze}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? 'Analyzing...' : '🔍 Readme Analysis'}
          </button>

          <button className="review-nav-btn" onClick={onOpenReview}>
            📋 Review Hub ({flaggedCount})
          </button>
        </div>
      </div>
    </div>
  );
};

export default DashboardHeader;