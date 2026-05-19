import { useState } from 'react';

export const useCompliance = (config, selectedRepo, selectedRepoOwner) => {
  const [complianceReports, setComplianceReports] = useState({});
  const [checkingPath, setCheckingPath] = useState(null);
  const [focusedCard, setFocusedCard] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [auditSelections, setAuditSelections] = useState({});

  const handleHybridCompliance = async (path) => {
    setCheckingPath(path);
    setFocusedCard(path);

    const params = new URLSearchParams({
      owner: selectedRepoOwner,
      repo: selectedRepo,
      branch: 'main',
      path: path,
      github_token: config.token || '',
    });

    try {
      const response = await fetch(
        `/api/check-hybrid?${params.toString()}`,
        { method: 'POST' }
      );

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Hybrid Check Error:', errorData.detail);
        alert(`Error: ${errorData.detail || 'Validation failed'}`);
        return;
      }

      const data = await response.json();

      setComplianceReports(prev => ({
        ...prev,
        [path]: data.report
      }));

      const newManualChecks = { ...auditSelections };
      Object.keys(newManualChecks).forEach(key => {
        if (key.startsWith(`${path}-`)) delete newManualChecks[key];
      });
      setAuditSelections(newManualChecks);
    } catch (error) {
      console.error('Network or parsing error:', error);
      alert('Compliance check failed. Check console for details.');
    } finally {
      setCheckingPath(null);
    }
  };

  const handleComprehensiveAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const params = new URLSearchParams({
        owner: selectedRepoOwner,
        repo: selectedRepo,
        branch: 'main',
        github_token: config.token || '',
      });
      params.append('analysis_types', 'readme');

      const response = await fetch(
        `/api/analyze-repo/specific?${params.toString()}`,
        { method: 'POST' }
      );

      const data = await response.json();
      setAiAnalysis(data.result.readme);
    } catch (error) {
      console.error('README Analysis failed:', error);
      alert('Analysis failed. Please check the console.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAuditChange = (folder, check, value) => {
    setAuditSelections(prev => ({
      ...prev,
      [`${folder}-${check}`]: value
    }));
  };

  const handlePushToReview = () => {
    const currentReport = complianceReports[focusedCard];
    if (!currentReport) return;

    const newSelections = { ...auditSelections };

    const flaggedItems = currentReport.results.map(item => {
      const auditKey = `${focusedCard}-${item.check}`;
      let apiStatus = item.passed === true ? 'yes' : 'no';
      if (item.passed === 'inconclusive') apiStatus = 'inconclusive';
      const currentStatus = auditSelections[auditKey] || apiStatus;
      newSelections[auditKey] = currentStatus;

      return {
        folder: focusedCard,
        check: item.check,
        status: currentStatus,
        message: item.message
      };
    }).filter(item => item.status === 'no' || item.status === 'inconclusive');

    if (flaggedItems.length === 0) {
      alert('No items marked for review!');
      return;
    }

    setAuditSelections(newSelections);
    console.log('Flagged for Further Review:', flaggedItems);
    localStorage.setItem('pending_reviews', JSON.stringify(flaggedItems));
    alert(`${flaggedItems.length} items pushed to further review.`);
  };

  const closeSidePanel = () => setFocusedCard(null);
  const closeAiAnalysis = () => setAiAnalysis(null);

  const flaggedCount = Object.values(auditSelections).filter(
    v => v === 'no' || v === 'inconclusive'
  ).length;

  return {
    complianceReports,
    checkingPath,
    focusedCard,
    setFocusedCard,
    aiAnalysis,
    isAnalyzing,
    auditSelections,
    handleHybridCompliance,
    handleComprehensiveAnalysis,
    handleAuditChange,
    handlePushToReview,
    closeSidePanel,
    closeAiAnalysis,
    flaggedCount
  };
};
