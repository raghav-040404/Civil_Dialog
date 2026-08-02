import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { FiMenu, FiMoon, FiSun, FiBell } from 'react-icons/fi';
import Sidebar, { MobileSidebar } from '../components/common/Sidebar';
import Avatar from '../components/ui/Avatar';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { NAV_ITEMS } from '../utils/constants';

export default function DashboardLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user } = useAuth();
  const { darkMode, toggleDarkMode } = useTheme();

  return (
    <div className="flex min-h-screen bg-surface dark:bg-surface-dark">
      <Sidebar items={NAV_ITEMS} />
      <MobileSidebar items={NAV_ITEMS} isOpen={mobileOpen} onClose={() => setMobileOpen(false)} />

      <div className="flex-1 flex flex-col min-w-0">
        <header className="sticky top-0 z-40 glass border-b border-gray-200/50 dark:border-gray-700/50 px-4 sm:px-6 h-16 flex items-center justify-between">
          <button
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            onClick={() => setMobileOpen(true)}
          >
            <FiMenu size={20} />
          </button>

          <div className="flex-1" />

          <div className="flex items-center gap-2 sm:gap-4">
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              aria-label="Toggle dark mode"
            >
              {darkMode ? <FiSun size={18} /> : <FiMoon size={18} />}
            </button>
            <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 relative">
              <FiBell size={18} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
            </button>
            <Avatar src={user?.avatar} name={user?.name} size="sm" />
          </div>
        </header>

        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
