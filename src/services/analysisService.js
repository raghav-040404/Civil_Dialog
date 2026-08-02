import api from './api';
import { USE_MOCK } from '../utils/constants';
import { mockAnalyze } from './mockData';

export const analysisService = {
  async analyze(text) {
    if (!text?.trim()) {
      return {
        toxicity: 0,
        sentiment: 'Neutral',
        fallacies: [],
        highlightedText: [],
        rewrite: '',
        score: 100,
      };
    }

    if (USE_MOCK) return mockAnalyze(text);

    const { data } = await api.post('/api/analyze', { text });
    return data;
  },
};

export default analysisService;
