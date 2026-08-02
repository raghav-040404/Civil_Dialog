import api from './api';
import { USE_MOCK } from '../utils/constants';
import { mockLogin, mockRegister } from './mockData';

export const authService = {
  async login(credentials) {
    if (USE_MOCK) return mockLogin(credentials.email, credentials.password);
    const { data } = await api.post('/api/auth/login', credentials);
    return data;
  },

  async register(userData) {
    if (USE_MOCK) return mockRegister(userData);
    const { data } = await api.post('/api/auth/register', userData);
    return data;
  },

  async logout() {
    if (USE_MOCK) return Promise.resolve();
    await api.post('/api/auth/logout');
  },

  async refreshToken(refreshToken) {
    const { data } = await api.post('/api/auth/refresh', { refresh_token: refreshToken });
    return data;
  },

  async getProfile() {
    if (USE_MOCK) {
      const { tokenStorage } = await import('../utils/tokenStorage');
      return tokenStorage.getUser();
    }
    const { data } = await api.get('/api/auth/me');
    return data;
  },
};

export default authService;
