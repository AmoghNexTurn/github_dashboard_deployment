import React from 'react';

const ReviewCenter = ({ auditSelections, complianceReports, onBack }) => {
  const flaggedEntries = Object.entries(auditSelections).filter(
    ([_, status]) => status === 'no' || status === 'inconclusive'
  );

  return (
    <div className="review-center">
      <div className="dashboard-header-container">
        <button className="back-btn" onClick={onBack}>
          Back to Dashboard
        </button>
        <h1>Review Center: Flagged Issues</h1>
      </div>

      <div className="review-table-container">
        <table className="review-table">
          <thead>
            <tr>
              <th>Folder</th>
              <th>Check Name</th>
              <th>Status</th>
              <th>Evidence / Message</th>
            </tr>
          </thead>
          <tbody>
            {flaggedEntries.map(([key, status]) => {
              const dashIndex = key.indexOf('-');
              const folder = key.substring(0, dashIndex);
              const check = key.substring(dashIndex + 1);
              const report = complianceReports[folder];
              const checkData = report?.results.find(r => r.check === check);

              return (
                <tr key={key}>
                  <td><strong>{folder}</strong></td>
                  <td>{check}</td>
                  <td>
                    <span className={`status-pill ${status}`}>
                      {status.toUpperCase()}
                    </span>
                  </td>
                  <td className="review-message-cell" style={{ color: '#000' }}>
                    {checkData?.message.includes('. LLM:') ? (
                      <div className="split-message">
                        <div className="det-part">
                          {checkData.message.split('. LLM:')[0]}
                        </div>
                        <div className="llm-part">
                          LLM: {checkData.message.split('. LLM:')[1]}
                        </div>
                      </div>
                    ) : (
                      checkData?.message
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {flaggedEntries.length === 0 && (
          <div className="empty-state">
            <p>No issues flagged for review.</p>
            <p>---------------</p>
            <p>Please go and Run the compliance</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewCenter;