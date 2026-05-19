import React from 'react';

const AiAnalysisModal = ({ aiAnalysis, selectedRepo, onClose }) => {
  if (!aiAnalysis) return null;

  return (
    <div className="ai-overlay">
      <div className="ai-modal">
        <div className="ai-modal-header">
          <h2>Detailed README Analysis: {selectedRepo}</h2>
          <button className="close-panel" onClick={onClose}>x</button>
        </div>

        <div className="ai-modal-body" style={{ color: '#000' }}>
          <div className="readme-score-section">
            <div className="score-circle">
              <span className="score-val">{aiAnalysis.quality_score}/10</span>
              <small>Quality</small>
            </div>
            <div className="justification-box">
              <p><strong>Analysis:</strong> {aiAnalysis.justification}</p>
            </div>
          </div>

          <div className="ai-grid">
            <div className="ai-card warning">
              <h3>Missing Sections</h3>
              <ul>
                {aiAnalysis.missing_sections.map((section, i) => (
                  <li key={i} style={{ color: '#000' }}>{section}</li>
                ))}
              </ul>
            </div>

            <div className="ai-card success">
              <h3>Top Improvements</h3>
              <ul>
                {aiAnalysis.top_improvements.map((item, i) => (
                  <li key={i} style={{ color: '#000' }}>{item}</li>
                ))}
              </ul>
            </div>
          </div>

          {aiAnalysis.pii_detected && aiAnalysis.pii_detected.length > 0 && (
            <div className="pii-banner">
              <strong>PII Detected:</strong> {aiAnalysis.pii_detected.join(', ')}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AiAnalysisModal;