import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiTrash2 } from 'react-icons/fi';
import Card from '../../components/ui/Card';
import Toggle from '../../components/ui/Toggle';
import Select from '../../components/ui/Select';
import Button from '../../components/ui/Button';
import Modal from '../../components/ui/Modal';
import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import userService from '../../services/userService';
import { LANGUAGES } from '../../utils/constants';

export default function SettingsPage() {
  const { darkMode, toggleDarkMode } = useTheme();
  const { logout } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState(true);
  const [language, setLanguage] = useState('en');
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    userService.getSettings().then((settings) => {
      setNotifications(settings.notifications);
      setLanguage(settings.language);
    });
  }, []);

  const handleSaveSettings = async () => {
    try {
      await userService.updateSettings({ darkMode, notifications, language });
      addToast('Settings saved', 'success');
    } catch {
      addToast('Failed to save settings', 'error');
    }
  };

  const handleDeleteAccount = async () => {
    setDeleting(true);
    try {
      await userService.deleteAccount();
      await logout();
      addToast('Account deleted', 'success');
      navigate('/');
    } catch {
      addToast('Failed to delete account', 'error');
    } finally {
      setDeleting(false);
      setDeleteModalOpen(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold">Settings</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Customize your experience</p>
      </div>

      <div className="max-w-2xl space-y-6">
        <Card>
          <h3 className="text-lg font-semibold mb-2">Appearance</h3>
          <Toggle
            label="Dark Mode"
            description="Switch between light and dark themes"
            enabled={darkMode}
            onChange={toggleDarkMode}
          />
        </Card>

        <Card>
          <h3 className="text-lg font-semibold mb-2">Notifications</h3>
          <Toggle
            label="Push Notifications"
            description="Receive alerts for analysis results and updates"
            enabled={notifications}
            onChange={setNotifications}
          />
        </Card>

        <Card>
          <h3 className="text-lg font-semibold mb-4">Language</h3>
          <Select
            label="Preferred Language"
            options={LANGUAGES}
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          />
        </Card>

        <Button onClick={handleSaveSettings}>Save Settings</Button>

        <Card className="border-red-200 dark:border-red-900/50">
          <h3 className="text-lg font-semibold text-red-600 mb-2">Danger Zone</h3>
          <p className="text-sm text-gray-500 mb-4">
            Permanently delete your account and all associated data.
          </p>
          <Button variant="danger" icon={FiTrash2} onClick={() => setDeleteModalOpen(true)}>
            Delete Account
          </Button>
        </Card>
      </div>

      <Modal isOpen={deleteModalOpen} onClose={() => setDeleteModalOpen(false)} title="Delete Account">
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          This action is permanent and cannot be undone. All your data will be deleted.
        </p>
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => setDeleteModalOpen(false)}>Cancel</Button>
          <Button variant="danger" loading={deleting} onClick={handleDeleteAccount}>Delete Forever</Button>
        </div>
      </Modal>
    </motion.div>
  );
}
