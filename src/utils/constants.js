export const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://civil-dialog-backend.onrender.com';
export const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true' || (!import.meta.env.VITE_API_URL && import.meta.env.PROD);

export const TOKEN_KEY = 'civil_dialog_token';
export const REFRESH_TOKEN_KEY = 'civil_dialog_refresh_token';
export const USER_KEY = 'civil_dialog_user';

export const DEBOUNCE_MS = 600;

export const CIVILITY_THRESHOLDS = {
  high: 70,
  medium: 40,
};

export const HIGHLIGHT_TYPES = {
  toxicity: 'highlight-toxicity',
  fallacy: 'highlight-fallacy',
  sentiment: 'highlight-sentiment',
};

export const SENTIMENT_COLORS = {
  Positive: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300',
  Neutral: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
  Negative: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',
};

export const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
  { path: '/dashboard/analyzer', label: 'Text Analyzer', icon: 'analyzer' },
  { path: '/dashboard/history', label: 'History', icon: 'history' },
  { path: '/dashboard/profile', label: 'Profile', icon: 'profile' },
  { path: '/dashboard/settings', label: 'Settings', icon: 'settings' },
];

export const ADMIN_NAV_ITEMS = [
  { path: '/admin', label: 'Overview', icon: 'dashboard' },
  { path: '/admin/users', label: 'Users', icon: 'users' },
  { path: '/admin/reports', label: 'Reports', icon: 'reports' },
];

export const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
];

export const ITEMS_PER_PAGE = 10;
