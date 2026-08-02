import { createContext, useContext, useState, useCallback } from 'react';
import analysisService from '../services/analysisService';
import historyService from '../services/historyService';

const AnalysisContext = createContext(null);

const initialResult = {
  toxicity: 0,
  sentiment: 'Neutral',
  fallacies: [],
  highlightedText: [],
  rewrite: '',
  score: 100,
};

export function AnalysisProvider({ children }) {
  const [text, setText] = useState('');
  const [result, setResult] = useState(initialResult);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyze = useCallback(async (inputText) => {
    if (!inputText?.trim()) {
      setResult(initialResult);
      return initialResult;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await analysisService.analyze(inputText);
      setResult(data);
      return data;
    } catch (err) {
      setError(err.message || 'Analysis failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const saveToHistory = useCallback(async () => {
    if (!text.trim()) return;
    return historyService.saveAnalysis({
      text,
      score: result.score,
      sentiment: result.sentiment,
      toxicity: result.toxicity,
      fallacies: result.fallacies,
    });
  }, [text, result]);

  const reset = useCallback(() => {
    setText('');
    setResult(initialResult);
    setError(null);
  }, []);

  return (
    <AnalysisContext.Provider
      value={{ text, setText, result, loading, error, analyze, saveToHistory, reset }}
    >
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis() {
  const context = useContext(AnalysisContext);
  if (!context) throw new Error('useAnalysis must be used within AnalysisProvider');
  return context;
}

export default AnalysisContext;
