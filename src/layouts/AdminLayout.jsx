import { Outlet } from 'react-router-dom';
import Sidebar, { MobileSidebar } from '../components/common/Sidebar';
import { ADMIN_NAV_ITEMS } from '../utils/constants';
import { useState } from 'react';
import { FiMenu, FiArrowLeft } from 'react-icons/fi';
import { Link } from 'react-router-dom';

export default function AdminLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-surface dark:bg-surface-dark">
      <Sidebar items={ADMIN_NAV_ITEMS} />
      <MobileSidebar items={ADMIN_NAV_ITEMS} isOpen={mobileOpen} onClose={() => setMobileOpen(false)} />

      <div className="flex-1 flex flex-col min-w-0">
        <header className="sticky top-0 z-40 glass border-b border-gray-200/50 dark:border-gray-700/50 px-4 sm:px-6 h-16 flex items-center gap-4">
          <button
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            onClick={() => setMobileOpen(true)}
          >
            <FiMenu size={20} />
          </button>
          <Link
            to="/dashboard"
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-primary-600 transition-colors"
          >
            <FiArrowLeft size={16} />
            Back to Dashboard
          </Link>
          <h1 className="text-lg font-semibold ml-auto">Admin Panel</h1>
        </header>

        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
