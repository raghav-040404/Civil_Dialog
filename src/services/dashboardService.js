import api from './api';
import { USE_MOCK } from '../utils/constants';
import { mockDashboardStats } from './mockData';

export const dashboardService = {
  async getStats() {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 300));
      return mockDashboardStats;
    }
    const { data } = await api.get('/api/dashboard/stats');
    return data;
  },

  async getRecentActivity() {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 300));
      return [
        { id: 1, action: 'Analysis completed', score: 85, time: '2 min ago' },
        { id: 2, action: 'Toxic message prevented', score: 32, time: '15 min ago' },
        { id: 3, action: 'Rewrite accepted', score: 78, time: '1 hour ago' },
      ];
    }
    const { data } = await api.get('/api/dashboard/activity');
    return data;
  },
};

export default dashboardService;
