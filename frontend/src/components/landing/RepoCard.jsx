import React from 'react';

const repoCard = ({ repo, onSelect, onToggleDescription, isDescriptionVisible }) => {
  return (
    <div className="repo-card" onClick={() => onSelect(repo)}>
      <div className="repo-card-header">
        <h3>{repo.name}</h3>

        {repo.description && (
          <button
            className="desc-toggle-btn"
            onClick={(e) => onToggleDescription(e, repo.id)}
          >
            {isDescriptionVisible ? 'Hide Description' : 'Show Description'}
          </button>
        )}
      </div>

      {isDescriptionVisible && (
        <p className="repo-description-text">{repo.description}</p>
      )}

      <small className="last-updated">
        Last pushed: {new Date(repo.pushed_at).toLocaleDateString()}
      </small>
    </div>
  );
};

export default repoCard;