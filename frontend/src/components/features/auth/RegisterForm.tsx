'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth, useRegister } from '@/hooks/useAuth';
import { useAuthStore } from '@/stores/authStore';
import { registerSchema, type RegisterInput } from '@/lib/validation/register-schema';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { Eye, EyeOff } from 'lucide-react';
import { ErrorMessage } from '@/components/shared/ErrorMessage';

export function RegisterForm() {
  const registerMutation = useRegister();
  const { mutate: registerUser, isPending } = registerMutation;
  const { error } = useAuth();  // Use store error, not mutation error
  const clearError = useAuthStore((state) => state.setError);  // Get function directly
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [dismissedError, setDismissedError] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<RegisterInput>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = (data: RegisterInput) => {
    // Clear previous error when attempting new submission
    clearError(null);
    setDismissedError(false);
    registerUser(data);
  };

  const password = watch('password');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Full Name Field */}
      <div>
        <label htmlFor="full_name" className="block text-sm font-medium text-slate-300 mb-2">
          Full Name
        </label>
        <input
          {...register('full_name')}
          type="text"
          placeholder="John Doe"
          className={cn(
            'w-full px-4 py-2 rounded-lg',
            'bg-slate-900/50 border border-slate-700/50',
            'text-white placeholder:text-slate-500',
            'focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/50',
            'transition-colors duration-200',
            errors.full_name && 'border-red-500/50'
          )}
        />
        {errors.full_name && (
          <p className="text-red-400 text-sm mt-1">{errors.full_name.message}</p>
        )}
      </div>

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

      {/* Organization Name Field */}
      <div>
        <label htmlFor="organization_name" className="block text-sm font-medium text-slate-300 mb-2">
          Organization
        </label>
        <input
          {...register('organization_name')}
          type="text"
          placeholder="Acme Corp"
          className={cn(
            'w-full px-4 py-2 rounded-lg',
            'bg-slate-900/50 border border-slate-700/50',
            'text-white placeholder:text-slate-500',
            'focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/50',
            'transition-colors duration-200',
            errors.organization_name && 'border-red-500/50'
          )}
        />
        {errors.organization_name && (
          <p className="text-red-400 text-sm mt-1">{errors.organization_name.message}</p>
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

      {/* Confirm Password Field */}
      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-300 mb-2">
          Confirm Password
        </label>
        <div className="relative">
          <input
            {...register('confirmPassword')}
            type={showConfirmPassword ? 'text' : 'password'}
            placeholder="••••••••"
            className={cn(
              'w-full px-4 py-2 rounded-lg',
              'bg-slate-900/50 border border-slate-700/50',
              'text-white placeholder:text-slate-500',
              'focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/50',
              'transition-colors duration-200',
              'pr-12',
              errors.confirmPassword && 'border-red-500/50'
            )}
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300 transition-colors"
          >
            {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        </div>
        {errors.confirmPassword && (
          <p className="text-red-400 text-sm mt-1">{errors.confirmPassword.message}</p>
        )}
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
        {isPending ? 'Creating account...' : 'Create Account'}
      </button>

      {/* Sign In Link */}
      <p className="text-center text-slate-400 text-sm mt-8">
        Already have an account?{' '}
        <Link href="/login" className="text-cyan-400 hover:text-cyan-300 font-medium">
          Sign in
        </Link>
      </p>
    </form>
  );
}
