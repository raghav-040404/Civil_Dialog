import { Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

import LandingPage from '../pages/LandingPage';
import DemoPage from '../pages/DemoPage';
import LoginPage from '../pages/auth/LoginPage';
import RegisterPage from '../pages/auth/RegisterPage';
import DashboardHome from '../pages/dashboard/DashboardHome';
import TextAnalyzer from '../pages/dashboard/TextAnalyzer';
import HistoryPage from '../pages/dashboard/HistoryPage';
import ProfilePage from '../pages/dashboard/ProfilePage';
import SettingsPage from '../pages/dashboard/SettingsPage';
import AdminDashboard from '../pages/admin/AdminDashboard';

import AuthLayout from '../layouts/AuthLayout';
import DashboardLayout from '../layouts/DashboardLayout';
import AdminLayout from '../layouts/AdminLayout';

import ProtectedRoute, { AdminRoute, GuestRoute } from '../components/common/ProtectedRoute';
import { AnalysisProvider } from '../context/AnalysisContext';

export default function AppRoutes() {
  return (
    <AnimatePresence mode="wait">
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/demo" element={<DemoPage />} />

        <Route element={<GuestRoute><AuthLayout /></GuestRoute>}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>

        <Route
          element={
            <ProtectedRoute>
              <AnalysisProvider>
                <DashboardLayout />
              </AnalysisProvider>
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<DashboardHome />} />
          <Route path="/dashboard/analyzer" element={<TextAnalyzer />} />
          <Route path="/dashboard/history" element={<HistoryPage />} />
          <Route path="/dashboard/profile" element={<ProfilePage />} />
          <Route path="/dashboard/settings" element={<SettingsPage />} />
        </Route>

        <Route
          element={
            <AdminRoute>
              <AdminLayout />
            </AdminRoute>
          }
        >
          <Route path="/admin" element={<AdminDashboard />} />
        </Route>

        <Route path="*" element={<LandingPage />} />
      </Routes>
    </AnimatePresence>
  );
}
