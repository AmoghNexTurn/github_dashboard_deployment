export const getFilteredAndSortedRepos = (repoList, searchQuery, sortType) => {
  let filtered = repoList.filter(repo =>
    repo.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  switch (sortType) {
    case "alphabetical":
      return filtered.sort((a, b) => a.name.localeCompare(b.name));
    case "reverse":
      return filtered.sort((a, b) => b.name.localeCompare(a.name));
    case "recent":
      return filtered.sort((a, b) => {
        const dateA = new Date(a.pushed_at).getTime();
        const dateB = new Date(b.pushed_at).getTime();
        return dateB - dateA;
      });
    default:
      return filtered;
  }
};