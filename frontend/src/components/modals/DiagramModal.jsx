import React from 'react';

const DiagramModal = ({ imageUrl, onClose, repoName }) => {
  if (!imageUrl) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="diagram-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Architecture: {repoName}</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <img src={imageUrl} alt="Architecture Diagram" />
        </div>
        <div className="modal-footer">
          <a href={imageUrl} download={`${repoName}_architecture.png`}>
            <button className="download-btn">📥 Download PNG</button>
          </a>
        </div>
      </div>
    </div>
  );
};

export default DiagramModal;