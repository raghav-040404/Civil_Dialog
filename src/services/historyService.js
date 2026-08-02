import api from './api';
import { USE_MOCK } from '../utils/constants';
import { mockHistory } from './mockData';

let localHistory = [...mockHistory];

export const historyService = {
  async getHistory({ search = '', filter = 'all', page = 1, limit = 10 } = {}) {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 300));
      let filtered = [...localHistory];

      if (search) {
        const q = search.toLowerCase();
        filtered = filtered.filter((item) => item.text.toLowerCase().includes(q));
      }

      if (filter === 'toxic') {
        filtered = filtered.filter((item) => item.toxicity > 0.5);
      } else if (filter === 'positive') {
        filtered = filtered.filter((item) => item.sentiment === 'Positive');
      }

      const total = filtered.length;
      const start = (page - 1) * limit;
      const items = filtered.slice(start, start + limit);

      return { items, total, page, totalPages: Math.ceil(total / limit) };
    }

    const { data } = await api.get('/api/history', { params: { search, filter, page, limit } });
    return data;
  },

  async getById(id) {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 200));
      return localHistory.find((item) => item.id === id) || null;
    }
    const { data } = await api.get(`/api/history/${id}`);
    return data;
  },

  async deleteHistory(id) {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 200));
      localHistory = localHistory.filter((item) => item.id !== id);
      return { success: true };
    }
    const { data } = await api.delete(`/api/history/${id}`);
    return data;
  },

  async saveAnalysis(analysis) {
    if (USE_MOCK) {
      const item = {
        id: `${Date.now()}`,
        ...analysis,
        createdAt: new Date().toISOString(),
      };
      localHistory.unshift(item);
      return item;
    }
    const { data } = await api.post('/api/history', analysis);
    return data;
  },
};

export default historyService;
