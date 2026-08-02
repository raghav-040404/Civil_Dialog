import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { FiMail, FiLock } from 'react-icons/fi';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/dashboard';

  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      await login(data);
      addToast('Welcome back!', 'success');
      navigate(from, { replace: true });
    } catch (err) {
      addToast(err.message || 'Login failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="lg:hidden flex items-center gap-2 mb-8">
        <div className="w-10 h-10 rounded-xl bg-primary-600 flex items-center justify-center">
          <span className="text-white font-bold">CD</span>
        </div>
        <span className="text-2xl font-bold gradient-text">CivilDialog</span>
      </div>

      <h1 className="text-3xl font-bold mb-2">Welcome back</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">
        Sign in to your account to continue
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <Input
          label="Email"
          type="email"
          placeholder="you@example.com"
          icon={FiMail}
          error={errors.email?.message}
          {...register('email', {
            required: 'Email is required',
            pattern: { value: /^\S+@\S+\.\S+$/, message: 'Invalid email address' },
          })}
        />
        <Input
          label="Password"
          type="password"
          placeholder="Enter your password"
          icon={FiLock}
          error={errors.password?.message}
          {...register('password', {
            required: 'Password is required',
            minLength: { value: 6, message: 'Password must be at least 6 characters' },
          })}
        />

        <Button type="submit" className="w-full" loading={loading}>
          Sign In
        </Button>
      </form>

      <p className="text-center text-sm text-gray-500 mt-6">
        Don't have an account?{' '}
        <Link to="/register" className="text-primary-600 hover:underline font-medium">
          Create one
        </Link>
      </p>

      <div className="mt-6 p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 text-sm text-gray-500">
        <p className="font-medium mb-1">Demo credentials:</p>
        <p>admin@civildialog.com / password123</p>
        <p>jane@example.com / password123</p>
      </div>
    </div>
  );
}
