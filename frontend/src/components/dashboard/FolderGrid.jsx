import React, { useMemo } from 'react';
import FolderCard from './FolderCard';

const FolderGrid = ({ repoData, focusedCard, checkingPath, onRunCompliance }) => {
  const entries = repoData
    ? Object.entries(repoData).filter(([name]) => !focusedCard || name === focusedCard)
    : [];

  // Find the card with the most recent lastUpdated, excluding Root
  const latestCardName = useMemo(() => {
    if (!repoData) return null;

    const nonRootEntries = Object.entries(repoData).filter(
      ([name]) => name !== 'Root'
    );

    if (nonRootEntries.length === 0) return null;

    return nonRootEntries.reduce((latest, [name, info]) => {
      if (!info.lastUpdated) return latest;
      if (!latest) return name;
      return new Date(info.lastUpdated) > new Date(repoData[latest].lastUpdated)
        ? name
        : latest;
    }, null);
  }, [repoData]);

  return (
    <div className={focusedCard ? 'solo-card' : 'grid'}>
      {entries.map(([name, info]) => (
        <FolderCard
          key={name}
          name={name}
          info={info}
          checkingPath={checkingPath}
          onRunCompliance={onRunCompliance}
          isLatest={name === latestCardName}
        />
      ))}
    </div>
  );
};

export default FolderGrid;