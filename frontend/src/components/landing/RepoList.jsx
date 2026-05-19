import React from 'react';
import RepoCard from './RepoCard';

const RepoList = ({
  filteredRepos,
  searchQuery,
  sortType,
  onSearchChange,
  onSortChange,
  onSelectRepo,
  onToggleDescription,
  visibleDescriptions
}) => {
  return (
    <>
      <div className="landing-controls">
        <div className="search-container">
          <input
            type="text"
            placeholder="Search repositories..."
            className="search-bar"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>

        <div className="filter-menu">
          <label>Sort By: </label>
          <select value={sortType} onChange={(e) => onSortChange(e.target.value)}>
            <option value="alphabetical">Alphabetical (A-Z)</option>
            <option value="reverse">Reverse Alphabetical (Z-A)</option>
            <option value="recent">Most Recent</option>
          </select>
        </div>
      </div>

      <div className="repo-list">
        {filteredRepos.length > 0 ? (
          filteredRepos.map(repo => (
            <RepoCard
              key={repo.id}
              repo={repo}
              onSelect={onSelectRepo}
              onToggleDescription={onToggleDescription}
              isDescriptionVisible={!!visibleDescriptions[repo.id]}
            />
          ))
        ) : (
          <p className="no-results">No repositories found matching "{searchQuery}"</p>
        )}
      </div>
    </>
  );
};

export default RepoList;