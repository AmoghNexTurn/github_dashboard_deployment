import React from 'react';

const ArchitectureView = ({ imageUrl, repoName, onBack, handleGenerateDiagram, isGenerating}) => {
  return (
    <div className="review-center"> {/* Reuse review-center padding/bg */}
      <div className="dashboard-header-container">
        <button className="back-btn" onClick={onBack}>
          ← Back to Dashboard
        </button>
        <div className="header-main-content">
          <div className="header-title-row">
            <h2>Architecture Blueprint: {repoName}</h2>
          </div>
          <div className="header-actions-row">
            {/* REFRESH BUTTON */}
            <button 
              className="architecture-btn" 
              onClick={() => handleGenerateDiagram(true)} 
              disabled={isGenerating}
              // style={{ background: '#334155' }}
            >
              {isGenerating ? "⏳ Refreshing..." : "🔄 Re-scan Repo"}
            </button>

            {imageUrl && (
              <a href={imageUrl} download={`${repoName}_architecture.png`} style={{ textDecoration: 'none' }}>
                <button className="architecture-btn">
                  📥 Download PNG
                </button>
              </a>
            )}
          </div>
        </div>
      </div>

      <div className="diagram-full-container">
        {!imageUrl ? (
          <div className="loading-text">Generating technical diagram...</div>
        ) : (
          <img src={imageUrl} alt="Architecture" className="diagram-large-image" />
        )}
      </div>
    </div>
  );
};

export default ArchitectureView;