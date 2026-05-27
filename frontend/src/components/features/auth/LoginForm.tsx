'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth, useLogin } from '@/hooks/useAuth';
import { useAuthStore } from '@/stores/authStore';
import { loginSchema, type LoginInput } from '@/lib/validation/login-schema';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { Eye, EyeOff } from 'lucide-react';
import { ErrorMessage } from '@/components/shared/ErrorMessage';

export function LoginForm() {
  const loginMutation = useLogin();
  const { mutate: login, isPending } = loginMutation;
  const { error } = useAuth();  // Use store error, not mutation error
  const clearError = useAuthStore((state) => state.setError);  // Get function directly
  const [showPassword, setShowPassword] = useState(false);
  const [dismissedError, setDismissedError] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = (data: LoginInput) => {
    // Clear previous error when attempting new submission
    clearError(null);
    setDismissedError(false);
    login(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Email Field */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-2">
          Email
        </label>
        <input
          {...register('email')}
          type="email"
          placeholder="you@example.com"
          className={cn(
            'w-full px-4 py-2 rounded-lg',
            'bg-slate-900/50 border border-slate-700/50',
            'text-white placeholder:text-slate-500',
            'focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/50',
            'transition-colors duration-200',
            errors.email && 'border-red-500/50'
          )}
        />
        {errors.email && (
          <p className="text-red-400 text-sm mt-1">{errors.email.message}</p>
        )}
      </div>

      {/* Password Field */}
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-2">
          Password
        </label>
        <div className="relative">
          <input
            {...register('password')}
            type={showPassword ? 'text' : 'password'}
            placeholder="••••••••"
            className={cn(
              'w-full px-4 py-2 rounded-lg',
              'bg-slate-900/50 border border-slate-700/50',
              'text-white placeholder:text-slate-500',
              'focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/50',
              'transition-colors duration-200',
              'pr-12',
              errors.password && 'border-red-500/50'
            )}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300 transition-colors"
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        </div>
        {errors.password && (
          <p className="text-red-400 text-sm mt-1">{errors.password.message}</p>
        )}
      </div>

      {/* Organization Slug (Optional) */}
      <div>
        <label htmlFor="org_slug" className="block text-sm font-medium text-slate-300 mb-2">
          Organization (Optional)
        </label>
        <input
          {...register('org_slug')}
          type="text"
          placeholder="organization-name"
          className={cn(
            'w-full px-4 py-2 rounded-lg',
            'bg-slate-900/50 border border-slate-700/50',
            'text-white placeholder:text-slate-500',
            'focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/50',
            'transition-colors duration-200'
          )}
        />
      </div>

      {/* Error Message */}
      {error && !dismissedError && (
        <ErrorMessage
          message={error}
          type="error"
          dismissible={true}
          onDismiss={() => {
            setDismissedError(true);
            clearError(null);
          }}
        />
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isPending}
        className={cn(
          'w-full px-4 py-2 rounded-lg font-semibold',
          'bg-gradient-to-r from-indigo-600 to-cyan-400',
          'text-white hover:shadow-lg hover:shadow-indigo-500/50',
          'transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed'
        )}
      >
        {isPending ? 'Signing in...' : 'Sign In'}
      </button>

      {/* Sign Up Link */}
      <p className="text-center text-slate-400 text-sm mt-8">
        Don't have an account?{' '}
        <Link href="/register" className="text-cyan-400 hover:text-cyan-300 font-medium">
          Sign up
        </Link>
      </p>
    </form>
  );
}
