// import React from 'react';

// const FolderCard = ({ name, info, checkingPath, onRunCompliance }) => {
//   const resolvedPath = name === 'Root' ? '.' : name;

//   return (
//     <div className={`card ${info.status}`}>
//       <div className="card-header">
//         <h2>{name === 'Root' ? 'Root' : name}</h2>
//         <button
//           className="compliance-btn"
//           onClick={() => onRunCompliance(resolvedPath)}
//           disabled={checkingPath === name}
//         >
//           {checkingPath === name ? 'Checking...' : 'Show Compliance'}
//         </button>
//       </div>

//       <ul className="item-list">
//         {info.children.slice(0, 8).map((child, i) => (
//           <li
//             key={i}
//             className={
//               child.type === 'tree' && child.children && child.children.length > 0
//                 ? 'has-tooltip'
//                 : ''
//             }
//           >
//             <span className="item-icon">
//               {child.type === 'tree' ? '[D]' : '[F]'}
//             </span>
//             <span className="item-name">{child.name}</span>

//             {child.type === 'tree' && child.children && child.children.length > 0 && (
//               <div className="tooltip">
//                 <strong>Sub-folder Contents:</strong>
//                 <ul>
//                   {child.children.slice(0, 10).map((sub, j) => (
//                     <li key={j}>- {sub.name}</li>
//                   ))}
//                   {child.children.length > 10 && (
//                     <li style={{ fontStyle: 'italic', color: '#adb5bd' }}>
//                       ...and {child.children.length - 10} more
//                     </li>
//                   )}
//                 </ul>
//               </div>
//             )}
//           </li>
//         ))}
//       </ul>

//       <div className="activity" />
//     </div>
//   );
// };

// export default FolderCard;

import React from 'react';

const formatDate = (isoString) => {
  if (!isoString) return null;
  const date = new Date(isoString);
  if (isNaN(date.getTime())) return null;

  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }) + ' at ' + date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit'
  });
};

const FolderCard = ({ name, info, checkingPath, onRunCompliance, isLatest }) => {
  const resolvedPath = name === 'Root' ? '.' : name;
  const formattedDate = formatDate(info.lastUpdated);

  return (
    <div className={`card ${info.status} ${isLatest ? 'latest-glow' : ''}`}>
      <div className="card-header">
        <h2>{name}</h2>
        <button
          className="compliance-btn"
          onClick={() => onRunCompliance(resolvedPath)}
          disabled={checkingPath === name}
        >
          {checkingPath === name ? 'Checking...' : 'Show Compliance'}
        </button>
      </div>

      <ul className="item-list">
        {info.children.slice(0, 8).map((child, i) => (
          <li
            key={i}
            className={
              child.type === 'tree' && child.children && child.children.length > 0
                ? 'has-tooltip'
                : ''
            }
          >
            <span className="item-icon">
              {child.type === 'tree' ? '[D]' : '[F]'}
            </span>
            <span className="item-name">{child.name}</span>

            {child.type === 'tree' && child.children && child.children.length > 0 && (
              <div className="tooltip">
                <strong>Sub-folder Contents:</strong>
                <ul>
                  {child.children.slice(0, 10).map((sub, j) => (
                    <li key={j}>- {sub.name}</li>
                  ))}
                  {child.children.length > 10 && (
                    <li style={{ fontStyle: 'italic', color: '#adb5bd' }}>
                      ...and {child.children.length - 10} more
                    </li>
                  )}
                </ul>
              </div>
            )}
          </li>
        ))}
      </ul>

      <div className="activity">
        {formattedDate ? (
          <small>Last updated: {formattedDate}</small>
        ) : (
          <small className="activity-unavailable">Last updated: unavailable</small>
        )}
      </div>
    </div>
  );
};

export default FolderCard;