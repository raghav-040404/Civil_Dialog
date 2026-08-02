import { useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import { FiUser, FiMail, FiLock, FiCamera } from 'react-icons/fi';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import Avatar from '../../components/ui/Avatar';
import Card from '../../components/ui/Card';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import userService from '../../services/userService';

export default function ProfilePage() {
  const { user, updateUser } = useAuth();
  const { addToast } = useToast();
  const [profileLoading, setProfileLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [avatarLoading, setAvatarLoading] = useState(false);
  const fileInputRef = useRef(null);

  const profileForm = useForm({
    defaultValues: { name: user?.name || '', email: user?.email || '' },
  });

  const passwordForm = useForm();

  const onProfileSubmit = async (data) => {
    setProfileLoading(true);
    try {
      const updated = await userService.updateProfile(data);
      updateUser(updated);
      addToast('Profile updated successfully', 'success');
    } catch (err) {
      addToast(err.message || 'Update failed', 'error');
    } finally {
      setProfileLoading(false);
    }
  };

  const onPasswordSubmit = async (data) => {
    setPasswordLoading(true);
    try {
      await userService.updatePassword(data);
      addToast('Password updated successfully', 'success');
      passwordForm.reset();
    } catch (err) {
      addToast(err.message || 'Password update failed', 'error');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleAvatarChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAvatarLoading(true);
    try {
      const updated = await userService.uploadAvatar(file);
      updateUser(updated);
      addToast('Avatar updated', 'success');
    } catch {
      addToast('Failed to upload avatar', 'error');
    } finally {
      setAvatarLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold">Profile</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Manage your account information</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1 flex flex-col items-center text-center">
          <div className="relative mb-4">
            <Avatar src={user?.avatar} name={user?.name} size="xl" />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={avatarLoading}
              className="absolute bottom-0 right-0 p-2 rounded-full bg-primary-600 text-white hover:bg-primary-700 transition-colors"
            >
              {avatarLoading ? (
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin block" />
              ) : (
                <FiCamera size={14} />
              )}
            </button>
            <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleAvatarChange} />
          </div>
          <h2 className="text-xl font-semibold">{user?.name}</h2>
          <p className="text-gray-500 text-sm">{user?.email}</p>
          <p className="text-xs text-primary-600 mt-1 capitalize">{user?.role || 'user'}</p>
        </Card>

        <div className="lg:col-span-2 space-y-6">
          <Card>
            <h3 className="text-lg font-semibold mb-4">Personal Information</h3>
            <form onSubmit={profileForm.handleSubmit(onProfileSubmit)} className="space-y-4">
              <Input
                label="Full Name"
                icon={FiUser}
                error={profileForm.formState.errors.name?.message}
                {...profileForm.register('name', { required: 'Name is required' })}
              />
              <Input
                label="Email"
                type="email"
                icon={FiMail}
                error={profileForm.formState.errors.email?.message}
                {...profileForm.register('email', {
                  required: 'Email is required',
                  pattern: { value: /^\S+@\S+\.\S+$/, message: 'Invalid email' },
                })}
              />
              <Button type="submit" loading={profileLoading}>Save Changes</Button>
            </form>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-4">Change Password</h3>
            <form onSubmit={passwordForm.handleSubmit(onPasswordSubmit)} className="space-y-4">
              <Input
                label="Current Password"
                type="password"
                icon={FiLock}
                error={passwordForm.formState.errors.currentPassword?.message}
                {...passwordForm.register('currentPassword', { required: 'Required' })}
              />
              <Input
                label="New Password"
                type="password"
                icon={FiLock}
                error={passwordForm.formState.errors.newPassword?.message}
                {...passwordForm.register('newPassword', {
                  required: 'Required',
                  minLength: { value: 6, message: 'Min 6 characters' },
                })}
              />
              <Button type="submit" loading={passwordLoading}>Update Password</Button>
            </form>
          </Card>
        </div>
      </div>
    </motion.div>
  );
}
