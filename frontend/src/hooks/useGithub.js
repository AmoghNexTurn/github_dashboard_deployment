// import { useState } from 'react';
// import { getFilteredAndSortedRepos } from '../utils/sorting';

// export const useGitHub = () => {
//   const [config, setConfig] = useState({ token: '', owner: '' });
//   const [isConnected, setIsConnected] = useState(false);
//   const [searchQuery, setSearchQuery] = useState('');
//   const [sortType, setSortType] = useState('alphabetical');
//   const [repoList, setRepoList] = useState([]);
//   const [selectedRepo, setSelectedRepo] = useState(null);
//   const [repoData, setRepoData] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [visibleDescriptions, setVisibleDescriptions] = useState({});

//   const handleConnect = () => {
//     if (!config.token || !config.owner) {
//       alert('Please enter both Owner name and Personal Access Token.');
//       return;
//     }

//     setLoading(true);
//     fetch(`https://api.github.com/users/${config.owner}/repos`, {
//       headers: { Authorization: `token ${config.token}` }
//     })
//       .then(res => {
//         if (!res.ok) throw new Error('Unauthorized or User not found');
//         return res.json();
//       })
//       .then(data => {
//         setRepoList(data);
//         setIsConnected(true);
//         setLoading(false);
//       })
//       .catch(err => {
//         alert(err.message);
//         setLoading(false);
//       });
//   };

//   const handleSelectRepo = async (repoName) => {
//     setLoading(true);
//     setSelectedRepo(repoName);
//     try {
//       const response = await fetch(
//         `http://localhost:8000/api/tree?owner=${config.owner}&repo=${repoName}&token=${config.token}`
//       );
//       const data = await response.json();

//       const processed = {
//         Root: {
//           status: 'success',
//           children: data.tree,
//           lastUpdated: data.tree.length > 0 ? data.tree[0].last_modified : ''
//         }
//       };

//       data.tree.forEach(node => {
//         if (node.type === 'tree') {
//           processed[node.name] = {
//             status: node.status || 'success',
//             children: node.children || [],
//             lastUpdated: node.last_modified || ''
//           };
//         }
//       });

//       setRepoData(processed);
//       setLoading(false);
//     } catch (error) {
//       console.error('Error loading dashboard:', error);
//       setLoading(false);
//     }
//   };

//   const handleLogout = () => {
//     setIsConnected(false);
//   };

//   const handleBackToProjects = (extraResets = () => {}) => {
//     setSelectedRepo(null);
//     setRepoData(null);
//     setSearchQuery('');
//     extraResets();
//   };

//   const toggleDescription = (e, repoId) => {
//     e.stopPropagation();
//     setVisibleDescriptions(prev => ({
//       ...prev,
//       [repoId]: !prev[repoId]
//     }));
//   };

//   const filteredAndSortedRepos = getFilteredAndSortedRepos(repoList, searchQuery, sortType);

//   return {
//     config,
//     setConfig,
//     isConnected,
//     searchQuery,
//     setSearchQuery,
//     sortType,
//     setSortType,
//     repoList,
//     selectedRepo,
//     repoData,
//     loading,
//     visibleDescriptions,
//     handleConnect,
//     handleSelectRepo,
//     handleLogout,
//     handleBackToProjects,
//     toggleDescription,
//     filteredAndSortedRepos
//   };
// };

import { useState } from 'react';
import { getFilteredAndSortedRepos } from '../utils/sorting';

export const useGitHub = () => {
  const [config, setConfig] = useState({ token: '', owner: '' });
  const [isConnected, setIsConnected] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortType, setSortType] = useState('alphabetical');
  const [repoList, setRepoList] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [repoData, setRepoData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [visibleDescriptions, setVisibleDescriptions] = useState({});
  const [selectedRepoOwner, setSelectedRepoOwner] = useState(null); // add this

  const handleConnect = () => {
    if (!config.token || !config.owner) {
      alert('Please enter both Owner name and Personal Access Token.');
      return;
    }

    setLoading(true);
    fetch(`https://api.github.com/user/repos?per_page=100&affiliation=owner,collaborator,organization_member`, {
      headers: { Authorization: `token ${config.token}` }
    })
      .then(res => {
        if (!res.ok) throw new Error('Unauthorized or User not found');
        return res.json();
      })
      .then(data => {
        setRepoList(data);
        setIsConnected(true);
        setLoading(false);
      })
      .catch(err => {
        alert(err.message);
        setLoading(false);
      });
  };

  const handleSelectRepo = async (repo) => {
    setLoading(true);
    setSelectedRepo(repo.name);
    setSelectedRepoOwner(repo.owner.login); // add this

    const repoOwner = repo.owner.login;  // actual owner, not config.owner
    const repoName = repo.name;

    try {
      const response = await fetch(
        `/api/tree?owner=${repoOwner}&repo=${repoName}&token=${encodeURIComponent(config.token)}`
      );
      const data = await response.json();

      const processed = {
        Root: {
          status: 'success',
          children: data.tree.length > 0 ? data.tree[0].children || [] : [],
          lastUpdated: data.tree.length > 0 ? data.tree[0].last_modified || '' : ''
        }
      };

      data.tree.slice(1).forEach(node => {
        if (node.type === 'tree') {
          processed[node.name] = {
            status: node.status || 'success',
            children: node.children || [],
            lastUpdated: node.last_modified || ''
          };
        }
      });

      setRepoData(processed);
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard:', error);
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setIsConnected(false);
  };

  const handleBackToProjects = (extraResets = () => { }) => {
    setSelectedRepo(null);
    setRepoData(null);
    setSearchQuery('');
    extraResets();
  };

  const toggleDescription = (e, repoId) => {
    e.stopPropagation();
    setVisibleDescriptions(prev => ({
      ...prev,
      [repoId]: !prev[repoId]
    }));
  };

  const filteredAndSortedRepos = getFilteredAndSortedRepos(repoList, searchQuery, sortType);

  return {
    config,
    setConfig,
    isConnected,
    searchQuery,
    setSearchQuery,
    sortType,
    setSortType,
    repoList,
    selectedRepo,
    selectedRepoOwner,
    repoData,
    loading,
    visibleDescriptions,
    handleConnect,
    handleSelectRepo,
    handleLogout,
    handleBackToProjects,
    toggleDescription,
    filteredAndSortedRepos
  };
};
