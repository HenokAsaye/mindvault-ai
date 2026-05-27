'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth, useLogout } from '@/hooks';
import { cn } from '@/lib/utils';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const { mutate: logout, isPending } = useLogout();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [user, isLoading, router]);

  // Loading state
  if (isLoading) {
    return (
      <div className={cn(
        'min-h-screen bg-slate-950 flex items-center justify-center',
        'px-6'
      )}>
        <div className="text-center">
          <div className="mb-4 inline-block w-12 h-12 border-4 border-slate-700 border-t-cyan-400 rounded-full animate-spin" />
          <p className="text-slate-300">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn(
      'min-h-screen bg-slate-950',
      'px-6 py-20'
    )}>
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-12">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-50 mb-2">Dashboard</h1>
            <p className="text-slate-400">Welcome back, {user?.email}!</p>
          </div>
          <button
            onClick={() => logout()}
            disabled={isPending}
            className={cn(
              'px-6 py-2 rounded-lg font-semibold',
              'bg-red-500/20 hover:bg-red-500/30',
              'text-red-400 border border-red-500/50',
              'transition-all duration-300 disabled:opacity-50'
            )}
          >
            {isPending ? 'Logging out...' : 'Logout'}
          </button>
        </div>
      </div>

      {/* User Info */}
      <div className="max-w-7xl mx-auto mb-12">
        <div className={cn(
          'p-8 rounded-xl',
          'bg-white/5 border border-slate-700/50',
          'backdrop-blur-sm'
        )}>
          <h2 className="text-xl font-bold text-slate-50 mb-6">Your Information</h2>
          <div className="grid grid-cols-2 gap-8">
            <div>
              <p className="text-sm text-slate-400 mb-2">User ID</p>
              <p className="font-mono text-slate-50 text-sm break-all">{user?.user_id}</p>
            </div>
            <div>
              <p className="text-sm text-slate-400 mb-2">Organization ID</p>
              <p className="font-mono text-slate-50 text-sm break-all">{user?.org_id}</p>
            </div>
            <div>
              <p className="text-sm text-slate-400 mb-2">Email</p>
              <p className="text-slate-50">{user?.email || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-slate-400 mb-2">Role</p>
              <p className="text-slate-50 capitalize">{user?.role}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Features Coming Soon */}
      <div className="max-w-7xl mx-auto">
        <h2 className="text-2xl font-bold text-slate-50 mb-6">Coming Soon</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              title: '📄 Documents',
              description: 'Upload and manage your documents',
              href: '#',
            },
            {
              title: '💬 Chat',
              description: 'Chat with your documents',
              href: '#',
            },
            {
              title: '📊 Analytics',
              description: 'View usage and insights',
              href: '#',
            },
          ].map((item) => (
            <div
              key={item.title}
              className={cn(
                'p-6 rounded-xl',
                'bg-white/5 border border-slate-700/50',
                'hover:bg-white/8 transition-all duration-300',
                'cursor-not-allowed opacity-50'
              )}
            >
              <h3 className="text-lg font-semibold text-slate-50 mb-2">
                {item.title}
              </h3>
              <p className="text-slate-400 text-sm">
                {item.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Back to Home */}
      <div className="max-w-7xl mx-auto mt-12 pt-8 border-t border-slate-800">
        <Link
          href="/"
          className="text-cyan-400 hover:text-cyan-300 transition-colors"
        >
          ← Back to Home
        </Link>
      </div>
    </div>
  );
}
