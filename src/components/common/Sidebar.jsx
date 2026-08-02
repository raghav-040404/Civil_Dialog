import { NavLink, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  FiGrid,
  FiEdit3,
  FiClock,
  FiUser,
  FiSettings,
  FiLogOut,
  FiShield,
  FiChevronLeft,
  FiChevronRight,
} from 'react-icons/fi';
import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import Avatar from '../ui/Avatar';

const ICONS = {
  dashboard: FiGrid,
  analyzer: FiEdit3,
  history: FiClock,
  profile: FiUser,
  settings: FiSettings,
  users: FiUser,
  reports: FiShield,
};

export default function Sidebar({ items, collapsed: controlledCollapsed, onCollapsedChange }) {
  const [internalCollapsed, setInternalCollapsed] = useState(false);
  const collapsed = controlledCollapsed ?? internalCollapsed;
  const setCollapsed = onCollapsedChange ?? setInternalCollapsed;
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 260 }}
      className="hidden lg:flex flex-col h-screen glass border-r border-gray-200/50 dark:border-gray-700/50 sticky top-0"
    >
      <div className="p-4 flex items-center justify-between border-b border-gray-200/50 dark:border-gray-700/50">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
              <span className="text-white font-bold text-sm">CD</span>
            </div>
            <span className="font-bold gradient-text">CivilDialog</span>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          {collapsed ? <FiChevronRight size={18} /> : <FiChevronLeft size={18} />}
        </button>
      </div>

      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {items.map(({ path, label, icon }) => {
          const Icon = ICONS[icon];
          return (
            <NavLink
              key={path}
              to={path}
              end={path === '/dashboard' || path === '/admin'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/25'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`
              }
            >
              <Icon size={20} />
              {!collapsed && <span>{label}</span>}
            </NavLink>
          );
        })}

        {isAdmin && (
          <NavLink
            to="/admin"
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                isActive
                  ? 'bg-amber-600 text-white'
                  : 'text-amber-600 dark:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-900/20'
              }`
            }
          >
            <FiShield size={20} />
            {!collapsed && <span>Admin Panel</span>}
          </NavLink>
        )}
      </nav>

      <div className="p-3 border-t border-gray-200/50 dark:border-gray-700/50">
        {!collapsed && user && (
          <div className="flex items-center gap-3 px-3 py-2 mb-2">
            <Avatar src={user.avatar} name={user.name} size="sm" />
            <div className="overflow-hidden">
              <p className="text-sm font-medium truncate">{user.name}</p>
              <p className="text-xs text-gray-500 truncate">{user.email}</p>
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
        >
          <FiLogOut size={20} />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </motion.aside>
  );
}

export function MobileSidebar({ items, isOpen, onClose }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  if (!isOpen) return null;

  return (
    <div className="lg:hidden fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <motion.div
        initial={{ x: -280 }}
        animate={{ x: 0 }}
        className="absolute left-0 top-0 bottom-0 w-[280px] glass flex flex-col"
      >
        <nav className="flex-1 p-4 space-y-1">
          {items.map(({ path, label, icon }) => {
            const Icon = ICONS[icon];
            return (
              <NavLink
                key={path}
                to={path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium ${
                    isActive ? 'bg-primary-600 text-white' : 'text-gray-600 dark:text-gray-400'
                  }`
                }
              >
                <Icon size={20} />
                {label}
              </NavLink>
            );
          })}
        </nav>
        <div className="p-4 border-t">
          <button
            onClick={async () => { await logout(); navigate('/login'); onClose(); }}
            className="flex items-center gap-3 w-full px-3 py-2.5 text-red-600"
          >
            <FiLogOut size={20} /> Logout
          </button>
        </div>
      </motion.div>
    </div>
  );
}
