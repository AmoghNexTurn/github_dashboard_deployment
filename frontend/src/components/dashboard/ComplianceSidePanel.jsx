import React from 'react';

const ComplianceSidePanel = ({
  focusedCard,
  complianceReports,
  auditSelections,
  onAuditChange,
  onClose,
  onPushToReview
}) => {
  const report = complianceReports[focusedCard];

  const getHeaderIcon = () => {
    if (!report) return '[?]';
    return report.passed === report.total_checks ? '[OK]' : '[!!]';
  };

  const getPillClass = () => {
    if (!report) return '';
    const percentage = (report.passed / report.total_checks) * 100;
    if (percentage === 100) return 'perfect';
    if (percentage >= 70) return 'good';
    if (percentage >= 50) return 'warning';
    return 'critical';
  };

  return (
    <div className="side-panel">
      <div className="panel-header">
        <h3 style={{ margin: 0, color: '#000000', display: 'flex', alignItems: 'center', gap: '10px' }}>
          {getHeaderIcon()} Compliance Report: {focusedCard}

          {report && (
            <div className={`compliance-pill ${getPillClass()}`}>
              <span className="pill-text">
                {report.passed} (out of {report.total_checks})
              </span>
            </div>
          )}
        </h3>
        <button className="close-panel" onClick={onClose}>x</button>
      </div>

      <div className="panel-body">
        {report ? (
          <div className="compliance-container">
            <div className="compliance-body">
              <div className="compliance-line info">
                <p style={{ color: '#000' }}>Category: {report.category}</p>
              </div>
              <hr />

              {report.results.map((item, index) => {
                const auditKey = `${focusedCard}-${item.check}`;
                let defaultStatus =
                  item.passed === 'inconclusive'
                    ? 'inconclusive'
                    : item.passed === true
                    ? 'yes'
                    : 'no';
                const currentSelection = auditSelections[auditKey] || defaultStatus;

                return (
                  <div key={index} className="audit-item-container">
                    <div className="compliance-line heading">
                      <p>
                        <strong style={{ color: '#000' }}>{item.check}</strong>
                      </p>
                    </div>

                    <div className="audit-controls">
                      {['yes', 'no', 'inconclusive', 'na'].map(option => (
                        <label
                          key={option}
                          className={`audit-label ${option} ${currentSelection === option ? 'active' : ''}`}
                        >
                          <input
                            type="radio"
                            name={auditKey}
                            value={option}
                            checked={currentSelection === option}
                            onChange={() => onAuditChange(focusedCard, item.check, option)}
                          />
                          {option === 'na'
                            ? 'N/A'
                            : option.charAt(0).toUpperCase() + option.slice(1)}
                        </label>
                      ))}
                    </div>

                    <div className="audit-message-container">
                      {item.message.includes('. LLM:') ? (
                        <>
                          <p className="audit-message deterministic">
                            {item.message.split('. LLM:')[0]}
                          </p>
                          <p className="audit-message llm">
                            LLM: {item.message.split('. LLM:')[1]}
                          </p>
                        </>
                      ) : (
                        <p className="audit-message">{item.message}</p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <p className="loading-text">Running hybrid analysis...</p>
        )}
      </div>

      <div className="panel-footer">
        <button className="review-btn" onClick={onPushToReview}>
          Push to Further Review
        </button>
      </div>
    </div>
  );
};

export default ComplianceSidePanel;