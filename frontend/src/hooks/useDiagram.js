import { useState } from 'react';

export const useDiagram = (config, selectedRepo, selectedRepoOwner) => {
  const [diagramUrl, setDiagramUrl] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateDiagram = async (refresh = false) => {
    // CRITICAL FIX: Clear the old image before starting a new request
    setDiagramUrl(null);

    setIsGenerating(true);

    const params = new URLSearchParams({
      owner: selectedRepoOwner,
      repo: selectedRepo,
      branch: 'main',
      refresh: refresh,
      github_token: config.token || '',
    });

    try {
      const url = `/api/diagram/architecture_diagram?${params.toString()}`;

      const response = await fetch(url, { method: 'POST' });

      if (!response.ok) throw new Error("Failed to generate diagram");

      const blob = await response.blob();
      const imageUrl = URL.createObjectURL(blob);
      setDiagramUrl(imageUrl);
    } catch (error) {
      console.error("Diagram Error:", error);
      alert("Could not generate diagram. Check backend logs.");
    } finally {
      setIsGenerating(false);
    }
  };

  const closeDiagram = () => {
    if (diagramUrl) URL.revokeObjectURL(diagramUrl);
    setDiagramUrl(null);
  };

  return { diagramUrl, isGenerating, handleGenerateDiagram, closeDiagram };
};
