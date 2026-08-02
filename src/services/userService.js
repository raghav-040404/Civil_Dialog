import api from './api';
import { USE_MOCK } from '../utils/constants';
import {
  mockAdminStats,
  mockDailyActivity,
  mockSentimentDistribution,
  mockTopToxicWords,
  mockRecentReports,
  mockUsers,
} from './mockData';

export const userService = {
  async updateProfile(updates) {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 400));
      const { tokenStorage } = await import('../utils/tokenStorage');
      const user = tokenStorage.getUser();
      const updated = { ...user, ...updates };
      tokenStorage.setUser(updated);
      return updated;
    }
    const { data } = await api.put('/api/user/profile', updates);
    return data;
  },

  async updatePassword({ currentPassword, newPassword }) {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 400));
      if (currentPassword.length < 6) throw new Error('Current password is incorrect');
      return { success: true };
    }
    const { data } = await api.put('/api/user/password', { currentPassword, newPassword });
    return data;
  },

  async uploadAvatar(file) {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 500));
      const avatarUrl = URL.createObjectURL(file);
      const { tokenStorage } = await import('../utils/tokenStorage');
      const user = tokenStorage.getUser();
      const updated = { ...user, avatar: avatarUrl };
      tokenStorage.setUser(updated);
      return updated;
    }
    const formData = new FormData();
    formData.append('avatar', file);
    const { data } = await api.post('/api/user/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async deleteAccount() {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 400));
      return { success: true };
    }
    const { data } = await api.delete('/api/user/account');
    return data;
  },

  async getSettings() {
    if (USE_MOCK) {
      return { darkMode: false, notifications: true, language: 'en' };
    }
    const { data } = await api.get('/api/user/settings');
    return data;
  },

  async updateSettings(settings) {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 300));
      return settings;
    }
    const { data } = await api.put('/api/user/settings', settings);
    return data;
  },
};

export const adminService = {
  async getStats() {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 300));
      return mockAdminStats;
    }
    const { data } = await api.get('/api/admin/stats');
    return data;
  },

  async getDailyActivity() {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 300));
      return mockDailyActivity;
    }
    const { data } = await api.get('/api/admin/activity');
    return data;
  },

  async getSentimentDistribution() {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 300));
      return mockSentimentDistribution;
    }
    const { data } = await api.get('/api/admin/sentiment');
    return data;
  },

  async getTopToxicWords() {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 300));
      return mockTopToxicWords;
    }
    const { data } = await api.get('/api/admin/toxic-words');
    return data;
  },

  async getRecentReports() {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 300));
      return mockRecentReports;
    }
    const { data } = await api.get('/api/admin/reports');
    return data;
  },

  async getUsers() {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 300));
      return mockUsers;
    }
    const { data } = await api.get('/api/admin/users');
    return data;
  },
};

export default userService;
